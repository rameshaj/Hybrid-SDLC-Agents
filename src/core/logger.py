from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from .schemas import EpisodeRecord


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_episode_id() -> str:
    return str(uuid.uuid4())


def append_episode_jsonl(out_path: Path, rec: EpisodeRecord) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec.__dict__, ensure_ascii=False) + "\n")


def as_dict(x: Any) -> Dict[str, Any]:
    if hasattr(x, "__dict__"):
        return dict(x.__dict__)
    if isinstance(x, dict):
        return x
    return {"value": str(x)}
