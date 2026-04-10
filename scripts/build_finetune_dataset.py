#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def clean_failure_summary(summary: str) -> str:
    if not summary:
        return ""
    # keep only the main error line before any tail
    main = summary.split("| tail:", 1)[0].strip()
    # redact absolute paths
    main = re.sub(r"/Users/[^\\s:]+", "<PATH>", main)
    return main


def build_input(
    prompt: str,
    failure_summary: str,
    slm_code: str,
    entry_point: str = "",
    error_type: str = "",
) -> str:
    lines = [
        "You are a coding assistant. Fix the function to pass tests.",
        "",
        "Task:",
        prompt.strip(),
        "",
    ]
    if entry_point:
        lines += ["Entry point:", entry_point.strip(), ""]
    if error_type:
        lines += ["Error type:", error_type.strip(), ""]
    lines += [
        "Failure (summary):",
        failure_summary.strip(),
        "",
        "SLM code:",
        slm_code.strip(),
        "",
        "Return ONLY valid Python code. No explanations, no markdown.",
    ]
    return "\n".join(lines) + "\n"


def split_by_task(
    rows: List[Dict[str, str]],
    seed: int,
    train_ratio: float,
    val_ratio: float,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, str]], Dict[str, int]]:
    by_task = defaultdict(list)
    for r in rows:
        by_task[r["task_id"]].append(r)

    task_ids = list(by_task.keys())
    random.Random(seed).shuffle(task_ids)

    n = len(task_ids)
    n_train = max(1, int(n * train_ratio))
    n_val = max(1, int(n * val_ratio))
    n_test = max(1, n - n_train - n_val)
    if n_train + n_val + n_test > n:
        n_test = max(0, n - n_train - n_val)

    train_ids = set(task_ids[:n_train])
    val_ids = set(task_ids[n_train:n_train + n_val])
    test_ids = set(task_ids[n_train + n_val:])

    train_rows, val_rows, test_rows = [], [], []
    for r in rows:
        if r["task_id"] in train_ids:
            train_rows.append(r)
        elif r["task_id"] in val_ids:
            val_rows.append(r)
        else:
            test_rows.append(r)

    summary = {
        "tasks_total": n,
        "train_tasks": len(train_ids),
        "val_tasks": len(val_ids),
        "test_tasks": len(test_ids),
        "train_rows": len(train_rows),
        "val_rows": len(val_rows),
        "test_rows": len(test_rows),
    }
    return train_rows, val_rows, test_rows, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases_path", default="data/derived/rag/cases.jsonl")
    ap.add_argument("--out_dir", default="data/derived/finetune")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--train_ratio", type=float, default=0.8)
    ap.add_argument("--val_ratio", type=float, default=0.1)
    args = ap.parse_args()

    cases_path = Path(args.cases_path)
    if not cases_path.exists():
        raise SystemExit(f"Missing cases file: {cases_path}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, str]] = []
    with cases_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            c = json.loads(line)
            prompt = (c.get("prompt") or "").strip()
            slm_code = (c.get("slm_code") or "").strip()
            llm_code = (c.get("llm_code") or "").strip()
            if not llm_code or not prompt:
                continue
            failure_summary = clean_failure_summary(c.get("slm_failure_summary") or "")
            rows.append({
                "task_id": c.get("task_id", "unknown"),
                "dataset": c.get("dataset", ""),
                "entry_point": c.get("entry_point", ""),
                "error_type": c.get("slm_failure_type", ""),
                "input": build_input(
                    prompt,
                    failure_summary,
                    slm_code,
                    c.get("entry_point", ""),
                    c.get("slm_failure_type", ""),
                ),
                "output": llm_code,
            })

    train_rows, val_rows, test_rows, split_summary = split_by_task(
        rows, seed=args.seed, train_ratio=args.train_ratio, val_ratio=args.val_ratio
    )

    full_path = out_dir / "humaneval_slm_fix_pairs.cleaned.jsonl"
    train_path = out_dir / "humaneval_slm_fix_pairs.cleaned.train.jsonl"
    val_path = out_dir / "humaneval_slm_fix_pairs.cleaned.val.jsonl"
    test_path = out_dir / "humaneval_slm_fix_pairs.cleaned.test.jsonl"

    for path, data in [
        (full_path, rows),
        (train_path, train_rows),
        (val_path, val_rows),
        (test_path, test_rows),
    ]:
        with path.open("w", encoding="utf-8") as f:
            for r in data:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    summary = {
        "cases_total": len(rows),
        **split_summary,
        "seed": args.seed,
        "train_ratio": args.train_ratio,
        "val_ratio": args.val_ratio,
    }
    (out_dir / "humaneval_slm_fix_pairs.cleaned.summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print("wrote:", full_path)
    print("wrote:", train_path)
    print("wrote:", val_path)
    print("wrote:", test_path)
    print("summary:", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
