# QuixBugs Runs File v2 (Complete — Verified from Artifacts)

Date generated: 2026-04-03

## 1) Scope and Selection Rule
- Source: `episodes/quixbugs_runs/attempts/` — latest run per task, verified from actual artifacts.
- Coverage: `16` tasks (task index `0` to `15`).
- Key difference from v1: v1 had task 4 (`detect_cycle`) incorrectly labeled as `FAIL_AFTER_APPLY`. This file corrects that to `PASS` based on artifact inspection.

---

## 2) Core Metrics (All Runs, Latest Per Task)

- Total tasks: `16`
- Final PASS: `7`
- Final FAIL: `9`

**PASS breakdown by model:**
- PASS by SLM: `5`
  - SLM pass on attempt-1: `5` (tasks 4, 5, 6, 7, 8)
  - SLM pass on attempt-2 or later: `0`
- PASS by LLM fallback: `2`
  - LLM pass on fallback attempt-1: `1` (task 0 — bitcount)
  - LLM pass on fallback attempt-2: `1` (task 2 — bucketsort)

**SLM failures that triggered LLM fallback: `11` tasks**
- LLM rescued: `2`
- Still FAIL after LLM: `9`

---

## 3) Status Legend
- `PASS`: tests passed
- `FAIL_AFTER_APPLY`: patch applied but tests still failed
- `PATCH_APPLY_FAIL`: patch could not be applied (context/format/hunk mismatch)
- `DIFF_NOT_APPLIED`: diff produced but not applied (duplicate suppression or no actionable content)
- `MODEL_OUTPUT_NO_DIFF`: model output existed but no usable diff could be extracted

---

## 4) Task-Level Attempt Status (All 16)

| Task idx | Algo | Latest run dir | Final | SLM attempts | LLM fallback attempts |
|---|---|---|---|---|---|
| 0 | bitcount | `20260310_051255_bitcount` | PASS | `attempt_01:FAIL_AFTER_APPLY; attempt_02:FAIL_AFTER_APPLY; attempt_03:DIFF_NOT_APPLIED` | `fallback_01:PASS` |
| 1 | breadth_first_search | `20260310_052650_breadth_first_search` | FAIL | `attempt_01:PATCH_APPLY_FAIL; attempt_02:PATCH_APPLY_FAIL; attempt_03:PATCH_APPLY_FAIL` | `fallback_01:FAIL_AFTER_APPLY; fallback_02:FAIL_AFTER_APPLY` |
| 2 | bucketsort | `20260309_202852_bucketsort` | PASS | `attempt_01:PATCH_APPLY_FAIL; attempt_02:PATCH_APPLY_FAIL` | `fallback_01:PATCH_APPLY_FAIL; fallback_02:PASS` |
| 3 | depth_first_search | `20260309_205140_depth_first_search` | FAIL | `attempt_01:MODEL_OUTPUT_NO_DIFF; attempt_02:MODEL_OUTPUT_NO_DIFF; attempt_03:MODEL_OUTPUT_NO_DIFF` | `fallback_01:PATCH_APPLY_FAIL; fallback_02:PATCH_APPLY_FAIL` |
| 4 | detect_cycle | `20260309_215320_detect_cycle` | PASS | `attempt_01:PASS` | `none` |
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

## 5) SLM Failure Groups (attempt_01 error type)

Covers all 11 tasks where SLM failed on attempt-1.

| SLM Failure Type | Total tasks | LLM rescued | Still FAIL |
|---|---|---|---|
| **FAIL_AFTER_APPLY** | **5** | 1 (task 0) | 4 (10, 11, 14, 15) |
| **PATCH_APPLY_FAIL** | **5** | 1 (task 2) | 4 (1, 9, 12, 13) |
| **MODEL_OUTPUT_NO_DIFF** | **1** | 0 | 1 (3) |
| **Total** | **11** | **2** | **9** |

### 5.1 FAIL_AFTER_APPLY — 5 tasks (0, 10, 11, 14, 15)
- Patch was applied to the file but tests still failed after patching.
- Root cause: SLM generated a syntactically valid diff but the logic fix was semantically incorrect.
- LLM recovery: only task 0 (bitcount) recovered — SLM timed out post-apply, LLM fallback-01 fixed it.
- Tasks 10, 11, 14, 15: both SLM and LLM applied patches but logic remained wrong throughout.

### 5.2 PATCH_APPLY_FAIL — 5 tasks (1, 2, 9, 12, 13)
- Patch could not be applied — hunk context mismatch, `NO_HUNKS`, or format error.
- Root cause: SLM generated diffs with incorrect context lines or unstable hunk headers.
- LLM recovery: only task 2 (bucketsort) recovered on fallback_02.
- Tasks 1, 9, 12, 13: LLM either also failed to apply (task 9 fallback_01, task 1 all attempts) or applied but could not fix logic.

### 5.3 MODEL_OUTPUT_NO_DIFF — 1 task (3)
- SLM produced output but no extractable unified diff.
- Root cause: depth_first_search — model generated explanation text instead of a valid patch.
- LLM recovery: both fallback attempts also failed with PATCH_APPLY_FAIL (hunk context mismatch).

---

## 6) LLM Fallback Failure Analysis (9 tasks still FAIL)

| Task | Algo | LLM fallback outcome | Root cause |
|---|---|---|---|
| 1 | breadth_first_search | both FAIL_AFTER_APPLY | Patch applied but `IndexError: pop from an empty deque` remained |
| 3 | depth_first_search | both PATCH_APPLY_FAIL | Hunk context mismatch on both attempts |
| 9 | get_factors | fallback_01:PATCH_APPLY_FAIL; fallback_02:FAIL_AFTER_APPLY | Context mismatch then wrong logic — output wrong on 10/11 cases |
| 10 | hanoi | both FAIL_AFTER_APPLY | Patch applied but move sequence logic still incorrect (7/8 cases failed) |
| 11 | is_valid_parenthesization | both FAIL_AFTER_APPLY | Patch applied but `((` case returned wrong result |
| 12 | kheapsort | both FAIL_AFTER_APPLY | Patch applied but output duplicated elements — heap logic still wrong |
| 13 | knapsack | both FAIL_AFTER_APPLY | Patch applied but test still timed out — knapsack recursion unresolved |
| 14 | kth | both FAIL_AFTER_APPLY | SLM introduced `RecursionError`; LLM changed to `IndexError` — neither correct |
| 15 | lcs_length | both FAIL_AFTER_APPLY | SLM: `KeyError`; LLM: worsened to `IndexError` (invalid boundary change) |

---

## 7) Results Metrics Snapshot

- Total tasks: `16`
- Final PASS: `7` (`43.8%`)
- Final FAIL: `9` (`56.3%`)

**SLM performance:**
- SLM total PASS: `5` (`31.3%` of 16)
- SLM pass on attempt-1: `5`
- SLM pass on attempt-2 or later: `0`

**LLM fallback performance:**
- LLM invoked on: `11` tasks (where SLM failed)
- LLM total PASS: `2` (`18.2%` of tasks where LLM was invoked)
- LLM pass on fallback attempt-1: `1` (bitcount)
- LLM pass on fallback attempt-2: `1` (bucketsort)

**Attempt outcome tag frequency (all SLM + LLM attempts across 16 tasks):**
- `FAIL_AFTER_APPLY`: `23`
- `PATCH_APPLY_FAIL`: `19`
- `PASS`: `7`
- `DIFF_NOT_APPLIED`: `3`
- `MODEL_OUTPUT_NO_DIFF`: `3`

**Key insight:**
- Dominant SLM failure pressure was split evenly between `PATCH_APPLY_FAIL` (format fragility) and `FAIL_AFTER_APPLY` (semantic incorrectness).
- LLM fallback had very low recovery rate (18.2%) — most hard tasks remained semantically unresolved even after LLM attempts.
- `MODEL_OUTPUT_NO_DIFF` (task 3) represents a complete generation failure — model did not produce any actionable diff.
