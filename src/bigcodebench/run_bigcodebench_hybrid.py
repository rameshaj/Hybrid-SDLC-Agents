#!/usr/bin/env python3
"""
BigCodeBench hybrid runner: SLM first, fallback to LLM if needed.
Rule-based router with hooks for learned routing later.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.slm_llama_cli import SLMConfig
from src.llm_fallback_openai_codegen import openai_chat_completion_codegen


@dataclass
class EvalResult:
    ok: bool
    score: float
    rc: int
    stdout: str
    stderr: str
    elapsed_s: float
    failure_summary: str = ""


class RuleBasedRouter:
    """
    Rule-based router.
    Hook point for learned router later (RouteLLM-style).
    """

    def decide(
        self,
        score: float,
        pass_threshold: float,
        slm_attempts_left: int,
        fallback_attempts_left: int,
    ) -> Tuple[str, str]:
        if score >= pass_threshold:
            return "ACCEPT", "score >= threshold"
        if slm_attempts_left > 0:
            return "RETRY_SLM", "score < threshold; slm attempts left"
        if fallback_attempts_left > 0:
            return "ESCALATE_LLM", "score < threshold; fallback attempts left"
        return "GIVE_UP", "score < threshold; no attempts left"


def load_tasks(path: Path) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tasks.append(json.loads(line))
    return tasks


def extract_code(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"```python\n(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\n(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    # Strip common chat prefixes
    if "assistant" in text:
        text = text.split("assistant", 1)[1]
    if "user" in text and text.strip().startswith("user"):
        text = text.split("user", 1)[-1]
    return text.strip()


def clean_code_blob(code: str) -> str:
    if not code:
        return code
    cleaned: List[str] = []
    for line in code.splitlines():
        s = line.strip()
        if s.startswith("```"):
            continue
        if s.startswith("assistant") or s.startswith("user"):
            continue
        if s.startswith("> EOF"):
            continue
        if line.startswith(("build:", "main:", "llama_", "common_", "system_info:", "sampler ", "load:")):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def trim_to_entry_point(code: str, entry_point: str) -> str:
    if not code or not entry_point:
        return code
    needle = f"def {entry_point}"
    idx = code.rfind(needle)
    if idx != -1:
        return code[idx:]
    return code


def trim_prompt_echo(code: str, entry_point: str) -> str:
    if not code or not entry_point:
        return code
    needle = f"def {entry_point}"
    idx = code.rfind(needle)
    if idx == -1:
        return code
    prefix = code[:idx]
    # find last import block before the function
    import_lines = [m.start() for m in re.finditer(r"^(?:from\\s+\\S+\\s+import\\s+|import\\s+\\S+)", prefix, re.M)]
    start = import_lines[-1] if import_lines else idx
    return code[start:].lstrip()


def extract_import_lines(code_prompt: str) -> List[str]:
    imports: List[str] = []
    for line in code_prompt.splitlines():
        stripped = line.strip()
        if stripped.startswith("def "):
            break
        if stripped.startswith("import ") or stripped.startswith("from "):
            imports.append(line)
    return imports


def inject_required_imports(code: str, code_prompt: str) -> str:
    if not code_prompt:
        return code
    required = extract_import_lines(code_prompt)
    if not required:
        return code
    missing = [ln for ln in required if ln not in code]
    if not missing:
        return code
    return "\n".join(missing) + "\n\n" + code.lstrip()


def extract_prompt_preamble(code_prompt: str, entry_point: str) -> str:
    if not code_prompt:
        return ""
    lines = code_prompt.splitlines()
    out: List[str] = []
    target = f"def {entry_point}" if entry_point else "def "
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(target):
            break
        out.append(line)
    return "\n".join(out).strip()


def inject_required_preamble(code: str, code_prompt: str, entry_point: str) -> str:
    preamble = extract_prompt_preamble(code_prompt, entry_point)
    if not preamble:
        return code
    if not code:
        return preamble + "\n"
    body = code.lstrip()
    if body.startswith(preamble):
        return code
    existing = {ln.strip() for ln in body.splitlines() if ln.strip()}
    missing_lines: List[str] = []
    for ln in preamble.splitlines():
        if not ln.strip() or ln.strip() not in existing:
            missing_lines.append(ln)
    if not missing_lines:
        return code
    return "\n".join(missing_lines).rstrip() + "\n\n" + body


def syntax_error_summary(code: str) -> str:
    if not code.strip():
        return "NO_CODE_EXTRACTED"
    try:
        ast.parse(code)
        return ""
    except SyntaxError as e:
        loc = f" line {e.lineno}" if e.lineno else ""
        return f"SyntaxError: {e.msg}{loc}"


def build_syntax_repair_prompt(code: str, entry_point: str, code_prompt: str, err: str) -> str:
    preamble = extract_prompt_preamble(code_prompt, entry_point)
    return (
        "Fix the Python syntax and return ONLY valid Python code.\n"
        "No markdown. No explanations. No tests.\n"
        f"Function name must remain: {entry_point}\n"
        "Keep required imports/constants and function signature.\n"
        f"Current syntax error: {err}\n\n"
        "Required preamble:\n"
        f"{preamble}\n\n"
        "Code to fix:\n"
        f"{code}\n"
    )


def build_prompt(task_prompt: str, entry_point: str, prev_failures: List[str]) -> str:
    header = (
        "You are a coding assistant.\n"
        "Complete the function below.\n"
        "Return ONLY valid Python code. No explanations, no markdown.\n"
        "Do NOT include tests or example usage.\n"
        f"Function name: {entry_point}\n"
        "Return the full code including all provided imports and the function definition.\n"
        "Do not remove or rename any provided imports or the function signature.\n"
        "Use the provided stub and fill in the function body.\n"
    )
    if prev_failures:
        header += "Previous failures:\n"
        for item in prev_failures:
            header += f"- {item}\n"
    return header + "\n" + task_prompt.strip() + "\n"


def build_fallback_system_prompt() -> str:
    return (
        "You are a coding assistant. "
        "Return ONLY valid Python code for the function. "
        "No explanations, no markdown."
    )


def run_slm_prompt(prompt: str, cfg: SLMConfig, timeout_s: int | None = None) -> str:
    if timeout_s is None:
        timeout_s = cfg.timeout_s

    cmd = [
        cfg.llama_cli,
        "-m", cfg.model_path,
        "-p", prompt,
        "-n", str(cfg.n_tokens),
        "--seed", str(cfg.seed),
        "--temp", str(cfg.temp),
        "--top-p", str(cfg.top_p),
        "--repeat-penalty", str(cfg.repeat_penalty),
    ]

    p = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        timeout=timeout_s,
        stdin=subprocess.DEVNULL,
    )

    # Return stdout only to avoid stderr logs polluting code extraction
    return (p.stdout or "").strip()


def summarize_failure(rc: int, stdout: str, stderr: str, timed_out: bool) -> str:
    if timed_out:
        return "TIMEOUT"
    if rc == 0:
        return "PASS"
    blob = (stderr or "") + ("\n" if stderr and stdout else "") + (stdout or "")
    lines = [ln for ln in blob.splitlines() if ln.strip()]
    tail = "\n".join(lines[-6:]) if lines else "no output"
    # Try to extract exception line
    exc = ""
    for ln in reversed(lines):
        if "Error" in ln or "Exception" in ln or "AssertionError" in ln:
            exc = ln.strip()
            break
    if exc:
        return f"{exc} | tail: {tail}"
    return f"FAIL | tail: {tail}"


def build_test_file(code: str, test: str, entry_point: str) -> str:
    return (
        f"{code}\n\n"
        f"{test}\n\n"
        "if __name__ == '__main__':\n"
        "    import unittest\n"
        "    unittest.main()\n"
    )


def run_tests(code: str, test: str, entry_point: str, timeout_s: int, work_dir: Path) -> EvalResult:
    tmp_path = work_dir / "candidate_run.py"
    tmp_path.write_text(build_test_file(code, test, entry_point), encoding="utf-8")

    start = time.time()
    timed_out = False
    def _to_text(x: Any) -> str:
        if x is None:
            return ""
        if isinstance(x, bytes):
            return x.decode("utf-8", errors="replace")
        return str(x)
    try:
        p = subprocess.run(
            [sys.executable, str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        rc = p.returncode
        stdout = p.stdout or ""
        stderr = p.stderr or ""
    except subprocess.TimeoutExpired as e:
        timed_out = True
        rc = 124
        stdout = _to_text(e.stdout)
        stderr = _to_text(e.stderr) + "\n[TIMEOUT]\n"

    elapsed = time.time() - start
    ok = (rc == 0) and (not timed_out)
    score = 1.0 if ok else 0.0
    summary = summarize_failure(rc, stdout, stderr, timed_out)

    return EvalResult(
        ok=ok,
        score=score,
        rc=rc,
        stdout=stdout,
        stderr=stderr,
        elapsed_s=elapsed,
        failure_summary=summary,
    )


def ensure_run_dir(base: Path, task_id: str) -> Path:
    ts = time.strftime("%Y%m%d_%H%M%S")
    safe_id = task_id.replace("/", "_")
    run_dir = base / f"{ts}_{safe_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text or "", encoding="utf-8")


def run_task(
    task: Dict[str, Any],
    slm_cfg: SLMConfig,
    slm_attempts: int,
    fallback_attempts: int,
    pass_threshold: float,
    test_timeout_s: int,
    out_base: Path,
    fallback_model: str,
    fallback_timeout_s: int,
    fallback_max_tokens: int,
    fallback_temp: float,
) -> Dict[str, Any]:
    task_id = task.get("task_id", "unknown")
    entry_point = task.get("entry_point", "")
    code_prompt = task.get("code_prompt", "") or ""
    prompt = (
        task.get("complete_prompt")
        or task.get("instruct_prompt")
        or code_prompt
        or ""
    )
    test = task.get("test", "")

    run_dir = ensure_run_dir(out_base, task_id)
    save_text(run_dir / "task.json", json.dumps(task, indent=2))

    router = RuleBasedRouter()
    slm_failures: List[str] = []
    fallback_failures: List[str] = []

    # SLM attempts
    slm_best: Optional[Dict[str, Any]] = None
    for k in range(1, slm_attempts + 1):
        ad = run_dir / f"slm_attempt_{k:02d}"
        ad.mkdir(exist_ok=True)
        attempt_prompt = build_prompt(prompt, entry_point, slm_failures)
        save_text(ad / "prompt.txt", attempt_prompt)

        code = ""
        try:
            raw = run_slm_prompt(attempt_prompt, slm_cfg, timeout_s=slm_cfg.timeout_s)
            save_text(ad / "slm_raw.txt", raw)

            code = clean_code_blob(extract_code(raw))
            code = trim_prompt_echo(code, entry_point)
            code = inject_required_imports(code, code_prompt)
            code = inject_required_preamble(code, code_prompt, entry_point)
            save_text(ad / "code.py", code)

            if not code:
                res = EvalResult(
                    ok=False, score=0.0, rc=1, stdout="", stderr="NO_CODE", elapsed_s=0.0,
                    failure_summary="NO_CODE_EXTRACTED",
                )
            else:
                syn = syntax_error_summary(code)
                if syn:
                    repair_prompt = build_syntax_repair_prompt(code, entry_point, code_prompt, syn)
                    save_text(ad / "syntax_repair_prompt.txt", repair_prompt)
                    try:
                        raw_fix = run_slm_prompt(repair_prompt, slm_cfg, timeout_s=min(180, slm_cfg.timeout_s))
                        save_text(ad / "syntax_repair_raw.txt", raw_fix)
                        repaired = clean_code_blob(extract_code(raw_fix))
                        repaired = trim_prompt_echo(repaired, entry_point)
                        repaired = inject_required_imports(repaired, code_prompt)
                        repaired = inject_required_preamble(repaired, code_prompt, entry_point)
                        save_text(ad / "code_repaired.py", repaired)
                        if repaired:
                            code = repaired
                            save_text(ad / "code.py", code)
                            syn = syntax_error_summary(code)
                    except Exception as e:
                        save_text(ad / "syntax_repair_error.txt", str(e))
                    if syn:
                        res = EvalResult(
                            ok=False, score=0.0, rc=1, stdout="", stderr=syn, elapsed_s=0.0,
                            failure_summary=syn,
                        )
                    else:
                        res = run_tests(code, test, entry_point, test_timeout_s, ad)
                else:
                    res = run_tests(code, test, entry_point, test_timeout_s, ad)
        except subprocess.TimeoutExpired:
            save_text(ad / "slm_raw.txt", "")
            save_text(ad / "code.py", "")
            res = EvalResult(
                ok=False, score=0.0, rc=124, stdout="", stderr="SLM_TIMEOUT", elapsed_s=0.0,
                failure_summary="SLM_TIMEOUT",
            )
        except Exception as e:
            msg = str(e).strip() or repr(e)
            save_text(ad / "slm_raw.txt", "")
            save_text(ad / "code.py", "")
            save_text(ad / "slm_error.txt", msg)
            res = EvalResult(
                ok=False, score=0.0, rc=1, stdout="", stderr=msg, elapsed_s=0.0,
                failure_summary=f"SLM_ERROR: {msg}",
            )
        except subprocess.TimeoutExpired:
            save_text(ad / "slm_raw.txt", "")
            save_text(ad / "code.py", "")
            res = EvalResult(
                ok=False, score=0.0, rc=124, stdout="", stderr="SLM_TIMEOUT", elapsed_s=0.0,
                failure_summary="SLM_TIMEOUT",
            )
        except Exception as e:
            msg = str(e).strip() or repr(e)
            save_text(ad / "slm_raw.txt", "")
            save_text(ad / "code.py", "")
            save_text(ad / "slm_error.txt", msg)
            res = EvalResult(
                ok=False, score=0.0, rc=1, stdout="", stderr=msg, elapsed_s=0.0,
                failure_summary=f"SLM_ERROR: {msg}",
            )

        save_text(ad / "test_stdout.txt", res.stdout)
        save_text(ad / "test_stderr.txt", res.stderr)
        save_text(ad / "result.json", json.dumps(res.__dict__, indent=2))

        slm_failures.append(f"attempt_{k:02d}: {res.failure_summary}")

        if slm_best is None or res.score > slm_best["score"]:
            slm_best = {"score": res.score, "ok": res.ok, "code": code, "dir": str(ad), "res": res.__dict__}

        action, reason = router.decide(res.score, pass_threshold, slm_attempts - k, fallback_attempts)
        if action == "ACCEPT":
            save_text(run_dir / "final_status.json", json.dumps({
                "status": "PASS",
                "model": "SLM",
                "attempt": k,
                "reason": reason,
                "score": res.score,
            }, indent=2))
            return {"status": "PASS", "model": "SLM", "attempt": k, "run_dir": str(run_dir)}

    # Fallback attempts
    if fallback_attempts > 0:
        for k in range(1, fallback_attempts + 1):
            fd = run_dir / f"fallback_attempt_{k:02d}"
            fd.mkdir(exist_ok=True)
            fb_prompt = build_prompt(prompt, entry_point, slm_failures + fallback_failures)
            save_text(fd / "prompt.txt", fb_prompt)

            try:
                raw, _meta = openai_chat_completion_codegen(
                    fb_prompt,
                    model=fallback_model,
                    temperature=fallback_temp,
                    max_tokens=fallback_max_tokens,
                    timeout_s=fallback_timeout_s,
                    system_prompt=build_fallback_system_prompt(),
                )
            except Exception as e:
                msg = str(e).strip() or repr(e)
                fallback_failures.append(f"fallback_{k:02d}: ERROR {msg}")
                save_text(fd / "error.txt", msg)
                continue

            save_text(fd / "llm_raw.txt", raw)
            code = trim_to_entry_point(clean_code_blob(extract_code(raw)), entry_point)
            code = inject_required_imports(code, code_prompt)
            code = inject_required_preamble(code, code_prompt, entry_point)
            save_text(fd / "code.py", code)

            if not code:
                res = EvalResult(
                    ok=False, score=0.0, rc=1, stdout="", stderr="NO_CODE", elapsed_s=0.0,
                    failure_summary="NO_CODE_EXTRACTED",
                )
            else:
                syn = syntax_error_summary(code)
                if syn:
                    repair_prompt = build_syntax_repair_prompt(code, entry_point, code_prompt, syn)
                    save_text(fd / "syntax_repair_prompt.txt", repair_prompt)
                    try:
                        raw_fix, _meta_fix = openai_chat_completion_codegen(
                            repair_prompt,
                            model=fallback_model,
                            temperature=fallback_temp,
                            max_tokens=fallback_max_tokens,
                            timeout_s=fallback_timeout_s,
                            system_prompt=build_fallback_system_prompt(),
                        )
                        save_text(fd / "llm_syntax_repair_raw.txt", raw_fix)
                        repaired = trim_to_entry_point(clean_code_blob(extract_code(raw_fix)), entry_point)
                        repaired = inject_required_imports(repaired, code_prompt)
                        repaired = inject_required_preamble(repaired, code_prompt, entry_point)
                        save_text(fd / "code_repaired.py", repaired)
                        if repaired:
                            code = repaired
                            save_text(fd / "code.py", code)
                            syn = syntax_error_summary(code)
                    except Exception as e:
                        save_text(fd / "syntax_repair_error.txt", str(e))
                    if syn:
                        res = EvalResult(
                            ok=False, score=0.0, rc=1, stdout="", stderr=syn, elapsed_s=0.0,
                            failure_summary=syn,
                        )
                    else:
                        res = run_tests(code, test, entry_point, test_timeout_s, fd)
                else:
                    res = run_tests(code, test, entry_point, test_timeout_s, fd)

            save_text(fd / "test_stdout.txt", res.stdout)
            save_text(fd / "test_stderr.txt", res.stderr)
            save_text(fd / "result.json", json.dumps(res.__dict__, indent=2))

            fallback_failures.append(f"fallback_{k:02d}: {res.failure_summary}")

            if res.score >= pass_threshold:
                save_text(run_dir / "final_status.json", json.dumps({
                    "status": "PASS",
                    "model": "LLM",
                    "attempt": k,
                    "score": res.score,
                }, indent=2))
                return {"status": "PASS", "model": "LLM", "attempt": k, "run_dir": str(run_dir)}

    # If none passed
    save_text(run_dir / "final_status.json", json.dumps({
        "status": "FAIL",
        "best_slm": slm_best,
        "slm_failures": slm_failures,
        "fallback_failures": fallback_failures,
    }, indent=2))
    return {"status": "FAIL", "model": "NONE", "run_dir": str(run_dir)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_path", default="data/external/bcb/bigcodebench_subset.jsonl")
    ap.add_argument("--task_index", type=int, default=-1)
    ap.add_argument("--task_id", default="")
    ap.add_argument("--max_tasks", type=int, default=-1)

    ap.add_argument("--llama_path", default=os.environ.get("LLAMA_COMPLETION", "/usr/local/bin/llama-completion"))
    ap.add_argument("--gguf_model_path", default="models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf")
    ap.add_argument("--max_new_tokens", type=int, default=1024)
    ap.add_argument("--slm_timeout_s", type=int, default=120)
    ap.add_argument("--slm_attempts", type=int, default=2)

    ap.add_argument("--test_timeout_s", type=int, default=10)
    ap.add_argument("--pass_threshold", type=float, default=1.0)

    ap.add_argument("--fallback_attempts", type=int, default=1)
    ap.add_argument("--fallback_model", default="gpt-4.2")
    ap.add_argument("--fallback_timeout_s", type=int, default=120)
    ap.add_argument("--fallback_max_tokens", type=int, default=1024)
    ap.add_argument("--fallback_temp", type=float, default=0.0)

    ap.add_argument("--out_dir", default="episodes/bigcodebench_runs")

    args = ap.parse_args()

    os.chdir(REPO_ROOT)

    tasks = load_tasks(Path(args.tasks_path))

    # select tasks
    if args.task_id:
        tasks = [t for t in tasks if t.get("task_id") == args.task_id]
    elif args.task_index >= 0:
        if args.task_index >= len(tasks):
            raise IndexError(f"task_index {args.task_index} out of range (n={len(tasks)})")
        tasks = [tasks[args.task_index]]

    if args.max_tasks > 0:
        tasks = tasks[: args.max_tasks]

    if not tasks:
        print("No tasks selected.")
        return 2

    slm_cfg = SLMConfig(
        timeout_s=args.slm_timeout_s,
        llama_cli=args.llama_path,
        model_path=args.gguf_model_path,
        n_tokens=args.max_new_tokens,
    )

    out_base = Path(args.out_dir)
    out_base.mkdir(parents=True, exist_ok=True)

    summary_path = out_base / "runs_summary.jsonl"
    with summary_path.open("a", encoding="utf-8") as sf:
        for task in tasks:
            res = run_task(
                task=task,
                slm_cfg=slm_cfg,
                slm_attempts=args.slm_attempts,
                fallback_attempts=args.fallback_attempts,
                pass_threshold=args.pass_threshold,
                test_timeout_s=args.test_timeout_s,
                out_base=out_base,
                fallback_model=args.fallback_model,
                fallback_timeout_s=args.fallback_timeout_s,
                fallback_max_tokens=args.fallback_max_tokens,
                fallback_temp=args.fallback_temp,
            )
            sf.write(json.dumps(res) + "\n")
            sf.flush()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
