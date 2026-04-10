# Dataset Raw vs Project Task Formats (Thesis Documentation Draft)

## Purpose
This note documents, for each dataset used in the project, two different views:
1. The **raw downloaded form** (how the dataset exists before orchestration/task conversion).
2. The **project task form** (how tasks are represented and consumed by the project code).

The datasets covered are:
- QuixBugs
- Defects4J
- HumanEval
- BigCodeBench (**stdlib subset only**)

---

## 1) QuixBugs

### Raw Download Structure
QuixBugs is repository-style data, not a single JSONL benchmark file. It contains buggy/correct programs and test assets for both Python and Java.

In the current workspace snapshot, the major raw folders are:
- `python_programs`
- `correct_python_programs`
- `python_testcases`
- `json_testcases`
- `java_programs`
- `correct_java_programs`
- `java_testcases`

The raw content includes:
- buggy implementations of algorithms,
- corrected implementations,
- python driver tests,
- json testcase pairs (input-output style),
- java programs and junit tests.

### Raw Fields
There is no single global row schema for raw QuixBugs because it is folder-and-file based.

The closest structured raw format is `json_testcases`, where each testcase record is:
- `[input_args, expected_output]`

### 1 Example (Raw)
Example buggy program (`bitcount`):

```python
def bitcount(n):
    count = 0
    while n:
        n ^= n - 1
        count += 1
    return count
```

Example raw testcase pairs:

```json
[[127], 7]
[[128], 1]
[[3005], 9]
```

### Project Task Fields
QuixBugs tasks used by the orchestrator are represented in JSONL rows with:
- `dataset`
- `language`
- `task_id`
- `algo`
- `buggy_path`
- `quixbugs_dir`
- `test_cmd`
- `test_timeout_s`

Current project task list size in v2 tasks file: **41 tasks**.

### Example Task (Project)
```json
{
  "dataset": "quixbugs",
  "language": "python",
  "task_id": "quixbugs::py::bitcount",
  "algo": "bitcount",
  "buggy_path": "data/external/QuixBugs/python_programs/bitcount.py",
  "quixbugs_dir": "data/external/QuixBugs",
  "test_cmd": "python3 src/quixbugs/run_quixbugs_python.py bitcount --quixbugs_dir data/external/QuixBugs",
  "test_timeout_s": 3
}
```

---

## 2) Defects4J

### Raw Download Structure
Defects4J is tool-driven benchmark infrastructure rather than a static single-file dataset. The raw process is:
- install/use Defects4J framework tooling,
- checkout buggy and fixed revisions for each bug,
- run `defects4j test`,
- collect failing tests and source changes.

In this workspace snapshot, previously generated artifacts/logs are present (batch patches/test logs), while the local Defects4J tool directory itself is currently not present.

Raw/derived content available in project snapshot includes:
- buggy/fixed test logs for Chart batch bugs,
- extracted full diffs and java-only patch diffs,
- generated task JSONL for batch execution.

### Raw Fields
Defects4J raw data is not naturally one row schema. Practically, bug metadata used in this project includes:
- `project`
- `bug_id`
- `buggy_version`
- `fixed_version`
- `failing_tests`
- source diff/patch between buggy and fixed versions

### 1 Example (Raw)
Example bug instance concept:
- Project: `Chart`
- Bug: `1`
- Buggy version: `1b`
- Fixed version: `1f`
- Failing test in buggy revision:
  - `org.jfree.chart.renderer.category.junit.AbstractCategoryItemRendererTests::test2947660`

### Project Task Fields
Defects4J project tasks (batch file) are represented as:
- top-level: `id`, `prompt`, `target`, `meta`
- `prompt` fields:
  - `instruction`, `task_id`, `dataset`, `project`, `buggy_version`, `fixed_version`, `failing_tests`
- `target`:
  - expected java unified diff patch text
- `meta`:
  - artifact and report references

Current batch task list size: **10 tasks** (`Chart-1` to `Chart-10`).

### Example Task (Project)
```json
{
  "id": "defects4j::Chart-1::1b->1f",
  "prompt": {
    "instruction": "Fix the bug so that failing tests pass. Output a unified diff patch for Java source files only.",
    "task_id": "Chart-1",
    "dataset": "Defects4J",
    "project": "Chart",
    "buggy_version": "1b",
    "fixed_version": "1f",
    "failing_tests": [
      "org.jfree.chart.renderer.category.junit.AbstractCategoryItemRendererTests::test2947660"
    ]
  },
  "target": "# Java-only patch ... unified diff ...",
  "meta": {
    "artifact_patch_java_only": "...",
    "artifact_patch_full": "...",
    "report_buggy": "...",
    "report_fixed": "..."
  }
}
```

---

## 3) HumanEval

### Raw Download Structure
In this project, HumanEval is stored directly as JSONL tasks. Each line is a complete coding task.

Raw content per task includes:
- function prompt/signature/docstring examples,
- canonical reference solution,
- test code (`check(candidate)`),
- entry point function name.

Current task count in the local HumanEval file: **164 tasks**.

### Raw Fields
HumanEval row schema:
- `task_id`
- `prompt`
- `canonical_solution`
- `test`
- `entry_point`

### 1 Example (Raw)
Example (`HumanEval/0`, entry point `has_close_elements`):

```python
from typing import List

def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
```

### Project Task Fields
For HumanEval, the project uses the same schema directly (no heavy reformat required):
- `task_id`
- `prompt`
- `canonical_solution`
- `test`
- `entry_point`

### Example Task (Project)
```json
{
  "task_id": "HumanEval/7",
  "entry_point": "filter_by_substring",
  "prompt": "from typing import List\n\ndef filter_by_substring(strings: List[str], substring: str) -> List[str]: ...",
  "canonical_solution": "return [x for x in strings if substring in x]",
  "test": "METADATA = {...}\n\ndef check(candidate): ..."
}
```

---

## 4) BigCodeBench (Stdlib Only)

### Raw Download Structure
In this project, BigCodeBench is available via JSONL task files. For this section, only the stdlib subset is considered.

The stdlib subset is a curated JSONL set where each row contains:
- task instruction,
- required code scaffold,
- tests,
- canonical solution,
- metadata such as libraries.

Current stdlib subset size: **30 tasks**.

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
Example (`BigCodeBench/4`) objective:
- Count occurrences of integers across dictionary values (lists) and return aggregate counts.

Example required scaffold:

```python
from collections import Counter
import itertools
def task_func(d):
```

### Project Task Fields
For BigCodeBench stdlib runs, project code uses the same row schema directly:
- `task_id`
- `instruct_prompt`
- `code_prompt`
- `complete_prompt`
- `entry_point`
- `test`
- `canonical_solution`
- `libs`
- `doc_struct`

### Example Task (Project)
```json
{
  "task_id": "BigCodeBench/22",
  "entry_point": "task_func",
  "instruct_prompt": "Combine two lists by alternating elements, sample size K, and return frequency Counter.",
  "code_prompt": "import collections\nfrom itertools import zip_longest\nfrom random import choices\ndef task_func(l1, l2, K=10):",
  "test": "import unittest\nclass TestCases(unittest.TestCase): ...",
  "canonical_solution": "...",
  "libs": ["collections", "random", "itertools"],
  "doc_struct": "..."
}
```

---

## Summary (Cross-Dataset)
- QuixBugs raw form is repository/folder based; project converts to task JSONL with test commands.
- Defects4J raw form is tool/checkouts + failing tests + diffs; project packages this into structured bug-fix task JSONL.
- HumanEval is already task JSONL in raw form and is used nearly directly.
- BigCodeBench stdlib is JSONL task format and is used directly for orchestration.

