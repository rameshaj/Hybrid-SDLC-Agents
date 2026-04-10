# Defects4J Data Card (Project-Specific)

## 1) Dataset Identity

- **Dataset name (project use):** `Defects4J` (Java program-repair benchmark)
- **Primary prepared task file (Step 5 format):**
  - `datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl`
- **Alternate lightweight task file (v3 format):**
  - `data/defects4j_tasks.jsonl`
- **Dataset type in this thesis pipeline:** bug-fix evaluation tasks (buggy/fixed versions, failing tests, and target patch), not a tabular classification dataset.

### Web-verified upstream benchmark facts

- Current upstream release shown in Defects4J README: **v3.0.1**.
- Upstream summary reports:
  - **854 active bugs** across 17 projects
  - **10 deprecated bugs** in two discontinued projects
  - active Chart bugs listed as **26**
- Upstream “relevant bug properties” emphasize:
  - reproducibility
  - triggering by at least one test
  - minimized patches
  - linked issue/commit traceability
- Upstream notes reproducibility constraints:
  - Java 11 runtime requirement
  - timezone should be `America/Los_Angeles`

## 2) Local Files and Paths (What Exists Now)

### A) Prepared task manifests

- `datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl`
  - **10 rows** (Chart-1 to Chart-10)
  - One full task object per bug id.
- `data/defects4j_tasks.jsonl`
  - **1 row**
  - Minimal task pointer: `{"project":"Chart","bug_id":"1"}`.

### B) Patch artifacts and test reports used to build Step 5 JSONL

- Patch artifacts:
  - `episodes/artifacts/defects4j/batch_10/Chart-1/patch.diff`
  - `episodes/artifacts/defects4j/batch_10/Chart-1/patch_java_only.diff`
  - ... similarly for `Chart-2` to `Chart-10`.
- Test reports:
  - `reports/defects4j/batch_10/Chart-1-1b-defects4j-test.txt`
  - `reports/defects4j/batch_10/Chart-1-1f-defects4j-test.txt`
  - ... similarly for all 10 buggy (`b`) and 10 fixed (`f`) versions.

### C) Episode records and orchestrator logs

- Batch preparation episode store:
  - `episodes/episodes.parquet`
  - Confirmed `BATCH10_EVAL_ONLY` rows: **20** (10 buggy + 10 fixed).
- Orchestrator logs:
  - `episodes/logs/step6_1_runs.jsonl` (**2 rows**)
  - `episodes/logs/step6_2_runs.jsonl` (**6 rows**)
  - `episodes/logs/step6_runs.jsonl` (**20 rows**, mixed historical formats).

### Example 1: One Defects4J source data file

From `reports/defects4j/batch_10/Chart-1-1b-defects4j-test.txt`:

```text
Running ant (compile.tests)................................................ OK
Running ant (run.dev.tests)................................................ OK
Failing tests: 1
  - org.jfree.chart.renderer.category.junit.AbstractCategoryItemRendererTests::test2947660
```

## 3) How Defects4J Batch-10 Data Was Prepared

This repo uses a 2-step preparation flow:

1. **Step 4 collection script**: `src/step4_defects4j_batch10.py`
   - Iterates `Chart-1` to `Chart-10` by default.
   - Checks out both buggy and fixed versions via `defects4j checkout`.
   - Runs `defects4j test` on both.
   - Writes:
     - raw test logs to `reports/defects4j/batch_10/`
     - patch artifacts to `episodes/artifacts/defects4j/batch_10/<task>/`
     - episode rows to `episodes/episodes.parquet`.
   - Uses phase tag: `BATCH10_EVAL_ONLY`.

2. **Step 5 JSONL build script**: `src/step5_build_jsonl_defects4j_batch10.py`
   - Reads `episodes/episodes.parquet`.
   - Filters only `TASKS = Chart-1..Chart-10`.
   - Filters only `phase == "BATCH10_EVAL_ONLY"`.
   - For each task:
     - pairs buggy (`*b`) and fixed (`*f`) rows
     - parses failing tests from buggy report
     - reads Java-only patch (`patch_java_only.diff`)
     - normalizes absolute patch paths to placeholders (`<BUGGY_ROOT>`, `<FIXED_ROOT>`)
   - Writes final dataset:
     - `datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl`.

## 4) Step 5 Dataset Schema (Detailed)

Each JSONL row contains:

- `id` (string)
  - Example: `defects4j::Chart-1::1b->1f`
- `prompt` (object)
  - `instruction` (string)
  - `task_id` (string): e.g., `Chart-1`
  - `dataset` (string): `Defects4J`
  - `project` (string): `Chart`
  - `buggy_version` (string): e.g., `1b`
  - `fixed_version` (string): e.g., `1f`
  - `failing_tests` (array of strings): parsed from buggy test report
- `target` (string)
  - Normalized unified Java diff (gold/reference patch)
- `meta` (object)
  - `artifact_patch_java_only`
  - `artifact_patch_full`
  - `report_buggy`
  - `report_fixed`

### Distribution in current file

- Total rows: **10**
- Projects: **Chart only**
- IDs: from `defects4j::Chart-1::1b->1f` to `defects4j::Chart-10::10b->10f`
- Failing test count per task:
  - 7 tasks with 1 failing test
  - 2 tasks with 2 failing tests
  - 1 task with 22 failing tests

### Example 2: One project task row (Step 5 JSONL)

From `datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl`:

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
  "target": "# Java-only patch ...",
  "meta": {
    "artifact_patch_java_only": "episodes/artifacts/defects4j/batch_10/Chart-1/patch_java_only.diff",
    "artifact_patch_full": "episodes/artifacts/defects4j/batch_10/Chart-1/patch.diff",
    "report_buggy": ".../reports/defects4j/batch_10/Chart-1-1b-defects4j-test.txt",
    "report_fixed": ".../reports/defects4j/batch_10/Chart-1-1f-defects4j-test.txt"
  }
}
```

## 5) Orchestrator Task Formats in This Repo

There are two Defects4J task input formats used by different orchestrator scripts:

### Format A: Step 5 rich JSONL (full prompt + target)

- File:
  - `datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl`
- Used by:
  - `src/step6_orchestrator_run.py` (default `--tasks_jsonl` points here)
  - `src/step6_orchestrator_run_v2.py` (default `--tasks_jsonl` points here)
  - `src/steps/step6_1_orchestrator_spine.py` (`--tasks_jsonl` required)
  - `src/steps/step6_2_orchestrator_run.py` (`--tasks_jsonl` required)

### Format B: Lightweight project/bug JSONL

- File:
  - `data/defects4j_tasks.jsonl`
- Row shape:
  - `{"project":"Chart","bug_id":"1"}`
- Used by:
  - `src/step6_orchestrator_run_v3.py` (default `--tasks_path` points here)
  - v3 builds task id with `defects4j::{project}-{bug_id}` if full task id is absent.

## 6) Which Orchestrator Task Format Was Actually Used (Confirmed From Logs)

### Confirmed usage in step6_1 and step6_2 logs

- `episodes/logs/step6_1_runs.jsonl`:
  - metadata contains `tasks_jsonl = datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl`.
- `episodes/logs/step6_2_runs.jsonl`:
  - metadata contains the same `tasks_jsonl`.

Therefore, for the recorded Step 6.1/6.2 runs, the **actually used** format is:

- `datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl` (Format A).

### Mixed historical entries in `step6_runs.jsonl`

- Lines with `task_uid = defects4j::Chart-1::1b->1f` correspond to Step-5-style tasks (older v1/v2 flow).
- Later flat rows with `task_id = defects4j::Chart-1` (and no `task_uid`) match v3 lightweight style (Format B).

So repository history shows both formats, but your primary logged 6.1/6.2 path is clearly Format A.

## 7) Defects4J Tooling Source Status (Important Documentation Note)

- `src/step4_defects4j_batch10.py` expects Defects4J at:
  - `tools/defects4j` (unless `DEFECTS4J_HOME` is set).
- In the current workspace snapshot:
  - `tools/defects4j` is **not present**.
  - Only `tools/summarize_quixbugs_attempt_run.py` exists.

Implication:

- We can fully document data products and preparation scripts from repo evidence.
- But the exact local Defects4J clone provenance (remote URL/commit) cannot be re-read from `tools/defects4j` in this snapshot because that folder is absent.
- For strict rerun reproducibility, a fresh local checkout of upstream Defects4J should be documented together with Java/timezone settings.

## 8) Practical Use in Thesis Pipeline

For reproducible Defects4J experiments in this project, treat:

- `datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl`

as the canonical dataset interface for Step 6 orchestration (especially 6.1/6.2 logs), because it bundles:

- task identity
- failing-test context
- normalized target patch
- traceable metadata links to artifacts/reports.

## 9) Reproducible Command Templates

### Build/refresh batch-10 raw artifacts and episode records (Step 4)

```bash
python src/step4_defects4j_batch10.py \
  --project Chart \
  --start 1 \
  --count 10 \
  --work_root data_raw/defects4j_batch_10 \
  --artifact_root episodes/artifacts/defects4j/batch_10 \
  --report_root reports/defects4j/batch_10 \
  --episodes_dir episodes \
  --episodes_file episodes.parquet
```

### Build Step-5 JSONL task file from Step-4 outputs

```bash
python src/step5_build_jsonl_defects4j_batch10.py
```

### Run Step 6 with Step-5 rich task format

```bash
python src/step6_orchestrator_run_v2.py \
  --tasks_jsonl datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl \
  --task_index 0
```

### Run Step 6 v3 with lightweight task format

```bash
python src/step6_orchestrator_run_v3.py \
  --tasks_path data/defects4j_tasks.jsonl \
  --task_index 0
```

## 10) External References (for Thesis Documentation)

- Defects4J upstream repository:
  - `https://github.com/rjust/defects4j`
- Defects4J documentation site:
  - `https://defects4j.org/`
