"""Feinjustierung F1/F3/F4: baselines, ablation of M1-M4, controls, H3 check (reports/feinjust_vorab.md).

Stages
  baseline  F1.1: reproduce Phase 3 (stress score, Ziel A) and Phase 2.3 (NDVI w2, Ziel B)
  ablation  F3.1-F3.2: A0 / B0 + each feature set, decision rule, kept features together, controls
Usage:  python -m croptransfer.feinjust --stage baseline|ablation
Writes results/<date>_feinjust_<stage>/ (metrics.json, metrics.csv, oof.parquet, config, git hash).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import date

import numpy as np
import pandas as pd

from croptransfer import evaluate, fj_features as fjf, splits, stress, targets
from croptransfer.config import load_config, repo_path
from croptransfer.phase3 import pr_metrics
from croptransfer.run_phase2 import eval_mask, load_features, pool_mask

THR = 0.85
HEALTHY = 0.95
FEATURE_SETS = {
    "M1": ["s1_rvi_mean", "s1_rvi_anom", "s1_vhvv_anom"],
    "M2": ["lst_dt_mean", "lst_anom_mean", "modis_et_ratio", "era5_et_ratio"],
    "M3": ["stress_gdd"],
    "M4": ["emerge_doy", "emerge_anom"],
}
PIXEL_SETS = {"M1": ["s1_vh_w2", "s1_vhvv_w2", "s1_rvi_w2"]}    # M2-M4: n/a for Ziel B (feinjust_vorab §5)


# ------------------------------------------------------------------ inputs ----
def load_inputs(cfg: dict) -> dict:
    """Feature rows at the cutoff, S2 NDVI dekads, S2 observations and daily weather per field-year."""
    from croptransfer.dataset_us import basis_obs, load_obs, weather_by_fy
    from croptransfer.extract_us import load_field_years

    fj = cfg["feinjust"]
    df = load_features(cfg, fj["cutoff"])
    dek = pd.read_parquet(repo_path(cfg["paths"]["processed"]) / "gt_dekads.parquet")
    dek = dek[(dek["index"] == "ndvi") & (dek.basis == fj["basis"])]
    fy = load_field_years(cfg)
    obs = basis_obs(load_obs(cfg), fy)
    s2 = {k: v.get(fj["basis"]) for k, v in obs.items()}
    return {"df": df, "dek": dek, "fy": fy, "s2": s2, "wx": weather_by_fy(cfg, fy)}


def cutoffs(df: pd.DataFrame, mmdd: str) -> dict:
    return {k: date.fromisoformat(f"{int(y)}-{mmdd}") for k, y in zip(df.fy_key, df.year)}


def build_features(cfg: dict, inp: dict) -> tuple[pd.DataFrame, dict]:
    """Field-level M1, M2, M4 features (+ GDD bins for M3, scored inside the folds)."""
    from croptransfer.extract_us import weather_points

    interim = repo_path(cfg["paths"]["interim"])
    df = inp["df"]
    keys = df[(df.sensor_era == "HLS") & (df.year >= cfg["years"]["s2"][0])]
    cut = cutoffs(keys, cfg["feinjust"]["cutoff"])
    ds_of = df.set_index("fy_key").dataset
    out = pd.DataFrame({"fy_key": list(cut)})
    # M1
    raw = pd.concat([pd.read_parquet(f) for f in sorted((interim / "obs_s1").glob("*.parquet"))], ignore_index=True)
    out = out.merge(fjf.s1_field_features(fjf.s1_scene_table(raw, cfg), ds_of, cut, cfg), on="fy_key", how="left")
    # M2
    lst = pd.concat([pd.read_parquet(f) for f in sorted((interim / "obs_lst").glob("*.parquet"))], ignore_index=True)
    tmax = pd.concat([inp["wx"][k][["date", "tmax"]].assign(fy_key=k) for k in cut if k in inp["wx"]])
    out = out.merge(fjf.lst_field_features(lst, tmax, ds_of, cut, cfg), on="fy_key", how="left")
    modis = pd.concat([pd.read_parquet(f) for f in sorted((interim / "obs_et").glob("modis_*.parquet"))])
    out["modis_et_ratio"] = out.fy_key.map(fjf.modis_et_ratio(modis, cut, cfg))
    era = pd.concat([pd.read_parquet(f) for f in sorted((interim / "obs_et").glob("era5_*.parquet"))])
    fy = inp["fy"].set_index("fy_key")
    wpt = pd.Series(weather_points(inp["fy"]).to_numpy(), index=inp["fy"].fy_key)
    out["era5_et_ratio"] = out.fy_key.map(fjf.era5_et_ratio(era, wpt, cut, cfg))
    # M4
    out["emerge_doy"] = [fjf.emergence_doy(inp["s2"].get(k), cut[k], cfg) for k in out.fy_key]
    tmp = out.assign(dataset=out.fy_key.map(ds_of), year=out.fy_key.map(df.set_index("fy_key").year))
    out["emerge_anom"] = fjf.neighbour_anomaly(tmp, "emerge_doy", ["dataset", "year"], cfg["s1"]["min_neighbours"])
    # M3 bins (reference and score need fold labels)
    bins = {k: fjf.gdd_bins(inp["s2"].get(k), inp["wx"].get(k), cut[k], cfg) for k in out.fy_key}
    c = fy.loc[out.fy_key].geometry.centroid
    out["lon"], out["lat"] = c.x.to_numpy(), c.y.to_numpy()
    return out, bins


# ------------------------------------------------------------- Ziel A folds ----
def fold_cache(df: pd.DataFrame, dek: pd.DataFrame, bins: dict, cfg: dict, shuffle_seed: int | None = None,
               folds=None) -> list[dict]:
    """Per LOFYO fold: in-fold labels, reference curves from healthy training rows, scores of train+test rows."""
    fj = cfg["feinjust"]
    basis, mmdd = fj["basis"], fj["cutoff"]
    em = eval_mask(df, basis)
    pool = pool_mask(df, "M-alle", basis, "main")
    rng = np.random.default_rng(shuffle_seed) if shuffle_seed is not None else None
    out = []
    for name, tr, te in folds or splits.lofyo(df, em):
        ry_tr, ry_te = targets.ry_in_fold(df, tr, te)
        ry_tr = ry_tr.dropna()
        if rng is not None:
            ry_tr = pd.Series(rng.permutation(ry_tr.to_numpy()), index=ry_tr.index)
        healthy = df.loc[ry_tr.index[(ry_tr >= HEALTHY) & (df.loc[ry_tr.index, "sensor_era"] == "HLS")], "fy_key"]
        ref = stress.reference_curve(dek, healthy, basis=basis)
        gref = fjf.gdd_reference(bins, healthy)
        fit = ry_tr.index[pool.loc[ry_tr.index]]
        te = ry_te.index[ry_te.notna()]

        def scores(idx):
            k = df.loc[idx, "fy_key"]
            return pd.DataFrame({"fy_key": k.to_numpy(), "dataset": df.loc[idx, "dataset"].to_numpy(),
                                 "year": df.loc[idx, "year"].to_numpy(),
                                 "score": [stress.stress_score(dek, x, ref, mmdd, basis=basis) for x in k],
                                 "stress_gdd": [fjf.gdd_score(bins.get(x), gref) for x in k]})

        train = scores(fit).assign(y=(ry_tr.loc[fit] < THR).astype(int).to_numpy())
        test = scores(te).assign(ry=ry_te.loc[te].to_numpy())
        out.append({"name": name, "train": train, "test": test})
    return out


def logreg_oof(folds: list[dict], feat: pd.DataFrame, cols: list[str], cfg: dict) -> pd.DataFrame:
    """Out-of-fold P(at risk) of the pre-registered logistic regression on [score] + cols."""
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    use = ["score"] + [c for c in cols if c != "score"]
    extra = [c for c in use if c not in ("score", "stress_gdd")]
    res = []
    for f in folds:
        tr = f["train"].merge(feat[["fy_key"] + extra], on="fy_key", how="left") if extra else f["train"]
        te = f["test"].merge(feat[["fy_key"] + extra], on="fy_key", how="left") if extra else f["test"]
        Xtr, Xte = tr[use].to_numpy(float), te[use].to_numpy(float)
        if tr.y.nunique() < 2:
            p = np.full(len(te), tr.y.mean())
        else:
            m = make_pipeline(SimpleImputer(strategy="median", keep_empty_features=True), StandardScaler(),
                              LogisticRegression(C=cfg["feinjust"]["logreg_C"], class_weight="balanced", max_iter=1000))
            m.fit(Xtr, tr.y.to_numpy())
            p = m.predict_proba(Xte)[:, 1]
        res.append(te[["fy_key", "dataset", "year", "ry"]].assign(p=p, fold=f["name"]))
    return pd.concat(res, ignore_index=True)


def raw_oof(folds: list[dict]) -> pd.DataFrame:
    """A-roh: risk = -stress score (Phase 3)."""
    return pd.concat([f["test"].assign(p=-f["test"].score, fold=f["name"]) for f in folds], ignore_index=True)


def within_site_year(oof: pd.DataFrame, min_n: int = 5) -> dict:
    """Median over site-years (both classes present, n >= min_n) of PR-AUC - prevalence and rho(-risk, RY)."""
    rows = []
    for (ds, yr), g in oof.dropna(subset=["p"]).groupby(["dataset", "year"]):
        y = (g.ry < THR).astype(int).to_numpy()
        if len(g) >= min_n and 0 < y.sum() < len(g):
            rows.append({"cluster": f"{ds}-{yr}", "n": len(g), "pos": int(y.sum()),
                         "pr_auc_minus_prev": evaluate.pr_auc(y, g.p) - y.mean(),
                         "rho": evaluate._spearman(-g.p.to_numpy(), g.ry.to_numpy())})
    t = pd.DataFrame(rows)
    if t.empty:
        return {"n_site_years": 0}
    return {"n_site_years": int(len(t)), "median_pr_auc_minus_prev": float(t.pr_auc_minus_prev.median()),
            "median_rho": float(t.rho.median()), "per_site_year": t.round(3).to_dict("records")}


def metrics_A(oof: pd.DataFrame, cfg: dict) -> dict:
    cl = oof.dataset + "-" + oof.year.astype(str)
    m = pr_metrics(oof.ry < THR, oof.p, cl, cfg)
    m["within"] = within_site_year(oof)
    return m


def delta_A(new: pd.DataFrame, base: pd.DataFrame, cfg: dict) -> dict:
    """PR-AUC(new) - PR-AUC(base) on identical rows, paired cluster bootstrap."""
    j = base[["fy_key", "dataset", "year", "ry", "p"]].merge(new[["fy_key", "p"]], on="fy_key", suffixes=("_b", "_n"))
    y = (j.ry < THR).astype(int).to_numpy()
    a, b = j.p_n.to_numpy(), j.p_b.to_numpy()
    d = evaluate.pr_auc(y, a) - evaluate.pr_auc(y, b)
    cl = pd.Series((j.dataset + "-" + j.year.astype(str)).to_numpy())
    bs = [evaluate.pr_auc(y[i], a[i]) - evaluate.pr_auc(y[i], b[i])
          for i in evaluate._boot_clusters(cl, cfg["validation"]["bootstrap_n"], cfg["seed"])]
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return {"delta": float(d), "lo": float(lo), "hi": float(hi), "n": int(len(j))}


# ------------------------------------------------------------------ Ziel B ----
def pixel_table(cfg: dict) -> tuple[pd.DataFrame, dict, dict]:
    """BARC pixels with S2 window composites and the S1 window composite (M1), + NDVI-w2 reproduction."""
    from croptransfer import within_field as wfm

    wf = wfm.wf_config(cfg)
    wf["ridge_alpha"] = cfg["feinjust"]["ridge_alpha"]
    px = wfm.load_pixels(cfg, wf)
    df = wfm.load_table(px, cfg)
    val = wfm.window_validity(df, wf)
    ab, _ = wfm.analysis_ab(df, val, wf)
    cache = repo_path(cfg["paths"]["interim"]) / "obs_s1" / "pixels"
    parts = []
    for key, g in df.groupby("fy_key", sort=False):
        f = cache / f"{wfm.safe_name(key)}.parquet"
        g = g.sort_values(["y", "x"]).reset_index(drop=True)
        if f.exists():
            s = pd.read_parquet(f).sort_values("pid").reset_index(drop=True)
            assert len(s) == len(g) and np.allclose(s.x, g.x) and np.allclose(s.y, g.y), key
            g = pd.concat([g, s[PIXEL_SETS["M1"] + ["s1_n_w2"]]], axis=1)
        parts.append(g)
    d = pd.concat(parts, ignore_index=True)
    w = cfg["feinjust"]["within_window"]
    ok = val[(val.window == w) & (val["index"] == "ndvi") & val.ok].fy_key
    d = d[d.fy_key.isin(ok)]
    return d, ab, wf


def run_B(d: pd.DataFrame, wf: dict, cols: list[str], shuffle: bool = False) -> tuple[dict, pd.DataFrame]:
    from croptransfer import within_field as wfm

    d = d[np.isfinite(d[cols]).all(axis=1)].reset_index(drop=True)
    z = wfm.zscore_within(d, cols)
    d = pd.concat([d, z], axis=1)
    pred = wfm.run_scheme(d, [f"z_{c}" for c in cols], "ridge", "lofo", wf, shuffle)
    m, t = wfm.eval_oof(d, pred, wf)
    lo, hi = _median_ci_fields(t, wf)
    m["rho_ci_field_cluster"] = [lo, hi]
    return m, t


def _median_ci_fields(t: pd.DataFrame, wf: dict) -> tuple[float, float]:
    from croptransfer import within_field as wfm

    _, lo, hi = wfm.boot_median_ci(t.rho, wf["bootstrap_n"], wf["seed"], wf["ci_level"], clusters=t.field_id)
    return lo, hi


def delta_B(t_new: pd.DataFrame, t_base: pd.DataFrame, wf: dict) -> dict:
    """median rho(new) - median rho(base) over common field-years, paired bootstrap over fields."""
    j = t_base[["fy_key", "field_id", "rho"]].merge(t_new[["fy_key", "rho"]], on="fy_key", suffixes=("_b", "_n"))
    d = float(j.rho_n.median() - j.rho_b.median())
    rng = np.random.default_rng(wf["seed"])
    fields = j.field_id.unique()
    idx = {f: np.flatnonzero(j.field_id.to_numpy() == f) for f in fields}
    bs = []
    for _ in range(wf["bootstrap_n"]):
        pick = np.concatenate([idx[f] for f in rng.choice(fields, len(fields), replace=True)])
        bs.append(np.median(j.rho_n.to_numpy()[pick]) - np.median(j.rho_b.to_numpy()[pick]))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"delta": d, "lo": float(lo), "hi": float(hi), "n_fy": int(len(j))}


# ---------------------------------------------------------------- controls ----
def lodo_A(df, dek, bins, feat, cols, cfg, a: str, b: str) -> pd.DataFrame:
    """Train on dataset a only (labels, reference), test on dataset b (descriptive RY)."""
    em = eval_mask(df, cfg["feinjust"]["basis"])
    tr = df.index[df.dataset == a]
    te = df.index[(df.dataset == b) & em]
    ry_tr = targets.compute_ry(df.loc[tr], df.loc[tr], df.loc[tr]).dropna()
    ry_te = targets.ry_descriptive(df).loc[te].dropna()
    fold = _single_fold(df, dek, bins, cfg, ry_tr, ry_te, f"{a}->{b}")
    return logreg_oof([fold], feat, cols, cfg)


def _single_fold(df, dek, bins, cfg, ry_tr, ry_te, name):
    fj = cfg["feinjust"]
    pool = pool_mask(df, "M-alle", fj["basis"], "main")
    healthy = df.loc[ry_tr.index[(ry_tr >= HEALTHY) & (df.loc[ry_tr.index, "sensor_era"] == "HLS")], "fy_key"]
    ref = stress.reference_curve(dek, healthy, basis=fj["basis"])
    gref = fjf.gdd_reference(bins, healthy)
    fit = ry_tr.index[pool.loc[ry_tr.index]]

    def scores(idx):
        k = df.loc[idx, "fy_key"]
        return pd.DataFrame({"fy_key": k.to_numpy(), "dataset": df.loc[idx, "dataset"].to_numpy(),
                             "year": df.loc[idx, "year"].to_numpy(),
                             "score": [stress.stress_score(dek, x, ref, fj["cutoff"], basis=fj["basis"]) for x in k],
                             "stress_gdd": [fjf.gdd_score(bins.get(x), gref) for x in k]})

    return {"name": name, "train": scores(fit).assign(y=(ry_tr.loc[fit] < THR).astype(int).to_numpy()),
            "test": scores(ry_te.index).assign(ry=ry_te.to_numpy())}


def adversarial(folds, feat, cols, cfg) -> dict:
    """Per fold: can a shallow classifier tell training from test rows? (5-fold CV AUC)."""
    from lightgbm import LGBMClassifier
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.metrics import roc_auc_score

    use = ["score"] + [c for c in cols if c != "score"]
    extra = [c for c in use if c not in ("score", "stress_gdd")]
    aucs, imp = [], pd.Series(0.0, index=use)
    for f in folds:
        X = pd.concat([f["train"], f["test"]], ignore_index=True)
        X = X.merge(feat[["fy_key"] + extra], on="fy_key", how="left") if extra else X
        y = np.r_[np.zeros(len(f["train"])), np.ones(len(f["test"]))]
        if y.sum() < 5:
            continue
        clf = LGBMClassifier(max_depth=2, num_leaves=4, n_estimators=100, learning_rate=0.05,
                             min_child_samples=5, verbose=-1, random_state=cfg["seed"])
        p = cross_val_predict(clf, X[use], y, cv=StratifiedKFold(5, shuffle=True, random_state=cfg["seed"]),
                              method="predict_proba")[:, 1]
        aucs.append(roc_auc_score(y, p))
        imp += pd.Series(clf.fit(X[use], y).feature_importances_, index=use)
    return {"n_folds": len(aucs), "median_auc": float(np.median(aucs)) if aucs else np.nan,
            "max_auc": float(np.max(aucs)) if aucs else np.nan,
            "importance": (imp / max(imp.sum(), 1)).round(3).to_dict()}


# -------------------------------------------------------------------- main ----
def _rundir(cfg, stage):
    run = repo_path(cfg["paths"]["results"]) / f"{date.today().isoformat()}_feinjust_{stage}"
    run.mkdir(parents=True, exist_ok=True)
    shutil.copy(repo_path("config.yaml"), run / "config.yaml")
    (run / "git.txt").write_text(subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout)
    return run


def stage_baseline(cfg) -> dict:
    run = _rundir(cfg, "baseline")
    inp = load_inputs(cfg)
    df = inp["df"]
    folds = fold_cache(df, inp["dek"], {}, cfg)
    oof_raw, oof_a0 = raw_oof(folds), logreg_oof(folds, pd.DataFrame({"fy_key": []}), [], cfg)
    d, ab, wf = pixel_table(cfg)
    mB0, tB0 = run_B(d, wf, ["ndvi_w2"])
    reported = {"A_roh_pr_auc": 0.71, "B_roh_rho": 0.676}
    out = {"A_roh": metrics_A(oof_raw, cfg), "A0": metrics_A(oof_a0, cfg),
           "B_roh": ab["ndvi_w2"], "B0": mB0, "reported": reported}
    out["gate_H1"] = {
        "A_roh_within_0.02": bool(abs(out["A_roh"]["pr_auc"] - reported["A_roh_pr_auc"]) <= 0.02),
        "B_roh_within_0.02": bool(abs(out["B_roh"]["rho_median"] - reported["B_roh_rho"]) <= 0.02)}
    out["gate_H1"]["passed"] = all(out["gate_H1"].values())
    pd.concat([oof_raw.assign(model="A_roh"), oof_a0.assign(model="A0")]).to_parquet(run / "oof.parquet")
    (run / "metrics.json").write_text(json.dumps(out, indent=2, default=float))
    return out


def decide(dA: dict | None, dB: dict | None, fj: dict) -> dict:
    """Pre-registered keep rule (Plan section 3)."""
    k, loss = fj["keep_delta_min"], fj["other_loss_max"]
    a = dA or {"delta": 0.0, "lo": 0.0}
    b = dB or {"delta": 0.0, "lo": 0.0}
    gain_a = a["delta"] >= k and a["lo"] > 0
    gain_b = b["delta"] >= k and b["lo"] > 0
    ok_other = (not gain_a or b["delta"] >= -loss) and (not gain_b or a["delta"] >= -loss)
    return {"gain_A": bool(gain_a), "gain_B": bool(gain_b), "other_ok": bool(ok_other),
            "keep": bool((gain_a or gain_b) and ok_other)}


def stage_ablation(cfg) -> dict:
    fj = cfg["feinjust"]
    run = _rundir(cfg, "ablation")
    inp = load_inputs(cfg)
    df, dek = inp["df"], inp["dek"]
    feat, bins = build_features(cfg, inp)
    feat.to_parquet(run / "features.parquet")
    folds = fold_cache(df, dek, bins, cfg)
    oofs = {"A_roh": raw_oof(folds), "A0": logreg_oof(folds, feat, [], cfg)}
    for m, cols in FEATURE_SETS.items():
        oofs[f"A0+{m}"] = logreg_oof(folds, feat, cols, cfg)
    d, ab, wf = pixel_table(cfg)
    s1cols = PIXEL_SETS["M1"]
    d = d[np.isfinite(d[["ndvi_w2"] + s1cols]).all(axis=1)]          # identical rows for B0 and B0+M1
    resB = {"B0": run_B(d, wf, ["ndvi_w2"]), "B0+M1": run_B(d, wf, ["ndvi_w2"] + s1cols)}
    out: dict = {"A": {k: metrics_A(v, cfg) for k, v in oofs.items()},
                 "B": {k: v[0] for k, v in resB.items()}, "decision": {}, "B_roh": ab["ndvi_w2"]}
    rows = []
    for m in FEATURE_SETS:
        dA = delta_A(oofs[f"A0+{m}"], oofs["A0"], cfg)
        dB = delta_B(resB[f"B0+{m}"][1], resB["B0"][1], wf) if m in PIXEL_SETS else None
        dec = decide(dA, dB, fj)
        out["decision"][m] = {"delta_A": dA, "delta_B": dB, **dec}
        a = out["A"][f"A0+{m}"]
        rows.append({"feature_set": m, "pr_auc": a["pr_auc"], "pr_auc_lo": a["pr_auc_lo"], "pr_auc_hi": a["pr_auc_hi"],
                     "recall_at_20fpr": a["recall_at_20fpr"], "dA": dA["delta"], "dA_lo": dA["lo"], "dA_hi": dA["hi"],
                     "dB": dB["delta"] if dB else np.nan, "dB_lo": dB["lo"] if dB else np.nan,
                     "dB_hi": dB["hi"] if dB else np.nan, "keep": dec["keep"]})
        print(m, json.dumps(rows[-1], default=float), flush=True)
    kept = [m for m in FEATURE_SETS if out["decision"][m]["keep"]]
    out["kept"] = kept
    cols_main = [c for m in kept for c in FEATURE_SETS[m]]
    pix_main = ["ndvi_w2"] + [c for m in kept if m in PIXEL_SETS for c in PIXEL_SETS[m]]
    if kept:
        oofs["A0+kept"] = logreg_oof(folds, feat, cols_main, cfg)
        out["A"]["A0+kept"] = metrics_A(oofs["A0+kept"], cfg)
        out["delta_kept_A"] = delta_A(oofs["A0+kept"], oofs["A0"], cfg)
        if len(pix_main) > 1:
            resB["B0+kept"] = run_B(d, wf, pix_main)
            out["B"]["B0+kept"] = resB["B0+kept"][0]
            out["delta_kept_B"] = delta_B(resB["B0+kept"][1], resB["B0"][1], wf)
    main_a = "A0+kept" if kept else "A0"
    main_b = "B0+kept" if "B0+kept" in resB else "B0"
    out["main_model"] = {"A": main_a, "B": main_b, "A_cols": ["score"] + cols_main, "B_cols": pix_main}
    out["controls"] = controls(df, dek, bins, feat, folds, oofs[main_a], cols_main, d, wf, pix_main, cfg)
    pd.DataFrame(rows).to_csv(run / "metrics.csv", index=False)
    pd.concat([v.assign(model=k) for k, v in oofs.items()]).to_parquet(run / "oof.parquet")
    pd.concat([v[1].assign(model=k) for k, v in resB.items()]).to_parquet(run / "oof_within.parquet")
    (run / "metrics.json").write_text(json.dumps(out, indent=2, default=float))
    (run / "controls.json").write_text(json.dumps(out["controls"], indent=2, default=float))
    return out


def controls(df, dek, bins, feat, folds, oof_main, cols, d, wf, pix_cols, cfg) -> dict:
    fj = cfg["feinjust"]
    out = {}
    sh = []
    for s in range(fj["shuffle_repeats"]):
        f = fold_cache(df, dek, bins, cfg, shuffle_seed=cfg["seed"] + s)
        sh.append(metrics_A(logreg_oof(f, feat, cols, cfg), cfg)["pr_auc"])
    prev = float((oof_main.ry < THR).mean())
    out["label_shuffle_A"] = {"repeats": len(sh), "mean_pr_auc": float(np.mean(sh)), "sd": float(np.std(sh)),
                              "prevalence": prev}
    mB, _ = run_B(d, wf, pix_cols, shuffle=True)
    out["label_shuffle_B"] = {"rho_median": mB["rho_median"], "rho_ci": mB["rho_ci"]}
    base = metrics_A(oof_main, cfg)["pr_auc"]
    oc = logreg_oof(folds, feat, cols + ["lat", "lon"], cfg)
    out["coordinates"] = {"pr_auc_with_latlon": metrics_A(oc, cfg)["pr_auc"], "pr_auc_main": base,
                          "delta": delta_A(oc, oof_main, cfg)}
    out["adversarial"] = adversarial(folds, feat, cols, cfg)
    out["lodo"] = {}
    for a, b in [("KBS", "BARC"), ("BARC", "KBS")]:
        o = lodo_A(df, dek, bins, feat, cols, cfg, a, b)
        full = oof_main[oof_main.dataset == b]
        cl_o, cl_f = o.dataset + "-" + o.year.astype(str), full.dataset + "-" + full.year.astype(str)
        mo, mf = pr_metrics(o.ry < THR, o.p, cl_o, cfg), pr_metrics(full.ry < THR, full.p, cl_f, cfg)
        out["lodo"][f"{a}->{b}"] = {"pr_auc_lodo": mo["pr_auc"], "pr_auc_full_same_rows": mf["pr_auc"],
                                    "loss": float(mf["pr_auc"] - mo["pr_auc"]), "n": mo["n"],
                                    "positives": mo["positives"]}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", choices=["baseline", "ablation"], required=True)
    a = ap.parse_args()
    cfg = load_config()
    out = stage_baseline(cfg) if a.stage == "baseline" else stage_ablation(cfg)
    print(json.dumps(out, indent=1, default=float)[:6000])


if __name__ == "__main__":
    main()
