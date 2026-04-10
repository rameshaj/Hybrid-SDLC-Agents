#!/usr/bin/env python3
"""Run one task at a time from the RAG sample list until done."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

TASKS = [
    "HumanEval/0", "HumanEval/1", "HumanEval/4", "HumanEval/5", "HumanEval/6",
    "HumanEval/7", "HumanEval/8", "HumanEval/9", "HumanEval/12", "HumanEval/119",
    "HumanEval/19", "HumanEval/54", "HumanEval/64", "HumanEval/69", "HumanEval/70",
    "HumanEval/71", "HumanEval/74", "HumanEval/75", "HumanEval/77", "HumanEval/79",
    "HumanEval/14", "HumanEval/17", "HumanEval/20", "HumanEval/21", "HumanEval/22", "HumanEval/25",
    "HumanEval/33", "HumanEval/37", "HumanEval/76", "HumanEval/67", "HumanEval/32",
]

CHECKPOINT = Path("episodes/humaneval_runs/rag_sample_checkpoint.json")
LOG = Path("episodes/humaneval_runs/run_rag_sample_fallback_single_loop.log")


def load_checkpoint() -> int:
    if not CHECKPOINT.exists():
        return 0
    try:
        data = json.loads(CHECKPOINT.read_text())
        return int(data.get("index", 0))
    except Exception:
        return 0


def save_checkpoint(idx: int) -> None:
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps({"index": idx}), encoding="utf-8")


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")
        f.flush()


def run_task(tid: str) -> None:
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


def main() -> int:
    while True:
        idx = load_checkpoint()
        if idx >= len(TASKS):
            log("DONE")
            return 0
        tid = TASKS[idx]
        log(f"RUN {tid}")
        run_task(tid)
        save_checkpoint(idx + 1)
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
