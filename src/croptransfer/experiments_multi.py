"""Multi-crop experiments E1-E5 and the D10 criteria (plan_mehrkultur.md Etappe 4; DECISIONS 2026-10-16).

Only training-side data (no Austria). One model round, everything reported. Outputs under
results/<date>_mehrkultur/ : metrics.csv, criteria.json, oof.parquet.

Usage:  python -m croptransfer.experiments_multi [--h 30] [--boot 1000]
"""

from __future__ import annotations

import argparse
import json
from datetime import date

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.model_selection import GroupKFold

from croptransfer import evaluate as ev
from croptransfer.config import load_config, repo_path
from croptransfer.splits import lofyo

WEATHER = ["gdd", "prec", "cwb", "cwb_30d", "prec_30d", "heat32_flower", "tmax_jun", "vpd_jun",
           "rzwsi_jun", "rzwsi_flower", "prec_spring", "rad_30d"]
SAT = ["k1_ndvi_max", "k2_ndvi_auc", "k3_evi_max", "k4_ndmi_mean60", "k5_ndvi_last"]
ALPHAS = np.logspace(0, 4, 9)
MIN_CELL_YEARS, SEED, N_GROUPS = 40, 42, 3


# ------------------------------------------------------------------------------ data -----
def prepare(h: int, use_sat: bool, cfg=None, tiers: tuple[str, ...] = ("S2",)) -> pd.DataFrame:
    """Rows with RY, weather and (if use_sat) a valid curve + all K features; adds cluster and field_group."""
    cfg = cfg or load_config()
    d = pd.read_parquet(repo_path(cfg["paths"]["processed"]) / f"features_multi_h{h:03d}.parquet")
    d = d[d.tier.isin(tiers) & d.RY.notna()].dropna(subset=WEATHER).copy()
    if use_sat:
        d = d[d.curve_ok].dropna(subset=SAT)
    d["cluster"] = d.cell_id + "_" + d.year.astype(int).astype(str)
    d["field_group"] = add_group(d)
    return d.reset_index(drop=True)


def add_group(d: pd.DataFrame, block_deg: float = 0.5) -> pd.Series:
    """Spatial group 0..N_GROUPS-1 from the 0.5 degree block (stable hash, no RNG)."""
    blk = np.floor(d.lat / block_deg).astype(int).astype(str) + "_" + np.floor(d.lon / block_deg).astype(int).astype(str)
    return pd.Series([sum(map(ord, b)) % N_GROUPS for b in blk], index=d.index)


def cell_years(d: pd.DataFrame) -> pd.Series:
    return d.drop_duplicates(["crop", "cell_id", "year"]).groupby("crop").size()


# ----------------------------------------------------------------------------- models -----
def relative_sat(train: pd.DataFrame, test: pd.DataFrame, cols=SAT) -> tuple[pd.DataFrame, pd.DataFrame]:
    """D8: subtract per crop the median of the training rows with RY >= 0.95 (training fold only)."""
    tr, te = train.copy(), test.copy()
    for crop, g in train.groupby("crop"):
        ref = g.loc[g.RY >= 0.95, cols].median()
        if ref.isna().any():
            ref = g[cols].median()
        for df in (tr, te):
            m = df.crop == crop
            df.loc[m, cols] = df.loc[m, cols] - ref
    return tr, te


def _alpha_ridge(X: np.ndarray, y: np.ndarray, groups: np.ndarray) -> Ridge:
    n_splits = min(5, len(np.unique(groups)))
    if n_splits < 2:
        return Ridge(alpha=100.0).fit(X, y)
    cv = list(GroupKFold(n_splits=n_splits).split(X, y, groups))
    return RidgeCV(alphas=ALPHAS, cv=cv).fit(X, y)


def _standardize(train: pd.DataFrame, test: pd.DataFrame, cols: list[str], scale_ref: pd.DataFrame | None = None):
    """Per-crop z-scores. Stats come from the training rows of that crop (or, for crops absent from the
    training set, from the unlabeled feature rows ``scale_ref`` of the target crop - no labels)."""
    def stats(g):
        return g[cols].mean(), g[cols].std(ddof=0).replace(0, 1.0)
    out = []
    for df, ref in ((train, None), (test, scale_ref)):
        z = df[cols].copy()
        for crop in df.crop.unique():
            m = df.crop == crop
            src = train[train.crop == crop]
            if len(src) < 5:
                src = (ref if ref is not None else df)[(ref if ref is not None else df).crop == crop]
            mu, sd = stats(src)
            z.loc[m] = (df.loc[m, cols] - mu) / sd
        out.append(z)
    return out[0].to_numpy(), out[1].to_numpy()


def predict(model: str, train: pd.DataFrame, test: pd.DataFrame, feats: list[str],
            sat: bool, scale_ref: pd.DataFrame | None = None) -> np.ndarray:
    """Out-of-sample RY prediction for ``test`` rows."""
    tr, te = (relative_sat(train, test) if sat else (train, test))
    cols = feats + (SAT if sat else [])
    if model == "B0":
        mu = tr.groupby("crop").RY.mean()
        return te.crop.map(mu).fillna(tr.RY.mean()).to_numpy()
    if model == "B1":
        pred = np.full(len(te), tr.RY.mean())
        for crop, g in tr.groupby("crop"):
            m = (te.crop == crop).to_numpy()
            if m.any() and len(g) >= 5 and g.cwb_30d.std() > 0:
                b = np.polyfit(g.cwb_30d, g.RY, 1)
                pred[m] = np.polyval(b, te.cwb_30d[m])
        return pred
    if model == "M-Kultur":
        pred = np.full(len(te), tr.RY.mean())
        for crop, g in tr.groupby("crop"):
            m = (te.crop == crop).to_numpy()
            if not m.any() or len(g) < 15:
                continue
            Xtr, Xte = _standardize(g, te[m], cols)
            mdl = _alpha_ridge(Xtr, g.RY.to_numpy(), g.cluster.to_numpy())
            pred[m] = mdl.predict(Xte)
        return pred
    if model in ("M-Pool", "M-Pool-ohne-Mais"):
        crops = sorted(set(tr.crop))
        Xtr, Xte = _standardize(tr, te, cols, scale_ref)
        dtr = np.column_stack([(tr.crop == c).to_numpy(float) for c in crops])
        dte = np.column_stack([(te.crop == c).to_numpy(float) for c in crops])
        mdl = _alpha_ridge(np.hstack([Xtr, dtr]), tr.RY.to_numpy(), tr.cluster.to_numpy())
        return mdl.predict(np.hstack([Xte, dte]))
    raise ValueError(model)


# ----------------------------------------------------------------------------- CV runs -----
def run_cv(d: pd.DataFrame, models: list[str], sat: bool, feats=WEATHER) -> pd.DataFrame:
    """LOFYO folds (D9): out-of-fold predictions for every model; returns d with pred_<model> columns."""
    out = d.copy()
    for m in models:
        out[f"pred_{m}"] = np.nan
    for name, tr_idx, te_idx in lofyo(d):
        for m in models:
            out.loc[te_idx, f"pred_{m}"] = predict(m, d.loc[tr_idx], d.loc[te_idx], feats, sat)
    return out


def run_transfer(d: pd.DataFrame, test_crop: str, sat: bool, train_crops: list[str] | None = None) -> pd.DataFrame:
    """Kultur-Transfer (E4): train on other crops, test on ``test_crop`` (unsupervised scaling of its features)."""
    te = d[d.crop == test_crop].copy()
    tr = d[(d.crop != test_crop) & (d.crop.isin(train_crops) if train_crops else True)]
    te["pred_M-Pool-ohne-Mais"] = predict("M-Pool-ohne-Mais", tr, te, WEATHER, sat, scale_ref=te)
    te["pred_B0"] = predict("B0", tr, te, WEATHER, sat)
    return te


def within_fold_median_rho(oof: pd.DataFrame, model: str, min_n: int = 5) -> float:
    rhos = []
    for _, g in oof.groupby(["year", "field_group"]):
        if len(g) >= min_n:
            r = ev._spearman(g[f"pred_{model}"].to_numpy(), g.RY.to_numpy())
            if not np.isnan(r):
                rhos.append(r)
    return float(np.median(rhos)) if rhos else np.nan


def metrics(oof: pd.DataFrame, models: list[str], n_boot: int) -> pd.DataFrame:
    """Per crop and pooled: rho (CI), RMSE difference to B0 / B1 (CI)."""
    rows = []
    for crop, g in [("ALL", oof)] + list(oof.groupby("crop")):
        for m in models:
            if m in ("B0", "B1"):
                continue
            rho, lo, hi = ev.spearman_ci(g[f"pred_{m}"], g.RY, g.cluster, n_boot, SEED)
            r = dict(crop=crop, model=m, n=len(g), cell_years=g.drop_duplicates(["cell_id", "year"]).shape[0],
                     rho=rho, rho_lo=lo, rho_hi=hi)
            for b in ("B0", "B1"):
                dd, dl, dh = ev.rmse_diff_ci(g.RY, g[f"pred_{m}"], g[f"pred_{b}"], g.cluster, n_boot, SEED)
                r.update({f"d_rmse_{b}": dd, f"d_rmse_{b}_lo": dl, f"d_rmse_{b}_hi": dh})
            rows.append(r)
    return pd.DataFrame(rows)


def label_shuffle(d: pd.DataFrame, sat: bool, model: str, n_boot: int, reps: int = 3) -> list[dict]:
    res = []
    for k in range(reps):
        s = d.copy()
        s["RY"] = np.random.default_rng(SEED + k).permutation(s.RY.to_numpy())
        o = run_cv(s, ["B0", "B1", model], sat)
        rho, lo, hi = ev.spearman_ci(o[f"pred_{model}"], o.RY, o.cluster, n_boot, SEED)
        dd, dl, dh = ev.rmse_diff_ci(o.RY, o[f"pred_{model}"], o.pred_B0, o.cluster, n_boot, SEED)
        res.append(dict(rep=k, rho=rho, rho_lo=lo, rho_hi=hi, d_rmse_B0=dd, d_rmse_B0_lo=dl, d_rmse_B0_hi=dh))
    return res


def criteria(met: pd.DataFrame, main: str, transfer: dict, shuffle: list[dict]) -> dict:
    """D10 (1)-(5) from the metric tables."""
    mm = met[met.model == main].set_index("crop")
    judged = [c for c in mm.index if c != "ALL" and mm.loc[c, "cell_years"] >= MIN_CELL_YEARS]
    unjudged = [c for c in mm.index if c != "ALL" and mm.loc[c, "cell_years"] < MIN_CELL_YEARS]
    beats = {c: bool(mm.loc[c, "d_rmse_B0_hi"] < 0 and mm.loc[c, "d_rmse_B1_hi"] < 0) for c in judged}
    maize_ok = beats.get("maize", False)
    c1 = maize_ok and sum(beats.values()) >= len(judged) / 2
    rho_all, rho_maize = float(mm.loc["ALL", "rho"]), float(mm.loc["maize", "rho"]) if "maize" in mm.index else np.nan
    c2 = rho_all >= 0.4 and rho_maize >= 0.3
    c3 = bool(transfer.get("rho_lo", -1) > 0)
    c4 = all(s["rho_lo"] <= 0 <= s["rho_hi"] and s["d_rmse_B0_lo"] <= 0 <= s["d_rmse_B0_hi"] or s["d_rmse_B0_lo"] > 0
             for s in shuffle)
    return {"1_beats_B0_B1": {"passed": bool(c1), "per_crop": beats},
            "2_rho": {"passed": bool(c2), "rho_all": rho_all, "rho_maize": rho_maize},
            "3_crop_transfer": {"passed": c3, **transfer},
            "4_label_shuffle": {"passed": bool(c4), "runs": shuffle},
            "5_not_assessable_crops": unjudged,
            "main_model": main, "all_passed": bool(c1 and c2 and c3 and c4)}


def run_controls(h: int, n_boot: int, cfg) -> dict:
    """E4b / E5: wheat->maize transfer, coordinate ablation, leave-one-dataset-out, adversarial validation,
    runs with S3 / S4 rows added (weather only). Every number is a diagnostic, none is used to pick a model."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score

    res: dict = {}
    d = prepare(h, True, cfg)
    ww = run_transfer(d, "maize", True, train_crops=["winter_wheat"])
    rho, lo, hi = ev.spearman_ci(ww["pred_M-Pool-ohne-Mais"], ww.RY, ww.cluster, n_boot, SEED)
    res["transfer_wheat_to_maize"] = dict(n=len(ww), rho=rho, rho_lo=lo, rho_hi=hi)
    # coordinate ablation: add lat/lon (standardised) to the pooled model; large gain = location proxy
    d2 = d.copy()
    d2["lat_f"], d2["lon_f"] = d2.lat, d2.lon
    base = run_cv(d2, ["B0", "M-Pool"], True)
    coords = run_cv(d2, ["B0", "M-Pool"], True, feats=WEATHER + ["lat_f", "lon_f"])
    res["coordinate_ablation"] = dict(
        rho_without=ev.spearman_ci(base["pred_M-Pool"], base.RY, base.cluster, n_boot, SEED),
        rho_with=ev.spearman_ci(coords["pred_M-Pool"], coords.RY, coords.cluster, n_boot, SEED))
    # leave-one-dataset-out (train on all other datasets of ALL crops, test on one dataset)
    lodo = {}
    for ds in sorted(d.dataset.unique()):
        te = d[d.dataset == ds]
        tr = d[d.dataset != ds]
        if len(te) < 20 or tr.crop.nunique() < 1:
            continue
        p = predict("M-Pool-ohne-Mais", tr, te, WEATHER, True, scale_ref=te)
        lodo[ds] = dict(n=len(te), rho=ev._spearman(p, te.RY.to_numpy()))
    res["leave_one_dataset_out"] = lodo
    # adversarial validation: can weather features tell maize from wheat rows (crop shift diagnostic)
    X = (d[WEATHER] - d[WEATHER].mean()) / d[WEATHER].std(ddof=0)
    y = (d.crop == "maize").astype(int)
    if y.nunique() == 2:
        gk = list(GroupKFold(5).split(X, y, d.cluster))
        pr = np.zeros(len(d))
        for a, b in gk:
            pr[b] = LogisticRegression(max_iter=500).fit(X.iloc[a], y.iloc[a]).predict_proba(X.iloc[b])[:, 1]
        res["adversarial_auc_maize_vs_rest"] = float(roc_auc_score(y, pr))
    # more rows: S3 and S4 added, weather only
    for label, tiers in (("with_S3", ("S2", "S3")), ("with_S3_S4", ("S2", "S3", "S4"))):
        dw = prepare(h, False, cfg, tiers=tiers)
        o = run_cv(dw, ["B0", "B1", "M-Kultur", "M-Pool"], False)
        mt = metrics(o, ["B0", "B1", "M-Kultur", "M-Pool"], n_boot)
        res[label] = mt[(mt.crop == "ALL")][["model", "n", "rho", "rho_lo", "rho_hi", "d_rmse_B0", "d_rmse_B0_lo", "d_rmse_B0_hi"]].to_dict("records")
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--h", type=int, default=30)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    cfg = load_config()
    out = repo_path(cfg["paths"]["results"]) / (args.out or f"{date.today().isoformat()}_mehrkultur_h{args.h:03d}")
    out.mkdir(parents=True, exist_ok=True)
    models = ["B0", "B1", "M-Kultur", "M-Pool"]
    runs = {}
    for label, sat in (("weather", False), ("weather+sat", True)):
        d = prepare(args.h, sat, cfg)
        cy = cell_years(d)
        print(label, len(d), "rows; cell-years:", cy.to_dict(), flush=True)
        oof = run_cv(d, models, sat)
        met = metrics(oof, models, args.boot)
        met["run"] = label
        runs[label] = (d, oof, met)
        oof.to_parquet(out / f"oof_{label.replace('+', '_')}.parquet", index=False)
    allmet = pd.concat([r[2] for r in runs.values()], ignore_index=True)
    allmet.to_csv(out / "metrics.csv", index=False)
    # main run = weather+sat (pre-registered main model rule)
    d, oof, met = runs["weather+sat"]
    main_model = max(["M-Kultur", "M-Pool"], key=lambda m: (within_fold_median_rho(oof, m) if not np.isnan(within_fold_median_rho(oof, m)) else -9, m == "M-Kultur"))
    tr = run_transfer(d, "maize", True)
    rho, lo, hi = ev.spearman_ci(tr["pred_M-Pool-ohne-Mais"], tr.RY, tr.cluster, args.boot, SEED)
    transfer = dict(n=len(tr), rho=rho, rho_lo=lo, rho_hi=hi)
    shuffle = label_shuffle(d, True, main_model, args.boot)
    crit = criteria(met, main_model, transfer, shuffle)
    ctrl = run_controls(args.h, args.boot, cfg)
    (out / "controls.json").write_text(json.dumps(ctrl, indent=2, default=float), encoding="utf-8")
    print(json.dumps(ctrl, indent=2, default=float))
    (out / "criteria.json").write_text(json.dumps(crit, indent=2, default=float), encoding="utf-8")
    print(json.dumps(crit, indent=2, default=float))
    print(allmet.round(3).to_string())


if __name__ == "__main__":
    main()
