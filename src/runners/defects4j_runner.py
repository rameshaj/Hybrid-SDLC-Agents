from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from src.core.schemas import TestResult


def _run(cmd: List[str], cwd: Optional[Path] = None, env: Optional[dict] = None, timeout: int = 3600) -> Tuple[int, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
    )
    return p.returncode, p.stdout


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="ignore")


def _parse_defects4j_test_output(txt: str) -> dict:
    summary = {"failures": None, "failures_parsed": []}
    m = re.search(r"Failing tests:\s*(\d+)", txt)
    if m:
        summary["failures"] = int(m.group(1))
    failures = re.findall(r"[A-Za-z0-9_$.]+::[A-Za-z0-9_$.]+", txt)
    summary["failures_parsed"] = sorted(set(failures))
    return summary


def checkout_project(workdir: Path, project: str, version: str) -> None:
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.parent.mkdir(parents=True, exist_ok=True)

    code, out = _run(["defects4j", "checkout", "-p", project, "-v", version, "-w", str(workdir)])
    if code != 0:
        raise RuntimeError(f"defects4j checkout failed ({code}). Output:\n{out}")


def _strip_to_unified_diff(patch_text: str) -> str:
    """
    Your gold patches may start with comments like '# Java-only patch'.
    'patch' can choke depending on settings. We strip everything before the first '--- '.
    """
    idx = patch_text.find("\n--- ")
    if idx == -1:
        # maybe patch starts exactly with '--- '
        if patch_text.startswith("--- "):
            return patch_text
        return patch_text
    return patch_text[idx + 1 :]  # keep the leading '--- ' line


def _normalize_lf_inplace(path: Path) -> None:
    """
    Convert CRLF/CR -> LF for robust patching.
    """
    if not path.exists() or not path.is_file():
        return
    data = path.read_bytes()
    # Replace CRLF then remaining CR
    data2 = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if data2 != data:
        path.write_bytes(data2)


def _extract_target_files_from_patch(patch_text: str) -> List[str]:
    """
    Extract file paths from lines like:
      --- source/...
      +++ source/...
    We return unique paths (without a/ b/ prefixes if present).
    """
    files = []
    for line in patch_text.splitlines():
        if line.startswith("--- ") or line.startswith("+++ "):
            p = line[4:].strip().split("\t")[0].strip()
            # ignore /dev/null
            if p == "/dev/null":
                continue
            # strip common prefixes
            p = p.lstrip("./")
            if p.startswith("a/") or p.startswith("b/"):
                p = p[2:]
            files.append(p)
    return sorted(set(files))


def apply_patch(workdir: Path, patch_text: str, patch_log: Path) -> None:
    """
    Apply unified diff from repo root with line-ending normalization and tolerant patch flags.
    """
    workdir.mkdir(parents=True, exist_ok=True)

    cleaned = _strip_to_unified_diff(patch_text)

    tmp_patch = workdir / "__candidate.patch"
    _write_text(tmp_patch, cleaned)

    # normalize patch file line endings
    _normalize_lf_inplace(tmp_patch)

    # normalize target files line endings (important for the error you saw)
    for rel in _extract_target_files_from_patch(cleaned):
        target = workdir / rel
        _normalize_lf_inplace(target)

    if not tmp_patch.exists():
        raise RuntimeError(f"Patch file was not created: {tmp_patch}")

    # More tolerant patching:
    # --binary: don't treat CRLF specially
    # -l: ignore whitespace differences
    # --fuzz=3: allow small context drift
    code, out = _run(["patch", "-p0", "--binary", "-l", "--fuzz=3", "-i", tmp_patch.name], cwd=workdir)
    _write_text(patch_log, out)

    if code != 0:
        # If there are .rej files, keep that as additional evidence
        raise RuntimeError(f"patch apply failed ({code}). See log: {patch_log}")


def run_tests(workdir: Path, test_log: Path, tests: Optional[List[str]] = None) -> TestResult:
    if not tests:
        code, out = _run(["defects4j", "test"], cwd=workdir, timeout=3600)
        _write_text(test_log, out)
        summary = _parse_defects4j_test_output(out)
        return TestResult(ok=(code == 0), raw_log_path=str(test_log), summary=summary)

    all_out = []
    any_fail = False
    parsed_failures = []

    for t in tests:
        code, out = _run(["defects4j", "test", "-t", t], cwd=workdir, timeout=3600)
        all_out.append(f"=== TEST {t} (rc={code}) ===\n{out}\n")
        if code != 0:
            any_fail = True
        parsed_failures.extend(re.findall(r"[A-Za-z0-9_$.]+::[A-Za-z0-9_$.]+", out))

    merged_out = "\n".join(all_out)
    _write_text(test_log, merged_out)

    summary = {
        "mode": "per_test",
        "tests_requested": tests,
        "failures_parsed": sorted(set(parsed_failures)),
        "failures": None if not any_fail else len(sorted(set(parsed_failures))),
    }
    return TestResult(ok=(not any_fail), raw_log_path=str(test_log), summary=summary)
