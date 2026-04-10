from __future__ import annotations

from typing import List
from src.core.schemas import RetrievalHit

def build_rag_context(hits: List[RetrievalHit], max_chars: int = 6000) -> str:
    """
    Convert retrieval hits into a compact context block for the LLM.
    Keeps highest-ranked hits and truncates strictly to max_chars.
    """
    if not hits:
        return ""

    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(
            f"[HIT {i}] score={h.score:.4f}\n"
            f"meta={h.meta}\n"
            f"{h.text}\n"
        )

    ctx = "\n---\n".join(blocks).strip()

    if len(ctx) > max_chars:
        suffix = "\n...[TRUNCATED]..."
        keep = max(0, max_chars - len(suffix))
        ctx = ctx[:keep] + suffix

    return ctx
