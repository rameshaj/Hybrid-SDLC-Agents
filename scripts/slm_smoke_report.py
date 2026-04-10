import json
import os
from datetime import datetime, timezone
from pathlib import Path
import hashlib

MODEL = "models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"

FILES = {
    "basic_raw": "reports/slm_smoke_basic.raw.txt",
    "basic_stderr": "reports/slm_smoke_basic.stderr.txt",
    "basic_answer": "reports/slm_smoke_basic.answer.clean.txt",
    "patch_raw": "reports/slm_smoke_patch.raw.txt",
    "patch_stderr": "reports/slm_smoke_patch.stderr.txt",
    "patch_diff": "reports/slm_smoke_patch.answer.clean.diff",
}

def sha256(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()

def stats(path: str):
    p = Path(path)
    if not p.exists():
        return {"exists": False}
    txt = p.read_text("utf-8", errors="ignore")
    return {
        "exists": True,
        "bytes": p.stat().st_size,
        "lines": txt.count("\n"),
        "sha256": sha256(path),
        "head_200": txt[:200],
    }

def main():
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_path": MODEL,
        "model_exists": Path(MODEL).exists(),
        "artifacts": {k: stats(v) for k, v in FILES.items()},
        "notes": {
            "backend": "llama.cpp (llama-cli)",
            "quant": "Q4_K_M",
            "seed": 42,
            "temperature": 0.2,
            "top_p": 0.95,
            "repeat_penalty": 1.05,
        },
    }

    out_path = Path("reports/slm_smoke.json")
    out_path.write_text(json.dumps(report, indent=2), "utf-8")
    print(f"Wrote: {out_path}")

if __name__ == "__main__":
    main()
