# Combined Runs Report

## QuixBug Runs

# QuixBugs Runs File (Session Consolidation)

Date saved: 2026-03-10  
Scope captured: from rerun wave starting at `20260310_045450_bitcount` up to `20260310_065059_knapsack`.

## 1) What this file captures

This file consolidates the QuixBugs work done in this session:

- Why `v5` was updated and what was changed.
- Why `v6` was created and what was changed.
- All QuixBugs episode runs in this rerun wave, with outcomes.
- Detailed reasons for SLM and LLM fallback failures.
- Dataset/workspace state at the end of capture.

Primary orchestrator files:

- `src/step6_orchestrator_quixbugs_v5_attempts.py`
- `src/step6_orchestrator_quixbugs_v6_attempts.py`

Primary run artifact root:

- `episodes/quixbugs_runs/attempts/`

---

## 2) Why v5 was updated (and what was updated)

### Why

During QuixBugs patching runs, key failure patterns were:

- Diff/hunk context mismatch even when patch content was close to correct.
- Patch repair needed before apply for many model diffs.
- Fallback/SLM apply path needed stronger context validation and repair behavior.
- CLI behavior differences around llama invocation needed stabilization.

### v5 updates captured in code

In `src/step6_orchestrator_quixbugs_v5_attempts.py`:

- Patch repair + context validation are enabled in apply paths:
  - `apply_patch(..., repair=True, validate_context=True)` for SLM and fallback flows.
- Newline-consistent context matching is implemented:
  - `repair_diff_to_file(...)` uses `splitlines()` for line model consistency.
  - `_validate_diff_context(...)` matches against newline-stripped file lines.
- Llama execution stabilization:
  - Uses `llama-completion` when available.
  - Drops unsupported `-no-cnv` flag.

Operational reason: reduce false negative patch-apply failures caused by formatting/context drift, and make generation invocation stable.

---

## 3) Why v6 was created (and what was added)

`v6` was created as a new file from v5 to avoid disrupting v5 behavior and to test feedback-loop improvements separately.

File:

- `src/step6_orchestrator_quixbugs_v6_attempts.py`

### v6 additions

- Stronger retry feedback in prompt:
  - Adds previous failure diagnostics into next SLM prompt.
  - Adds summaries of recently attempted diffs into next SLM prompt.
- Duplicate SLM diff suppression:
  - Hashes sanitized SLM diffs.
  - If attempt N repeats an earlier diff, marks `DUPLICATE_DIFF` and skips apply.

Operational reason: force non-redundant retry behavior and provide better self-correction signal across attempts.

---

## 4) Standard run settings used in this session

Common inputs:

- `--tasks_path data/quixbugs_tasks_v2.jsonl`
- `--llama_path /usr/local/bin/llama-completion`
- `--gguf_model_path models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`
- `--slm_timeout_s 400`

Primary setting families used:

- Family A: `SLM=3`, `fallback=2`
- Family B: `SLM=2`, `fallback=2`

Fallback models used:

- Mostly `gpt-4o-mini`
- One comparative rerun on task 13 with `gpt-4.1`

---

## 5) Chronological run log (this rerun wave)

| Run dir | Task | Final | SLM applied | Fallback applied | Key note |
|---|---|---|---:|---:|---|
| `20260310_045450_bitcount` | bitcount | PASS | 3/3 | 1/1 | Fallback recovered final pass |
| `20260310_050740_bitcount` | bitcount | ALREADY_PASS | 0/0 | 0/0 | Baseline already passing (file was in fixed state) |
| `20260310_050907_bitcount` | bitcount | FAIL | 2/3 | 0/2 | Fallback not executed (no `llm_raw.txt`; network/API unavailable in that run context) |
| `20260310_051255_bitcount` | bitcount | PASS | 2/3 | 1/1 | v6 duplicate suppression seen on attempt 3; fallback fixed |
| `20260310_052246_breadth_first_search` | breadth_first_search | ALREADY_PASS | 0/0 | 0/0 | Baseline pass before restoration to buggy HEAD |
| `20260310_052428_breadth_first_search` | breadth_first_search | FAIL | 0/3 | 0/2 | SLM no usable patch; fallback unavailable (network/API in that run context) |
| `20260310_052650_breadth_first_search` | breadth_first_search | FAIL | 0/3 | 2/2 | Fallback patches applied but did not fix tests |
| `20260310_053902_kheapsort` | kheapsort | FAIL | 0/3 | 2/2 | Fallback patches applied but behavior unchanged |
| `20260310_054639_kheapsort` | kheapsort | FAIL | 0/3 | 2/2 | Re-run: same failure mode |
| `20260310_055428_knapsack` | knapsack | FAIL | 0/3 | 1/2 | Mixed fallback behavior; one apply, then context mismatch |
| `20260310_060128_knapsack` | knapsack | FAIL | 0/2 | 0/2 | Both fallback attempts context/hunk mismatch |
| `20260310_060911_kth` | kth | FAIL | 2/2 | 2/2 | Both SLM and fallback patches applied but logic still wrong |
| `20260310_061801_lcs_length` | lcs_length | FAIL | 2/2 | 2/2 | Applied patches worsened behavior (`IndexError` after patch) |
| `20260310_062558_knapsack` | knapsack | FAIL | 0/2 | 1/2 | Fallback apply introduced conflict-marker corruption in file path during run |
| `20260310_063642_knapsack` | knapsack | NO_FINAL_STATUS | 0/2 | 0/0 | Interrupted run |
| `20260310_065059_knapsack` | knapsack | FAIL | 0/2 | 2/2 | Comparative fallback model `gpt-4.1`, still failed |

---

## 6) Detailed findings: why fallback failed

Fallback failure was not a single issue; it split into multiple technical modes.

### A) Patch applies, but logic is not sufficient

Examples:

- `kheapsort`: patch changed heap initialization (`arr[:k] if k < len(arr) else arr`) but core incorrect behavior remained.
- `kth`: fallback edits were semantically ineffective / recursion still failed.
- `lcs_length`: fallback added `range(len(t)+1)` causing `IndexError`.

### B) Patch format/context mismatch

Example:

- `knapsack` attempts frequently produced diffs that could not match target context (`HUNK_CONTEXT_NOT_FOUND`), especially with pseudo full-file style headers (`index e69de29...`) and unstable hunk contexts.

### C) Patch application side effects (conflict-marker corruption case)

Observed in `knapsack` runs:

- `applied_diff_actual.diff` showed `diff --cc` style and conflict markers (e.g., `<<<<<<< ours`) after fallback apply in one run branch.
- This led to Python `SyntaxError` on subsequent tests.

### D) Weak failure signal into fallback prompt

In some `knapsack` runs baseline was `[TIMEOUT]`, which gives weaker debugging signal than specific assertion/trace failures; fallback quality was poorer in those runs.

### E) Environment/network phase

In early reruns (non-escalated execution), fallback had no `llm_raw.txt` artifacts, matching OpenAI network/API unavailability in that run context.

---

## 7) Specific answer history captured in this session

- SLM did not pass task 0 by attempt 3 in v6; task 0 was recovered by fallback.
- v6 fix itself worked as designed (feedback sections + duplicate suppression), but it did not guarantee SLM correctness.
- Task 1 after restoring to buggy HEAD failed on v5 (`SLM context mismatch`, fallback not sufficient).
- Tasks 13/14/15 with `SLM=2`, `LLM=2` on v6 all failed.
- Task 13 with different fallback model (`gpt-4.1`) also failed (`20260310_065059_knapsack`).

---

## 8) Evidence pointers (key artifacts)

Key run folders used for analysis:

- `episodes/quixbugs_runs/attempts/20260310_051255_bitcount/`
- `episodes/quixbugs_runs/attempts/20260310_052650_breadth_first_search/`
- `episodes/quixbugs_runs/attempts/20260310_054639_kheapsort/`
- `episodes/quixbugs_runs/attempts/20260310_060911_kth/`
- `episodes/quixbugs_runs/attempts/20260310_061801_lcs_length/`
- `episodes/quixbugs_runs/attempts/20260310_062558_knapsack/`
- `episodes/quixbugs_runs/attempts/20260310_065059_knapsack/`

Important artifact file types per attempt:

- `prompt.txt`
- `slm_raw.txt` / `slm_err.txt`
- `llm_raw.txt`
- `diff_sanitized.txt`
- `diff_repaired.txt` (if generated)
- `applied_diff_actual.diff`
- `test_pre.txt`
- `test_after.txt`
- `patch_apply_err.txt` (on apply failure)
- `final_status.txt`

---

## 9) End-of-capture workspace state

QuixBugs task files explicitly restored to clean `HEAD` (buggy baseline) for consistency:

- `python_programs/bitcount.py`
- `python_programs/breadth_first_search.py`
- `python_programs/kheapsort.py`
- `python_programs/knapsack.py`
- `python_programs/kth.py`
- `python_programs/lcs_length.py`

Note:

- `src/step6_orchestrator_quixbugs_v5_attempts.py` and `src/step6_orchestrator_quixbugs_v6_attempts.py` are present as working files for ongoing experimentation.

---

## 10) Summary conclusion

The session achieved:

- Clear separation of orchestrator evolution (`v5` stability fixes, `v6` retry-feedback enhancements).
- Full rerun evidence for requested tasks with reproducible artifacts.
- Confirmed failure taxonomy for fallback:
  - sometimes unavailable (network phase),
  - sometimes patch-context invalid,
  - often patch semantics insufficient even when apply succeeds.

This document is the consolidated audit trail for the QuixBugs rerun phase in this session.

---

## 11) Task 0-15 attempt-level status (latest run per task)

This section explicitly captures SLM and LLM attempt outcomes for each QuixBugs task index `0..15` using the latest available run directory for that task.

Status legend:

- `PASS`: tests passed for that attempt.
- `FAIL_AFTER_APPLY`: patch applied, tests still failed.
- `PATCH_APPLY_FAIL`: patch could not be applied (context/format/apply failure).
- `DIFF_NOT_APPLIED`: diff was produced but not applied (for example duplicate suppression or invalid actionable content).
- `MODEL_OUTPUT_NO_DIFF`: model output existed but no usable diff could be extracted.

| Task idx | Algo | Latest run dir | Final | SLM attempts | LLM fallback attempts |
|---|---|---|---|---|---|
| 0 | bitcount | `20260310_051255_bitcount` | PASS | `attempt_01:FAIL_AFTER_APPLY; attempt_02:FAIL_AFTER_APPLY; attempt_03:DIFF_NOT_APPLIED` | `fallback_01:PASS` |
| 1 | breadth_first_search | `20260310_052650_breadth_first_search` | FAIL | `attempt_01:PATCH_APPLY_FAIL; attempt_02:PATCH_APPLY_FAIL; attempt_03:PATCH_APPLY_FAIL` | `fallback_01:FAIL_AFTER_APPLY; fallback_02:FAIL_AFTER_APPLY` |
| 2 | bucketsort | `20260309_202852_bucketsort` | PASS | `attempt_01:PATCH_APPLY_FAIL; attempt_02:PATCH_APPLY_FAIL` | `fallback_01:PATCH_APPLY_FAIL; fallback_02:PASS` |
| 3 | depth_first_search | `20260309_205140_depth_first_search` | FAIL | `attempt_01:MODEL_OUTPUT_NO_DIFF; attempt_02:MODEL_OUTPUT_NO_DIFF; attempt_03:MODEL_OUTPUT_NO_DIFF` | `fallback_01:PATCH_APPLY_FAIL; fallback_02:PATCH_APPLY_FAIL` |
| 4 | detect_cycle | `20260309_215320_detect_cycle` | PASS | `attempt_01:FAIL_AFTER_APPLY` | `none` |
| 5 | find_first_in_sorted | `20260309_220147_find_first_in_sorted` | PASS | `attempt_01:PASS` | `none` |
| 6 | find_in_sorted | `20260309_220447_find_in_sorted` | PASS | `attempt_01:PASS` | `none` |
| 7 | flatten | `20260309_221252_flatten` | PASS | `attempt_01:PASS` | `none` |
| 8 | gcd | `20260309_221625_gcd` | PASS | `attempt_01:PASS` | `none` |
| 9 | get_factors | `20260309_222133_get_factors` | FAIL | `attempt_01:PATCH_APPLY_FAIL; attempt_02:PATCH_APPLY_FAIL; attempt_03:PATCH_APPLY_FAIL` | `fallback_01:PATCH_APPLY_FAIL; fallback_02:FAIL_AFTER_APPLY` |
| 10 | hanoi | `20260309_222937_hanoi` | FAIL | `attempt_01:FAIL_AFTER_APPLY; attempt_02:PATCH_APPLY_FAIL; attempt_03:PATCH_APPLY_FAIL` | `fallback_01:FAIL_AFTER_APPLY; fallback_02:FAIL_AFTER_APPLY` |
| 11 | is_valid_parenthesization | `20260309_225001_is_valid_parenthesization` | FAIL | `attempt_01:FAIL_AFTER_APPLY; attempt_02:PATCH_APPLY_FAIL; attempt_03:PATCH_APPLY_FAIL` | `fallback_01:FAIL_AFTER_APPLY; fallback_02:FAIL_AFTER_APPLY` |
| 12 | kheapsort | `20260310_054639_kheapsort` | FAIL | `attempt_01:PATCH_APPLY_FAIL; attempt_02:PATCH_APPLY_FAIL; attempt_03:DIFF_NOT_APPLIED` | `fallback_01:FAIL_AFTER_APPLY; fallback_02:FAIL_AFTER_APPLY` |
| 13 | knapsack | `20260310_065059_knapsack` | FAIL | `attempt_01:PATCH_APPLY_FAIL; attempt_02:DIFF_NOT_APPLIED` | `fallback_01:FAIL_AFTER_APPLY; fallback_02:FAIL_AFTER_APPLY` |
| 14 | kth | `20260310_060911_kth` | FAIL | `attempt_01:FAIL_AFTER_APPLY; attempt_02:FAIL_AFTER_APPLY` | `fallback_01:FAIL_AFTER_APPLY; fallback_02:FAIL_AFTER_APPLY` |
| 15 | lcs_length | `20260310_061801_lcs_length` | FAIL | `attempt_01:FAIL_AFTER_APPLY; attempt_02:FAIL_AFTER_APPLY` | `fallback_01:FAIL_AFTER_APPLY; fallback_02:FAIL_AFTER_APPLY` |

---

## 12) Task 0-15 detailed reason notes (appendix)

This appendix gives task-by-task reason detail using the latest run per task (the same mapping used in Section 11).

### Task 0 (`bitcount`) - latest run `20260310_051255_bitcount` - final PASS

- SLM attempt 1 patch applied but post-test timed out.
- SLM attempt 2 patch applied but post-test timed out.
- SLM attempt 3 produced duplicate diff and was not applied.
- LLM fallback attempt 1 produced an applied patch and tests passed.

### Task 1 (`breadth_first_search`) - latest run `20260310_052650_breadth_first_search` - final FAIL

- SLM attempts 1/2/3: patch apply failed with `NO_HUNKS` (no usable hunk content after sanitize).
- LLM fallback attempts 1/2: patches applied, but behavior remained failing (test output still not equivalent to expected pass behavior).

### Task 2 (`bucketsort`) - latest run `20260309_202852_bucketsort` - final PASS

- SLM attempts 1/2: `NO_HUNKS` patch-apply failures.
- LLM fallback attempt 1: patch apply failure.
- LLM fallback attempt 2: produced working patch; task passed.

### Task 3 (`depth_first_search`) - latest run `20260309_205140_depth_first_search` - final FAIL

- SLM attempts 1/2/3: model output did not yield a usable patch diff for application.
- LLM fallback attempts 1/2: patch application failed.

### Task 4 (`detect_cycle`) - latest run `20260309_215320_detect_cycle` - final PASS

- SLM attempt 1 patch fixed the failure and tests passed.
- No fallback was required.

### Task 5 (`find_first_in_sorted`) - latest run `20260309_220147_find_first_in_sorted` - final PASS

- SLM attempt 1 passed directly.
- No fallback was required.

### Task 6 (`find_in_sorted`) - latest run `20260309_220447_find_in_sorted` - final PASS

- SLM attempt 1 passed directly.
- No fallback was required.

### Task 7 (`flatten`) - latest run `20260309_221252_flatten` - final PASS

- SLM attempt 1 passed directly.
- No fallback was required.

### Task 8 (`gcd`) - latest run `20260309_221625_gcd` - final PASS

- SLM attempt 1 passed directly.
- No fallback was required.

### Task 9 (`get_factors`) - latest run `20260309_222133_get_factors` - final FAIL

- SLM attempts 1/2/3: patch apply failures with `NO_HUNKS`.
- LLM fallback attempt 1: context/hunk mismatch (`HUNK_CONTEXT_NOT_FOUND`).
- LLM fallback attempt 2: patch applied but output still wrong on at least one case.

### Task 10 (`hanoi`) - latest run `20260309_222937_hanoi` - final FAIL

- SLM attempt 1: patch applied but logic remained incorrect.
- SLM attempts 2/3: patch apply failed (`NO_HUNKS`).
- LLM fallback attempts 1/2: patches applied but both still failed the same functional case.

### Task 11 (`is_valid_parenthesization`) - latest run `20260309_225001_is_valid_parenthesization` - final FAIL

- SLM attempt 1: patch applied but resulted in runtime failure (traceback).
- SLM attempts 2/3: patch apply failed (`NO_HUNKS`).
- LLM fallback attempts 1/2: patches applied, but semantic bug remained (incorrect output for invalid parentheses case).

### Task 12 (`kheapsort`) - latest run `20260310_054639_kheapsort` - final FAIL

- SLM attempts 1/2: patch apply failed (`NO_HUNKS`).
- SLM attempt 3: diff not applied.
- LLM fallback attempts 1/2: patches applied, but results stayed identical to failing behavior (no functional correction).

### Task 13 (`knapsack`) - latest run `20260310_065059_knapsack` - final FAIL

- SLM attempt 1: patch apply failed (`NO_HUNKS`).
- SLM attempt 2: non-actionable/duplicate-style output, no useful apply.
- LLM fallback attempts 1/2: patches applied but test phase still timed out/fail (no recovery).
- Additional earlier knapsack runs in this session also showed patch-context instability and one conflict-marker corruption branch (`<<<<<<< ours`) during fallback application.

### Task 14 (`kth`) - latest run `20260310_060911_kth` - final FAIL

- SLM attempts 1/2: patches applied but introduced/kept recursion failure (`RecursionError`).
- LLM fallback attempts 1/2: patches applied but original failure pattern remained (`IndexError`), so no semantic fix.

### Task 15 (`lcs_length`) - latest run `20260310_061801_lcs_length` - final FAIL

- SLM attempts 1/2: patches applied but logic remained incorrect (`KeyError` failure mode).
- LLM fallback attempts 1/2: patches applied but worsened behavior to `IndexError` (invalid loop/index boundary change).

---

## 13) QuixBugs Results Metrics Snapshot (Task 0-15 Latest Runs)

This section summarizes the same dataset already listed in Section 11, but in thesis-friendly metrics form.

- Total tasks analyzed (latest run per task): `16`
- Final PASS: `7`
- Final FAIL: `9`
- Fallback-recovered passes: `2` tasks (`0`, `2`)
- Not recovered after fallback budget: `9`

Direct SLM-pass signal:
- Confirmed direct SLM pass rows (`attempt_x:PASS` in SLM column): `4` tasks (`5`, `6`, `7`, `8`).
- Additional note: task `4` has final `PASS` with `fallback=none`; this indicates SLM-side recovery despite the recorded intermediate label `FAIL_AFTER_APPLY` in the summarized row.

Attempt outcome tag frequency (all attempt-status tags across SLM + fallback columns in Section 11):
- `FAIL_AFTER_APPLY`: `24`
- `PATCH_APPLY_FAIL`: `19`
- `PASS`: `6`
- `DIFF_NOT_APPLIED`: `3`
- `MODEL_OUTPUT_NO_DIFF`: `3`

Interpretation for thesis analysis:
- Dominant failure pressure was patch-application fragility (`PATCH_APPLY_FAIL`) plus semantic non-repair even after apply (`FAIL_AFTER_APPLY`).
- Fallback provided measurable gain (2 additional recovered tasks), but most hard cases remained semantically unresolved under the configured attempt budget.

## HumanEval Runs

# HumanEval Runs File (Initial 164-Task Sweep, Attempt-Level)

Date generated: 2026-03-16

## 1) Scope and Selection Rule
- Source: `episodes/humaneval_runs/runs_summary.jsonl` + per-run attempt artifacts.
- Selection rule: for each `HumanEval/<id>`, use the **earliest run timestamp** in `runs_summary.jsonl`.
- Coverage: `164` tasks (`HumanEval/0` to `HumanEval/163`).

## 2) Core Metrics (Initial Sweep)
- Total tasks: `164`
- Final PASS: `68`
- Final FAIL: `96`
- PASS winner = SLM: `68`
- PASS winner = LLM fallback: `0`
- FAIL winner = NONE: `96`

Second-attempt SLM recoveries (explicitly verified):
- Count: `4`
- Tasks: `HumanEval/10, HumanEval/105, HumanEval/118, HumanEval/121`

## 3) Status Legend
- `PASS`: tests passed
- `SLM_TIMEOUT`/`TIMEOUT`: timeout signatures
- `ASSERT_FAIL`, `NAME_ERROR`, `TYPE_ERROR`, etc.: normalized failure classes from `result.json.failure_summary`
- `none` in fallback column: no fallback attempts recorded for that selected run

## 4) Task-Level Attempt Status (All 164)
| Task ID | Selected run dir | Final | Winner | Winner attempt | SLM attempts | LLM fallback attempts |
|---|---|---|---|---:|---|---|
| HumanEval/0 | `20260201_180812_HumanEval_0` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/1 | `20260201_180950_HumanEval_1` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/2 | `20260201_181202_HumanEval_2` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/3 | `20260201_181211_HumanEval_3` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/4 | `20260201_181311_HumanEval_4` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/5 | `20260201_181457_HumanEval_5` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/6 | `20260201_211005_HumanEval_6` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/7 | `20260201_211200_HumanEval_7` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/8 | `20260201_211309_HumanEval_8` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/9 | `20260201_211446_HumanEval_9` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/10 | `20260201_211622_HumanEval_10` | PASS | SLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:PASS` | `none` |
| HumanEval/11 | `20260201_211734_HumanEval_11` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/12 | `20260201_211746_HumanEval_12` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/13 | `20260201_211910_HumanEval_13` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/14 | `20260201_211922_HumanEval_14` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/15 | `20260201_212020_HumanEval_15` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/16 | `20260201_212029_HumanEval_16` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/17 | `20260201_212039_HumanEval_17` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/18 | `20260201_212244_HumanEval_18` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/19 | `20260201_164813_HumanEval_19` | FAIL | NONE | - | `attempt_01:SYNTAX_ERROR; attempt_02:SYNTAX_ERROR` | `none` |
| HumanEval/20 | `20260202_040331_HumanEval_20` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/21 | `20260202_040436_HumanEval_21` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/22 | `20260202_040609_HumanEval_22` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/23 | `20260202_040711_HumanEval_23` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/24 | `20260202_040726_HumanEval_24` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/25 | `20260202_040748_HumanEval_25` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/26 | `20260202_040929_HumanEval_26` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/27 | `20260202_041041_HumanEval_27` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/28 | `20260202_041057_HumanEval_28` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/29 | `20260202_041127_HumanEval_29` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/30 | `20260202_041206_HumanEval_30` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/31 | `20260202_041216_HumanEval_31` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/32 | `20260202_041250_HumanEval_32` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:INDENT_ERROR` | `none` |
| HumanEval/33 | `20260202_041439_HumanEval_33` | FAIL | NONE | - | `attempt_01:TYPE_ERROR; attempt_02:TYPE_ERROR` | `none` |
| HumanEval/34 | `20260201_175614_HumanEval_34` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/35 | `20260202_041538_HumanEval_35` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/36 | `20260202_041547_HumanEval_36` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/37 | `20260202_041605_HumanEval_37` | FAIL | NONE | - | `attempt_01:INDEX_ERROR; attempt_02:TYPE_ERROR` | `none` |
| HumanEval/38 | `20260202_041641_HumanEval_38` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/39 | `20260202_041752_HumanEval_39` | FAIL | NONE | - | `attempt_01:TIMEOUT; attempt_02:TIMEOUT` | `none` |
| HumanEval/40 | `20260202_041902_HumanEval_40` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/41 | `20260202_041923_HumanEval_41` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/42 | `20260202_041933_HumanEval_42` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/43 | `20260202_041943_HumanEval_43` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/44 | `20260202_041957_HumanEval_44` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/45 | `20260202_042016_HumanEval_45` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/46 | `20260202_042025_HumanEval_46` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:SYNTAX_ERROR` | `none` |
| HumanEval/47 | `20260202_042151_HumanEval_47` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/48 | `20260202_042209_HumanEval_48` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/49 | `20260202_042217_HumanEval_49` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/50 | `20260202_042246_HumanEval_50` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/51 | `20260202_042322_HumanEval_51` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/52 | `20260202_042334_HumanEval_52` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/53 | `20260202_042347_HumanEval_53` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/54 | `20260202_042356_HumanEval_54` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/55 | `20260202_042450_HumanEval_55` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/56 | `20260202_042505_HumanEval_56` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/57 | `20260201_180042_HumanEval_57` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/58 | `20260201_180055_HumanEval_58` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/59 | `20260202_042522_HumanEval_59` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/60 | `20260202_042556_HumanEval_60` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/61 | `20260202_042607_HumanEval_61` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/62 | `20260202_042623_HumanEval_62` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/63 | `20260202_042634_HumanEval_63` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/64 | `20260202_042658_HumanEval_64` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/65 | `20260202_042817_HumanEval_65` | FAIL | NONE | - | `attempt_01:TYPE_ERROR; attempt_02:TYPE_ERROR` | `none` |
| HumanEval/66 | `20260202_042901_HumanEval_66` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/67 | `20260202_042911_HumanEval_67` | FAIL | NONE | - | `attempt_01:VALUE_ERROR; attempt_02:VALUE_ERROR` | `none` |
| HumanEval/68 | `20260202_042940_HumanEval_68` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/69 | `20260202_043006_HumanEval_69` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/70 | `20260202_043047_HumanEval_70` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/71 | `20260202_043115_HumanEval_71` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/72 | `20260202_043154_HumanEval_72` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/73 | `20260202_043208_HumanEval_73` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/74 | `20260202_043227_HumanEval_74` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/75 | `20260202_043303_HumanEval_75` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/76 | `20260202_043340_HumanEval_76` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:UNBOUNDLOCAL_ERROR` | `none` |
| HumanEval/77 | `20260202_043502_HumanEval_77` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/78 | `20260202_043527_HumanEval_78` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/79 | `20260202_043543_HumanEval_79` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/80 | `20260202_043636_HumanEval_80` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/81 | `20260202_043649_HumanEval_81` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:KEY_ERROR` | `none` |
| HumanEval/82 | `20260202_043745_HumanEval_82` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/83 | `20260202_043802_HumanEval_83` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/84 | `20260202_043836_HumanEval_84` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/85 | `20260202_043846_HumanEval_85` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/86 | `20260202_043858_HumanEval_86` | FAIL | NONE | - | `attempt_01:TYPE_ERROR; attempt_02:TYPE_ERROR` | `none` |
| HumanEval/87 | `20260202_043921_HumanEval_87` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/88 | `20260202_043939_HumanEval_88` | FAIL | NONE | - | `attempt_01:INDEX_ERROR; attempt_02:INDEX_ERROR` | `none` |
| HumanEval/89 | `20260202_044046_HumanEval_89` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/90 | `20260202_044105_HumanEval_90` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/91 | `20260202_044134_HumanEval_91` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/92 | `20260202_044221_HumanEval_92` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/93 | `20260202_044237_HumanEval_93` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/94 | `20260202_044327_HumanEval_94` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/95 | `20260202_044358_HumanEval_95` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/96 | `20260202_044420_HumanEval_96` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/97 | `20260202_044444_HumanEval_97` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/98 | `20260202_044455_HumanEval_98` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/99 | `20260202_044507_HumanEval_99` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/100 | `20260202_044522_HumanEval_100` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/101 | `20260202_044534_HumanEval_101` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/102 | `20260202_044558_HumanEval_102` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/103 | `20260202_044658_HumanEval_103` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/104 | `20260202_044732_HumanEval_104` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/105 | `20260202_044744_HumanEval_105` | PASS | SLM | 2 | `attempt_01:TYPE_ERROR; attempt_02:PASS` | `none` |
| HumanEval/106 | `20260202_044854_HumanEval_106` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/107 | `20260202_044929_HumanEval_107` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/108 | `20260202_044955_HumanEval_108` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/109 | `20260202_045028_HumanEval_109` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/110 | `20260202_045050_HumanEval_110` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/111 | `20260202_045215_HumanEval_111` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/112 | `20260202_045243_HumanEval_112` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/113 | `20260202_045315_HumanEval_113` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/114 | `20260202_045405_HumanEval_114` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/115 | `20260202_045425_HumanEval_115` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/116 | `20260202_045525_HumanEval_116` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/117 | `20260202_045552_HumanEval_117` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/118 | `20260202_045727_HumanEval_118` | PASS | SLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:PASS` | `none` |
| HumanEval/119 | `20260202_133710_HumanEval_119` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/120 | `20260202_050203_HumanEval_120` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/121 | `20260202_050258_HumanEval_121` | PASS | SLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:PASS` | `none` |
| HumanEval/122 | `20260202_050403_HumanEval_122` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/123 | `20260202_134111_HumanEval_123` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/124 | `20260202_134512_HumanEval_124` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/125 | `20260202_053859_HumanEval_125` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/126 | `20260202_134913_HumanEval_126` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/127 | `20260202_135315_HumanEval_127` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/128 | `20260202_073517_HumanEval_128` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/129 | `20260202_074309_HumanEval_129` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/130 | `20260202_135716_HumanEval_130` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/131 | `20260202_140117_HumanEval_131` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/132 | `20260202_140519_HumanEval_132` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/133 | `20260202_083147_HumanEval_133` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/134 | `20260202_140920_HumanEval_134` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/135 | `20260202_141322_HumanEval_135` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/136 | `20260202_110209_HumanEval_136` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/137 | `20260202_131707_HumanEval_137` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/138 | `20260202_132135_HumanEval_138` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/139 | `20260202_110210_HumanEval_139` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/140 | `20260202_131707_HumanEval_140` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/141 | `20260202_110048_HumanEval_141` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/142 | `20260202_110048_HumanEval_142` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/143 | `20260202_131543_HumanEval_143` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/144 | `20260202_132011_HumanEval_144` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/145 | `20260202_132412_HumanEval_145` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/146 | `20260202_132812_HumanEval_146` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/147 | `20260202_133213_HumanEval_147` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/148 | `20260202_133614_HumanEval_148` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/149 | `20260202_134015_HumanEval_149` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/150 | `20260202_134416_HumanEval_150` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/151 | `20260202_134816_HumanEval_151` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/152 | `20260202_135218_HumanEval_152` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/153 | `20260202_135619_HumanEval_153` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/154 | `20260202_140020_HumanEval_154` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/155 | `20260202_140422_HumanEval_155` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/156 | `20260202_140823_HumanEval_156` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/157 | `20260202_141225_HumanEval_157` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/158 | `20260202_141626_HumanEval_158` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/159 | `20260202_142028_HumanEval_159` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/160 | `20260202_142430_HumanEval_160` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/161 | `20260202_142831_HumanEval_161` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/162 | `20260202_143233_HumanEval_162` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/163 | `20260202_143635_HumanEval_163` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |

## 5) Terminal Failure Taxonomy (96 Final Fails)
- `SLM_TIMEOUT`: `37`
- `ASSERT_FAIL`: `26`
- `NAME_ERROR`: `21`
- `TYPE_ERROR`: `4`
- `SYNTAX_ERROR`: `2`
- `INDENT_ERROR`: `1`
- `INDEX_ERROR`: `1`
- `KEY_ERROR`: `1`
- `TIMEOUT`: `1`
- `UNBOUNDLOCAL_ERROR`: `1`
- `VALUE_ERROR`: `1`

## 6) Notes for Thesis Reporting
- This table is aligned to the initial sweep methodology used in prior HumanEval SLM analysis in this workspace.
- The “4 tasks passed in SLM attempt-2” statement is preserved and explicitly listed above.

## 7) Appendix Deep-Dive: The 4 SLM Attempt-2 Recoveries

These are the only tasks where attempt-1 failed but attempt-2 passed (no fallback used in selected initial runs):

1. `HumanEval/10` (`make_palindrome`)
2. `HumanEval/105` (`by_length`)
3. `HumanEval/118` (`get_closest_vowel`)
4. `HumanEval/121` (`solution`)

Observed pattern across all 4:
- Attempt-1 failed with a concrete test/runtime signal (`ASSERT_FAIL` or `TYPE_ERROR`).
- Attempt-2 fixed a localized logic issue and reached `PASS`.
- This is consistent with iterative self-correction behavior where explicit prior error context improves the second generation.

Task-specific short notes:
- `HumanEval/10`: `ASSERT_FAIL -> PASS` (edge-case palindrome completion corrected).
- `HumanEval/105`: `TYPE_ERROR -> PASS` (collection/indexing misuse corrected).
- `HumanEval/118`: `ASSERT_FAIL -> PASS` (vowel-selection rule corrected).
- `HumanEval/121`: `ASSERT_FAIL -> PASS` (constraint/logic alignment corrected).

## 8) Appendix Coverage: Outcome Groups Across All 164 Tasks

This grouped appendix ensures complete coverage of all tasks in compact narrative form.

### 8.1 SLM Pass on Attempt-1 (64 tasks)

Task IDs:
`2, 11, 13, 15, 16, 18, 23, 24, 27, 30, 31, 34, 35, 36, 40, 41, 42, 43, 44, 45, 47, 48, 49, 51, 52, 53, 55, 56, 57, 58, 59, 60, 61, 62, 63, 66, 68, 72, 73, 78, 80, 82, 84, 85, 87, 89, 92, 94, 95, 96, 97, 98, 99, 100, 104, 107, 109, 111, 114, 116, 122, 125, 128, 138`

Interpretation:
- These tasks were solved without requiring retry or fallback in the selected initial sweep run.

### 8.2 SLM Pass on Attempt-2 (4 tasks)

Task IDs:
`10, 105, 118, 121`

Interpretation:
- These are the explicit second-attempt recoveries and represent positive iterative-correction signal.

### 8.3 Final Fail: `SLM_TIMEOUT` (37 tasks)

Task IDs:
`119, 123, 124, 126, 127, 130, 131, 132, 133, 134, 135, 136, 137, 139, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163`

Interpretation:
- Largest failure group; primary blocker is generation timeout rather than semantic mismatch.

### 8.4 Final Fail: `ASSERT_FAIL` (26 tasks)

Task IDs:
`54, 64, 69, 70, 71, 74, 75, 77, 79, 83, 90, 91, 93, 101, 102, 103, 106, 108, 110, 112, 113, 115, 117, 120, 129, 140`

Interpretation:
- Code executed but did not satisfy expected behavior in one or more tests.

### 8.5 Final Fail: `NAME_ERROR` (21 tasks)

Task IDs:
`0, 1, 3, 4, 5, 6, 7, 8, 9, 12, 14, 17, 20, 21, 22, 25, 26, 28, 29, 38, 50`

Interpretation:
- Frequent missing symbol/import context in early selected runs (notably type-hint/module misses).

### 8.6 Final Fail: `TYPE_ERROR` (4 tasks)

Task IDs:
`33, 37, 65, 86`

Interpretation:
- Runtime type misuse; likely recoverable with stronger type-consistency prompting.

### 8.7 Final Fail: `SYNTAX_ERROR` (2 tasks)

Task IDs:
`19, 46`

Interpretation:
- Minor fraction of failures are compile-level syntax breaks.

### 8.8 Final Fail: Single-Task Buckets

- `INDENT_ERROR`: task `32`
- `INDEX_ERROR`: task `88`
- `KEY_ERROR`: task `81`
- `TIMEOUT`: task `39`
- `UNBOUNDLOCAL_ERROR`: task `76`
- `VALUE_ERROR`: task `67`

Interpretation:
- These are isolated edge/runtime signatures compared with the dominant timeout/assertion/name-error clusters.

## 9) Final Alignment Note

This file now contains the same structural elements used in QuixBugs/BigCodeBench run files:
- full attempt-level task table,
- explicit recovery accounting,
- failure taxonomy,
- appendix narrative coverage for the whole task set.

## 10) RAG-Enabled Runs (v2) Added for Analysis/Results Reporting

This section captures the later HumanEval v2 phase where retrieval (`--rag_enabled 1`) was used before fallback LLM generation.

Evidence source:
- `episodes/humaneval_runs/*_HumanEval_*/slm_attempt_*/rag_query.txt`
- `episodes/humaneval_runs/*_HumanEval_*/slm_attempt_*/rag_hits.json`
- `episodes/humaneval_runs/*_HumanEval_*/slm_attempt_*/rag_context.txt`
- `episodes/humaneval_runs/*_HumanEval_*/fallback_attempt_*/prompt.txt`

Snapshot files generated for thesis reporting:
- `reports/rag_humaneval_runs_snapshot.json` (all detected RAG runs)
- `reports/rag_humaneval_latest_per_task.json` (latest RAG run per task)

### 10.1 Coverage Summary

All RAG run directories found in history:
- RAG run directories: `187`
- Unique HumanEval task IDs with at least one RAG run: `67`
- Total RAG attempt artifact sets (`rag_query/rag_hits/rag_context`): `371`
- Runs with fallback attempt directories: `184`
- Runs with fallback prompt artifacts: `184`
- Final outcomes across these 187 runs: `69 PASS`, `118 FAIL`

Latest-per-task view (67 tasks, one latest RAG run per task):
- Final PASS: `42`
- Final FAIL: `25`
- Final PASS by SLM: `2` (`HumanEval/148`, `HumanEval/149`)
- Final PASS by fallback LLM: `40`
- Final FAIL after fallback/non-pass: `25`
- Tasks with fallback prompts recorded: `65`
- LLM passes by attempt: `38` on fallback attempt-1, `2` on fallback attempt-2

### 10.2 Tasks That Had RAG Runs (Unique Task IDs)

`HumanEval/14, HumanEval/26, HumanEval/28, HumanEval/29, HumanEval/32, HumanEval/38, HumanEval/39, HumanEval/46, HumanEval/50, HumanEval/65, HumanEval/74, HumanEval/76, HumanEval/79, HumanEval/81, HumanEval/83, HumanEval/86, HumanEval/88, HumanEval/90, HumanEval/91, HumanEval/93, HumanEval/101, HumanEval/102, HumanEval/103, HumanEval/106, HumanEval/108, HumanEval/110, HumanEval/112, HumanEval/113, HumanEval/115, HumanEval/117, HumanEval/119, HumanEval/120, HumanEval/123, HumanEval/124, HumanEval/126, HumanEval/127, HumanEval/129, HumanEval/130, HumanEval/131, HumanEval/132, HumanEval/133, HumanEval/134, HumanEval/135, HumanEval/136, HumanEval/137, HumanEval/139, HumanEval/140, HumanEval/141, HumanEval/142, HumanEval/143, HumanEval/144, HumanEval/145, HumanEval/146, HumanEval/147, HumanEval/148, HumanEval/149, HumanEval/150, HumanEval/151, HumanEval/152, HumanEval/153, HumanEval/154, HumanEval/155, HumanEval/156, HumanEval/157, HumanEval/160, HumanEval/162, HumanEval/163`

### 10.3 Exactly What RAG Data Was Captured Before Fallback LLM

For each failed SLM attempt in v2, the runner writes:
- `slm_attempt_XX/rag_query.txt`
  - composed from `entry_point`, normalized `error_type`, `error_summary`, and full task prompt.
- `slm_attempt_XX/rag_hits.json`
  - top-k retrieved cases (here k=3), with fields such as:
    - `id`, `case_id`, `task_id`, `dataset`, `entry_point`
    - `slm_failure_type`, `slm_failure_summary`
    - `fix_actions`, `llm_code`, `fix_diff`, `prompt`, `run_dir`, `timestamp`
    - retrieval `score`
- `slm_attempt_XX/rag_context.txt`
  - formatted prompt-ready hint block built from hits:
    - case id/task
    - failure type
    - fix actions
    - retrieval score
    - optional import hints from diff
    - truncated diff excerpts

Before fallback attempt, `fallback_attempt_XX/prompt.txt` includes:
- previous SLM/fallback failures,
- self-debug notes (if generated),
- `RAG hints:` section from `rag_context.txt`.

### 10.4 Concrete Artifact Example (HumanEval/101)

Run directory:
- `episodes/humaneval_runs/20260222_182120_HumanEval_101`

Observed artifacts:
- `slm_attempt_01/rag_query.txt`
  - contains `entry_point: words_string`, `error_type: AssertionError`, full failure tail, and task prompt text.
- `slm_attempt_01/rag_hits.json`
  - contains exactly 3 retrieved cases with similarity scores.
- `slm_attempt_01/rag_context.txt`
  - includes structured cases and diff-based hints.
- `fallback_attempt_01/prompt.txt`
  - includes explicit `RAG hints:` section before final task prompt.

In this run, retrieval artifacts were successfully written before fallback prompting and the final status is `PASS` via fallback LLM.

## BigCodeBench Runs

# BigCodeBench Runs Session Log (Complete)

## 1) Session Metadata
- Project root: `/Users/ajayramesh/Documents/AIML/Masteers/ThesisImplementation/thesis-hybrid-sdlc-agent`
- Session topic: BigCodeBench task execution and diagnosis (stdlib subset), with SLM + LLM fallback.
- Primary execution date: March 10, 2026.
- Primary run output root: `episodes/bigcodebench_runs_fixcheck_v2`
- Main orchestrator script: `src/bigcodebench/run_bigcodebench_hybrid.py`

## 2) User Questions and Assistant Answers (BigCodeBench Session Transcript Summary)
1. User: Start BigCodeBench task session.
   Assistant: Agreed and prepared to identify task files and run plan.

2. User: There are ~3 BigCodeBench task lists (stdlib and API related); provide JSON task files.
   Assistant: Identified files under `data/external/bcb/`, including:
   - `data/external/bcb/bigcodebench_subset_stdlib.jsonl`
   - `data/external/bcb/bcb_rest_endpoint_tasks.jsonl`
   - `data/external/bcb/bigcodebench_subset.jsonl`
   - `data/external/bcb/bigcodebench_task_76.jsonl`

3. User: Show task prompts from API tasks file.
   Assistant: Parsed and shared API-task prompt details from the API-specific task file.

4. User: Show stdlib tasks.
   Assistant: Parsed and shared stdlib task details from `bigcodebench_subset_stdlib.jsonl`.

5. User: Run stdlib tasks one-by-one with 2 SLM attempts and 2 LLM fallback attempts.
   Assistant: Executed with requested attempt configuration and reported status task-by-task.

6. User: Confirm how many tasks were run and SLM/LLM pass/fail.
   Assistant: Reported aggregate counts and per-task outcomes.

7. User: Why taking long / why failures?
   Assistant: Explained runtime/test overhead, then investigated whether failures were code quality vs pipeline issues.

8. User: Would increasing generation length help? What fixes needed for SLM/LLM quality?
   Assistant: Implemented targeted runtime/prompt handling fixes, increased token budgets/timeouts, and reran.

9. User: Restart; accidentally interrupted.
   Assistant: Restarted and continued remaining tasks sequentially.

10. User: After every task, report SLM pass/fail and LLM pass/fail.
    Assistant: Reported after each completed task.

11. User: Analyze why most SLM tasks failed; did SLM produce logic or not?
    Assistant: Per-run artifact analysis showed SLM generally produced runnable code, but many outputs failed semantic correctness tests.

12. User: Why did LLM fail for remaining 12?
    Assistant: Categorized all 12 LLM failures. No API/network failures found; main causes were logic/runtime mistakes plus environment/timeouts.

13. User: Save entire BigCodeBench session with full details.
    Assistant: This file is that complete session log.

## 3) Data Files Used in This Session
- Main stdlib tasks file used for this run:
  - `data/external/bcb/bigcodebench_subset_stdlib.jsonl`
- Other BigCodeBench files identified during session:
  - `data/external/bcb/bcb_rest_endpoint_tasks.jsonl`
  - `data/external/bcb/bigcodebench_subset.jsonl`
  - `data/external/bcb/bigcodebench_task_76.jsonl`
- Existing BigCodeBench data card:
  - `reports/bigcodebench_datacard.md`

## 4) Run Configuration Used
- Script: `python src/bigcodebench/run_bigcodebench_hybrid.py`
- Key arguments used during the stdlib session:
  - `--tasks_path data/external/bcb/bigcodebench_subset_stdlib.jsonl`
  - `--task_index <index>`
  - `--slm_attempts 2`
  - `--fallback_attempts 2`
  - `--fallback_model gpt-4o-mini`
  - `--gguf_model_path models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`
  - `--out_dir episodes/bigcodebench_runs_fixcheck_v2`
- Patch-updated defaults in script (applied during session):
  - `--max_new_tokens` default: `1024` (was lower)
  - `--fallback_max_tokens` default: `1024`
  - `--test_timeout_s` default: `10`

## 5) Code Changes Applied During Session (to Improve Reliability)
File changed: `src/bigcodebench/run_bigcodebench_hybrid.py`

Implemented:
- Prompt preamble retention and reinjection:
  - `extract_prompt_preamble(...)`
  - `inject_required_preamble(...)`
- Syntax-aware repair loop:
  - `syntax_error_summary(...)`
  - `build_syntax_repair_prompt(...)`
  - Applied for both SLM and LLM fallback paths.
- Fallback path correction:
  - Ensured fallback output also preserves required imports/preamble after extraction/trim.
- Timeout stderr handling fix:
  - Added robust bytes-to-text conversion in timeout path.
- Budget/time defaults increased:
  - More output tokens and test timeout.

Impact observed:
- Syntax-truncation-style failures were significantly reduced in this run set.
- Remaining failures became mostly semantic/runtime/environment class.

## 6) Full Task-Level Results (This Session Run Set)
Source: `episodes/bigcodebench_runs_fixcheck_v2/runs_summary.jsonl` and each run directory `final_status.json`.

| Task ID | SLM | LLM Fallback | Run Directory |
|---|---|---|---|
| 4 | PASS | NOT_RUN | `20260310_084816_BigCodeBench_4` |
| 22 | FAIL | PASS | `20260310_084915_BigCodeBench_22` |
| 220 | FAIL | FAIL | `20260310_085246_BigCodeBench_220` |
| 270 | FAIL | FAIL | `20260310_085606_BigCodeBench_270` |
| 279 | FAIL | PASS | `20260310_085745_BigCodeBench_279` |
| 295 | FAIL | FAIL | `20260310_204411_BigCodeBench_295` |
| 320 | FAIL | FAIL | `20260310_204622_BigCodeBench_320` |
| 330 | PASS | NOT_RUN | `20260310_204826_BigCodeBench_330` |
| 348 | FAIL | PASS | `20260310_204914_BigCodeBench_348` |
| 400 | PASS | NOT_RUN | `20260310_205132_BigCodeBench_400` |
| 667 | PASS | NOT_RUN | `20260310_205435_BigCodeBench_667` |
| 669 | FAIL | PASS | `20260310_205522_BigCodeBench_669` |
| 670 | FAIL | PASS | `20260310_205719_BigCodeBench_670` |
| 733 | FAIL | FAIL | `20260310_205848_BigCodeBench_733` |
| 791 | FAIL | FAIL | `20260310_210049_BigCodeBench_791` |
| 795 | FAIL | PASS | `20260310_210321_BigCodeBench_795` |
| 820 | FAIL | FAIL | `20260310_210705_BigCodeBench_820` |
| 852 | PASS | NOT_RUN | `20260310_210907_BigCodeBench_852` |
| 854 | FAIL | PASS | `20260310_213545_BigCodeBench_854` |
| 861 | PASS | NOT_RUN | `20260310_213829_BigCodeBench_861` |
| 892 | FAIL | FAIL | `20260310_213936_BigCodeBench_892` |
| 896 | FAIL | PASS | `20260310_214106_BigCodeBench_896` |
| 928 | FAIL | FAIL | `20260310_214339_BigCodeBench_928` |
| 930 | FAIL | FAIL | `20260310_214613_BigCodeBench_930` |
| 931 | FAIL | PASS | `20260310_214756_BigCodeBench_931` |
| 957 | FAIL | PASS | `20260310_215035_BigCodeBench_957` |
| 958 | FAIL | PASS | `20260310_215218_BigCodeBench_958` |
| 1028 | FAIL | FAIL | `20260310_215408_BigCodeBench_1028` |
| 1104 | FAIL | FAIL | `20260310_215704_BigCodeBench_1104` |
| 1111 | FAIL | PASS | `20260310_220056_BigCodeBench_1111` |

## 7) Aggregate Metrics
- Total tasks in this stdlib run set: `30`
- SLM pass: `6`
- SLM fail: `24`
- For 24 SLM-failed tasks:
  - LLM pass: `12`
  - LLM fail: `12`
- LLM rescued on attempt-2 (attempt-1 fail -> attempt-2 pass): `2` tasks.

## 8) Why Most SLM Tasks Failed (Detailed Diagnosis)
SLM final-attempt failure categories across 30 tasks:
- logic/assertion mismatch: `13`
- timeout: `4`
- runtime/API misuse: `3`
- missing dependency (`faker`): `2`
- name error: `2`
- syntax/parse: `0`
- pass: `6`

Conclusion:
- SLM generally produced code (often executable), but failed mainly on semantic correctness and edge handling.
- This indicates model capability/fit limits on these tasks, not just output formatting.
- Infrastructure/environment also contributed (timeouts, missing external package in tests).

Examples:
- Logic mismatch: Task `670` assertion mismatch (`'bc' != 'c'`).
- Runtime/API misuse: Task `1028` used `platform.cpu_percent` (invalid API).
- Missing dependency: Tasks `270` and `295` failed due to missing `faker`.

## 9) Why LLM Failed for Remaining 12 (Detailed Diagnosis)
LLM failure categories for the 12 not recovered tasks:
- logic/assertion mismatch: `4` (`320, 733, 791, 892`)
- runtime/API bugs: `3` (`928, 930, 1028`)
- timeouts: `2` (`220, 1104`)
- missing dependency (`faker`): `2` (`270, 295`)
- name error: `1` (`820`)
- API/network failures: `0` detected in logs

Interpretation:
- 12/24 recovered is substantial and confirms fallback effectiveness.
- Remaining misses are not mostly network/API access problems.
- The unrecovered set is a combination of hard semantic tasks and environment/test constraints.

Additional note:
- In `bigcodebench_subset_stdlib.jsonl`, tasks `270` and `295` tests reference `faker`, which is not installed in the current environment. This created unavoidable failures unless dependency is installed or those tasks are filtered.

## 10) Session Conclusions Recorded
- SLM failed mostly because of semantic correctness limits, not because it returned no code.
- LLM fallback materially improved outcomes (recovered 12 of 24 SLM-failed tasks).
- Remaining LLM failures split between:
  - genuine logic/runtime misses,
  - environment constraints (`faker` missing),
  - timeout ceiling.
- Pipeline code quality improved during session (better code extraction/preamble/syntax-repair/timeout handling), reducing format-related failures.

## 11) Key Paths for Future Thesis Documentation
- Main run summary:
  - `episodes/bigcodebench_runs_fixcheck_v2/runs_summary.jsonl`
- Per-task artifact directories:
  - `episodes/bigcodebench_runs_fixcheck_v2/20260310_*_BigCodeBench_*`
- Orchestrator used:
  - `src/bigcodebench/run_bigcodebench_hybrid.py`
- Dataset used:
  - `data/external/bcb/bigcodebench_subset_stdlib.jsonl`
- Existing background data card:
  - `reports/bigcodebench_datacard.md`

## 12) Practical Next-Step Recommendations (Captured)
1. Install missing dependency for fair run on affected tasks:
   - `faker` for tasks with test-side dependency.
2. Re-run only 12 LLM-failed tasks with higher test timeout (for timeout-prone cases).
3. Optionally rerun those 12 with stronger fallback model to isolate residual model-vs-environment gap.

---

## 13) Task-Level Attempt Status (QuixBugs-Aligned Format)

This section mirrors the QuixBugs file style by recording per-task attempt outcomes explicitly.

Status code legend used below:
- `PASS`: tests passed.
- `ASSERT_FAIL`: assertion-level test failure.
- `TIMEOUT`: execution timeout in runner/tests.
- `SLM_TIMEOUT`: SLM generation timeout signature.
- `MODULE_NOT_FOUND`: missing dependency at runtime.
- `NAME_ERROR`, `TYPE_ERROR`, `VALUE_ERROR`, `KEY_ERROR`, `ATTR_ERROR`: Python runtime error classes.
- `RUNTIME_ERROR`: runtime failure (non-timeout).
- `JSON_DECODE`: parse error from generated/test path.
- `HARNESS_ERROR`: runner/harness execution error.
- `FAIL`: generic fail signature from run artifact.

| Task ID | Latest run dir | Final | Winner | Winner attempt | SLM attempts | LLM fallback attempts |
|---|---|---|---|---:|---|---|
| 4 | `20260310_084816_BigCodeBench_4` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| 22 | `20260310_084915_BigCodeBench_22` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:NAME_ERROR` | `fallback_01:PASS; fallback_02:-` |
| 220 | `20260310_085246_BigCodeBench_220` | FAIL | NONE | - | `attempt_01:TIMEOUT; attempt_02:TIMEOUT` | `fallback_01:TIMEOUT; fallback_02:TIMEOUT` |
| 270 | `20260310_085606_BigCodeBench_270` | FAIL | NONE | - | `attempt_01:MODULE_NOT_FOUND; attempt_02:MODULE_NOT_FOUND` | `fallback_01:MODULE_NOT_FOUND; fallback_02:MODULE_NOT_FOUND` |
| 279 | `20260310_085745_BigCodeBench_279` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS; fallback_02:-` |
| 295 | `20260310_204411_BigCodeBench_295` | FAIL | NONE | - | `attempt_01:MODULE_NOT_FOUND; attempt_02:MODULE_NOT_FOUND` | `fallback_01:MODULE_NOT_FOUND; fallback_02:MODULE_NOT_FOUND` |
| 320 | `20260310_204622_BigCodeBench_320` | FAIL | NONE | - | `attempt_01:HARNESS_ERROR; attempt_02:HARNESS_ERROR` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| 330 | `20260310_204826_BigCodeBench_330` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| 348 | `20260310_204914_BigCodeBench_348` | PASS | LLM | 1 | `attempt_01:TIMEOUT; attempt_02:TIMEOUT` | `fallback_01:PASS; fallback_02:-` |
| 400 | `20260310_205132_BigCodeBench_400` | PASS | SLM | 2 | `attempt_01:JSON_DECODE; attempt_02:PASS` | `none` |
| 667 | `20260310_205435_BigCodeBench_667` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| 669 | `20260310_205522_BigCodeBench_669` | PASS | LLM | 1 | `attempt_01:KEY_ERROR; attempt_02:TYPE_ERROR` | `fallback_01:PASS; fallback_02:-` |
| 670 | `20260310_205719_BigCodeBench_670` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS; fallback_02:-` |
| 733 | `20260310_205848_BigCodeBench_733` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| 791 | `20260310_210049_BigCodeBench_791` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:RUNTIME_ERROR` | `fallback_01:FAIL; fallback_02:FAIL` |
| 795 | `20260310_210321_BigCodeBench_795` | PASS | LLM | 1 | `attempt_01:TYPE_ERROR; attempt_02:ASSERT_FAIL` | `fallback_01:PASS; fallback_02:-` |
| 820 | `20260310_210705_BigCodeBench_820` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:NAME_ERROR; fallback_02:NAME_ERROR` |
| 852 | `20260310_210907_BigCodeBench_852` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| 854 | `20260310_213545_BigCodeBench_854` | PASS | LLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:ASSERT_FAIL; fallback_02:PASS` |
| 861 | `20260310_213829_BigCodeBench_861` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| 892 | `20260310_213936_BigCodeBench_892` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| 896 | `20260310_214106_BigCodeBench_896` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS; fallback_02:-` |
| 928 | `20260310_214339_BigCodeBench_928` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:TYPE_ERROR` | `fallback_01:KEY_ERROR; fallback_02:KEY_ERROR` |
| 930 | `20260310_214613_BigCodeBench_930` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:VALUE_ERROR; fallback_02:VALUE_ERROR` |
| 931 | `20260310_214756_BigCodeBench_931` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS; fallback_02:-` |
| 957 | `20260310_215035_BigCodeBench_957` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS; fallback_02:-` |
| 958 | `20260310_215218_BigCodeBench_958` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS; fallback_02:-` |
| 1028 | `20260310_215408_BigCodeBench_1028` | FAIL | NONE | - | `attempt_01:ATTR_ERROR; attempt_02:ATTR_ERROR` | `fallback_01:VALUE_ERROR; fallback_02:VALUE_ERROR` |
| 1104 | `20260310_215704_BigCodeBench_1104` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:TIMEOUT` | `fallback_01:TIMEOUT; fallback_02:TIMEOUT` |
| 1111 | `20260310_220056_BigCodeBench_1111` | PASS | LLM | 2 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:ASSERT_FAIL; fallback_02:PASS` |

---

## 14) Task-Wise Run Notes (Appendix, 30 Tasks)

- `BigCodeBench/4` (`20260310_084816_BigCodeBench_4`): SLM passed on attempt_01; fallback not needed.
- `BigCodeBench/22` (`20260310_084915_BigCodeBench_22`): LLM fallback recovered task on fallback attempt 1.
- `BigCodeBench/220` (`20260310_085246_BigCodeBench_220`): Not recovered; terminal signature `TIMEOUT`.
- `BigCodeBench/270` (`20260310_085606_BigCodeBench_270`): Not recovered; terminal signature `ModuleNotFoundError: No module named 'faker'`.
- `BigCodeBench/279` (`20260310_085745_BigCodeBench_279`): LLM fallback recovered task on fallback attempt 1.
- `BigCodeBench/295` (`20260310_204411_BigCodeBench_295`): Not recovered; terminal signature `ModuleNotFoundError: No module named 'faker'`.
- `BigCodeBench/320` (`20260310_204622_BigCodeBench_320`): Not recovered; terminal signature `AssertionError: None != 0`.
- `BigCodeBench/330` (`20260310_204826_BigCodeBench_330`): SLM passed on attempt_01; fallback not needed.
- `BigCodeBench/348` (`20260310_204914_BigCodeBench_348`): LLM fallback recovered task on fallback attempt 1.
- `BigCodeBench/400` (`20260310_205132_BigCodeBench_400`): SLM recovered on attempt_02; fallback not needed.
- `BigCodeBench/667` (`20260310_205435_BigCodeBench_667`): SLM passed on attempt_01; fallback not needed.
- `BigCodeBench/669` (`20260310_205522_BigCodeBench_669`): LLM fallback recovered task on fallback attempt 1.
- `BigCodeBench/670` (`20260310_205719_BigCodeBench_670`): LLM fallback recovered task on fallback attempt 1.
- `BigCodeBench/733` (`20260310_205848_BigCodeBench_733`): Not recovered; terminal signature `AssertionError: None != 1`.
- `BigCodeBench/791` (`20260310_210049_BigCodeBench_791`): Not recovered; terminal signature `FAIL` after fallback.
- `BigCodeBench/795` (`20260310_210321_BigCodeBench_795`): LLM fallback recovered task on fallback attempt 1.
- `BigCodeBench/820` (`20260310_210705_BigCodeBench_820`): Not recovered; terminal signature `NameError: name 'string' is not defined`.
- `BigCodeBench/852` (`20260310_210907_BigCodeBench_852`): SLM passed on attempt_01; fallback not needed.
- `BigCodeBench/854` (`20260310_213545_BigCodeBench_854`): LLM fallback recovered task on fallback attempt 2.
- `BigCodeBench/861` (`20260310_213829_BigCodeBench_861`): SLM passed on attempt_01; fallback not needed.
- `BigCodeBench/892` (`20260310_213936_BigCodeBench_892`): Not recovered; terminal signature `AssertionError: 1 != 10`.
- `BigCodeBench/896` (`20260310_214106_BigCodeBench_896`): LLM fallback recovered task on fallback attempt 1.
- `BigCodeBench/928` (`20260310_214339_BigCodeBench_928`): Not recovered; terminal signature `KeyError: 'zz'`.
- `BigCodeBench/930` (`20260310_214613_BigCodeBench_930`): Not recovered; terminal signature `ValueError: Input must only contain letters`.
- `BigCodeBench/931` (`20260310_214756_BigCodeBench_931`): LLM fallback recovered task on fallback attempt 1.
- `BigCodeBench/957` (`20260310_215035_BigCodeBench_957`): LLM fallback recovered task on fallback attempt 1.
- `BigCodeBench/958` (`20260310_215218_BigCodeBench_958`): LLM fallback recovered task on fallback attempt 1.
- `BigCodeBench/1028` (`20260310_215408_BigCodeBench_1028`): Not recovered; terminal signature `ValueError: invalid literal for int() with base 10: ''`.
- `BigCodeBench/1104` (`20260310_215704_BigCodeBench_1104`): Not recovered; terminal signature `TIMEOUT`.
- `BigCodeBench/1111` (`20260310_220056_BigCodeBench_1111`): LLM fallback recovered task on fallback attempt 2.

---

## 15) Terminal Failure Taxonomy (Unrecovered 12 Tasks)

Terminal signature categories for the `12` unrecovered tasks:
- `TIMEOUT`: `2` tasks (`220`, `1104`)
- `MODULE_NOT_FOUND`: `2` tasks (`270`, `295`)
- `ASSERT_FAIL`: `3` tasks (`320`, `733`, `892`)
- `FAIL` (generic): `1` task (`791`)
- `NAME_ERROR`: `1` task (`820`)
- `KEY_ERROR`: `1` task (`928`)
- `VALUE_ERROR`: `2` tasks (`930`, `1028`)

Thesis-use interpretation:
- Recovery via fallback is strong (`12` recovered), but remaining failures are a mixed set of environment constraints (`faker`), timeout ceilings, and hard semantic/runtime mismatch.
- Attempt-level logs now provide direct evidence of exactly which stage failed (`SLM attempt_01/02`, `fallback_01/02`) for each task.

## RAG Runs

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

## LoRA Approach Runs

Screenshot file: `lora_approach_runs.png`

![LoRA Approach Runs](./lora_approach_runs.png)

## Metrics Appendix (Timing, Tokens, and I/O Size)

### A) What Is Measured vs Not Measured

- `elapsed_s` in `result.json` is **test execution time** for generated code, not model generation latency.
- True OpenAI usage fields (`prompt_tokens`, `completion_tokens`, `total_tokens`) are not persisted in run artifacts.
- HumanEval/BigCodeBench v2 runners do not persist llama-cli token/time perf counters.
- QuixBugs orchestrator captures llama-cli perf lines in `slm_err.txt`; those were parsed for SLM timing/token stats.

### B) Availability Matrix

| Scope | SLM generation time | LLM generation time | True token usage | Prompt/output size proxy |
|---|---|---|---|---|
| QuixBugs (captured runs) | Available for most SLM attempts via `common_perf_print` | Not recorded | SLM only (from llama perf), LLM not recorded | Available (`prompt.txt`, `slm_raw.txt`, `llm_raw.txt`) |
| HumanEval initial 164 | Not recorded | Not recorded | Not recorded | Available (`prompt.txt`, `slm_raw.txt`) |
| HumanEval RAG latest 67 | Not recorded | Not recorded | Not recorded | Available (`prompt.txt`, `slm_raw.txt`, `llm_raw.txt`, RAG files) |
| BigCodeBench stdlib 30 | Not recorded | Not recorded | Not recorded | Available (`prompt.txt`, `slm_raw.txt`, `llm_raw.txt`) |

### C) QuixBugs Metrics (Runs Referenced in QuixBugs Section)

Coverage extracted from run directories referenced in `quixbug_runs_file.md`:
- Run directories parsed: `26`
- SLM attempt dirs: `55`
- Fallback attempt dirs: `34`

SLM llama perf (`slm_err.txt -> common_perf_print`) stats:
- Attempts with parsed perf: `52/55` (missing `3`)
- `total time` per SLM attempt: min `23.86s`, mean `69.30s`, median `59.22s`, max `230.56s`
- `total tokens` per SLM attempt: min `299`, mean `801.15`, median `685`, max `2466`
- `prompt tokens`: min `210`, mean `630.48`, median `466.5`, max `2334`
- `generation tokens` (`eval runs`): min `73`, mean `170.67`, median `148`, max `489`

I/O size proxies:
- SLM prompt chars: min `665`, mean `9700.82`, median `1603`, max `147182`
- SLM raw output chars: min `0`, mean `2225.05`, median `2107`, max `5570`
- Fallback prompt chars: min `1074`, mean `10969.32`, median `2048`, max `147862`
- Fallback raw output chars (available files): min `344`, mean `872.77`, median `762`, max `1847`
- Fallback attempts missing `llm_raw.txt`: `4/34`

### D) HumanEval Initial 164 Metrics

Coverage (same selection as HumanEval section: earliest run per task):
- Run directories: `164`
- SLM attempt dirs: `276`
- Fallback attempt dirs: `0`

Test runtime (`elapsed_s`) on SLM attempts:
- Count: `276`
- min `0.00s`, mean `0.08s`, median `0.05s`, max `5.01s`
- Zero-duration entries: `73` (typically timeout/error paths)
- Near timeout (>= `4.9s`): `2`

I/O size proxies:
- SLM prompt chars: min `308`, mean `850.68`, median `731.5`, max `2219`
- SLM raw output chars: min `0`, mean `936.22`, median `782.5`, max `11868`

Token note:
- True token usage not persisted; only size proxies are available for this phase.

### E) HumanEval RAG Phase Metrics (Latest Per 67 RAG Tasks)

Coverage:
- Run directories: `67`
- SLM attempt dirs: `134`
- Fallback attempt dirs: `90`

Test runtime (`elapsed_s`):
- SLM attempts (`n=134`): min `0.00s`, mean `0.09s`, median `0.00s`, max `5.05s`
- Fallback attempts with result (`n=87`): min `0.05s`, mean `0.21s`, median `0.10s`, max `1.35s`
- SLM zero-duration entries: `85`

I/O size proxies:
- SLM prompt chars: min `435`, mean `1584.49`, median `1657`, max `3703`
- SLM raw output chars: min `0`, mean `4371.63`, median `0`, max `14456`
- Fallback prompt chars: min `1717`, mean `2685.28`, median `2585.5`, max `3974`
- Fallback raw output chars (`n=87`): min `85`, mean `265.25`, median `242`, max `923`

RAG payload sizes:
- `rag_query.txt` chars (`n=132`): min `251`, mean `793.27`, median `737`, max `2058`
- `rag_context.txt` chars (`n=132`): min `1008`, mean `1196.31`, median `1200`, max `1200`
- `rag_hits.json` retrieved hits per attempt (`n=132`): min/mean/median/max = `3 / 3 / 3 / 3`

Token note:
- True SLM/LLM token usage not persisted in this phase.

### F) BigCodeBench Stdlib Metrics (30-Task Session Set)

Coverage:
- Run directories: `30`
- SLM attempt dirs: `55`
- Fallback attempt dirs: `38`

Test runtime (`elapsed_s`):
- SLM attempts (`n=55`): min `0.00s`, mean `1.05s`, median `0.15s`, max `10.02s`
- Fallback attempts (`n=38`): min `0.05s`, mean `1.54s`, median `0.09s`, max `10.01s`
- Near timeout (>= `9.9s`): SLM `5`, fallback `4`

I/O size proxies:
- SLM prompt chars: min `765`, mean `1432.91`, median `1388`, max `2293`
- SLM raw output chars: min `0`, mean `2423.40`, median `2391`, max `4172`
- Fallback prompt chars: min `1153`, mean `2105.95`, median `2154`, max `2914`
- Fallback raw output chars: min `152`, mean `495.08`, median `394`, max `3128`

Token note:
- True SLM/LLM token usage not persisted for this run set.

### G) Practical Interpretation for Thesis Results Writing

- The report now includes measured runtime and size proxies from artifacts across all run sections.
- For HumanEval/BigCodeBench, runtime reflects test execution only; generation latency and API token usage are missing by design of current logging.
- For QuixBugs, SLM generation time/token information is available from llama perf logs and can be used as the strongest quantitative generation-efficiency evidence in this workspace.
