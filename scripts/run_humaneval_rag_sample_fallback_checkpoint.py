#!/usr/bin/env python3
"""Run the RAG sample task list with checkpointing so it can resume safely."""
from __future__ import annotations

import json
import subprocess
import sys
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

CHECKPOINT = Path("episodes/humaneval_runs/rag_sample_checkpoint.json")
LOG = Path("episodes/humaneval_runs/run_rag_sample_fallback_checkpoint.log")


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


def main() -> int:
    start = load_checkpoint()
    log(f"RESUME index={start}")

    for i in range(start, len(TASKS)):
        tid = TASKS[i]
        log(f"RUN {tid}")
        cmd = [
            sys.executable,
            "src/humaneval/run_humaneval_hybrid.py",
            "--task_id", tid,
            "--slm_attempts", "2",
            "--fallback_attempts", "2",
            "--fallback_model", "gpt-4o-mini",
            "--gguf_model_path", "models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        ]
        try:
            subprocess.run(cmd, check=False)
        except Exception as e:
            log(f"ERROR {tid}: {e}")
        save_checkpoint(i + 1)

    log("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
