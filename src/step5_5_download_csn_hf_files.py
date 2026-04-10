from __future__ import annotations

import argparse
import gzip
import json
import re
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

REPO_ID = "code_search_net"
OUT_DEFAULT = Path("data_raw/codesearchnet/csn_java_python.parquet")


def list_repo_files(repo_id: str) -> List[str]:
    api = HfApi()
    files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
    return files


def pick_split_files(files: List[str], lang: str, split: str) -> List[str]:
    """
    Pick files for a given language+split.
    We try Parquet first; if none, try jsonl/jsonl.gz.
    """
    # Make split matching more forgiving (e.g. "train", "training")
    split_pat = re.compile(rf"(^|/){re.escape(split)}([._/-]|$)", re.IGNORECASE)
    lang_pat = re.compile(rf"(^|/){re.escape(lang)}([._/-]|$)", re.IGNORECASE)

    parquet = [f for f in files if f.lower().endswith(".parquet") and split_pat.search(f) and lang_pat.search(f)]
    if parquet:
        return sorted(parquet)

    # Fallbacks
    jsonl_gz = [f for f in files if f.lower().endswith(".jsonl.gz") and split_pat.search(f) and lang_pat.search(f)]
    if jsonl_gz:
        return sorted(jsonl_gz)

    jsonl = [f for f in files if f.lower().endswith(".jsonl") and split_pat.search(f) and lang_pat.search(f)]
    if jsonl:
        return sorted(jsonl)

    return []


def hf_download(repo_id: str, filename: str) -> Path:
    p = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
    return Path(p)


def normalize_cols(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    # CodeSearchNet commonly contains: repository_name, path, func_name, docstring, code
    for c in ["repository_name", "path", "func_name", "docstring", "code"]:
        if c not in df.columns:
            df[c] = ""

    out = pd.DataFrame(
        {
            "language": lang,
            "repo": df["repository_name"].astype(str),
            "path": df["path"].astype(str),
            "func_name": df["func_name"].astype(str),
            "docstring": df["docstring"].astype(str).fillna(""),
            "code": df["code"].astype(str).fillna(""),
        }
    )
    out = out[out["code"].str.len() > 0].copy()
    return out


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


def json_records_to_df(records: Iterable[dict]) -> pd.DataFrame:
    # try best-effort mapping
    rows = []
    for r in records:
        rows.append(
            {
                "repository_name": r.get("repository_name", r.get("repo", "")),
                "path": r.get("path", ""),
                "func_name": r.get("func_name", r.get("function_name", "")),
                "docstring": r.get("docstring", r.get("doc", "")),
                "code": r.get("code", r.get("func_code_string", "")),
            }
        )
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="train", choices=["train", "validation", "test"])
    ap.add_argument("--max_files_per_lang", type=int, default=1, help="Start small. 0 = all files for that lang/split.")
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--print_files", action="store_true", help="Print repo file list and exit.")
    args = ap.parse_args()

    files = list_repo_files(REPO_ID)

    if args.print_files:
        print("=== HF DATASET FILES ===")
        for f in files:
            print(f)
        return

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    frames = []

    for lang in ["java", "python"]:
        picked = pick_split_files(files, lang, args.split)
        if not picked:
            raise RuntimeError(
                f"No files found for lang={lang} split={args.split}. "
                f"Run: python -m src.step5_5_download_csn_hf_files --print_files"
            )

        if args.max_files_per_lang > 0:
            picked = picked[: args.max_files_per_lang]

        print(f"\n{lang} {args.split}: using {len(picked)} file(s)")
        for fname in picked:
            print("  -", fname)
            local = hf_download(REPO_ID, fname)

            if fname.lower().endswith(".parquet"):
                df = pd.read_parquet(local)
            elif fname.lower().endswith(".jsonl.gz"):
                df = json_records_to_df(read_jsonl_gz(local))
            elif fname.lower().endswith(".jsonl"):
                df = json_records_to_df(read_jsonl(local))
            else:
                raise RuntimeError(f"Unsupported file type: {fname}")

            frames.append(normalize_cols(df, lang))

    merged = pd.concat(frames, ignore_index=True)
    merged.to_parquet(out_path, index=False)

    print("\n✅ Wrote:", out_path)
    print("Rows:", len(merged))
    print(merged["language"].value_counts().to_string())
    print("Columns:", list(merged.columns))


if __name__ == "__main__":
    main()
