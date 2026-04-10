from src.utils.episode_schema import EpisodeRecord
from src.utils.episode_logger import EpisodeLogger

def main():
    logger = EpisodeLogger()

    # Simulate a tiny run (no real model yet)
    ep = EpisodeRecord(
        dataset_name="Defects4J",
        task_id="Chart-1",
        language="Java",
        task_type="bug_fix",
        run_mode="SLM_ONLY",
        router_decision="N/A",
        bug_context="Failing test: testFoo -> NullPointerException at Line 42",
        test_command="mvn -q test",
        slm_prompt="You are a code repair assistant. Suggest minimal patch.",
        slm_output="Proposed fix: add null check before dereference.",
        slm_success=False,
        tests_passed=0,
        tests_failed=1,
        test_result_raw="1 test failed: NullPointerException",
        latency_total_ms=1234,
        meta={"note": "smoke test record"}
    )

    episode_id = logger.log(ep)
    print("Logged episode_id:", episode_id)

    df = logger.read()
    print("\nEpisodes table (last 5 rows):")
    print(df.tail(5).to_string(index=False))

if __name__ == "__main__":
    main()
