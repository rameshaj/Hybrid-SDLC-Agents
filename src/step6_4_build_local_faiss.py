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
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def iter_java_files(src_root: Path) -> List[Path]:
    return sorted([p for p in src_root.rglob("*.java") if p.is_file()])


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def file_passes_keywords(text_lc: str, keywords: List[str], mode: str) -> bool:
    if not keywords:
        return True
    if mode == "any":
        return any(k in text_lc for k in keywords)
    return all(k in text_lc for k in keywords)


def chunk_lines(
    text: str,
    max_lines: int = 140,
    overlap: int = 40,
) -> List[Tuple[int, int, str]]:
    """
    Returns list of (start_line_1based, end_line_1based, chunk_text)
    Simple sliding window chunker: robust for Java parsing issues.
    """
    lines = text.splitlines()
    if not lines:
        return []

    chunks = []
    step = max(1, max_lines - overlap)
    n = len(lines)

    i = 0
    while i < n:
        start = i
        end = min(n, i + max_lines)
        chunk = "\n".join(lines[start:end]).strip()
        if chunk:
            chunks.append((start + 1, end, chunk))
        if end == n:
            break
        i += step

    return chunks


def build_embed_text(path: str, start: int, end: int, chunk: str) -> str:
    # compact but informative for retrieval
    return f"path: {path}\nlines: {start}-{end}\ncode:\n{chunk}\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src_root", required=True, help="Path to Defects4J checkout source dir (e.g., .../workdir/source)")
    ap.add_argument("--out_dir", default="data_raw/rag/local_d4j")
    ap.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    ap.add_argument("--normalize", action="store_true", help="cosine via normalized embeddings + IP index")
    ap.add_argument("--batch_size", type=int, default=8)
    ap.add_argument("--max_files", type=int, default=0, help="0 = all java files")
    ap.add_argument("--max_chunks", type=int, default=0, help="0 = all chunks")
    ap.add_argument("--chunk_lines", type=int, default=140)
    ap.add_argument("--chunk_overlap", type=int, default=40)
    ap.add_argument("--keyword", action="append", default=[], help="Repeatable keyword filter at FILE level")
    ap.add_argument("--keyword_mode", choices=["any", "all"], default="any")
    args = ap.parse_args()

    src_root = Path(args.src_root)
    assert src_root.exists(), f"Missing src_root: {src_root}"
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    keywords = [k.strip().lower() for k in (args.keyword or []) if k and k.strip()]

    # limit FAISS threads
    try:
        faiss.omp_set_num_threads(1)
    except Exception:
        pass

    files = iter_java_files(src_root)
    if args.max_files and args.max_files > 0:
        files = files[: args.max_files]

    meta_path = out_dir / "local.meta.jsonl"
    texts: List[str] = []
    metas: List[Dict[str, Any]] = []

    kept_files = 0
    seen_chunks = 0

    for fp in files:
        raw = read_text(fp)
        raw_lc = raw.lower()

        if not file_passes_keywords(raw_lc, keywords, args.keyword_mode):
            continue

        kept_files += 1
        rel_path = str(fp.relative_to(src_root))

        for (s, e, chunk) in chunk_lines(raw, max_lines=args.chunk_lines, overlap=args.chunk_overlap):
            text = build_embed_text(rel_path, s, e, chunk)
            texts.append(text)

            metas.append({
                "id": len(metas),
                "path": rel_path,
                "start_line": s,
                "end_line": e,
                "char_len": len(chunk),
            })

            seen_chunks += 1
            if args.max_chunks and args.max_chunks > 0 and seen_chunks >= args.max_chunks:
                break

        if args.max_chunks and args.max_chunks > 0 and seen_chunks >= args.max_chunks:
            break

    # write meta
    with meta_path.open("w", encoding="utf-8") as f:
        for m in metas:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    assert metas, "No chunks produced. Try removing keywords or check src_root."

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

    idx_path = out_dir / "local.index.faiss"
    faiss.write_index(index, str(idx_path))

    stats = {
        "src_root": str(src_root),
        "n_java_files_total": len(iter_java_files(src_root)),
        "n_java_files_indexed": kept_files,
        "keywords": keywords,
        "keyword_mode": args.keyword_mode,
        "n_chunks": int(index.ntotal),
        "dim": int(index.d),
        "embedding_model": args.model,
        "metric": metric,
        "normalize": bool(args.normalize),
        "batch_size": int(args.batch_size),
        "chunk_lines": int(args.chunk_lines),
        "chunk_overlap": int(args.chunk_overlap),
    }
    (out_dir / "local.stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print("\n✅ Built LOCAL Defects4J FAISS index")
    print("out_dir:", out_dir)
    print("index:", idx_path)
    print("meta :", meta_path)
    print("stats:", out_dir / "local.stats.json")
    print("n_chunks:", index.ntotal, "dim:", index.d)
    print("files_indexed:", kept_files)
    if keywords:
        print("keywords:", keywords, "mode:", args.keyword_mode)


if __name__ == "__main__":
    main()
