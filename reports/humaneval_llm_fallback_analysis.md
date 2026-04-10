# HumanEval LLM Fallback Output Analysis

Generated on: 2026-03-08  
Workspace: `/Users/ajayramesh/Documents/AIML/Masteers/ThesisImplementation/thesis-hybrid-sdlc-agent`

## 1) Scope and Evidence

This analysis focuses on HumanEval runs that invoked fallback LLM attempts.

Primary artifacts:

- `episodes/humaneval_runs/runs_summary.jsonl`
- per-run folders in `episodes/humaneval_runs/<timestamp>_HumanEval_<id>/`
- fallback files:
  - `fallback_attempt_01/prompt.txt`, `llm_raw.txt`, `code.py`, `result.json`, `error.txt`
  - `fallback_attempt_02/prompt.txt`, `llm_raw.txt`, `code.py`, `result.json`, `error.txt`
- orchestration code:
  - `src/humaneval/run_humaneval_hybrid.py`
  - `src/humaneval/run_humaneval_hybrid_v2.py`

## 2) High-Level Outcome (Latest Snapshot)

Using latest run per task (`HumanEval/0..163`, n=164):

- Final `SLM` pass attempt-1: 81
- Final `SLM` pass attempt-2: 6
- Final `LLM` fallback pass attempt-1: 49
- Final `LLM` fallback pass attempt-2: 5
- Final unresolved fail: 23

Fallback was invoked on 77/164 tasks.

Among fallback-invoked tasks (n=77):

- Fallback solved 54 tasks total (70.1% rescue rate)
- Fallback attempt-1 solved 49 tasks
- Fallback attempt-2 added 5 more tasks
- 23 tasks remained unresolved

## 3) Fallback Attempt Dynamics

State matrix across the 77 fallback-invoked tasks (latest snapshot):

- `PASS` at fallback-1 and stop: 49
- `FAIL -> PASS` (fallback-2 recovery): 4
- `NO_RESULT_TIMEOUT -> PASS` (transient API timeout then recovery): 1
- `FAIL -> FAIL`: 22
- `NO_RESULT_NETWORK -> NO_RESULT_NETWORK`: 1

So attempt-2 contributed a real but bounded gain: +5 tasks over fallback attempt-1.

Fallback attempt-2 pass tasks:

1. `HumanEval/8`
2. `HumanEval/20`
3. `HumanEval/33`
4. `HumanEval/117`
5. `HumanEval/155`

## 4) What Fallback Recovered Best

SLM attempt-2 failure class to final LLM rescue rate (fallback-invoked tasks only):

- `AssertionError|tail`: 10/10 rescued (100.0%)
- `AssertionError`: 4/4 rescued (100.0%)
- `NameError`: 16/20 rescued (80.0%)
- `SLM_TIMEOUT`: 18/33 rescued (54.5%)
- `SyntaxError`: 0/4 rescued (0.0%)

Interpretation:

- LLM fallback was highly effective on executable-but-incorrect code (`AssertionError`) and many `NameError` issues.
- Fallback partially mitigated SLM generation timeouts.
- It was weak on syntax/formatting malformed outputs in this snapshot.

## 5) Why 23 Tasks Still Failed After Fallback

Final failure reasons in latest snapshot (fallback-invoked unresolved tasks, n=23):

- `NameError`: 10
- `AssertionError | tail`: 8
- `IndentationError`: 2
- `AssertionError`: 2
- network API failure (`Network is unreachable`): 1

`NameError` symbols in final unresolved fallback outputs:

- `List`: 3
- `math`: 3
- `encode_cyclic`: 1
- `encode_shift`: 1
- `gcd`: 1
- `hashlib`: 1

These are mostly symbol/import hygiene misses, not deep algorithmic impossibility.

## 6) Persistence vs Adaptation on Fallback Attempt-2

For tasks that failed both fallback attempts (`FAIL -> FAIL`, n=22):

- code was exactly unchanged between fallback-1 and fallback-2 in 14/22 tasks (63.6%)
- code changed in 8/22 tasks, but still did not pass tests

Common failure transitions:

- `NameError -> NameError`: 9
- `AssertionError|tail -> AssertionError|tail`: 8
- `IndentationError -> IndentationError`: 2

This indicates many fallback-2 failures were not due to absence of retry logic, but due to insufficient corrective diversity in generated candidates.

## 7) Concrete Recovery Examples (Fallback Attempt-2)

### 7.1 `HumanEval/8` (`sum_product`)

- SLM attempt-1/2 failed with `NameError: List not defined`
- fallback-1 repeated typed signature (`List`, `Tuple`) and failed similarly
- fallback-2 removed problematic type hints and passed

### 7.2 `HumanEval/20` (`find_closest_elements`)

- SLM and fallback-1 repeated `List`-annotation `NameError`
- fallback-2 switched to untyped signature and corrected loop indexing, then passed

### 7.3 `HumanEval/33` (`sort_third`)

- SLM failed with `TypeError`
- fallback-1 produced executable but wrong logic (`AssertionError`)
- fallback-2 fixed selection/replacement logic and passed

### 7.4 `HumanEval/117` (`select_words`)

- SLM timed out on both attempts
- fallback-1 API call timed out (`error.txt: The read operation timed out`)
- fallback-2 succeeded and passed, showing transient service issue recovery

### 7.5 `HumanEval/155` (`even_odd_count`)

- SLM and fallback-1 both failed assertion on edge case `candidate(0) == (1, 0)`
- fallback-2 adjusted digit handling and passed

## 8) What the Code Is Doing in Fallback Mode

From `src/humaneval/run_humaneval_hybrid_v2.py`:

- Fallback prompt includes:
  - task prompt + entry point
  - `Previous failures` (SLM and fallback traces)
  - optional `Self-debug notes`
  - optional `RAG hints` from similar past cases
- LLM generation uses `openai_chat_completion_codegen(...)`
- output is cleaned/extracted into `code.py`, then executed against task tests
- on API exception, run writes `error.txt` and continues to next fallback attempt

Operational note:

- Prompt artifacts clearly indicate v2-style runs include both self-debug and RAG sections.
- In latest snapshot, fallback-fail tasks were concentrated in the harder v2 segment; this is expected selection bias and should not be interpreted as “RAG/self-debug hurts performance.”

## 9) Historical Artifact Caution (All Logged Runs)

Across all 353 fallback-invoked run records (including repeated reruns), many attempts have no execution result due API/environment errors:

- 343 `error.txt` files for fallback attempts
- dominant historical issue: `OpenAI URLError: [Errno 1] Operation not permitted` (270 cases)
- additional issue: model access/config errors (`404 model_not_found` for `gpt-4.2`)

Therefore, all-run aggregates are heavily confounded by infrastructure.  
For thesis reporting of model behavior, the latest-per-task snapshot is the more reliable view.

## 10) Thesis-Ready Conclusions

1. Fallback LLM materially improved HumanEval outcomes: 54 of 77 fallback-routed tasks passed in latest snapshot.
2. Most value came from fallback attempt-1 (49 tasks), with a measurable incremental gain from attempt-2 (+5 tasks).
3. Remaining failures are dominated by:
   - repeated symbol/import hygiene (`NameError`), and
   - persistent semantic mismatch (`AssertionError`), plus a small number of formatting and network failures.
4. The orchestration design (SLM -> retry -> fallback with failure-aware context) is validated by evidence, but second fallback attempts need stronger anti-repetition controls to reduce `FAIL -> FAIL` stagnation.

