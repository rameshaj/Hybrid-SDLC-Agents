# Session Summary (Hybrid SDLC Agent)

## High-level progress
- Implemented BigCodeBench runner and RAG-enabled v2 runners.
- Built RAG case memory and FAISS index.
- Generated cleaned fine-tuning dataset (teacher-student) and splits.
- Installed `peft` and `hf_transfer`.
- Download of HF model weights for Qwen2.5-Coder-1.5B-Instruct is **incomplete** (stalled around 2.0 GB of 3.087 GB).

## Key files created/updated
- `src/bigcodebench/run_bigcodebench_hybrid.py` (BigCodeBench runner; fixed extraction/imports).
- `src/bigcodebench/run_bigcodebench_hybrid_v2.py` (RAG + self-debug).
- `src/humaneval/run_humaneval_hybrid_v2.py` (RAG + self-debug).
- `src/core/retriever_rag_cases_v2.py` (FAISS case retriever).
- `scripts/build_rag_cases_from_fallback.py` (existing; used).
- `scripts/build_rag_cases_faiss.py` (build FAISS index).
- `scripts/build_finetune_dataset.py` (cleaned dataset + splits).
- `scripts/train_lora_peft.py` (LoRA training script via PEFT).
- `scripts/finetune_status.md` (status and commands).
- `reports/rag_plan.md` (plan).
- `reports/humaneval_failed_attempts_report.txt`, `reports/humaneval_failed_attempts_summary.json`.

## RAG artifacts
- Cases file: `data/derived/rag/cases.jsonl` (LLM-pass only).
- FAISS index: `data/derived/rag/cases.index.faiss`
- FAISS meta: `data/derived/rag/cases.meta.jsonl`
- FAISS stats: `data/derived/rag/cases.stats.json`

## Fine-tune dataset (teacher-student)
- Cleaned dataset: `data/derived/finetune/humaneval_slm_fix_pairs.cleaned.jsonl`
- Splits:
  - Train: `data/derived/finetune/humaneval_slm_fix_pairs.cleaned.train.jsonl`
  - Val: `data/derived/finetune/humaneval_slm_fix_pairs.cleaned.val.jsonl`
  - Test: `data/derived/finetune/humaneval_slm_fix_pairs.cleaned.test.jsonl`
- Summary: `data/derived/finetune/humaneval_slm_fix_pairs.cleaned.summary.json`
- Train error breakdown (21 rows): NameError=11, AssertionError=7, TypeError=2, ValueError=1

## HumanEval re-runs (31 tasks)
- Completed 31-task rerun with 2 SLM attempts + 2 LLM fallback.
- Some tasks still failed on LLM fallback: HumanEval/32, HumanEval/74, HumanEval/76, HumanEval/119.
- See run logs under `episodes/humaneval_runs/*` and summaries in `reports/`.

## HF model download (important)
- Target repo: `Qwen/Qwen2.5-Coder-1.5B-Instruct`
- Target path: `models/hf/qwen2.5-coder-1.5b-instruct`
- Download attempted many times; partial file present at:
  `models/hf/qwen2.5-coder-1.5b-instruct/.cache/huggingface/download/*.incomplete`
- Current partial size: ~2.0 GB (out of 3.087 GB)
- Current attempt uses:
  `HF_HUB_ENABLE_HF_TRANSFER=1` + `hf_hub_download` (5-min chunks)
- Needs to finish download and then validate with:
  `python - <<'PY' ... safe_open ... PY`

## Deletions performed to free space
- Deleted:
  - `episodes/quixbugs_runs`
  - `data_raw/codesearchnet`
  - `tools/defects4j`
  - `episodes/runs`
  - `data_raw/defects4j_batch_10`
  - `data_raw/defects4j_work`
  - `models/gguf/deepseek-...` (base/instruct)
  - `models/gguf/starcoder2-3b-q4_k_m.gguf`
  - `models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`
  - `models/gguf/qwen2.5-coder-3b-instruct-q4_k_m.gguf`
  - `models/hf/qwen2.5-coder-1.5b-instruct` (was re-created later)

## Token handling
- HF token was provided and saved by user request:
  - `scripts/hf_access_token.txt`
  - Hugging Face cache: `~/.cache/huggingface/token`

## Current free space (last checked)
- `df -h .` reported ~9.7 GiB free before the latest download chunk.

## Next steps when you return
1) Resume HF weight download until `model.safetensors` lands in `models/hf/qwen2.5-coder-1.5b-instruct`.
2) Verify integrity:
   ```
   python - <<'PY'
   from safetensors import safe_open
   from pathlib import Path
   path = Path('models/hf/qwen2.5-coder-1.5b-instruct/model.safetensors')
   with safe_open(str(path), framework='pt') as f:
       print('ok, tensors:', len(list(f.keys())))
   PY
   ```
3) Run LoRA training:
   ```
   python scripts/train_lora_peft.py \
     --model_name_or_path models/hf/qwen2.5-coder-1.5b-instruct \
     --train_file data/derived/finetune/humaneval_slm_fix_pairs.cleaned.train.jsonl \
     --eval_file data/derived/finetune/humaneval_slm_fix_pairs.cleaned.val.jsonl \
     --output_dir data/derived/finetune/qwen1.5b_lora_fix
   ```

