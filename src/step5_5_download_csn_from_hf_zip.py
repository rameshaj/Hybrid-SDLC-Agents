from __future__ import annotations

import argparse
import gzip
import json
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd
from huggingface_hub import hf_hub_download

REPO_ID = "code_search_net"

ZIP_FILES = {
    "java": "data/java.zip",
    "python": "data/python.zip",
}

EXTRACT_ROOT = Path("data_raw/codesearchnet/hf_extract")
OUT_DIR = Path("data_raw/codesearchnet")


def read_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def read_jsonl_gz(path: Path) -> Iterable[dict]:
    with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def normalize_record(r: dict) -> Dict[str, str]:
    """
    Best-effort mapping to:
      repository_name, path, func_name, docstring, code
    """
    return {
        "repository_name": r.get("repository_name", r.get("repo", r.get("repo_name", ""))) or "",
        "path": r.get("path", r.get("file", "")) or "",
        "func_name": r.get("func_name", r.get("function_name", r.get("name", ""))) or "",
        "docstring": r.get("docstring", r.get("doc", "")) or "",
        "code": r.get("code", r.get("func_code_string", "")) or "",
    }


def find_split_files(extract_dir: Path, split: str) -> List[Path]:
    """
    Search for split files in extracted CodeSearchNet zip.

    In CodeSearchNet zips, split data is often stored as:
      - *.jsonl.gz  (most common)
      - *.jsonl
    and split indicators may appear in directory names, not just filenames.
    So we match split names against the *full relative path*.
    """
    split_aliases = {
        "train": ["train", "training"],
        "validation": ["valid", "validation", "dev", "val"],
        "test": ["test"],
    }[split]

    # Collect jsonl/jsonl.gz
    candidates: List[Path] = []
    for p in extract_dir.rglob("*"):
        if not p.is_file():
            continue
        name = p.name.lower()
        if not (name.endswith(".jsonl") or name.endswith(".jsonl.gz")):
            continue

        rel = str(p.relative_to(extract_dir)).lower()
        if any(a in rel for a in split_aliases):
            candidates.append(p)

    return sorted(candidates)


def load_split_into_df(paths: List[Path], lang: str, max_rows: int) -> pd.DataFrame:
    rows = []
    total = 0

    for jp in paths:
        if jp.name.lower().endswith(".jsonl.gz"):
            it = read_jsonl_gz(jp)
        else:
            it = read_jsonl(jp)

        for r in it:
            nr = normalize_record(r)
            code = str(nr["code"] or "")
            if not code.strip():
                continue

            rows.append(
                {
                    "language": lang,
                    "repo": str(nr["repository_name"]),
                    "path": str(nr["path"]),
                    "func_name": str(nr["func_name"]),
                    "docstring": str(nr["docstring"] or ""),
                    "code": code,
                }
            )
            total += 1
            if max_rows > 0 and total >= max_rows:
                return pd.DataFrame(rows)

    return pd.DataFrame(rows)


def ensure_extracted(lang: str, force: bool = False) -> Path:
    zip_name = ZIP_FILES[lang]
    EXTRACT_ROOT.mkdir(parents=True, exist_ok=True)
    out_dir = EXTRACT_ROOT / lang

    if out_dir.exists() and any(out_dir.iterdir()) and not force:
        return out_dir

    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {zip_name} from HF ({REPO_ID}) ...")
    zip_path = hf_hub_download(repo_id=REPO_ID, filename=zip_name, repo_type="dataset")
    zip_path = Path(zip_path)

    print(f"Extracting {zip_path.name} -> {out_dir} ...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir)

    return out_dir


def debug_preview(exdir: Path, max_items: int = 80) -> None:
    print("\n=== DEBUG PREVIEW (first files) ===")
    shown = 0
    for p in exdir.rglob("*"):
        if p.is_file():
            print(" -", p.relative_to(exdir))
            shown += 1
            if shown >= max_items:
                break


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="train", choices=["train", "validation", "test"])
    ap.add_argument("--max_rows_per_lang", type=int, default=2000, help="0 = all rows (huge). Start small.")
    ap.add_argument("--force_extract", action="store_true", help="Re-extract even if folder exists.")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"csn_java_python_{args.split}.parquet"

    frames = []
    for lang in ["java", "python"]:
        exdir = ensure_extracted(lang, force=args.force_extract)

        split_files = find_split_files(exdir, args.split)
        if not split_files:
            print(f"\n!! Could not find split files for lang={lang} split={args.split}")
            print("Top-level extracted entries:")
            for p in list(exdir.glob("*"))[:30]:
                print(" -", p.name)
            debug_preview(exdir)
            raise SystemExit(2)

        print(f"\n{lang} {args.split}: found {len(split_files)} file(s)")
        for p in split_files[:10]:
            print("  -", p.relative_to(exdir))

        df_lang = load_split_into_df(split_files, lang, args.max_rows_per_lang)
        print(f"{lang} loaded rows:", len(df_lang))
        frames.append(df_lang)

    merged = pd.concat(frames, ignore_index=True)
    merged.to_parquet(out_path, index=False)

    print("\n✅ Wrote:", out_path)
    print("Rows:", len(merged))
    print(merged["language"].value_counts().to_string())
    print("Columns:", list(merged.columns))


if __name__ == "__main__":
    main()
