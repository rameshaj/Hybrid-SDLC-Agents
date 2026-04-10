from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

PARQUET = Path("episodes/episodes.parquet")
ART_ROOT = Path("episodes/artifacts/defects4j/batch_10")
OUT_JSONL = Path("datasets/defects4j/batch_10/defects4j_chart_batch10.jsonl")

TASKS = [f"Chart-{i}" for i in range(1, 11)]


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def meta_get(m, k, default=None):
    return m.get(k, default) if isinstance(m, dict) else default


def parse_version_from_bug_context(bug_context: Optional[str]) -> Optional[str]:
    # "Defects4J Chart-7-7b" -> "7b"
    if not bug_context:
        return None
    m = re.search(r"-([0-9]+[bf])\b", bug_context)
    return m.group(1) if m else None


def parse_failing_tests_from_report(report_path: Path) -> List[str]:
    """
    Robust extractor for failing tests:
    - Collects tokens like pkg.Class::method
    """
    if not report_path.exists():
        return []

    txt = _read_text(report_path)
    tests = set()

    for line in txt.splitlines():
        line = line.strip()
        if "::" in line and "." in line:
            parts = re.findall(r"[A-Za-z0-9_$.]+::[A-Za-z0-9_$.]+", line)
            for p in parts:
                tests.add(p)

    return sorted(tests)


def normalize_patch_paths(patch_text: str, buggy_root: str, fixed_root: str) -> str:
    """
    Normalize unified diff:
    - Remove absolute filesystem paths
    - Strip timestamps
    - Normalize comment headers

    Output becomes repo-relative and portable.
    """
    buggy_root = (buggy_root or "").rstrip("/")
    fixed_root = (fixed_root or "").rstrip("/")

    out_lines: List[str] = []

    for line in patch_text.splitlines():
        # Normalize comment headers (important for training cleanliness)
        if line.startswith("# buggy: "):
            line = "# buggy: <BUGGY_ROOT>"
        elif line.startswith("# fixed: "):
            line = "# fixed: <FIXED_ROOT>"

        # Normalize diff headers
        elif line.startswith("--- "):
            if buggy_root:
                line = re.sub(rf"^---\s+{re.escape(buggy_root)}/", "--- ", line)
            line = re.sub(r"\t.*$", "", line)

        elif line.startswith("+++ "):
            if fixed_root:
                line = re.sub(rf"^\+\+\+\s+{re.escape(fixed_root)}/", "+++ ", line)
            line = re.sub(r"\t.*$", "", line)

        out_lines.append(line)

    return "\n".join(out_lines) + "\n"


def main():
    assert PARQUET.exists(), f"Missing {PARQUET}"

    df = pd.read_parquet(PARQUET)

    # Keep only batch tasks
    df = df[df["task_id"].astype(str).isin(TASKS)].copy()

    # Keep only batch evaluation phase
    df["phase"] = df["meta"].apply(lambda m: meta_get(m, "phase"))
    df = df[df["phase"] == "BATCH10_EVAL_ONLY"].copy()

    # Determine version
    df["version"] = df["meta"].apply(lambda m: meta_get(m, "version"))
    df["version"] = df["version"].fillna(df["bug_context"].apply(parse_version_from_bug_context))

    # Expect exactly 20 rows: 10 buggy + 10 fixed
    if len(df) != 20:
        print("!! Expected 20 batch rows. Found:", len(df))
        print(df["task_id"].astype(str).value_counts().to_string())
        raise SystemExit(2)

    examples: List[Dict] = []

    for task in TASKS:
        sub = df[df["task_id"].astype(str) == task].copy()
        if len(sub) != 2:
            raise RuntimeError(f"{task}: expected 2 rows, found {len(sub)}")

        row_b = sub[sub["version"].astype(str).str.endswith("b")].iloc[0]
        row_f = sub[sub["version"].astype(str).str.endswith("f")].iloc[0]

        patch_java = ART_ROOT / task / "patch_java_only.diff"
        patch_full = ART_ROOT / task / "patch.diff"

        assert patch_java.exists(), f"Missing {patch_java}"
        assert patch_full.exists(), f"Missing {patch_full}"

        rep_b = Path(str(row_b["compliance_report_ref"]))
        rep_f = Path(str(row_f["compliance_report_ref"]))

        failing_tests = parse_failing_tests_from_report(rep_b)

        raw_patch = _read_text(patch_java)
        buggy_root = meta_get(row_b["meta"], "workdir", "")
        fixed_root = meta_get(row_f["meta"], "workdir", "")
        target_patch = normalize_patch_paths(raw_patch, buggy_root, fixed_root)

        prompt = {
            "instruction": (
                "Fix the bug so that failing tests pass. "
                "Output a unified diff patch for Java source files only."
            ),
            "task_id": task,
            "dataset": "Defects4J",
            "project": "Chart",
            "buggy_version": row_b["version"],
            "fixed_version": row_f["version"],
            "failing_tests": failing_tests,
        }

        meta = {
            "artifact_patch_java_only": str(patch_java),
            "artifact_patch_full": str(patch_full),
            "report_buggy": str(rep_b),
            "report_fixed": str(rep_f),
        }

        examples.append(
            {
                "id": f"defects4j::{task}::{row_b['version']}->{row_f['version']}",
                "prompt": prompt,
                "target": target_patch,
                "meta": meta,
            }
        )

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print("Wrote JSONL:", OUT_JSONL)
    print("Examples:", len(examples))
    print("First id:", examples[0]["id"])
    print("Last  id:", examples[-1]["id"])


if __name__ == "__main__":
    main()
