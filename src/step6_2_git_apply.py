from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass
class ApplyResult:
    ok: bool
    error: str | None
    stdout: str
    stderr: str


def git_apply(repo_root: str, diff_text: str) -> ApplyResult:
    try:
        p = subprocess.run(
            ["git", "apply", "--whitespace=nowarn", "-"],
            input=diff_text.encode("utf-8"),
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return ApplyResult(
            ok=(p.returncode == 0),
            error=None if p.returncode == 0 else f"git apply failed (code={p.returncode})",
            stdout=p.stdout.decode("utf-8", errors="replace"),
            stderr=p.stderr.decode("utf-8", errors="replace"),
        )
    except Exception as e:
        return ApplyResult(False, f"Exception running git apply: {e}", "", "")
