#!/usr/bin/env python3
"""
Run remaining BigCodeBench tasks by skipping those already in runs_summary.jsonl.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_completed(summary_path: Path) -> set[str]:
    completed: set[str] = set()
    if not summary_path.exists():
        return completed
    for line in summary_path.read_text().splitlines():
        try:
            obj = json.loads(line)
        except Exception:
            continue
        run_dir = obj.get("run_dir", "")
        name = Path(run_dir).name
        idx = name.rfind("BigCodeBench_")
        if idx != -1:
            tid = name[idx:].replace("BigCodeBench_", "BigCodeBench/")
            completed.add(tid)
    return completed


def load_tasks(tasks_path: Path) -> list[dict]:
    tasks: list[dict] = []
    with tasks_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            tasks.append(json.loads(line))
    return tasks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_path", default="data/external/bcb/bigcodebench_subset.jsonl")
    ap.add_argument("--summary_path", default="episodes/bigcodebench_runs/runs_summary.jsonl")
    ap.add_argument("--slm_attempts", type=int, default=2)
    ap.add_argument("--fallback_attempts", type=int, default=0)
    args = ap.parse_args()

    repo = Path(".").resolve()
    tasks_path = repo / args.tasks_path
    summary_path = repo / args.summary_path

    completed = load_completed(summary_path)
    tasks = load_tasks(tasks_path)

    print(f"Completed: {len(completed)}", flush=True)
    print(f"Total tasks: {len(tasks)}", flush=True)

    for t in tasks:
        task_id = t.get("task_id")
        if task_id in completed:
            continue
        print(f"RUN {task_id}", flush=True)
        cmd = [
            sys.executable,
            "src/bigcodebench/run_bigcodebench_hybrid.py",
            "--task_id", task_id,
            "--slm_attempts", str(args.slm_attempts),
            "--fallback_attempts", str(args.fallback_attempts),
        ]
        subprocess.run(cmd, check=False)

    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
