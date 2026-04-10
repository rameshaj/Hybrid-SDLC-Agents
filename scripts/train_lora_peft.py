#!/usr/bin/env python3
from __future__ import annotations

import argparse
import inspect
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

import torch
from torch.utils.data import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model


@dataclass
class Sample:
    input_text: str
    output_text: str


class JsonlFixDataset(Dataset):
    def __init__(self, path: Path) -> None:
        self.samples: List[Sample] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                self.samples.append(Sample(
                    input_text=obj["input"],
                    output_text=obj["output"],
                ))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Sample:
        return self.samples[idx]


class CausalFixCollator:
    def __init__(self, tokenizer, max_seq_len: int) -> None:
        self.tok = tokenizer
        self.max_seq_len = max_seq_len

    def __call__(self, batch: List[Sample]) -> Dict[str, torch.Tensor]:
        input_ids_list = []
        labels_list = []
        attn_list = []

        for s in batch:
            input_ids = self.tok.encode(s.input_text, add_special_tokens=False)
            output_ids = self.tok.encode(s.output_text, add_special_tokens=False)

            # Ensure space for EOS
            eos_id = self.tok.eos_token_id
            if eos_id is None:
                raise ValueError("Tokenizer missing eos_token_id.")

            max_input = self.max_seq_len - len(output_ids) - 1
            if max_input < 0:
                # Output too long; truncate output
                output_ids = output_ids[: self.max_seq_len - 1]
                max_input = 0

            if len(input_ids) > max_input:
                input_ids = input_ids[-max_input:] if max_input > 0 else []

            full_ids = input_ids + output_ids + [eos_id]
            labels = [-100] * len(input_ids) + output_ids + [eos_id]

            input_ids_list.append(torch.tensor(full_ids, dtype=torch.long))
            labels_list.append(torch.tensor(labels, dtype=torch.long))
            attn_list.append(torch.ones(len(full_ids), dtype=torch.long))

        # Pad to max length in batch
        max_len = max(x.size(0) for x in input_ids_list)
        pad_id = self.tok.pad_token_id if self.tok.pad_token_id is not None else self.tok.eos_token_id

        def pad(seq_list, pad_value):
            out = []
            for seq in seq_list:
                if seq.size(0) < max_len:
                    pad_len = max_len - seq.size(0)
                    pad_tensor = torch.full((pad_len,), pad_value, dtype=seq.dtype)
                    out.append(torch.cat([seq, pad_tensor], dim=0))
                else:
                    out.append(seq)
            return torch.stack(out, dim=0)

        input_ids = pad(input_ids_list, pad_id)
        labels = pad(labels_list, -100)
        attention_mask = pad(attn_list, 0)

        return {
            "input_ids": input_ids,
            "labels": labels,
            "attention_mask": attention_mask,
        }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_name_or_path", required=True)
    ap.add_argument("--train_file", required=True)
    ap.add_argument("--eval_file", required=True)
    ap.add_argument("--output_dir", required=True)
    ap.add_argument("--max_seq_len", type=int, default=2048)
    ap.add_argument("--per_device_train_batch_size", type=int, default=2)
    ap.add_argument("--per_device_eval_batch_size", type=int, default=2)
    ap.add_argument("--gradient_accumulation_steps", type=int, default=8)
    ap.add_argument("--learning_rate", type=float, default=2e-4)
    ap.add_argument("--num_train_epochs", type=int, default=3)
    ap.add_argument("--logging_steps", type=int, default=10)
    ap.add_argument("--save_steps", type=int, default=50)
    ap.add_argument("--save_total_limit", type=int, default=2)
    ap.add_argument("--eval_steps", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--resume_from_checkpoint", default=None)

    ap.add_argument("--lora_r", type=int, default=16)
    ap.add_argument("--lora_alpha", type=int, default=32)
    ap.add_argument("--lora_dropout", type=float, default=0.05)
    ap.add_argument("--target_modules", default="q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj")

    args = ap.parse_args()

    model = AutoModelForCausalLM.from_pretrained(args.model_name_or_path)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    target_modules = [m.strip() for m in args.target_modules.split(",") if m.strip()]
    lora_cfg = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=target_modules,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_cfg)

    train_ds = JsonlFixDataset(Path(args.train_file))
    eval_ds = JsonlFixDataset(Path(args.eval_file))
    collator = CausalFixCollator(tokenizer, max_seq_len=args.max_seq_len)

    steps_per_epoch = math.ceil(len(train_ds) / (args.per_device_train_batch_size * args.gradient_accumulation_steps))
    total_steps = steps_per_epoch * args.num_train_epochs

    ta_kwargs = dict(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        num_train_epochs=args.num_train_epochs,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        eval_steps=args.eval_steps,
        save_strategy="steps",
        save_total_limit=2,
        seed=args.seed,
        report_to=[],
    )
    ta_params = inspect.signature(TrainingArguments.__init__).parameters
    if "eval_strategy" in ta_params:
        ta_kwargs["eval_strategy"] = "steps"
    else:
        ta_kwargs["evaluation_strategy"] = "steps"

    training_args = TrainingArguments(**ta_kwargs)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=collator,
    )

    print(f"train_rows={len(train_ds)} eval_rows={len(eval_ds)} total_steps={total_steps}")
    trainer.train(resume_from_checkpoint=args.resume_from_checkpoint)
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
