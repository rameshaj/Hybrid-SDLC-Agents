from __future__ import annotations
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class TestResult:
    ok: bool
    stdout: str
    stderr: str
    failing_tests: List[str]
    error_signature: str

def _run(cmd, cwd: Path, timeout_s: int = 1800, stream: bool = False):
    """
    If stream=True: show live output in terminal (no capture).
    If stream=False: capture output (old behavior).
    """
    if stream:
        return subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            timeout=timeout_s,
            check=False,
        )
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout_s,
        check=False,
    )

def defects4j_checkout(workdir: Path, project: str, version: str, stream: bool = True) -> None:
    """
    Checkout project into workdir with live logs (macOS friendly).
    """
    if workdir.exists():
        shutil.rmtree(workdir, ignore_errors=True)

    workdir.parent.mkdir(parents=True, exist_ok=True)

    cmd = ["defects4j", "checkout", "-p", project, "-v", version, "-w", str(workdir)]
    print("▶ defects4j checkout:", " ".join(cmd))
    print("▶ cwd:", str(workdir.parent))

    p = _run(cmd, cwd=workdir.parent, timeout_s=1800, stream=stream)

    if p.returncode != 0:
        raise RuntimeError(f"defects4j checkout failed (rc={p.returncode}).")

    if not workdir.exists():
        raise RuntimeError(f"defects4j checkout did not create workdir: {workdir}")

    children = list(workdir.iterdir())
    if not children:
        raise RuntimeError(f"defects4j checkout produced empty directory: {workdir}")

def defects4j_export_trigger(workdir: Path) -> str:
    p = _run(["defects4j", "export", "-p", "tests.trigger"], cwd=workdir, timeout_s=600, stream=False)
    return (getattr(p, "stdout", "") or "").strip()

def defects4j_test_failing_only(workdir: Path) -> TestResult:
    trigger = defects4j_export_trigger(workdir)
    cmd = ["defects4j", "test"]

    if trigger and len(trigger.splitlines()) == 1:
        cmd = ["defects4j", "test", "-t", trigger.strip()]

    print("▶ defects4j test:", " ".join(cmd))
    p = _run(cmd, cwd=workdir, timeout_s=1800, stream=True)

    # When stream=True, stdout/stderr aren't captured. Keep them empty here.
    ok = (p.returncode == 0)
    sig = "tests_pass" if ok else "tests_failed"

    return TestResult(
        ok=ok,
        stdout="",
        stderr="",
        failing_tests=[],
        error_signature=sig,
    )
