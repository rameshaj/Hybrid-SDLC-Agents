# Fine-tune Status (Qwen-1.5B LoRA)

## Dataset
- Cleaned dataset (input/output pairs): `data/derived/finetune/humaneval_slm_fix_pairs.cleaned.jsonl`
- Train split: `data/derived/finetune/humaneval_slm_fix_pairs.cleaned.train.jsonl`
- Val split: `data/derived/finetune/humaneval_slm_fix_pairs.cleaned.val.jsonl`
- Test split: `data/derived/finetune/humaneval_slm_fix_pairs.cleaned.test.jsonl`
- Summary: `data/derived/finetune/humaneval_slm_fix_pairs.cleaned.summary.json`

## Training Script
- PEFT LoRA trainer: `scripts/train_lora_peft.py`

## Package Check (2026-02-14)
Checked availability via `pkgutil` to avoid torch import OMP errors in the sandbox:
- torch: FOUND
- transformers: FOUND
- peft: MISSING

Attempting to import torch/transformers in the sandbox raised:
`OMP: Error #179: Function Can't open SHM2 failed: System error #1: Operation not permitted`

This is a sandbox limitation; on your local machine, imports should work.

## Install (if needed)
```
pip install peft
```

## HF Model Download Status
- Target repo: `Qwen/Qwen2.5-Coder-1.5B-Instruct`
- Target path: `models/hf/qwen2.5-coder-1.5b-instruct`
- Status: download started, weights not complete yet (no `*.safetensors` in target dir)
- Partial file observed in cache:
  `models/hf/qwen2.5-coder-1.5b-instruct/.cache/huggingface/download/*.incomplete`
- Latest attempt: timed out after 30 minutes; weights still missing in target dir.

## Example Train Command
```
python scripts/train_lora_peft.py \
  --model_name_or_path <HF_QWEN_1_5B_CODER_PATH> \
  --train_file data/derived/finetune/humaneval_slm_fix_pairs.cleaned.train.jsonl \
  --eval_file data/derived/finetune/humaneval_slm_fix_pairs.cleaned.val.jsonl \
  --output_dir data/derived/finetune/qwen1.5b_lora_fix \
  --max_seq_len 2048 \
  --per_device_train_batch_size 2 \
  --gradient_accumulation_steps 8 \
  --learning_rate 2e-4 \
  --num_train_epochs 3
```
