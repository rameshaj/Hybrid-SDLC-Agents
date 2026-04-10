python src/step6_orchestrator_run_v4_slm.py \
  --tasks_path data/defects4j_tasks.jsonl \
  --task_index 0 \
  --tests_mode failing_only \
  --rag_k 1 \
  --rag_query "AbstractCategoryItemRenderer getLegendItems getLegendItem LegendItemCollection CategoryPlot test2947660" \
  --llama_cli_path "/usr/local/bin/llama-cli" \
  --gguf_model_path "models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf" \
  --slm_timeout_s 900 \
  --max_new_tokens 220









from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from src.step6_2_patchgen_slm import generate_patch_with_slm
from src.step6_2_diff_sanitize import sanitize_unified_diff
from src.step6_2_git_apply import git_apply
from src.step6_2_test_runner import run_cmd
soOOOx
# Always run from repo root (prevents path issues if you run from workdir)
REPO_ROOT = Path(__file__).resolve().parents[1]  # src/.. = repo root
os.chdir(REPO_ROOT)

# reduce noisy TF logs if TF leaks in
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

python src/step6_orchestrator_run_v4_slm.py \
  --tasks_path data/defects4j_tasks.jsonl \
  --task_index 0 \
  --tests_mode failing_only \
  --rag_k 1 \
  --rag_query "AbstractCategoryItemRenderer getLegendItems getLegendItem LegendItemCollection CategoryPlot test2947660" \
  --llama_cli_path "/usr/local/bin/llama-cli" \
  --gguf_model_path "models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf" \
  --slm_timeout_s 900 \
  --max_new_tokens 220


from src.agents.tester_defects4j import run_defects4j_task
from src.core.io import load_tasks_from_step5_jsonl
from src.core.logger import append_episode_jsonl, new_episode_id, utc_now_iso
from src.core.schemas import EpisodeRecord, PatchCandidate, RouterDecision

# ✅ Local RAG imports (Step 6.4+)
from src.core.retriever_local import LocalCodeRetriever
from src.core.retrieval_context import build_rag_context

STEP6_LOG = Path("episodes/logs/step6_runs.jsonl")


def _source_root_from_local_stats(out_dir: Path) -> Path | None:
    stats_path = out_dir / "local.stats.json"
    if not stats_path.exists():
        return None
    try:
        stats = json.loads(stats_path.read_text(encoding="utf-8"))
        src_root = Path(stats.get("src_root", ""))
        if src_root.exists():
            return src_root
    except Exception:
        return None
    return None


def _find_newest_existing_source_root() -> Path | None:
    runs = Path("episodes/runs")
    if not runs.exists():
        return None

    # Sort by mtime, newest first; pick the first that has workdir/source
    for ep in sorted(runs.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        src_root = ep / "workdir" / "source"
        if src_zroot.exists():
            return src_root
    return None


def _resolve_source_root(local_out_dir: Path, override: str | None = None) -> Path | None:
    """
    Resolve a valid src_root for LocalCodeRetriever.

    Priority:
    1) CLI override --src_root (if exists)
    2) data_raw/rag/local_d4j/local.stats.json src_root (the path used when building the index)
    3) newest episodes/runs/*/workdir/source that actually exists
    """
    if override:
        p = Path(override)
        if p.exists():
            return p

    p = _source_root_from_local_stats(local_out_dir)
    if p is not None:
        return p

    return _find_newest_existing_source_root()


def _build_local_rag_context(query: str, k: int = 8, src_root_override: str | None = None) -> dict:
    """
    Build local code RAG context from a Defects4J checkout.
    Returns a dict with context + debug info for logging.
    """
    out_dir = Path("data_raw/rag/local_d4j")
    idx = out_dir / "local.index.faiss"
    meta = out_dir / "local.meta.jsonl"

    if not idx.exists() or not meta.exists():
        return {
            "enabled": False,
            "error": f"Local index missing. Build it first: {idx} / {meta}",
            "query": query,
            "k": k,
            "rag_context": "",
            "top_hits": [],
        }

    src_root = _resolve_source_root(out_dir, override=src_root_override)
    if src_root is None:
        return {
            "enabled": False,
            "error": "Could not find any valid src_root. Provide --src_root or ensure episodes/runs/*/workdir/source exists.",
            "query": query,
            "k": k,
            "rag_context": "",
            "top_hits": [],
        }

    r = LocalCodeRetriever(
        index_path=idx,
        meta_path=meta,
        src_root=src_root,
        normalize=True,
    )
    r.load()
    hits = r.retrieve(query, k=k)
    ctx = build_rag_context(hits, max_chars=6000)

    top_hits = []
    for h in hits[: min(3, len(hits))]:
        top_hits.append(
            {
                "score": round(h.score, 4),
                "path": h.meta.get("path"),
                "lines": f"{h.meta.get('start_line')}-{h.meta.get('end_line')}",
            }
        )

    return {
        "enabled": True,
        "query": query,
        "k": k,
        "src_root": str(src_root),
        "rag_context": ctx,
        "rag_chars": len(ctx),
        "top_hits": top_hits,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_jsonl", default="datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl")
    ap.add_argument("--task_index", type=int, default=0)
    ap.add_argument("--mode", choices=["gold_patch", "empty_patch"], default="gold_patch")
    ap.add_argument("--tests_mode", choices=["all", "failing_only"], default="all")

    # ✅ RAG knobs
    ap.add_argument("--rag_k", type=int, default=8)
    ap.add_argument("--rag_query", default="", help="Optional override query for retrieval")
    ap.add_argument("--src_root", default="", help="Optional override source root (must contain *.java paths)")

    args = ap.parse_args()

    tasks = load_tasks_from_step5_jsonl(Path(args.tasks_jsonl))
    assert tasks, f"No tasks loaded from {args.tasks_jsonl}"
    task = tasks[args.task_index]

    episode_id = new_episode_id()

    # ✅ Build a query for local retrieval (defaults to task prompt content)
    default_query = (
        f"{task.dataset} {task.task_id} "
        f"{task.prompt.get('failing_tests','')} "
        f"{task.prompt.get('error_message','')} "
        f"{task.prompt.get('stacktrace','')} "
        f"{task.prompt.get('bug_description','')}"
    ).strip()
    query = (args.rag_query.strip() or default_query)

    # ✅ Local RAG context (logged for verification; will be used by Coder later)
    rag_info = _build_local_rag_context(
        query=query,
        k=args.rag_k,
        src_root_override=(args.src_root.strip() or None),
    )

    # Coder placeholder
    if args.mode == "gold_patch":
        patch = PatchCandidate(patch=task.target_patch, model="GOLD", confidence=1.0)
        router = RouterDecision(action="ACCEPT", reason="Sanity run with gold patch")
    else:
        patch = PatchCandidate(patch="", model="HEURISTIC", confidence=0.0)
        router = RouterDecision(action="GIVE_UP", reason="Empty patch mode")

    failing_tests = None
    if args.tests_mode == "failing_only":
        failing_tests = task.prompt.get("failing_tests") or None

    # Tester
    test = {"ok": False, "note": "not run"}
    try:
        tr = run_defects4j_task(
            episode_id=episode_id,
            task=task,
            patch=patch,
            failing_tests=failing_tests,
        )
        test = {"ok": tr.ok, "raw_log_path": tr.raw_log_path, "summary": tr.summary}
    except Exception as e:
        test = {"ok": False, "error": str(e)}

    rec = EpisodeRecord(
        episode_id=episode_id,
        ts_utc=utc_now_iso(),
        dataset=task.dataset or "Defects4J",
        task_id=task.task_id,
        task_uid=task.id,
        phase="STEP6_ORCHESTRATOR_V2_TESTER_WITH_LOCAL_RAG",
        router=router.__dict__,
        patch=patch.__dict__,
        test=test,
        compliance={"verdict": "SKIPPED", "note": "Compliance not wired yet (Step 6.4+)"},
        metrics={
            "mode": args.mode,
            "tests_mode": args.tests_mode,
            "rag_enabled": rag_info.get("enabled", False),
            "rag_k": args.rag_k,
            "rag_chars": rag_info.get("rag_chars", 0),
            "rag_top_hits": rag_info.get("top_hits", []),
            "rag_src_root": rag_info.get("src_root", ""),
        },
        notes={
            "message": "Tester wired + Local RAG context built (logged). Coder/LLM not wired yet.",
            "rag_query": rag_info.get("query", ""),
            "rag_context": rag_info.get("rag_context", ""),
            "rag_error": rag_info.get("error", ""),
        },
    )

    append_episode_jsonl(STEP6_LOG, rec)

    print("✅ Step 6.2+ run complete (tester + local RAG logged)")
    print("Episode:", episode_id)
    print("Task:", task.id)
    print("Test ok:", test.get("ok"))
    print("RAG enabled:", rag_info.get("enabled"))
    if rag_info.get("enabled"):
        print("RAG src_root:", rag_info.get("src_root"))
        print("RAG chars:", rag_info.get("rag_chars", 0))
        print("RAG top hits:", rag_info.get("top_hits", []))
    else:
        print("RAG error:", rag_info.get("error"))
    print("Run folder:", f"episodes/runs/{episode_id}")


if __name__ == "__main__":
    main()
