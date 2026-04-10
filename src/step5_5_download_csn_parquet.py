from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import pandas as pd
from huggingface_hub import hf_hub_download


REPO_ID = "code_search_net"
OUT_DEFAULT = Path("data_raw/codesearchnet/csn_java_python.parquet")


# The HF dataset stores each language as a "config".
# For Parquet-based datasets, filenames commonly look like:
#   data/<lang>/<split>-*.parquet  (or similar)
# We will try a small set of known patterns and pick the ones that exist.
CANDIDATE_PATTERNS = [
    "data/{lang}/{split}-00000-of-00001.parquet",
    "data/{lang}/{split}-00000-of-00010.parquet",
    "data/{lang}/{split}-00000-of-00020.parquet",
    "{lang}/{split}-00000-of-00001.parquet",
    "{lang}/{split}-00000-of-00010.parquet",
    "{lang}/{split}-00000-of-00020.parquet",
]


def try_download_one(repo_id: str, filename: str) -> Path | None:
    try:
        p = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
        return Path(p)
    except Exception:
        return None


def discover_shards(repo_id: str, lang: str, split: str, max_shards: int) -> List[Path]:
    """
    Discover shard files by attempting common naming conventions.
    Once we find a 'of-N' template that works, we download shards 0..N-1 (capped by max_shards).
    """
    # Find a working "template"
    found = None
    total = None

    for pat in CANDIDATE_PATTERNS:
        filename0 = pat.format(lang=lang, split=split)
        p0 = try_download_one(repo_id, filename0)
        if p0 is None:
            continue

        # Parse total from "...of-00020.parquet" etc
        s = filename0
        m = __import__("re").search(r"of-(\d+)\.parquet$", s)
        if not m:
            # single-file
            found = pat
            total = 1
            return [p0]

        total = int(m.group(1))
        found = pat
        break

    if found is None:
        raise RuntimeError(
            f"Could not discover parquet shard naming for lang={lang} split={split}. "
            f"Try using Option 2 (official CodeSearchNet release)."
        )

    # Download shards
    out = []
    n = min(total, max_shards) if max_shards > 0 else total

    for i in range(n):
        # Replace the shard number
        # We assume 5-digit shard numbers in filenames: 00000
        fname = found.format(lang=lang, split=split).replace("00000", f"{i:05d}")
        p = try_download_one(repo_id, fname)
        if p is None:
            # stop early if naming differs
            break
        out.append(p)

    if not out:
        raise RuntimeError(f"Discovered template but downloaded 0 shards for {lang} {split}")
    return out


def normalize_cols(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    # Normalize to fields we expect downstream
    # CodeSearchNet parquet typically includes: repository_name, path, func_name, docstring, code
    for c in ["repository_name", "path", "func_name", "docstring", "code"]:
        if c not in df.columns:
            df[c] = ""
    out = pd.DataFrame(
        {
            "language": lang,
            "repo": df["repository_name"].astype(str),
            "path": df["path"].astype(str),
            "func_name": df["func_name"].astype(str),
            "docstring": df["docstring"].astype(str),
            "code": df["code"].astype(str),
        }
    )
    out["docstring"] = out["docstring"].fillna("")
    out["code"] = out["code"].fillna("")
    out = out[out["code"].str.len() > 0].copy()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="train", choices=["train", "validation", "test"])
    ap.add_argument("--max_shards_per_lang", type=int, default=1, help="Start small. 0 = all shards.")
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    frames = []
    for lang in ["java", "python"]:
        shards = discover_shards(REPO_ID, lang, args.split, args.max_shards_per_lang)
        print(f"{lang} {args.split}: shards downloaded:", len(shards))

        # Read and normalize
        for sp in shards:
            df = pd.read_parquet(sp)
            frames.append(normalize_cols(df, lang))

    merged = pd.concat(frames, ignore_index=True)
    merged.to_parquet(out_path, index=False)

    print("✅ Wrote:", out_path)
    print("Rows:", len(merged))
    print(merged["language"].value_counts().to_string())
    print("Columns:", list(merged.columns))


if __name__ == "__main__":
    main()
