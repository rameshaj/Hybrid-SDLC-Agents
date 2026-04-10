from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import List


@dataclass
class DiffSanitizeResult:
    ok: bool
    error: str | None
    diff: str | None
    touched_files: List[str]


_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)\s*$", re.MULTILINE)
_FILE_LINE_RE = re.compile(r"^(---|\+\+\+) (a|b)/(.+?)\s*$", re.MULTILINE)

MAX_DIFF_CHARS = 120_000
MAX_FILES_TOUCHED = 1
BLOCKED_PATH_PREFIXES = (".git/",)


def _extract_touched_files(diff_text: str) -> List[str]:
    touched: List[str] = []
    for m in _DIFF_HEADER_RE.finditer(diff_text):
        a_path, b_path = m.group(1), m.group(2)
        touched.append(a_path if a_path == b_path else b_path)

    if not touched:
        for m in _FILE_LINE_RE.finditer(diff_text):
            touched.append(m.group(3))

    seen = set()
    out: List[str] = []
    for p in touched:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def sanitize_unified_diff(diff_text: str, repo_root: str) -> DiffSanitizeResult:
    if not diff_text or not diff_text.strip():
        return DiffSanitizeResult(False, "Empty diff", None, [])

    if len(diff_text) > MAX_DIFF_CHARS:
        return DiffSanitizeResult(False, f"Diff too large ({len(diff_text)} chars)", None, [])

    diff_text = diff_text.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"

    touched = _extract_touched_files(diff_text)
    if not touched:
        return DiffSanitizeResult(False, "Could not detect touched files in diff", None, [])

    if len(touched) > MAX_FILES_TOUCHED:
        return DiffSanitizeResult(False, f"Too many files touched: {touched}", None, touched)

    root_abs = os.path.abspath(repo_root)

    for rel_path in touched:
        if rel_path.startswith(BLOCKED_PATH_PREFIXES):
            return DiffSanitizeResult(False, f"Blocked path: {rel_path}", None, touched)

        if ".." in rel_path.split("/"):
            return DiffSanitizeResult(False, f"Path traversal detected: {rel_path}", None, touched)

        abs_path = os.path.abspath(os.path.join(repo_root, rel_path))
        if not abs_path.startswith(root_abs + os.sep) and abs_path != root_abs:
            return DiffSanitizeResult(False, f"Path escapes repo root: {rel_path}", None, touched)

    return DiffSanitizeResult(True, None, diff_text, touched)
