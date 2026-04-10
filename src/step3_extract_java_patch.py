from __future__ import annotations

python src/step6_orchestrator_run_v4_slm.py \
  --tasks_path data/defects4j_tasks.jsonl \
  --task_index 0 \
  --tests_mode failing_only \
  --rag_k 12 \
  --rag_query "AbstractCategoryItemRenderer getLegendItems getLegendItem LegendItemCollection CategoryPlot test2947660" \
  --llama_cli_path "/usr/local/bin/llama-cli" \
  --gguf_model_path "models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf" \
  --slm_timeout_s 900 \
  --max_new_tokens 220


import argparse
import subprocess
from pathlib import Path
from typing import List

JAVA_EXTS = {".java"}

def list_java_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in JAVA_EXTS:
            files.append(p)
    return files

def relpath(base: Path, p: Path) -> str:
    return str(p.relative_to(base)).replace("\\", "/")

def run_diff_file(buggy_file: Path, fixed_file: Path) -> str:
    """
    Return unified diff (-u) for two files.
    If file doesn't exist in one side, still diff properly.
    """
    cmd = ["diff", "-u", str(buggy_file), str(fixed_file)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # diff returns exit code 1 when differences exist; that's normal.
    out = p.stdout.decode("utf-8", errors="ignore")
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--buggy", required=True, help="Buggy checkout dir (e.g., Chart-1b)")
    ap.add_argument("--fixed", required=True, help="Fixed checkout dir (e.g., Chart-1f)")
    ap.add_argument("--out", required=True, help="Output diff file path")
    args = ap.parse_args()

    buggy = Path(args.buggy).resolve()
    fixed = Path(args.fixed).resolve()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if not buggy.exists():
        raise FileNotFoundError(f"Buggy dir not found: {buggy}")
    if not fixed.exists():
        raise FileNotFoundError(f"Fixed dir not found: {fixed}")

    buggy_java = {relpath(buggy, p): p for p in list_java_files(buggy)}
    fixed_java = {relpath(fixed, p): p for p in list_java_files(fixed)}

    all_rel = sorted(set(buggy_java.keys()) | set(fixed_java.keys()))

    chunks: List[str] = []
    chunks.append(f"# Java-only patch\n")
    chunks.append(f"# buggy: {buggy}\n")
    chunks.append(f"# fixed: {fixed}\n\n")

    changed_files = 0

    for r in all_rel:
        b = buggy_java.get(r)
        f = fixed_java.get(r)

        # If file exists only on one side, diff should still work by using /dev/null trick
        if b is None and f is not None:
            # file added in fixed
            diff_txt = run_diff_file(Path("/dev/null"), f)
        elif f is None and b is not None:
            # file removed in fixed
            diff_txt = run_diff_file(b, Path("/dev/null"))
        else:
            # both exist
            diff_txt = run_diff_file(b, f)

        # Only keep if it actually contains a diff header
        if diff_txt.strip() and ("--- " in diff_txt and "+++ " in diff_txt):
            changed_files += 1
            chunks.append(diff_txt)
            if not diff_txt.endswith("\n"):
                chunks.append("\n")

    if changed_files == 0:
        chunks.append("# No Java source differences detected.\n")

    out.write_text("".join(chunks), encoding="utf-8")
    print(f"Saved Java-only patch to: {out}")
    print(f"Changed Java files: {changed_files}")
    print(f"Size: {out.stat().st_size} bytes")

if __name__ == "__main__":
    main()
