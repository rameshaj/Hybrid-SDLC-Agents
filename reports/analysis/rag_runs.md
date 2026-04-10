# RAG Approach Used in This Project (FAISS Case-Memory)

Date captured: 2026-03-14

## 1) Scope
This document captures the exact RAG approach implemented in this repo for HumanEval/BigCodeBench hybrid runners, focusing on:
- how run outputs were captured,
- how successful fallback fixes were converted into RAG cases,
- how those cases were embedded/stored in FAISS,
- how retrieval was injected into later attempts.

Primary code files:
- `scripts/build_rag_cases_from_fallback.py`
- `scripts/build_rag_cases_faiss.py`
- `src/core/retriever_rag_cases_v2.py`
- `src/humaneval/run_humaneval_hybrid_v2.py`
- `src/bigcodebench/run_bigcodebench_hybrid_v2.py`

---

## 2) Data Source: HumanEval Run Artifacts

Run root:
- `episodes/humaneval_runs/`

Each task run directory has timestamped form:
- `YYYYMMDD_HHMMSS_HumanEval_<id>/`

Per run, artifacts include:
- `task.json`
- `final_status.json`
- `slm_attempt_01/`, `slm_attempt_02/`, ...
- `fallback_attempt_01/`, `fallback_attempt_02/`, ...

Per attempt, artifacts include:
- `prompt.txt`
- model raw output (`slm_raw.txt` or `llm_raw.txt`)
- `code.py`
- `candidate_run.py`
- `result.json`
- `test_stdout.txt`, `test_stderr.txt`

Important point:
- RAG case memory is built from **runs where fallback produced a passing result** (`result.json` with `ok=true` in a fallback attempt).

---

## 3) Case Construction from Runs (`build_rag_cases_from_fallback.py`)

Default input:
- `--runs_root episodes/humaneval_runs`
- `--out_path data/derived/rag/cases.jsonl`

### 3.1 Run selection logic
For each run directory:
1. Read `task.json` (must exist).
2. Find the first fallback attempt directory with `result.json` and `ok == true` (`fallback_attempt_*`).
3. If no fallback pass exists, skip run.
4. Extract SLM failure summary/code from:
   - `final_status.json` (`slm_failures`) if available, else
   - latest `slm_attempt_*/result.json` and `slm_attempt_*/code.py`.
5. Sanitize code text and require fallback code is valid Python via `ast.parse`.

### 3.2 Derived case fields
Each output case includes:
- `case_id` = `<task_id>::<run_dir_name>`
- `task_id`
- `dataset`
- `entry_point`
- `prompt`
- `slm_failure_type` (derived by keyword classifier)
- `slm_failure_summary`
- `slm_code` (sanitized)
- `llm_code` (sanitized fallback-passing code)
- `fix_diff` (unified diff: SLM code -> LLM code)
- `fix_actions` (heuristic tags from added lines, e.g. `add_import`, `add_guard`, `change_return`)
- `run_dir`
- `timestamp`

### 3.3 Dedupe behavior
`--dedupe_latest` keeps latest case per `task_id` (timestamp comparison).

Note on implementation detail:
- `--dedupe_latest` is declared as `store_true` with `default=True`, so it is effectively always on unless code is changed.

### 3.4 Optional merge
- `--include_cases_path` can append old cases before dedupe.
- This is how a larger merged file can be produced (example present locally: `data/derived/rag/cases.5d_plus27.jsonl`).

---

## 4) FAISS Build (`build_rag_cases_faiss.py`)

Input:
- `data/derived/rag/cases.jsonl`

Outputs:
- `data/derived/rag/cases.index.faiss`
- `data/derived/rag/cases.meta.jsonl`
- `data/derived/rag/cases.stats.json`

### 4.1 Embedding text per case
The embed text is built as:
- `dataset`
- `task_id`
- `entry_point`
- `error_type` (`slm_failure_type`)
- `error_summary` (`slm_failure_summary`)
- `prompt`

So retrieval is keyed mainly by **task prompt + failure context**, not by full `llm_code`.

### 4.2 Embedding model and index type
Configured model:
- `sentence-transformers/all-MiniLM-L6-v2`

Local stats file currently shows:
- `n_cases`: 27
- `dim`: 384
- `metric`: `cosine (IP on normalized embeddings)`
- `normalize`: `true`
- `batch_size`: `8`

FAISS index used:
- `IndexFlatIP` when normalized (`cosine via IP`)
- else `IndexFlatL2`

### 4.3 Metadata stored in `cases.meta.jsonl`
Each row stores:
- index id + case identity fields
- failure type/summary
- `fix_actions`
- full `llm_code`
- `fix_diff`
- `prompt`
- `run_dir`
- `timestamp`

Note on implementation detail:
- `--normalize` is declared as `store_true` with `default=True`, so current script behavior is effectively normalized by default.

---

## 5) Retrieval Runtime Flow (`retriever_rag_cases_v2.py` + runner v2)

### 5.1 Retriever behavior
`RagCaseRetriever`:
1. loads `cases.index.faiss` + `cases.meta.jsonl`,
2. loads the same sentence-transformer embedding model on CPU,
3. embeds query text,
4. verifies embedding dimension matches index dimension,
5. executes FAISS `search(k)`,
6. returns top-k metadata with `score`.

### 5.2 Query built after a failed SLM attempt
In `run_humaneval_hybrid_v2.py`, query text is:
- `entry_point`
- classified `error_type`
- `error_summary`
- full task `prompt`

RAG runs only when:
- `--rag_enabled 1`
- and current SLM attempt score `< pass_threshold`.

### 5.3 Prompt injection
Retrieved hits are formatted into `rag_context` and appended to next prompt under `RAG hints:`.

Included hint content per case:
- `task_id`, `slm_failure_type`, `fix_actions`, retrieval `score`
- optional `import_hints` extracted from `+import`/`+from` lines in `fix_diff`
- truncated `fix_diff`

This context is then used in:
- next SLM attempt prompt,
- and fallback prompt (if escalation happens).

### 5.4 Runtime RAG artifacts per attempt
Saved in each `slm_attempt_*` directory:
- `rag_query.txt`
- `rag_hits.json`
- `rag_context.txt`
- or `rag_error.txt` if unavailable/failing.

---

## 6) Chunking and Granularity

For this HumanEval case-memory FAISS:
- **No sliding-window chunking is used.**
- One case row (`cases.jsonl`) = one embedding vector.

So “chunk” granularity is:
- case-level (task + failure context), not line/window-level code chunks.

Prompt-level truncation during hint injection:
- per-case `fix_diff` truncated to ~600 chars,
- full `rag_context` truncated to ~1200 chars.

---

## 7) What Was Actually Stored (Current Workspace Snapshot)

RAG files:
- `data/derived/rag/cases.jsonl` -> 27 rows
- `data/derived/rag/cases.meta.jsonl` -> 27 rows
- `data/derived/rag/cases.index.faiss`
- `data/derived/rag/cases.stats.json`
- `data/derived/rag/cases.5d_plus27.jsonl` -> 72 rows (merged/alternate cases file, not the one current index stats point to)

Dataset currently present in indexed cases:
- `HumanEval` only

Current `cases.jsonl` failure-type distribution:
- `NameError`: 16
- `AssertionError`: 8
- `TypeError`: 2
- `ValueError`: 1

Current `fix_actions` tag counts (non-empty only):
- `change_return`: 19
- `add_guard`: 9

Observed HumanEval fallback-pass coverage in run history:
- 95 fallback-pass runs
- 72 unique HumanEval task IDs with fallback pass

Current indexed case memory is a filtered/deduped subset (27).

---

## 8) Repro Command Sequence

### 8.1 Generate fallback-pass runs (example scripts)
- `scripts/run_humaneval_rag_sample_fallback.py`
- `scripts/run_humaneval_rag_sample_fallback_checkpoint.py`
- `scripts/run_humaneval_rag_sample_fallback_single_loop.py`

These run HumanEval hybrid with fallback attempts and create run directories in `episodes/humaneval_runs`.

### 8.2 Build cases from run artifacts
```bash
python scripts/build_rag_cases_from_fallback.py \
  --runs_root episodes/humaneval_runs \
  --dataset HumanEval \
  --out_path data/derived/rag/cases.jsonl
```

Optional merge:
```bash
python scripts/build_rag_cases_from_fallback.py \
  --runs_root episodes/humaneval_runs \
  --out_path data/derived/rag/cases.5d_plus27.jsonl \
  --include_cases_path data/derived/rag/cases.jsonl
```

### 8.3 Build FAISS index
```bash
python scripts/build_rag_cases_faiss.py \
  --cases_path data/derived/rag/cases.jsonl \
  --out_dir data/derived/rag \
  --model sentence-transformers/all-MiniLM-L6-v2 \
  --batch_size 8
```

### 8.4 Run with RAG enabled (HumanEval v2)
```bash
python src/humaneval/run_humaneval_hybrid_v2.py \
  --tasks_path data/external/humaneval/humaneval_train.jsonl \
  --task_id HumanEval/101 \
  --slm_attempts 2 \
  --fallback_attempts 2 \
  --fallback_model gpt-4o-mini \
  --rag_enabled 1 \
  --rag_top_k 3 \
  --self_debug_enabled 1 \
  --out_dir episodes/humaneval_runs
```

### 8.5 Version clarification + how HumanEval was run in this project
HumanEval version clarification:
- There is no `HumanEval v5` runner file in this repository.
- RAG retrieval support is in `src/humaneval/run_humaneval_hybrid_v2.py` (latest HumanEval runner here).
- `src/humaneval/run_humaneval_hybrid.py` is the older non-RAG baseline runner.

Observed project run pattern for RAG-enabled HumanEval:
- Wrapper script: `scripts/run_failed_slm_tasks_with_fallback.py`
- That wrapper invokes `run_humaneval_hybrid_v2.py` and passes:
  - `--rag_enabled 1`
  - `--rag_top_k 3`
  - `--self_debug_enabled 1`
  - plus SLM/fallback attempt settings.

Example wrapper command:
```bash
python scripts/run_failed_slm_tasks_with_fallback.py \
  --tasks_path reports/failed_slm_tasks.jsonl \
  --slm_attempts 2 \
  --fallback_attempts 2 \
  --fallback_model gpt-4o \
  --rag_enabled 1 \
  --rag_top_k 3 \
  --self_debug_enabled 1 \
  --out_dir episodes/humaneval_runs
```

Evidence from a run directory:
- `episodes/humaneval_runs/20260221_073015_HumanEval_101/final_status.json`
  - contains `"rag_enabled": true`
  - contains `"rag_top_k": 3`
- corresponding attempt folders contain:
  - `rag_query.txt`
  - `rag_hits.json`
  - `rag_context.txt`

### 8.6 How much RAG data is needed
Hard requirement:
- You need a valid FAISS index/meta pair:
  - `data/derived/rag/cases.index.faiss`
  - `data/derived/rag/cases.meta.jsonl`
- At least 1 case vector must exist in the index.

Practical guidance used here:
- Current indexed memory size: `27` cases (`data/derived/rag/cases.stats.json`).
- Runtime setting used in runs: `rag_top_k = 3`.
- So each failed attempt can retrieve up to 3 nearest historical fix-cases.

`rag_top_k` behavior:
- If `rag_top_k <= n_cases`, retrieval returns up to `rag_top_k` hits.
- If `rag_top_k > n_cases`, FAISS returns only available valid hits (extra positions are ignored by code).

---

## 9) Important Evaluation Caveat

The v2 retrieval code does **not** exclude same-task matches by `task_id` during retrieval.
If a task already exists in case memory, RAG may return very similar prior fixes for that same task.
For strict benchmark isolation, add a filter to remove hits with the current `task_id` (or hold out tasks during index build).

---

## 10) Distinction from Other FAISS Pipelines in Repo

There are separate FAISS builders not used for this HumanEval case-memory retrieval:
- `src/step6_3_build_csn_faiss.py` (CodeSearchNet Java retrieval corpus)
- `src/step6_4_build_local_faiss.py` (local Defects4J source indexing with line-window chunking)

Only the case-memory files under `data/derived/rag/` are used by:
- `src/humaneval/run_humaneval_hybrid_v2.py`
- `src/bigcodebench/run_bigcodebench_hybrid_v2.py`

---

## 11) RAG Run Coverage and Pre-LLM Capture Evidence (HumanEval v2)

Date captured: 2026-03-16

Evidence extraction basis:
- scan `episodes/humaneval_runs/*_HumanEval_*/slm_attempt_*/rag_query.txt`
- require run directory naming pattern `YYYYMMDD_HHMMSS_HumanEval_<id>`
- read `final_status.json`, `fallback_attempt_*/prompt.txt`, `fallback_attempt_*/result.json`

Generated analysis artifacts:
- `reports/rag_humaneval_runs_snapshot.json`
  - all detected RAG run directories with per-attempt capture metadata.
- `reports/rag_humaneval_latest_per_task.json`
  - latest RAG run per task, used for task-level reporting without double-counting reruns.

### 11.1 Coverage Metrics

All RAG runs in history:
- run directories: `187`
- unique tasks with RAG runs: `67`
- total RAG attempt artifacts: `371`
- runs with fallback prompt artifacts: `184`
- final outcomes across all 187: `69 PASS`, `118 FAIL`

Latest-per-task (67 tasks):
- final pass: `42`
- final fail: `25`
- pass by SLM: `2` (`HumanEval/148`, `HumanEval/149`)
- pass by fallback LLM: `40`
- tasks with fallback prompt recorded: `65`
- fallback pass split: `38` at fallback attempt-1, `2` at fallback attempt-2

### 11.2 Task IDs Covered by RAG Runs

`HumanEval/14, HumanEval/26, HumanEval/28, HumanEval/29, HumanEval/32, HumanEval/38, HumanEval/39, HumanEval/46, HumanEval/50, HumanEval/65, HumanEval/74, HumanEval/76, HumanEval/79, HumanEval/81, HumanEval/83, HumanEval/86, HumanEval/88, HumanEval/90, HumanEval/91, HumanEval/93, HumanEval/101, HumanEval/102, HumanEval/103, HumanEval/106, HumanEval/108, HumanEval/110, HumanEval/112, HumanEval/113, HumanEval/115, HumanEval/117, HumanEval/119, HumanEval/120, HumanEval/123, HumanEval/124, HumanEval/126, HumanEval/127, HumanEval/129, HumanEval/130, HumanEval/131, HumanEval/132, HumanEval/133, HumanEval/134, HumanEval/135, HumanEval/136, HumanEval/137, HumanEval/139, HumanEval/140, HumanEval/141, HumanEval/142, HumanEval/143, HumanEval/144, HumanEval/145, HumanEval/146, HumanEval/147, HumanEval/148, HumanEval/149, HumanEval/150, HumanEval/151, HumanEval/152, HumanEval/153, HumanEval/154, HumanEval/155, HumanEval/156, HumanEval/157, HumanEval/160, HumanEval/162, HumanEval/163`

### 11.3 What Is Captured Before LLM Fallback Prompting

Per failed SLM attempt (`slm_attempt_XX/`):
- `rag_query.txt`
  - contains `entry_point`, `error_type`, `error_summary`, and task prompt.
- `rag_hits.json`
  - contains top-k retrieved FAISS case objects plus `score`.
  - in this workspace runs, `rag_top_k=3`, and observed hits count per attempt is consistently 3.
- `rag_context.txt`
  - prompt-formatted compact context used by the next generation stage.

Per fallback attempt (`fallback_attempt_XX/`):
- `prompt.txt`
  - includes `RAG hints:` block copied from `rag_context.txt` (plus previous failures and self-debug notes).

### 11.4 Concrete Verified Example

Run:
- `episodes/humaneval_runs/20260222_182120_HumanEval_101`

Verified pre-fallback files:
- `slm_attempt_01/rag_query.txt`
- `slm_attempt_01/rag_hits.json`
- `slm_attempt_01/rag_context.txt`
- `fallback_attempt_01/prompt.txt` (contains `RAG hints:` section)

This run demonstrates the full RAG capture chain before fallback LLM invocation and ended with final status `PASS` via fallback.
