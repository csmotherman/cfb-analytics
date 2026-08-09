from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path = Path(__file__).resolve().parents[2]
    explosive_run_yards: int = 12
    explosive_pass_yards: int = 16

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    def raw_dir(self, season: int) -> Path:
        return self.data_dir / "raw" / str(season)

    def clean_dir(self, season: int) -> Path:
        return self.data_dir / "clean" / str(season)


SETTINGS = Settings()
