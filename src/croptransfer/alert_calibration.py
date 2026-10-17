"""Alert logic for "Dein Feld, dein Verlauf" (DECISIONS 2026-10-17, pre-registered before this ran).

Target E_X: the field-year ends with RY < 1 - X/100. Signal: frozen stress score (freeze-at-1) at cutoff t.
Rule: alert if score(t) <= s*(t, X), where s* is the largest threshold that alerts at most 20 % of the
field-years without E_X. Hit rates are out-of-fold (leave-one-site-year-out); inside each fold the
reference curve and s* come only from the other site-years. The frozen s* use all US data and the frozen
reference curve. US data only (KBS, BARC, Colorado); nothing Austrian is read.

Usage:  python -m croptransfer.alert_calibration
Writes: results/<date>_alert_calibration/{calibration.json, oof.csv, git.txt}
"""

from __future__ import annotations

import json
import subprocess
from datetime import date

import numpy as np
import pandas as pd

from croptransfer import at_test
from croptransfer import timeseries as ts
from croptransfer.config import load_config, repo_path

CUTOFFS = ["06-01", "06-15", "07-01", "07-15", "08-01", "08-15", "09-01"]
THRESHOLDS_PCT = [10, 15, 20, 25, 30]
MAX_FPR = 0.20
HEALTHY_RY = 0.95
MIN_ALERTS, MIN_SITE_YEARS, MIN_EVENTS = 10, 3, 5
N_BOOT, SEED = 1000, 42


def us_dekad_matrix(cfg) -> pd.DataFrame:
    """fy_key x dekad matrix of observed HLS-NDVI dekad medians, same code path as the frozen score."""
    files = sorted(repo_path("data/interim/obs").glob("*_HLS.parquet"))
    obs = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    obs = ts.valid_obs(ts.add_indices(ts.to_reflectance(obs)), cfg["field"]["clear_frac_min"])
    return at_test.dekad_matrix(obs)


def labels(cfg) -> pd.DataFrame:
    """US HLS-era field-years with RY_descr; cluster = dataset x year (shared weather)."""
    proc = repo_path(cfg["paths"]["processed"])
    f = pd.read_parquet(proc / "features_0901.parquet", columns=["fy_key", "dataset", "year", "RY_descr", "sensor_era"])
    assert set(f.dataset) <= {"KBS", "BARC", "Colorado"}, "only US training data allowed"
    f = f[(f.sensor_era == "HLS") & f.RY_descr.notna()].copy()
    f["cluster"] = f.dataset + "|" + f.year.astype(str)
    return f.set_index("fy_key")


def reference_from(mat: pd.DataFrame, keys) -> pd.Series:
    """Median observed NDVI per dekad over the given field-years (= stress.reference_curve on the same data)."""
    return mat.loc[mat.index.intersection(list(keys))].median(axis=0, skipna=True)


def threshold_for(neg_scores: np.ndarray, max_fpr: float = MAX_FPR) -> float:
    """Largest s with share(neg <= s) <= max_fpr; -inf if not even one negative may be alerted."""
    neg = np.sort(neg_scores[np.isfinite(neg_scores)])
    allowed = int(np.floor(max_fpr * len(neg)))
    if allowed == 0:
        return -np.inf
    best = -np.inf
    for c in np.unique(neg):
        if (neg <= c).sum() <= allowed:
            best = c
    return float(best)


def scores(mat: pd.DataFrame, ref: pd.Series, cutoff: str, cfg) -> pd.Series:
    sc = cfg["at_test"]
    return at_test.scores_from_matrix(mat, ref, cutoff, sc["stress"]["first_dekad"], sc["min_observed_dekads"]).score


def out_of_fold(mat: pd.DataFrame, lab: pd.DataFrame, cfg) -> pd.DataFrame:
    """One row per (field-year, cutoff, X): OOF score, fold threshold, alert flag, event flag."""
    rows = []
    for c in sorted(lab.cluster.unique()):
        test = lab[lab.cluster == c]
        train = lab[lab.cluster != c]
        ref = reference_from(mat, train.index[train.RY_descr >= HEALTHY_RY])
        for t in CUTOFFS:
            s_all = scores(mat.loc[mat.index.intersection(lab.index)], ref, t, cfg)
            s_tr, s_te = s_all.reindex(train.index), s_all.reindex(test.index)
            for x in THRESHOLDS_PCT:
                ev_tr = train.RY_descr < 1 - x / 100
                thr = threshold_for(s_tr[~ev_tr].to_numpy())
                for k in test.index:
                    s = s_te.get(k, np.nan)
                    rows.append({"fy_key": k, "cluster": c, "cutoff": t, "x_pct": x, "score": s,
                                 "threshold": thr, "valid": bool(np.isfinite(s)),
                                 "alert": bool(np.isfinite(s) and s <= thr),
                                 "event": bool(test.loc[k, "RY_descr"] < 1 - x / 100), "ry": float(test.loc[k, "RY_descr"])})
    return pd.DataFrame(rows)


def _precision_ci(g: pd.DataFrame, rng: np.random.Generator) -> tuple[float, float]:
    """Cluster bootstrap (site-years) of the precision among valid field-years."""
    cl = g.cluster.unique()
    vals = []
    by = {c: g[g.cluster == c] for c in cl}
    for _ in range(N_BOOT):
        pick = pd.concat([by[c] for c in rng.choice(cl, size=len(cl), replace=True)])
        a = pick[pick.alert]
        if len(a):
            vals.append(a.event.mean())
    if not vals:
        return (np.nan, np.nan)
    return (float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975)))


def summarise(oof: pd.DataFrame) -> list[dict]:
    rng = np.random.default_rng(SEED)
    out = []
    for (t, x), g in oof.groupby(["cutoff", "x_pct"], sort=False):
        v = g[g.valid]
        a = v[v.alert]
        n_alert, k_hit = int(len(a)), int(a.event.sum())
        n_event = int(v.event.sum())
        n_neg = int((~v.event).sum())
        reasons = []
        if len(v) == 0:
            reasons.append("no valid score before this cutoff")
        if n_alert < MIN_ALERTS:
            reasons.append(f"fewer than {MIN_ALERTS} alerts")
        if a.cluster.nunique() < MIN_SITE_YEARS:
            reasons.append(f"alerts from fewer than {MIN_SITE_YEARS} site-years")
        if n_event < MIN_EVENTS:
            reasons.append(f"fewer than {MIN_EVENTS} events")
        lo, hi = _precision_ci(v, rng) if n_alert else (np.nan, np.nan)
        out.append({
            "cutoff": t, "x_pct": x, "n_valid": int(len(v)), "n_site_years": int(v.cluster.nunique()),
            "n_event": n_event, "prevalence": n_event / len(v) if len(v) else None,
            "n_alert": n_alert, "k_hit": k_hit, "precision": k_hit / n_alert if n_alert else None,
            "precision_ci": [lo, hi], "recall": k_hit / n_event if n_event else None,
            "fpr": int((a.event == False).sum()) / n_neg if n_neg else None,  # noqa: E712
            "alert_site_years": int(a.cluster.nunique()),
            "statement": "ok" if not reasons else "no_statement", "reasons": reasons,
        })
    return out


def frozen_thresholds(mat: pd.DataFrame, lab: pd.DataFrame, cfg) -> dict:
    """s*(t, X) with the frozen reference curve (freeze-at-1) on all US field-years."""
    ref = pd.read_csv(repo_path("reports/freeze_at/stress_reference_hls_ndvi.csv"), index_col=0)["ndvi_median"]
    out = {}
    for t in CUTOFFS:
        s = scores(mat.loc[mat.index.intersection(lab.index)], ref, t, cfg).reindex(lab.index)
        for x in THRESHOLDS_PCT:
            thr = threshold_for(s[~(lab.RY_descr < 1 - x / 100)].to_numpy())
            out[f"{t}|{x}"] = None if not np.isfinite(thr) else round(thr, 6)
    return out


def main() -> None:
    cfg = load_config()
    mat = us_dekad_matrix(cfg)
    lab = labels(cfg)
    lab = lab[lab.index.isin(mat.index)]
    oof = out_of_fold(mat, lab, cfg)
    table = summarise(oof)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    res = {
        "date": date.today().isoformat(), "commit": commit, "decision": "DECISIONS.md 2026-10-17 Warnlogik",
        "n_field_years": int(len(lab)), "n_site_years": int(lab.cluster.nunique()),
        "rules": {"max_fpr": MAX_FPR, "min_alerts": MIN_ALERTS, "min_site_years": MIN_SITE_YEARS,
                  "min_events": MIN_EVENTS, "healthy_ry": HEALTHY_RY, "first_dekad": cfg["at_test"]["stress"]["first_dekad"],
                  "min_observed_dekads": cfg["at_test"]["min_observed_dekads"]},
        "table": table, "frozen_thresholds": frozen_thresholds(mat, lab, cfg),
    }
    out = repo_path("results") / f"{date.today().isoformat()}_alert_calibration"
    out.mkdir(parents=True, exist_ok=True)
    (out / "calibration.json").write_text(json.dumps(res, indent=2, default=float), encoding="utf-8")
    oof.to_csv(out / "oof.csv", index=False)
    (out / "git.txt").write_text(commit + "\n", encoding="utf-8")
    view = pd.DataFrame(table)[["cutoff", "x_pct", "n_valid", "n_event", "n_alert", "k_hit", "precision", "recall", "fpr", "alert_site_years", "statement"]]
    print(view.to_string(index=False))


if __name__ == "__main__":
    main()
