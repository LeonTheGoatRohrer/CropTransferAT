"""Within-field analysis (PLAN.md Phase 2 task 3 / Phase 3 task 3): which parts of a field yield less?

Data: BARC kriged yield maps (10 m blocks) 2017-2021 + Sentinel-2 pixel composites + Copernicus DEM,
all sampled at the yield points. Relative pixel yield = pixel yield / mean of the same field-year;
problem zone = relative pixel yield < 0.85. Pixels are treated as NON-independent: every confidence
interval resamples field-years (not pixels).

Usage:  python -m croptransfer.within_field [--no-extract] [--refresh] [--workers 4] [--jobs 4]
Writes: results/<date>_within_field/ (metrics.json, config copies, git hash, tables),
        reports/figures/phase2_within_field_*.png, pixel cache data/interim/pixels/<field-year>.parquet
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score

from croptransfer.config import load_config, repo_path
from croptransfer.models import family

# Defaults; an optional `within_field:` section in config.yaml overrides them (config.yaml is the
# single source of truth, the code does not hide numbers elsewhere).
DEFAULTS: dict[str, Any] = {
    "dataset": "BARC",
    "years": [2017, 2021],
    "min_pixels": 50,                 # per field-year (and per window/index)
    "problem_threshold": None,        # None -> targets.at_risk_threshold (0.85)
    "windows": {                      # name -> [first day, last day (= cutoff)], inclusive, MM-DD
        "w1": ["06-15", "07-15"],
        "w2": ["07-16", "08-15"],
        "w3": ["08-16", "09-15"],
    },
    "indices": ["ndvi", "ndre"],      # NDVI = (B8A-B4)/(B8A+B4), NDRE = (B8A-B5)/(B8A+B5)
    "terrain": ["elev", "slope", "tpi"],
    "tpi_radius_m": 150,
    "sample_scale_m": 10,
    "chunk_points": 2500,             # sampleRegions request size
    "example_window": "w2",
    "lgbm": {"max_depth": 3, "num_leaves": 8, "n_estimators": 200, "learning_rate": 0.05,
             "min_child_samples": 50},
    "ridge_alpha": 1.0,
    "recurring_min_pixels": 50,
    "interior_min_dist_m": 20,        # robustness check: only pixels this far inside the buffered outline
}

SAT_FSETS = {"terrain": "terrain", "satellite": "sat", "both": "both"}


# ----------------------------------------------------------------------------------------------
# configuration, bookkeeping
# ----------------------------------------------------------------------------------------------
def wf_config(cfg: dict[str, Any]) -> dict[str, Any]:
    """Within-field settings: DEFAULTS < config.yaml `within_field:`; fills thresholds from config."""
    wf = {**DEFAULTS, **cfg.get("within_field", {})}
    if wf["problem_threshold"] is None:
        wf["problem_threshold"] = cfg["targets"]["at_risk_threshold"]
    wf["seed"] = cfg["seed"]
    wf["bootstrap_n"] = cfg["validation"]["bootstrap_n"]
    wf["ci_level"] = cfg["validation"]["ci_level"]
    return wf


def safe_name(fy_key: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", fy_key)


def cutoff_of(wf: dict[str, Any], window: str, year: int) -> date:
    mm, dd = wf["windows"][window][1].split("-")
    return date(year, int(mm), int(dd))


# ----------------------------------------------------------------------------------------------
# pure functions (unit-tested)
# ----------------------------------------------------------------------------------------------
def relative_yield(df: pd.DataFrame, key: str = "fy_key", col: str = "yield_t_ha") -> pd.Series:
    """Pixel yield divided by the mean pixel yield of the same field-year."""
    return df[col] / df.groupby(key)[col].transform("mean")


def problem_zone(rel: pd.Series | np.ndarray, threshold: float) -> np.ndarray:
    """Problem zone = relative pixel yield strictly below the threshold (PLAN.md 3.6)."""
    return np.asarray(rel, dtype=float) < threshold


def zscore_within(df: pd.DataFrame, cols: list[str], key: str = "fy_key") -> pd.DataFrame:
    """z-standardise columns inside each field-year (mean 0, SD 1 over finite pixels; constant -> 0).

    Uses only the field-year's own pixels, so no information crosses field-years.
    """
    out = pd.DataFrame(index=df.index)
    for c in cols:
        g = df.groupby(key)[c]
        mu, sd = g.transform("mean"), g.transform(lambda s: s.std(ddof=0))
        z = (df[c] - mu) / sd.where(sd > 1e-12)
        z = z.where(~(sd <= 1e-12) | df[c].isna(), 0.0)
        out[f"z_{c}"] = z
    return out


def logo_folds(groups: np.ndarray) -> list[tuple[Any, np.ndarray, np.ndarray]]:
    """Leave-one-group-out folds (group = field-year, year or field): (group, train_idx, test_idx).

    Asserts that no group appears on both sides, so a held-out group never leaks into training.
    """
    groups = np.asarray(groups)
    folds = []
    for g in pd.unique(groups):
        te = np.flatnonzero(groups == g)
        tr = np.flatnonzero(groups != g)
        assert not set(groups[tr]) & set(groups[te])
        folds.append((g, tr, te))
    return folds


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or np.std(a[m]) == 0 or np.std(b[m]) == 0:
        return np.nan
    return float(spearmanr(a[m], b[m]).statistic)


def boot_median_ci(values, n_boot: int = 1000, seed: int = 42, level: float = 0.95,
                   clusters=None) -> tuple[float, float, float]:
    """Median with percentile bootstrap CI; resamples units (or `clusters` if given), never pixels."""
    v = np.asarray(values, float)
    ok = np.isfinite(v)
    v = v[ok]
    if len(v) == 0:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed)
    if clusters is None:
        idx = rng.integers(0, len(v), (n_boot, len(v)))
        meds = np.median(v[idx], axis=1)
    else:
        c = np.asarray(clusters)[ok]
        keys = pd.unique(c)
        members = [v[c == k] for k in keys]
        meds = np.empty(n_boot)
        for b in range(n_boot):
            pick = rng.integers(0, len(keys), len(keys))
            meds[b] = np.median(np.concatenate([members[i] for i in pick]))
    a = (1 - level) / 2
    return (float(np.median(v)), float(np.quantile(meds, a)), float(np.quantile(meds, 1 - a)))


def fy_pr_auc(y: np.ndarray, score: np.ndarray) -> tuple[float, float]:
    """(PR-AUC, prevalence) of one field-year; NaN if it has no positives or no negatives."""
    y = np.asarray(y, bool)
    if y.all() or not y.any():
        return (np.nan, float(y.mean()) if len(y) else np.nan)
    return (float(average_precision_score(y, score)), float(y.mean()))


def r2_pooled(y, p) -> float:
    y, p = np.asarray(y, float), np.asarray(p, float)
    return float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def lag1_corr(x: np.ndarray, y: np.ndarray, v: np.ndarray, step: float = 10.0) -> float:
    """Pearson correlation between a pixel value and its right-hand and upper neighbour (smoothness)."""
    ix = np.round((x - x.min()) / step).astype(int)
    iy = np.round((y - y.min()) / step).astype(int)
    lut = {(a, b): val for a, b, val in zip(ix, iy, v)}
    pairs = [(val, lut[(a + da, b + db)]) for a, b, val in zip(ix, iy, v)
             for da, db in ((1, 0), (0, 1)) if (a + da, b + db) in lut]
    if len(pairs) < 10:
        return np.nan
    arr = np.array(pairs)
    return float(np.corrcoef(arr[:, 0], arr[:, 1])[0, 1])


# ----------------------------------------------------------------------------------------------
# yield points -> pixels inside the buffered field
# ----------------------------------------------------------------------------------------------
def load_pixels(cfg: dict[str, Any], wf: dict[str, Any], keep_outside: bool = False) -> pd.DataFrame:
    """BARC yield points 2017-2021 kept only if inside the (already -10 m buffered) field outline.

    keep_outside=True also returns the dropped points (column `inside`), only for data criticism.
    """
    import geopandas as gpd
    import shapely

    proc = repo_path(cfg["paths"]["processed"])
    pts = pd.read_parquet(proc / "gt_yield_points.parquet")
    lo, hi = wf["years"]
    pts = pts[(pts.dataset == wf["dataset"]) & pts.year.between(lo, hi)].copy()
    assert (pts.crs == "EPSG:32618").all(), "yield points are expected in EPSG:32618"
    fy = gpd.read_parquet(proc / "gt_field_years.parquet")
    fy = fy[(fy.dataset == wf["dataset"]) & fy.year.between(lo, hi)].to_crs("EPSG:32618")
    geoms = {(r.field_id, r.year): (r.fy_key, r.geometry) for r in fy.itertuples()}
    parts = []
    for (fid, yr), g in pts.groupby(["field_id", "year"]):
        if (fid, yr) not in geoms:
            continue
        key, geom = geoms[(fid, yr)]
        inside = shapely.contains_xy(geom, g.x.to_numpy(), g.y.to_numpy())
        g = g.assign(inside=inside)
        g = g if keep_outside else g[inside].copy()
        g["fy_key"] = key
        g["dist_edge_m"] = shapely.distance(geom.boundary, shapely.points(g.x.to_numpy(), g.y.to_numpy()))
        g["n_points_all"] = len(inside)
        parts.append(g)
    px = pd.concat(parts, ignore_index=True)
    in_mean = px[px.inside].groupby("fy_key").yield_t_ha.mean() if keep_outside else None
    px["rel"] = relative_yield(px) if not keep_outside else px.yield_t_ha / px.fy_key.map(in_mean)
    px["problem"] = problem_zone(px["rel"], wf["problem_threshold"])
    px["x"], px["y"] = px.x.round(1), px.y.round(1)
    return px.drop(columns=["crs"]) if keep_outside else px.drop(columns=["crs", "inside"])


def edge_stats(cfg: dict[str, Any], wf: dict[str, Any]) -> dict[str, Any]:
    """Selection check: are the dropped (outer 10 m) points different, and does yield change with edge distance?"""
    allp = load_pixels(cfg, wf, keep_outside=True)
    thr = wf["problem_threshold"]
    kept, drop = allp[allp.inside], allp[~allp.inside]
    bands = [(0, 10), (10, 20), (20, 40), (40, 1e9)]
    return dict(
        share_points_dropped=float(len(drop) / len(allp)),
        rel_yield_median_kept=float(kept.rel.median()), rel_yield_median_dropped=float(drop.rel.median()),
        problem_share_kept=float((kept.rel < thr).mean()), problem_share_dropped=float((drop.rel < thr).mean()),
        by_distance_inside_buffer={f"{lo}-{int(hi) if hi < 1e8 else 'inf'} m": dict(
            n=int(((kept.dist_edge_m >= lo) & (kept.dist_edge_m < hi)).sum()),
            rel_yield_median=float(kept[(kept.dist_edge_m >= lo) & (kept.dist_edge_m < hi)].rel.median()),
            problem_share=float((kept[(kept.dist_edge_m >= lo) & (kept.dist_edge_m < hi)].rel < thr).mean()))
            for lo, hi in bands})


# ----------------------------------------------------------------------------------------------
# Earth Engine extraction (cached per field-year)
# ----------------------------------------------------------------------------------------------
def pixel_image(region, year: int, cfg: dict[str, Any], wf: dict[str, Any]):
    """Multi-band image: per window median NDVI/NDRE + number of clear observations, plus terrain."""
    import ee

    g = cfg["gee"]
    bands: list = []
    for name, (first, last) in wf["windows"].items():
        start = f"{year}-{first}"
        end = (date.fromisoformat(f"{year}-{last}") + timedelta(days=1)).isoformat()   # end exclusive
        coll = ee.ImageCollection(g["collections"]["s2_sr"]).filterBounds(region).filterDate(start, end)
        cs = ee.ImageCollection(g["collections"]["s2_cloudscore"]).filterBounds(region).filterDate(start, end)
        coll = coll.linkCollection(cs, [g["s2_cloudscore_band"]])

        def prep(img):
            clear = img.select(g["s2_cloudscore_band"]).gte(g["s2_cloudscore_min"])
            valid = clear.And(img.select("B8A").gt(0))
            ndvi = img.normalizedDifference(["B8A", "B4"]).rename("ndvi")
            ndre = img.normalizedDifference(["B8A", "B5"]).rename("ndre")
            return ndvi.addBands(ndre).updateMask(valid)

        coll = coll.map(prep)
        for idx in wf["indices"]:
            bands.append(coll.select(idx).median().rename(f"{idx}_{name}"))
        bands.append(coll.select(wf["indices"][0]).count().rename(f"n_{name}"))
    dem_coll = ee.ImageCollection(g["collections"]["dem"]).select("DEM")
    dem = dem_coll.mosaic().setDefaultProjection(dem_coll.first().projection()).rename("elev")
    slope = ee.Terrain.slope(dem).rename("slope")
    tpi = dem.subtract(dem.focalMean(wf["tpi_radius_m"], "circle", "meters")).rename("tpi")
    return ee.Image.cat(bands + [dem, slope, tpi])


def extract_field_year(key: str, pts: pd.DataFrame, year: int, cfg: dict[str, Any], wf: dict[str, Any]):
    """Sample all pixel points of one field-year; returns DataFrame (pid, x, y, bands)."""
    import ee

    xs, ys = pts.x.to_numpy(), pts.y.to_numpy()
    region = ee.Geometry.Rectangle([float(xs.min()) - 20, float(ys.min()) - 20,
                                    float(xs.max()) + 20, float(ys.max()) + 20], "EPSG:32618", False)
    img = pixel_image(region, year, cfg, wf).unmask(-9999)
    rows = []
    n = wf["chunk_points"]
    for s in range(0, len(pts), n):
        feats = [ee.Feature(ee.Geometry.Point([float(x), float(y)], "EPSG:32618"), {"pid": int(i)})
                 for i, x, y in zip(range(s, min(s + n, len(pts))), xs[s:s + n], ys[s:s + n])]
        out = img.sampleRegions(ee.FeatureCollection(feats), scale=wf["sample_scale_m"],
                                projection="EPSG:32618").getInfo()["features"]
        rows += [f["properties"] for f in out]
    df = pd.DataFrame(rows).replace(-9999, np.nan).sort_values("pid").reset_index(drop=True)
    assert len(df) == len(pts), f"{key}: sampled {len(df)} of {len(pts)} points"
    df["x"], df["y"] = xs[df.pid.to_numpy()], ys[df.pid.to_numpy()]
    df["fy_key"] = key
    return df


def extract_all(px: pd.DataFrame, cfg: dict[str, Any], wf: dict[str, Any], workers: int = 4,
                refresh: bool = False) -> None:
    """Fill the cache; errors are logged and skipped; concurrency errors are retried serially."""
    from concurrent.futures import ThreadPoolExecutor

    from croptransfer import gee_extract

    cache = repo_path(cfg["paths"]["interim"]) / "pixels"
    cache.mkdir(parents=True, exist_ok=True)
    log = cache / "_errors.log"
    gee_extract.init_ee()
    todo = []
    for key, g in px.groupby("fy_key"):
        if refresh or not (cache / f"{safe_name(key)}.parquet").exists():
            todo.append((key, g.sort_values(["y", "x"]).reset_index(drop=True), int(g.year.iloc[0])))
    print(f"extraction: {len(todo)} of {px.fy_key.nunique()} field-years to fetch", flush=True)

    def work(item):
        key, g, yr = item
        t0 = time.time()
        df = extract_field_year(key, g, yr, cfg, wf)
        df.to_parquet(cache / f"{safe_name(key)}.parquet")
        return key, len(df), time.time() - t0

    def attempt(item, retries: int = 2):
        for k in range(retries + 1):
            try:
                return work(item), None
            except Exception as e:   # noqa: BLE001 - log and continue (task spec)
                err = f"{type(e).__name__}: {e}"
                if "concurrent" in err.lower() or "too many" in err.lower():
                    return None, "retry_serial"
                if k == retries:
                    with open(log, "a", encoding="utf-8") as f:
                        f.write(f"{date.today()} {item[0]}: {err[:500]}\n")
                    return None, err
                time.sleep(5 * (k + 1))
        return None, "unreachable"

    serial = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for item, (res, err) in zip(todo, ex.map(attempt, todo)):
            if err == "retry_serial":
                serial.append(item)
            elif err:
                print(f"  FAILED {item[0]}: {err[:120]}", flush=True)
            else:
                print(f"  ok {res[0]} n={res[1]} {res[2]:.0f}s", flush=True)
    for item in serial:
        res, err = attempt(item)
        print(f"  serial {item[0]}: {'ok' if res else 'FAILED ' + str(err)[:120]}", flush=True)
    missing = [k for k, _, _ in todo if not (cache / f"{safe_name(k)}.parquet").exists()]
    if missing:
        print(f"WARNING: {len(missing)} field-years without cache (see {log})", flush=True)


def load_table(px: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    """Join cached satellite/terrain samples onto the pixel table (field-years without cache drop out)."""
    cache = repo_path(cfg["paths"]["interim"]) / "pixels"
    parts = []
    for key, g in px.groupby("fy_key"):
        f = cache / f"{safe_name(key)}.parquet"
        if not f.exists():
            continue
        s = pd.read_parquet(f).drop(columns=["fy_key"])
        g = g.sort_values(["y", "x"]).reset_index(drop=True)
        assert len(s) == len(g) and np.allclose(s.x, g.x) and np.allclose(s.y, g.y), key
        parts.append(pd.concat([g, s.drop(columns=["x", "y", "pid"])], axis=1))
    return pd.concat(parts, ignore_index=True)


# ----------------------------------------------------------------------------------------------
# analysis a) + b): index vs relative yield, problem-zone PR-AUC
# ----------------------------------------------------------------------------------------------
def window_validity(df: pd.DataFrame, wf: dict[str, Any]) -> pd.DataFrame:
    """Per field-year x window x index: valid pixels, median clear images, flag usable."""
    rows = []
    for key, g in df.groupby("fy_key"):
        for w in wf["windows"]:
            n_img = g[f"n_{w}"].to_numpy(float)
            for idx in wf["indices"]:
                nv = int(np.isfinite(g[f"{idx}_{w}"]).sum())
                med = float(np.nanmedian(n_img)) if np.isfinite(n_img).any() else 0.0
                rows.append(dict(fy_key=key, window=w, index=idx, n_valid=nv, median_clear_images=med,
                                 ok=bool(nv >= wf["min_pixels"] and med >= 1)))
    return pd.DataFrame(rows)


def analysis_ab(df: pd.DataFrame, val: pd.DataFrame, wf: dict[str, Any]) -> tuple[dict, pd.DataFrame]:
    """Spearman rho(index, rel yield) and PR-AUC(-index) of problem zones per field-year and window."""
    n_boot, seed, lvl = wf["bootstrap_n"], wf["seed"], wf["ci_level"]
    ok = val.set_index(["fy_key", "window", "index"]).ok
    rows = []
    for key, g in df.groupby("fy_key"):
        for w in wf["windows"]:
            for idx in wf["indices"]:
                if not ok.get((key, w, idx), False):
                    continue
                m = np.isfinite(g[f"{idx}_{w}"].to_numpy())
                v, rel, pr = g[f"{idx}_{w}"].to_numpy()[m], g["rel"].to_numpy()[m], g["problem"].to_numpy()[m]
                auc, prev = fy_pr_auc(pr, -v)
                rows.append(dict(fy_key=key, field_id=g.field_id.iloc[0], year=int(g.year.iloc[0]),
                                 window=w, index=idx, n_pixels=int(m.sum()), rho=spearman(v, rel),
                                 prevalence=prev, pr_auc=auc))
    t = pd.DataFrame(rows)
    out: dict[str, Any] = {}
    for (idx, w), g in t.groupby(["index", "window"]):
        med, lo, hi = boot_median_ci(g.rho, n_boot, seed, lvl)
        medc, loc, hic = boot_median_ci(g.rho, n_boot, seed, lvl, clusters=g.field_id)
        gp = g.dropna(subset=["pr_auc"])
        pm, pl, ph = boot_median_ci(gp.pr_auc, n_boot, seed, lvl)
        prm = float(gp.prevalence.median()) if len(gp) else np.nan
        dm, dl, dh = boot_median_ci(gp.pr_auc - gp.prevalence, n_boot, seed, lvl)
        out[f"{idx}_{w}"] = dict(
            n_fy=int(len(g)), n_fields=int(g.field_id.nunique()),
            rho_median=med, rho_ci=[lo, hi], rho_ci_field_cluster=[loc, hic],
            frac_rho_pos=float((g.rho > 0).mean()),
            n_fy_with_problem_zone=int(len(gp)), prevalence_median=prm,
            pr_auc_median=pm, pr_auc_ci=[pl, ph], pr_auc_minus_prev_median=dm, pr_auc_minus_prev_ci=[dl, dh])
    return out, t


def analysis_interior(df: pd.DataFrame, val: pd.DataFrame, wf: dict[str, Any]) -> dict[str, Any]:
    """Robustness: rho(index, rel yield) using only pixels >= interior_min_dist_m from the outline.

    Edge pixels have both lower yield and (often) lower NDVI; this shows what is left without them.
    """
    inner = df[df.dist_edge_m >= wf["interior_min_dist_m"]]
    counts = inner.groupby("fy_key").size()
    inner = inner[inner.fy_key.isin(counts[counts >= wf["min_pixels"]].index)]
    out, _ = analysis_ab(inner, val[val.fy_key.isin(inner.fy_key.unique())], wf)
    return {k: dict(n_fy=v["n_fy"], rho_median=v["rho_median"], rho_ci=v["rho_ci"],
                    pr_auc_minus_prev_median=v["pr_auc_minus_prev_median"],
                    pr_auc_minus_prev_ci=v["pr_auc_minus_prev_ci"]) for k, v in out.items()}


def analysis_terrain(df: pd.DataFrame, wf: dict[str, Any]) -> tuple[dict, pd.DataFrame]:
    """Per field-year Spearman of terrain and distance-to-edge with rel yield (descriptive)."""
    rows = []
    for key, g in df.groupby("fy_key"):
        r = dict(fy_key=key, field_id=g.field_id.iloc[0], year=int(g.year.iloc[0]), n_pixels=len(g))
        for c in wf["terrain"] + ["dist_edge_m"]:
            ok = np.isfinite(g[c]).sum() >= wf["min_pixels"]
            r[c] = spearman(g[c], g["rel"]) if ok else np.nan
            r[f"{c}_n_unique"] = int(g[c].nunique())
        rows.append(r)
    t = pd.DataFrame(rows)
    out = {}
    for c in wf["terrain"] + ["dist_edge_m"]:
        s = t[c].dropna()
        med, lo, hi = boot_median_ci(s, wf["bootstrap_n"], wf["seed"], wf["ci_level"])
        out[c] = dict(n_fy=int(len(s)), rho_median=med, rho_ci=[lo, hi], frac_rho_pos=float((s > 0).mean()))
    return out, t


# ----------------------------------------------------------------------------------------------
# analysis c): pixel models
# ----------------------------------------------------------------------------------------------
def feature_columns(fset: str, cutoff_idx: int, wf: dict[str, Any]) -> list[str]:
    """z-feature names: satellite windows up to the cutoff (as-of) and/or terrain."""
    wins = list(wf["windows"])[:cutoff_idx + 1]
    sat = [f"z_{i}_{w}" for w in wins for i in wf["indices"]]
    ter = [f"z_{c}" for c in wf["terrain"]]
    return {"terrain": ter, "satellite": sat, "both": sat + ter}[fset]


def model_dataset(df: pd.DataFrame, val: pd.DataFrame, wf: dict[str, Any], cutoff_idx: int) -> pd.DataFrame:
    """Pixels of field-years usable for ALL windows up to the cutoff, with finite features of every fset."""
    wins = list(wf["windows"])[:cutoff_idx + 1]
    need = len(wins) * len(wf["indices"])
    good = val[val.window.isin(wins) & val.ok].groupby("fy_key").size()
    keys = good[good == need].index
    d = df[df.fy_key.isin(keys)]
    cols = feature_columns("both", cutoff_idx, wf)
    return d[np.isfinite(d[cols]).all(axis=1)].reset_index(drop=True)


def _fit_predict(kind: str, params: dict, seed: int, Xtr, ytr, Xte):
    m = family.make(kind, params, seed)
    m.fit(Xtr, ytr)
    return m.predict(Xte)


def run_scheme(d: pd.DataFrame, cols: list[str], kind: str, scheme: str, wf: dict[str, Any],
               shuffle: bool = False) -> np.ndarray:
    """Out-of-fold predictions for one scheme: 'lofyo' (field-year), 'loyo' (year), 'lofo' (field)."""
    gcol = {"lofyo": "fy_key", "loyo": "year", "lofo": "field_id"}[scheme]
    params = wf["lgbm"] if kind == "lgbm" else {"alpha": wf["ridge_alpha"]}
    X, y = d[cols].to_numpy(float), d["rel"].to_numpy(float)
    rng = np.random.default_rng(wf["seed"])
    pred = np.full(len(d), np.nan)
    for _, tr, te in logo_folds(d[gcol].to_numpy()):
        ytr = y[tr]
        if shuffle:                      # label-shuffle control: break pixel-target link in training
            ytr = ytr.copy()
            fy = d.fy_key.to_numpy()[tr]
            for k in np.unique(fy):
                ix = np.flatnonzero(fy == k)
                ytr[ix] = rng.permutation(ytr[ix])
        pred[te] = _fit_predict(kind, params, wf["seed"], X[tr], ytr, X[te])
    return pred


def eval_oof(d: pd.DataFrame, pred: np.ndarray, wf: dict[str, Any]) -> tuple[dict, pd.DataFrame]:
    """Median field-year rho (+CI over field-years), pooled R2, problem-zone PR-AUC."""
    rows = []
    for key, g in d.assign(pred=pred).groupby("fy_key"):
        auc, prev = fy_pr_auc(g.problem.to_numpy(), -g.pred.to_numpy())
        rows.append(dict(fy_key=key, field_id=g.field_id.iloc[0], year=int(g.year.iloc[0]),
                         rho=spearman(g.pred, g.rel), pr_auc=auc, prevalence=prev))
    t = pd.DataFrame(rows)
    n, s, l = wf["bootstrap_n"], wf["seed"], wf["ci_level"]
    med, lo, hi = boot_median_ci(t.rho, n, s, l)
    tp = t.dropna(subset=["pr_auc"])
    dm, dl, dh = boot_median_ci(tp.pr_auc - tp.prevalence, n, s, l)
    return dict(n_fy=int(len(t)), n_pixels=int(len(d)), rho_median=med, rho_ci=[lo, hi],
                frac_rho_pos=float((t.rho > 0).mean()), r2_pooled=r2_pooled(d.rel, pred),
                r2_b0=r2_pooled(d.rel, np.ones(len(d))), n_fy_with_problem_zone=int(len(tp)),
                pr_auc_minus_prev_median=dm, pr_auc_minus_prev_ci=[dl, dh]), t


def analysis_models(df: pd.DataFrame, val: pd.DataFrame, wf: dict[str, Any], jobs: int = 4):
    from joblib import Parallel, delayed

    feats = [f"{i}_{w}" for w in wf["windows"] for i in wf["indices"]] + wf["terrain"]
    df = pd.concat([df, zscore_within(df, feats)], axis=1)
    tasks = []
    datasets = {}
    for ci in range(len(wf["windows"])):
        datasets[ci] = model_dataset(df, val, wf, ci)
        for fset in SAT_FSETS:
            for kind in ("ridge", "lgbm"):
                for scheme in ("lofyo", "loyo", "lofo"):
                    tasks.append((ci, fset, kind, scheme, False))
        for fset in ("satellite", "both"):         # label-shuffle controls (AGENTS 3.3)
            tasks.append((ci, fset, "lgbm", "lofyo", True))

    def one(ci, fset, kind, scheme, shuffle):
        d = datasets[ci]
        cols = feature_columns(fset, ci, wf)
        pred = run_scheme(d, cols, kind, scheme, wf, shuffle)
        m, t = eval_oof(d, pred, wf)
        t = t.assign(cutoff=list(wf["windows"])[ci], fset=fset, model=kind, scheme=scheme, shuffle=shuffle)
        return (list(wf["windows"])[ci], fset, kind, scheme, shuffle), m, t

    res = Parallel(n_jobs=jobs)(delayed(one)(*t) for t in tasks)
    metrics = {}
    for (w, fset, kind, scheme, shuffle), m, _ in res:
        metrics[f"{'shuffle_' if shuffle else ''}{w}|{fset}|{kind}|{scheme}"] = m
    return metrics, pd.concat([t for _, _, t in res], ignore_index=True), df


# ----------------------------------------------------------------------------------------------
# analysis d): recurring zones
# ----------------------------------------------------------------------------------------------
def to_s2_cells(g: pd.DataFrame, step: float = 10.0) -> pd.DataFrame:
    """Average relative yield per 10-m cell of the common UTM grid (= Sentinel-2 pixel grid).

    The kriging grids of different years are shifted against each other (arbitrary offsets, found in
    Phase 2), so identical x/y never match across years; the S2 grid is the common reference.
    """
    c = g.assign(cx=np.floor(g.x / step).astype(int), cy=np.floor(g.y / step).astype(int))
    return c.groupby(["cx", "cy"], as_index=False).agg(rel=("rel", "mean"))


def analysis_recurring(df: pd.DataFrame, wf: dict[str, Any]) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Same S2 pixels in different years: Spearman of relative yields, and leave-one-year-out site mean."""
    pairs, loyo = [], []
    for fid, g in df.groupby("field_id"):
        years = sorted(g.year.unique())
        if len(years) < 2:
            continue
        piv = pd.concat({int(y): to_s2_cells(g[g.year == y]).set_index(["cx", "cy"]).rel for y in years}, axis=1)
        for i, a in enumerate(years):
            for b in years[i + 1:]:
                m = piv[[a, b]].dropna()
                if len(m) >= wf["recurring_min_pixels"]:
                    pairs.append(dict(field_id=fid, year_a=a, year_b=b, gap=b - a, n_pixels=len(m),
                                      rho=spearman(m[a], m[b]),
                                      pearson=float(np.corrcoef(m[a], m[b])[0, 1])))
        for a in years:                              # predict year a from the mean of the OTHER years
            others = piv[[y for y in years if y != a]].mean(axis=1)
            m = pd.concat([piv[a], others], axis=1, keys=["t", "p"]).dropna()
            if len(m) >= wf["recurring_min_pixels"]:
                loyo.append(dict(field_id=fid, year=int(a), fy_key=g[g.year == a].fy_key.iloc[0],
                                 n_pixels=len(m), rho=spearman(m.p, m.t)))
    P, L = pd.DataFrame(pairs), pd.DataFrame(loyo)
    out: dict[str, Any] = {}
    if len(P):
        n, s, l = wf["bootstrap_n"], wf["seed"], wf["ci_level"]
        med, lo, hi = boot_median_ci(P.rho, n, s, l, clusters=P.field_id)
        pm, pl, ph = boot_median_ci(P.pearson, n, s, l, clusters=P.field_id)
        lm, ll, lh = boot_median_ci(L.rho, n, s, l, clusters=L.field_id)
        out = dict(n_pairs=int(len(P)), n_fields=int(P.field_id.nunique()),
                   pair_rho_median=med, pair_rho_ci_field_cluster=[lo, hi],
                   pair_pearson_median=pm, pair_pearson_ci_field_cluster=[pl, ph],
                   frac_pair_rho_pos=float((P.rho > 0).mean()),
                   frac_pair_rho_gt_0_3=float((P.rho > 0.3).mean()),
                   pair_rho_min=float(P.rho.min()), pair_rho_max=float(P.rho.max()),
                   loyo_site_mean_n_fy=int(len(L)), loyo_site_mean_rho_median=lm,
                   loyo_site_mean_rho_ci_field_cluster=[ll, lh])
    return out, P, L


def ablation_deltas(mtab: pd.DataFrame, wf: dict[str, Any]) -> dict[str, Any]:
    """Paired per-field-year differences of rho between feature sets (CI over field-years)."""
    out = {}
    m = mtab[~mtab.shuffle]
    for (cut, kind, scheme), g in m.groupby(["cutoff", "model", "scheme"]):
        p = g.pivot(index="fy_key", columns="fset", values="rho")
        for a, b in (("both", "satellite"), ("both", "terrain"), ("satellite", "terrain")):
            med, lo, hi = boot_median_ci(p[a] - p[b], wf["bootstrap_n"], wf["seed"], wf["ci_level"])
            out[f"{cut}|{kind}|{scheme}|{a}-{b}"] = dict(median_delta_rho=med, ci=[lo, hi], n_fy=int(p[a].notna().sum()))
    return out


def by_year(tab: pd.DataFrame, wf: dict[str, Any]) -> dict[str, Any]:
    """Median rho(index, rel yield) per calendar year + Kruskal-Wallis test across years."""
    from scipy.stats import kruskal

    out = {}
    for (idx, w), g in tab.groupby(["index", "window"]):
        groups = [x.rho.to_numpy() for _, x in g.groupby("year")]
        out[f"{idx}_{w}"] = dict(
            per_year={int(y): dict(n_fy=int(len(x)), rho_median=float(x.rho.median()),
                                   rho_min=float(x.rho.min()), rho_max=float(x.rho.max()))
                      for y, x in g.groupby("year")},
            kruskal_p=float(kruskal(*groups).pvalue) if len(groups) > 1 else np.nan)
    return out


def smoothness(df: pd.DataFrame, wf: dict[str, Any]) -> dict[str, float]:
    """Lag-1 neighbour correlation: kriged yield vs the Sentinel-2 index (kriging smooths -> higher)."""
    w = wf["example_window"]
    ry, rn = [], []
    for _, g in df.groupby("fy_key"):
        ry.append(lag1_corr(g.x.to_numpy(), g.y.to_numpy(), g.rel.to_numpy()))
        v = g[f"ndvi_{w}"]
        if v.notna().sum() >= wf["min_pixels"] and v.notna().all():
            rn.append(lag1_corr(g.x.to_numpy(), g.y.to_numpy(), v.to_numpy()))
    return dict(lag1_rel_yield_median=float(np.nanmedian(ry)), lag1_ndvi_median=float(np.nanmedian(rn)),
                n_fy_yield=len(ry), n_fy_ndvi=len(rn))


# ----------------------------------------------------------------------------------------------
# figures
# ----------------------------------------------------------------------------------------------
def _grid(g: pd.DataFrame, col: str, step: float = 10.0):
    ix = np.round((g.x - g.x.min()) / step).astype(int).to_numpy()
    iy = np.round((g.y - g.y.min()) / step).astype(int).to_numpy()
    a = np.full((iy.max() + 1, ix.max() + 1), np.nan)
    a[iy, ix] = g[col].to_numpy()
    return a


def figure_example(df: pd.DataFrame, tab: pd.DataFrame, wf: dict[str, Any], path: Path) -> str:
    """Yield map vs NDVI map of the field-year with the MEDIAN rho (not cherry-picked)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    w, idx = wf["example_window"], "ndvi"
    t = tab[(tab.window == w) & (tab["index"] == idx)].dropna(subset=["rho"]).sort_values("rho")
    pick = t.iloc[len(t) // 2]
    g = df[df.fy_key == pick.fy_key]
    fig, ax = plt.subplots(1, 3, figsize=(9, 3.1), dpi=100)
    for a, col, title, cmap in ((ax[0], "rel", "Relative pixel yield", "RdYlBu"),
                                (ax[1], f"{idx}_{w}", f"NDVI median {wf['windows'][w][0]} to {wf['windows'][w][1]}",
                                 "viridis")):
        im = a.imshow(_grid(g, col), origin="lower", cmap=cmap, interpolation="nearest")
        a.set_title(title, fontsize=8)
        a.set_xticks([]), a.set_yticks([])
        fig.colorbar(im, ax=a, fraction=0.046, pad=0.02).ax.tick_params(labelsize=7)
    ax[0].contour(_grid(g, "rel") < wf["problem_threshold"], levels=[0.5], colors="k", linewidths=0.6)
    ax[2].scatter(g[f"{idx}_{w}"], g.rel, s=3, alpha=0.4, color="#2b6f9e")
    ax[2].axhline(wf["problem_threshold"], color="k", lw=0.6, ls="--")
    ax[2].set_xlabel("NDVI", fontsize=8), ax[2].set_ylabel("relative pixel yield", fontsize=8)
    ax[2].tick_params(labelsize=7)
    ax[2].set_title(f"Spearman rho = {pick.rho:.2f}, n = {int(pick.n_pixels)}", fontsize=8)
    fig.suptitle(f"{pick.fy_key.split('|')[1].split(':')[1]} {int(pick.year)} (median-rho field-year; "
                 f"black line: relative yield < {wf['problem_threshold']})", fontsize=8)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return str(pick.fy_key)


def figure_bars(ab: dict, wf: dict[str, Any], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    wins, idxs = list(wf["windows"]), wf["indices"]
    fig, ax = plt.subplots(figsize=(5.2, 3.2), dpi=100)
    width = 0.8 / len(idxs)
    colors = {"ndvi": "#2b6f9e", "ndre": "#d98a2b"}
    for j, idx in enumerate(idxs):
        xs, med, err = [], [], [[], []]
        for i, w in enumerate(wins):
            r = ab.get(f"{idx}_{w}")
            if not r:
                continue
            xs.append(i + j * width - 0.4 + width / 2)
            med.append(r["rho_median"])
            err[0].append(r["rho_median"] - r["rho_ci"][0])
            err[1].append(r["rho_ci"][1] - r["rho_median"])
        ax.bar(xs, med, width, yerr=err, capsize=3, color=colors.get(idx, "grey"), label=idx.upper())
        for x, m, k in zip(xs, med, [ab[f"{idx}_{w}"]["n_fy"] for w in wins if f"{idx}_{w}" in ab]):
            ax.text(x, 0.015, f"n={k}", ha="center", fontsize=6, color="white")
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xticks(range(len(wins)))
    ax.set_xticklabels([f"{wf['windows'][w][0]} to\n{wf['windows'][w][1]}" for w in wins], fontsize=7)
    ax.set_ylabel("median Spearman rho (field-years)", fontsize=8)
    ax.set_title("Index vs relative pixel yield, BARC 2017-2021 (95 % CI over field-years)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# ----------------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------------
def git_info() -> str:
    root = repo_path(".")
    h = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=root).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=root).stdout
    return f"{h}\n{'dirty (uncommitted changes)' if dirty.strip() else 'clean'}\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-extract", action="store_true", help="use the pixel cache only, no GEE calls")
    ap.add_argument("--extract-only", action="store_true")
    ap.add_argument("--refresh", action="store_true", help="re-extract cached field-years")
    ap.add_argument("--workers", type=int, default=4, help="parallel GEE requests")
    ap.add_argument("--jobs", type=int, default=4, help="parallel model fits")
    ap.add_argument("--out", default=None, help="results dir (default results/<today>_within_field)")
    args = ap.parse_args()

    cfg = load_config()
    wf = wf_config(cfg)
    px = load_pixels(cfg, wf)
    print(f"pixels inside: {len(px)} in {px.fy_key.nunique()} field-years", flush=True)
    if not args.no_extract:
        extract_all(px, cfg, wf, args.workers, args.refresh)
    if args.extract_only:
        return
    df = load_table(px, cfg)
    val = window_validity(df, wf)

    run = repo_path(args.out) if args.out else repo_path(cfg["paths"]["results"]) / f"{date.today()}_within_field"
    run.mkdir(parents=True, exist_ok=True)
    fig_dir = repo_path(cfg["paths"]["figures"])
    shutil.copy(repo_path("config.yaml"), run / "config.yaml")
    (run / "within_field_config.json").write_text(json.dumps(wf, indent=2), encoding="utf-8")
    (run / "git.txt").write_text(git_info())

    n_all = int(px.fy_key.nunique())
    summary = dict(
        n_fy_requested=n_all, n_fy_with_cache=int(df.fy_key.nunique()), n_pixels_inside=int(len(px)),
        n_points_total=int(px.groupby("fy_key").n_points_all.first().sum()),
        n_fields=int(df.field_id.nunique()), pixels_per_fy_median=float(df.groupby("fy_key").size().median()),
        prevalence_problem_median=float(df.groupby("fy_key").problem.mean().median()),
        n_fy_with_problem_zone=int((df.groupby("fy_key").problem.sum() > 0).sum()),
        rel_cv_median=float(df.groupby("fy_key").rel.std().median()))
    clear_by_window = {w: float(val[(val.window == w) & (val["index"] == wf["indices"][0])].median_clear_images.median())
                       for w in wf["windows"]}
    usable = {f"{i}_{w}": int(val[(val.window == w) & (val["index"] == i)].ok.sum())
              for w in wf["windows"] for i in wf["indices"]}
    ab, tab = analysis_ab(df, val, wf)
    terr, ttab = analysis_terrain(df, wf)
    inner = analysis_interior(df, val, wf)
    models, mtab, dfz = analysis_models(df, val, wf, args.jobs)
    rec, pairs, loyo = analysis_recurring(df, wf)
    abl = ablation_deltas(mtab, wf)
    yr = by_year(tab, wf)
    rec_fy = loyo.fy_key.unique() if len(loyo) else []
    sub = mtab[mtab.fy_key.isin(rec_fy) & ~mtab.shuffle & (mtab.cutoff == wf['example_window'])]
    rec["model_rho_on_same_field_years"] = {
        f"{r.fset}|{r.model}|{r.scheme}": float(g.rho.median())
        for r, g in [(g.iloc[0], g) for _, g in sub.groupby(["fset", "model", "scheme"])]}
    smooth = smoothness(df, wf)
    edge = edge_stats(cfg, wf)

    metrics = dict(date=str(date.today()), summary=summary, usable_field_years=usable,
                   median_clear_images_per_pixel=clear_by_window, index_vs_rel_yield=ab, index_vs_rel_yield_interior=inner,
                   terrain_vs_rel_yield=terr, models=models, ablation_deltas=abl, by_year=yr,
                   recurring=rec, smoothness=smooth, edge=edge)
    tab.to_csv(run / "fy_window_metrics.csv", index=False)
    ttab.to_csv(run / "fy_terrain_metrics.csv", index=False)
    mtab.to_csv(run / "model_fy_metrics.csv", index=False)
    pairs.to_csv(run / "recurring_pairs.csv", index=False)
    loyo.to_csv(run / "recurring_loyo_site_mean.csv", index=False)
    val.to_csv(run / "window_validity.csv", index=False)

    fig_dir.mkdir(parents=True, exist_ok=True)
    metrics["example_field_year"] = figure_example(df, tab, wf, fig_dir / "phase2_within_field_maps.png")
    figure_bars(ab, wf, fig_dir / "phase2_within_field_rho.png")
    (run / "metrics.json").write_text(json.dumps(metrics, indent=2, default=float), encoding="utf-8")
    print(f"done -> {run}", flush=True)


if __name__ == "__main__":
    main()
