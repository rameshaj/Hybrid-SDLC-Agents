from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--buggy", required=True)
    ap.add_argument("--fixed", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    buggy = Path(args.buggy).resolve()
    fixed = Path(args.fixed).resolve()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if not buggy.exists():
        raise FileNotFoundError(f"Buggy dir not found: {buggy}")
    if not fixed.exists():
        raise FileNotFoundError(f"Fixed dir not found: {fixed}")

    cmd = ["diff", "-ruN", str(buggy), str(fixed)]

    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    diff_text = p.stdout.decode("utf-8", errors="ignore")

    if diff_text.strip() == "":
        diff_text = "# No differences found (unexpected for Defects4J bug)\n"

    out.write_text(diff_text, encoding="utf-8")

    print(f"Saved diff to: {out}")
    print(f"Diff size: {out.stat().st_size} bytes")

if __name__ == "__main__":
    main()
