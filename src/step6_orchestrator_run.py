from __future__ import annotations

import argparse
from pathlib import Path

from src.core.io import load_tasks_from_step5_jsonl
from src.core.logger import append_episode_jsonl, new_episode_id, utc_now_iso
from src.core.schemas import EpisodeRecord, PatchCandidate, RouterDecision


STEP6_LOG = Path("episodes/logs/step6_runs.jsonl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_jsonl", default="datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl")
    ap.add_argument("--task_index", type=int, default=0)
    ap.add_argument("--mode", choices=["gold_patch", "empty_patch"], default="gold_patch")
    args = ap.parse_args()

    tasks = load_tasks_from_step5_jsonl(Path(args.tasks_jsonl))
    assert tasks, f"No tasks loaded from {args.tasks_jsonl}"
    assert 0 <= args.task_index < len(tasks), f"task_index out of range: {args.task_index} / {len(tasks)}"

    task = tasks[args.task_index]

    # "Coder" (placeholder for now)
    if args.mode == "gold_patch":
        patch = PatchCandidate(patch=task.target_patch, model="GOLD", confidence=1.0)
        router = RouterDecision(action="ACCEPT", reason="Sanity run with gold patch")
    else:
        patch = PatchCandidate(patch="", model="HEURISTIC", confidence=0.0)
        router = RouterDecision(action="GIVE_UP", reason="Empty patch mode for pipeline wiring")

    rec = EpisodeRecord(
        episode_id=new_episode_id(),
        ts_utc=utc_now_iso(),
        dataset=task.dataset or "Defects4J",
        task_id=task.task_id,
        task_uid=task.id,
        phase="STEP6_ORCHESTRATOR_V1",
        router=router.__dict__,
        patch=patch.__dict__,
        test={"ok": False, "note": "Tester not wired yet (Step 6.2+)"},
        compliance={"verdict": "SKIPPED", "note": "Compliance not wired yet (Step 6.4+)"},
        metrics={"mode": args.mode},
        notes={"message": "Step 6.1 schema + logging sanity run"},
    )

    append_episode_jsonl(STEP6_LOG, rec)

    print("✅ Step 6.1 sanity run complete")
    print("Task:", task.id)
    print("Logged to:", STEP6_LOG)


if __name__ == "__main__":
    main()
