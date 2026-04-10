#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import signal
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel


class TimeoutError(Exception):
    pass


class Timeout:
    def __init__(self, seconds: int) -> None:
        self.seconds = seconds
        self._old = None

    def _handler(self, signum, frame):
        raise TimeoutError(f"timeout after {self.seconds}s")

    def __enter__(self):
        self._old = signal.signal(signal.SIGALRM, self._handler)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc, tb):
        signal.alarm(0)
        if self._old is not None:
            signal.signal(signal.SIGALRM, self._old)


@dataclass
class Task:
    task_id: str
    entry_point: str
    test: str
    prompt: str


def load_prompts(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            out[obj["task_id"]] = obj["input"]
    return out


def load_tasks(tasks_path: Path, task_ids: List[str], prompts: Dict[str, str]) -> List[Task]:
    want = set(task_ids)
    found: List[Task] = []
    with tasks_path.open("r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            tid = obj["task_id"]
            if tid in want:
                if tid not in prompts:
                    raise ValueError(f"missing prompt for {tid} in prompts_jsonl")
                found.append(Task(
                    task_id=tid,
                    entry_point=obj["entry_point"],
                    test=obj["test"],
                    prompt=prompts[tid],
                ))
    missing = want - {t.task_id for t in found}
    if missing:
        raise ValueError(f"tasks not found in {tasks_path}: {sorted(missing)}")
    return found


def generate(model, tokenizer, prompt: str, max_seq_len: int, max_new_tokens: int, device: str) -> str:
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=max_seq_len,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    gen_ids = output_ids[0, inputs["input_ids"].shape[1]:]
    return tokenizer.decode(gen_ids, skip_special_tokens=True)


def run_test(code: str, test_src: str, timeout_s: int) -> str:
    glb = {"__builtins__": __builtins__}
    with Timeout(timeout_s):
        exec(code, glb)
        exec(test_src, glb)
    return "PASS"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_name_or_path", required=True)
    ap.add_argument("--adapter_path", required=True)
    ap.add_argument("--prompts_jsonl", default="data/derived/finetune/humaneval_slm_fix_pairs.cleaned.jsonl")
    ap.add_argument("--tasks_path", default="data/external/humaneval/humaneval_train.jsonl")
    ap.add_argument("--task_ids", default="HumanEval/0,HumanEval/7,HumanEval/14,HumanEval/75")
    ap.add_argument("--max_seq_len", type=int, default=512)
    ap.add_argument("--max_new_tokens", type=int, default=128)
    ap.add_argument("--timeout_s", type=int, default=5)
    ap.add_argument("--device", default=None)
    ap.add_argument("--print_code", action="store_true")
    ap.add_argument("--dump_dir", default=None)
    args = ap.parse_args()

    device = args.device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    dtype = torch.float16 if device.startswith("cuda") else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name_or_path,
        torch_dtype=dtype,
    )
    model = PeftModel.from_pretrained(model, args.adapter_path)
    model.to(device)
    model.eval()

    prompts = load_prompts(Path(args.prompts_jsonl))
    task_ids = [t.strip() for t in args.task_ids.split(",") if t.strip()]
    tasks = load_tasks(Path(args.tasks_path), task_ids, prompts)

    dump_dir = Path(args.dump_dir) if args.dump_dir else None
    if dump_dir:
        dump_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for t in tasks:
        try:
            code = generate(
                model,
                tokenizer,
                t.prompt,
                max_seq_len=args.max_seq_len,
                max_new_tokens=args.max_new_tokens,
                device=device,
            )
            if dump_dir:
                (dump_dir / f"{t.task_id.replace('/', '_')}.py").write_text(code, encoding="utf-8")
            if args.print_code:
                print(f"--- {t.task_id} code ---")
                print(code)
            status = run_test(code, t.test, args.timeout_s)
            results.append((t.task_id, status, ""))
        except Exception as e:
            results.append((t.task_id, "FAIL", f"{type(e).__name__}: {e}"))

    passed = sum(1 for _, s, _ in results if s == "PASS")
    total = len(results)
    print(f"passed {passed}/{total}")
    for tid, status, err in results:
        if status == "PASS":
            print(f"{tid}: PASS")
        else:
            print(f"{tid}: FAIL ({err})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
