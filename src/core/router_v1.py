from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Tuple, Optional

@dataclass(frozen=True)
class RouterConfig:
    max_slm_failures_before_escalate: int = 1
    local_rag_min_hits: int = 1
    local_rag_min_max_score: float = 0.25  # conservative default
    time_budget_ms: Optional[int] = None   # can be set later

def route_v1(signals: Dict[str, Any], cfg: RouterConfig) -> Tuple[str, str]:
    """
    Deterministic router:
    returns (selected_mode, reason)
    Modes: "SLM" or "LLM"
    """
    slm_available = bool(signals.get("slm_available", True))
    prior_slm_failures = int(signals.get("prior_slm_failures", 0))
    failure_type = str(signals.get("failure_type", ""))

    local_hits = int(signals.get("local_rag_hits", 0))
    local_max_score = float(signals.get("local_rag_max_score", 0.0))

    # A) Hard constraints
    if not slm_available:
        return "LLM", "SLM unavailable"

    # B) Escalate early signals
    if prior_slm_failures >= cfg.max_slm_failures_before_escalate:
        return "LLM", f"SLM failed {prior_slm_failures} time(s); escalate"

    if failure_type in {"invalid_diff", "compile_error"}:
        return "LLM", f"High-risk failure_type={failure_type}; escalate"

    # RAG weakness -> escalate (later we can prefer Global RAG before escalating)
    if signals.get("rag_enabled", False):
        if local_hits < cfg.local_rag_min_hits:
            return "LLM", f"Local RAG weak: hits={local_hits} < {cfg.local_rag_min_hits}"
        if local_max_score < cfg.local_rag_min_max_score:
            return "LLM", f"Local RAG weak: max_score={local_max_score:.3f} < {cfg.local_rag_min_max_score:.3f}"

    # C) Default
    return "SLM", "Default: try local SLM first"
