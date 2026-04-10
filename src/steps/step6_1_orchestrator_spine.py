from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

from src.core.episode_schema import (
    AttemptRecord, RouterDecision, new_episode, now_ms, sha256_text
)
from src.core.router_v1 import RouterConfig, route_v1

from src.core.retriever_local import LocalCodeRetriever

LOG_PATH = Path("episodes/logs/step6_1_runs.jsonl")

LOCAL_FAISS_PATH = Path("data_raw/rag/local_d4j/local.index.faiss")
LOCAL_META_PATH  = Path("data_raw/rag/local_d4j/local.meta.jsonl")

# cache retriever so we don't reload FAISS + MiniLM every run
_RETRIEVER: Optional[LocalCodeRetriever] = None
_RETRIEVER_SRC_ROOT: Optional[str] = None

def load_task_from_jsonl(jsonl_path: str, task_index: int) -> Dict[str, Any]:
    lines = Path(jsonl_path).read_text("utf-8", errors="ignore").splitlines()
    if task_index < 0 or task_index >= len(lines):
        raise IndexError(f"task_index={task_index} out of range (n_lines={len(lines)})")
    return json.loads(lines[task_index])

def ensure_logs_dir():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def append_episode(ep: Dict[str, Any]):
    ensure_logs_dir()
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ep, ensure_ascii=False) + "\n")

def build_query_from_task(task: Dict[str, Any]) -> str:
    parts: List[str] = []
    for k in ["project", "bug_id", "task_id", "title", "description", "failing_test", "error", "stack_trace"]:
        v = task.get(k)
        if isinstance(v, str) and v.strip():
            parts.append(v.strip())
    if not parts:
        parts.append(str(task.get("task_id", "unknown")))
    return " ".join(parts)[:2000]

def find_latest_src_root() -> Optional[str]:
    """
    Find latest episodes/runs/*/workdir/source (most recently modified).
    """
    base = Path("episodes/runs")
    if not base.exists():
        return None
    candidates = list(base.glob("*/workdir/source"))
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return str(candidates[0])

def get_local_rag(task: Dict[str, Any], rag_k: int) -> Tuple[str, int, float]:
    """
    Real Local RAG using Step 6.0 FAISS + meta + MiniLM.
    Returns: (rag_context_text, hits_count, max_score)
    """
    global _RETRIEVER, _RETRIEVER_SRC_ROOT

    if rag_k <= 0:
        return "", 0, 0.0

    if not LOCAL_FAISS_PATH.exists() or not LOCAL_META_PATH.exists():
        return "", 0, 0.0

    src_root = find_latest_src_root()
    if not src_root:
        # No episode workdir found yet => cannot map chunks to files
        return "", 0, 0.0

    # (Re)create retriever if first time OR src_root changed
    if _RETRIEVER is None or _RETRIEVER_SRC_ROOT != src_root:
        _RETRIEVER = LocalCodeRetriever(
            index_path=LOCAL_FAISS_PATH,
            meta_path=LOCAL_META_PATH,
            src_root=Path(src_root),
        )
        _RETRIEVER.load()
        _RETRIEVER_SRC_ROOT = src_root

    query = build_query_from_task(task)

    hits = _RETRIEVER.retrieve(query=query, k=rag_k)  # <-- correct API

    if not hits:
        return "", 0, 0.0

    max_score = max(float(h.score) for h in hits)

    # hit.text already contains: path/lines/code chunk formatted
    rag_context = "\n\n---\n\n".join(h.text.strip() for h in hits if getattr(h, "text", None))
    return rag_context, len(hits), max_score

def stub_generate_patch(mode: str) -> Optional[str]:
    # Step 6.1 still stubbed on purpose:
    if mode == "SLM":
        return None
    if mode == "LLM":
        return "--- a/Foo.java\n+++ b/Foo.java\n@@ -1,1 +1,1 @@\n-// stub\n+// stub\n"
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_jsonl", required=True)
    ap.add_argument("--task_index", type=int, default=0)
    ap.add_argument("--rag_k", type=int, default=10)
    args = ap.parse_args()

    task = load_task_from_jsonl(args.tasks_jsonl, args.task_index)
    task_id = task.get("task_id") or task.get("id") or f"task_{args.task_index}"
    dataset = task.get("dataset") or "defects4j"

    ep = new_episode(dataset=dataset, task_id=task_id, meta={
        "tasks_jsonl": args.tasks_jsonl,
        "task_index": args.task_index,
        "step": "6.1",
        "rag_impl": "local_faiss_step6_0",
    })

    rag_enabled = args.rag_k > 0
    rag_context, local_hits, local_max_score = get_local_rag(task, args.rag_k)
    rag_sha = sha256_text(rag_context) if rag_enabled and rag_context else None

    cfg = RouterConfig()

    # Attempt 0
    signals0: Dict[str, Any] = {
        "slm_available": True,
        "prior_slm_failures": 0,
        "failure_type": "",
        "rag_enabled": rag_enabled,
        "local_rag_hits": local_hits,
        "local_rag_max_score": local_max_score,
    }
    mode0, reason0 = route_v1(signals0, cfg)
    decision0 = RouterDecision(selected=mode0, reason=reason0, signals=signals0)

    a0 = AttemptRecord(
        attempt_id=f"a0_{ep.episode_id}",
        mode=mode0,
        started_ms=now_ms(),
        router=decision0,
        rag_enabled=rag_enabled,
        rag_k=max(args.rag_k, 0),
        rag_context_sha256=rag_sha,
    )

    patch0 = stub_generate_patch(mode0)
    a0.patch_diff = patch0
    a0.patch_sha256 = sha256_text(patch0) if patch0 else None

    if patch0 is None:
        a0.test_ok = False
        a0.error_signature = "no_patch"
    a0.status = "completed"
    a0.ended_ms = now_ms()
    ep.attempts.append(a0)

    # Attempt 1 fallback
    if a0.test_ok is False:
        signals1: Dict[str, Any] = {
            "slm_available": True,
            "prior_slm_failures": 1,
            "failure_type": a0.error_signature,
            "rag_enabled": rag_enabled,
            "local_rag_hits": local_hits,
            "local_rag_max_score": local_max_score,
        }
        mode1, reason1 = route_v1(signals1, cfg)
        decision1 = RouterDecision(selected=mode1, reason=reason1, signals=signals1)

        a1 = AttemptRecord(
            attempt_id=f"a1_{ep.episode_id}",
            mode=mode1,
            started_ms=now_ms(),
            router=decision1,
            rag_enabled=rag_enabled,
            rag_k=max(args.rag_k, 0),
            rag_context_sha256=rag_sha,
        )
        patch1 = stub_generate_patch(mode1)
        a1.patch_diff = patch1
        a1.patch_sha256 = sha256_text(patch1) if patch1 else None
        a1.test_ok = None  # tests wired in 6.2
        a1.status = "completed"
        a1.ended_ms = now_ms()
        ep.attempts.append(a1)

    append_episode(ep.to_dict())
    print(f"Wrote episode to {LOG_PATH} (episode_id={ep.episode_id}, attempts={len(ep.attempts)})")
    print(f"Local RAG: enabled={rag_enabled} hits={local_hits} max_score={local_max_score:.4f} sha256={(rag_sha or '')[:12]}")

if __name__ == "__main__":
    main()
