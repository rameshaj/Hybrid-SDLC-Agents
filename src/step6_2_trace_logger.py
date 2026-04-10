from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List


def now_ms() -> int:
    return int(time.time() * 1000)


def safe_mkdir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def tail(s: str, n: int) -> str:
    if not s:
        return ""
    return s[-n:]


@dataclass
class TraceLogger:
    episode_dir: str
    commands: List[Dict[str, Any]]

    def __post_init__(self) -> None:
        self.commands = self.commands or []
        safe_mkdir(self.episode_dir)
        safe_mkdir(os.path.join(self.episode_dir, "meta"))

    def write_text(self, relpath: str, text: str) -> str:
        abspath = os.path.join(self.episode_dir, relpath)
        safe_mkdir(os.path.dirname(abspath))
        with open(abspath, "w", encoding="utf-8") as f:
            f.write(text or "")
        return abspath

    def write_json(self, relpath: str, obj: Any) -> str:
        abspath = os.path.join(self.episode_dir, relpath)
        safe_mkdir(os.path.dirname(abspath))
        with open(abspath, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)
        return abspath

    def log_cmd(
        self,
        *,
        step: str,
        cwd: str,
        cmd: List[str],
        rc: int,
        stdout: str,
        stderr: str,
        started_ms: int,
        ended_ms: int,
    ) -> None:
        self.commands.append(
            {
                "ts_started_ms": started_ms,
                "ts_ended_ms": ended_ms,
                "step": step,
                "cwd": cwd,
                "cmd": cmd,
                "rc": rc,
                "stdout_tail": tail(stdout, 4000),
                "stderr_tail": tail(stderr, 4000),
            }
        )
        self.write_json("meta/commands.json", self.commands)
