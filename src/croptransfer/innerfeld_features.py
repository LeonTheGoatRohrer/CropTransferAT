"""Satellite features for the multi-site within-field study (plan_innerfeld.md, I2.2). No yield labels are used.

From the dekad table (`innerfeld_extract`) this builds, per field-year:
  * the field-mean NDVI curve (mean over cells, per dekad, needs enough valid cells),
  * the peak dekad of the 3-dekad moving average of that curve inside a search range,
  * B1 = NDVI of each cell, median over peak-1..peak+1 (about +-15 days),
  * M1 windows: median over [peak-4..peak-2], [peak-1..peak+1], [peak+2..peak+4], for NDVI and NDRE,
  * z-scores of all of these inside the field-year (no information crosses field-years).

The search range, window widths and validity limits are parameters here and are fixed once in
`reports/innerfeld_vorab.md` (step I3) before any model run.

Usage:  python -m croptransfer.innerfeld_features   # writes data/processed/features_innerfeld.parquet
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import numpy as np
import pandas as pd

from croptransfer.config import load_config, repo_path
from croptransfer.innerfeld_extract import N_DEKADS, load_dekads
from croptransfer.within_field import zscore_within

DEFAULTS: dict[str, Any] = {
    "peak_search": [6, 17],       # dekad indices (6 = 31 May, 17 = 18 Sep) searched for the NDVI maximum
    "smooth_dekads": 3,           # centred moving mean of the field-mean curve
    "min_valid_share": 0.5,       # a dekad enters the field curve only if >= this share of cells is valid
    "half_width": 1,              # B1 window = peak -+ half_width dekads
    "m1_offsets": [[-4, -2], [-1, 1], [2, 4]],
    "min_cells_valid": 0.8,       # a cell needs a value in the window; field-year ok if >= this share of cells
}


def field_curve(ndvi: np.ndarray, min_valid_share: float) -> np.ndarray:
    """Field-mean NDVI per dekad from a (cells x dekads) array; NaN where too few cells are valid."""
    valid = np.isfinite(ndvi)
    share = valid.mean(axis=0)
    with np.errstate(all="ignore"):
        mean = np.nanmean(np.where(valid, ndvi, np.nan), axis=0)
    return np.where(share >= min_valid_share, mean, np.nan)


def smooth(curve: np.ndarray, width: int) -> np.ndarray:
    """Centred moving mean over `width` dekads, ignoring NaN; NaN if no value in the window."""
    half = width // 2
    out = np.full(len(curve), np.nan)
    for i in range(len(curve)):
        w = curve[max(0, i - half): i + half + 1]
        if np.isfinite(w).any():
            out[i] = np.nanmean(w)
    return out


def peak_dekad(curve: np.ndarray, lo: int, hi: int, width: int) -> int | None:
    """Dekad of the maximum of the smoothed curve inside [lo, hi]; None if the range has no value."""
    s = smooth(curve, width)[lo: hi + 1]
    return None if not np.isfinite(s).any() else lo + int(np.nanargmax(s))


def window_median(arr: np.ndarray, first: int, last: int) -> np.ndarray:
    """Per-cell median over dekads first..last (clipped to the season); NaN if no dekad is valid."""
    first, last = max(0, first), min(N_DEKADS - 1, last)
    if first > last:
        return np.full(arr.shape[0], np.nan)
    sub = arr[:, first: last + 1]
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return np.nanmedian(sub, axis=1)


def build_features(tab: pd.DataFrame, p: dict[str, Any] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (cell features, field-year summary). `tab` = gt_pixels joined with the dekad columns."""
    p = {**DEFAULTS, **(p or {})}
    nd = [f"ndvi_d{k:02d}" for k in range(N_DEKADS)]
    nr = [f"ndre_d{k:02d}" for k in range(N_DEKADS)]
    cells, summ = [], []
    for key, g in tab.groupby("fy_key", sort=True):
        a_nd, a_nr = g[nd].to_numpy(float), g[nr].to_numpy(float)
        curve = field_curve(a_nd, p["min_valid_share"])
        pk = peak_dekad(curve, p["peak_search"][0], p["peak_search"][1], p["smooth_dekads"])
        row = dict(fy_key=key, site=g.site.iloc[0], year=int(g.year.iloc[0]), n_cells=len(g),
                   peak_dekad=pk, n_valid_dekads=int(np.isfinite(curve).sum()),
                   share_valid_cells_any=float(np.isfinite(a_nd).any(axis=1).mean()))
        if pk is None:
            row.update(ok=False, reason="no valid dekad in search range")
            summ.append(row)
            continue
        h = p["half_width"]
        out = g[["fy_key"]].copy()
        out["b1_ndvi"] = window_median(a_nd, pk - h, pk + h)
        for j, (o1, o2) in enumerate(p["m1_offsets"], start=1):
            out[f"m1_ndvi_w{j}"] = window_median(a_nd, pk + o1, pk + o2)
            out[f"m1_ndre_w{j}"] = window_median(a_nr, pk + o1, pk + o2)
        share = float(np.isfinite(out["b1_ndvi"]).mean())
        peak_val = float(np.nanmax(smooth(curve, p["smooth_dekads"])[p["peak_search"][0]: p["peak_search"][1] + 1]))
        row.update(peak_ndvi=peak_val, b1_share_valid=share, ok=bool(share >= p["min_cells_valid"]),
                   reason="" if share >= p["min_cells_valid"] else "b1 window valid share below limit")
        summ.append(row)
        keep = g.drop(columns=nd + nr + [c for c in g.columns if c.startswith("n_d")])
        cells.append(pd.concat([keep.reset_index(drop=True), out.drop(columns="fy_key").reset_index(drop=True)], axis=1))
    feats = pd.concat(cells, ignore_index=True)
    zc = ["b1_ndvi"] + [c for c in feats.columns if c.startswith("m1_")] + ["elev", "slope", "tpi"]
    feats = pd.concat([feats, zscore_within(feats, [c for c in zc if c in feats.columns])], axis=1)
    return feats, pd.DataFrame(summ)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args()
    cfg = load_config()
    proc = repo_path(cfg["paths"]["processed"])
    gt = pd.read_parquet(proc / "gt_pixels.parquet")
    tab = load_dekads(gt, cfg)
    feats, summ = build_features(tab)
    feats.to_parquet(proc / "features_innerfeld.parquet", index=False)
    summ.to_csv(proc / "features_innerfeld_fy.csv", index=False)
    out = {s: dict(n_fy=int(len(g)), n_ok=int(g.ok.sum()), peak_dekad_median=float(g.peak_dekad.median()))
           for s, g in summ.groupby("site")}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
