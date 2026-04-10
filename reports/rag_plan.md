# RAG-First Plan (FAISS-based)

## Goal
Build a RAG case-memory first, index it with the existing FAISS stack, then add retrieval to the `_v2` runners and evaluate on a balanced failure set.

---

## Step 1 — Build RAG Memory Dataset (cases.jsonl)
Source data:
- Existing HumanEval runs (failed + passed)
- LLM fallback runs (when available)

Case schema (per row):
- case_id
- task_id
- dataset (HumanEval / BigCodeBench)
- entry_point
- prompt (task prompt)
- error_type (NameError / AssertionError / TIMEOUT / SyntaxError / etc.)
- failure_trace_tail
- fix_code (only if fallback passed)
- model (SLM / LLM)
- status (pass/fail)

Output:
- data/derived/rag/cases.jsonl

---

## Step 2 — Build FAISS Index (reuse existing infra)
Use existing FAISS utilities:
- src/core/retriever_local.py
- src/step6_4_build_local_faiss.py (as template)

Index artifacts:
- data/derived/rag/cases.index.faiss
- data/derived/rag/cases.meta.jsonl

Embedding input (per case):
- prompt + error_type + failure_trace

---

## Step 3 — Retrieval + Prompt Injection (new _v2 runners)
Create _v2 runners:
- src/humaneval/run_humaneval_hybrid_v2.py
- src/bigcodebench/run_bigcodebench_hybrid_v2.py

New CLI args:
- --rag_enabled (0/1)
- --rag_top_k (int)

Flow:
- On failure, query FAISS with (prompt + error_type + failure_trace)
- Retrieve top-k cases
- Inject short hints into next attempt prompt

---

## Step 4 — Select Tasks for RAG Validation
Balanced sample from failed tasks:
- 10 x SLM_TIMEOUT
- 10 x AssertionError
- 6 x NameError
- 2 x TypeError
- 1 x UnboundLocalError
- 1 x ValueError
- 1 x IndentationError

RAG memory build includes:
- All failed tasks (broad coverage)
- All LLM fallback fixes (as they accumulate)

---

## Step 5 — Evaluate RAG Impact
Run the selected set:
- With RAG enabled
- Without RAG

Outputs:
- data/derived/rag/eval_results.jsonl
- data/derived/rag/eval_summary.json

---

## Notes
- Use existing FAISS stack (no new vector DB).
- All new changes will go into *_v2 files only.
