#!/usr/bin/env python3
"""
Build a stdlib-only subset of BigCodeBench from an input JSONL file.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


def stdlib_modules() -> set[str]:
    names = set(getattr(sys, "stdlib_module_names", set()))
    # some common modules may not appear depending on build
    names.update({
        "collections", "itertools", "math", "random", "string", "re", "statistics",
        "heapq", "functools", "operator", "datetime", "time", "os", "sys",
        "pathlib", "json", "csv", "typing", "bisect", "deque", "fractions",
        "decimal", "array", "numbers", "copy", "copyreg", "enum",
    })
    return names


def extract_imports(code_prompt: str) -> set[str]:
    mods: set[str] = set()
    for line in code_prompt.splitlines():
        stripped = line.strip()
        if stripped.startswith("def "):
            break
        if stripped.startswith("import "):
            parts = stripped.replace("import", "", 1).split(",")
            for part in parts:
                mod = part.strip().split(" ")[0]
                if mod:
                    mods.add(mod)
        elif stripped.startswith("from "):
            parts = stripped.split()
            if len(parts) >= 2:
                mods.add(parts[1])
    return mods


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_path", default="data/external/bcb/bigcodebench_subset.jsonl")
    ap.add_argument("--out_path", default="data/external/bcb/bigcodebench_subset_stdlib.jsonl")
    args = ap.parse_args()

    stdlib = stdlib_modules()

    in_path = Path(args.in_path)
    out_path = Path(args.out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    kept = 0
    total = 0
    with in_path.open("r", encoding="utf-8") as f_in, out_path.open("w", encoding="utf-8") as f_out:
        for line in f_in:
            if not line.strip():
                continue
            total += 1
            obj = json.loads(line)
            code_prompt = obj.get("code_prompt", "") or ""
            libs_raw = obj.get("libs") or []
            if isinstance(libs_raw, str):
                try:
                    libs_list = ast.literal_eval(libs_raw)
                except Exception:
                    libs_list = [libs_raw]
            elif isinstance(libs_raw, list):
                libs_list = libs_raw
            else:
                libs_list = list(libs_raw)
            libs = set(libs_list)
            imports = extract_imports(code_prompt)
            needed = libs.union(imports)
            if needed and not needed.issubset(stdlib):
                continue
            f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")
            kept += 1

    print(f"kept {kept} of {total}")
    print(f"output: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
