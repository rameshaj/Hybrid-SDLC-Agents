#!/usr/bin/env python3
"""
QuixBugs Python-only test runner.

- Runs buggy python_programs/<algo>.py against json_testcases/<algo>.json
- Compares outputs to correct_python_programs/<algo>.py
- Exits 0 if all testcases match, else 1
- Designed to be called from repo root
"""

import argparse
import copy
import json
import os
import sys
import types
import importlib


def pretty(o):
    if isinstance(o, types.GeneratorType):
        return list(o)
    return o


def py_call(pkg: str, algo: str, args):
    """
    Call QuixBugs function.

    QuixBugs variants:
    1) module.algo is a function        -> call directly
    2) module.algo is a class/namespace -> call module.algo.algo(...)
    """
    module = importlib.import_module(f"{pkg}.{algo}")
    obj = getattr(module, algo)

    if callable(obj):
        fx = obj
    else:
        fx = getattr(obj, algo)

    try:
        return fx(*args)
    except Exception:
        return ("__EXC__", repr(sys.exc_info()[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("algo", help="Program name without .py (e.g., bitcount)")
    ap.add_argument(
        "--quixbugs_dir",
        default="data/external/QuixBugs",
        help="Path to QuixBugs repo directory",
    )
    ap.add_argument(
        "--max_cases",
        type=int,
        default=0,
        help="If >0, run only first N testcases",
    )
    args = ap.parse_args()

    qb = os.path.abspath(args.quixbugs_dir)
    tc_path = os.path.join(qb, "json_testcases", f"{args.algo}.json")

    if not os.path.exists(tc_path):
        print(f"[ERR] Missing testcase file: {tc_path}", file=sys.stderr)
        return 2

    # Ensure imports work
    if qb not in sys.path:
        sys.path.insert(0, qb)

    total = 0
    failed = 0

    with open(tc_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            test_in, _ = json.loads(line)

            # Inputs must be list
            if not isinstance(test_in, list):
                test_in = [test_in]

            good = py_call(
                "correct_python_programs", args.algo, copy.deepcopy(test_in)
            )
            bad = py_call(
                "python_programs", args.algo, copy.deepcopy(test_in)
            )

            good = pretty(good)
            bad = pretty(bad)

            total += 1
            if good != bad:
                failed += 1
                print(
                    f"[FAIL] {args.algo} case#{total} "
                    f"in={test_in} good={good} bad={bad}"
                )

            if args.max_cases and total >= args.max_cases:
                break

    if failed == 0:
        print(f"[PASS] {args.algo} ({total} cases)")
        return 0
    else:
        print(f"[FAIL] {args.algo} failed {failed}/{total} cases")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
