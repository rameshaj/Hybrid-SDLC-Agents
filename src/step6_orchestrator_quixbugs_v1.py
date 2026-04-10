#!/usr/bin/env python3
"""
QuixBugs SLM Patch Orchestrator (v1)

Single-attempt repair loop for QuixBugs Python programs.
All artifacts are logged for reproducibility and evaluation.
"""

import argparse
import json
import os
import re
import shlex
import subprocess
from datetime import datetime
from pathlib import Path


def read_jsonl_line(path, index):
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i == index:
                return json.loads(line)
    raise IndexError(f"task_index {index} out of range")


def run_cmd(cmd, timeout_s, cwd=None):
    print(f"[RUN] {cmd}")
    args = shlex.split(cmd)
    try:
        p = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        print("[TIMEOUT] command exceeded limit")
        return 124, e.stdout or "", (e.stderr or "") + "\n[TIMEOUT]\n"


def load_text(path):
    return Path(path).read_text(encoding="utf-8")


def save_text(path, text):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8")


def extract_unified_diff(text):
    m = re.search(r"```(?:diff)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"(^---\s.*?$.*)", text, flags=re.DOTALL | re.MULTILINE)
    if m and "+++" in m.group(1):
        return m.group(1).strip()
    m = re.search(r"(^diff --git\s.*$.*)", text, flags=re.DOTALL | re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def apply_patch(patch_text, repo_root):
    patch_file = Path(repo_root) / ".tmp_quixbugs.patch"
    patch_file.write_text(patch_text, encoding="utf-8")
    print("[PATCH] Applying patch")
    try:
        p = subprocess.run(
            ["patch", "-p0", "-i", str(patch_file)],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        return p.returncode == 0, (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return False, "patch command not found"


def build_prompt(task, buggy_code, test_output):
    return (
        "You are a senior software engineer fixing a Python bug.\n\n"
        f"Program: {task['algo']}\n"
        f"File: {task['buggy_path']}\n\n"
        "Return ONLY a unified diff patch.\n\n"
        "Buggy code:\n"
        "```python\n"
        f"{buggy_code}\n"
        "```\n\n"
        "Test output:\n"
        "```\n"
        f"{test_output}\n"
        "```\n"
    )


def call_slm(llama_cli, model, prompt, max_tokens, temp, timeout_s):
    print("[SLM] Invoking on-device model")
    cmd = [
        llama_cli,
        "-m", model,
        "-n", str(max_tokens),
        "--temp", str(temp),
        "-p", prompt,
    ]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
        return p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        print("[SLM] Timeout")
        return e.stdout or "", (e.stderr or "") + "\n[SLM TIMEOUT]\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_path", required=True)
    ap.add_argument("--task_index", type=int, required=True)
    ap.add_argument("--llama_cli_path", required=True)
    ap.add_argument("--gguf_model_path", required=True)
    ap.add_argument("--slm_timeout_s", type=int, default=900)
    ap.add_argument("--max_new_tokens", type=int, default=220)
    ap.add_argument("--temp", type=float, default=0.2)
    ap.add_argument("--repo_root", default=".")
    args = ap.parse_args()

    print("=== QuixBugs Orchestrator START ===")

    repo_root = os.path.abspath(args.repo_root)
    task = read_jsonl_line(args.tasks_path, args.task_index)

    print(f"[TASK] {task['task_id']}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(
        repo_root,
        "episodes",
        "quixbugs_runs",
        f"{ts}_{task['algo']}",
    )
    os.makedirs(run_dir, exist_ok=True)

    save_text(os.path.join(run_dir, "task.json"), json.dumps(task, indent=2))

    print("[TEST] Running buggy tests")
    rc0, out0, err0 = run_cmd(
        task["test_cmd"],
        int(task.get("test_timeout_s", 3)),
        cwd=repo_root,
    )
    test_before = (out0 or "") + (err0 or "")
    save_text(os.path.join(run_dir, "test_before.txt"), test_before)

    buggy_path = os.path.join(repo_root, task["buggy_path"])
    buggy_code = load_text(buggy_path)
    save_text(os.path.join(run_dir, "buggy_before.py"), buggy_code)

    prompt = build_prompt(task, buggy_code, test_before)
    save_text(os.path.join(run_dir, "prompt.txt"), prompt)

    slm_out, slm_err = call_slm(
        args.llama_cli_path,
        args.gguf_model_path,
        prompt,
        args.max_new_tokens,
        args.temp,
        args.slm_timeout_s,
    )
    save_text(os.path.join(run_dir, "slm_raw.txt"), slm_out)
    save_text(os.path.join(run_dir, "slm_err.txt"), slm_err)

    diff = extract_unified_diff(slm_out)
    if not diff:
        print("[FAIL] No diff produced")
        save_text(os.path.join(run_dir, "status.txt"), "NO_DIFF")
        return 1

    save_text(os.path.join(run_dir, "patch.diff"), diff)

    ok, patch_log = apply_patch(diff, repo_root)
    save_text(os.path.join(run_dir, "patch_apply.txt"), patch_log)
    if not ok:
        print("[FAIL] Patch application failed")
        save_text(os.path.join(run_dir, "status.txt"), "PATCH_APPLY_FAIL")
        return 2

    print("[TEST] Running tests after patch")
    rc1, out1, err1 = run_cmd(
        task["test_cmd"],
        int(task.get("test_timeout_s", 3)),
        cwd=repo_root,
    )
    test_after = (out1 or "") + (err1 or "")
    save_text(os.path.join(run_dir, "test_after.txt"), test_after)

    status = "PASS" if rc1 == 0 else "FAIL"
    save_text(os.path.join(run_dir, "status.txt"), status)

    print(f"=== RESULT: {status} ===")
    print(f"[EPISODE] {run_dir}")
    print("=== QuixBugs Orchestrator END ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
