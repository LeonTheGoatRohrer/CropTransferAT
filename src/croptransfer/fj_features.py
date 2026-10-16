"""Feature builders M1-M4 of the Feinjustierung (definitions fixed in reports/feinjust_vorab.md).

Pure functions on cached extracts; every builder takes the cutoff date and uses only rows dated
<= cutoff (as-of rule, tests/test_no_leakage.py). No builder sees yields.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from croptransfer import timeseries as ts


def _dates(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s).dt.date


def neighbour_anomaly(df: pd.DataFrame, value: str, group_cols: list[str], min_others: int = 3) -> pd.Series:
    """value minus the median of the OTHER rows of the same group (NaN with < min_others others)."""
    out = pd.Series(np.nan, index=df.index, dtype=float)
    for _, g in df.dropna(subset=[value]).groupby(group_cols):
        if len(g) - 1 < min_others:
            continue
        v = g[value].to_numpy(float)
        med = np.array([np.median(np.delete(v, i)) for i in range(len(v))])
        out.loc[g.index] = v - med
    return out


# ------------------------------------------------------------------ M1 radar ----
def s1_scene_table(raw: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Quality rules per field x scene, slice duplicates merged, linear RVI and VH-VV (dB)."""
    s = cfg["s1"]
    d = raw.copy()
    ok = (d.n_pix >= s["min_pixels"]) & d.vv_db.between(*s["vv_range_db"]) & d.vh_db.between(*s["vh_range_db"])
    d = d[ok]
    d = d.groupby(["fy_key", "date", "orbit_pass"], as_index=False)[["vv_db", "vh_db"]].median()
    vv, vh = 10 ** (d.vv_db / 10), 10 ** (d.vh_db / 10)
    d["rvi"] = 4 * vh / (vv + vh)
    d["vhvv"] = d.vh_db - d.vv_db
    return d


def s1_field_features(scenes: pd.DataFrame, dataset_of: pd.Series, cutoff_by_key: dict, cfg: dict) -> pd.DataFrame:
    """M1 per field-year: mean RVI, neighbour anomalies of RVI and VH-VV over scenes window..cutoff."""
    s = cfg["s1"]
    d = scenes.copy()
    d["dataset"] = d.fy_key.map(dataset_of)
    dd = _dates(d.date)
    cut = d.fy_key.map(cutoff_by_key)
    start = cut.map(lambda c: date.fromisoformat(f"{c.year}-{s['window_start_mmdd']}"))
    d = d[(dd <= cut) & (dd >= start)].copy()
    assert (_dates(d.date) <= d.fy_key.map(cutoff_by_key)).all()
    grp = ["dataset", "date", "orbit_pass"]
    d["rvi_anom"] = neighbour_anomaly(d, "rvi", grp, s["min_neighbours"])
    d["vhvv_anom"] = neighbour_anomaly(d, "vhvv", grp, s["min_neighbours"])
    g = d.groupby("fy_key")
    out = pd.DataFrame({"s1_n_scenes": g.size(), "s1_rvi_mean": g.rvi.mean(),
                        "s1_rvi_anom": g.rvi_anom.mean(), "s1_vhvv_anom": g.vhvv_anom.mean()})
    few = out.s1_n_scenes < s["min_scenes"]
    out.loc[few, ["s1_rvi_mean", "s1_rvi_anom", "s1_vhvv_anom"]] = np.nan
    return out.reindex(list(cutoff_by_key)).rename_axis("fy_key").reset_index()


# ------------------------------------------------------- M2 temperature, ET ----
def lst_field_features(raw: pd.DataFrame, tmax: pd.DataFrame, dataset_of: pd.Series, cutoff_by_key: dict,
                       cfg: dict) -> pd.DataFrame:
    """M2a: mean (LST - ERA5 Tmax) and its neighbour anomaly over clear scenes window..cutoff.

    raw: fy_key, date, n_clear, n_total, lst_k; tmax: fy_key, date, tmax (degC).
    """
    c = cfg["lst"]
    d = raw[(raw.n_total > 0) & (raw.n_clear / raw.n_total >= c["clear_frac_min"]) & raw.lst_k.notna()].copy()
    d = d.groupby(["fy_key", "date"], as_index=False).lst_k.median()      # overlapping rows, same overpass
    dd = _dates(d.date)
    cut = d.fy_key.map(cutoff_by_key)
    start = cut.map(lambda x: date.fromisoformat(f"{x.year}-{c['window_start_mmdd']}"))
    d = d[(dd <= cut) & (dd >= start)].copy()
    assert (_dates(d.date) <= d.fy_key.map(cutoff_by_key)).all()
    t = tmax.assign(date=pd.to_datetime(tmax.date).dt.strftime("%Y-%m-%d"))
    d = d.merge(t[["fy_key", "date", "tmax"]], on=["fy_key", "date"], how="left")
    d["dt"] = d.lst_k - 273.15 - d.tmax
    d["dataset"] = d.fy_key.map(dataset_of)
    d["anom"] = neighbour_anomaly(d, "lst_k", ["dataset", "date"], cfg["s1"]["min_neighbours"])
    g = d.groupby("fy_key")
    out = pd.DataFrame({"lst_n_scenes": g.size(), "lst_dt_mean": g.dt.mean(), "lst_anom_mean": g.anom.mean()})
    out.loc[out.lst_n_scenes < c["min_scenes"], ["lst_dt_mean", "lst_anom_mean"]] = np.nan
    return out.reindex(list(cutoff_by_key)).rename_axis("fy_key").reset_index()


def modis_et_ratio(raw: pd.DataFrame, cutoff_by_key: dict, cfg: dict) -> pd.Series:
    """M2b: sum ET / sum PET of 8-day composites starting >= window start and ending <= cutoff."""
    c = cfg["et"]
    d = raw.dropna(subset=["ET", "PET"])
    d = d[(d.ET < c["modis_fill_min"]) & (d.PET < c["modis_fill_min"])].copy()
    start = pd.to_datetime(d.date)
    end = (start + pd.Timedelta(days=c["composite_days"] - 1)).dt.date
    cut = d.fy_key.map(cutoff_by_key)
    win = cut.map(lambda x: date.fromisoformat(f"{x.year}-{c['window_start_mmdd']}"))
    d = d[(end <= cut) & (start.dt.date >= win)]
    g = d.groupby("fy_key")[["ET", "PET"]].sum()
    r = (g.ET / g.PET).where(g.PET > 0)
    return r.reindex(list(cutoff_by_key))


def era5_et_ratio(evap: pd.DataFrame, wpt_of: pd.Series, cutoff_by_key: dict, cfg: dict) -> pd.Series:
    """M2b: sum actual / sum potential evaporation (ERA5-Land daily) window start..cutoff, per field-year."""
    out = {}
    e = evap.assign(d=_dates(evap.date))
    for key, cut in cutoff_by_key.items():
        w = e[(e.pt == wpt_of.get(key)) & (e.d <= cut)
              & (e.d >= date.fromisoformat(f"{cut.year}-{cfg['et']['window_start_mmdd']}"))]
        w = w[pd.to_datetime(w.date).dt.year == cut.year]
        den = w.pev_m.sum()
        out[key] = float(w.evap_m.sum() / den) if len(w) and den != 0 else np.nan
    return pd.Series(out)


# ------------------------------------------------------------- M3 GDD axis ----
def gdd_bins(obs: pd.DataFrame, daily: pd.DataFrame, cutoff: date, cfg: dict, index: str = "ndvi") -> pd.Series:
    """Median index value per thermal-time bin (100 degCd) for one field-year, as-of cutoff.

    Only bins completed before the cutoff (cumulative GDD at cutoff >= bin upper edge) and from
    first_cdd on; GDD summed from 1.4. with the maize thermal time of features.daily_weather.
    """
    g = cfg["gdd_score"]
    if obs is None or obs.empty or daily is None or daily.empty:
        return pd.Series(dtype=float)
    d = daily[(daily.date >= pd.Timestamp(f"{cutoff.year}-04-01")) & (daily.date <= pd.Timestamp(cutoff))]
    if d.empty:
        return pd.Series(dtype=float)
    cum = pd.Series(d.gdd.cumsum().to_numpy(), index=d.date.dt.normalize())
    o = obs[_dates(obs.date) <= cutoff]
    o = o.assign(g=pd.to_datetime(o.date).dt.normalize().map(cum)).dropna(subset=["g", index])
    b = np.floor(o.g / g["bin_cdd"]).astype(int)
    complete = (b + 1) * g["bin_cdd"] <= cum.iloc[-1]
    o = o[(b * g["bin_cdd"] >= g["first_cdd"]) & complete].assign(b=b)
    return o.groupby("b")[index].median()


def gdd_reference(bins: dict[str, pd.Series], keys) -> pd.Series:
    """Median per thermal-time bin over the given (healthy, training) field-years."""
    parts = [bins[k] for k in keys if k in bins and len(bins[k])]
    if not parts:
        return pd.Series(dtype=float)
    return pd.concat(parts).groupby(level=0).median()


def gdd_score(bins_key: pd.Series, ref: pd.Series) -> float:
    """Mean negative deviation from the reference over the field-year's observed bins (<= 0)."""
    if bins_key is None or bins_key.empty:
        return np.nan
    dev = bins_key.to_numpy() - ref.reindex(bins_key.index).to_numpy()
    dev = dev[np.isfinite(dev)]
    return float(np.minimum(dev, 0).mean()) if len(dev) else np.nan


# ------------------------------------------------------------ M4 emergence ----
def emergence_doy(obs: pd.DataFrame, cutoff: date, cfg: dict, index: str = "ndvi") -> float:
    """Green-up date: first crossing of base + frac x amplitude on the smoothed as-of dekad curve.

    base = minimum of the smoothed curve before its maximum; the crossing is searched after that
    minimum (bare soil after tillage), with linear interpolation between dekads. NaN if the
    amplitude is < min_amplitude or fewer than min_obs_dekads_before_peak observed dekads.
    """
    e = cfg["emerge"]
    if obs is None or obs.empty:
        return np.nan
    comp = ts.dekad_composite(obs, cutoff, index)
    v = comp.value.to_numpy()
    k = int(np.flatnonzero(np.isfinite(v)).max()) if np.isfinite(v).any() else -1
    if k < 2:
        return np.nan
    sm = ts.smooth(v[: k + 1])
    ipk = int(np.nanargmax(sm))
    if comp.is_observed[:ipk].sum() < e["min_obs_dekads_before_peak"]:
        return np.nan
    imin = int(np.nanargmin(sm[: ipk + 1]))
    base, amp = sm[imin], sm[ipk] - sm[imin]
    if not amp >= e["min_amplitude"]:
        return np.nan
    thr = base + e["amplitude_frac"] * amp
    for d in range(imin + 1, ipk + 1):
        if sm[d] >= thr:
            frac = (d - 1) + (thr - sm[d - 1]) / (sm[d] - sm[d - 1])
            start = pd.Timestamp(f"{cutoff.year}-04-01").dayofyear
            return float(start + 10 * frac + 5)          # dekad midpoint
    return np.nan
