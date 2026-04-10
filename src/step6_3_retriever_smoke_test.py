from __future__ import annotations

from pathlib import Path
from src.core.retriever_csn import CSNRetriever

def main():
    r = CSNRetriever(
        index_path=Path("data_raw/rag/csn/csn.index.faiss"),
        meta_path=Path("data_raw/rag/csn/csn.meta.jsonl"),
        normalize=True,
    )
    r.load()

    q = "null check dataset return result legend items CategoryDataset"
    hits = r.retrieve(q, k=5)

    print("Query:", q)
    for i, h in enumerate(hits, 1):
        print("\n" + "="*80)
        print(f"#{i} score={h.score:.4f} source_id={h.source_id}")
        print("meta:", h.meta)
        print("text preview:", h.text[:500].replace("\n", " ") + ("..." if len(h.text) > 500 else ""))

if __name__ == "__main__":
    main()
