# QuixBugs Data Card (Project-Specific)

## 1) Dataset Identity

- **Dataset name (project):** `quixbugs` (Python task manifest form)
- **Primary task files used by this thesis code:**
  - `data/quixbugs_tasks.jsonl`
  - `data/quixbugs_tasks_v2.jsonl`
- **Upstream benchmark repo:** `https://github.com/jkoppel/QuixBugs.git`
- **Local upstream mirror path:** `data/external/QuixBugs`
- **Dataset type:** program repair benchmark (buggy code + tests + reference-correct code), not a classical tabular dataset.

### Confirmed source

- Upstream remote is configured as:
  - `origin https://github.com/jkoppel/QuixBugs.git`
- Upstream README also documents the same clone source and benchmark context.

### Web-verified upstream benchmark facts

- Upstream positions QuixBugs as a **multi-lingual repair benchmark** from Quixey Challenge programs.
- Upstream benchmark description states:
  - **40 programs**
  - translated into **Python and Java**
  - each with a **one-line defect**
  - defects grouped into **14 defect classes**
- Upstream repository license is **MIT**.

## 2) What QuixBugs Contains (Local Copy)

Inside `data/external/QuixBugs`, the key folders are:

- `python_programs/`
  - Buggy Python implementations.
  - **50 `.py` files** used as algorithm/program modules.
  - Folder also has additional non-core artifacts (`*.orig`, `*.rej`, and test-driver modules in this repo copy).
- `correct_python_programs/`
  - Reference-correct Python implementations for comparison/oracle behavior.
  - **50 `.py` files**.
- `json_testcases/`
  - JSON-formatted testcase input/output records used by the custom runner for many tasks.
  - **31 `.json` files**.
- `python_testcases/`
  - pytest-style tests from upstream.
  - **40 `test_*.py` files** (42 total `.py` in that folder).
- `java_programs/`, `correct_java_programs/`, `java_testcases/`
  - Java benchmark side (present in repo, not primary path for your current QuixBugs SLM pipeline).

### Example 1: One QuixBugs source dataset file

From `data/external/QuixBugs/python_programs/bitcount.py`:

```python
def bitcount(n):
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
```

## 3) What `quixbugs_tasks*.jsonl` Contains

Each line is one executable task descriptor consumed by the QuixBugs orchestrator.

### Schema (all fields required in current files)

- `dataset` (string): always `"quixbugs"`
- `language` (string): always `"python"`
- `task_id` (string): canonical id like `quixbugs::py::bitcount`
- `algo` (string): algorithm/program name
- `buggy_path` (string): path to buggy file under `python_programs`
- `quixbugs_dir` (string): QuixBugs repo root path
- `test_cmd` (string): exact shell command used to validate buggy/fixed behavior
- `test_timeout_s` (int): timeout for that test command

### Size and distribution

- `data/quixbugs_tasks.jsonl`: **41** rows
- `data/quixbugs_tasks_v2.jsonl`: **41** rows
- `v1` timeout values: all `3`
- `v2` timeout values: `3` for 32 tasks, `10` for 9 tasks

### Example 2: One project task row

```json
{"dataset":"quixbugs","language":"python","task_id":"quixbugs::py::bitcount","algo":"bitcount","buggy_path":"data/external/QuixBugs/python_programs/bitcount.py","quixbugs_dir":"data/external/QuixBugs","test_cmd":"python3 src/quixbugs/run_quixbugs_python.py bitcount --quixbugs_dir data/external/QuixBugs","test_timeout_s":3}
```

## 4) Why This Task File Exists in This Thesis Project

`quixbugs_tasks*.jsonl` is a **task manifest contract** for the Step-6 repair orchestrator.

The orchestrator logic is:

1. Read one JSONL row by `task_index`.
2. Run baseline `test_cmd`.
3. Load buggy file from `buggy_path`.
4. Build SLM prompt from buggy content + failing output.
5. Generate/apply patch.
6. Re-run `test_cmd`.
7. Persist episode artifacts under `episodes/quixbugs_runs/...`.

This is exactly how the code in `src/step6_orchestrator_quixbugs_v5_attempts.py` (and earlier v1/v2/v3/v4 variants) is structured, so the manifest is necessary for scalable per-task automation.

## 5) How `quixbugs_tasks` Was Created (What Is Confirmed vs Inferred)

### Confirmed

- No dedicated generator script for `quixbugs_tasks*.jsonl` is present in the current repo tree.
- Manifest rows are structurally consistent with orchestrator requirements and QuixBugs file layout.
- `v2` differs from `v1` on 9 tasks by switching test strategy and timeout.

### Strong inference

The manifest was likely produced as follows:

1. Enumerate relevant Python program modules from `data/external/QuixBugs/python_programs`.
2. For each algorithm, create a default row that uses the custom runner:
   - `python3 src/quixbugs/run_quixbugs_python.py <algo> --quixbugs_dir data/external/QuixBugs`
   - timeout `3`.
3. Patch a known subset of graph/object-heavy tasks to dedicated test drivers in `python_programs/*_test.py` with timeout `10`.
4. Save as `quixbugs_tasks.jsonl` then revised `quixbugs_tasks_v2.jsonl`.

## 6) Inferred Pseudo-Generator Script (for Documentation)

> Note: This is reconstructed from repository evidence and file diffs. It is not an original historical script.

```python
# pseudo_build_quixbugs_tasks.py
from pathlib import Path
import json

QB_DIR = "data/external/QuixBugs"
PY_DIR = Path(QB_DIR) / "python_programs"
OUT_V1 = Path("data/quixbugs_tasks.jsonl")
OUT_V2 = Path("data/quixbugs_tasks_v2.jsonl")

# tasks that use dedicated test drivers in v2
GRAPHISH = {
    "breadth_first_search",
    "depth_first_search",
    "detect_cycle",
    "minimum_spanning_tree",
    "reverse_linked_list",
    "shortest_path_length",
    "shortest_path_lengths",
    "shortest_paths",
    "topological_ordering",
}

def base_row(algo: str) -> dict:
    return {
        "dataset": "quixbugs",
        "language": "python",
        "task_id": f"quixbugs::py::{algo}",
        "algo": algo,
        "buggy_path": f"{QB_DIR}/python_programs/{algo}.py",
        "quixbugs_dir": QB_DIR,
        "test_cmd": f"python3 src/quixbugs/run_quixbugs_python.py {algo} --quixbugs_dir {QB_DIR}",
        "test_timeout_s": 3,
    }

def v2_adjustments(row: dict) -> dict:
    algo = row["algo"]
    if algo in GRAPHISH:
        row["test_cmd"] = (
            'python3 -c "import sys; '
            f"sys.path.insert(0,'{QB_DIR}'); "
            f'import python_programs.{algo}_test as t; t.main()"'
        )
        row["test_timeout_s"] = 10
    return row

def collect_algos():
    # inferred behavior:
    # include .py modules but not *_test.py driver modules
    algos = []
    for p in sorted(PY_DIR.glob("*.py")):
        name = p.stem
        if name.endswith("_test"):
            continue
        algos.append(name)
    return algos

def write_jsonl(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

algos = collect_algos()
rows_v1 = [base_row(a) for a in algos]
rows_v2 = [v2_adjustments(base_row(a)) for a in algos]

write_jsonl(OUT_V1, rows_v1)
write_jsonl(OUT_V2, rows_v2)
```

## 7) v1 -> v2 Task Changes (Confirmed)

The following 9 algorithms were changed in `v2`:

- `breadth_first_search`
- `depth_first_search`
- `detect_cycle`
- `minimum_spanning_tree`
- `reverse_linked_list`
- `shortest_path_length`
- `shortest_path_lengths`
- `shortest_paths`
- `topological_ordering`

Change pattern:

- `test_cmd` switched from generic `run_quixbugs_python.py` to dedicated `python_programs/<algo>_test.py` driver.
- `test_timeout_s` increased from `3` to `10`.

## 8) Caveats to Capture in Proposal

- Upstream README says 40 benchmark programs; this project manifest has 41 rows.
- The extra row includes `node` (helper-like module) in manifest.
- There is no checked-in historical generator script, so “creation method” is partially inferred from code behavior and file diffs.
- This thesis pipeline uses a task-manifest abstraction (`quixbugs_tasks*.jsonl`) that is project-specific and not an upstream canonical artifact.

## 9) Practical Conclusion for Thesis Use

For your SLM repair loop, **`data/quixbugs_tasks_v2.jsonl` is the operational dataset interface**:

- It normalizes each QuixBugs problem into one executable task row.
- It encodes both code target (`buggy_path`) and validation protocol (`test_cmd`, `test_timeout_s`).
- It enables deterministic, index-based, repeatable repair episodes.

## 10) External References (for Thesis Documentation)

- QuixBugs upstream repository:
  - `https://github.com/jkoppel/QuixBugs`
- QuixBugs benchmark paper (linked by upstream):
  - `https://github.com/jkoppel/QuixBugs` (README links `quixbugs.pdf`)
