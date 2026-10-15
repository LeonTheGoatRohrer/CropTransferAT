"""Load config.yaml and resolve repository-relative paths."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "config.yaml"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Read the YAML config (default: config.yaml in the repo root)."""
    with open(path or DEFAULT_CONFIG, encoding="utf-8") as f:
        return yaml.safe_load(f)


def repo_path(relative: str | Path) -> Path:
    """Turn a repo-relative path from the config into an absolute path."""
    return REPO_ROOT / relative


def cutoff_dates(year: int, mmdd_list: list[str]) -> list[date]:
    """Convert 'MM-DD' strings from the config into dates of a given year."""
    return [date.fromisoformat(f"{year}-{mmdd}") for mmdd in mmdd_list]
