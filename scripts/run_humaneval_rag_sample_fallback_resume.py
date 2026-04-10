#!/usr/bin/env python3
"""Resume the RAG sample fallback run, skipping tasks already run after a cutoff time."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path


TASKS = [
    # SLM_TIMEOUT (10)
    "HumanEval/0", "HumanEval/1", "HumanEval/4", "HumanEval/5", "HumanEval/6",
    "HumanEval/7", "HumanEval/8", "HumanEval/9", "HumanEval/12", "HumanEval/119",
    # AssertionError (10)
    "HumanEval/19", "HumanEval/54", "HumanEval/64", "HumanEval/69", "HumanEval/70",
    "HumanEval/71", "HumanEval/74", "HumanEval/75", "HumanEval/77", "HumanEval/79",
    # NameError (6)
    "HumanEval/14", "HumanEval/17", "HumanEval/20", "HumanEval/21", "HumanEval/22", "HumanEval/25",
    # TypeError (2)
    "HumanEval/33", "HumanEval/37",
    # UnboundLocalError (1)
    "HumanEval/76",
    # ValueError (1)
    "HumanEval/67",
    # IndentationError (1)
    "HumanEval/32",
]

RUN_RE = re.compile(r".*/(\d{8})_(\d{6})_(HumanEval_\d+)$")


def run_ts_epoch(ts: str) -> float:
    return time.mktime(time.strptime(ts, "%Y%m%d_%H%M%S"))


def latest_run_epoch(summary_path: Path) -> dict[str, float]:
    latest: dict[str, float] = {}
    if not summary_path.exists():
        return latest
    for line in summary_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        run_dir = obj.get("run_dir", "")
        m = RUN_RE.match(run_dir)
        if not m:
            continue
        ts = f"{m.group(1)}_{m.group(2)}"
        tid = m.group(3).replace("_", "/")
        epoch = run_ts_epoch(ts)
        if tid not in latest or epoch > latest[tid]:
            latest[tid] = epoch
    return latest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary_path", default="episodes/humaneval_runs/runs_summary.jsonl")
    ap.add_argument("--since_epoch", type=float, required=True)
    args = ap.parse_args()

    latest = latest_run_epoch(Path(args.summary_path))
    todo = [t for t in TASKS if latest.get(t, 0) < args.since_epoch]

    print(f"Resuming {len(todo)} tasks (cutoff={args.since_epoch})", flush=True)

    for tid in todo:
        print(f"RUN {tid}", flush=True)
        cmd = [
            sys.executable,
            "src/humaneval/run_humaneval_hybrid.py",
            "--task_id", tid,
            "--slm_attempts", "2",
            "--fallback_attempts", "2",
            "--fallback_model", "gpt-4o-mini",
            "--gguf_model_path", "models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        ]
        subprocess.run(cmd, check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
