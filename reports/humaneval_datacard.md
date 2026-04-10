# HumanEval Data Card (Project-Specific, Initial Data Preparation)

## 1) Dataset Identity

- **Dataset name (project):** `HumanEval`
- **Primary benchmark file used in this repository:**
  - `data/external/humaneval/humaneval_train.jsonl`
- **Additional project task manifest used for targeted reruns:**
  - `reports/failed_slm_tasks.jsonl`
- **Dataset type:** executable Python programming tasks (prompt + reference solution + test harness + entry point).

### Critical naming clarification

- `data/external/humaneval/humaneval_train.jsonl` is the **benchmark task file** name as stored in this repo.
- It is **not** the LoRA fine-tuning split file (`data/derived/finetune/...train.jsonl`).
- Therefore, in this project, the word `train` appears in two different contexts:
  - benchmark file naming (`humaneval_train.jsonl`)
  - fine-tune split naming (`*.cleaned.train.jsonl`)

## 2) Source and Provenance (Confirmed vs Inferred)

### Confirmed

- Local HumanEval data exists at:
  - `data/external/humaneval/humaneval_train.jsonl`
- Local file count in `data/external/humaneval`: **1 file** (`humaneval_train.jsonl`).
- Benchmark row count: **164** tasks.
- Task IDs span: `HumanEval/0` to `HumanEval/163`.
- Repository-wide check in current workspace finds no HumanEval task IDs above `HumanEval/163` and no 168-task HumanEval task file.
- The v2 runner default task source is:
  - `src/humaneval/run_humaneval_hybrid_v2.py` with `--tasks_path data/external/humaneval/humaneval_train.jsonl`.

### Inferred

- No explicit download/preparation script for `humaneval_train.jsonl` is currently checked in.
- Based on schema and task-id coverage, this local file aligns with the standard HumanEval benchmark format.

### Web-verified upstream benchmark facts

- OpenAI HumanEval is described as a **hand-written programming task benchmark** for functional correctness evaluation.
- Upstream package includes data for **164 problems**.
- Upstream README includes a security warning that executing model-generated code requires sandboxing and caution.

### Timing evidence from file timestamps (current workspace)

- `data/external/humaneval/humaneval_train.jsonl`: **Feb 1, 2026**
- `data/derived/finetune/humaneval_slm_fix_pairs.cleaned.train.jsonl`: **Feb 15, 2026**
- `src/humaneval/run_humaneval_hybrid_v2.py`: **Feb 21, 2026**

Interpretation:

- The benchmark task file existed before v2 in this workspace snapshot.
- Fine-tuning train split files were created later than the benchmark task file.

## 3) What HumanEval Contains (Local Copy)

Each JSONL row contains the fields:

- `task_id`: canonical ID (for example `HumanEval/0`)
- `prompt`: natural-language task statement + function signature/starter code
- `canonical_solution`: reference implementation
- `test`: executable Python test harness (`check(candidate)` style)
- `entry_point`: function name expected from generated code

Additional observed metadata notes:

- `test` strings contain `METADATA` blocks in many rows.
- `dataset: 'test'` appears inside the test harness metadata for a subset of tasks; this is benchmark-internal metadata, not a train/val/test split file.

### Example 1: One HumanEval benchmark row (from `humaneval_train.jsonl`)

```json
{
  "task_id": "HumanEval/0",
  "prompt": "from typing import List\\n\\n\\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\\n    ...",
  "canonical_solution": "    for idx, elem in enumerate(numbers):\\n        ...\\n    return False\\n",
  "test": "\\n\\nMETADATA = {\\n    'author': 'jt',\\n    'dataset': 'test'\\n}\\n\\ndef check(candidate):\\n    assert ...\\n",
  "entry_point": "has_close_elements"
}
```

## 4) What HumanEval Task Files Contain in This Thesis Project

### A) Canonical full benchmark task file

- File: `data/external/humaneval/humaneval_train.jsonl`
- Rows: **164**
- Usage: default input to HumanEval hybrid runners (`run_humaneval_hybrid.py` and `run_humaneval_hybrid_v2.py`).

### B) Targeted rerun task file

- File: `reports/failed_slm_tasks.jsonl`
- Rows: **66**
- ID range in this file: `HumanEval/26` to `HumanEval/163` (non-contiguous subset)
- Schema: exactly same fields as canonical benchmark rows.
- Row equality check: all 66 rows are exact row copies from `humaneval_train.jsonl` for those task IDs.

### Example 2: One project task row (from `reports/failed_slm_tasks.jsonl`)

```json
{
  "task_id": "HumanEval/26",
  "prompt": "from typing import List\\n\\n\\ndef remove_duplicates(numbers: List[int]) -> List[int]:\\n    ...",
  "canonical_solution": "    import collections\\n    c = collections.Counter(numbers)\\n    ...",
  "test": "\\n\\nMETADATA = {\\n    'author': 'jt',\\n    'dataset': 'test'\\n}\\n\\ndef check(candidate):\\n    assert ...",
  "entry_point": "remove_duplicates"
}
```

## 5) Why These Task Files Exist in This Project

- `humaneval_train.jsonl` is the **canonical benchmark interface** for full HumanEval runs.
- `failed_slm_tasks.jsonl` is an **operational subset interface** used to rerun selected failed tasks with fallback logic in `scripts/run_failed_slm_tasks_with_fallback.py`.
- This separation allows:
  - full benchmark evaluation from a stable source file
  - faster targeted reruns for debugging/fallback experiments.

## 6) How `failed_slm_tasks.jsonl` Was Created (Confirmed vs Inferred)

### Confirmed

- No dedicated generator script is present in the repo for this file.
- The set of 66 task IDs in `failed_slm_tasks.jsonl` exactly equals:
  - `reports/fallback_ok_tasks.json` (**38** IDs)
  - union
  - `reports/fallback_fail_tasks.json` (**28** IDs)
- Therefore: `38 + 28 = 66`, no overlap.

### Also confirmed (consistency check against summary artifacts)

- `reports/humaneval_failed_attempts_summary.json` reports `failed_total = 92`.
- `reports/humaneval_failed_attempts_report.txt` contains **92** unique failed task IDs.
- `failed_slm_tasks.jsonl` includes **66** of those 92 failed IDs.
- Missing from 66-subset relative to 92-summary: **26** task IDs  
  (`HumanEval/0,1,4,5,6,7,8,9,12,14,17,19,20,21,22,25,33,37,54,64,67,69,70,71,75,77`).

### Strong inference

- The subset file was likely built by taking selected fallback-processed IDs and extracting the corresponding full rows from `humaneval_train.jsonl`.

## 7) Inferred Pseudo-Generator Script (Documentation Reconstruction)

> This is reconstructed from repository artifacts; it is not an original historical script from the project.

```python
import json

with open("data/external/humaneval/humaneval_train.jsonl", "r", encoding="utf-8") as f:
    base_rows = [json.loads(line) for line in f if line.strip()]

with open("reports/fallback_ok_tasks.json", "r", encoding="utf-8") as f:
    ok_ids = set(json.load(f))

with open("reports/fallback_fail_tasks.json", "r", encoding="utf-8") as f:
    fail_ids = set(json.load(f))

target_ids = ok_ids | fail_ids

with open("reports/failed_slm_tasks.jsonl", "w", encoding="utf-8") as out:
    for row in base_rows:
        if row["task_id"] in target_ids:
            out.write(json.dumps(row, ensure_ascii=False) + "\\n")
```

## 8) Data Integrity and Reproducibility Notes for Thesis

- All HumanEval task files used here are JSONL and line-delimited task objects.
- The operational subset (`failed_slm_tasks.jsonl`) is schema-compatible with the full benchmark and can be passed directly via `--tasks_path`.
- For thesis reproducibility, document both:
  - canonical file (`humaneval_train.jsonl`, 164 tasks), and
  - subset file (`failed_slm_tasks.jsonl`, 66 tasks), including selection rule provenance.

## 9) Practical Conclusion

- For benchmark-level reporting: use `data/external/humaneval/humaneval_train.jsonl`.
- For targeted fallback/rerun experiments: use `reports/failed_slm_tasks.jsonl`.
- If you need strict alignment with the 92-task failure summary, regenerate a new subset directly from `reports/humaneval_failed_attempts_report.txt`.
- Current repository evidence supports **164 benchmark tasks**, not 168, for the HumanEval task file used by v2.

## 10) External References (for Thesis Documentation)

- HumanEval upstream repository:
  - `https://github.com/openai/human-eval`
