#!/usr/bin/env python3
"""Run a balanced sample of failed HumanEval tasks with LLM fallback enabled."""
from __future__ import annotations

import subprocess
import sys

TASKS = [
    # SLM_TIMEOUT (10)
    "HumanEval/0","HumanEval/1","HumanEval/4","HumanEval/5","HumanEval/6","HumanEval/7","HumanEval/8","HumanEval/9","HumanEval/12","HumanEval/119",
    # AssertionError (10)
    "HumanEval/19","HumanEval/54","HumanEval/64","HumanEval/69","HumanEval/70","HumanEval/71","HumanEval/74","HumanEval/75","HumanEval/77","HumanEval/79",
    # NameError (6)
    "HumanEval/14","HumanEval/17","HumanEval/20","HumanEval/21","HumanEval/22","HumanEval/25",
    # TypeError (2)
    "HumanEval/33","HumanEval/37",
    # UnboundLocalError (1)
    "HumanEval/76",
    # ValueError (1)
    "HumanEval/67",
    # IndentationError (1)
    "HumanEval/32",
]


def main() -> int:
    for tid in TASKS:
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
