"""As-of feature builder (PLAN.md Phase 2, groups S, W, B, B+; §3.3 indicators, §3.5 as-of rule).

`build(cutoff_mmdd)` returns one row per US field-year with features computed only from
data dated <= cutoff in the field-year's own season. Every satellite and weather input is
filtered by date first and asserted afterwards (tests/test_no_leakage.py).

Satellite basis "HLS": HLS observations from 2013, harmonised Landsat 5/7 before 2013.
Satellite basis "S2": Sentinel-2 observations (2017+), adds NDRE.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from croptransfer import timeseries as ts

GDD_BASE, GDD_CAP = 10.0, 30.0
FLOWER_WINDOW = ("07-10", "08-20")     # silking window for heat/drought around flowering
AUG_DEKADS = (12, 13, 14)               # dekads covering 1.8.-31.8. (start 1.4.)
MIN_RECENT_OBS = 2                      # clear dates needed since 1.6. (1.5.) for curve features
MAX_STALE_DAYS = 20                     # 'last/mean3/slope3' missing if last clear date is older
SAT_INDICES = {"HLS":["ndvi", "evi", "ndmi", "gndvi"], "S2": ["ndvi", "evi", "ndmi", "gndvi", "ndre"]}


def cutoff_date(year: int, mmdd: str) -> date:
    return date.fromisoformat(f"{year}-{mmdd}")


# ------------------------------------------------------------- S group ----
def satellite_features(obs: pd.DataFrame, cutoff: date, indices: list[str], suffix: str) -> dict:
    """Curve features up to the cutoff for one field-year (obs = valid scenes of that field-year)."""
    f: dict[str, float] = {}
    dates = pd.to_datetime(obs["date"]).dt.date if len(obs) else pd.Series([], dtype=object)
    past = sorted(set(d for d in dates if d <= cutoff))
    f[f"n_obs_{suffix}"] = len(past)
    # data-quality rule (DECISIONS 2026-10-16): need >= MIN_RECENT_OBS clear dates since 1.6.
    # (since 1.5. for cutoffs <= 1.6.), otherwise the curve features are missing, not carried forward
    window_start = date(cutoff.year, 5 if cutoff <= date(cutoff.year, 6, 1) else 6, 1)
    if sum(window_start <= d for d in past) < MIN_RECENT_OBS:
        return f
    stale = (cutoff - past[-1]).days > MAX_STALE_DAYS
    f[f"days_since_obs_{suffix}"] = (cutoff - past[-1]).days
    for idx in indices:
        comp = ts.dekad_composite(obs, cutoff, idx) if len(obs) else None
        p = f"{idx}_{suffix}"
        if comp is None or comp.value.isna().all():
            continue
        v = comp.value.dropna().to_numpy()
        sm = ts.smooth(v)
        k = len(v) - 1
        f[f"{p}_last"] = np.nan if stale else v[-1]
        f[f"{p}_max"] = np.max(v)
        f[f"{p}_mean3"] = np.nan if stale else np.mean(v[-3:])
        f[f"{p}_slope3"] = np.nan if stale else (v[-1] - v[max(0, k - 3)]) / 3.0
        f[f"{p}_mean_jun"] = np.mean(v[6:]) if k >= 6 else np.nan       # from 1.6. to cutoff
        base = np.nanpercentile(v, 10)
        f[f"{p}_auc"] = float(np.clip(v - base, 0, None).sum())          # K4-like integral so far
        ipk = int(np.argmax(sm))
        f[f"{p}_peak"] = sm[ipk]                                         # K3
        f[f"{p}_peak_dekad"] = ipk
        post = v[ipk + 1: ipk + 5]                                       # K2: 40 days after peak
        f[f"{p}_postpeak"] = np.mean(post) if len(post) >= 2 else np.nan
        aug = comp[comp.dekad.isin(AUG_DEKADS)]
        f[f"{p}_aug"] = aug.value.mean() if aug.is_observed.sum() >= 2 and k >= max(AUG_DEKADS) else np.nan  # K1
        f[f"{p}_obsfrac"] = comp.is_observed[: k + 1].mean()
    return f


# ------------------------------------------------------------- W group ----
def _ra_mm(lat_deg: float, doy: np.ndarray) -> np.ndarray:
    """Extraterrestrial radiation (FAO-56 eq. 21) in mm/day equivalent evaporation."""
    phi = np.radians(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    delta = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(delta), -1, 1))
    ra = 24 * 60 / np.pi * 0.082 * dr * (ws * np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.sin(ws))
    return ra * 0.408


def daily_weather(w: pd.DataFrame, lat: float) -> pd.DataFrame:
    """ERA5-Land daily -> degC, mm, Hargreaves ET0, VPD, GDD."""
    d = w.copy()
    d["date"] = pd.to_datetime(d["date"])
    d = d.sort_values("date")
    d["tmax"], d["tmin"], d["tmean"] = d.tmax_K - 273.15, d.tmin_K - 273.15, d.tmean_K - 273.15
    d["tdew"] = d.tdew_K - 273.15
    d["prec"] = d.prec_m * 1000.0
    es = 0.6108 * np.exp(17.27 * d.tmean / (d.tmean + 237.3))
    ea = 0.6108 * np.exp(17.27 * d.tdew / (d.tdew + 237.3))
    d["vpd"] = (es - ea).clip(lower=0)
    doy = d.date.dt.dayofyear.to_numpy()
    d["et0"] = 0.0023 * _ra_mm(lat, doy) * (d.tmean + 17.8) * np.sqrt((d.tmax - d.tmin).clip(lower=0))
    tx = d.tmax.clip(upper=GDD_CAP)
    tn = d.tmin.clip(lower=GDD_BASE).clip(upper=GDD_CAP)
    d["gdd"] = ((tx + tn) / 2 - GDD_BASE).clip(lower=0)
    return d


def crop_coefficient(gdd_cum: np.ndarray) -> np.ndarray:
    """Simple maize Kc by thermal time (FAO-56 stages mapped to GDD, base 10 degC)."""
    return np.interp(gdd_cum, [0, 200, 900, 1700, 2600], [0.3, 0.3, 1.2, 1.2, 0.6])


def rzwsi_series(d: pd.DataFrame, taw_mm: float, p: float = 0.55) -> np.ndarray:
    """Daily root-zone water stress 1-Ks from a FAO-56 single bucket (starts full on 1.4.)."""
    dr, out = 0.0, []
    kc = crop_coefficient(d.gdd.cumsum().to_numpy())
    raw = p * taw_mm
    for prec, et0, k in zip(d.prec.to_numpy(), d.et0.to_numpy(), kc):
        ks = 1.0 if dr <= raw else max(0.0, (taw_mm - dr) / ((1 - p) * taw_mm))
        dr = min(taw_mm, max(0.0, dr - prec + k * ks * et0))
        out.append(1 - ks)
    return np.asarray(out)


def weather_features(daily: pd.DataFrame, cutoff: date, taw_mm: float) -> dict:
    """Weather features for one field-year from daily data (1.4. .. cutoff)."""
    year = cutoff.year
    d = daily[(daily.date >= pd.Timestamp(f"{year}-04-01")) & (daily.date <= pd.Timestamp(cutoff))].copy()
    assert (d.date.dt.date <= cutoff).all()
    if d.empty:
        return {}
    d["rzwsi"] = rzwsi_series(d, taw_mm)
    last30 = d[d.date > pd.Timestamp(cutoff) - pd.Timedelta(days=30)]
    jun = d[d.date >= pd.Timestamp(f"{year}-06-01")]
    fl = d[(d.date >= pd.Timestamp(f"{year}-{FLOWER_WINDOW[0]}")) & (d.date <= pd.Timestamp(f"{year}-{FLOWER_WINDOW[1]}"))]
    spring = d[d.date < pd.Timestamp(f"{year}-06-01")]
    nan = np.nan
    return {
        "gdd": d.gdd.sum(), "prec": d.prec.sum(), "cwb": (d.prec - d.et0).sum(),
        "prec_30d": last30.prec.sum(), "cwb_30d": (last30.prec - last30.et0).sum(),
        "heat30": int((d.tmax > 30).sum()), "heat32": int((d.tmax > 32).sum()),
        "heat32_flower": int((fl.tmax > 32).sum()) if len(fl) else 0,
        "tmax_jun": jun.tmax.mean() if len(jun) else nan,
        "vpd_jun": jun.vpd.mean() if len(jun) else nan,
        "swvl1_30d": last30.swvl1.mean(), "swvl2_30d": last30.swvl2.mean(), "swvl3_30d": last30.swvl3.mean(),
        "swvl2_min_jun": jun.swvl2.min() if len(jun) else nan,
        "prec_spring": spring.prec.sum(),
        "rzwsi_jun": jun.rzwsi.mean() if len(jun) else 0.0,
        "rzwsi_flower": fl.rzwsi.mean() if len(fl) else nan,
        "rad_30d": last30.rad_J_m2.mean() / 1e6,
    }


# ------------------------------------------------------------- B group ----
def saxton_rawls_awc(sand: float, clay: float, om: float) -> float:
    """Plant-available water (vol. fraction) after Saxton & Rawls (2006), eqs. 1-2.

    sand, clay as fractions (0-1), om organic matter in % weight.
    """
    t1500 = (-0.024 * sand + 0.487 * clay + 0.006 * om + 0.005 * sand * om - 0.013 * clay * om
             + 0.068 * sand * clay + 0.031)
    th1500 = t1500 + (0.14 * t1500 - 0.02)
    t33 = (-0.251 * sand + 0.195 * clay + 0.011 * om + 0.006 * sand * om - 0.027 * clay * om
           + 0.452 * sand * clay + 0.299)
    th33 = t33 + (1.283 * t33 ** 2 - 0.374 * t33 - 0.015)
    return float(max(0.02, th33 - th1500))


STATIC_B = ["clay", "sand", "soc", "awc", "elev", "slope", "northness", "eastness", "tpi", "twi"]
STATIC_BPLUS = ["nccpi_corn", "ssurgo_corn_yield"]


def static_features(static_gee: pd.DataFrame) -> pd.DataFrame:
    """SoilGrids units -> fractions/%, AWC via Saxton & Rawls; one row per field_uid."""
    s = static_gee.copy()
    s["clay"] = s["clay"] / 1000.0          # g/kg -> fraction
    s["sand"] = s["sand"] / 1000.0
    s["soc"] = s["soc"] / 100.0             # dg/kg -> % (g/100 g)
    s["awc"] = [saxton_rawls_awc(a, c, 1.72 * o) for a, c, o in zip(s.sand, s.clay, s.soc)]
    return s


# --------------------------------------------------------------- build ----
def build_rows(fy: pd.DataFrame, obs_by_key: dict[str, dict[str, pd.DataFrame]],
               weather_by_key: dict[str, pd.DataFrame], static: pd.DataFrame, cutoff_mmdd: str,
               root_depth_m: float = 1.0) -> pd.DataFrame:
    """Feature table for all field-years at one cutoff.

    obs_by_key[fy_key][basis] = valid observations (with indices) of that field-year;
    weather_by_key[fy_key] = daily weather of that field-year (output of daily_weather).
    """
    st = static.set_index("field_uid")
    rows = []
    for r in fy.itertuples():
        cut = cutoff_date(int(r.year), cutoff_mmdd)
        f = {"fy_key": r.fy_key}
        for basis, idxs in SAT_INDICES.items():
            o = obs_by_key.get(r.fy_key, {}).get(basis)
            if o is not None and len(o):
                f.update(satellite_features(o, cut, idxs, basis.lower()))
        awc = st.loc[r.field_uid, "awc"] if r.field_uid in st.index else 0.15
        w = weather_by_key.get(r.fy_key)
        if w is not None:
            f.update(weather_features(w, cut, taw_mm=awc * root_depth_m * 1000))
        if r.field_uid in st.index:
            for c in STATIC_B + [c for c in STATIC_BPLUS if c in st.columns]:
                f[c] = st.loc[r.field_uid, c]
        rows.append(f)
    return pd.DataFrame(rows)


def feature_groups(columns) -> dict[str, list[str]]:
    """Column names per feature group for one satellite basis suffix (_hls or _s2)."""
    cols = list(columns)
    sat_hls = [c for c in cols if c.endswith(("_hls",)) or "_hls_" in c]
    sat_s2 = [c for c in cols if "_s2_" in c or c.endswith("_s2")]
    weather = ["gdd", "prec", "cwb", "prec_30d", "cwb_30d", "heat30", "heat32", "heat32_flower",
               "tmax_jun", "vpd_jun", "swvl1_30d", "swvl2_30d", "swvl3_30d", "swvl2_min_jun",
               "prec_spring", "rzwsi_jun", "rzwsi_flower", "rad_30d"]
    return {"S_hls": sat_hls, "S_s2": sat_s2, "W": [c for c in weather if c in cols],
            "B": [c for c in STATIC_B if c in cols], "B+": [c for c in STATIC_BPLUS if c in cols]}
