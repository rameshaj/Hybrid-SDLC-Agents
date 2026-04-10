# HumanEval Code Implementation Details (Hybrid Runner + Fallback)

Generated on: 2026-03-09  
Project root: `/Users/ajayramesh/Documents/AIML/Masteers/ThesisImplementation/thesis-hybrid-sdlc-agent`

## 1) Scope

This note documents exactly how HumanEval execution is implemented in this codebase, including:

- SLM attempt loop behavior
- LLM fallback behavior
- whether previous failure output is fed into later attempts
- v2 additions (RAG + self-debug)
- exact task file paths used in practice (default vs overridden)

## 2) Main Implementation Files

- `src/humaneval/run_humaneval_hybrid.py`
- `src/humaneval/run_humaneval_hybrid_v2.py`
- `src/llm_fallback_openai_codegen.py` (separate fallback module used by both runners)
- `src/core/slm_llama_cli.py` (SLM config defaults / llama-cli invocation pattern)
- `src/core/retriever_rag_cases_v2.py` (v2 RAG retriever)

## 3) High-Level Execution Flow

For each selected HumanEval task:

1. Load task row from JSONL (`task_id`, `prompt`, `test`, `entry_point`).
2. Run SLM attempts (up to `--slm_attempts`).
3. After each SLM attempt:
   - extract code
   - run local tests
   - summarize failure
   - append failure summary to history
4. If SLM did not pass and fallback enabled:
   - run LLM fallback attempts (up to `--fallback_attempts`)
   - run same local tests
5. Save per-attempt artifacts and final status.

Important: `canonical_solution` is present in task rows but not used by execution logic.

## 4) Pseudo-Code (Behavioral Reconstruction)

```python
tasks = load_jsonl(tasks_path)
tasks = select_by_task_id_or_index_or_max_tasks(tasks, args)

for task in tasks:
    run_dir = make_timestamped_run_dir(task["task_id"])
    save(task.json)
    slm_failures = []
    fallback_failures = []
    rag_context = ""          # v2 only
    self_debug_notes = ""     # v2 only

    # ---------- SLM LOOP ----------
    for k in range(1, slm_attempts + 1):
        prompt = build_prompt(
            task_prompt=task["prompt"],
            entry_point=task["entry_point"],
            prev_failures=slm_failures,
            rag_context=rag_context,            # v2
            self_debug_notes=self_debug_notes,  # v2
        )
        raw = run_llama_cli(prompt, gguf_model_path, max_new_tokens, timeout)
        code = extract_and_clean_code(raw, entry_point)

        if code is empty:
            result = NO_CODE_EXTRACTED
        else:
            result = run_tests_locally(code, task["test"], task["entry_point"], timeout=test_timeout)

        save_attempt_artifacts(result, raw, code, prompt)
        slm_failures.append(f"attempt_{k}: {result.failure_summary}")

        if v2 and failed and code:
            self_debug_notes = slm_self_debug(code, failure_summary)  # bullet hints
        if v2 and failed and rag_enabled:
            rag_context = retrieve_rag_hints(task_prompt, entry_point, failure_summary)

        if result.score >= pass_threshold:
            mark_final_pass(model="SLM", attempt=k)
            break

    # ---------- LLM FALLBACK LOOP ----------
    if not passed and fallback_attempts > 0:
        for k in range(1, fallback_attempts + 1):
            fb_prompt = build_prompt(
                task_prompt=task["prompt"],
                entry_point=task["entry_point"],
                prev_failures=slm_failures + fallback_failures,
                rag_context=rag_context,            # v2
                self_debug_notes=self_debug_notes,  # v2
            )
            raw = openai_chat_completion_codegen(fb_prompt, model=fallback_model, ...)
            code = extract_and_clean_code(raw, entry_point)

            if code is empty:
                result = NO_CODE_EXTRACTED
            else:
                result = run_tests_locally(code, task["test"], task["entry_point"], timeout=test_timeout)

            save_fallback_artifacts(result, raw, code, fb_prompt)
            fallback_failures.append(f"fallback_{k}: {result.failure_summary}")

            if result.score >= pass_threshold:
                mark_final_pass(model="LLM", attempt=k)
                break

    if still_not_passed:
        mark_final_fail_with_summaries()
```

## 5) How This Pseudo-Code Is Run (Exact Execution Path)

### 5.1 Preconditions

- Python environment with project dependencies installed.
- Local SLM binary and model path configured:
  - `--llama_path` (default `/usr/local/bin/llama-completion`)
  - `--gguf_model_path` (project-specific gguf file path)
- For LLM fallback:
  - `OPENAI_API_KEY` must be set.
  - optional `OPENAI_API_BASE` can override endpoint.

### 5.2 Direct runner commands (v2, latest path)

Single task by ID:

```bash
python src/humaneval/run_humaneval_hybrid_v2.py \
  --tasks_path data/external/humaneval/humaneval_train.jsonl \
  --task_id HumanEval/8 \
  --llama_path /usr/local/bin/llama-completion \
  --gguf_model_path models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf \
  --slm_attempts 2 \
  --fallback_attempts 2 \
  --fallback_model gpt-4o-mini \
  --rag_enabled 1 \
  --self_debug_enabled 1 \
  --out_dir episodes/humaneval_runs
```

Single task by index:

```bash
python src/humaneval/run_humaneval_hybrid_v2.py \
  --tasks_path data/external/humaneval/humaneval_train.jsonl \
  --task_index 8 \
  --slm_attempts 2 \
  --fallback_attempts 2
```

Full sweep over selected tasks path:

```bash
python src/humaneval/run_humaneval_hybrid_v2.py \
  --tasks_path data/external/humaneval/humaneval_train.jsonl \
  --max_tasks -1 \
  --slm_attempts 2 \
  --fallback_attempts 2 \
  --out_dir episodes/humaneval_runs
```

### 5.3 Wrapper path for failed-task reruns

Script:

- `scripts/run_failed_slm_tasks_with_fallback.py`

Typical usage:

```bash
python scripts/run_failed_slm_tasks_with_fallback.py \
  --tasks_path reports/failed_slm_tasks.jsonl \
  --slm_attempts 2 \
  --fallback_attempts 2 \
  --fallback_model gpt-4o \
  --rag_enabled 1 \
  --self_debug_enabled 1 \
  --out_dir episodes/humaneval_runs
```

This wrapper calls `run_humaneval_hybrid_v2.py` once per task and prints per-attempt summaries.

### 5.4 How runtime artifacts map back to pseudo-code

For each task run:

- `episodes/humaneval_runs/<timestamp>_HumanEval_<id>/task.json`
- SLM loop artifacts:
  - `slm_attempt_01/`, `slm_attempt_02/`, ...
  - `prompt.txt`, `slm_raw.txt`, `code.py`, `result.json`, `test_stdout.txt`, `test_stderr.txt`
  - v2 extras: `self_debug_*`, `rag_query.txt`, `rag_hits.json`, `rag_context.txt`
- Fallback loop artifacts:
  - `fallback_attempt_01/`, `fallback_attempt_02/`, ...
  - `prompt.txt`, `llm_raw.txt`, `code.py`, `result.json` (or `error.txt` on API failure)
- Run terminal state:
  - `final_status.json`
- Global append-only run ledger:
  - `episodes/humaneval_runs/runs_summary.jsonl`

So the pseudo-code execution is not theoretical; every loop transition is persisted in run directories.

## 6) Confirmed: Previous Failure Is Input To Next Attempt

This is explicitly implemented and observed in artifacts.

- Code path:
  - `slm_failures.append(...)` is done after each SLM attempt.
  - next attempt prompt is rebuilt using `prev_failures`.
- Artifact proof:
  - Run: `episodes/humaneval_runs/20260201_164813_HumanEval_19`
  - Attempt-1 failure: `slm_attempt_01/result.json`
  - Attempt-2 prompt includes the exact prior failure under `Previous failures:` in `slm_attempt_02/prompt.txt`

In v2, attempt-N+1 prompt can also include:

- `Self-debug notes:` generated from prior failed code
- `RAG hints:` retrieved from previous solved cases

## 7) LLM Fallback Is Separate Module (Confirmed)

Fallback is not implemented inline only; both HumanEval runners import and call:

- `from src.llm_fallback_openai_codegen import openai_chat_completion_codegen`

Module behavior:

- Reads `OPENAI_API_KEY` from environment
- Uses Chat Completions endpoint (`OPENAI_API_BASE` override supported)
- Sends system prompt enforcing: return only Python code, no markdown/explanations
- Returns model text + raw response metadata

File: `src/llm_fallback_openai_codegen.py`

## 8) Task Path Clarification (Critical)

Both statements below are true, depending on run mode:

### A) Default benchmark runs

Both runners default to:

- `data/external/humaneval/humaneval_train.jsonl`

So if no `--tasks_path` override is provided, this is used.

### B) Targeted fallback rerun flow

Wrapper script `scripts/run_failed_slm_tasks_with_fallback.py` defaults to:

- `reports/failed_slm_tasks.jsonl`

And explicitly forwards that path into `run_humaneval_hybrid_v2.py --tasks_path ...`.

So targeted reruns are often not from `humaneval_train.jsonl`; they run from the 66-task subset file.

## 9) Confirmed Local HumanEval Task Files

- `data/external/humaneval/humaneval_train.jsonl` (full benchmark set in this repo; 164 tasks)
- `reports/failed_slm_tasks.jsonl` (targeted subset; 66 tasks)

Observed schema for both includes:

- `task_id`
- `prompt`
- `canonical_solution`
- `test`
- `entry_point`

Execution uses only: `task_id`, `prompt`, `test`, `entry_point`.

## 10) v1 vs v2 Difference Summary

### v1 (`run_humaneval_hybrid.py`)

- SLM attempts + fallback attempts
- previous failure summaries included in next prompt
- no RAG, no self-debug note generation

### v2 (`run_humaneval_hybrid_v2.py`)

- everything in v1, plus:
  - optional RAG retrieval (`--rag_enabled`, `--rag_top_k`)
  - optional self-debug pass (`--self_debug_enabled`)
  - richer prompt context from prior failed attempt

## 11) Method Inspiration Mapping (Inference for Thesis Framing)

The code design aligns with these research-style ideas:

1. Reflexion-style iterative repair:
   - test failure summary from attempt-N becomes context for attempt-N+1
2. Self-debug / self-refine style:
   - model generates debugging notes and re-attempts
3. Cascade routing:
   - inexpensive/local SLM first, stronger LLM fallback on persistent failure
4. Case-based retrieval:
   - similar historical fixes retrieved as hints (RAG)
5. Tool-coupled software agent loop:
   - code generation is always coupled with external execution feedback (tests), not single-shot generation

This is a conceptual alignment for literature framing; code does not explicitly cite papers inline.

## 12) Literature References (for write-up)

- Reflexion:  
  Shinn et al., 2023, `https://arxiv.org/abs/2303.11366`
- Self-Refine:  
  Madaan et al., 2023, `https://arxiv.org/abs/2303.17651`
- Self-Debugging:  
  Chen et al., 2023, `https://arxiv.org/abs/2304.05128`
- ReAct:  
  Yao et al., 2022, `https://arxiv.org/abs/2210.03629`
- FrugalGPT (cascade perspective):  
  Chen et al., 2023, `https://arxiv.org/abs/2305.05176`
- SWE-agent (software-agent interaction framing):  
  Yang et al., 2024, `https://arxiv.org/abs/2405.15793`

## 13) Final Confirmation

- Yes, previous output/failure is fed into subsequent attempts.
- Yes, LLM fallback is separate code (`src/llm_fallback_openai_codegen.py`).
- Yes, the actual tasks path is context-dependent:
  - default benchmark: `data/external/humaneval/humaneval_train.jsonl`
  - targeted fallback reruns: `reports/failed_slm_tasks.jsonl`
