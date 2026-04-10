#!/usr/bin/env python3
"""
Run the first 10 failed HumanEval tasks with StarCoder2-3B.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def main() -> int:
    summary = Path("episodes/humaneval_runs/runs_summary.jsonl")
    pat = re.compile(r".*/(\d{8}_\d{6})_(HumanEval_\d+)")
    entries = []
    if not summary.exists():
        print("missing runs_summary.jsonl")
        return 1
    for line in summary.read_text().splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        m = pat.match(obj.get("run_dir", ""))
        if not m:
            continue
        obj["_ts"] = m.group(1)
        obj["_tid"] = m.group(2).replace("_", "/")
        entries.append(obj)

    latest = {}
    for e in entries:
        tid = e["_tid"]
        if tid not in latest or e["_ts"] > latest[tid]["_ts"]:
            latest[tid] = e

    failed = sorted(
        [tid for tid, e in latest.items() if e.get("status") == "FAIL"],
        key=lambda t: int(t.split("/")[-1]),
    )
    first10 = failed[:10]
    print(f"running {first10}", flush=True)

    for tid in first10:
        print(f"RUN {tid}", flush=True)
        cmd = [
            sys.executable,
            "src/humaneval/run_humaneval_hybrid.py",
            "--task_id", tid,
            "--slm_attempts", "2",
            "--fallback_attempts", "0",
            "--gguf_model_path", "models/gguf/starcoder2-3b-q4_k_m.gguf",
        ]
        subprocess.run(cmd, check=False)

    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
