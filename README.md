# Hybrid SDLC Agent — SLM + LLM Fallback for Automated Program Repair and Code Generation

**Masters Thesis Implementation** | Submitted 2026

This repository contains the full implementation, experiment runs, analysis, and results for a thesis on a **hybrid agent architecture** for automated software development tasks. The system combines a local Small Language Model (SLM) with a cloud LLM fallback, augmented by RAG-based case memory and LoRA fine-tuning, evaluated across four established benchmarks.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Datasets](#datasets)
- [Repository Structure](#repository-structure)
- [Source Code](#source-code-src)
- [Scripts](#scripts-scripts)
- [Episode Run Directories](#episode-run-directories-episodes)
- [Reports and Analysis](#reports-and-analysis-reports)
- [Data](#data-data--datasets)
- [LoRA Adapters](#lora-adapters)
- [Configuration](#configuration-configs)
- [Implementation Notes](#implementation-notes-implementation)
- [Hardware Environment](#hardware-environment)

---

## Overview

The thesis proposes and evaluates a **two-agent hybrid pipeline** for program repair and code generation:

1. **Coder Agent** — A local SLM (Qwen2.5-Coder-1.5B-Instruct via llama.cpp) generates candidate patches or code completions. If the SLM exhausts its attempt budget without passing tests, a cloud LLM fallback (OpenAI API) is invoked.
2. **Patch-Fixer Agent** — Validates, sanitizes, and repairs the candidate output before test execution. For patch tasks (QuixBugs, Defects4J), this agent handles diff extraction, context repair, and multi-method application. For code tasks (HumanEval, BigCodeBench), it extracts code, repairs syntax, rejects imports, and enforces format constraints.

The pipeline follows a **Generate → Validate → Iterate** loop with failure history fed back into subsequent prompts (Reflexion-style iterative repair). Additionally, a **RAG case memory** (FAISS-indexed past fix episodes) is available to inject relevant past solutions into prompts.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Task Input                             │
│          (task JSONL: prompt, buggy code, test cmd)          │
└───────────────────────────┬──────────────────────────────────┘
                            │
                ┌───────────▼───────────┐
                │    RAG Retrieval       │  ← FAISS case memory
                │  (optional, top-k)     │    data/derived/rag/
                └───────────┬───────────┘
                            │
          ┌─────────────────▼──────────────────┐
          │           Coder Agent               │
          │  Local SLM (llama.cpp GGUF)         │
          │  → up to N attempts                 │
          │  → failure history in prompt        │
          │  → duplicate diff suppression (v6)  │
          └─────────────────┬──────────────────┘
                            │ candidate patch / code
          ┌─────────────────▼──────────────────┐
          │         Patch-Fixer Agent           │
          │  Diff sanitize + context repair     │
          │  (git apply / patch -p1 / -p0)      │
          │  Code extract + syntax repair       │
          └─────────────────┬──────────────────┘
                            │
          ┌─────────────────▼──────────────────┐
          │           Test Execution            │
          │   PASS → save result, done          │
          │   FAIL → capture failure signal     │
          └─────────────────┬──────────────────┘
                            │ (if SLM budget exhausted)
          ┌─────────────────▼──────────────────┐
          │        LLM Fallback Agent           │
          │  Cloud LLM (OpenAI API)             │
          │  → up to M fallback attempts        │
          └─────────────────┬──────────────────┘
                            │
                  ┌─────────▼─────────┐
                  │   Episode Logger   │
                  │  episodes/<dataset>│
                  └────────────────────┘
```

---

## Datasets

The system was evaluated across four benchmarks:

| Dataset | Type | Tasks | Language | Task Files |
|---|---|---|---|---|
| **QuixBugs** | Program repair (patch) | 41 bugs | Python | `data/quixbugs_tasks_v2.jsonl` |
| **HumanEval** | Code generation | 164 tasks | Python | `data/external/humaneval/humaneval_train.jsonl` |
| **BigCodeBench** | Code generation | 96 tasks (subset) | Python | `data/external/bcb/` |
| **Defects4J** | Program repair (patch) | 10 bugs (Chart project) | Java | `datasets/defects4j/batch_10/` |

### QuixBugs
- Upstream: [github.com/jkoppel/QuixBugs](https://github.com/jkoppel/QuixBugs) (MIT) — added as git submodule at `data/external/QuixBugs`
- 40 programs, each with a single-line defect, 14 defect classes
- Orchestrators: `src/step6_orchestrator_quixbugs_v5_attempts.py` (canonical) and `v6` (enhanced feedback loop)

### HumanEval
- 164 Python function-completion tasks from OpenAI HumanEval benchmark
- Canonical orchestrator: `src/humaneval/run_humaneval_hybrid_v2.py` (RAG + self-debug)
- **Key result**: SLM pass rate 64/164 (attempt-1) + 4/164 (attempt-2); LLM fallback recovered 72 of 93 invocations

### BigCodeBench
- Subset of BigCodeBench (stdlib-focused, 30 tasks; broader subset, 66 tasks; REST-endpoint, 10 tasks)
- Canonical orchestrator: `src/bigcodebench/run_bigcodebench_hybrid.py`

### Defects4J
- Java program repair benchmark; Chart project bugs 1–10 (batch of 10)
- Multi-step pipeline: log extraction → diff generation → patch application → test validation
- Orchestrators: `src/step6_orchestrator_run_v3.py` + `src/step6_2_patchgen_slm.py`

---

## Repository Structure

```
thesis-hybrid-sdlc-agent/
│
├── src/                        # All source code
├── scripts/                    # Experiment and build scripts
├── configs/                    # YAML configuration files
│
├── data/                       # Task manifests and derived artifacts
│   ├── quixbugs_tasks_v2.jsonl
│   ├── defects4j_tasks.jsonl
│   ├── external/               # External dataset files
│   │   ├── QuixBugs/           # Git submodule (jkoppel/QuixBugs)
│   │   ├── humaneval/
│   │   └── bcb/
│   └── derived/                # Generated artifacts
│       ├── finetune/           # LoRA fine-tuning datasets + adapters
│       ├── finetune_5d_plus27/ # Extended fine-tuning split
│       └── rag/                # FAISS index + case memory
│
├── datasets/
│   └── defects4j/batch_10/     # Defects4J prepared task JSONL
│
├── episodes/                   # All experiment run artifacts
│   ├── quixbugs_runs/
│   ├── humaneval_runs/
│   ├── bigcodebench_runs/
│   ├── bigcodebench_runs_fixcheck/
│   ├── bigcodebench_runs_fixcheck_v2/
│   ├── bigcodebench_runs_token_test/
│   ├── artifacts/defects4j/
│   └── logs/
│
├── reports/                    # Analysis, datacards, run summaries
│   ├── analysis/               # Cross-dataset comparisons and charts
│   └── defects4j/
│
├── manual_runs/chart1/         # Hand-traced Defects4J Chart-1 run
├── notebooks/                  # Jupyter notebooks
├── tools/                      # Utility scripts
├── Implementation/             # Thesis document and scope notes
└── configs/slm_local.yaml      # SLM runtime configuration
```

---

## Source Code (`src/`)

### Core Modules (`src/core/`)

| File | Purpose |
|---|---|
| `schemas.py` | Pydantic/dataclass schemas for episodes and attempts |
| `episode_schema.py` | Episode data structure |
| `io.py` | File read/write helpers |
| `logger.py` | Structured episode logger |
| `patch_utils.py` | Diff extraction, sanitization, context repair, multi-method apply |
| `slm_llama_cli.py` | Local SLM invocation via llama.cpp CLI |
| `router_v1.py` | SLM → LLM fallback routing logic |
| `retrieval_context.py` | RAG context wrapper |
| `retriever_csn.py` | CodeSearchNet FAISS retriever |
| `retriever_local.py` | Local FAISS case retriever |
| `retriever_rag_cases_v2.py` | RAG case memory retriever (FAISS, v2) |
| `defects4j_runner.py` | Defects4J test execution wrapper |

### Dataset Orchestrators

| File | Dataset | Notes |
|---|---|---|
| `step6_orchestrator_quixbugs_v5_attempts.py` | QuixBugs | **Canonical** — context-repair + multi-attempt |
| `step6_orchestrator_quixbugs_v6_attempts.py` | QuixBugs | **Canonical** — adds rich failure feedback + duplicate diff suppression |
| `step6_orchestrator_quixbugs_v1–v4_attempts.py` | QuixBugs | Earlier versions, kept for traceability |
| `humaneval/run_humaneval_hybrid_v2.py` | HumanEval | **Canonical** — RAG + self-debug |
| `humaneval/run_humaneval_hybrid.py` | HumanEval | Earlier version |
| `bigcodebench/run_bigcodebench_hybrid.py` | BigCodeBench | **Canonical** |
| `bigcodebench/run_bigcodebench_hybrid_v2.py` | BigCodeBench | RAG + self-debug variant |
| `step6_orchestrator_run_v3.py` | Defects4J | **Canonical** |
| `step6_orchestrator_run.py`, `_v2.py`, `_v4_slm.py` | Defects4J | Earlier versions |

### Pipeline Step Scripts (`src/step*.py`)

The `step1`–`step6` scripts represent the sequential data and execution pipeline:

| Step | Script(s) | Purpose |
|---|---|---|
| Step 1 | `step1_smoke_test.py` | SLM smoke test — verify llama.cpp invocation works |
| Step 2 | `step2_defects4j_log.py` | Defects4J: extract failing test logs |
| Step 3 | `step3_extract_diff.py`, `step3_extract_java_patch.py` | Extract and format diffs from Defects4J |
| Step 4 | `step4_defects4j_batch10.py`, `step4_validate_batch10.py` | Batch run and validate Defects4J patches |
| Step 5 | `step5_build_jsonl_defects4j_batch10.py`, `step5_5_download_csn_*.py` | Build task JSONL; download CodeSearchNet for RAG |
| Step 6 | `step6_orchestrator_*.py`, `step6_2_*.py`, `step6_3_*.py`, `step6_4_*.py` | Full hybrid orchestration, FAISS index building, patch apply/test |

### Other Source Files

| File | Purpose |
|---|---|
| `llm_fallback_openai.py` | OpenAI LLM fallback client |
| `llm_fallback_openai_codegen.py` | OpenAI codegen-specific fallback |
| `agents/tester_defects4j.py` | Defects4J test agent |
| `utils/episode_logger.py` | Episode logging utilities |
| `quixbugs/run_quixbugs_python.py` | QuixBugs Python test runner |

---

## Scripts (`scripts/`)

| Script | Purpose |
|---|---|
| `build_rag_cases_faiss.py` | Build FAISS index from RAG case memory |
| `build_rag_cases_from_fallback.py` | Construct RAG cases from LLM fallback run episodes |
| `build_finetune_dataset.py` | Build teacher-student fine-tuning pairs from HumanEval episodes |
| `build_bigcodebench_stdlib_subset.py` | Extract stdlib-only BigCodeBench tasks |
| `train_lora_peft.py` | LoRA fine-tuning via HuggingFace PEFT |
| `run_lora_infer.py` | Run inference using LoRA-adapted model |
| `run_lora_humaneval_eval.py` | Evaluate LoRA model on HumanEval |
| `run_humaneval_rag_sample_fallback*.py` | HumanEval RAG+fallback run variants (checkpoint/resume) |
| `run_humaneval_remaining.py` | Resume incomplete HumanEval runs |
| `run_humaneval_failed_first10_starcoder.py` | StarCoder baseline on first 10 failed tasks |
| `run_failed_slm_tasks_with_fallback.py` | Re-run SLM-failed tasks with LLM fallback |
| `run_bigcodebench_remaining.py` | Resume incomplete BigCodeBench runs |
| `slm_smoke_report.py` | Generate SLM smoke test report |
| `smoke_slm_1_basic.sh`, `smoke_slm_2_patch.sh` | Shell smoke tests for SLM basic and patch generation |
| `finetune_status.md` | Fine-tuning run log and commands |

---

## Episode Run Directories (`episodes/`)

Each subdirectory stores timestamped run folders for a dataset. Each run folder contains the full artifact trail for one task attempt.

### `episodes/humaneval_runs/`
- **~400+ run directories**, named `<timestamp>_HumanEval_<id>`
- Each run folder contains:
  - `attempt_01/`, `attempt_02/` — SLM attempt artifacts (prompt, raw output, extracted code, test results)
  - `fallback_01/`, `fallback_02/` — LLM fallback artifacts (when invoked)
  - `final_status.txt` — `PASS` / `FAIL` / `FALLBACK_PASS`
  - `slm_raw.txt`, `slm_err.txt` — raw SLM output
  - `test_before.txt`, `test_after.txt` — test output snapshots
- `runs_summary.jsonl` — consolidated run log (one row per run, used for all analysis)
- `run_all.log` — full run log

### `episodes/quixbugs_runs/`
- `attempts/` — per-task attempt directories
- Each task folder: `attempt_01/`, `attempt_02/`, fallback folders, patch artifacts, test snapshots

### `episodes/bigcodebench_runs/`
- Timestamped BigCodeBench run directories
- `bigcodebench_runs_fixcheck/` and `bigcodebench_runs_fixcheck_v2/` — verification reruns
- `bigcodebench_runs_token_test/` — token budget experiments

### `episodes/artifacts/defects4j/`
- Defects4J patch and test artifacts per bug

### `episodes/logs/`
- `step6_runs.jsonl`, `step6_1_runs.jsonl`, `step6_2_runs.jsonl` — structured run event logs

---

## Reports and Analysis (`reports/`)

### Dataset Datacards
| File | Content |
|---|---|
| `humaneval_datacard.md` | HumanEval dataset provenance and project-specific task coverage |
| `quixbugs_datacard.md` | QuixBugs provenance, local file inventory, test driver details |
| `bigcodebench_datacard.md` | BigCodeBench upstream facts, local subset composition |
| `defects4j_datacard.md` | Defects4J upstream facts, batch-10 preparation details |

### Run Files (Per Dataset)
| File | Content |
|---|---|
| `humaneval_runs_file.md`, `humaneval_runs_file_v2.md` | HumanEval run-by-run outcome narrative |
| `quixbug_runs_file.md`, `quixbug_runs_file_v2.md` | QuixBugs run outcomes; v5/v6 evolution rationale |
| `bigcode_runs_file.md` | BigCodeBench run outcomes |
| `reports/analysis/combined_runs_report.md` | Cross-dataset consolidated run summary |

### SLM and Fallback Analysis
| File | Content |
|---|---|
| `humaneval_slmattempts_analysis.md` | SLM attempt-1 vs attempt-2 breakdown for HumanEval (64 pass attempt-1, 4 attempt-2) |
| `humaneval_llmfallback_attempts_analysis.md` | LLM fallback analysis — 72/93 recovery rate |
| `humaneval_llm_fallback_analysis.md` | Fallback failure taxonomy and per-task deep dive |
| `humaneval_fallback_network_cleaned_analysis.md` | Network-error-cleaned fallback analysis |
| `humaneval_slmattempts_analysis.md` | SLM failure taxonomy (SLM_TIMEOUT: 36, AssertionError: 31, NameError: 24) |
| `quixbugs_slmattempts_analysis.md` | QuixBugs SLM attempt analysis |

### Code Implementation Details
| File | Content |
|---|---|
| `hybrid_orchestrators_detailed_pseudocode_with_citations.md` | Full pseudocode for all 4 dataset orchestrators with literature citations |
| `humaneval_code_implementation_details.md` | HumanEval v2 orchestrator implementation walkthrough |
| `quixbugs_code_implementation_details.md` | QuixBugs v5/v6 orchestrator implementation walkthrough |

### RAG and Fine-tuning
| File | Content |
|---|---|
| `rag_plan.md` | RAG case memory design — FAISS schema, retrieval flow, prompt injection |
| `session_summary.md` | Full session state — RAG build, fine-tuning dataset creation, LoRA training |

### Result Files (JSON/CSV)
| File | Content |
|---|---|
| `humaneval_fallback_task_level_all164.json` / `.csv` | Per-task fallback outcomes across all 164 tasks |
| `humaneval_fallback_slm_failed_only_selected.json` / `.csv` | Network-cleaned SLM-failed subset analysis |
| `humaneval_failed_attempts_summary.json` | SLM failure summary per task |
| `rag_humaneval_latest_per_task.json` | Latest RAG-enabled run per task |
| `rag_humaneval_runs_snapshot.json` | RAG experiment snapshot |
| `test_humaneval_passfail.json`, `val_humaneval_passfail.json` | Pass/fail matrices for test and validation splits |
| `failed_slm_tasks.jsonl` | All tasks that failed after all SLM attempts |
| `fallback_ok_tasks.json`, `fallback_fail_tasks.json` | LLM fallback pass/fail task lists |

### `reports/analysis/`
| File | Content |
|---|---|
| `combined_runs_report.md` | Multi-dataset run narrative |
| `humaneval_runs_file_v2.md`, `quixbug_runs_file_v2.md` | Per-dataset extended run files |
| `rag_runs.md` | RAG experiment run notes |
| `lora_approach_runs.png` | LoRA training approach visualization |
| `benchmark_comparison_slm_llm_fail.png` | SLM vs LLM failure comparison chart |
| `llm_recovery_by_failure_category.png` | LLM recovery rate by error type |
| `plot_llm_recovery.py` | Script used to generate recovery chart |

### `reports/defects4j/`
- `Chart-1-1b-defects4j-test.txt`, `Chart-1-1f-defects4j-test.txt` — Defects4J Chart-1 test outputs (before/after patch)
- `batch_10/` — batch patch and test artifacts

---

## Data (`data/` & `datasets/`)

### Task Manifests
| File | Content |
|---|---|
| `data/quixbugs_tasks.jsonl` | QuixBugs task list (v1 format) |
| `data/quixbugs_tasks_v2.jsonl` | QuixBugs task list (v2, 41 tasks, canonical) |
| `data/defects4j_tasks.jsonl` | Defects4J minimal task pointer |
| `datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl` | Defects4J Chart bugs 1–10, full task objects |

### External Dataset Files (`data/external/`)
| Path | Content |
|---|---|
| `QuixBugs/` | Git submodule — full QuixBugs repo (`python_programs/`, `correct_python_programs/`, `json_testcases/`) |
| `humaneval/humaneval_train.jsonl` | HumanEval 164-task prompt file |
| `bcb/bigcodebench_subset.jsonl` | BigCodeBench 66-task broader subset |
| `bcb/bigcodebench_subset_stdlib.jsonl` | BigCodeBench 30-task stdlib-focused subset (canonical) |
| `bcb/bcb_rest_endpoint_tasks.jsonl` | 10-task REST-endpoint focused subset |
| `bcb/bcb_algo_family_candidates.jsonl`, `bcb_keyword_matches.jsonl` | Task selection intermediates |

### Derived Artifacts (`data/derived/`)

#### RAG Case Memory (`data/derived/rag/`)
| File | Content |
|---|---|
| `cases.jsonl` | Base RAG case memory — LLM-pass episodes from HumanEval |
| `cases.5d_plus27.jsonl` | Extended RAG cases (5-day window + 27 additional) |
| `cases.meta.jsonl` | FAISS index metadata (maps index IDs to case records) |
| `cases.stats.json` | Index statistics (size, embedding model, dimensionality) |
| `cases.index.faiss` | FAISS flat index (binary) |

Each RAG case contains: `task_id`, `entry_point`, `prompt`, `error_type`, `failure_trace_tail`, `fix_code`, `model`, `status`.

#### Fine-tuning Datasets (`data/derived/finetune/`)

Teacher-student pairs built from HumanEval episodes where the SLM failed but LLM fallback passed.

| File | Content |
|---|---|
| `humaneval_slm_fix_pairs.jsonl` | Raw teacher-student pairs |
| `humaneval_slm_fix_pairs.cleaned.jsonl` | Cleaned pairs (deduplicated, validated) |
| `humaneval_slm_fix_pairs.cleaned.train.jsonl` | Training split |
| `humaneval_slm_fix_pairs.cleaned.val.jsonl` | Validation split |
| `humaneval_slm_fix_pairs.cleaned.test.jsonl` | Test split |
| `humaneval_slm_fix_pairs.cleaned.summary.json` | Split summary and error type breakdown |

Extended split (`data/derived/finetune_5d_plus27/`): same structure, built from a larger episode window.

---

## LoRA Adapters

Three LoRA adapters are stored in `data/derived/finetune/`. These are PEFT adapters for `Qwen2.5-Coder-1.5B-Instruct`, trained via `scripts/train_lora_peft.py` on HumanEval teacher-student fix pairs.

> **Note:** Large binary files (`optimizer.pt`, `adapter_model.safetensors`, `*.pth`, `*.bin`) are excluded from this repository via `.gitignore`. Only configuration and tokenizer files are committed. To use these adapters, re-run `scripts/train_lora_peft.py` with the committed dataset splits.

| Adapter | Description |
|---|---|
| `qwen1.5b_lora_fix/` | Initial LoRA adapter — trained on base fine-tune split (9 steps) |
| `qwen1.5b_lora_fix_smoketest/` | Smoke-test adapter — 1-step training sanity check |
| `qwen1.5b_lora_fix_v2_72/` | Extended adapter — trained on 72-pair cleaned split (12 steps) |

Each adapter directory contains:
- `adapter_config.json` — LoRA configuration (rank, alpha, target modules)
- `tokenizer.json`, `tokenizer_config.json`, `vocab.json`, `merges.txt` — tokenizer
- `trainer_state.json` — training loss/step history per checkpoint
- `README.md` — HuggingFace model card

---

## Configuration (`configs/`)

### `configs/slm_local.yaml`
Main runtime configuration for the SLM:
- Path to GGUF model file
- llama.cpp CLI invocation parameters (context length, threads, temperature, max tokens)
- Timeout settings for SLM subprocess
- Fallback model selection and API configuration

---

## Implementation Notes (`Implementation/`)

| File | Content |
|---|---|
| `Ajay_Final_Thesis_V1.pdf` | Submitted thesis document |
| `code_scope_confirmation.md` | Confirms canonical script versions used for each dataset (QuixBugs v5/v6, HumanEval v2, BigCodeBench primary) |
| `hardware_environment.md` | Hardware spec (8GB RAM, dual-core, macOS 15.7.3), Python 3.9.6/3.11.7, llama.cpp version 7650 |

---

## Hardware Environment

All experiments were run locally on a resource-constrained machine:

- **RAM**: 8 GB
- **CPU**: Dual-core (x86_64, macOS)
- **OS**: macOS 15.7.3 (Darwin 24.x)
- **SLM Runtime**: llama.cpp v7650, via `llama-completion` / `llama-cli`
- **Model**: Qwen2.5-Coder-1.5B-Instruct (Q4_K_M GGUF, ~1GB)
- **LLM Fallback**: OpenAI API (gpt-4o / gpt-4-turbo class)
- **Python**: 3.11.7 (primary), 3.9.6 (secondary)

The choice of a constrained local setup was intentional — the thesis evaluates the viability of SLM-first hybrid pipelines in low-resource environments.

---

## Key Results Summary

| Dataset | SLM Pass (All Attempts) | LLM Fallback Pass | Final Pass Rate |
|---|---|---|---|
| HumanEval (164 tasks) | 68 (64 attempt-1 + 4 attempt-2) | 72 of 93 invoked | ~85% overall |
| QuixBugs (41 tasks) | See `reports/quixbug_runs_file.md` | See reports | — |
| BigCodeBench (subset) | See `reports/bigcode_runs_file.md` | See reports | — |
| Defects4J (10 Chart bugs) | See `reports/defects4j/` | See reports | — |

Detailed per-task results are in `reports/` and per-run artifacts are in `episodes/`.

---

## Notes on `.gitignore`

The following are excluded from version control:
- `models/` — GGUF and HuggingFace model weights (4.3 GB)
- `data/derived/**/*.safetensors`, `*.pt`, `*.pth`, `*.bin` — LoRA optimizer states and weight tensors
- `.env` — API keys
- `api tokens.rtf`, `scripts/hf_access_token.txt` — credential files
- `_dummy_files_backup/` — local cleanup backup
- `__pycache__/`, `.DS_Store` — system artifacts
