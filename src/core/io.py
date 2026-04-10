from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from .schemas import TaskSpec


def iter_jsonl(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_tasks_from_step5_jsonl(path: Path) -> list[TaskSpec]:
    tasks: list[TaskSpec] = []
    for obj in iter_jsonl(path):
        tasks.append(
            TaskSpec(
                id=str(obj["id"]),
                dataset=str(obj.get("prompt", {}).get("dataset", obj.get("prompt", {}).get("dataset_name", "UNKNOWN"))),
                task_id=str(obj.get("prompt", {}).get("task_id", "")),
                prompt=obj.get("prompt", {}),
                target_patch=str(obj.get("target", "")),
                meta=obj.get("meta", {}),
            )
        )
    return tasks
