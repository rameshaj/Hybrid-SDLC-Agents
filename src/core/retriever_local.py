from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from src.core.schemas import RetrievalHit


@dataclass
class LocalCodeRetriever:
    index_path: Path
    meta_path: Path
    src_root: Path
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    normalize: bool = True

    _index: Optional[faiss.Index] = None
    _index_dim: Optional[int] = None
    _meta: Optional[List[Dict[str, Any]]] = None
    _model: Optional[SentenceTransformer] = None

    def load(self) -> None:
        assert self.index_path.exists(), f"Missing index: {self.index_path}"
        assert self.meta_path.exists(), f"Missing meta: {self.meta_path}"
        assert self.src_root.exists(), f"Missing src_root: {self.src_root}"

        try:
            faiss.omp_set_num_threads(1)
        except Exception:
            pass

        self._index = faiss.read_index(str(self.index_path))
        self._index_dim = int(self._index.d)

        meta: List[Dict[str, Any]] = []
        with self.meta_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line:
                    meta.append(json.loads(line))
        self._meta = meta

        assert len(self._meta) == self._index.ntotal, (
            f"meta lines {len(self._meta)} != index.ntotal {self._index.ntotal}"
        )

        self._model = SentenceTransformer(self.model_name, device="cpu")

    def retrieve(self, query: str, k: int = 5) -> List[RetrievalHit]:
        assert self._index and self._meta and self._model, "Call .load() first"

        vec = self._model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=bool(self.normalize),
            show_progress_bar=False,
        )

        # Safety checks: FAISS expects float32 and correct embedding dimension
        vec = np.asarray(vec)
        if vec.ndim != 2 or vec.shape[0] != 1:
            raise ValueError(f"Unexpected query embedding shape: {vec.shape}")
        if self._index_dim is None:
            self._index_dim = int(self._index.d)
        if int(vec.shape[1]) != int(self._index_dim):
            raise ValueError(
                f"Embedding dim mismatch: query={int(vec.shape[1])}, index={int(self._index_dim)}. "
                "Build and query must use the same embedding model."
            )
        vec = vec.astype("float32", copy=False)

        D, I = self._index.search(vec, k)

        hits: List[RetrievalHit] = []
        for score, idx in zip(D[0].tolist(), I[0].tolist()):
            if idx < 0:
                continue
            m = self._meta[int(idx)]
            path = m["path"]
            s = m["start_line"]
            e = m["end_line"]
            fp = self.src_root / path
            code = fp.read_text(encoding="utf-8", errors="ignore")

            # slice lines for exact chunk (no need to store chunk text in meta)
            lines = code.splitlines()
            chunk = "\n".join(lines[s - 1 : e]).strip()

            text = f"path: {path}\nlines: {s}-{e}\ncode:\n{chunk}\n"

            hits.append(
                RetrievalHit(
                    text=text,
                    score=float(score),
                    source_id=str(m.get("id", idx)),
                    source_type="local_repo",
                    meta={"path": path, "start_line": s, "end_line": e},
                )
            )
        return hits
