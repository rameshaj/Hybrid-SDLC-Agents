from __future__ import annotations

import argparse
import uuid
from pathlib import Path
from datetime import datetime, timezone

from src.runners.defects4j_runner import defects4j_test, save_report
from src.utils.episode_logger import EpisodeLogger
from src.utils.episode_schema import EpisodeRecord


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workdir",
        required=True,
        help="Path to checked-out Defects4J project (e.g., data_raw/defects4j_work/Chart-1b)",
    )
    parser.add_argument("--dataset", default="Defects4J", help="Dataset name")
    parser.add_argument("--task_id", default="Chart-1", help="Task ID label (e.g., Chart-1)")
    parser.add_argument("--language", default="Java", help="Language")
    parser.add_argument("--version", required=True, help="Version tag: 1b or 1f")
    args = parser.parse_args()

    workdir = Path(args.workdir).resolve()
    if not workdir.exists():
        raise FileNotFoundError(f"workdir not found: {workdir}")

    # Run tests and capture output
    result = defects4j_test(workdir)

    # Save raw output to reports for reproducibility
    report_path = save_report(
        Path("reports/defects4j"),
        name=f"{args.task_id}-{args.version}-defects4j-test.txt",
        text=result.raw_output,
    )

    # EpisodeRecord requires:
    # - episode_id: str
    # - run_mode: one of SLM_ONLY / LLM_ONLY / HYBRID
    ep = EpisodeRecord(
        episode_id=str(uuid.uuid4()),
        run_id=datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
        timestamp_utc=utc_now_iso(),
        dataset_name=args.dataset,
        task_id=args.task_id,
        language=args.language,
        task_type="bug_fix",

        # We are doing evaluation-only, but schema doesn't allow EVAL_ONLY.
        # So we store SLM_ONLY and mark actual phase in meta.
        run_mode="SLM_ONLY",
        router_decision="N/A",
        difficulty_score=None,

        bug_context=f"Defects4J {args.task_id}-{args.version}",
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

        tests_passed=result.passed,
        tests_failed=result.failed,
        test_result_raw="; ".join(result.failing_tests) if result.failing_tests else "OK",

        compliance_label="N/A",
        compliance_report_ref=str(report_path),

        latency_total_ms=None,
        cost_estimate=None,

        meta={
            "workdir": str(workdir),
            "version": args.version,
            "phase": "EVAL_ONLY",
        },
    )

    # IMPORTANT: match your EpisodeLogger signature
    logger = EpisodeLogger(out_dir="episodes", filename="episodes.parquet")
    episode_id = logger.log(ep)

    print(f"Logged episode_id: {episode_id}")
    print(f"Report saved at: {report_path}")
    print(f"Failing tests ({result.failed}):")
    for t in result.failing_tests:
        print(f"  - {t}")


if __name__ == "__main__":
    main()
