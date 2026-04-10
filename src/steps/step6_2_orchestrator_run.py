from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.core.episode_schema import AttemptRecord, RouterDecision, new_episode, now_ms, sha256_text
from src.core.router_v1 import RouterConfig, route_v1
from src.core.retriever_local import LocalCodeRetriever
from src.core.defects4j_runner import defects4j_checkout, defects4j_test_failing_only
from src.core.patch_utils import is_unified_diff, apply_patch_unified
from src.core.slm_llama_cli import SLMConfig, run_llama_prompt, build_patch_prompt

LOG_PATH = Path("episodes/logs/step6_2_runs.jsonl")
FAISS = Path("data_raw/rag/local_d4j/local.index.faiss").resolve()
META  = Path("data_raw/rag/local_d4j/local.meta.jsonl").resolve()


def load_task(jsonl_path: str, idx: int) -> Dict[str, Any]:
    lines = Path(jsonl_path).read_text("utf-8", errors="ignore").splitlines()
    return json.loads(lines[idx])


def get_task_id(task: Dict[str, Any], task_index: int) -> str:
    for k in ["task_id", "id", "instance_id", "uid"]:
        v = task.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return f"task_{task_index}"


def parse_defects4j_from_task_id(task_id: str) -> Optional[Tuple[str, str]]:
    # Expected: defects4j::Chart-1::1b->1f
    if "defects4j::" not in task_id:
        return None
    core = task_id.split("defects4j::", 1)[1]
    parts = core.split("::")
    if len(parts) < 2:
        return None
    proj_bug = parts[0]
    vers = parts[1]
    if "-" not in proj_bug or "->" not in vers:
        return None
    project = proj_bug.split("-", 1)[0]
    buggy = vers.split("->", 1)[0]
    return project, buggy


def append_episode(ep: Dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ep, ensure_ascii=False) + "\n")


def pick_src_root(workdir: Path) -> Path:
    if (workdir / "source").exists():
        return workdir / "source"
    return workdir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_jsonl", required=True)
    ap.add_argument("--task_index", type=int, default=0)
    ap.add_argument("--rag_k", type=int, default=10)
    args = ap.parse_args()

    task = load_task(args.tasks_jsonl, args.task_index)
    task_id = get_task_id(task, args.task_index)

    parsed = parse_defects4j_from_task_id(task_id)
    if not parsed:
        raise ValueError(f"Could not parse Defects4J project/version from task_id='{task_id}'")
    project, buggy = parsed

    ep = new_episode(
        "defects4j",
        task_id,
        meta={"step": "6.2", "tasks_jsonl": args.tasks_jsonl, "task_index": args.task_index},
    )

    workdir = Path(f"episodes/runs/{ep.episode_id}/workdir").resolve()
    print("=== Step 6.2 ===")
    print("Episode:", ep.episode_id)
    print("Task:", task_id)
    print("Workdir:", workdir)
    print("FAISS:", FAISS)
    print("META :", META)

    print("\n[1/5] Checkout buggy version...")
    defects4j_checkout(workdir, project, buggy, stream=True)

    src_root = pick_src_root(workdir)
    print("\n[2/5] Using src_root:", src_root)
    if not src_root.exists():
        raise RuntimeError(f"src_root missing even after checkout: {src_root}")

    print("\n[3/5] Load retriever (FAISS + MiniLM)...")
    retriever = LocalCodeRetriever(index_path=FAISS, meta_path=META, src_root=src_root)
    retriever.load()

    prompt_obj = task.get("prompt") if isinstance(task.get("prompt"), dict) else {}
    query = task_id
    if isinstance(prompt_obj, dict) and prompt_obj.get("failing_tests"):
        query += " " + " ".join(prompt_obj.get("failing_tests", []))

    print("\n[4/5] Retrieve local RAG...")
    hits = retriever.retrieve(query=query, k=args.rag_k)
    rag_ctx = "\n\n".join(h.text for h in hits)
    rag_sha = sha256_text(rag_ctx) if rag_ctx else None

    cfg = RouterConfig()
    signals = {
        "slm_available": True,
        "prior_slm_failures": 0,
        "failure_type": "",
        "rag_enabled": True,
        "local_rag_hits": len(hits),
        "local_rag_max_score": max((h.score for h in hits), default=0.0),
    }
    mode, reason = route_v1(signals, cfg)
    print("Router:", mode, "|", reason, "| rag_max=", f"{signals['local_rag_max_score']:.4f}")

    a0 = AttemptRecord(
        attempt_id=f"a0_{ep.episode_id}",
        mode=mode,
        started_ms=now_ms(),
        router=RouterDecision(mode, reason, signals),
        rag_enabled=True,
        rag_k=args.rag_k,
        rag_context_sha256=rag_sha,
    )

    print("\n[5/5] Run SLM (llama-cli) and evaluate patch...")
    slm_cfg = SLMConfig()

    failing_info = ""
    if isinstance(prompt_obj, dict):
        failing_info = "\n".join(prompt_obj.get("failing_tests", []) or [])

    prompt = build_patch_prompt(task_id, failing_info, rag_ctx)

    try:

        raw = run_llama_prompt(prompt[:3500], slm_cfg)
    except subprocess.TimeoutExpired:
        a0.test_ok = False
        a0.error_signature = "slm_timeout"
        a0.status = "completed"
        a0.ended_ms = now_ms()
        ep.attempts.append(a0)
        append_episode(ep.to_dict())
        _to = getattr(slm_cfg, "timeout_s", getattr(slm_cfg, "timeout_sec", getattr(slm_cfg, "timeout", "UNKNOWN"))); print(f"\n❌ SLM timed out after {_to}s (attempt logged, episode saved).")
        print("Episode:", ep.episode_id)
        return

    # Try to extract unified diff if model adds junk
    patch = raw
    if "diff --git" in raw:
        patch = raw[raw.find("diff --git"):]
    elif "--- " in raw:
        patch = raw[raw.find("--- "):]

    a0.patch_diff = patch
    a0.patch_sha256 = sha256_text(patch) if patch else None

    ok_diff, why = is_unified_diff(patch)
    if not ok_diff:
        a0.test_ok = False
        a0.error_signature = f"invalid_diff:{why}"
    else:
        ok_apply, msg = apply_patch_unified(workdir, patch)
        if not ok_apply:
            a0.test_ok = False
            a0.error_signature = f"apply_failed:{msg[:160]}"
        else:
            tr = defects4j_test_failing_only(workdir)
            a0.test_ok = tr.ok
            a0.error_signature = tr.error_signature

    a0.status = "completed"
    a0.ended_ms = now_ms()
    ep.attempts.append(a0)

    append_episode(ep.to_dict())

    print("\n✅ Step 6.2 completed")
    print("Episode:", ep.episode_id)
    print("Local RAG:", f"hits={len(hits)} max={signals['local_rag_max_score']:.4f}")
    print("SLM test_ok:", a0.test_ok)
    print("error_signature:", a0.error_signature)


if __name__ == "__main__":
    main()
