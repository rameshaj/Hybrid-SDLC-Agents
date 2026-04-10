#!/usr/bin/env python3
from __future__ import annotations

# MUST be set before importing transformers/sentence_transformers (stability on macOS)
import os
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["KERAS_BACKEND"] = "torch"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def build_embed_text(case: Dict[str, Any]) -> str:
    prompt = (case.get("prompt") or "").strip()
    failure_type = (case.get("slm_failure_type") or "").strip()
    failure_summary = (case.get("slm_failure_summary") or "").strip()
    task_id = case.get("task_id", "")
    entry_point = case.get("entry_point", "")
    dataset = case.get("dataset", "")

    parts = [
        f"dataset: {dataset}",
        f"task_id: {task_id}",
        f"entry_point: {entry_point}",
        f"error_type: {failure_type}",
        f"error_summary: {failure_summary}",
        "prompt:",
        prompt,
    ]
    return "\n".join([p for p in parts if p is not None]).strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases_path", default="data/derived/rag/cases.jsonl")
    ap.add_argument("--out_dir", default="data/derived/rag")
    ap.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    ap.add_argument("--normalize", action="store_true", default=True)
    ap.add_argument("--batch_size", type=int, default=8)
    ap.add_argument("--max_cases", type=int, default=0, help="0 = all cases")
    args = ap.parse_args()

    cases_path = Path(args.cases_path)
    assert cases_path.exists(), f"Missing cases file: {cases_path}"

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # limit FAISS threads
    try:
        faiss.omp_set_num_threads(1)
    except Exception:
        pass

    cases: List[Dict[str, Any]] = []
    with cases_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cases.append(json.loads(line))
            if args.max_cases and len(cases) >= args.max_cases:
                break

    assert cases, "No cases loaded."

    texts: List[str] = []
    metas: List[Dict[str, Any]] = []
    for idx, case in enumerate(cases):
        texts.append(build_embed_text(case))
        metas.append({
            "id": idx,
            "case_id": case.get("case_id"),
            "task_id": case.get("task_id"),
            "dataset": case.get("dataset"),
            "entry_point": case.get("entry_point"),
            "slm_failure_type": case.get("slm_failure_type"),
            "slm_failure_summary": case.get("slm_failure_summary"),
            "fix_actions": case.get("fix_actions"),
            "llm_code": case.get("llm_code"),
            "fix_diff": case.get("fix_diff"),
            "prompt": case.get("prompt"),
            "run_dir": case.get("run_dir"),
            "timestamp": case.get("timestamp"),
        })

    meta_path = out_dir / "cases.meta.jsonl"
    with meta_path.open("w", encoding="utf-8") as f:
        for m in metas:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    model = SentenceTransformer(args.model, device="cpu")
    emb = model.encode(
        texts,
        batch_size=args.batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=bool(args.normalize),
    ).astype("float32")

    if args.normalize:
        index = faiss.IndexFlatIP(emb.shape[1])
        metric = "cosine (IP on normalized embeddings)"
    else:
        index = faiss.IndexFlatL2(emb.shape[1])
        metric = "l2"

    index.add(emb)

    idx_path = out_dir / "cases.index.faiss"
    faiss.write_index(index, str(idx_path))

    stats = {
        "cases_path": str(cases_path),
        "n_cases": int(index.ntotal),
        "dim": int(index.d),
        "embedding_model": args.model,
        "metric": metric,
        "normalize": bool(args.normalize),
        "batch_size": int(args.batch_size),
    }
    (out_dir / "cases.stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print("\n✅ Built RAG cases FAISS index")
    print("out_dir:", out_dir)
    print("index:", idx_path)
    print("meta :", meta_path)
    print("stats:", out_dir / "cases.stats.json")
    print("n_cases:", index.ntotal, "dim:", index.d)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
