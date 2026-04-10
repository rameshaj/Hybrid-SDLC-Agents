# QuixBug and HumanEval Code Snapshot

Date captured: 2026-03-14

## QuixBugs v5 Code
Source: `src/step6_orchestrator_quixbugs_v5_attempts.py`

```python
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
```

## HumanEval Code (Latest in Repo)
Requested as 'HumanEval v5', but `v5` is not present in this repository. Included latest available script: `src/humaneval/run_humaneval_hybrid_v2.py`.

```python
#!/usr/bin/env python3
"""
HumanEval hybrid runner v2: SLM first, fallback to LLM if needed.
Adds optional RAG hints from FAISS cases.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.slm_llama_cli import SLMConfig
from src.core.retriever_rag_cases_v2 import RagCaseRetriever
from src.llm_fallback_openai_codegen import openai_chat_completion_codegen

RAG_INDEX_PATH = Path("data/derived/rag/cases.index.faiss")
RAG_META_PATH = Path("data/derived/rag/cases.meta.jsonl")
_RAG_RETRIEVER: Optional[RagCaseRetriever] = None
_RAG_ERROR: Optional[str] = None


@dataclass
class EvalResult:
    ok: bool
    score: float
    rc: int
    stdout: str
    stderr: str
    elapsed_s: float
    failure_summary: str = ""


class RuleBasedRouter:
    """
    Rule-based router.
    Hook point for learned router later (RouteLLM-style).
    """

    def decide(
        self,
        score: float,
        pass_threshold: float,
        slm_attempts_left: int,
        fallback_attempts_left: int,
    ) -> Tuple[str, str]:
        if score >= pass_threshold:
            return "ACCEPT", "score >= threshold"
        if slm_attempts_left > 0:
            return "RETRY_SLM", "score < threshold; slm attempts left"
        if fallback_attempts_left > 0:
            return "ESCALATE_LLM", "score < threshold; fallback attempts left"
        return "GIVE_UP", "score < threshold; no attempts left"


def load_tasks(path: Path) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tasks.append(json.loads(line))
    return tasks


def extract_code(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"```python\n(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\n(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    # Strip common chat prefixes
    if "assistant" in text:
        text = text.split("assistant", 1)[1]
    if "user" in text and text.strip().startswith("user"):
        text = text.split("user", 1)[-1]
    return text.strip()


def clean_code_blob(code: str) -> str:
    if not code:
        return code
    cleaned: List[str] = []
    for line in code.splitlines():
        s = line.strip()
        if s.startswith("```"):
            continue
        if s.startswith("assistant") or s.startswith("user"):
            continue
        if s.startswith("> EOF"):
            continue
        if s.startswith(("- ", "* ", "• ")):
            continue
        if line.startswith(("build:", "main:", "llama_", "common_", "system_info:", "sampler ", "load:")):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def trim_to_entry_point(code: str, entry_point: str) -> str:
    if not code or not entry_point:
        return code
    needle = f"def {entry_point}"
    idx = code.rfind(needle)
    if idx != -1:
        return code[idx:]
    return code


def classify_error(summary: str) -> str:
    if not summary:
        return "UNKNOWN"
    for key in [
        "SLM_TIMEOUT",
        "TIMEOUT",
        "NameError",
        "AssertionError",
        "SyntaxError",
        "IndentationError",
        "TypeError",
        "ValueError",
        "IndexError",
        "KeyError",
        "UnboundLocalError",
        "ModuleNotFoundError",
        "NO_CODE_EXTRACTED",
    ]:
        if key in summary:
            return key
    return "OTHER"


def build_rag_query(task_prompt: str, entry_point: str, failure_summary: str) -> str:
    failure_type = classify_error(failure_summary)
    parts = [
        f"entry_point: {entry_point}",
        f"error_type: {failure_type}",
        f"error_summary: {failure_summary}",
        "prompt:",
        task_prompt.strip(),
    ]
    return "\n".join([p for p in parts if p]).strip() + "\n"


def truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def extract_added_imports(diff_text: str) -> List[str]:
    imports: List[str] = []
    for line in diff_text.splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        if line.startswith("+import ") or line.startswith("+from "):
            imports.append(line[1:].strip())
    return imports


def format_rag_context(hits: List[Dict[str, Any]], max_chars: int = 1200) -> str:
    if not hits:
        return ""
    lines: List[str] = ["RAG hints from similar cases:"]
    for i, h in enumerate(hits, start=1):
        task_id = h.get("task_id", "")
        err = h.get("slm_failure_type", "")
        fix_actions = h.get("fix_actions", [])
        score = h.get("score", 0.0)
        lines.append(f"[case {i}] task_id={task_id} error={err} fix_actions={fix_actions} score={score:.3f}")
        diff = (h.get("fix_diff") or "").strip()
        added_imports = extract_added_imports(diff)
        if added_imports:
            lines.append("import_hints: " + ", ".join(added_imports))
        if diff:
            lines.append("fix_diff:")
            lines.append(truncate_text(diff, 600))
    return truncate_text("\n".join(lines), max_chars)


def get_rag_retriever() -> Optional[RagCaseRetriever]:
    global _RAG_RETRIEVER, _RAG_ERROR
    if _RAG_ERROR:
        return None
    if _RAG_RETRIEVER is None:
        if not RAG_INDEX_PATH.exists() or not RAG_META_PATH.exists():
            _RAG_ERROR = "missing_rag_index_or_meta"
            return None
        retriever = RagCaseRetriever(index_path=RAG_INDEX_PATH, meta_path=RAG_META_PATH)
        retriever.load()
        _RAG_RETRIEVER = retriever
    return _RAG_RETRIEVER


def build_rag_context(
    task_prompt: str,
    entry_point: str,
    failure_summary: str,
    rag_top_k: int,
    attempt_dir: Path,
) -> str:
    retriever = get_rag_retriever()
    query = build_rag_query(task_prompt, entry_point, failure_summary)
    save_text(attempt_dir / "rag_query.txt", query)
    if retriever is None:
        save_text(attempt_dir / "rag_error.txt", _RAG_ERROR or "rag_unavailable")
        return ""
    try:
        hits = retriever.retrieve(query, k=rag_top_k)
    except Exception as e:
        save_text(attempt_dir / "rag_error.txt", str(e))
        return ""
    save_text(attempt_dir / "rag_hits.json", json.dumps(hits, indent=2))
    return format_rag_context(hits)


def build_prompt(
    task_prompt: str,
    entry_point: str,
    prev_failures: List[str],
    rag_context: str,
    self_debug_notes: str,
) -> str:
    header = (
        "You are a coding assistant.\n"
        "Implement the function below.\n"
        "Return ONLY valid Python code for the function. No explanations, no markdown.\n"
        "Do NOT include tests or example usage.\n"
        "Self-debug notes are hints only. Do NOT copy them into the code.\n"
        f"Function name: {entry_point}\n"
    )
    if prev_failures:
        header += "Previous failures:\n"
        for item in prev_failures:
            header += f"- {item}\n"
    if self_debug_notes:
        header += "Self-debug notes:\n"
        header += self_debug_notes.strip() + "\n"
    if rag_context:
        header += "RAG hints:\n"
        header += rag_context + "\n"
    return header + "\n" + task_prompt.strip() + "\n"


def build_fallback_system_prompt() -> str:
    return (
        "You are a coding assistant. "
        "Return ONLY valid Python code for the function. "
        "No explanations, no markdown."
    )


def build_self_debug_prompt(
    task_prompt: str,
    entry_point: str,
    code: str,
    failure_summary: str,
    max_code_chars: int = 1200,
) -> str:
    code_block = truncate_text(code.strip(), max_code_chars) if code else ""
    return (
        "You are a debugging assistant.\n"
        "Given the task and failing code, propose minimal fixes.\n"
        "Return 1-3 short bullet points, each starting with '- '. No code.\n"
        f"Function name: {entry_point}\n"
        "Task:\n"
        f"{task_prompt.strip()}\n\n"
        "Failed code:\n"
        f"{code_block}\n\n"
        "Failure:\n"
        f"{failure_summary}\n"
    )


def clean_self_debug_notes(text: str) -> str:
    if not text:
        return ""
    cleaned: List[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("---"):
            continue
        if s.startswith("```"):
            continue
        if s.startswith("assistant") or s.startswith("user"):
            continue
        if s.startswith(("-", "*", "•")):
            item = s.lstrip("-*•").strip()
            if item:
                cleaned.append(f"- {item}")
    return "\n".join(cleaned[:3]).strip()


def run_slm_prompt(prompt: str, cfg: SLMConfig, timeout_s: int | None = None) -> str:
    if timeout_s is None:
        timeout_s = cfg.timeout_s

    cmd = [
        cfg.llama_cli,
        "-m", cfg.model_path,
        "-p", prompt,
        "-n", str(cfg.n_tokens),
        "--seed", str(cfg.seed),
        "--temp", str(cfg.temp),
        "--top-p", str(cfg.top_p),
        "--repeat-penalty", str(cfg.repeat_penalty),
    ]

    p = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        timeout=timeout_s,
        stdin=subprocess.DEVNULL,
    )

    # Some llama-cli builds emit tokens to stderr; combine streams for extraction.
    stdout = p.stdout or ""
    stderr = p.stderr or ""
    if stdout and stderr:
        return (stdout + "\n" + stderr).strip()
    return (stdout or stderr).strip()


def summarize_failure(rc: int, stdout: str, stderr: str, timed_out: bool) -> str:
    if timed_out:
        return "TIMEOUT"
    if rc == 0:
        return "PASS"
    blob = (stderr or "") + ("\n" if stderr and stdout else "") + (stdout or "")
    lines = [ln for ln in blob.splitlines() if ln.strip()]
    tail = "\n".join(lines[-6:]) if lines else "no output"
    # Try to extract exception line
    exc = ""
    for ln in reversed(lines):
        if "Error" in ln or "Exception" in ln or "AssertionError" in ln:
            exc = ln.strip()
            break
    if exc:
        return f"{exc} | tail: {tail}"
    return f"FAIL | tail: {tail}"


def build_test_file(code: str, test: str, entry_point: str) -> str:
    return (
        f"{code}\n\n"
        f"{test}\n\n"
        "def __run_tests():\n"
        f"    check(globals().get('{entry_point}'))\n\n"
        "if __name__ == '__main__':\n"
        "    __run_tests()\n"
    )


def run_tests(code: str, test: str, entry_point: str, timeout_s: int, work_dir: Path) -> EvalResult:
    tmp_path = work_dir / "candidate_run.py"
    tmp_path.write_text(build_test_file(code, test, entry_point), encoding="utf-8")

    start = time.time()
    timed_out = False
    try:
        p = subprocess.run(
            [sys.executable, str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        rc = p.returncode
        stdout = p.stdout or ""
        stderr = p.stderr or ""
    except subprocess.TimeoutExpired as e:
        timed_out = True
        rc = 124
        stdout = e.stdout or ""
        stderr = (e.stderr or "") + "\n[TIMEOUT]\n"

    elapsed = time.time() - start
    ok = (rc == 0) and (not timed_out)
    score = 1.0 if ok else 0.0
    summary = summarize_failure(rc, stdout, stderr, timed_out)

    return EvalResult(
        ok=ok,
        score=score,
        rc=rc,
        stdout=stdout,
        stderr=stderr,
        elapsed_s=elapsed,
        failure_summary=summary,
    )


def ensure_run_dir(base: Path, task_id: str) -> Path:
    ts = time.strftime("%Y%m%d_%H%M%S")
    safe_id = task_id.replace("/", "_")
    run_dir = base / f"{ts}_{safe_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text or "", encoding="utf-8")


def load_dotenv_if_present(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = val


def run_task(
    task: Dict[str, Any],
    slm_cfg: SLMConfig,
    slm_attempts: int,
    fallback_attempts: int,
    pass_threshold: float,
    test_timeout_s: int,
    out_base: Path,
    fallback_model: str,
    fallback_timeout_s: int,
    fallback_max_tokens: int,
    fallback_temp: float,
    rag_enabled: bool,
    rag_top_k: int,
    self_debug_enabled: bool,
    self_debug_max_tokens: int,
) -> Dict[str, Any]:
    task_id = task.get("task_id", "unknown")
    entry_point = task.get("entry_point", "")
    prompt = task.get("prompt", "")
    test = task.get("test", "")

    run_dir = ensure_run_dir(out_base, task_id)
    save_text(run_dir / "task.json", json.dumps(task, indent=2))

    router = RuleBasedRouter()
    slm_failures: List[str] = []
    fallback_failures: List[str] = []
    rag_context = ""
    self_debug_notes = ""

    # SLM attempts
    slm_best: Optional[Dict[str, Any]] = None
    for k in range(1, slm_attempts + 1):
        ad = run_dir / f"slm_attempt_{k:02d}"
        ad.mkdir(exist_ok=True)
        attempt_prompt = build_prompt(prompt, entry_point, slm_failures, rag_context, self_debug_notes)
        save_text(ad / "prompt.txt", attempt_prompt)

        code = ""
        try:
            raw = run_slm_prompt(attempt_prompt, slm_cfg, timeout_s=slm_cfg.timeout_s)
            save_text(ad / "slm_raw.txt", raw)

            code = trim_to_entry_point(clean_code_blob(extract_code(raw)), entry_point)
            save_text(ad / "code.py", code)

            if not code:
                res = EvalResult(
                    ok=False, score=0.0, rc=1, stdout="", stderr="NO_CODE", elapsed_s=0.0,
                    failure_summary="NO_CODE_EXTRACTED",
                )
            else:
                res = run_tests(code, test, entry_point, test_timeout_s, ad)
        except subprocess.TimeoutExpired:
            save_text(ad / "slm_raw.txt", "")
            save_text(ad / "code.py", "")
            res = EvalResult(
                ok=False, score=0.0, rc=124, stdout="", stderr="SLM_TIMEOUT", elapsed_s=0.0,
                failure_summary="SLM_TIMEOUT",
            )
        except Exception as e:
            msg = str(e).strip() or repr(e)
            save_text(ad / "slm_raw.txt", "")
            save_text(ad / "code.py", "")
            save_text(ad / "slm_error.txt", msg)
            res = EvalResult(
                ok=False, score=0.0, rc=1, stdout="", stderr=msg, elapsed_s=0.0,
                failure_summary=f"SLM_ERROR: {msg}",
            )

        save_text(ad / "test_stdout.txt", res.stdout)
        save_text(ad / "test_stderr.txt", res.stderr)
        save_text(ad / "result.json", json.dumps(res.__dict__, indent=2))

        slm_failures.append(f"attempt_{k:02d}: {res.failure_summary}")
        if self_debug_enabled and res.score < pass_threshold and code:
            debug_cfg = SLMConfig(
                timeout_s=slm_cfg.timeout_s,
                llama_cli=slm_cfg.llama_cli,
                model_path=slm_cfg.model_path,
                n_tokens=self_debug_max_tokens,
                seed=slm_cfg.seed,
                temp=slm_cfg.temp,
                top_p=slm_cfg.top_p,
                repeat_penalty=slm_cfg.repeat_penalty,
            )
            debug_prompt = build_self_debug_prompt(prompt, entry_point, code, res.failure_summary)
            save_text(ad / "self_debug_prompt.txt", debug_prompt)
            try:
                debug_raw = run_slm_prompt(debug_prompt, debug_cfg, timeout_s=slm_cfg.timeout_s)
                save_text(ad / "self_debug_raw.txt", debug_raw)
                self_debug_notes = clean_self_debug_notes(debug_raw)
                save_text(ad / "self_debug_notes.txt", self_debug_notes)
            except Exception as e:
                save_text(ad / "self_debug_error.txt", str(e))
        if rag_enabled and res.score < pass_threshold:
            rag_context = build_rag_context(prompt, entry_point, res.failure_summary, rag_top_k, ad)
            save_text(ad / "rag_context.txt", rag_context)

        if slm_best is None or res.score > slm_best["score"]:
            slm_best = {"score": res.score, "ok": res.ok, "code": code, "dir": str(ad), "res": res.__dict__}

        action, reason = router.decide(res.score, pass_threshold, slm_attempts - k, fallback_attempts)
        if action == "ACCEPT":
            save_text(run_dir / "final_status.json", json.dumps({
                "status": "PASS",
                "model": "SLM",
                "attempt": k,
                "reason": reason,
                "score": res.score,
                "rag_enabled": bool(rag_enabled),
                "rag_top_k": int(rag_top_k),
            }, indent=2))
            return {"status": "PASS", "model": "SLM", "attempt": k, "run_dir": str(run_dir)}

    # Fallback attempts
    if fallback_attempts > 0:
        for k in range(1, fallback_attempts + 1):
            fd = run_dir / f"fallback_attempt_{k:02d}"
            fd.mkdir(exist_ok=True)
            fb_prompt = build_prompt(
                prompt,
                entry_point,
                slm_failures + fallback_failures,
                rag_context,
                self_debug_notes,
            )
            save_text(fd / "prompt.txt", fb_prompt)

            try:
                raw, _meta = openai_chat_completion_codegen(
                    fb_prompt,
                    model=fallback_model,
                    temperature=fallback_temp,
                    max_tokens=fallback_max_tokens,
                    timeout_s=fallback_timeout_s,
                    system_prompt=build_fallback_system_prompt(),
                )
            except Exception as e:
                msg = str(e).strip() or repr(e)
                fallback_failures.append(f"fallback_{k:02d}: ERROR {msg}")
                save_text(fd / "error.txt", msg)
                continue

            save_text(fd / "llm_raw.txt", raw)
            code = trim_to_entry_point(clean_code_blob(extract_code(raw)), entry_point)
            save_text(fd / "code.py", code)

            if not code:
                res = EvalResult(
                    ok=False, score=0.0, rc=1, stdout="", stderr="NO_CODE", elapsed_s=0.0,
                    failure_summary="NO_CODE_EXTRACTED",
                )
            else:
                res = run_tests(code, test, entry_point, test_timeout_s, fd)

            save_text(fd / "test_stdout.txt", res.stdout)
            save_text(fd / "test_stderr.txt", res.stderr)
            save_text(fd / "result.json", json.dumps(res.__dict__, indent=2))

            fallback_failures.append(f"fallback_{k:02d}: {res.failure_summary}")

            if res.score >= pass_threshold:
                save_text(run_dir / "final_status.json", json.dumps({
                    "status": "PASS",
                    "model": "LLM",
                    "attempt": k,
                    "score": res.score,
                    "rag_enabled": bool(rag_enabled),
                    "rag_top_k": int(rag_top_k),
                }, indent=2))
                return {"status": "PASS", "model": "LLM", "attempt": k, "run_dir": str(run_dir)}

    # If none passed
    save_text(run_dir / "final_status.json", json.dumps({
        "status": "FAIL",
        "best_slm": slm_best,
        "slm_failures": slm_failures,
        "fallback_failures": fallback_failures,
        "rag_enabled": bool(rag_enabled),
        "rag_top_k": int(rag_top_k),
    }, indent=2))
    return {"status": "FAIL", "model": "NONE", "run_dir": str(run_dir)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_path", default="data/external/humaneval/humaneval_train.jsonl")
    ap.add_argument("--task_index", type=int, default=-1)
    ap.add_argument("--task_id", default="")
    ap.add_argument("--max_tasks", type=int, default=-1)

    ap.add_argument("--llama_path", default=os.environ.get("LLAMA_COMPLETION", "/usr/local/bin/llama-completion"))
    ap.add_argument("--gguf_model_path", default="models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf")
    ap.add_argument("--max_new_tokens", type=int, default=256)
    ap.add_argument("--slm_timeout_s", type=int, default=120)
    ap.add_argument("--slm_attempts", type=int, default=2)

    ap.add_argument("--test_timeout_s", type=int, default=5)
    ap.add_argument("--pass_threshold", type=float, default=1.0)

    ap.add_argument("--fallback_attempts", type=int, default=1)
    ap.add_argument("--fallback_model", default="gpt-4.2")
    ap.add_argument("--fallback_timeout_s", type=int, default=120)
    ap.add_argument("--fallback_max_tokens", type=int, default=512)
    ap.add_argument("--fallback_temp", type=float, default=0.0)

    ap.add_argument("--rag_enabled", type=int, default=0)
    ap.add_argument("--rag_top_k", type=int, default=3)
    ap.add_argument("--self_debug_enabled", type=int, default=1)
    ap.add_argument("--self_debug_max_tokens", type=int, default=128)

    ap.add_argument("--out_dir", default="episodes/humaneval_runs")

    args = ap.parse_args()

    os.chdir(REPO_ROOT)
    load_dotenv_if_present(REPO_ROOT / ".env")

    tasks = load_tasks(Path(args.tasks_path))

    # select tasks
    if args.task_id:
        tasks = [t for t in tasks if t.get("task_id") == args.task_id]
    elif args.task_index >= 0:
        if args.task_index >= len(tasks):
            raise IndexError(f"task_index {args.task_index} out of range (n={len(tasks)})")
        tasks = [tasks[args.task_index]]

    if args.max_tasks > 0:
        tasks = tasks[: args.max_tasks]

    if not tasks:
        print("No tasks selected.")
        return 2

    slm_cfg = SLMConfig(
        timeout_s=args.slm_timeout_s,
        llama_cli=args.llama_path,
        model_path=args.gguf_model_path,
        n_tokens=args.max_new_tokens,
    )

    out_base = Path(args.out_dir)
    out_base.mkdir(parents=True, exist_ok=True)

    summary_path = out_base / "runs_summary.jsonl"
    with summary_path.open("a", encoding="utf-8") as sf:
        for task in tasks:
            res = run_task(
                task=task,
                slm_cfg=slm_cfg,
                slm_attempts=args.slm_attempts,
                fallback_attempts=args.fallback_attempts,
                pass_threshold=args.pass_threshold,
                test_timeout_s=args.test_timeout_s,
                out_base=out_base,
                fallback_model=args.fallback_model,
                fallback_timeout_s=args.fallback_timeout_s,
                fallback_max_tokens=args.fallback_max_tokens,
                fallback_temp=args.fallback_temp,
                rag_enabled=bool(args.rag_enabled),
                rag_top_k=args.rag_top_k,
                self_debug_enabled=bool(args.self_debug_enabled),
                self_debug_max_tokens=args.self_debug_max_tokens,
            )
            sf.write(json.dumps(res) + "\n")
            sf.flush()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
