from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import List


@dataclass
class TestResult:
    ok: bool
    returncode: int
    stdout: str
    stderr: str
    command: List[str]


def run_cmd(repo_root: str, cmd: List[str], timeout_s: int = 900) -> TestResult:
    p = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout_s,
    )
    return TestResult(
        ok=(p.returncode == 0),
        returncode=p.returncode,
        stdout=p.stdout.decode("utf-8", errors="replace"),
        stderr=p.stderr.decode("utf-8", errors="replace"),
        command=cmd,
    )
