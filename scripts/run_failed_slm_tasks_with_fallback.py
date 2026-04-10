#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


def load_tasks(path: Path) -> List[Dict[str, str]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def latest_run_dir(out_dir: Path, task_id: str) -> Optional[Path]:
    if not task_id.startswith("HumanEval/"):
        return None
    tid = task_id.split("/", 1)[1]
    pattern = f"*HumanEval_{tid}"
    matches = [p for p in out_dir.glob(pattern) if p.is_dir()]
    if not matches:
        return None
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0]


def read_result(path: Path) -> Optional[Dict[str, str]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def summarize_attempts(run_dir: Path, slm_attempts: int, fallback_attempts: int) -> Dict[str, List[str]]:
    summary = {"slm": [], "fallback": [], "fallback_errors": []}
    for k in range(1, slm_attempts + 1):
        res = read_result(run_dir / f"slm_attempt_{k:02d}" / "result.json")
        if res:
            ok = "PASS" if res.get("ok") else "FAIL"
            msg = res.get("failure_summary") or res.get("stderr") or ""
            summary["slm"].append(f"SLM attempt_{k:02d}: {ok} ({msg})")
        else:
            summary["slm"].append(f"SLM attempt_{k:02d}: NO_RESULT")

    for k in range(1, fallback_attempts + 1):
        fb_dir = run_dir / f"fallback_attempt_{k:02d}"
        res = read_result(fb_dir / "result.json")
        if res:
            ok = "PASS" if res.get("ok") else "FAIL"
            msg = res.get("failure_summary") or res.get("stderr") or ""
            summary["fallback"].append(f"LLM fallback_{k:02d}: {ok} ({msg})")
        else:
            err = fb_dir / "error.txt"
            if err.exists():
                msg = err.read_text(encoding="utf-8").strip()
                summary["fallback"].append(f"LLM fallback_{k:02d}: ERROR ({msg})")
                summary["fallback_errors"].append(msg)
            else:
                summary["fallback"].append(f"LLM fallback_{k:02d}: NO_RESULT")
    return summary


def is_auth_or_network_error(msg: str) -> bool:
    if not msg:
        return False
    needles = [
        "HTTPError",
        "Unauthorized",
        "authentication",
        "API key",
        "invalid_request_error",
        "model_not_found",
        "Connection",
        "Network",
        "timed out",
        "timeout",
        "ServiceUnavailable",
        "Rate limit",
    ]
    return any(n.lower() in msg.lower() for n in needles)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_path", default="reports/failed_slm_tasks.jsonl")
    ap.add_argument("--start_index", type=int, default=0)
    ap.add_argument("--max_tasks", type=int, default=-1)
    ap.add_argument("--out_dir", default="episodes/humaneval_runs")
    ap.add_argument("--slm_attempts", type=int, default=2)
    ap.add_argument("--fallback_attempts", type=int, default=2)
    ap.add_argument("--fallback_model", default="gpt-4o")
    ap.add_argument("--fallback_temp", type=float, default=0.0)
    ap.add_argument("--fallback_max_tokens", type=int, default=512)
    ap.add_argument("--fallback_timeout_s", type=int, default=120)
    ap.add_argument("--rag_enabled", type=int, default=1)
    ap.add_argument("--rag_top_k", type=int, default=3)
    ap.add_argument("--self_debug_enabled", type=int, default=1)
    args = ap.parse_args()

    tasks = load_tasks(Path(args.tasks_path))
    tasks = tasks[args.start_index:] if args.start_index > 0 else tasks
    if args.max_tasks > 0:
        tasks = tasks[: args.max_tasks]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, task in enumerate(tasks, start=1):
        task_id = task.get("task_id", "unknown")
        entry_point = task.get("entry_point", "")
        print(f"\n=== Task {i}/{len(tasks)}: {task_id} ({entry_point}) ===", flush=True)

        cmd = [
            sys.executable,
            "src/humaneval/run_humaneval_hybrid_v2.py",
            "--tasks_path", str(Path(args.tasks_path)),
            "--task_id", task_id,
            "--slm_attempts", str(args.slm_attempts),
            "--fallback_attempts", str(args.fallback_attempts),
            "--fallback_model", args.fallback_model,
            "--fallback_temp", str(args.fallback_temp),
            "--fallback_max_tokens", str(args.fallback_max_tokens),
            "--fallback_timeout_s", str(args.fallback_timeout_s),
            "--rag_enabled", str(args.rag_enabled),
            "--rag_top_k", str(args.rag_top_k),
            "--self_debug_enabled", str(args.self_debug_enabled),
            "--out_dir", str(out_dir),
        ]

        subprocess.run(cmd, check=False)

        run_dir = latest_run_dir(out_dir, task_id)
        if not run_dir:
            print("No run_dir found for task.", flush=True)
            continue

        summary = summarize_attempts(run_dir, args.slm_attempts, args.fallback_attempts)
        for line in summary["slm"]:
            print(line, flush=True)
        for line in summary["fallback"]:
            print(line, flush=True)

        # Stop if auth/network error encountered
        for msg in summary["fallback_errors"]:
            if is_auth_or_network_error(msg):
                print("\nStopping due to auth/network error in fallback:", flush=True)
                print(msg, flush=True)
                return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
