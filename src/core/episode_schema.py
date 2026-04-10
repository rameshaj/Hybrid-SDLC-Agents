from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional
import json
import time
import uuid
import hashlib

def now_ms() -> int:
    return int(time.time() * 1000)

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()

@dataclass
class RouterDecision:
    selected: str  # "SLM" or "LLM"
    reason: str
    signals: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AttemptRecord:
    attempt_id: str
    mode: str  # "SLM" or "LLM"
    started_ms: int
    ended_ms: Optional[int] = None

    router: Optional[RouterDecision] = None

    rag_enabled: bool = False
    rag_k: int = 0
    rag_context_sha256: Optional[str] = None

    patch_diff: Optional[str] = None
    patch_sha256: Optional[str] = None

    # Step 6.1: tests are not executed yet (wired in 6.2)
    test_ok: Optional[bool] = None
    error_signature: Optional[str] = None

    status: str = "started"  # started|completed|skipped|error
    error: Optional[str] = None

@dataclass
class EpisodeRecord:
    episode_id: str
    dataset: str
    task_id: str
    created_ms: int
    meta: Dict[str, Any] = field(default_factory=dict)
    attempts: List[AttemptRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

def new_episode(dataset: str, task_id: str, meta: Optional[Dict[str, Any]] = None) -> EpisodeRecord:
    return EpisodeRecord(
        episode_id=new_id("ep"),
        dataset=dataset,
        task_id=task_id,
        created_ms=now_ms(),
        meta=meta or {},
        attempts=[],
    )
