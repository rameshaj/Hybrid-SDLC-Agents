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
