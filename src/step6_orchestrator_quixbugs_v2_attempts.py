#!/usr/bin/env python3
"""
QuixBugs SLM Patch Orchestrator – Step 6.3 (FINAL, SINGLE-FILE)

Guarantees:
- No git apply --check gating
- Robust patch application
- Clear terminal progress logs
- Works across all QuixBugs Python tasks
- Captures actual applied diff
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import time
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

# -------------------- logging --------------------

def ts():
    return datetime.now().strftime("%H:%M:%S")

def log(msg):
    print(f"[{ts()}] {msg}", flush=True)

def stage(name):
    print(f"\n[{ts()}] ===== {name} =====", flush=True)

# -------------------- helpers --------------------

def read_jsonl_line(path, idx):
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i == idx:
                return json.loads(line)
    raise IndexError("task_index out of range")

def save_text(p: Path, t: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t or "", encoding="utf-8")

def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def run_cmd(cmd, timeout, cwd=None):
    log(f"RUN: {cmd}")
    start = time.time()
    env = os.environ.copy()
    env["PYTHONFAULTHANDLER"] = "1"
    p = subprocess.Popen(
        shlex.split(cmd),
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out or "", err or "", time.time() - start
    except subprocess.TimeoutExpired:
        try:
            p.send_signal(signal.SIGUSR1)
            time.sleep(0.5)
            p.kill()
        except Exception:
            pass
        return 124, "", "[TIMEOUT]\n", time.time() - start

# -------------------- QuixBugs helpers --------------------

def qb_relpath(task):
    marker = "data/external/QuixBugs/"
    return task["buggy_path"].split(marker, 1)[-1]

def qb_rollback(task):
    return f"git -C {task['quixbugs_dir']} checkout -- {qb_relpath(task)}"

# -------------------- diff handling --------------------

def extract_diff(text: str) -> Optional[str]:
    idx = text.find("diff --git")
    if idx == -1:
        return None
    diff = text[idx:]
    if "@@" not in diff:
        return None
    return diff.strip() + "\n"

# -------------------- patch apply --------------------

def apply_patch(diff: str, repo: Path, target_rel: str, out_dir: Path) -> Tuple[bool, str]:
    patch_file = out_dir / ".attempt.patch"
    patch_file.write_text(diff, encoding="utf-8")

    methods = [
        ["git", "apply", "--3way", "--whitespace=nowarn", str(patch_file)],
        ["git", "apply", "--whitespace=nowarn", str(patch_file)],
        ["patch", "-p1", "--fuzz=3", "--batch", "-i", str(patch_file)],
        ["patch", "-p0", "--fuzz=3", "--batch", "-i", str(patch_file)],
    ]

    for cmd in methods:
        log(f"TRY APPLY: {' '.join(cmd)}")
        p = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True)
        if p.returncode == 0:
            rc, out, err, _ = run_cmd(
                f"git -C {repo} diff -- {target_rel}", 10
            )
            save_text(out_dir / "applied_diff_actual.diff", out + err)
            return True, " ".join(cmd)

    return False, "ALL_APPLY_METHODS_FAILED"

# -------------------- prompt --------------------

def build_prompt(task, buggy, failing, attempt, max_attempts, prev):
    rel = qb_relpath(task)
    return (
        "You are fixing a Python bug.\n"
        "STRICT RULES:\n"
        "1) Output ONLY a unified diff\n"
        "2) First line MUST be: diff --git\n"
        "3) NO explanation text\n\n"
        f"Target:\n"
        f"a/{rel}\n"
        f"b/{rel}\n\n"
        f"Attempt {attempt}/{max_attempts}\n"
        f"Previous status: {prev}\n\n"
        "Buggy code:\n"
        "```python\n"
        f"{buggy}\n"
        "```\n\n"
        "Failing output:\n"
        "```\n"
        f"{failing}\n"
        "```\n"
    )

# -------------------- SLM runner --------------------

def run_slm(llama, model, prompt_file, timeout, out_p, err_p):
    cmd = [
        llama,
        "-m", model,
        "-n", "1200",
        "--temp", "0.0",
        "-f", str(prompt_file),
        "-no-cnv",
    ]
    start = time.time()
    with open(out_p, "w") as fo, open(err_p, "w") as fe:
        p = subprocess.Popen(cmd, stdout=fo, stderr=fe)
        while True:
            if p.poll() is not None:
                return p.returncode, time.time() - start
            if time.time() - start > timeout:
                fe.write("\n[SLM TIMEOUT]\n")
                p.kill()
                return 124, time.time() - start
            time.sleep(0.5)

# -------------------- main --------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_path", required=True)
    ap.add_argument("--task_index", type=int, required=True)
    ap.add_argument("--llama_path", required=True)
    ap.add_argument("--gguf_model_path", required=True)
    ap.add_argument("--max_attempts", type=int, default=5)
    ap.add_argument("--slm_timeout_s", type=int, default=900)
    ap.add_argument("--repo_root", default=".")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    task = read_jsonl_line(args.tasks_path, args.task_index)

    qb_repo = Path(task["quixbugs_dir"]).resolve()
    test_cmd = task["test_cmd"]
    test_timeout = max(int(task.get("test_timeout_s", 3)), 10)

    run_dir = repo_root / "episodes/quixbugs_runs/attempts" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task['algo']}"
    run_dir.mkdir(parents=True, exist_ok=True)

    log(f"TASK: {task['task_id']}")
    log(f"RUN_DIR: {run_dir}")

    stage("BASELINE")
    rc0, o0, e0, _ = run_cmd(test_cmd, test_timeout, cwd=str(repo_root))
    save_text(run_dir / "test_before.txt", o0 + e0)

    if rc0 == 0:
        save_text(run_dir / "final_status.txt", "ALREADY_PASS")
        log("BASELINE PASS – EXIT")
        return 0

    prev_status = "INIT"
    buggy_abs = repo_root / task["buggy_path"]

    for k in range(1, args.max_attempts + 1):
        stage(f"ATTEMPT {k}/{args.max_attempts}")
        ad = run_dir / f"attempt_{k:02d}"
        ad.mkdir(exist_ok=True)

        run_cmd(qb_rollback(task), 30, cwd=str(repo_root))

        rc_pre, o_pre, e_pre, _ = run_cmd(test_cmd, test_timeout, cwd=str(repo_root))
        save_text(ad / "test_pre.txt", o_pre + e_pre)

        buggy = load_text(buggy_abs)
        prompt = build_prompt(task, buggy, o_pre + e_pre, k, args.max_attempts, prev_status)
        save_text(ad / "prompt.txt", prompt)

        stage("SLM")
        rc_slm, dt = run_slm(
            args.llama_path,
            args.gguf_model_path,
            ad / "prompt.txt",
            args.slm_timeout_s,
            ad / "slm_raw.txt",
            ad / "slm_err.txt",
        )
        log(f"SLM rc={rc_slm} time={dt:.1f}s")

        diff = extract_diff(load_text(ad / "slm_raw.txt"))
        if not diff:
            prev_status = "BAD_DIFF"
            log("BAD_DIFF")
            continue

        stage("PATCH APPLY")
        ok, method = apply_patch(diff, qb_repo, qb_relpath(task), ad)
        log(f"PATCH RESULT: {method}")

        if not ok:
            prev_status = "PATCH_APPLY_FAIL"
            continue

        stage("POST TEST")
        rc_post, o_post, e_post, _ = run_cmd(test_cmd, test_timeout, cwd=str(repo_root))
        save_text(ad / "test_after.txt", o_post + e_post)

        if rc_post == 0:
            save_text(run_dir / "final_status.txt", "PASS")
            log("PASS")
            return 0

        prev_status = "FAIL"

    save_text(run_dir / "final_status.txt", "FAIL")
    log("FAIL AFTER ALL ATTEMPTS")
    return 1

if __name__ == "__main__":
    sys.exit(main())
