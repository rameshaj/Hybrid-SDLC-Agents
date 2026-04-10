from __future__ import annotations
import re
import subprocess
from pathlib import Path
from typing import Tuple

HUNK_RE = re.compile(r"^@@\\s-\\d+(?:,\\d+)?\\s\\+\\d+(?:,\\d+)?\\s@@", re.M)

def is_unified_diff(text: str) -> Tuple[bool, str]:
    if not text or not text.strip():
        return False, "empty"
    if "--- " not in text or "+++ " not in text:
        return False, "missing_file_headers"
    if not HUNK_RE.search(text):
        return False, "missing_hunk_header"
    return True, "ok"

def apply_patch_unified(workdir: Path, diff_text: str) -> Tuple[bool, str]:
    try:
        p = subprocess.run(
            ["git", "apply", "--whitespace=nowarn", "-"],
            input=diff_text,
            text=True,
            cwd=str(workdir),
            capture_output=True,
        )
        if p.returncode != 0:
            return False, (p.stderr or p.stdout or "git apply failed").strip()
        return True, "applied"
    except Exception as e:
        return False, f"exception:{e}"
