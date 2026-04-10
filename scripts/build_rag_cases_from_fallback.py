#!/usr/bin/env python3
"""
Build RAG case memory from LLM fallback runs that passed tests.
Only stores cases where fallback produced a passing solution.
"""

from __future__ import annotations

import argparse
import ast
import difflib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


RUN_RE = re.compile(r"^(\d{8})_(\d{6})_")


@dataclass
class Case:
    case_id: str
    task_id: str
    dataset: str
    entry_point: str
    prompt: str
    slm_failure_type: str
    slm_failure_summary: str
    slm_code: str
    llm_code: str
    fix_diff: str
    fix_actions: List[str]
    run_dir: str
    timestamp: str


def parse_run_ts(name: str) -> Optional[datetime]:
    m = RUN_RE.match(name)
    if not m:
        return None
    ts = f"{m.group(1)}_{m.group(2)}"
    try:
        return datetime.strptime(ts, "%Y%m%d_%H%M%S")
    except ValueError:
        return None


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


def sanitize_code(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines()

    # Extract the first fenced code block if present.
    in_block = False
    block_lines: List[str] = []
    for line in lines:
        if line.strip().startswith("```"):
            if in_block:
                break
            in_block = True
            continue
        if in_block:
            block_lines.append(line)

    if block_lines:
        lines = block_lines

    # Drop common chat artifacts.
    while lines and lines[0].strip().lower() in ("assistant", "assistant:", "assistant response:"):
        lines = lines[1:]
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("> eof"):
            lines = lines[:i]
            break

    return "\n".join(lines).strip()


def is_valid_python(code: str) -> bool:
    if not code:
        return False
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def summarize_fix_actions(diff_lines: Iterable[str]) -> List[str]:
    actions = set()
    for line in diff_lines:
        if not line.startswith("+") or line.startswith("+++"):
            continue
        s = line[1:].strip()
        if s.startswith("import ") or s.startswith("from "):
            actions.add("add_import")
        if s.startswith("if ") or s.startswith("elif "):
            actions.add("add_guard")
        if s.startswith("return "):
            actions.add("change_return")
    return sorted(actions)


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def slm_failed(run_dir: Path) -> bool:
    final_status = run_dir / "final_status.json"
    if final_status.exists():
        try:
            data = read_json(final_status)
        except Exception:
            data = {}
        slm_failures = data.get("slm_failures")
        if isinstance(slm_failures, list):
            return len(slm_failures) > 0
        best_slm = data.get("best_slm")
        if isinstance(best_slm, dict) and best_slm.get("ok") is False:
            return True
        if isinstance(best_slm, dict) and best_slm.get("ok") is True:
            return False

    slm_dirs = sorted(run_dir.glob("slm_attempt_*"))
    if not slm_dirs:
        return False
    for attempt_dir in reversed(slm_dirs):
        res_path = attempt_dir / "result.json"
        if not res_path.exists():
            continue
        try:
            res = read_json(res_path)
        except Exception:
            continue
        if "ok" in res:
            return res.get("ok") is False
    return False


def slm_failure_from_run(run_dir: Path) -> Tuple[str, str, str]:
    final_status = run_dir / "final_status.json"
    summary = ""
    if final_status.exists():
        try:
            data = read_json(final_status)
            slm_failures = data.get("slm_failures") or []
            if slm_failures:
                summary = slm_failures[-1]
        except Exception:
            summary = ""
    # fallback to latest slm attempt
    slm_dirs = sorted(run_dir.glob("slm_attempt_*"))
    slm_code = ""
    if slm_dirs:
        last = slm_dirs[-1]
        res_path = last / "result.json"
        if res_path.exists() and not summary:
            try:
                res = read_json(res_path)
                summary = res.get("failure_summary", "") or res.get("stderr", "")
            except Exception:
                pass
        code_path = last / "code.py"
        if code_path.exists():
            slm_code = code_path.read_text(encoding="utf-8")
    return summary, classify_error(summary), slm_code


def pick_fallback_pass(run_dir: Path) -> Optional[Path]:
    fb_dirs = sorted(run_dir.glob("fallback_attempt_*"))
    for fb in fb_dirs:
        res_path = fb / "result.json"
        if not res_path.exists():
            continue
        try:
            res = read_json(res_path)
        except Exception:
            continue
        if res.get("ok") is True:
            return fb
    return None


def build_case(
    run_dir: Path,
    dataset: str,
    require_slm_failure: bool,
    stats: Dict[str, int],
) -> Optional[Case]:
    if require_slm_failure and not slm_failed(run_dir):
        stats["slm_not_failed"] += 1
        return None
    task_path = run_dir / "task.json"
    if not task_path.exists():
        stats["missing_task"] += 1
        return None
    task = read_json(task_path)
    task_id = task.get("task_id", "")
    entry_point = task.get("entry_point", "")
    prompt = task.get("prompt", "") or task.get("complete_prompt", "") or task.get("instruct_prompt", "")

    fb_dir = pick_fallback_pass(run_dir)
    if fb_dir is None:
        stats["no_fallback_pass"] += 1
        return None

    llm_code_path = fb_dir / "code.py"
    if not llm_code_path.exists():
        stats["missing_llm_code"] += 1
        return None
    llm_code = sanitize_code(llm_code_path.read_text(encoding="utf-8"))
    if not is_valid_python(llm_code):
        stats["invalid_llm_code"] += 1
        return None

    slm_summary, slm_type, slm_code = slm_failure_from_run(run_dir)
    slm_code = sanitize_code(slm_code)

    diff_lines = list(
        difflib.unified_diff(
            slm_code.splitlines(),
            llm_code.splitlines(),
            fromfile="slm",
            tofile="llm",
            lineterm="",
        )
    )
    fix_diff = "\n".join(diff_lines)
    fix_actions = summarize_fix_actions(diff_lines)

    ts = parse_run_ts(run_dir.name)
    ts_str = ts.strftime("%Y%m%d_%H%M%S") if ts else ""

    case_id = f"{task_id}::{run_dir.name}"
    return Case(
        case_id=case_id,
        task_id=task_id,
        dataset=dataset,
        entry_point=entry_point,
        prompt=prompt,
        slm_failure_type=slm_type,
        slm_failure_summary=slm_summary,
        slm_code=slm_code,
        llm_code=llm_code,
        fix_diff=fix_diff,
        fix_actions=fix_actions,
        run_dir=str(run_dir),
        timestamp=ts_str,
    )


def iter_run_dirs(root: Path) -> Iterable[Path]:
    for p in root.iterdir():
        if p.is_dir() and RUN_RE.match(p.name):
            yield p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs_root", default="episodes/humaneval_runs")
    ap.add_argument("--dataset", default="HumanEval")
    ap.add_argument("--out_path", default="data/derived/rag/cases.jsonl")
    ap.add_argument("--dedupe_latest", action="store_true", default=True)
    ap.add_argument("--last_days", type=int, default=0)
    ap.add_argument("--include_cases_path", default="")
    ap.add_argument("--require_slm_failure", action="store_true", default=False)
    args = ap.parse_args()

    runs_root = Path(args.runs_root)
    out_path = Path(args.out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    stats = {
        "missing_task": 0,
        "slm_not_failed": 0,
        "no_fallback_pass": 0,
        "missing_llm_code": 0,
        "invalid_llm_code": 0,
    }

    runs: List[Tuple[Optional[datetime], Path]] = []
    for run_dir in iter_run_dirs(runs_root):
        runs.append((parse_run_ts(run_dir.name), run_dir))

    if args.last_days > 0:
        ts_candidates = [ts for ts, _ in runs if ts]
        if ts_candidates:
            latest_ts = max(ts_candidates)
            cutoff = latest_ts - timedelta(days=args.last_days)
            runs = [(ts, d) for ts, d in runs if ts and ts >= cutoff]
        else:
            runs = []

    cases: List[Dict[str, Any]] = []
    for _, run_dir in runs:
        case = build_case(run_dir, args.dataset, args.require_slm_failure, stats)
        if case:
            cases.append(case.__dict__)

    if args.include_cases_path:
        include_path = Path(args.include_cases_path)
        if include_path.exists():
            with include_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    cases.append(json.loads(line))

    # optional: keep latest per task_id
    if args.dedupe_latest:
        latest: Dict[str, Dict[str, Any]] = {}
        for c in cases:
            task_id = c.get("task_id")
            if not task_id:
                continue
            prev = latest.get(task_id)
            if not prev:
                latest[task_id] = c
                continue
            if (c.get("timestamp") or "") > (prev.get("timestamp") or ""):
                latest[task_id] = c
        cases = list(latest.values())

    with out_path.open("w", encoding="utf-8") as f:
        for c in sorted(cases, key=lambda x: x.get("task_id") or ""):
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"cases_written: {len(cases)}")
    print(f"stats: {stats}")
    print(f"out_path: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
