"""Regional re-training with Austrian Bundesland yields (addendum F5, `reports/plan_at_nachtraining.md`).

R0 frozen EU model | R1 linear recalibration | R2 EU + Austrian rows (weight 20), all validated leave-one-year-out
over 2015-2023. Reported side by side; no winner is chosen.

Usage:  python -m croptransfer.at_retrain
"""

from __future__ import annotations

import json
from datetime import date

import lightgbm as lgb
import numpy as np
import pandas as pd

from croptransfer import at_test, evaluate
from croptransfer import regional_cybench as rc
from croptransfer.config import load_config, repo_path

YEARS = (2015, 2023)
CUTOFFS = ["08-01", "09-01"]
AT_WEIGHT = 20.0


def fit_linear(p: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """OLS y = a + b p (b fixed to 0 if p has no variance)."""
    if np.ptp(p) == 0:
        return float(np.mean(y)), 0.0
    b, a = np.polyfit(p, y, 1)
    return float(a), float(b)


def retrain_predict(eu: pd.DataFrame, at_train: pd.DataFrame, at_test_rows: pd.DataFrame, meta: dict,
                    cfg: dict, weight: float = AT_WEIGHT) -> np.ndarray:
    """EU rows (weight 1) + Austrian training rows (weight `weight`), hyperparameters from the frozen meta."""
    feats = meta["features"]
    X = np.vstack([eu[feats].to_numpy(np.float32), at_train[feats].to_numpy(np.float32)])
    y = np.concatenate([eu["yas"].to_numpy(float), at_train["yas"].to_numpy(float)])
    w = np.concatenate([np.ones(len(eu)), np.full(len(at_train), weight)])
    ds = lgb.Dataset(X, label=y, weight=w, feature_name=feats, params={"verbose": -1, "max_bin": 255})
    booster = lgb.train(meta["lightgbm_params"], ds, num_boost_round=meta["n_estimators"])
    return booster.predict(at_test_rows[feats].to_numpy(np.float32), num_iteration=meta["n_estimators"])


def loyo(rows: pd.DataFrame, eu: pd.DataFrame, meta: dict, cfg: dict, cutoff: str) -> pd.DataFrame:
    out = rows[["adm_id", "year", "yas", "pred_r0"]].copy()
    out["pred_r1"], out["pred_r2"] = np.nan, np.nan
    for yr in sorted(rows.year.unique()):
        tr, te = rows[rows.year != yr], rows[rows.year == yr]
        a, b = fit_linear(tr.pred_r0.to_numpy(), tr.yas.to_numpy())
        out.loc[te.index, "pred_r1"] = a + b * te.pred_r0.to_numpy()
        out.loc[te.index, "pred_r2"] = retrain_predict(eu, tr, te, meta, cfg)
    return out


def summarise(o: pd.DataFrame, cfg: dict) -> dict:
    res = {}
    n_boot, seed = cfg["validation"]["bootstrap_n"], cfg["seed"]
    for k in ["pred_r0", "pred_r1", "pred_r2"]:
        r = at_test.rho_ci(o[k], o.yas, o.year, cfg)
        d1, lo1, hi1 = evaluate.rmse_diff_ci(o.yas, o[k], np.ones(len(o)), o.year, n_boot, seed)
        entry = {**r, "rmse": evaluate.rmse(o.yas, o[k]), "rmse_diff_vs_yas1": d1, "rmse_diff_vs_yas1_lo": lo1,
                 "rmse_diff_vs_yas1_hi": hi1,
                 "within_year": at_test.descriptive_within(o, k, "yas", "year", 4)}
        if k != "pred_r0":
            d0, lo0, hi0 = evaluate.rmse_diff_ci(o.yas, o[k], o.pred_r0, o.year, n_boot, seed)
            entry.update({"rmse_diff_vs_r0": d0, "rmse_diff_vs_r0_lo": lo0, "rmse_diff_vs_r0_hi": hi0,
                          "improves_r0": bool(hi0 < 0)})
        res[k] = entry
    res["rmse_yas1"] = evaluate.rmse(o.yas, np.ones(len(o)))
    res["n"] = int(len(o))
    return res


def main() -> None:
    cfg = load_config()
    out_dir = repo_path(f"results/{date.today().isoformat()}_at_retrain")
    out_dir.mkdir(parents=True, exist_ok=True)
    data, _ = rc.load_dataset(cfg)
    reg_y = at_test.region_yields(cfg)
    fz = cfg["cybench"]["freeze"]
    res: dict = {"plan": "reports/plan_at_nachtraining.md", "at_weight": AT_WEIGHT, "years": YEARS, "cutoffs": {}}
    for c in CUTOFFS:
        f = at_test.at_regional_features(cfg, c, YEARS)
        rows = f.merge(reg_y[["adm_id", "year", "yas"]], on=["adm_id", "year"], how="inner")
        rows = rows[rows.yas.notna()].reset_index(drop=True)
        rows["pred_r0"] = rc.predict_zero_shot(rows, c, repo_path(fz["dir"]), repo_path(fz["protocol"]))
        meta = json.loads((repo_path(fz["dir"]) / f"lgbm_{rc.cutoff_tag(c)}_meta.json").read_text(encoding="utf-8"))
        eu = data[c].dropna(subset=["yas"])
        assert "AT" not in set(eu["country"]), "Austria must not be in the EU rows"
        o = loyo(rows, eu, meta, cfg, c)
        o.to_csv(out_dir / f"loyo_{rc.cutoff_tag(c)}.csv", index=False)
        res["cutoffs"][c] = summarise(o, cfg)
        # additional evaluation of R0 on the registered test years only (same rows as V1) for reference
        sub = o[o.year >= 2018]
        res["cutoffs"][c]["r0_2018_2023"] = at_test.rho_ci(sub.pred_r0, sub.yas, sub.year, cfg)
    (out_dir / "metrics.json").write_text(json.dumps(res, indent=2, default=float), encoding="utf-8")
    print(json.dumps(res, indent=1, default=float)[:5000])


if __name__ == "__main__":
    main()
