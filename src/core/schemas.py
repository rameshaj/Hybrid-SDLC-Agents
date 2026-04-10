from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TaskSpec:
    """
    Canonical representation of one evaluation task.
    For now we load from your Step 5 JSONL (Defects4J batch10).
    """
    id: str
    dataset: str
    task_id: str
    prompt: Dict[str, Any]
    target_patch: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalHit:
    """
    One RAG retrieval hit (code chunk, trace, test, log snippet, etc.).
    In Step 6.3 we will connect this to FAISS/metadata.
    """
    text: str
    score: float
    source_id: str
    source_type: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineContext:
    """
    What every role receives.
    """
    task: TaskSpec
    failing_tests: List[str] = field(default_factory=list)
    retrieved: List[RetrievalHit] = field(default_factory=list)
    notes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PatchCandidate:
    """
    Output of the Coder role (SLM/LLM).
    """
    patch: str
    model: str  # "SLM" | "LLM" | "GOLD" | "HEURISTIC"
    confidence: float = 0.0
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """
    Output of Tester role.
    """
    ok: bool
    raw_log_path: Optional[str] = None
    summary: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceResult:
    """
    Output of Compliance role (ScanCode now; later optional model assist).
    """
    verdict: str  # "SAFE" | "WARN" | "BLOCKED" | "SKIPPED"
    report_path: Optional[str] = None
    issues: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RouterDecision:
    """
    Router output: do we accept SLM patch, retry, or escalate to LLM?
    """
    action: str  # "ACCEPT" | "RETRY_SLM" | "ESCALATE_LLM" | "GIVE_UP"
    reason: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EpisodeRecord:
    """
    What we persist per run attempt.
    This is intentionally JSON-serializable.
    """
    episode_id: str
    ts_utc: str

    dataset: str
    task_id: str
    task_uid: str

    phase: str  # e.g. "STEP6_ORCHESTRATOR_V1"

    # decisions
    router: Dict[str, Any] = field(default_factory=dict)

    # artifacts
    patch: Dict[str, Any] = field(default_factory=dict)
    test: Dict[str, Any] = field(default_factory=dict)
    compliance: Dict[str, Any] = field(default_factory=dict)

    # metrics
    metrics: Dict[str, Any] = field(default_factory=dict)

    # free-form debug notes
    notes: Dict[str, Any] = field(default_factory=dict)
