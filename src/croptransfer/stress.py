"""Problem fields (PLAN.md Phase 3): reference curve, stress score, pre-registered cause rules.

Cause rules and thresholds are fixed in DECISIONS.md (2026-10-16) before any evaluation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DROUGHT_RZWSI, DROUGHT_CWB30 = 0.30, -60.0
HEAT_DAYS = 5
WET_SPRING_MM = 250.0
ABRUPT_DROP, ABRUPT_NO_RECOVERY = 0.15, 0.10
ABRUPT_DEKADS = (9, 15)                 # July-August (dekad 0 = 1.-10.4.)


def last_complete_dekad(cutoff_mmdd: str, season_start: str = "04-01") -> int:
    """Index of the last dekad that ends before the cutoff (as-of safe for dekad medians)."""
    c = pd.Timestamp(f"2001-{cutoff_mmdd}")
    s = pd.Timestamp(f"2001-{season_start}")
    return int((c - s).days // 10) - 1


def reference_curve(dekads: pd.DataFrame, keys, index: str = "ndvi", basis: str = "HLS") -> pd.Series:
    """Median observed index value per dekad over the given (healthy, training) field-years."""
    d = dekads[(dekads.fy_key.isin(keys)) & (dekads["index"] == index) & (dekads.basis == basis) & dekads.is_observed]
    return d.groupby("dekad").value.median()


def stress_score(dekads: pd.DataFrame, key: str, ref: pd.Series, cutoff_mmdd: str,
                 index: str = "ndvi", basis: str = "HLS", first_dekad: int = 6) -> float:
    """Mean negative deviation from the reference over observed dekads first_dekad..cutoff (<= 0)."""
    k = last_complete_dekad(cutoff_mmdd)
    d = dekads[(dekads.fy_key == key) & (dekads["index"] == index) & (dekads.basis == basis)
               & dekads.is_observed & dekads.dekad.between(first_dekad, k)]
    if d.empty:
        return np.nan
    dev = d.value.to_numpy() - ref.reindex(d.dekad).to_numpy()
    dev = dev[np.isfinite(dev)]
    return float(np.minimum(dev, 0).mean()) if len(dev) else np.nan


def abrupt_drop(series: pd.DataFrame) -> bool:
    """Pre-registered rule on observed dekads (columns dekad, value) in July-August."""
    s = series.sort_values("dekad")
    s = s[s.dekad.between(*ABRUPT_DEKADS)].reset_index(drop=True)
    for i in range(1, len(s)):
        before, now = s.value[i - 1], s.value[i]
        if before - now >= ABRUPT_DROP:
            nxt = s.value[i + 1] if i + 1 < len(s) else now
            if before - nxt >= ABRUPT_NO_RECOVERY:
                return True
    return False


def causes(row: pd.Series, observed_series: pd.DataFrame | None) -> list[str]:
    """Cause labels for one at-risk field-year (features at 1.9.)."""
    out = []
    rz, cwb = row.get("rzwsi_flower", np.nan), row.get("cwb_30d", np.nan)
    if (np.isfinite(rz) and rz >= DROUGHT_RZWSI) or (np.isfinite(cwb) and cwb < DROUGHT_CWB30):
        out.append("Trockenstress")
    if row.get("heat32_flower", 0) >= HEAT_DAYS:
        out.append("Hitze")
    if row.get("prec_spring", 0) >= WET_SPRING_MM:
        out.append("Nässe")
    if observed_series is not None and len(observed_series) and abrupt_drop(observed_series):
        out.append("abrupter Schaden")
    return out or ["Ursache unklar"]
