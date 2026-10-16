"""Multi-crop feature tables (plan_mehrkultur.md W3.4; D5, D6, D8, DECISIONS 2026-10-16).

Cutoff of a site-year = harvest date - h days (D5; missing harvest dates -> median day of year of the same
crop, dates only, never yields). Weather features use ``features.weather_features`` with the crop's
parameters (``config.crops``); satellite features K1-K5 use only scenes dated <= cutoff.
Output: data/processed/features_multi_h<h>.parquet  (one row per site-year).

Usage:  python -m croptransfer.features_multi [--h 30 60 90]
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta

import numpy as np
import pandas as pd

from croptransfer import features, timeseries as ts
from croptransfer.config import load_config, repo_path
from croptransfer.crops import CropSpec, get_crop
from croptransfer.extract_multi import point_key

HORIZONS = (30, 60, 90)
MIN_OBS, NDVI_MAX_MIN, AMPLITUDE_MIN = 5, 0.45, 0.20       # curve test (DECISIONS 2026-10-16)
MAX_STALE_DAYS, NDMI_WINDOW_DAYS = 20, 60
TAW_MM = 150.0                                               # fixed root-zone capacity (no soil input yet)
SAT_COLS = ["k1_ndvi_max", "k2_ndvi_auc", "k3_evi_max", "k4_ndmi_mean60", "k5_ndvi_last", "n_obs", "curve_ok"]


def harvest_dates(gt: pd.DataFrame) -> pd.Series:
    """Harvest date per row; gaps filled with the median day of year (same dataset+crop, else same crop)."""
    h = pd.to_datetime(gt["harvest_date"])
    doy = h.dt.dayofyear
    med_ds = doy.groupby([gt.dataset, gt.crop]).transform("median")
    med_crop = doy.groupby(gt.crop).transform("median")
    fill = med_ds.fillna(med_crop)
    est = pd.to_datetime(gt.year.astype(int).astype(str) + "-01-01") + pd.to_timedelta(fill.round() - 1, unit="D")
    return h.fillna(est)


def satellite_row(obs: pd.DataFrame, start: date, cutoff: date) -> dict:
    """K1-K5 and the curve test for one site-year from valid scenes in [start, cutoff] (as-of)."""
    nan = np.nan
    empty = {"k1_ndvi_max": nan, "k2_ndvi_auc": nan, "k3_evi_max": nan, "k4_ndmi_mean60": nan,
             "k5_ndvi_last": nan, "n_obs": 0, "curve_ok": False}
    if obs.empty:
        return empty
    d = obs[(obs.date >= pd.Timestamp(start)) & (obs.date <= pd.Timestamp(cutoff))].sort_values("date")
    assert (d.date.dt.date <= cutoff).all()
    d = d.drop_duplicates("date")
    if d.empty:
        return empty
    t = (d.date - d.date.iloc[0]).dt.days.to_numpy(float)
    auc = np.trapezoid(d.ndvi.to_numpy(), t) / t[-1] if len(d) > 1 and t[-1] > 0 else nan
    recent = d[d.date > pd.Timestamp(cutoff) - pd.Timedelta(days=NDMI_WINDOW_DAYS)]
    stale = (pd.Timestamp(cutoff) - d.date.iloc[-1]).days > MAX_STALE_DAYS
    out = {"k1_ndvi_max": d.ndvi.max(), "k2_ndvi_auc": auc, "k3_evi_max": d.evi.max(),
           "k4_ndmi_mean60": recent.ndmi.mean() if len(recent) else nan,
           "k5_ndvi_last": nan if stale else d.ndvi.iloc[-1], "n_obs": len(d)}
    out["curve_ok"] = bool(len(d) >= MIN_OBS and d.ndvi.max() >= NDVI_MAX_MIN
                           and d.ndvi.max() - d.ndvi.min() >= AMPLITUDE_MIN)
    return out


def load_obs(cfg) -> dict[str, pd.DataFrame]:
    """All cached scene tables -> valid scenes with indices, grouped by fy_key (HLS and S2 pooled by date)."""
    files = sorted((repo_path(cfg["paths"]["interim"]) / "obs_multi").glob("*.parquet"))
    frames = [pd.read_parquet(f) for f in files]
    frames = [f for f in frames if len(f) and "n_clear" in f]
    if not frames:
        return {}
    o = pd.concat(frames, ignore_index=True)
    o = ts.add_indices(ts.to_reflectance(o))
    o = ts.valid_obs(o, cfg["field"]["clear_frac_min"])
    o = o[o.n_clear >= 2].copy()
    o["date"] = pd.to_datetime(o["date"])
    # one value per key and day: prefer the sensor with more clear pixels
    o = o.sort_values("n_clear", ascending=False).drop_duplicates(["fy_key", "date"])
    return {k: g for k, g in o.groupby("fy_key")}


def load_weather(cfg) -> dict[str, pd.DataFrame]:
    """Daily ERA5-Land per cell id (all cached years)."""
    files = sorted((repo_path(cfg["paths"]["interim"]) / "weather_multi").glob("era5_*.parquet"))
    if not files:
        return {}
    w = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True).drop_duplicates(["pt", "date"])
    return {k: g.drop(columns="pt") for k, g in w.groupby("pt")}


def build(h: int, cfg=None) -> pd.DataFrame:
    """Feature table for horizon ``h`` days before harvest (all tiers; satellites only where scenes exist)."""
    cfg = cfg or load_config()
    gt = pd.read_parquet(repo_path(cfg["paths"]["processed"]) / "gt_site_years.parquet").reset_index(drop=True)
    gt["fy_key"] = point_key(gt)
    gt["harvest_est"] = harvest_dates(gt)
    gt["cutoff"] = gt["harvest_est"] - pd.to_timedelta(h, unit="D")
    obs, wx = load_obs(cfg), load_weather(cfg)
    specs: dict[str, CropSpec] = {c: get_crop(c, cfg) for c in gt.crop.unique()}
    daily_cache: dict[tuple, pd.DataFrame] = {}
    rows = []
    for r in gt.itertuples():
        spec, cut = specs[r.crop], r.cutoff.date()
        row = {"fy_key": r.fy_key, "h": h, "cutoff": r.cutoff}
        w = wx.get(r.cell_id)
        if w is not None:
            key = (r.cell_id, r.crop)
            if key not in daily_cache:
                daily_cache[key] = features.daily_weather(w, float(r.lat), spec)
            row.update(features.weather_features(daily_cache[key], cut, TAW_MM, spec))
        sat = satellite_row(obs.get(r.fy_key, pd.DataFrame()), spec.season_start(int(r.year)), cut) \
            if r.tier == "S2" else {c: np.nan for c in SAT_COLS[:-2]} | {"n_obs": 0, "curve_ok": False}
        row.update(sat)
        rows.append(row)
    f = pd.DataFrame(rows)
    return gt.drop(columns=["harvest_est", "cutoff"]).merge(f, on="fy_key")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--h", type=int, nargs="*", default=list(HORIZONS))
    args = ap.parse_args()
    cfg = load_config()
    for h in args.h:
        d = build(h, cfg)
        out = repo_path(cfg["paths"]["processed"]) / f"features_multi_h{h:03d}.parquet"
        d.to_parquet(out, index=False)
        print(h, len(d), "weather:", int(d.get("gdd", pd.Series(dtype=float)).notna().sum()),
              "curve_ok:", int(d.curve_ok.sum()))


if __name__ == "__main__":
    main()
