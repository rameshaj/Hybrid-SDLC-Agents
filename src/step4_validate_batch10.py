from __future__ import annotations

import re
from pathlib import Path
import pandas as pd

BATCH_ROOT = Path("episodes/artifacts/defects4j/batch_10")
REPORT_ROOT = Path("reports/defects4j/batch_10")
PARQUET = Path("episodes/episodes.parquet")

def main():
    assert PARQUET.exists(), f"Missing {PARQUET}"
    df = pd.read_parquet(PARQUET)

    print("=== PARQUET ===")
    print("rows:", len(df))
    if "episode_id" in df.columns:
        nuniq = df["episode_id"].nunique(dropna=False)
        print("episode_id unique:", nuniq, "/", len(df))
        if nuniq != len(df):
            dup = df[df["episode_id"].duplicated(keep=False)].sort_values("episode_id")
            print("!! Duplicate episode_id found:")
            print(dup[["episode_id","task_id","timestamp_utc"]].to_string(index=False))
            raise SystemExit(2)

    # Artifact checks
    tasks = [f"Chart-{i}" for i in range(1, 11)]
    missing_art = []
    for t in tasks:
        td = BATCH_ROOT / t
        if not (td / "patch.diff").exists():
            missing_art.append((t, "patch.diff"))
        if not (td / "patch_java_only.diff").exists():
            missing_art.append((t, "patch_java_only.diff"))

    print("\n=== ARTIFACTS (batch_10) ===")
    if missing_art:
        for t,f in missing_art:
            print("MISSING:", t, f)
        raise SystemExit(3)
    print("All patch.diff + patch_java_only.diff present for Chart-1..Chart-10")

    # Report checks (expect 20)
    report_files = list(REPORT_ROOT.glob("Chart-*-*-defects4j-test.txt"))
    print("\n=== REPORTS (batch_10) ===")
    print("report files:", len(report_files))
    if len(report_files) < 20:
        print("!! Expected ~20 report files (10 buggy + 10 fixed). Found:", len(report_files))
        # show which tasks missing
        names = {p.name for p in report_files}
        for i in range(1, 11):
            for v in (f"{i}b", f"{i}f"):
                expected = f"Chart-{i}-{v}-defects4j-test.txt"
                if expected not in names:
                    print("Missing report:", expected)
        raise SystemExit(4)

    # Episode coverage checks for batch tasks (should have at least 2 rows per task, except Chart-1 has extra)
    print("\n=== EPISODE COVERAGE ===")
    for i in range(1, 11):
        task = f"Chart-{i}"
        sub = df[df["task_id"].astype(str) == task]
        print(task, "rows:", len(sub))
        if len(sub) < 2:
            print("!! Missing episodes for", task)
            raise SystemExit(5)

    print("\n✅ VALIDATION PASS: batch_10 dataset looks healthy.")

if __name__ == "__main__":
    main()
