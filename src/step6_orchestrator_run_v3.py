from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

# --- Step 6.2 modules you already created ---
from step6_2_patchgen_slm import generate_patch_with_slm
from step6_2_diff_sanitize import sanitize_unified_diff
from step6_2_git_apply import git_apply
from step6_2_test_runner import run_cmd
from step6_2_trace_logger import TraceLogger


def now_ms() -> int:
    return int(time.time() * 1000)


def safe_mkdir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def tail(s: str, n: int) -> str:
    if not s:
        return ""
    return s[-n:]


@dataclass
class EpisodeLogger:
    episode_dir: str
    step6_jsonl_path: str
    episode_meta_path: str
    _attempts: List[Dict[str, Any]]

    @staticmethod
    def create(base_runs_dir: str = "episodes/runs", base_logs_dir: str = "episodes/logs") -> "EpisodeLogger":
        run_id = str(uuid.uuid4())
        episode_dir = os.path.join(base_runs_dir, run_id)
        safe_mkdir(episode_dir)
        safe_mkdir(base_logs_dir)

        step6_jsonl_path = os.path.join(base_logs_dir, "step6_runs.jsonl")
        episode_meta_path = os.path.join(episode_dir, "episode.json")

        return EpisodeLogger(
            episode_dir=episode_dir,
            step6_jsonl_path=step6_jsonl_path,
            episode_meta_path=episode_meta_path,
            _attempts=[],
        )

    def write_attempt(self, attempt: Dict[str, Any]) -> None:
        self._attempts.append(attempt)

    def finalize(self, summary: Dict[str, Any]) -> None:
        payload = {"episode_dir": self.episode_dir, "summary": summary, "attempts": self._attempts}
        with open(self.episode_meta_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        flat = {
            "ts_ms": now_ms(),
            "episode_dir": self.episode_dir,
            "task_id": summary.get("task_id"),
            "success": summary.get("success"),
            "mode": summary.get("mode"),
            "tests_mode": summary.get("tests_mode"),
            "rag_k": summary.get("rag_k"),
            "touched_files": summary.get("touched_files"),
            "final_error": summary.get("final_error"),
        }
        with open(self.step6_jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(flat) + "\n")


# =========================
# Local SLM runner (llama.cpp)
# =========================
class LlamaCppClient:
    """
    Works with llama-cli builds that behave like interactive chat (prints `>`).
    We do NOT rely on unsupported flags like --no-conversation.

    Strategy:
      - Run llama-cli with -p and -n
      - Stream stdout
      - Once we see 'diff --git', capture until output goes quiet briefly
      - Terminate process
    """
    def __init__(self, llama_cli_path: str, gguf_model_path: str, temperature: float = 0.2, timeout_s: int = 900):
        self.llama_cli_path = llama_cli_path
        self.gguf_model_path = gguf_model_path
        self.temperature = temperature
        self.timeout_s = timeout_s

    def generate(self, prompt: str, max_new_tokens: int = 250) -> str:
        if not os.path.exists(self.llama_cli_path):
            raise RuntimeError(f"llama-cli not found at: {self.llama_cli_path}")
        if not os.path.exists(self.gguf_model_path):
            raise RuntimeError(f"GGUF model not found at: {self.gguf_model_path}")

        cmd = [
            self.llama_cli_path,
            "-m", self.gguf_model_path,
            "-p", prompt,
            "-n", str(int(max_new_tokens)),
            "--temp", str(self.temperature),
        ]

        started = time.time()
        p = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        captured: List[str] = []
        saw_diff = False
        last_output_time = time.time()

        max_chars = 250_000  # safety
        quiet_window_s = 0.8  # if no new output for this long AFTER seeing diff, stop

        try:
            assert p.stdout is not None
            while True:
                if (time.time() - started) > self.timeout_s:
                    break

                line = p.stdout.readline()

                if line == "":
                    # process ended?
                    if p.poll() is not None:
                        break
                    time.sleep(0.05)
                    # if diff already started and we are quiet, stop
                    if saw_diff and (time.time() - last_output_time) > quiet_window_s:
                        break
                    continue

                captured.append(line)
                last_output_time = time.time()

                if "diff --git" in line:
                    saw_diff = True

                if sum(len(x) for x in captured) > max_chars:
                    break

                # Some llama-cli builds echo a REPL prompt `>` even in one-shot.
                # If diff already started and we see a bare prompt line, stop.
                if saw_diff and line.strip() == ">":
                    break

            # terminate
            try:
                p.terminate()
                time.sleep(0.1)
            except Exception:
                pass
            try:
                if p.poll() is None:
                    p.kill()
            except Exception:
                pass

            out = "".join(captured)

            # If we never saw diff, include stderr tail for debugging
            if not saw_diff:
                err = ""
                try:
                    if p.stderr is not None:
                        err = p.stderr.read() or ""
                except Exception:
                    err = ""
                raise RuntimeError(f"slm_no_diff_seen_in_stream: {tail(err, 2000)}")

            return out

        finally:
            try:
                if p.poll() is None:
                    p.kill()
            except Exception:
                pass


# =========================
# Tasks
# =========================
def load_tasks(tasks_path: str) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []
    with open(tasks_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tasks.append(json.loads(line))
    return tasks


def build_task_id(t: Dict[str, Any]) -> str:
    proj = t.get("project") or t.get("proj") or "UNKNOWN"
    bug = str(t.get("bug_id") or t.get("bug") or "UNKNOWN")
    return t.get("task_id") or f"defects4j::{proj}-{bug}"


def normalize_version(bug_id: str, suffix: str) -> str:
    if bug_id.endswith("b") or bug_id.endswith("f"):
        return bug_id
    return f"{bug_id}{suffix}"


# =========================
# Defects4J helpers
# =========================
def defects4j_checkout(project: str, version: str, workdir: str, trace: TraceLogger, step: str) -> None:
    safe_mkdir(workdir)
    cmd = ["defects4j", "checkout", "-p", project, "-v", version, "-w", workdir]
    started = now_ms()
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    ended = now_ms()

    out = p.stdout.decode("utf-8", errors="replace")
    err = p.stderr.decode("utf-8", errors="replace")

    trace.log_cmd(step=step, cwd=os.getcwd(), cmd=cmd, rc=p.returncode, stdout=out, stderr=err, started_ms=started, ended_ms=ended)
    trace.write_text(f"{step}/defects4j_checkout.out.txt", out)
    trace.write_text(f"{step}/defects4j_checkout.err.txt", err)

    if p.returncode != 0:
        raise RuntimeError(f"defects4j checkout failed (code={p.returncode}): {tail(err, 2000)}")


def defects4j_test(repo_root: str, timeout_s: int = 1200) -> Tuple[bool, str, str, List[str]]:
    tr = run_cmd(repo_root, ["defects4j", "test"], timeout_s=timeout_s)
    out = tr.stdout or ""
    err = tr.stderr or ""

    failing: List[str] = []
    for line in (out + "\n" + err).splitlines():
        line = line.strip()
        if "::" in line:
            failing.append(line)

    # unique preserve order
    seen = set()
    ft: List[str] = []
    for x in failing:
        if x not in seen:
            seen.add(x)
            ft.append(x)
    return tr.ok, out, err, ft


# =========================
# Local RAG (FIXED: only Java in source/tests + context)
# =========================
def local_rag_grep(repo_root: str, query: str, k: int = 10) -> str:
    rg = shutil.which("rg")
    if not rg:
        return ""

    # Keep only useful tokens
    tokens = [t for t in re.split(r"[\s,;()]+", query) if len(t) >= 3][:8]

    snippets: List[str] = []
    hits = 0

    # Search only real Java source/tests, avoid ChangeLog/all_tests/build artifacts
    search_roots = [os.path.join(repo_root, "source"), os.path.join(repo_root, "tests")]

    for tok in tokens:
        for root in search_roots:
            if not os.path.exists(root):
                continue

            cmd = [
                rg,
                "-n",
                "--no-heading",
                "-C", "2",                 # 2 lines of context
                "--max-count", "5",
                "--glob", "*.java",        # ONLY Java files
                tok,
                root,
            ]
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            out_lines = p.stdout.decode("utf-8", errors="replace").splitlines()

            # Group context blocks (rg prints '--' separators). We keep as-is.
            for line in out_lines:
                snippets.append(line)
            if out_lines:
                snippets.append("")  # separator between token hits

            # Count hits roughly by matching file:line:
            for line in out_lines:
                if ":" in line and ("/" in line or "\\" in line):
                    hits += 1
                    if hits >= k:
                        break
            if hits >= k:
                break
        if hits >= k:
            break

    return "\n".join(snippets).strip()


# =========================
# Baseline mode
# =========================
def run_fixed_baseline(tasks_path: str, task_index: int, rag_query: str, rag_k: int) -> int:
    logger = EpisodeLogger.create()
    trace = TraceLogger(episode_dir=logger.episode_dir, commands=[])

    workdir = os.path.join(logger.episode_dir, "workdir")
    buggy_root = os.path.join(workdir, "buggy")
    fixed_root = os.path.join(workdir, "fixed")
    safe_mkdir(workdir)

    tasks = load_tasks(tasks_path)
    task = tasks[task_index]

    task_id = build_task_id(task)
    project = task.get("project") or task.get("proj")
    bug_id = str(task.get("bug_id") or task.get("bug"))

    summary: Dict[str, Any] = {
        "task_id": task_id,
        "task_index": task_index,
        "mode": "fixed_baseline",
        "tests_mode": None,
        "rag_k": rag_k,
        "rag_query": rag_query,
        "episode_dir": logger.episode_dir,
        "workdir": workdir,
        "success": False,
        "final_error": None,
        "touched_files": [],
    }

    t0 = time.time()
    try:
        print("==[1/5] checkout buggy==")
        buggy_ver = normalize_version(bug_id, "b")
        defects4j_checkout(project, buggy_ver, buggy_root, trace, step="checkout_buggy")

        print("==[2/5] tests buggy==")
        ok_b, out_b, err_b, failing_b = defects4j_test(buggy_root)
        trace.write_text(
            "tests_buggy/defects4j_test.full.txt",
            f"=== defects4j test (buggy {buggy_ver}) ===\nok={ok_b}\n"
            "---- STDOUT (tail) ----\n" + tail(out_b, 8000) + "\n"
            "---- STDERR (tail) ----\n" + tail(err_b, 8000) + "\n",
        )
        trace.write_json("tests_buggy/defects4j_test.parsed.json", {"ok": ok_b, "failing_tests": failing_b})

        print("==[3/5] local RAG on buggy (logged)==")
        rag_hits = local_rag_grep(buggy_root, rag_query, k=rag_k)
        trace.write_text("rag/rag_query.txt", rag_query)
        trace.write_text("rag/rag_hits.txt", rag_hits)

        print("==[4/5] checkout fixed==")
        fixed_ver = normalize_version(bug_id, "f")
        defects4j_checkout(project, fixed_ver, fixed_root, trace, step="checkout_fixed")

        print("==[5/5] tests fixed==")
        ok_f, out_f, err_f, failing_f = defects4j_test(fixed_root)
        trace.write_text(
            "tests_fixed/defects4j_test.full.txt",
            f"=== defects4j test (fixed {fixed_ver}) ===\nok={ok_f}\n"
            "---- STDOUT (tail) ----\n" + tail(out_f, 8000) + "\n"
            "---- STDERR (tail) ----\n" + tail(err_f, 8000) + "\n",
        )
        trace.write_json("tests_fixed/defects4j_test.parsed.json", {"ok": ok_f, "failing_tests": failing_f})

        summary["success"] = (len(failing_b) > 0) and (len(failing_f) == 0)
        if not summary["success"]:
            summary["final_error"] = f"baseline_check_failed: failing_buggy={len(failing_b)} failing_fixed={len(failing_f)}"
        summary["elapsed_s"] = round(time.time() - t0, 3)

        logger.finalize(summary)

        print("✅ baseline complete")
        print(f"Episode: {Path(logger.episode_dir).name}")
        print(f"Task: {task_id} (project={project} bug_id={bug_id})")
        print(f"Buggy failing tests: {len(failing_b)}")
        print(f"Fixed failing tests: {len(failing_f)}")
        print(f"Success: {summary['success']}")
        print(f"Episode meta: {logger.episode_meta_path}")
        print(f"Global log:   {logger.step6_jsonl_path}")
        return 0 if summary["success"] else 5

    except Exception as e:
        summary["final_error"] = f"exception: {e}"
        summary["elapsed_s"] = round(time.time() - t0, 3)
        logger.finalize(summary)
        trace.write_text("meta/exception.txt", str(e))
        print("❌ baseline failed with exception")
        print(f"Episode: {Path(logger.episode_dir).name}")
        print(f"Error: {e}")
        print(f"Episode meta: {logger.episode_meta_path}")
        return 10


# =========================
# SLM patch mode
# =========================
def run_slm_patch(
    tasks_path: str,
    task_index: int,
    tests_mode: str,
    rag_query: str,
    rag_k: int,
    llama_cli_path: str,
    gguf_model_path: str,
    slm_timeout_s: int,
    max_new_tokens: int,
) -> int:
    logger = EpisodeLogger.create()
    trace = TraceLogger(episode_dir=logger.episode_dir, commands=[])

    workdir = os.path.join(logger.episode_dir, "workdir")
    src_root = os.path.join(workdir, "source")
    safe_mkdir(workdir)

    tasks = load_tasks(tasks_path)
    task = tasks[task_index]

    task_id = build_task_id(task)
    project = task.get("project") or task.get("proj")
    bug_id = str(task.get("bug_id") or task.get("bug"))
    buggy_ver = normalize_version(bug_id, "b")

    summary: Dict[str, Any] = {
        "task_id": task_id,
        "task_index": task_index,
        "mode": "slm_patch",
        "tests_mode": tests_mode,
        "rag_k": rag_k,
        "rag_query": rag_query,
        "episode_dir": logger.episode_dir,
        "workdir": workdir,
        "success": False,
        "final_error": None,
        "touched_files": [],
    }

    t0 = time.time()
    try:
        trace.write_json(
            "meta/steps_why.json",
            {
                "checkout": "Checkout buggy version (reproducible workdir)",
                "tests_before": "Capture failing tests as bug signal",
                "rag": "Retrieve real Java snippets from source/tests",
                "slm": "Generate candidate unified diff",
                "sanitize": "Validate diff format + normalize paths",
                "policy": "Reject edits outside source/*.java",
                "apply": "Apply patch via git apply",
                "tests_after": "Verify by rerunning defects4j tests",
            },
        )

        print("==[1/7] defects4j checkout (buggy)==")
        defects4j_checkout(project, buggy_ver, src_root, trace, step="checkout_buggy")

        print("==[2/7] tests before patch==")
        ok0, out0, err0, failing_tests = defects4j_test(src_root)
        failing_output_text = (
            "=== defects4j test (initial) ===\n"
            f"version={buggy_ver}\n"
            f"ok={ok0}\n"
            "---- STDOUT (tail) ----\n" + tail(out0, 8000) + "\n"
            "---- STDERR (tail) ----\n" + tail(err0, 8000) + "\n"
        )
        trace.write_text("tests_before/defects4j_test.full.txt", failing_output_text)
        trace.write_json("tests_before/defects4j_test.parsed.json", {"ok": ok0, "failing_tests": failing_tests})

        print("==[3/7] local RAG (java snippets)==")
        rag_snippets_text = local_rag_grep(src_root, rag_query, k=rag_k)
        trace.write_text("rag/rag_query.txt", rag_query)
        trace.write_text("rag/rag_hits.txt", rag_snippets_text)

        print("==[4/7] SLM patch generation==")
        slm_client = LlamaCppClient(
            llama_cli_path=llama_cli_path,
            gguf_model_path=gguf_model_path,
            temperature=0.2,
            timeout_s=slm_timeout_s,
        )

        repo_hint = (
            f"Project={project} Bug={bug_id} Version={buggy_ver}\n"
            "IMPORTANT:\n"
            "- Output ONLY a unified diff (git style)\n"
            "- No markdown fences\n"
            "- Modify ONLY ONE file\n"
            "- File path MUST be relative and MUST start with 'source/' and end with '.java'\n"
            "Example header:\n"
            "diff --git a/source/org/.../Foo.java b/source/org/.../Foo.java\n"
        )

        patch_res = generate_patch_with_slm(
            llm_client=slm_client,
            task_id=task_id,
            failing_test_output=failing_output_text,
            rag_snippets=rag_snippets_text,
            repo_hint=repo_hint,
            max_new_tokens=max_new_tokens,
        )

        prompt_used = getattr(patch_res, "prompt_used", "") or ""
        trace.write_text("prompt/prompt_full.txt", prompt_used)
        trace.write_text("slm/slm_stdout.txt", patch_res.raw_text or "")
        trace.write_text("diff/diff_raw.patch", patch_res.diff or "")

        attempt: Dict[str, Any] = {
            "attempt_idx": 0,
            "model": "slm",
            "patchgen_ok": patch_res.ok,
            "patchgen_error": patch_res.error,
            "raw_model_text_chars": len(patch_res.raw_text or ""),
            "initial_tests_ok": ok0,
            "initial_failing_tests": failing_tests[:50],
            "rag_k": rag_k,
            "rag_query": rag_query,
            "slm_timeout_s": slm_timeout_s,
            "max_new_tokens": max_new_tokens,
        }

        if not patch_res.ok:
            logger.write_attempt(attempt)
            summary["final_error"] = patch_res.error or "patchgen_failed"
            summary["elapsed_s"] = round(time.time() - t0, 3)
            logger.finalize(summary)
            print("❌ failed at patch generation")
            print(f"Episode: {Path(logger.episode_dir).name}")
            print(f"Error: {summary['final_error']}")
            return 2

        print("==[5/7] sanitize diff==")
        san = sanitize_unified_diff(patch_res.diff or "", repo_root=src_root)
        trace.write_json("diff/sanitize_meta.json", {"ok": san.ok, "error": san.error, "touched_files": san.touched_files})
        trace.write_text("diff/diff_sanitized.patch", san.diff or "")

        attempt["diff_sanitize_ok"] = san.ok
        attempt["diff_sanitize_error"] = san.error
        attempt["touched_files"] = san.touched_files

        if not san.ok:
            logger.write_attempt(attempt)
            summary["final_error"] = san.error or "diff_sanitize_failed"
            summary["touched_files"] = san.touched_files
            summary["elapsed_s"] = round(time.time() - t0, 3)
            logger.finalize(summary)
            print("❌ failed at diff sanitize")
            print(f"Episode: {Path(logger.episode_dir).name}")
            print(f"Error: {summary['final_error']}")
            return 3

        print("==[5.5/7] diff policy guard (source/*.java only)==")
        bad: List[str] = []
        for f in san.touched_files:
            if not f.startswith("source/") or not f.endswith(".java"):
                bad.append(f)

        if bad:
            attempt["diff_policy_reject"] = True
            attempt["diff_policy_reject_files"] = bad
            logger.write_attempt(attempt)
            summary["final_error"] = f"diff_policy_reject: only source/*.java allowed, got: {bad}"
            summary["touched_files"] = san.touched_files
            summary["elapsed_s"] = round(time.time() - t0, 3)
            logger.finalize(summary)
            trace.write_json("diff/policy_reject.json", {"rejected_files": bad, "touched_files": san.touched_files})
            print("❌ rejected diff: edited outside source/*.java")
            print(f"Rejected files: {bad}")
            return 6

        print("==[6/7] apply diff==")
        app = git_apply(repo_root=src_root, diff_text=san.diff or "")
        trace.write_text("apply/git_apply.out.txt", app.stdout or "")
        trace.write_text("apply/git_apply.err.txt", app.stderr or "")
        trace.write_json("apply/git_apply_meta.json", {"ok": app.ok, "error": app.error})

        attempt["git_apply_ok"] = app.ok
        attempt["git_apply_error"] = app.error
        attempt["git_apply_stderr_tail"] = tail(app.stderr or "", 2000)

        if not app.ok:
            logger.write_attempt(attempt)
            summary["final_error"] = app.error or "git_apply_failed"
            summary["touched_files"] = san.touched_files
            summary["elapsed_s"] = round(time.time() - t0, 3)
            logger.finalize(summary)
            print("❌ failed at git apply")
            print(f"Error: {summary['final_error']}")
            return 4

        print("==[7/7] tests after patch==")
        ok1, out1, err1, failing_tests_after = defects4j_test(src_root)
        trace.write_text("tests_after/defects4j_test.out.txt", out1 or "")
        trace.write_text("tests_after/defects4j_test.err.txt", err1 or "")
        trace.write_json("tests_after/defects4j_test.parsed.json", {"ok": ok1, "failing_tests": failing_tests_after})

        attempt["tests_ok"] = ok1
        attempt["failing_tests_after"] = failing_tests_after[:50]
        logger.write_attempt(attempt)

        summary["touched_files"] = san.touched_files
        summary["success"] = (len(failing_tests_after) == 0)
        if not summary["success"]:
            summary["final_error"] = "tests_failed_after_patch"
        summary["elapsed_s"] = round(time.time() - t0, 3)

        logger.finalize(summary)

        print("✅ slm_patch run complete")
        print(f"Episode: {Path(logger.episode_dir).name}")
        print(f"Task: {task_id} (project={project} bug_id={bug_id})")
        print(f"Success: {summary['success']}")
        print(f"Touched files: {summary['touched_files']}")
        print(f"Episode meta: {logger.episode_meta_path}")
        print(f"Global log:   {logger.step6_jsonl_path}")
        return 0 if summary["success"] else 5

    except Exception as e:
        summary["final_error"] = f"exception: {e}"
        summary["elapsed_s"] = round(time.time() - t0, 3)
        logger.finalize(summary)
        trace.write_text("meta/exception.txt", str(e))
        print("❌ slm_patch failed with exception")
        print(f"Episode: {Path(logger.episode_dir).name}")
        print(f"Error: {e}")
        return 10


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="baseline", choices=["baseline", "slm_patch"])

    ap.add_argument("--tasks_path", default="data/defects4j_tasks.jsonl")
    ap.add_argument("--task_index", type=int, default=0)

    ap.add_argument("--tests_mode", default="failing_only", choices=["failing_only", "full"])
    ap.add_argument("--rag_k", type=int, default=10)
    ap.add_argument("--rag_query", default="")

    ap.add_argument("--llama_cli_path", default=os.environ.get("LLAMA_CLI", "/usr/local/bin/llama-cli"))
    ap.add_argument("--gguf_model_path", default=os.environ.get("GGUF_MODEL", "models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"))
    ap.add_argument("--slm_timeout_s", type=int, default=900)
    ap.add_argument("--max_new_tokens", type=int, default=250)

    args = ap.parse_args()

    if not os.path.exists(args.tasks_path):
        print(f"❌ tasks_path not found: {args.tasks_path}")
        print('Create JSONL like: {"project":"Chart","bug_id":"1"}')
        return 1

    tasks = load_tasks(args.tasks_path)
    if args.task_index < 0 or args.task_index >= len(tasks):
        print(f"❌ task_index out of range: {args.task_index} (tasks={len(tasks)})")
        return 1

    if not args.rag_query:
        args.rag_query = build_task_id(tasks[args.task_index])

    if args.mode == "baseline":
        return run_fixed_baseline(args.tasks_path, args.task_index, args.rag_query, args.rag_k)

    return run_slm_patch(
        tasks_path=args.tasks_path,
        task_index=args.task_index,
        tests_mode=args.tests_mode,
        rag_query=args.rag_query,
        rag_k=args.rag_k,
        llama_cli_path=args.llama_cli_path,
        gguf_model_path=args.gguf_model_path,
        slm_timeout_s=args.slm_timeout_s,
        max_new_tokens=args.max_new_tokens,
    )


if __name__ == "__main__":
    raise SystemExit(main())
