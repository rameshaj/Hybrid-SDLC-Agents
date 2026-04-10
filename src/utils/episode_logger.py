from __future__ import annotations

from pathlib import Path
from typing import List, Union
import pandas as pd
from .episode_schema import EpisodeRecord


class EpisodeLogger:
    """
    Appends EpisodeRecord rows to a Parquet file.
    Design goal: simple, robust, thesis-friendly.
    """
    def __init__(self, out_dir: Union[str, Path] = "episodes", filename: str = "episodes.parquet"):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.out_dir / filename

    def log(self, record: EpisodeRecord) -> str:
        df = pd.DataFrame([record.model_dump()])

        if self.path.exists():
            # Append by reading existing and concatenating (simple + reliable).
            # Later, we can optimize using partitioned datasets if needed.
            existing = pd.read_parquet(self.path)
            combined = pd.concat([existing, df], ignore_index=True)
            combined.to_parquet(self.path, index=False)
        else:
            df.to_parquet(self.path, index=False)

        return record.episode_id

    def log_many(self, records: List[EpisodeRecord]) -> List[str]:
        ids = []
        for r in records:
            ids.append(self.log(r))
        return ids

    def read(self) -> pd.DataFrame:
        if not self.path.exists():
            return pd.DataFrame()
        return pd.read_parquet(self.path)
