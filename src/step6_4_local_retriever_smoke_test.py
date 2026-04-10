from __future__ import annotations

from pathlib import Path
from src.core.retriever_local import LocalCodeRetriever

def main():
    # update these two if you used a different out_dir
    out_dir = Path("data_raw/rag/local_d4j")
    idx = out_dir / "local.index.faiss"
    meta = out_dir / "local.meta.jsonl"

    # IMPORTANT: src_root must be the same root you indexed (workdir/source)
    # We'll auto-detect the latest episode and point there.
    import os
    runs = Path("episodes/runs")
    latest = sorted(runs.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)[0]
    src_root = latest / "workdir" / "source"

    r = LocalCodeRetriever(
        index_path=idx,
        meta_path=meta,
        src_root=src_root,
        normalize=True,
    )
    r.load()

    q = "org.jfree.chart.renderer.category.AbstractCategoryItemRenderer getLegendItems CategoryDataset CategoryPlot null plot"
    hits = r.retrieve(q, k=8)

    print("LATEST_EP:", latest.name)
    print("Query:", q)
    for i, h in enumerate(hits, 1):
        print("\n" + "="*90)
        print(f"#{i} score={h.score:.4f} id={h.source_id} meta={h.meta}")
        print(h.text[:700])

if __name__ == "__main__":
    main()
