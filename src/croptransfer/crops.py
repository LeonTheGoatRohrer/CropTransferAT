"""Crop parameters from config.yaml block ``crops`` (plan_mehrkultur.md D6)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import numpy as np

from croptransfer.config import load_config


@dataclass(frozen=True)
class CropSpec:
    """Thermal-time, season and Kc settings of one crop."""

    name: str
    winter: bool
    season_start_mmdd: str
    season_start_offset_year: int
    gdd_base: float
    gdd_cap: float
    flower_window: tuple[str, str]
    heat_threshold: float
    mid_start_mmdd: str
    gdd_nodes: tuple[float, ...]
    kc_nodes: tuple[float, ...]

    def season_start(self, harvest_year: int) -> date:
        """First day of the weather window for a harvest year (autumn of the year before for winter crops)."""
        return date.fromisoformat(f"{harvest_year + self.season_start_offset_year}-{self.season_start_mmdd}")

    def kc(self, gdd_cum: np.ndarray) -> np.ndarray:
        """Crop coefficient by accumulated thermal time (piecewise linear)."""
        return np.interp(gdd_cum, self.gdd_nodes, self.kc_nodes)


def get_crop(name: str, cfg: dict[str, Any] | None = None) -> CropSpec:
    """Build the CropSpec for ``name`` from the config (validated)."""
    cfg = cfg or load_config()
    c = cfg["crops"][name]
    spec = CropSpec(
        name=name, winter=bool(c["winter"]), season_start_mmdd=c["season_start_mmdd"],
        season_start_offset_year=int(c["season_start_offset_year"]), gdd_base=float(c["gdd_base"]),
        gdd_cap=float(c["gdd_cap"]), flower_window=tuple(c["flower_window"]),
        heat_threshold=float(c["heat_threshold"]), mid_start_mmdd=c["mid_start_mmdd"],
        gdd_nodes=tuple(map(float, c["gdd_nodes"])), kc_nodes=tuple(map(float, c["kc_nodes"])),
    )
    assert len(spec.gdd_nodes) == len(spec.kc_nodes) >= 2 and list(spec.gdd_nodes) == sorted(spec.gdd_nodes)
    assert spec.winter == (spec.season_start_offset_year < 0)
    return spec
