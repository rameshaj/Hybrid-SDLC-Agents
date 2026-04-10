#!/usr/bin/env python3
"""
BigCodeBench hybrid runner v2: SLM first, fallback to LLM if needed.
Adds optional RAG hints from FAISS cases.
"""

from __future__ import annotations

import argparse
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
from src.core.retriever_rag_cases_v2 import RagCaseRetriever
from src.llm_fallback_openai_codegen import openai_chat_completion_codegen

RAG_INDEX_PATH = Path("data/derived/rag/cases.index.faiss")
RAG_META_PATH = Path("data/derived/rag/cases.meta.jsonl")
_RAG_RETRIEVER: Optional[RagCaseRetriever] = None
_RAG_ERROR: Optional[str] = None


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
        if s.startswith(("- ", "* ", "• ")):
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


def classify_error(summary: str) -> str:
    if not summary:
        return "UNKNOWN"
    for key in [
        "SLM_TIMEOUT",
        "TIMEOUT",
        "NameError",
        "AssertionError",
        "SyntaxError",
        "IndentationError",
        "TypeError",
        "ValueError",
        "IndexError",
        "KeyError",
        "UnboundLocalError",
        "ModuleNotFoundError",
        "NO_CODE_EXTRACTED",
    ]:
        if key in summary:
            return key
    return "OTHER"


def build_rag_query(task_prompt: str, entry_point: str, failure_summary: str) -> str:
    failure_type = classify_error(failure_summary)
    parts = [
        f"entry_point: {entry_point}",
        f"error_type: {failure_type}",
        f"error_summary: {failure_summary}",
        "prompt:",
        task_prompt.strip(),
    ]
    return "\n".join([p for p in parts if p]).strip() + "\n"


def truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def extract_added_imports(diff_text: str) -> List[str]:
    imports: List[str] = []
    for line in diff_text.splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        if line.startswith("+import ") or line.startswith("+from "):
            imports.append(line[1:].strip())
    return imports


def format_rag_context(hits: List[Dict[str, Any]], max_chars: int = 1200) -> str:
    if not hits:
        return ""
    lines: List[str] = ["RAG hints from similar cases:"]
    for i, h in enumerate(hits, start=1):
        task_id = h.get("task_id", "")
        err = h.get("slm_failure_type", "")
        fix_actions = h.get("fix_actions", [])
        score = h.get("score", 0.0)
        lines.append(f"[case {i}] task_id={task_id} error={err} fix_actions={fix_actions} score={score:.3f}")
        diff = (h.get("fix_diff") or "").strip()
        added_imports = extract_added_imports(diff)
        if added_imports:
            lines.append("import_hints: " + ", ".join(added_imports))
        if diff:
            lines.append("fix_diff:")
            lines.append(truncate_text(diff, 600))
    return truncate_text("\n".join(lines), max_chars)


def get_rag_retriever() -> Optional[RagCaseRetriever]:
    global _RAG_RETRIEVER, _RAG_ERROR
    if _RAG_ERROR:
        return None
    if _RAG_RETRIEVER is None:
        if not RAG_INDEX_PATH.exists() or not RAG_META_PATH.exists():
            _RAG_ERROR = "missing_rag_index_or_meta"
            return None
        retriever = RagCaseRetriever(index_path=RAG_INDEX_PATH, meta_path=RAG_META_PATH)
        retriever.load()
        _RAG_RETRIEVER = retriever
    return _RAG_RETRIEVER


def build_rag_context(
    task_prompt: str,
    entry_point: str,
    failure_summary: str,
    rag_top_k: int,
    attempt_dir: Path,
) -> str:
    retriever = get_rag_retriever()
    query = build_rag_query(task_prompt, entry_point, failure_summary)
    save_text(attempt_dir / "rag_query.txt", query)
    if retriever is None:
        save_text(attempt_dir / "rag_error.txt", _RAG_ERROR or "rag_unavailable")
        return ""
    try:
        hits = retriever.retrieve(query, k=rag_top_k)
    except Exception as e:
        save_text(attempt_dir / "rag_error.txt", str(e))
        return ""
    save_text(attempt_dir / "rag_hits.json", json.dumps(hits, indent=2))
    return format_rag_context(hits)


def build_prompt(
    task_prompt: str,
    entry_point: str,
    prev_failures: List[str],
    rag_context: str,
    self_debug_notes: str,
) -> str:
    header = (
        "You are a coding assistant.\n"
        "Complete the function below.\n"
        "Return ONLY valid Python code. No explanations, no markdown.\n"
        "Do NOT include tests or example usage.\n"
        "Self-debug notes are hints only. Do NOT copy them into the code.\n"
        f"Function name: {entry_point}\n"
        "Return the full code including all provided imports and the function definition.\n"
        "Do not remove or rename any provided imports or the function signature.\n"
        "Use the provided stub and fill in the function body.\n"
    )
    if prev_failures:
        header += "Previous failures:\n"
        for item in prev_failures:
            header += f"- {item}\n"
    if self_debug_notes:
        header += "Self-debug notes:\n"
        header += self_debug_notes.strip() + "\n"
    if rag_context:
        header += "RAG hints:\n"
        header += rag_context + "\n"
    return header + "\n" + task_prompt.strip() + "\n"


def build_fallback_system_prompt() -> str:
    return (
        "You are a coding assistant. "
        "Return ONLY valid Python code for the function. "
        "No explanations, no markdown."
    )


def build_self_debug_prompt(
    task_prompt: str,
    entry_point: str,
    code: str,
    failure_summary: str,
    max_code_chars: int = 1200,
) -> str:
    code_block = truncate_text(code.strip(), max_code_chars) if code else ""
    return (
        "You are a debugging assistant.\n"
        "Given the task and failing code, propose minimal fixes.\n"
        "Return 1-3 short bullet points, each starting with '- '. No code.\n"
        f"Function name: {entry_point}\n"
        "Task:\n"
        f"{task_prompt.strip()}\n\n"
        "Failed code:\n"
        f"{code_block}\n\n"
        "Failure:\n"
        f"{failure_summary}\n"
    )


def clean_self_debug_notes(text: str) -> str:
    if not text:
        return ""
    cleaned: List[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("---"):
            continue
        if s.startswith("```"):
            continue
        if s.startswith("assistant") or s.startswith("user"):
            continue
        if s.startswith(("-", "*", "•")):
            item = s.lstrip("-*•").strip()
            if item:
                cleaned.append(f"- {item}")
    return "\n".join(cleaned[:3]).strip()


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
        "def __run_tests():\n"
        f"    check(globals().get('{entry_point}'))\n\n"
        "if __name__ == '__main__':\n"
        "    __run_tests()\n"
    )


def run_tests(code: str, test: str, entry_point: str, timeout_s: int, work_dir: Path) -> EvalResult:
    tmp_path = work_dir / "candidate_run.py"
    tmp_path.write_text(build_test_file(code, test, entry_point), encoding="utf-8")

    start = time.time()
    timed_out = False
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
        stdout = e.stdout or ""
        stderr = (e.stderr or "") + "\n[TIMEOUT]\n"

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
    rag_enabled: bool,
    rag_top_k: int,
    self_debug_enabled: bool,
    self_debug_max_tokens: int,
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
    rag_context = ""
    self_debug_notes = ""

    # SLM attempts
    slm_best: Optional[Dict[str, Any]] = None
    for k in range(1, slm_attempts + 1):
        ad = run_dir / f"slm_attempt_{k:02d}"
        ad.mkdir(exist_ok=True)
        attempt_prompt = build_prompt(prompt, entry_point, slm_failures, rag_context, self_debug_notes)
        save_text(ad / "prompt.txt", attempt_prompt)

        code = ""
        try:
            raw = run_slm_prompt(attempt_prompt, slm_cfg, timeout_s=slm_cfg.timeout_s)
            save_text(ad / "slm_raw.txt", raw)

            code = clean_code_blob(extract_code(raw))
            code = trim_prompt_echo(code, entry_point)
            code = inject_required_imports(code, code_prompt)
            save_text(ad / "code.py", code)

            if not code:
                res = EvalResult(
                    ok=False, score=0.0, rc=1, stdout="", stderr="NO_CODE", elapsed_s=0.0,
                    failure_summary="NO_CODE_EXTRACTED",
                )
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

        save_text(ad / "test_stdout.txt", res.stdout)
        save_text(ad / "test_stderr.txt", res.stderr)
        save_text(ad / "result.json", json.dumps(res.__dict__, indent=2))

        slm_failures.append(f"attempt_{k:02d}: {res.failure_summary}")
        if self_debug_enabled and res.score < pass_threshold and code:
            debug_cfg = SLMConfig(
                timeout_s=slm_cfg.timeout_s,
                llama_cli=slm_cfg.llama_cli,
                model_path=slm_cfg.model_path,
                n_tokens=self_debug_max_tokens,
                seed=slm_cfg.seed,
                temp=slm_cfg.temp,
                top_p=slm_cfg.top_p,
                repeat_penalty=slm_cfg.repeat_penalty,
            )
            debug_prompt = build_self_debug_prompt(prompt, entry_point, code, res.failure_summary)
            save_text(ad / "self_debug_prompt.txt", debug_prompt)
            try:
                debug_raw = run_slm_prompt(debug_prompt, debug_cfg, timeout_s=slm_cfg.timeout_s)
                save_text(ad / "self_debug_raw.txt", debug_raw)
                self_debug_notes = clean_self_debug_notes(debug_raw)
                save_text(ad / "self_debug_notes.txt", self_debug_notes)
            except Exception as e:
                save_text(ad / "self_debug_error.txt", str(e))
        if rag_enabled and res.score < pass_threshold:
            rag_context = build_rag_context(prompt, entry_point, res.failure_summary, rag_top_k, ad)
            save_text(ad / "rag_context.txt", rag_context)

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
                "rag_enabled": bool(rag_enabled),
                "rag_top_k": int(rag_top_k),
            }, indent=2))
            return {"status": "PASS", "model": "SLM", "attempt": k, "run_dir": str(run_dir)}

    # Fallback attempts
    if fallback_attempts > 0:
        for k in range(1, fallback_attempts + 1):
            fd = run_dir / f"fallback_attempt_{k:02d}"
            fd.mkdir(exist_ok=True)
            fb_prompt = build_prompt(
                prompt,
                entry_point,
                slm_failures + fallback_failures,
                rag_context,
                self_debug_notes,
            )
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
            save_text(fd / "code.py", code)

            if not code:
                res = EvalResult(
                    ok=False, score=0.0, rc=1, stdout="", stderr="NO_CODE", elapsed_s=0.0,
                    failure_summary="NO_CODE_EXTRACTED",
                )
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
                    "rag_enabled": bool(rag_enabled),
                    "rag_top_k": int(rag_top_k),
                }, indent=2))
                return {"status": "PASS", "model": "LLM", "attempt": k, "run_dir": str(run_dir)}

    # If none passed
    save_text(run_dir / "final_status.json", json.dumps({
        "status": "FAIL",
        "best_slm": slm_best,
        "slm_failures": slm_failures,
        "fallback_failures": fallback_failures,
        "rag_enabled": bool(rag_enabled),
        "rag_top_k": int(rag_top_k),
    }, indent=2))
    return {"status": "FAIL", "model": "NONE", "run_dir": str(run_dir)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks_path", default="data/external/bcb/bigcodebench_subset_stdlib.jsonl")
    ap.add_argument("--task_index", type=int, default=-1)
    ap.add_argument("--task_id", default="")
    ap.add_argument("--max_tasks", type=int, default=-1)

    ap.add_argument("--llama_path", default=os.environ.get("LLAMA_COMPLETION", "/usr/local/bin/llama-completion"))
    ap.add_argument("--gguf_model_path", default="models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf")
    ap.add_argument("--max_new_tokens", type=int, default=256)
    ap.add_argument("--slm_timeout_s", type=int, default=120)
    ap.add_argument("--slm_attempts", type=int, default=2)

    ap.add_argument("--test_timeout_s", type=int, default=10)
    ap.add_argument("--pass_threshold", type=float, default=1.0)

    ap.add_argument("--fallback_attempts", type=int, default=1)
    ap.add_argument("--fallback_model", default="gpt-4.2")
    ap.add_argument("--fallback_timeout_s", type=int, default=120)
    ap.add_argument("--fallback_max_tokens", type=int, default=512)
    ap.add_argument("--fallback_temp", type=float, default=0.0)

    ap.add_argument("--rag_enabled", type=int, default=0)
    ap.add_argument("--rag_top_k", type=int, default=3)
    ap.add_argument("--self_debug_enabled", type=int, default=1)
    ap.add_argument("--self_debug_max_tokens", type=int, default=128)

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
                rag_enabled=bool(args.rag_enabled),
                rag_top_k=args.rag_top_k,
                self_debug_enabled=bool(args.self_debug_enabled),
                self_debug_max_tokens=args.self_debug_max_tokens,
            )
            sf.write(json.dumps(res) + "\n")
            sf.flush()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
