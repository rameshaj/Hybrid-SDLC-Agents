# HumanEval LLM Fallback Deep Analysis (Attempt-1 vs Attempt-2)

Generated on: 2026-03-08  
Workspace: `/Users/ajayramesh/Documents/AIML/Masteers/ThesisImplementation/thesis-hybrid-sdlc-agent`

## 1) What This Analysis Covers

This report analyzes **LLM fallback attempt-1 vs attempt-2** for HumanEval, in the same style as the SLM attempt analysis.

Key questions:

1. For tasks where SLM failed and fallback was invoked, how much did fallback-1 and fallback-2 recover?
2. What failure types were most recoverable vs persistent?
3. What exactly happened in the 4 tasks recovered on fallback attempt-2?
4. Why did some tasks still fail after fallback?

## 2) Data and Method (Network-Filtered)

Primary artifacts:

- `episodes/humaneval_runs/runs_summary.jsonl`
- per-run folders under `episodes/humaneval_runs/*_HumanEval_*`
- network-cleaned task-level files:
  - `reports/humaneval_fallback_task_level_all164.json`
  - `reports/humaneval_fallback_slm_failed_only_selected.json`

Method:

1. Enumerate all HumanEval tasks found in artifacts (current repository snapshot).
2. For each task, identify runs where:
   - fallback exists, and
   - both SLM attempts failed (`slm_attempt_01 != PASS` and `slm_attempt_02 != PASS`).
3. Remove infrastructure-only fallback failures from selection (network/access/API config errors).
4. If latest run is infra-failed, select another run for the same task with usable fallback evidence.
5. Analyze selected fallback attempt transitions (`fb1`, `fb2`) task by task.

Infra/network classes excluded from evidence selection:

- `INFRA_NETWORK_PERMISSION`
- `INFRA_NETWORK_UNREACHABLE`
- `INFRA_MISSING_API_KEY`
- `INFRA_MODEL_NOT_FOUND_OR_ACCESS`
- `INFRA_API_TIMEOUT`
- `INFRA_CONNECTION_ERROR`

## 3) Coverage and Core Results

### 3.1 Task universe in current artifacts

- Unique HumanEval tasks found: **164** (`HumanEval/0..HumanEval/163`)
- Note: current repository artifacts do **not** contain 165/166 tasks.

### 3.2 Selected analysis set (SLM-failed + fallback-invoked, network-cleaned)

- Tasks in selected set: **93**
- Final fallback outcome:
  - `FALLBACK_PASS`: **72**
  - `FALLBACK_FAIL_NON_INFRA`: **21**
  - `FALLBACK_NO_RESULT_NON_INFRA`: **0**
  - `FALLBACK_INFRA_ONLY`: **0**

### 3.3 Fallback attempt contribution

- Fallback attempt-1 passes: **68**
- Additional passes from fallback attempt-2: **4**
- Total fallback pass: **72**

So attempt-2 provided:

- **4/93 = 4.3% absolute gain** over attempt-1 baseline in this selected set
- **4/25 = 16.0% recovery** among tasks that failed fallback-1
- **4/22 = 18.2% recovery** among tasks where fallback-2 was actually executed after fallback-1 failure

## 4) Transition Matrix (Fallback-1 -> Fallback-2)

Across selected 93 tasks:

- `PASS -> MISSING`: 68  
  (fallback-1 solved task; no second fallback needed)
- `FAIL -> PASS`: 4  
  (true fallback-2 recoveries)
- `FAIL -> FAIL`: 18  
  (fallback-2 executed but remained failing)
- `FAIL -> MISSING`: 3  
  (run had only one fallback attempt configured)

Recovered on fallback attempt-2:

1. `HumanEval/8`
2. `HumanEval/20`
3. `HumanEval/33`
4. `HumanEval/155`

## 5) Failure Taxonomy: Attempt-1 vs Attempt-2

### 5.1 Fallback attempt-1 failure classes (n=25)

- `AssertionError|tail`: 10
- `NameError`: 9
- `AssertionError`: 3
- `IndentationError`: 2
- `TIMEOUT`: 1

### 5.2 Fallback attempt-2 failure classes (executed and failed, n=18)

- `NameError`: 7
- `AssertionError|tail`: 7
- `IndentationError`: 2
- `AssertionError`: 2

### 5.3 Recovery by fallback-1 failure class

From fallback-1 failure class to final fallback outcome:

- `NameError`: 2/9 recovered (22.2%)
- `AssertionError|tail`: 2/10 recovered (20.0%)
- `AssertionError`: 0/3 recovered
- `IndentationError`: 0/2 recovered
- `TIMEOUT`: 0/1 recovered (and no fallback-2 in selected run)

Interpretation:

- fallback-2 helps in a subset of local semantic/symbol issues,
- but repeated semantic mismatch and formatting defects remain hard.

## 6) Task-Type Grouping (Heuristic)

Using the same prompt-keyword heuristic style:

- List/Array/Data-transform: 41 tasks
- String/Text: 40 tasks
- Math/Number-theory: 9 tasks
- General logic: 3 tasks

Outcome by group (selected set):

- List/Array/Data-transform: 34 pass, 7 fail, 4 recovered on fallback-2
- String/Text: 28 pass, 12 fail
- Math/Number-theory: 7 pass, 2 fail
- General logic: 3 pass, 0 fail

Interpretation:

- fallback-2 recoveries in this set occurred in list/data-transform tasks.

## 7) Deep Dive: The 4 Tasks Recovered on Fallback Attempt-2

### 7.1 `HumanEval/8` (`sum_product`)

Run directory:

- `episodes/humaneval_runs/20260212_073415_HumanEval_8`

Fallback-1:

- failed with `NameError: List not defined`
- code kept typed signature (`List[int]`, `Tuple[int, int]`)

Fallback-2:

- removed problematic type hints in signature
- passed tests

### 7.2 `HumanEval/20` (`find_closest_elements`)

Run directory:

- `episodes/humaneval_runs/20260213_073022_HumanEval_20`

Fallback-1:

- failed with `NameError: List not defined`
- included typed signature with `List`/`Tuple`

Fallback-2:

- changed to untyped signature and corrected pair-indexing loop
- passed tests

### 7.3 `HumanEval/33` (`sort_third`)

Run directory:

- `episodes/humaneval_runs/20260213_075605_HumanEval_33`

Fallback-1:

- failed with `AssertionError` (semantically wrong transform)

Fallback-2:

- changed strategy to collect/sort third-position elements and write back
- passed tests

### 7.4 `HumanEval/155` (`even_odd_count`)

Run directory:

- `episodes/humaneval_runs/20260224_073437_HumanEval_155`

Fallback-1:

- failed `AssertionError` on edge case `candidate(0) == (1, 0)`

Fallback-2:

- changed digit handling via string iteration
- passed tests

## 8) Positive Signal First: Why Fallback-2 Matters

Before limitations, the key positive result is:

- fallback-2 produced **4 extra task passes** beyond fallback-1 in this network-cleaned selected set,
- without model retraining, purely through test-time iteration and failure-conditioned prompting.

This is direct evidence that iterative fallback attempts can recover additional correctness beyond first escalation.

## 9) Why 21 Tasks Still Failed (Non-Infra)

Terminal (network-cleaned) unresolved failures are 21 tasks:

- `NameError`: 7
- `AssertionError|tail`: 7
- `IndentationError`: 2
- `AssertionError`: 2
- plus 3 cases where fallback-2 was not executed in selected run (`FAIL -> MISSING`)

Tasks with `FAIL -> MISSING`:

- `HumanEval/119` (`AssertionError|tail`)
- `HumanEval/129` (`TIMEOUT`)
- `HumanEval/143` (`NameError`)

These are run-configuration artifacts (single fallback attempt), not fallback-2 model failures.

## 10) Persistent Error Patterns

### 10.1 Repeated `NameError` in unresolved tasks

Symbol-level unresolved `NameError` cases include:

- `List` (2)
- `math` (2)
- `encode_cyclic` (1)
- `encode_shift` (1)
- `is_prime` (1)
- `hashlib` (1)

This remains mostly interface/import hygiene and helper-symbol resolution.

### 10.2 Repeated semantic mismatch (`AssertionError`)

Examples like `HumanEval/65` show same semantic failure across both fallback attempts with nearly identical code, indicating correction stagnation.

### 10.3 Formatting/structure defects

`HumanEval/32` persisted with `IndentationError` in both fallback attempts, showing fallback did not reliably recover structurally malformed outputs for this task.

## 11) Important Clarification on Network Errors

In this analysis file, network/access errors were **not counted as model failure outcomes**.

Example:

- `HumanEval/129` latest fallback run had network-unreachable errors.
- Another run for the same task with valid fallback execution was selected for model-behavior analysis.

Result:

- infra-only unresolved count in selected set is **0**.

## 12) Relation to Pipeline Design in Code

From `src/humaneval/run_humaneval_hybrid_v2.py`:

- Fallback prompt includes:
  - `Previous failures`
  - optional `Self-debug notes`
  - optional `RAG hints`
- each fallback attempt is executed/tested in isolated attempt folders
- on API exception, code writes `error.txt` and continues

This implementation supports iterative, failure-aware fallback behavior; the measured +4 fallback-2 recoveries validate that design direction.

## 13) Literature Mapping (Primary Sources)

This fallback behavior aligns with:

1. Reflexion (verbal feedback loops): `https://arxiv.org/abs/2303.11366`
2. Self-Refine (iterative improvement): `https://arxiv.org/abs/2303.17651`
3. Self-Debugging (execution-driven correction): `https://arxiv.org/abs/2304.05128`
4. FrugalGPT (cascade routing and cost-performance tradeoff): `https://arxiv.org/abs/2305.05176`
5. ReAct / SWE-agent perspective on environment-coupled agents:
   - `https://arxiv.org/abs/2210.03629`
   - `https://arxiv.org/abs/2405.15793`

## 14) Final Thesis-Ready Summary

In the network-cleaned HumanEval fallback analysis (SLM-failed tasks only, n=93):

- fallback solved **72** tasks,
- fallback-1 solved **68** directly,
- fallback-2 recovered **4** additional tasks,
- **21** tasks remained unresolved due to persistent non-infra code/test failures.

So the correct framing is:

- fallback escalation provides substantial recovery,
- second fallback attempt adds a smaller but real incremental gain,
- residual failures are dominated by repeated symbol-hygiene and semantic mismatch, not network artifacts.

## 15) Appendix: Evidence Pointers

Primary files:

- `reports/humaneval_fallback_network_cleaned_analysis.md`
- `reports/humaneval_fallback_task_level_all164.json`
- `reports/humaneval_fallback_task_level_all164.csv`
- `reports/humaneval_fallback_slm_failed_only_selected.json`
- `reports/humaneval_fallback_slm_failed_only_selected.csv`

Recovered-on-fallback-2 run directories:

- `episodes/humaneval_runs/20260212_073415_HumanEval_8`
- `episodes/humaneval_runs/20260213_073022_HumanEval_20`
- `episodes/humaneval_runs/20260213_075605_HumanEval_33`
- `episodes/humaneval_runs/20260224_073437_HumanEval_155`

Unresolved non-infra task IDs (21):

- `HumanEval/28, 29, 32, 38, 50, 65, 91, 106, 108, 115, 119, 129, 130, 132, 133, 134, 135, 143, 145, 162, 163`

