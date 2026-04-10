from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


DatasetName = Literal["Defects4J", "SWE-Bench-Lite", "BigCodeBench", "CodeSearchNet", "Other"]
RunMode = Literal["SLM_ONLY", "LLM_ONLY", "HYBRID"]
RouterDecision = Literal["SLM_ONLY", "ESCALATE_TO_LLM", "LLM_ONLY", "N/A"]
ComplianceLabel = Literal["SAFE", "WARN", "BLOCKED", "N/A"]


def new_episode_id() -> str:
    return str(uuid.uuid4())


class EpisodeRecord(BaseModel):
    # Identity
    episode_id: str = Field(default_factory=new_episode_id)
    run_id: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"))
    timestamp_utc: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    # Task info
    dataset_name: DatasetName
    task_id: str
    language: str  # "Java" | "Python" | etc.
    task_type: str  # "bug_fix" | "repo_issue" | "codegen"

    # Mode
    run_mode: RunMode
    router_decision: RouterDecision = "N/A"
    difficulty_score: Optional[float] = None

    # Inputs (store short text; store long blobs as file paths if huge)
    bug_context: Optional[str] = None
    buggy_code_refs: Optional[List[str]] = None  # file paths / identifiers
    test_command: Optional[str] = None

    # Prompts & outputs
    slm_prompt: Optional[str] = None
    slm_output: Optional[str] = None
    slm_success: Optional[bool] = None
    slm_tokens_in: Optional[int] = None
    slm_tokens_out: Optional[int] = None
    slm_latency_ms: Optional[int] = None

    llm_prompt: Optional[str] = None
    llm_output: Optional[str] = None
    llm_success: Optional[bool] = None
    llm_tokens_in: Optional[int] = None
    llm_tokens_out: Optional[int] = None
    llm_latency_ms: Optional[int] = None

    # Reflection / experience traces
    reflection_text: Optional[str] = None
    stored_as_trace: bool = False  # True if this episode produced an experience trace

    # Tests
    tests_passed: Optional[int] = None
    tests_failed: Optional[int] = None
    test_result_raw: Optional[str] = None  # keep short; long logs -> file path

    # Compliance (ScanCode later)
    compliance_label: ComplianceLabel = "N/A"
    compliance_report_ref: Optional[str] = None  # path or ID

    # Costs / metrics
    latency_total_ms: Optional[int] = None
    cost_estimate: Optional[float] = None  # optional normalized cost unit

    # Freeform metadata
    meta: Dict[str, Any] = Field(default_factory=dict)
