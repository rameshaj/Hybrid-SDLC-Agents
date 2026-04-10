from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from src.core.schemas import PatchCandidate, TaskSpec, TestResult
from src.runners.defects4j_runner import apply_patch, checkout_project, run_tests


def run_defects4j_task(
    episode_id: str,
    task: TaskSpec,
    patch: PatchCandidate,
    failing_tests: Optional[List[str]] = None,
    runs_root: Path = Path("episodes/runs"),
) -> TestResult:
    """
    End-to-end tester:
      - checkout buggy version
      - apply patch
      - run tests
      - store logs + metadata
    """
    assert task.prompt.get("project") == "Chart", "This tester currently expects Defects4J Chart tasks."

    project = str(task.prompt.get("project"))
    buggy_version = str(task.prompt.get("buggy_version"))

    run_dir = runs_root / episode_id
    workdir = run_dir / "workdir"
    patch_log = run_dir / "patch_apply.log"
    test_log = run_dir / "defects4j_test.log"

    # 1) checkout
    checkout_project(workdir=workdir, project=project, version=buggy_version)

    # 2) apply patch
    apply_patch(workdir=workdir, patch_text=patch.patch, patch_log=patch_log)

    # 3) run tests
    tr = run_tests(workdir=workdir, test_log=test_log, tests=failing_tests)

    # 4) save minimal metadata
    meta = {
        "episode_id": episode_id,
        "task_uid": task.id,
        "project": project,
        "buggy_version": buggy_version,
        "failing_tests_requested": failing_tests or [],
        "test_ok": tr.ok,
        "summary": tr.summary,
        "patch_model": patch.model,
    }
    (run_dir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return tr
