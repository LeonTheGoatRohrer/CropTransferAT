"""Scene statistics -> reflectance, harmonisation, indices, as-of dekad composites (PLAN §3.2).

All functions that build composites take a `cutoff` date and use only observations
with date <= cutoff (as-of rule §3.5) - including the interpolation of gaps.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

BANDS = ["blue", "green", "red", "rededge1", "nir", "swir1", "swir2"]
# (scale, offset) from stored DN to surface reflectance
SCALING = {"HLS": (1.0, 0.0), "S2": (1e-4, 0.0), "L5": (2.75e-5, -0.2), "L7": (2.75e-5, -0.2)}
# ETM+ -> OLI OLS transformation (Roy et al. 2016, Table 2); also applied to TM (L5)
ROY_ETM_TO_OLI = {"blue": (0.0003, 0.8474), "green": (0.0088, 0.8483), "red": (0.0061, 0.9047),
                  "nir": (0.0412, 0.8462), "swir1": (0.0254, 0.8937), "swir2": (0.0172, 0.9071)}
INDICES_HLS = ["ndvi", "evi", "gndvi", "ndmi", "savi"]
INDICES_S2 = INDICES_HLS + ["ndre"]


def to_reflectance(obs: pd.DataFrame, harmonise_landsat: bool = True) -> pd.DataFrame:
    """Scale stored band medians to reflectance; Landsat 5/7 optionally to OLI level."""
    out = obs.copy()
    for sensor, (sc, off) in SCALING.items():
        m = out["sensor"] == sensor
        for b in BANDS:
            if b in out:
                out.loc[m, b] = out.loc[m, b] * sc + off
        if harmonise_landsat and sensor in ("L5", "L7"):
            for b, (a, k) in ROY_ETM_TO_OLI.items():
                out.loc[m, b] = a + k * out.loc[m, b]
    return out


def add_indices(df: pd.DataFrame) -> pd.DataFrame:
    """Spectral indices from band reflectances (NDRE only where rededge1 exists)."""
    d = df
    with np.errstate(divide="ignore", invalid="ignore"):
        d["ndvi"] = (d.nir - d.red) / (d.nir + d.red)
        d["evi"] = 2.5 * (d.nir - d.red) / (d.nir + 6 * d.red - 7.5 * d.blue + 1)
        d["gndvi"] = (d.nir - d.green) / (d.nir + d.green)
        d["ndmi"] = (d.nir - d.swir1) / (d.nir + d.swir1)
        d["savi"] = 1.5 * (d.nir - d.red) / (d.nir + d.red + 0.5)
        if "rededge1" in d:
            d["ndre"] = (d.nir - d.rededge1) / (d.nir + d.rededge1)
    return d


def valid_obs(obs: pd.DataFrame, clear_frac_min: float = 0.7) -> pd.DataFrame:
    """Keep scenes with clear_frac >= threshold and indices inside [-1, 1] (EVI may exceed 1)."""
    o = obs.copy()
    o["clear_frac"] = o.n_clear / o.n_total
    ok = (o.clear_frac >= clear_frac_min) & o.ndvi.between(-1, 1) & o.ndmi.between(-1, 1)
    ok &= o.evi.between(-1, 2)
    return o[ok]


def dekad_index(dates: pd.Series, season_start: str = "04-01") -> np.ndarray:
    """Dekad number since season start (0 = first 10 days), clipped to 0..20 (Apr..Oct)."""
    d = pd.to_datetime(dates)
    start = pd.to_datetime(d.dt.year.astype(str) + "-" + season_start)
    return np.clip(((d - start).dt.days // 10).to_numpy(), -1, 20)


def dekad_composite(obs: pd.DataFrame, cutoff: date, index: str, season_start: str = "04-01",
                    n_dekads: int = 21) -> pd.DataFrame:
    """As-of dekad composite of one index for one field-year.

    Returns 21 rows (dekad 0..20): value (median of valid obs, gaps linearly interpolated
    between observed dekads, ends filled with the nearest observed value), is_observed,
    days_since_last_obs. Dekads after the cutoff are NaN. Only obs dated <= cutoff are used.
    """
    o = obs[pd.to_datetime(obs["date"]).dt.date <= cutoff]
    assert (pd.to_datetime(o["date"]).dt.date <= cutoff).all()
    year = cutoff.year
    start = pd.Timestamp(f"{year}-{season_start}")
    last_dekad = int(min(n_dekads - 1, max(-1, (pd.Timestamp(cutoff) - start).days // 10)))
    out = pd.DataFrame({"dekad": np.arange(n_dekads), "value": np.nan, "is_observed": False,
                        "days_since_last_obs": np.nan})
    if last_dekad < 0:
        return out
    o = o.assign(dk=dekad_index(o["date"], season_start))
    o = o[(o.dk >= 0) & o[index].notna()]
    med = o.groupby("dk")[index].median()
    vals = pd.Series(np.nan, index=np.arange(last_dekad + 1))
    vals.loc[med.index[med.index <= last_dekad]] = med[med.index <= last_dekad]
    observed = vals.notna()
    if observed.any():
        vals = vals.interpolate(limit_area="inside").ffill().bfill()
    out.loc[: last_dekad, "value"] = vals.to_numpy()
    out.loc[: last_dekad, "is_observed"] = observed.to_numpy()
    if len(o):
        last_obs = pd.to_datetime(o["date"]).max()
        out.loc[last_dekad, "days_since_last_obs"] = (pd.Timestamp(cutoff) - last_obs).days
    return out


def smooth(v: np.ndarray) -> np.ndarray:
    """3-dekad centred moving average (NaN-aware) used for peak detection."""
    s = pd.Series(v)
    return s.rolling(3, center=True, min_periods=1).mean().to_numpy()
