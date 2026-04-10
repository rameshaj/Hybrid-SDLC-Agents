from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List
import re


@dataclass
class PatchGenResult:
    ok: bool
    diff: Optional[str] = None
    raw_text: Optional[str] = None
    prompt_used: Optional[str] = None
    error: Optional[str] = None


def _strip_code_fences(text: str) -> str:
    if not text:
        return ""
    # Remove triple backticks fences if model emits them
    text = text.replace("```diff", "```").replace("```patch", "```")
    # If multiple fenced blocks exist, just drop fence markers
    text = text.replace("```", "")
    return text


def _extract_first_unified_diff(raw: str) -> Optional[str]:
    """
    Extract the first unified diff starting at 'diff --git'.
    Stops when:
      - another REPL-like prompt starts (line beginning with '>') AFTER diff started
      - or end of text

    We keep it simple and robust against llama-cli REPL output.
    """
    if not raw:
        return None

    raw2 = _strip_code_fences(raw)

    lines = raw2.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("diff --git "):
            start = i
            break
    if start is None:
        return None

    out: List[str] = []
    saw_diff = False
    for j in range(start, len(lines)):
        line = lines[j]

        # If llama REPL prints a new prompt after diff, stop
        if saw_diff and line.lstrip().startswith(">"):
            break

        if line.startswith("diff --git "):
            saw_diff = True

        out.append(line)

    diff_text = "\n".join(out).strip()
    return diff_text if diff_text.startswith("diff --git ") else None


def _touched_files_from_diff(diff_text: str) -> List[str]:
    """
    Parse file paths from 'diff --git a/... b/...'
    Return b-paths without the leading 'b/'.
    """
    touched: List[str] = []
    if not diff_text:
        return touched

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            # diff --git a/path b/path
            parts = line.split()
            if len(parts) >= 4:
                bpath = parts[3]
                if bpath.startswith("b/"):
                    bpath = bpath[2:]
                touched.append(bpath)
    # unique preserve order
    seen = set()
    out = []
    for f in touched:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def _validate_diff_policy(diff_text: str) -> Optional[str]:
    """
    Strict policy for our Step 6.2:
      - MUST touch exactly ONE file
      - file MUST be under source/ and must end with .java
    """
    touched = _touched_files_from_diff(diff_text)
    if len(touched) == 0:
        return "no_files_in_diff"
    if len(touched) != 1:
        return f"policy_violation: expected 1 file, got {len(touched)}: {touched}"

    f = touched[0]
    if not f.startswith("source/"):
        return f"policy_violation: file not under source/: {f}"
    if not f.endswith(".java"):
        return f"policy_violation: file not .java: {f}"
    return None


def generate_patch_with_slm(
    llm_client,
    task_id: str,
    failing_test_output: str,
    rag_snippets: str,
    repo_hint: str,
    max_new_tokens: int = 250,
) -> PatchGenResult:
    """
    llm_client must expose: generate(prompt: str, max_new_tokens: int) -> str
    """
    # IMPORTANT:
    # keep prompt short-ish but strict; 1.5B model needs tight constraints.
    prompt = f"""You are a coding patch generator.

{repo_hint}

RULES (MUST FOLLOW):
1) Output ONLY a valid unified diff (git style).
2) The diff MUST start with: diff --git
3) Modify ONLY ONE file.
4) The file MUST be under source/ and end with .java
5) Do NOT include markdown fences, no explanations.

TASK: {task_id}

FAILING TEST OUTPUT:
{failing_test_output}

LOCAL CONTEXT (RAG HITS):
{rag_snippets}

Now output the unified diff:
"""

    try:
        raw = llm_client.generate(prompt, max_new_tokens=max_new_tokens)
    except Exception as e:
        return PatchGenResult(ok=False, error=f"slm_generate_exception: {e}", prompt_used=prompt)

    diff = _extract_first_unified_diff(raw)
    if not diff:
        # helpful debug hint: show if model refused
        refused = "I can't assist" in (raw or "")
        hint = "model_refused" if refused else "no_diff_found"
        return PatchGenResult(
            ok=False,
            error=hint,
            raw_text=raw,
            prompt_used=prompt,
        )

    # Remove any weird control chars
    diff = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", diff)

    policy_err = _validate_diff_policy(diff)
    if policy_err:
        return PatchGenResult(
            ok=False,
            error=policy_err,
            diff=diff,
            raw_text=raw,
            prompt_used=prompt,
        )

    return PatchGenResult(
        ok=True,
        diff=diff,
        raw_text=raw,
        prompt_used=prompt,
        error=None,
    )
