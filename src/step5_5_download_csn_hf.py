from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from datasets import load_dataset


OUT_DEFAULT = Path("data_raw/codesearchnet/csn_java_python.parquet")


def norm_str(x):
    if x is None:
        return ""
    return str(x)


def pick_cols(ex: dict, language: str) -> dict:
    """
    CodeSearchNet schema varies slightly across variants.
    We normalize into the fields our pipeline expects:
      language, repo, path, func_name, docstring, code
    """
    # Common CodeSearchNet keys include:
    # - "repository_name" or "repo"
    # - "path"
    # - "func_name"
    # - "docstring"
    # - "code"
    repo = ex.get("repository_name", ex.get("repo", ""))
    return {
        "language": language,
        "repo": norm_str(repo),
        "path": norm_str(ex.get("path", "")),
        "func_name": norm_str(ex.get("func_name", "")),
        "docstring": norm_str(ex.get("docstring", "")),
        "code": norm_str(ex.get("code", "")),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--split", default="train", choices=["train", "validation", "test"])
    ap.add_argument("--max_rows_per_lang", type=int, default=0, help="0 = all rows")
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for lang in ["java", "python"]:
        ds = load_dataset("code_search_net", lang, split=args.split)

        if args.max_rows_per_lang and args.max_rows_per_lang > 0:
            ds = ds.select(range(min(args.max_rows_per_lang, len(ds))))

        for ex in ds:
            rows.append(pick_cols(ex, lang))

        print(f"Loaded {lang} split={args.split} rows:", len(ds))

    df = pd.DataFrame(rows)

    # Basic cleanup
    df["docstring"] = df["docstring"].fillna("")
    df["code"] = df["code"].fillna("")
    df = df[df["code"].astype(str).str.len() > 0].copy()

    df.to_parquet(out_path, index=False)
    print("✅ Wrote:", out_path)
    print("Rows:", len(df))
    print(df["language"].value_counts().to_string())


if __name__ == "__main__":
    main()
