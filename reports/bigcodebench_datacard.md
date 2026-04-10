# BigCodeBench Data Card (Project-Specific, Initial Data Preparation)

## 1) Dataset Identity

- **Dataset name (project):** `BigCodeBench`
- **Primary benchmark-like task file used by v1 runner in this repo:**
  - `data/external/bcb/bigcodebench_subset.jsonl`
- **Primary task file used by v2 runner in this repo:**
  - `data/external/bcb/bigcodebench_subset_stdlib.jsonl`
- **Additional derived task file used for REST-endpoint-focused experiments:**
  - `data/external/bcb/bcb_rest_endpoint_tasks.jsonl`
- **Dataset type:** Python code-generation benchmark tasks with executable tests and explicit function-call/tool-use requirements.

### Web-verified upstream benchmark facts

- Upstream dataset page (`bigcode/bigcodebench`) defines two variants:
  - **BigCodeBench-Complete**
  - **BigCodeBench-Instruct**
- Upstream statistics (dataset card):
  - **1,140 tasks** per variant
  - **~5.6 tests/task**
  - **~99% average branch coverage**
- BigCodeBench paper reports:
  - **139 libraries**
  - **7 domains**
  - strong gap between current LLMs and human performance on complex instruction-following/tool use.
- Upstream repository/license:
  - `bigcode-project/bigcodebench`
  - **Apache-2.0**

## 2) Source and Provenance (Confirmed vs Inferred)

### Confirmed

- Local BigCodeBench files in this workspace are under:
  - `data/external/bcb`
- Current file counts:
  - `bigcodebench_subset.jsonl`: **66** rows
  - `bigcodebench_subset_stdlib.jsonl`: **30** rows
  - `bcb_rest_endpoint_tasks.jsonl`: **10** rows
  - `bigcodebench_task_76.jsonl`: **1** row
  - `bcb_algo_subset_candidates.jsonl`: **23** rows
  - `bcb_keyword_matches.jsonl`: **48** rows
  - `bcb_algo_family_candidates.jsonl`: **0** rows (empty)
- The local 66-row subset schema is stable and matches runner expectations:
  - `task_id`, `complete_prompt`, `instruct_prompt`, `canonical_solution`, `code_prompt`, `test`, `entry_point`, `doc_struct`, `libs`
- `run_bigcodebench_hybrid.py` default:
  - `--tasks_path data/external/bcb/bigcodebench_subset.jsonl`
- `run_bigcodebench_hybrid_v2.py` default:
  - `--tasks_path data/external/bcb/bigcodebench_subset_stdlib.jsonl`

### Inferred

- No script is present in this repo that originally creates `bigcodebench_subset.jsonl` from the full 1,140-task upstream dataset.
- The 66-row subset was likely prepared externally (or in an earlier session) and then checked in.

## 3) What BigCodeBench Contains (Local Copy)

In this project, `data/external/bcb/bigcodebench_subset.jsonl` is the local benchmark-facing dataset file.

Each row contains:

- `task_id`: canonical id (for example `BigCodeBench/4`)
- `complete_prompt`: full PEP257-style docstring prompt
- `instruct_prompt`: instruction-focused variant
- `canonical_solution`: reference solution
- `code_prompt`: import + function signature scaffold
- `test`: executable `unittest` test code
- `entry_point`: function name to evaluate
- `doc_struct`: structured prompt metadata
- `libs`: required/expected libraries

Observed local stats for this 66-row file:

- task IDs span from `BigCodeBench/4` to `BigCodeBench/1111` (non-contiguous subset)
- all rows include non-empty library requirement data (`libs`)

### Example 1: One source dataset row (from `bigcodebench_subset.jsonl`)

```json
{
  "task_id": "BigCodeBench/4",
  "entry_point": "task_func",
  "libs": "['collections', 'itertools']",
  "instruct_prompt_preview": "Count the occurrence of each integer in the values of the input dictionary, where each value is a list of integers, and return a dictionary with these counts...",
  "test_preview": "import unittest class TestCases(unittest.TestCase): def test_case_1(self): ..."
}
```

## 4) What BigCodeBench Task Files Contain in This Thesis Project

### A) v1 task file (broader subset)

- File: `data/external/bcb/bigcodebench_subset.jsonl`
- Rows: **66**
- Used by default in:
  - `src/bigcodebench/run_bigcodebench_hybrid.py`
  - `scripts/run_bigcodebench_remaining.py`

### B) v2 task file (stdlib-only subset)

- File: `data/external/bcb/bigcodebench_subset_stdlib.jsonl`
- Rows: **30**
- Used by default in:
  - `src/bigcodebench/run_bigcodebench_hybrid_v2.py`
- Produced by script:
  - `scripts/build_bigcodebench_stdlib_subset.py`
- Relation: all 30 tasks are a subset of the 66-row file.

### C) REST-endpoint focused file

- File: `data/external/bcb/bcb_rest_endpoint_tasks.jsonl`
- Rows: **10**
- Row schema:
  - `task_id`, `split`, `libs`, `prompt_preview`
- Purpose: lightweight index/manifest for API-endpoint-style task selection, not direct runner input (unless transformed back to full task rows).

### Example 2: One project task row (from `bcb_rest_endpoint_tasks.jsonl`)

```json
{
  "task_id": "BigCodeBench/81",
  "split": "v0.1.0_hf",
  "libs": ["flask", "flask_restful", "requests"],
  "prompt_preview": "Creates a Flask application with a RESTful API endpoint..."
}
```

## 5) Why These Task Files Exist in This Project

- `bigcodebench_subset.jsonl` provides a manageable evaluation subset for local SLM/fallback runs.
- `bigcodebench_subset_stdlib.jsonl` isolates tasks that do not require non-stdlib dependencies, improving reproducibility and reducing environment failures.
- `bcb_rest_endpoint_tasks.jsonl` supports topic-focused analysis (REST/API endpoint tasks) for targeted experiments and reporting.

## 6) How Project BigCodeBench Files Were Prepared (Confirmed vs Inferred)

### Confirmed

- `bigcodebench_subset_stdlib.jsonl` is generated by:
  - `scripts/build_bigcodebench_stdlib_subset.py`
- Generation logic:
  - parse each row from `bigcodebench_subset.jsonl`
  - infer required modules from both `libs` and import lines in `code_prompt`
  - keep task only if required modules are within computed stdlib set
  - write resulting rows to `bigcodebench_subset_stdlib.jsonl`

### Inferred

- `bigcodebench_subset.jsonl` was likely extracted from upstream `bigcode/bigcodebench` by selecting a custom subset relevant to this project’s compute envelope and evaluation goals.
- `bcb_rest_endpoint_tasks.jsonl` appears to be generated by filtering BigCodeBench tasks for framework/endpoint patterns and storing a compact manifest (`task_id`, `split`, `libs`, prompt preview).

## 7) Inferred Pseudo-Generator Scripts (Documentation Reconstruction)

> These are reconstructions from repository evidence; not original historical scripts.

### A) Upstream -> local subset (inferred)

```python
# pseudo_build_bigcodebench_subset.py
from datasets import load_dataset
import json

rows = []
for split in ["v0.1.0_hf", "v0.1.1", "v0.1.2", "v0.1.3", "v0.1.4"]:
    ds = load_dataset("bigcode/bigcodebench", split=split)
    for r in ds:
        if keep_for_project(r):  # project-specific filter
            rows.append({
                "task_id": r["task_id"],
                "complete_prompt": r["complete_prompt"],
                "instruct_prompt": r["instruct_prompt"],
                "canonical_solution": r["canonical_solution"],
                "code_prompt": r["code_prompt"],
                "test": r["test"],
                "entry_point": r["entry_point"],
                "doc_struct": r["doc_struct"],
                "libs": r["libs"],
            })

with open("data/external/bcb/bigcodebench_subset.jsonl", "w", encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
```

### B) Subset -> REST endpoint manifest (inferred)

```python
# pseudo_build_bcb_rest_endpoint_tasks.py
import json

KEYWORDS = ["flask", "django", "fastapi", "route", "apirouter", "httpresponse", "restful", "endpoint"]

out = []
for line in open("data/external/bcb/bigcodebench_subset.jsonl", encoding="utf-8"):
    if not line.strip():
        continue
    r = json.loads(line)
    blob = " ".join([
        str(r.get("instruct_prompt", "")),
        str(r.get("complete_prompt", "")),
        str(r.get("libs", "")),
    ]).lower()
    if any(k in blob for k in KEYWORDS):
        out.append({
            "task_id": r["task_id"],
            "split": r.get("split", "v0.1.x_unknown"),
            "libs": r.get("libs", []),
            "prompt_preview": (r.get("instruct_prompt", "")[:220]).replace("\n", " "),
        })

with open("data/external/bcb/bcb_rest_endpoint_tasks.jsonl", "w", encoding="utf-8") as f:
    for row in out:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
```

## 8) Data Integrity and Reproducibility Notes for Thesis

- `bigcodebench_subset.jsonl` is not the full upstream benchmark; document it explicitly as a project subset.
- `bigcodebench_subset_stdlib.jsonl` is deterministic given:
  - input subset
  - current stdlib module list logic in `build_bigcodebench_stdlib_subset.py`
- `bcb_rest_endpoint_tasks.jsonl` is a compact index and does not include test/canonical solution fields; it is not a drop-in replacement for runner task files.
- BigCodeBench tasks can depend on third-party libraries; environment parity strongly affects execution pass rates.

## 9) Practical Conclusion

- For broad local BigCodeBench evaluation in this repo: use `data/external/bcb/bigcodebench_subset.jsonl`.
- For v2/stability-focused runs: use `data/external/bcb/bigcodebench_subset_stdlib.jsonl`.
- For endpoint-focused analysis only: use `data/external/bcb/bcb_rest_endpoint_tasks.jsonl`.

## 10) External References (for Thesis Documentation)

- BigCodeBench dataset card (Hugging Face):
  - `https://huggingface.co/datasets/bigcode/bigcodebench`
- BigCodeBench repository:
  - `https://github.com/bigcode-project/bigcodebench`
- BigCodeBench paper:
  - `https://arxiv.org/abs/2406.15877`
