from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass
class SLMConfig:
    # how long we allow llama-cli to run (seconds)
    timeout_s: int = 900

    llama_cli: str = "llama-cli"
    model_path: str = "models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"

    # keep this low initially to avoid slow / hanging runs
    n_tokens: int = 160

    seed: int = 42
    temp: float = 0.2
    top_p: float = 0.95
    repeat_penalty: float = 1.05


def run_llama_prompt(prompt: str, cfg: SLMConfig, timeout_s: int | None = None) -> str:
    # IMPORTANT:
    # Do NOT use --simple-io here. It makes llama-cli go into interactive mode and it won't exit,
    # which is why your Python subprocess kept timing out.
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

    p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout_s, stdin=subprocess.DEVNULL)

    # dump last run for debugging
    try:
        with open("/tmp/slm_last_run.txt", "w", encoding="utf-8") as f:
            f.write(
                f"RET={p.returncode}\n"
                f"STDOUT:\n{p.stdout or ''}\n"
                f"STDERR:\n{p.stderr or ''}\n"
            )
    except Exception:
        pass

    # Some llama-cli builds log stuff to stderr; return both.
    return ((p.stdout or "") + ("\n" if (p.stdout and p.stderr) else "") + (p.stderr or "")).strip()


def build_patch_prompt(task_id: str, failing_info: str, rag_context: str) -> str:
    return f"""You are a software repair assistant.

Task: {task_id}

Failing information:
{failing_info}

Relevant code context:
{rag_context}

Return ONLY a unified diff.
Do not include explanations or markdown.
"""
