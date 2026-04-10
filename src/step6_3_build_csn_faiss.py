from __future__ import annotations

# MUST be set before importing transformers/sentence_transformers
import os
os.environ["TRANSFORMERS_NO_TF"] = "1"          # prevents TF import path
os.environ["KERAS_BACKEND"] = "torch"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""         # ensure CPU only

import argparse
import json
from pathlib import Path
from typing import Dict, Any

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


def build_text_row(r: Dict[str, Any]) -> str:
    parts = []
    parts.append(f"language: {r.get('language','')}")
    parts.append(f"repo: {r.get('repo','')}")
    parts.append(f"path: {r.get('path','')}")
    fn = (r.get("func_name") or "").strip()
    if fn:
        parts.append(f"function: {fn}")
    doc = (r.get("docstring") or "").strip()
    if doc:
        parts.append("docstring:\n" + doc)
    code = (r.get("code") or "").strip()
    parts.append("code:\n" + code)
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", default="data_raw/codesearchnet/csn_java_python_train.parquet")
    ap.add_argument("--out_dir", default="data_raw/rag/csn")
    ap.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    ap.add_argument("--max_rows", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--normalize", action="store_true")
    ap.add_argument("--batch_size", type=int, default=8)  # smaller = safer
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    parquet_path = Path(args.parquet)
    assert parquet_path.exists(), f"Missing parquet: {parquet_path}"

    df = pd.read_parquet(parquet_path)

    # basic cleaning
    df["code"] = df["code"].astype(str)
    df = df[df["code"].str.strip().astype(bool)]

    # ✅ IMPORTANT: Java-only index for Defects4J (prevents Python pandas hits)
    df["language"] = df["language"].astype(str)
    df = df[df["language"].str.lower() == "java"]

    # sample down if requested
    if args.max_rows and args.max_rows > 0 and len(df) > args.max_rows:
        df = df.sample(n=args.max_rows, random_state=args.seed).reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)

    # reduce FAISS thread usage too
    try:
        faiss.omp_set_num_threads(1)
    except Exception:
        pass

    model = SentenceTransformer(args.model, device="cpu")

    meta_path = out_dir / "csn.meta.jsonl"
    texts = []

    # write meta jsonl alongside embeddings index id
    with meta_path.open("w", encoding="utf-8") as f:
        for i, row in df.iterrows():
            r = row.to_dict()
            texts.append(build_text_row(r))
            meta = {
                "id": int(i),
                "language": r.get("language", ""),
                "repo": r.get("repo", ""),
                "path": r.get("path", ""),
                "func_name": r.get("func_name", ""),
                "docstring": r.get("docstring", ""),
                "code": r.get("code", ""),
            }
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")

    # encode
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

    idx_path = out_dir / "csn.index.faiss"
    faiss.write_index(index, str(idx_path))

    stats = {
        "source_parquet": str(parquet_path),
        "n_rows_input": int(len(df)),
        "n_vectors": int(index.ntotal),
        "dim": int(index.d),
        "embedding_model": args.model,
        "metric": metric,
        "normalize": bool(args.normalize),
        "batch_size": int(args.batch_size),
        "language_filter": "java",
    }
    stats_path = out_dir / "csn.stats.json"
    stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print("\n✅ Built CSN FAISS index (JAVA ONLY)")
    print("out_dir:", out_dir)
    print("index:", idx_path)
    print("meta:", meta_path)
    print("stats:", stats_path)
    print("n_vectors:", index.ntotal, "dim:", index.d)
    print("metric:", metric)


if __name__ == "__main__":
    main()