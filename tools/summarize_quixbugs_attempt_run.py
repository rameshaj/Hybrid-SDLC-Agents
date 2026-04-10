#!/usr/bin/env python3
import json
from pathlib import Path

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def head(s: str, n=18) -> str:
    lines = s.splitlines()
    return "\n".join(lines[:n])

def tail(s: str, n=12) -> str:
    lines = s.splitlines()
    return "\n".join(lines[-n:])

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    args = ap.parse_args()

    run = Path(args.run_dir)
    print(f"RUN_DIR: {run}")

    if (run / "final_status.txt").exists():
        print("FINAL_STATUS:", read(run / "final_status.txt").strip())

    if (run / "task.json").exists():
        try:
            tj = json.loads(read(run / "task.json"))
            print("TASK:", tj.get("task_id"), "| algo:", tj.get("algo"), "| buggy_path:", tj.get("buggy_path"))
        except Exception:
            pass

    print("-" * 88)

    attempts = sorted([p for p in run.iterdir() if p.is_dir() and p.name.startswith("attempt_")])
    if not attempts:
        print("No attempt_* folders found.")
        return

    for a in attempts:
        status = read(a / "status.txt").strip()
        slm_rc = read(a / "slm_rc.txt").strip()
        slm_dt = read(a / "slm_duration_s.txt").strip()
        rc_pre = read(a / "rc_pre.txt").strip()
        rc_after = read(a / "rc_after.txt").strip()

        print(f"[{a.name}] status={status} slm_rc={slm_rc} slm_s={slm_dt} rc_pre={rc_pre or 'NA'} rc_after={rc_after or 'NA'}")

        # Patch details
        if (a / "patch.diff").exists():
            pd_lines = read(a / "patch.diff").splitlines()
            first = pd_lines[0] if pd_lines else ""
            print("  patch.diff: YES | first_line:", first)
        else:
            print("  patch.diff: NO")

        # Patch apply quick head
        if (a / "patch_apply.txt").exists():
            pa = read(a / "patch_apply.txt")
            if pa.strip():
                print("  patch_apply head:")
                print("    " + head(pa, 10).replace("\n", "\n    "))

        # If test_after exists, show tail (usually failure message)
        if (a / "test_after.txt").exists():
            ta = read(a / "test_after.txt")
            if ta.strip():
                print("  test_after tail:")
                print("    " + tail(ta, 12).replace("\n", "\n    "))

        print("-" * 88)

if __name__ == "__main__":
    main()
