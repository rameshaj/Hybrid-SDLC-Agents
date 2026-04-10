#!/usr/bin/env python3
"""
QuixBugs SLM Patch Orchestrator – Step 6.3 (v5 + fallback)

Guarantees:
- No git apply --check gating
- Robust patch application
- Clear terminal progress logs
- Works across all QuixBugs Python tasks
- Captures actual applied diff

v4 adds:
- Optional cloud LLM fallback after SLM attempts fail.
- Fallback uses OPENAI_API_KEY from environment.

v5 adds:
- Uses llama-completion when available to avoid chat-mode echo.
- Drops unsupported -no-cnv flag for llama-cli.
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import time
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from llm_fallback_openai import openai_chat_completion

# -------------------- logging --------------------

def ts():
    return datetime.now().strftime("%H:%M:%S")

def log(msg):
    print(f"[{ts()}] {msg}", flush=True)

def stage(name):
    print(f"\n[{ts()}] ===== {name} =====", flush=True)

# -------------------- helpers --------------------

def read_jsonl_line(path, idx):
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i == idx:
                return json.loads(line)
    raise IndexError("task_index out of range")

def save_text(p: Path, t: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t or "", encoding="utf-8")

def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def run_cmd(cmd, timeout, cwd=None):
    log(f"RUN: {cmd}")
    start = time.time()
    env = os.environ.copy()
    env["PYTHONFAULTHANDLER"] = "1"
    p = subprocess.Popen(
        shlex.split(cmd),
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out or "", err or "", time.time() - start
    except subprocess.TimeoutExpired:
        try:
            p.send_signal(signal.SIGUSR1)
            time.sleep(0.5)
            p.kill()
        except Exception:
            pass
        return 124, "", "[TIMEOUT]\n", time.time() - start

# -------------------- QuixBugs helpers --------------------

def qb_relpath(task):
    marker = "data/external/QuixBugs/"
    return task["buggy_path"].split(marker, 1)[-1]

def qb_rollback(task):
    return f"git -C {task['quixbugs_dir']} checkout -- {qb_relpath(task)}"

# -------------------- diff handling --------------------

def _sanitize_diff(raw: str) -> Optional[str]:
    idx = raw.find("diff --git")
    if idx == -1:
        return None
    raw = raw[idx:]

    lines = raw.splitlines()
    kept: List[str] = []
    in_hunk = False
    saw_hunk = False

    def _is_header(line: str) -> bool:
        return line.startswith((
            "diff --git",
            "index ",
            "--- ",
            "+++ ",
            "new file",
            "deleted file",
            "similarity index",
            "rename from",
            "rename to",
            "old mode",
            "new mode",
            "Binary files ",
        ))

    for line in lines:
        if not kept:
            if line.startswith("diff --git"):
                kept.append(line)
            continue

        if line.startswith("@@ "):
            in_hunk = True
            saw_hunk = True
            kept.append(line)
            continue

        if in_hunk:
            if line == "":
                kept.append(line)
                continue
            if line.startswith((" ", "+", "-", "\\")):
                kept.append(line)
                continue
            if line.startswith("diff --git"):
                in_hunk = False
                kept.append(line)
                continue
            # stop at first non-diff line after hunks start
            break

        # not in hunk yet, allow headers
        if _is_header(line):
            kept.append(line)
            continue
        # skip stray blank lines before hunks
        if not line.strip():
            continue
        break

    if not kept or not saw_hunk:
        return None

    # normalize blank lines inside hunks
    normalized: List[str] = []
    in_hunk = False
    for line in kept:
        if line.startswith("@@ "):
            in_hunk = True
            normalized.append(line)
            continue
        if in_hunk and line == "":
            normalized.append(" ")
            continue
        if line.startswith("diff --git"):
            in_hunk = False
        normalized.append(line)

    # fix hunk header counts
    fixed: List[str] = []
    i = 0
    while i < len(normalized):
        line = normalized[i]
        if line.startswith("@@ "):
            m = re.match(r"@@ -(\d+)(?:,(\d+))? \\+(\d+)(?:,(\d+))? @@", line)
            if not m:
                fixed.append(line)
                i += 1
                continue
            old_start = m.group(1)
            new_start = m.group(3)
            old_count = 0
            new_count = 0
            j = i + 1
            while j < len(normalized):
                l = normalized[j]
                if l.startswith("@@ ") or l.startswith("diff --git"):
                    break
                if l.startswith("\\"):
                    j += 1
                    continue
                if l.startswith("+"):
                    new_count += 1
                elif l.startswith("-"):
                    old_count += 1
                else:
                    old_count += 1
                    new_count += 1
                j += 1
            fixed.append(f"@@ -{old_start},{old_count} +{new_start},{new_count} @@")
            fixed.extend(normalized[i + 1:j])
            i = j
            continue
        fixed.append(line)
        i += 1

    return "\n".join(fixed).strip() + "\n"


def extract_diff(text: str) -> Optional[str]:
    return _sanitize_diff(text)

# -------------------- SLM diff extraction --------------------

def extract_slm_diff(text: str) -> Optional[str]:
    segments: List[str] = []
    start = 0
    while True:
        s = text.find("<PATCH>", start)
        if s == -1:
            break
        e = text.find("</PATCH>", s + 7)
        if e == -1:
            break
        segments.append(text[s + 7:e])
        start = e + 8

    segments.append(text)

    best: Optional[str] = None
    for seg in segments:
        idx = 0
        while True:
            idx = seg.find("diff --git", idx)
            if idx == -1:
                break
            cand = seg[idx:]
            diff = _sanitize_diff(cand)
            if diff:
                best = diff
            idx += len("diff --git")

    return best


def sanitize_slm_diff(diff: str) -> Tuple[Optional[str], bool, Optional[str]]:
    fixed, changed1 = _fix_hunk_line_prefixes(diff)
    fixed, changed2 = _trim_hunk_trailing_context(fixed)
    fixed, changed3 = _drop_noop_hunks(fixed)
    fixed, changed4 = _recount_hunks(fixed)
    err = _validate_diff_format(fixed)
    if err:
        return None, (changed1 or changed2 or changed3 or changed4), err
    return fixed, (changed1 or changed2 or changed3 or changed4), None


def _extract_error_line(failing: str, rel: str) -> Optional[int]:
    pattern = re.compile(rf"File \".*?{re.escape(rel)}\", line (\\d+)")
    matches = pattern.findall(failing)
    if matches:
        try:
            return int(matches[-1])
        except ValueError:
            return None
    return None


def _format_context(lines: List[str], start: int, end: int) -> str:
    return "\n".join(f"{i+1}: {lines[i]}" for i in range(start, end))

def _tail_lines(text: str, n: int) -> str:
    lines = text.splitlines()
    if len(lines) <= n:
        return "\n".join(lines)
    return "\n".join(lines[-n:])

def _one_line(text: str, limit: int = 300) -> str:
    compact = " ".join(text.split())
    if len(compact) > limit:
        return compact[:limit - 3] + "..."
    return compact


def select_buggy_context(buggy: str, failing: str, rel: str, window: int = 40, max_lines: int = 200) -> Tuple[str, str]:
    lines = buggy.splitlines()
    if len(lines) <= max_lines:
        return "Buggy file content (exact):", buggy

    line_no = _extract_error_line(failing, rel)
    if line_no:
        start = max(0, line_no - 1 - window)
        end = min(len(lines), line_no - 1 + window)
        ctx = _format_context(lines, start, end)
        return f"Buggy context (lines {start+1}-{end}):", ctx

    # fallback: head + tail
    head = _format_context(lines, 0, min(len(lines), max_lines))
    return "Buggy context (head):", head


def _parse_hunks(diff: str) -> List[List[str]]:
    hunks: List[List[str]] = []
    cur: Optional[List[str]] = None
    for line in diff.splitlines():
        if line.startswith("@@ "):
            cur = []
            hunks.append(cur)
            continue
        if cur is None:
            continue
        if line.startswith((" ", "+", "-", "\\")):
            cur.append(line)
    return hunks


def _find_subsequence(hay: List[str], needle: List[str], strip: bool) -> Optional[int]:
    if not needle:
        return None
    n = len(needle)
    for i in range(0, len(hay) - n + 1):
        ok = True
        for j in range(n):
            a = hay[i + j]
            b = needle[j]
            if strip:
                if a.lstrip() != b.lstrip():
                    ok = False
                    break
            else:
                if a != b:
                    ok = False
                    break
        if ok:
            return i
    return None


def _apply_hunk(lines: List[str], hunk: List[str]) -> Optional[List[str]]:
    old_seq = [l[1:] for l in hunk if l.startswith((" ", "-"))]
    # try exact match, then lstrip match
    idx = _find_subsequence(lines, old_seq, strip=False)
    if idx is None:
        idx = _find_subsequence(lines, old_seq, strip=True)
    if idx is None:
        return None

    new_lines: List[str] = []
    new_lines.extend(lines[:idx])
    pos = idx
    for l in hunk:
        if l.startswith(" "):
            new_lines.append(lines[pos])
            pos += 1
        elif l.startswith("-"):
            pos += 1
        elif l.startswith("+"):
            new_lines.append(l[1:])
        elif l.startswith("\\"):
            continue
    new_lines.extend(lines[pos:])
    return new_lines


def repair_diff_to_file(diff: str, file_path: Path, rel: str) -> Optional[str]:
    if not file_path.exists():
        return None
    # Keep line model consistent with parsed hunks (no trailing '\n' chars),
    # otherwise context matching can fail even when text is identical.
    orig = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    hunks = _parse_hunks(diff)
    if not hunks:
        return None

    cur = orig[:]
    for h in hunks:
        updated = _apply_hunk(cur, h)
        if updated is None:
            return None
        cur = updated

    if cur == orig:
        return None

    import difflib
    new_diff = list(difflib.unified_diff(
        orig, cur,
        fromfile=f"a/{rel}",
        tofile=f"b/{rel}",
        lineterm=""
    ))
    if not new_diff:
        return None
    return "\n".join(new_diff) + "\n"

# -------------------- patch apply helpers --------------------

def _validate_diff_context(diff: str, file_path: Path) -> Optional[str]:
    if not file_path.exists():
        return "FILE_NOT_FOUND"
    # Parsed hunk lines are newline-stripped; match against stripped file lines too.
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    hunks = _parse_hunks(diff)
    if not hunks:
        return "NO_HUNKS"
    for i, h in enumerate(hunks, 1):
        old_seq = [l[1:] for l in h if l.startswith((" ", "-"))]
        if not old_seq:
            continue
        if _find_subsequence(lines, old_seq, strip=False) is None and _find_subsequence(lines, old_seq, strip=True) is None:
            sample = old_seq[0].strip()
            return f"HUNK_CONTEXT_NOT_FOUND hunk={i} sample={sample}"
    return None

def _summarize_apply_errors(errors: List[Tuple[str, str]]) -> str:
    parts: List[str] = []
    for cmd, text in errors:
        tail = _tail_lines(text, 6).strip()
        if tail:
            parts.append(f"{cmd}: {tail}")
    summary = "\n".join(parts).strip()
    if len(summary) > 800:
        summary = summary[-800:]
    return summary

# -------------------- fallback diff validation --------------------

def _fix_hunk_line_prefixes(diff: str) -> Tuple[str, bool]:
    lines = diff.splitlines()
    fixed: List[str] = []
    in_hunk = False
    changed = False

    for line in lines:
        if line.startswith("diff --git"):
            in_hunk = False
            fixed.append(line)
            continue
        if line.startswith("@@ "):
            in_hunk = True
            fixed.append(line)
            continue
        if in_hunk:
            if line == "":
                fixed.append(" ")
                changed = True
                continue
            if line.startswith((" ", "+", "-", "\\")):
                fixed.append(line)
                continue
            # Treat malformed lines as context lines
            fixed.append(" " + line)
            changed = True
            continue
        fixed.append(line)

    return "\n".join(fixed).strip() + "\n", changed


def _validate_diff_format(diff: str) -> Optional[str]:
    lines = diff.splitlines()
    in_hunk = False

    for i, line in enumerate(lines, 1):
        if line.startswith("diff --git"):
            in_hunk = False
            continue
        if line.startswith("@@ "):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line == "":
            return f"empty hunk line at {i}"
        if not line.startswith((" ", "+", "-", "\\")):
            return f"invalid hunk line at {i}"

    return None


def _trim_hunk_trailing_context(diff: str) -> Tuple[str, bool]:
    lines = diff.splitlines()
    fixed: List[str] = []
    changed = False
    i = 0

    while i < len(lines):
        line = lines[i]
        if not line.startswith("@@ "):
            fixed.append(line)
            i += 1
            continue

        # Collect hunk body
        hunk_header = line
        hunk_body: List[str] = []
        i += 1
        while i < len(lines):
            l = lines[i]
            if l.startswith("@@ ") or l.startswith("diff --git"):
                break
            hunk_body.append(l)
            i += 1

        # Find last change line (+ or -)
        last_change = None
        for idx in range(len(hunk_body) - 1, -1, -1):
            if hunk_body[idx].startswith(("+", "-")):
                last_change = idx
                break

        if last_change is not None:
            # Drop trailing context lines after last change
            trimmed = hunk_body[: last_change + 1]
            # Drop trailing blank-line additions (e.g., "+")
            while trimmed and trimmed[-1].startswith("+") and trimmed[-1][1:].strip() == "":
                trimmed.pop()
                changed = True
            if len(trimmed) != len(hunk_body):
                changed = True
            hunk_body = trimmed

        fixed.append(hunk_header)
        fixed.extend(hunk_body)

    return "\n".join(fixed).strip() + "\n", changed


def _drop_noop_hunks(diff: str) -> Tuple[str, bool]:
    lines = diff.splitlines()
    fixed: List[str] = []
    changed = False
    i = 0

    while i < len(lines):
        line = lines[i]
        if not line.startswith("@@ "):
            fixed.append(line)
            i += 1
            continue

        hunk_header = line
        hunk_body: List[str] = []
        i += 1
        while i < len(lines):
            l = lines[i]
            if l.startswith("@@ ") or l.startswith("diff --git"):
                break
            hunk_body.append(l)
            i += 1

        old_lines: List[str] = []
        new_lines: List[str] = []
        for l in hunk_body:
            if l.startswith("+"):
                new_lines.append(l[1:])
            elif l.startswith("-"):
                old_lines.append(l[1:])
            elif l.startswith("\\"):
                continue
            else:
                ctx = l[1:] if l.startswith(" ") else l
                old_lines.append(ctx)
                new_lines.append(ctx)

        if old_lines == new_lines:
            changed = True
            continue

        fixed.append(hunk_header)
        fixed.extend(hunk_body)

    return "\n".join(fixed).strip() + "\n", changed


def _recount_hunks(diff: str) -> Tuple[str, bool]:
    lines = diff.splitlines()
    fixed: List[str] = []
    changed = False
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith("@@ "):
            m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
            if not m:
                fixed.append(line)
                i += 1
                continue
            old_start = m.group(1)
            new_start = m.group(3)
            old_count = 0
            new_count = 0
            j = i + 1
            while j < len(lines):
                l = lines[j]
                if l.startswith("@@ ") or l.startswith("diff --git"):
                    break
                if l.startswith("\\"):
                    j += 1
                    continue
                if l.startswith("+"):
                    new_count += 1
                elif l.startswith("-"):
                    old_count += 1
                else:
                    old_count += 1
                    new_count += 1
                j += 1
            new_header = f"@@ -{old_start},{old_count} +{new_start},{new_count} @@"
            if new_header != line:
                changed = True
            fixed.append(new_header)
            fixed.extend(lines[i + 1:j])
            i = j
            continue
        fixed.append(line)
        i += 1

    return "\n".join(fixed).strip() + "\n", changed


def extract_fallback_diff(text: str) -> Tuple[Optional[str], bool, Optional[str]]:
    diff = extract_diff(text)
    if not diff:
        return None, False, "NO_DIFF"

    fixed, changed1 = _fix_hunk_line_prefixes(diff)
    fixed, changed2 = _trim_hunk_trailing_context(fixed)
    fixed, changed3 = _drop_noop_hunks(fixed)
    fixed, changed4 = _recount_hunks(fixed)
    diff = fixed

    err = _validate_diff_format(diff)
    if err:
        return None, (changed1 or changed2 or changed3 or changed4), err

    return diff, (changed1 or changed2 or changed3 or changed4), None

# -------------------- patch apply --------------------

def apply_patch(
    diff: str,
    repo: Path,
    target_rel: str,
    out_dir: Path,
    repair: bool = False,
    validate_context: bool = True,
) -> Tuple[bool, str, str]:
    patch_file = out_dir / ".attempt.patch"
    patch_file.write_text(diff, encoding="utf-8")
    errors: List[Tuple[str, str]] = []

    if validate_context:
        ctx_err = _validate_diff_context(diff, repo / target_rel)
        if ctx_err:
            save_text(out_dir / "patch_apply_err.txt", ctx_err)
            if repair:
                repaired = repair_diff_to_file(diff, repo / target_rel, target_rel)
                if not repaired:
                    return False, "CONTEXT_MISMATCH", ctx_err
                save_text(out_dir / "diff_repaired.txt", repaired)
                patch_file = out_dir / ".attempt_repaired.patch"
                patch_file.write_text(repaired, encoding="utf-8")
            else:
                return False, "CONTEXT_MISMATCH", ctx_err

    methods = [
        ["git", "apply", "--3way", "--whitespace=nowarn", str(patch_file)],
        ["git", "apply", "--whitespace=nowarn", str(patch_file)],
        ["patch", "-p1", "--fuzz=3", "--batch", "-i", str(patch_file)],
        ["patch", "-p0", "--fuzz=3", "--batch", "-i", str(patch_file)],
    ]

    for cmd in methods:
        log(f"TRY APPLY: {' '.join(cmd)}")
        p = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True)
        if p.returncode == 0:
            rc, out, err, _ = run_cmd(
                f"git -C {repo} diff -- {target_rel}", 10
            )
            save_text(out_dir / "applied_diff_actual.diff", out + err)
            return True, " ".join(cmd), ""
        errors.append((" ".join(cmd), (p.stdout or "") + (p.stderr or "")))

    if not repair:
        summary = _summarize_apply_errors(errors)
        if summary:
            save_text(out_dir / "patch_apply_err.txt", summary)
        return False, "ALL_APPLY_METHODS_FAILED", summary

    repaired = repair_diff_to_file(diff, repo / target_rel, target_rel)
    if not repaired:
        summary = _summarize_apply_errors(errors)
        if summary:
            save_text(out_dir / "patch_apply_err.txt", summary)
        return False, "ALL_APPLY_METHODS_FAILED", summary

    save_text(out_dir / "diff_repaired.txt", repaired)
    repaired_patch = out_dir / ".attempt_repaired.patch"
    repaired_patch.write_text(repaired, encoding="utf-8")

    repaired_methods = [
        ["git", "apply", "--3way", "--whitespace=nowarn", str(repaired_patch)],
        ["git", "apply", "--whitespace=nowarn", str(repaired_patch)],
        ["patch", "-p1", "--fuzz=3", "--batch", "-i", str(repaired_patch)],
        ["patch", "-p0", "--fuzz=3", "--batch", "-i", str(repaired_patch)],
    ]
    for cmd in repaired_methods:
        log(f"TRY APPLY (REPAIRED): {' '.join(cmd)}")
        p = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True)
        if p.returncode == 0:
            rc, out, err, _ = run_cmd(
                f"git -C {repo} diff -- {target_rel}", 10
            )
            save_text(out_dir / "applied_diff_actual.diff", out + err)
            return True, "REPAIRED " + " ".join(cmd), ""
        errors.append(("REPAIRED " + " ".join(cmd), (p.stdout or "") + (p.stderr or "")))

    summary = _summarize_apply_errors(errors)
    if summary:
        save_text(out_dir / "patch_apply_err.txt", summary)
    return False, "ALL_APPLY_METHODS_FAILED", summary

# -------------------- prompt --------------------

def build_prompt(task, buggy, failing, attempt, max_attempts, prev):
    rel = qb_relpath(task)
    ctx_label, ctx_text = select_buggy_context(buggy, failing, rel)
    return (
        "You are fixing a Python bug.\n"
        "STRICT RULES:\n"
        "1) Output ONLY a unified diff\n"
        "2) First line MUST be: diff --git\n"
        "3) NO explanation text\n"
        "4) Do NOT wrap in code fences or <PATCH> tags\n"
        "5) Do NOT repeat the prompt\n\n"
        f"Target:\n"
        f"a/{rel}\n"
        f"b/{rel}\n\n"
        f"Attempt {attempt}/{max_attempts}\n"
        f"Previous status: {prev}\n\n"
        f"{ctx_label}\n"
        f"{ctx_text}\n\n"
        "Failing output:\n"
        "```\n"
        f"{failing}\n"
        "```\n"
    )


def build_fallback_prompt(task, buggy, failing, slm_attempt_summaries, fallback_attempt_summaries=None):
    rel = qb_relpath(task)
    summary = "\n".join(slm_attempt_summaries) if slm_attempt_summaries else "None"
    fb_summary = "\n".join(fallback_attempt_summaries) if fallback_attempt_summaries else "None"
    return (
        "You are a senior software engineer fixing a Python bug.\n"
        "STRICT OUTPUT RULES:\n"
        "1) Output ONLY a unified diff patch.\n"
        "2) First line MUST start with: diff --git\n"
        "3) Do NOT add any explanation before or after the diff.\n"
        "4) Provide COMPLETE hunks (do not truncate).\n"
        "5) Do NOT use code fences. Optional wrapper ONLY if needed: <PATCH> ... </PATCH>\n"
        "6) Every hunk line MUST start with one of: space, '+', '-', or '\\'.\n"
        "7) Unchanged context lines MUST start with a single space.\n"
        f"Target path MUST be exactly: a/{rel} and b/{rel}\n\n"
        "SLM attempts summary:\n"
        f"{summary}\n\n"
        "Fallback attempts summary:\n"
        f"{fb_summary}\n\n"
        "Buggy file content (exact):\n```python\n"
        f"{buggy}\n"
        "```\n\n"
        "Failing test output:\n```\n"
        f"{failing}\n"
        "```\n"
    )

# -------------------- SLM runner --------------------

def _kill_process_group(p):
    try:
        os.killpg(p.pid, signal.SIGTERM)
        time.sleep(0.2)
        os.killpg(p.pid, signal.SIGKILL)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass

def _resolve_llama_binary(llama_path: str) -> Tuple[str, str]:
    p = Path(llama_path)
    name = p.name.lower()
    if "llama-completion" in name:
        return str(p), "completion"
    if "llama-cli" in name or name == "main":
        candidate = p.with_name("llama-completion")
        if candidate.exists():
            return str(candidate), "completion"
    return str(p), "cli"

def _build_slm_cmd(llama_path: str, model: str, prompt_file: Path) -> Tuple[List[str], str]:
    llama_bin, mode = _resolve_llama_binary(llama_path)
    cmd = [
        llama_bin,
        "-m", model,
        "-n", "1200",
        "--temp", "0.0",
        "-f", str(prompt_file),
    ]
    return cmd, mode

def run_slm(llama, model, prompt_file, timeout, out_p, err_p, max_output_bytes: Optional[int] = None):
    cmd, mode = _build_slm_cmd(llama, model, Path(prompt_file))
    log(f"SLM: mode={mode} bin={cmd[0]}")
    start = time.time()
    with open(out_p, "w") as fo, open(err_p, "w") as fe:
        p = subprocess.Popen(cmd, stdout=fo, stderr=fe, start_new_session=True)
        while True:
            if p.poll() is not None:
                return p.returncode, time.time() - start
            if time.time() - start > timeout:
                fe.write("\n[SLM TIMEOUT]\n")
                _kill_process_group(p)
                return 124, time.time() - start
            if max_output_bytes:
                try:
                    if Path(out_p).stat().st_size > max_output_bytes:
                        fe.write("\n[SLM OUTPUT LIMIT]\n")
                        _kill_process_group(p)
                        return 125, time.time() - start
                except Exception:
                    pass
            time.sleep(0.5)

# -------------------- main --------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_path", required=True)
    ap.add_argument("--task_index", type=int, required=True)
    ap.add_argument("--llama_path", required=True)
    ap.add_argument("--gguf_model_path", required=True)
    ap.add_argument("--max_attempts", type=int, default=5)
    ap.add_argument("--slm_timeout_s", type=int, default=900)
    ap.add_argument("--slm_max_output_mb", type=int, default=8)
    ap.add_argument("--skip_rollback", action="store_true")
    ap.add_argument("--fallback_model", default="")
    ap.add_argument("--fallback_max_attempts", type=int, default=2)
    ap.add_argument("--fallback_timeout_s", type=int, default=120)
    ap.add_argument("--fallback_max_new_tokens", type=int, default=1200)
    ap.add_argument("--fallback_temp", type=float, default=0.0)
    ap.add_argument("--repo_root", default=".")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    task = read_jsonl_line(args.tasks_path, args.task_index)

    qb_repo = Path(task["quixbugs_dir"]).resolve()
    test_cmd = task["test_cmd"]
    test_timeout = max(int(task.get("test_timeout_s", 3)), 10)

    run_dir = repo_root / "episodes/quixbugs_runs/attempts" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task['algo']}"
    run_dir.mkdir(parents=True, exist_ok=True)

    log(f"TASK: {task['task_id']}")
    log(f"RUN_DIR: {run_dir}")

    if args.fallback_model and not os.environ.get("OPENAI_API_KEY"):
        log("FALLBACK ERROR: OPENAI_API_KEY is not set")
        save_text(run_dir / "fallback_status.txt", "ERROR_NO_OPENAI_API_KEY")
        return 2

    stage("BASELINE")
    rc0, o0, e0, _ = run_cmd(test_cmd, test_timeout, cwd=str(repo_root))
    save_text(run_dir / "test_before.txt", o0 + e0)

    if rc0 == 0:
        save_text(run_dir / "final_status.txt", "ALREADY_PASS")
        log("BASELINE PASS – EXIT")
        return 0

    prev_status = "INIT"
    slm_attempt_summaries: List[str] = []
    buggy_abs = repo_root / task["buggy_path"]

    for k in range(1, args.max_attempts + 1):
        stage(f"ATTEMPT {k}/{args.max_attempts}")
        ad = run_dir / f"attempt_{k:02d}"
        ad.mkdir(exist_ok=True)

        if not args.skip_rollback:
            run_cmd(qb_rollback(task), 30, cwd=str(repo_root))

        rc_pre, o_pre, e_pre, _ = run_cmd(test_cmd, test_timeout, cwd=str(repo_root))
        save_text(ad / "test_pre.txt", o_pre + e_pre)

        buggy = load_text(buggy_abs)
        prompt = build_prompt(task, buggy, o_pre + e_pre, k, args.max_attempts, prev_status)
        save_text(ad / "prompt.txt", prompt)

        stage("SLM")
        rc_slm, dt = run_slm(
            args.llama_path,
            args.gguf_model_path,
            ad / "prompt.txt",
            args.slm_timeout_s,
            ad / "slm_raw.txt",
            ad / "slm_err.txt",
            args.slm_max_output_mb * 1024 * 1024 if args.slm_max_output_mb > 0 else None,
        )
        log(f"SLM rc={rc_slm} time={dt:.1f}s")

        diff = extract_slm_diff(load_text(ad / "slm_raw.txt"))
        if not diff:
            prev_status = "BAD_DIFF"
            log("BAD_DIFF")
            slm_attempt_summaries.append(f"attempt_{k:02d}: {prev_status}")
            continue
        diff, sanitized, err = sanitize_slm_diff(diff)
        if not diff:
            reason = _one_line(err or "", 260)
            prev_status = f"BAD_DIFF_FORMAT: {reason}" if reason else "BAD_DIFF_FORMAT"
            log("BAD_DIFF_FORMAT")
            slm_attempt_summaries.append(f"attempt_{k:02d}: {prev_status}")
            continue
        if sanitized:
            save_text(ad / "diff_sanitized.txt", diff)

        stage("PATCH APPLY")
        ok, method, reason = apply_patch(diff, qb_repo, qb_relpath(task), ad, repair=True, validate_context=True)
        log(f"PATCH RESULT: {method}")

        if not ok:
            reason_line = _one_line(reason or "", 260)
            prev_status = f"PATCH_APPLY_FAIL: {reason_line}" if reason_line else "PATCH_APPLY_FAIL"
            slm_attempt_summaries.append(f"attempt_{k:02d}: {prev_status}")
            continue

        stage("POST TEST")
        rc_post, o_post, e_post, _ = run_cmd(test_cmd, test_timeout, cwd=str(repo_root))
        save_text(ad / "test_after.txt", o_post + e_post)

        if rc_post == 0:
            save_text(run_dir / "final_status.txt", "PASS")
            log("PASS")
            return 0

        fail_reason = _one_line(_tail_lines(o_post + e_post, 12), 260)
        prev_status = f"FAIL: {fail_reason}" if fail_reason else "FAIL"
        slm_attempt_summaries.append(f"attempt_{k:02d}: {prev_status}")

    if args.fallback_model:
        stage("FALLBACK")
        fallback_attempt_summaries: List[str] = []
        for fk in range(1, args.fallback_max_attempts + 1):
            stage(f"FALLBACK {fk}/{args.fallback_max_attempts}")
            fd = run_dir / f"fallback_{fk:02d}"
            fd.mkdir(exist_ok=True)

            if not args.skip_rollback:
                run_cmd(qb_rollback(task), 30, cwd=str(repo_root))

            rc_pre, o_pre, e_pre, _ = run_cmd(test_cmd, test_timeout, cwd=str(repo_root))
            save_text(fd / "test_pre.txt", o_pre + e_pre)

            buggy = load_text(buggy_abs)
            fb_prompt = build_fallback_prompt(
                task,
                buggy,
                o_pre + e_pre,
                slm_attempt_summaries,
                fallback_attempt_summaries,
            )
            save_text(fd / "prompt.txt", fb_prompt)

            try:
                llm_out, _meta = openai_chat_completion(
                    fb_prompt,
                    model=args.fallback_model,
                    temperature=args.fallback_temp,
                    max_tokens=args.fallback_max_new_tokens,
                    timeout_s=args.fallback_timeout_s,
                )
            except Exception as e:
                msg = str(e).strip()
                if not msg:
                    msg = repr(e)
                status = f"FALLBACK_ERROR: {type(e).__name__}: {msg}"
                save_text(fd / "status.txt", status)
                log(status)
                fallback_attempt_summaries.append(f"fallback_{fk:02d}: {status}")
                continue

            save_text(fd / "llm_raw.txt", llm_out)
            diff, sanitized, err = extract_fallback_diff(llm_out)
            if not diff:
                reason = _one_line(err or "", 260)
                if err and reason:
                    status = f"FALLBACK_BAD_DIFF_FORMAT: {reason}"
                else:
                    status = "FALLBACK_BAD_DIFF_FORMAT" if err else "FALLBACK_BAD_DIFF"
                save_text(fd / "status.txt", status)
                log(status)
                fallback_attempt_summaries.append(f"fallback_{fk:02d}: {status}")
                continue
            if sanitized:
                save_text(fd / "diff_sanitized.txt", diff)

            # Fallback diffs often have valid intent but weak hunk anchors.
            # Reuse context validation + repair so near-miss patches can still apply.
            ok, method, reason = apply_patch(
                diff,
                qb_repo,
                qb_relpath(task),
                fd,
                repair=True,
                validate_context=True,
            )
            log(f"FALLBACK PATCH RESULT: {method}")
            if not ok:
                reason_line = _one_line(reason or "", 260)
                status = f"FALLBACK_PATCH_APPLY_FAIL: {reason_line}" if reason_line else "FALLBACK_PATCH_APPLY_FAIL"
                save_text(fd / "status.txt", status)
                log(status)
                fallback_attempt_summaries.append(f"fallback_{fk:02d}: {status}")
                continue

            rc_post, o_post, e_post, _ = run_cmd(test_cmd, test_timeout, cwd=str(repo_root))
            save_text(fd / "test_after.txt", o_post + e_post)
            if rc_post == 0:
                save_text(run_dir / "final_status.txt", "PASS")
                log("PASS (fallback)")
                return 0

            status = "FALLBACK_FAIL"
            save_text(fd / "status.txt", status)
            log(status)
            fallback_attempt_summaries.append(f"fallback_{fk:02d}: {status}")

    save_text(run_dir / "final_status.txt", "FAIL")
    log("FAIL AFTER ALL ATTEMPTS")
    return 1

if __name__ == "__main__":
    sys.exit(main())
