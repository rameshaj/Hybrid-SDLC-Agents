# HumanEval SLM Attempt Results Summary

Generated on: 2026-03-07  
Source: `episodes/humaneval_runs/runs_summary.jsonl`

## 1) Task Coverage Confirmed

- Unique HumanEval tasks found in run summary: **164**
- Task ID range: **HumanEval/0** to **HumanEval/163**

Note: this is 164 (not 166) in current repository artifacts.

## 2) Initial Full Sweep (First Run Per Task)

Method:

- For each task, select the **earliest** run entry by timestamp from `runs_summary.jsonl`.
- This corresponds to the initial full benchmark sweep across:
  - **2026-02-01** (23 tasks)
  - **2026-02-02** (141 tasks)

Results (first run per 164 tasks):

- SLM pass on attempt 1: **64**
- SLM pass on attempt 2: **4**
- LLM pass: **0**
- Final fail: **96**

### SLM Attempt-2 Pass Tasks (Initial Sweep)

Exactly 4 tasks:

1. `HumanEval/10`
2. `HumanEval/105`
3. `HumanEval/118`
4. `HumanEval/121`

This matches your recollection that 4 tasks passed on the 2nd SLM attempt.

## 3) Latest Snapshot (Latest Run Per Task)

Method:

- For each task, select the **latest** run entry by timestamp from `runs_summary.jsonl`.

Results (latest run per 164 tasks):

- SLM pass on attempt 1: **81**
- SLM pass on attempt 2: **6**
- LLM pass: **54**
- Final fail: **23**

SLM attempt-2 pass task IDs (latest snapshot):

- `HumanEval/10`
- `HumanEval/105`
- `HumanEval/118`
- `HumanEval/121`
- `HumanEval/148`
- `HumanEval/149`

## 4) Across All Logged Runs (No De-duplication)

If counting every run record in `runs_summary.jsonl`:

- SLM pass on attempt 1: **86**
- SLM pass on attempt 2: **11**
- LLM pass: **95**
- Fail: **491**

This view includes repeated reruns of the same tasks.

## 5) Related Evidence Files

- Main run summary:
  - `episodes/humaneval_runs/runs_summary.jsonl`
- 31-task rerun note:
  - `reports/session_summary.md` (section: “HumanEval re-runs (31 tasks)”)
- 31-task status table artifact:
  - `reports/rag_sample_run_status.txt`

## 6) Practical Interpretation

- If you are documenting the **initial SLM-only behavior**, use the “Initial Full Sweep” numbers:
  - **Attempt-1 SLM pass = 64**
  - **Attempt-2 SLM pass = 4**
- If you are documenting the **current best-known status after reruns/fallback**, use the “Latest Snapshot” numbers.
