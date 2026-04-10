#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel


def load_prompt(args: argparse.Namespace) -> str:
    if args.prompt:
        return args.prompt
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if args.prompt_jsonl:
        path = Path(args.prompt_jsonl)
        with path.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i == args.prompt_index:
                    obj = json.loads(line)
                    return obj["input"]
        raise ValueError(f"prompt_index {args.prompt_index} out of range for {path}")
    return (
        "You are a coding assistant. Fix the function to pass tests.\n\n"
        "Task:\n"
        "def add(a, b):\n"
        "    return a - b\n\n"
        "Entry point:\n"
        "add\n\n"
        "Return ONLY valid Python code. No explanations, no markdown.\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_name_or_path", required=True)
    ap.add_argument("--adapter_path", required=True)
    ap.add_argument("--prompt", default=None)
    ap.add_argument("--prompt_file", default=None)
    ap.add_argument("--prompt_jsonl", default=None)
    ap.add_argument("--prompt_index", type=int, default=0)
    ap.add_argument("--max_new_tokens", type=int, default=256)
    ap.add_argument("--max_seq_len", type=int, default=1024)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--top_p", type=float, default=1.0)
    ap.add_argument("--device", default=None)
    ap.add_argument("--print_new_only", action="store_true")
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

    prompt = load_prompt(args)
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=args.max_seq_len,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    do_sample = args.temperature > 0
    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=do_sample,
            temperature=args.temperature if do_sample else None,
            top_p=args.top_p if do_sample else None,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    if args.print_new_only:
        gen_ids = output_ids[0, inputs["input_ids"].shape[1] :]
        text = tokenizer.decode(gen_ids, skip_special_tokens=True)
    else:
        text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
