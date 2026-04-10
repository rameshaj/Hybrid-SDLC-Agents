# Dataset Raw vs Project Task Formats (Synced to Sample Runs)

Date captured: 2026-03-15

## Purpose
This version keeps the same documentation format as the earlier dataset-format note, but aligns all dataset examples to the exact sample runs documented in:
- `reports/sample_runs`

Sync map used in this file:
- HumanEval sample run `episodes/humaneval_runs/20260201_211622_HumanEval_10` -> `HumanEval/10`
- QuixBugs sample run `episodes/quixbugs_runs/attempts/20260309_221252_flatten` -> `quixbugs::py::flatten`
- Defects4J sample run report `reports/defects4j/batch_10/Chart-2-2b-defects4j-test.txt` -> `defects4j::Chart-2::2b->2f`
- BigCodeBench sample run `episodes/bigcodebench_runs_fixcheck_v2/20260310_085745_BigCodeBench_279` -> `BigCodeBench/279`

---

## 1) QuixBugs (Synced to `flatten`)

### Raw Download Structure
QuixBugs is repository-style data (folder/file benchmark), not a single JSONL task file.  
Raw root in this workspace:
- `data/external/QuixBugs`

Main raw folders used:
- `python_programs`
- `correct_python_programs`
- `python_testcases`
- `json_testcases`
- `java_programs`
- `correct_java_programs`
- `java_testcases`

The sample run used `flatten`, which maps to:
- buggy code: `data/external/QuixBugs/python_programs/flatten.py`
- raw testcase pairs: `data/external/QuixBugs/json_testcases/flatten.json`

### Raw Fields
QuixBugs raw data is file-based, so there is no single global row schema.  
For `json_testcases/*.json`, the structural unit is:
- `[input_args, expected_output]`

### 1 Example (Raw)
Sample raw buggy file (`flatten.py`) logic (abridged):
```python
def flatten(arr):
    for x in arr:
        if isinstance(x, list):
            for y in flatten(x):
                yield y
        else:
            yield x
```

Sample raw testcase pairs (`flatten.json`):
```json
[[[[1, [], [2, 3]], [[4]], 5]], [1, 2, 3, 4, 5]]
[[[[], [], [], [], []]], []]
```

### Project Task Fields
Project orchestration task format (JSONL row, from `data/quixbugs_tasks_v2.jsonl`):
- `dataset`
- `language`
- `task_id`
- `algo`
- `buggy_path`
- `quixbugs_dir`
- `test_cmd`
- `test_timeout_s`

Task file size:
- `data/quixbugs_tasks_v2.jsonl`: 41 tasks

### Example Task (Project)
This is the exact project task row aligned to the sample run (`flatten`):
```json
{
  "dataset": "quixbugs",
  "language": "python",
  "task_id": "quixbugs::py::flatten",
  "algo": "flatten",
  "buggy_path": "data/external/QuixBugs/python_programs/flatten.py",
  "quixbugs_dir": "data/external/QuixBugs",
  "test_cmd": "python3 src/quixbugs/run_quixbugs_python.py flatten --quixbugs_dir data/external/QuixBugs",
  "test_timeout_s": 3
}
```

Sync note:
- The QuixBugs sample run folder itself is algorithm-scoped (`..._flatten`) and does not carry a separate `task.json`; mapping is done via `algo=flatten` to `task_id=quixbugs::py::flatten`.

---

## 2) Defects4J (Synced to `Chart-2`)

### Raw Download Structure
Defects4J raw data is checkout/tooling oriented. In this project line, each bug has:
- buggy checkout (`2b`)
- fixed checkout (`2f`)
- failing test reports
- generated patch artifacts

Sample-linked artifacts in this workspace:
- buggy test report: `reports/defects4j/batch_10/Chart-2-2b-defects4j-test.txt`
- fixed test report: `reports/defects4j/batch_10/Chart-2-2f-defects4j-test.txt`
- java-only patch artifact: `episodes/artifacts/defects4j/batch_10/Chart-2/patch_java_only.diff`
- structured task file: `datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl`

The patch artifact references the raw checkout roots:
- `.../data_raw/defects4j_batch_10/Chart-2-2b`
- `.../data_raw/defects4j_batch_10/Chart-2-2f`

### Raw Fields
Defects4J raw bug metadata used by this project includes:
- `project`
- `bug_id`
- `buggy_version`
- `fixed_version`
- `failing_tests`
- source-level patch/diff between buggy and fixed

### 1 Example (Raw)
For sample-linked `Chart-2`:
- buggy report says:
  - `Failing tests: 2`
  - `org.jfree.data.general.junit.DatasetUtilitiesTests::testBug2849731_2`
  - `org.jfree.data.general.junit.DatasetUtilitiesTests::testBug2849731_3`
- fixed report says:
  - `Failing tests: 0`

Patch artifact shows edited file:
- `source/org/jfree/data/general/DatasetUtilities.java`
- fix updates min/max range handling around `getStartXValue/getEndXValue` and `getStartYValue/getEndYValue`.

### Project Task Fields
Project task format (JSONL row in `datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl`):
- top-level: `id`, `prompt`, `target`, `meta`
- `prompt`: `instruction`, `task_id`, `dataset`, `project`, `buggy_version`, `fixed_version`, `failing_tests`
- `target`: expected java unified diff patch
- `meta`: patch/report artifact pointers

Task file size:
- `datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl`: 10 tasks

### Example Task (Project)
This is the exact project task aligned to the sample run (`Chart-2`):
```json
{
  "id": "defects4j::Chart-2::2b->2f",
  "prompt": {
    "instruction": "Fix the bug so that failing tests pass. Output a unified diff patch for Java source files only.",
    "task_id": "Chart-2",
    "dataset": "Defects4J",
    "project": "Chart",
    "buggy_version": "2b",
    "fixed_version": "2f",
    "failing_tests": [
      "org.jfree.data.general.junit.DatasetUtilitiesTests::testBug2849731_2",
      "org.jfree.data.general.junit.DatasetUtilitiesTests::testBug2849731_3"
    ]
  },
  "target": "# Java-only patch ... DatasetUtilities.java ...",
  "meta": {
    "artifact_patch_java_only": "episodes/artifacts/defects4j/batch_10/Chart-2/patch_java_only.diff",
    "artifact_patch_full": "episodes/artifacts/defects4j/batch_10/Chart-2/patch.diff",
    "report_buggy": "/Users/ajayramesh/Documents/AIML/Masteers/ThesisImplementation/thesis-hybrid-sdlc-agent/reports/defects4j/batch_10/Chart-2-2b-defects4j-test.txt",
    "report_fixed": "/Users/ajayramesh/Documents/AIML/Masteers/ThesisImplementation/thesis-hybrid-sdlc-agent/reports/defects4j/batch_10/Chart-2-2f-defects4j-test.txt"
  }
}
```

---

## 3) HumanEval (Synced to `HumanEval/10`)

### Raw Download Structure
HumanEval in this workspace is stored as JSONL tasks:
- `data/external/humaneval/humaneval_train.jsonl`

Each line is one complete code-generation task with prompt, tests, and canonical solution.

Task file size:
- `data/external/humaneval/humaneval_train.jsonl`: 164 tasks

### Raw Fields
HumanEval row schema:
- `task_id`
- `prompt`
- `canonical_solution`
- `test`
- `entry_point`

### 1 Example (Raw)
Sample-linked raw task (`HumanEval/10`, entry point `make_palindrome`) includes:
- prompt defining helpers + target function (`is_palindrome`, `make_palindrome`)
- canonical solution for shortest-palindrome completion
- test block with:
  - `METADATA = {'author': 'jt', 'dataset': 'test'}`
  - `check(candidate)` assertions

Prompt excerpt:
```python
def is_palindrome(string: str) -> bool:
    """ Test if given string is a palindrome """
    return string == string[::-1]

def make_palindrome(string: str) -> str:
    """ Find the shortest palindrome that begins with a supplied string. """
```

### Project Task Fields
Project HumanEval runs consume the same task schema directly:
- `task_id`
- `prompt`
- `canonical_solution`
- `test`
- `entry_point`

In sample run evidence:
- `episodes/humaneval_runs/20260201_211622_HumanEval_10/task.json`

### Example Task (Project)
This is the exact sample-linked task identity:
```json
{
  "task_id": "HumanEval/10",
  "entry_point": "make_palindrome",
  "prompt": "... palindrome helper + make_palindrome docstring and examples ...",
  "canonical_solution": "... shortest palindrome completion logic ...",
  "test": "METADATA + check(candidate) assertions ..."
}
```

---

## 4) BigCodeBench (Stdlib Only, Synced to `BigCodeBench/279`)

### Raw Download Structure
For this project slice, stdlib tasks are in JSONL:
- `data/external/bcb/bigcodebench_subset_stdlib.jsonl`

Each row includes instruction prompt, code scaffold, tests, canonical solution, and metadata.

Task file size:
- `data/external/bcb/bigcodebench_subset_stdlib.jsonl`: 30 tasks

### Raw Fields
BigCodeBench stdlib row schema:
- `task_id`
- `instruct_prompt`
- `code_prompt`
- `complete_prompt`
- `entry_point`
- `test`
- `canonical_solution`
- `libs`
- `doc_struct`

### 1 Example (Raw)
Sample-linked raw task is `BigCodeBench/279`:
- objective: draw `x` random 5-card hands and return `(hands, Counter)`
- scaffold imports:
  - `import random`
  - `from collections import Counter`
- constant:
  - `CARDS = ['2', ..., 'A']`
- entry point:
  - `task_func(x=1)`

Test snippet characteristics:
- checks hand size, drawn batch size, card uniqueness, valid card domain, and card distribution coverage.

### Project Task Fields
Project BigCodeBench stdlib runs use the same schema directly.

Sample-linked run evidence:
- run dir: `episodes/bigcodebench_runs_fixcheck_v2/20260310_085745_BigCodeBench_279`
- `task.json` in run dir carries the selected task payload.

### Example Task (Project)
This is the exact sample-linked project task identity:
```json
{
  "task_id": "BigCodeBench/279",
  "entry_point": "task_func",
  "libs": "['collections', 'random']",
  "code_prompt": "import random\nfrom collections import Counter\n# Constants\nCARDS = [...]\ndef task_func(x=1):\n",
  "instruct_prompt": "Draw x random 5-card poker hands ... return hands with card Counter ...",
  "test": "unittest suite validating size, uniqueness, validity, randomness/distribution checks",
  "canonical_solution": "draw with random.sample(CARDS, 5), update Counter, return tuple"
}
```

---

## Final Sync Confirmation
This file is synchronized to `reports/sample_runs` by using the same task examples:
- HumanEval -> `HumanEval/10`
- QuixBugs -> `quixbugs::py::flatten`
- Defects4J -> `defects4j::Chart-2::2b->2f`
- BigCodeBench stdlib -> `BigCodeBench/279`

