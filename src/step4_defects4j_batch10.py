from __future__ import annotations

import argparse
import os
import subprocess
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from src.runners.defects4j_runner import defects4j_checkout, defects4j_test, save_report
from src.utils.episode_logger import EpisodeLogger
from src.utils.episode_schema import EpisodeRecord


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_id_now() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def already_done(task_dir: Path) -> bool:
    return (task_dir / "patch.diff").exists() and (task_dir / "patch_java_only.diff").exists()


def ensure_defects4j_env():
    """
    Make Step 4 self-contained:
    - If DEFECTS4J_HOME isn't set, set it to <repo_root>/tools/defects4j
    - Also prepend framework/bin to PATH so 'defects4j' can be found
    """
    repo_root = Path(__file__).resolve().parents[1]  # src/... -> repo root
    default_home = repo_root / "tools" / "defects4j"

    if "DEFECTS4J_HOME" not in os.environ:
        os.environ["DEFECTS4J_HOME"] = str(default_home)

    d4j_bin = Path(os.environ["DEFECTS4J_HOME"]) / "framework" / "bin"
    os.environ["PATH"] = f"{d4j_bin}:{os.environ.get('PATH','')}"

    d4j_exe = d4j_bin / "defects4j"
    if not d4j_exe.exists():
        raise RuntimeError(
            f"Defects4J not found at expected path: {d4j_exe}\n"
            f"Check that tools/defects4j exists and is correctly installed."
        )


def main():
    ensure_defects4j_env()

    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="Chart", help="Defects4J project id (Chart, Lang, Math, ...)")
    ap.add_argument("--start", type=int, default=1, help="Start bug id (e.g., 1)")
    ap.add_argument("--count", type=int, default=10, help="How many bugs from start (Option B = 10)")
    ap.add_argument("--dataset", default="Defects4J")
    ap.add_argument("--language", default="Java")

    ap.add_argument("--work_root", default="data_raw/defects4j_batch_10")
    ap.add_argument("--artifact_root", default="episodes/artifacts/defects4j/batch_10")
    ap.add_argument("--report_root", default="reports/defects4j/batch_10")

    ap.add_argument("--episodes_dir", default="episodes")
    ap.add_argument("--episodes_file", default="episodes.parquet")
    args = ap.parse_args()

    project = args.project
    start = args.start
    count = args.count

    work_root = Path(args.work_root).resolve()
    artifact_root = Path(args.artifact_root).resolve()
    report_root = Path(args.report_root).resolve()

    ensure_dir(work_root)
    ensure_dir(artifact_root)
    ensure_dir(report_root)

    episodes_dir = Path(args.episodes_dir).resolve()
    ensure_dir(episodes_dir)

    logger = EpisodeLogger(out_dir=episodes_dir, filename=args.episodes_file)

    tasks: List[Tuple[str, str, str]] = []
    for i in range(start, start + count):
        task_id = f"{project}-{i}"
        buggy_v = f"{i}b"
        fixed_v = f"{i}f"
        tasks.append((task_id, buggy_v, fixed_v))

    print(f"Planned tasks: {len(tasks)} -> {tasks[0]} ... {tasks[-1]}")

    for task_id, buggy_v, fixed_v in tasks:
        print("\n" + "=" * 90)
        print(f"Task: {task_id} | buggy={buggy_v} fixed={fixed_v}")

        task_art_dir = artifact_root / task_id
        ensure_dir(task_art_dir)

        if already_done(task_art_dir):
            print(f"SKIP (already has artifacts): {task_art_dir}")
            continue

        buggy_dir = work_root / f"{task_id}-{buggy_v}"
        fixed_dir = work_root / f"{task_id}-{fixed_v}"

        # (1) checkout
        if not buggy_dir.exists():
            print(f"Checkout buggy -> {buggy_dir}")
            defects4j_checkout(project=project, version=buggy_v, workdir=buggy_dir)
        else:
            print(f"Buggy checkout exists -> {buggy_dir}")

        if not fixed_dir.exists():
            print(f"Checkout fixed -> {fixed_dir}")
            defects4j_checkout(project=project, version=fixed_v, workdir=fixed_dir)
        else:
            print(f"Fixed checkout exists -> {fixed_dir}")

        # (2) tests + save raw output
        buggy_res = defects4j_test(buggy_dir)
        fixed_res = defects4j_test(fixed_dir)

        buggy_report = save_report(
            report_root, f"{task_id}-{buggy_v}-defects4j-test.txt", buggy_res.raw_output
        )
        fixed_report = save_report(
            report_root, f"{task_id}-{fixed_v}-defects4j-test.txt", fixed_res.raw_output
        )

        # (3) full diff -> patch.diff
        patch_full = task_art_dir / "patch.diff"
        cmd_full = [
            "python", "-m", "src.step3_extract_diff",
            "--buggy", str(buggy_dir),
            "--fixed", str(fixed_dir),
            "--out", str(patch_full),
        ]
        print("Run:", " ".join(cmd_full))
        p = subprocess.run(cmd_full, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out_full = p.stdout.decode("utf-8", errors="ignore")
        if p.returncode != 0:
            raise RuntimeError(f"[{task_id}] step3_extract_diff failed\n{out_full}")
        print(out_full.strip())

        # (4) java-only diff -> patch_java_only.diff
        patch_java = task_art_dir / "patch_java_only.diff"
        cmd_java = [
            "python", "-m", "src.step3_extract_java_patch",
            "--buggy", str(buggy_dir),
            "--fixed", str(fixed_dir),
            "--out", str(patch_java),
        ]
        print("Run:", " ".join(cmd_java))
        p2 = subprocess.run(cmd_java, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out_java = p2.stdout.decode("utf-8", errors="ignore")
        if p2.returncode != 0:
            raise RuntimeError(f"[{task_id}] step3_extract_java_patch failed\n{out_java}")
        print(out_java.strip())

        # (5) log 2 episodes (buggy + fixed)
        base_meta: Dict = {
            "phase": "BATCH10_EVAL_ONLY",
            "project": project,
            "diff_path": str(patch_full),
            "java_patch_path": str(patch_java),
        }

        buggy_ep = EpisodeRecord(
            episode_id=str(uuid.uuid4()),
            run_id=run_id_now(),
            timestamp_utc=utc_now_iso(),
            dataset_name=args.dataset,
            task_id=task_id,
            language=args.language,
            task_type="bug_fix",
            run_mode="SLM_ONLY",
            router_decision="N/A",
            difficulty_score=None,
            bug_context=f"Defects4J {task_id}-{buggy_v}",
            buggy_code_refs=None,
            test_command="defects4j test",
            slm_prompt=None,
            slm_output=None,
            slm_success=None,
            slm_tokens_in=None,
            slm_tokens_out=None,
            slm_latency_ms=None,
            llm_prompt=None,
            llm_output=None,
            llm_success=None,
            llm_tokens_in=None,
            llm_tokens_out=None,
            llm_latency_ms=None,
            reflection_text=None,
            stored_as_trace=False,
            tests_passed=buggy_res.passed,
            tests_failed=buggy_res.failed,
            test_result_raw="; ".join(buggy_res.failing_tests) if buggy_res.failing_tests else "OK",
            compliance_label="N/A",
            compliance_report_ref=str(buggy_report),
            latency_total_ms=None,
            cost_estimate=None,
            meta={**base_meta, "version": buggy_v, "workdir": str(buggy_dir)},
        )

        fixed_ep = EpisodeRecord(
            episode_id=str(uuid.uuid4()),
            run_id=run_id_now(),
            timestamp_utc=utc_now_iso(),
            dataset_name=args.dataset,
            task_id=task_id,
            language=args.language,
            task_type="bug_fix",
            run_mode="SLM_ONLY",
            router_decision="N/A",
            difficulty_score=None,
            bug_context=f"Defects4J {task_id}-{fixed_v}",
            buggy_code_refs=None,
            test_command="defects4j test",
            slm_prompt=None,
            slm_output=None,
            slm_success=None,
            slm_tokens_in=None,
            slm_tokens_out=None,
            slm_latency_ms=None,
            llm_prompt=None,
            llm_output=None,
            llm_success=None,
            llm_tokens_in=None,
            llm_tokens_out=None,
            llm_latency_ms=None,
            reflection_text=None,
            stored_as_trace=False,
            tests_passed=fixed_res.passed,
            tests_failed=fixed_res.failed,
            test_result_raw="; ".join(fixed_res.failing_tests) if fixed_res.failing_tests else "OK",
            compliance_label="N/A",
            compliance_report_ref=str(fixed_report),
            latency_total_ms=None,
            cost_estimate=None,
            meta={**base_meta, "version": fixed_v, "workdir": str(fixed_dir)},
        )

        id1 = logger.log(buggy_ep)
        id2 = logger.log(fixed_ep)

        print(f"Logged buggy episode_id: {id1}")
        print(f"Logged fixed episode_id: {id2}")
        print(f"Artifacts saved in: {task_art_dir}")

    print("\nDONE: Batch pipeline finished.")


if __name__ == "__main__":
    main()
