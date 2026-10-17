"""Austria test (protocol `reports/freeze_protocol_at.md`, tag freeze-at-1): scores, trial yields, V1/V2 metrics.

Everything here applies the frozen definitions unchanged. The yield columns of `at_trials.csv` and the
Statistik-Austria yields are opened only by `trial_yields()` / `region_yields()`, i.e. after the freeze.

Usage:  python -m croptransfer.at_test
Writes: results/<date>_at_test/{field_scores.parquet, site_year.csv, region_year.csv, metrics.json, qc.json}
"""

from __future__ import annotations

import json
from datetime import date

import numpy as np
import pandas as pd

from croptransfer import evaluate, stress
from croptransfer import regional_cybench as rc
from croptransfer import timeseries as ts
from croptransfer.config import load_config, repo_path

NUTS_OF = {"Burgenland": "AT11", "Niederösterreich": "AT12", "Kärnten": "AT21", "Steiermark": "AT22",
           "Oberösterreich": "AT31"}
BL_KEY = {"Steiermark": "Steiermark", "Oberoesterreich": "Oberösterreich"}


# ------------------------------------------------------------------------------------------ fields
def load_field_obs(cfg) -> pd.DataFrame:
    """Valid HLS scenes of all sampled parcels (clear_frac >= 0.7), duplicates from shared parcels removed."""
    files = sorted((repo_path("data/interim/at") / "obs").glob("*_HLS.parquet"))
    obs = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    obs = obs.drop_duplicates(["fy_key", "date", "img_id"])
    obs = ts.add_indices(ts.to_reflectance(obs))
    return ts.valid_obs(obs, cfg["field"]["clear_frac_min"])


def dekad_matrix(obs: pd.DataFrame, index: str = "ndvi") -> pd.DataFrame:
    """fy_key x dekad(0..20) matrix of observed dekad medians (NaN = not observed); no interpolation."""
    o = obs[["fy_key", "date", index]].dropna().copy()
    o["dk"] = ts.dekad_index(o["date"])
    o = o[(o.dk >= 0)]
    m = o.groupby(["fy_key", "dk"])[index].median().unstack("dk")
    return m.reindex(columns=range(21))


def scores_from_matrix(mat: pd.DataFrame, ref: pd.Series, cutoff: str, first_dekad: int,
                       min_obs: int) -> pd.DataFrame:
    """Frozen stress score (same definition as stress.stress_score) for all fields at once."""
    k = stress.last_complete_dekad(cutoff)
    cols = [d for d in range(first_dekad, k + 1)]
    sub = mat[cols]
    dev = np.minimum(sub.to_numpy() - ref.reindex(cols).to_numpy()[None, :], 0.0)
    dev[np.isnan(sub.to_numpy())] = np.nan
    n = np.isfinite(dev).sum(axis=1)
    score = np.where(n >= min_obs, np.nanmean(np.where(np.isfinite(dev), dev, np.nan), axis=1), np.nan)
    return pd.DataFrame({"score": score, "n_obs": n}, index=mat.index)


def field_table(cfg) -> pd.DataFrame:
    atc = cfg["at_test"]
    ref = pd.read_csv(repo_path("reports/freeze_at/stress_reference_hls_ndvi.csv"), index_col=0)["ndvi_median"]
    obs = load_field_obs(cfg)
    mat = dekad_matrix(obs)
    out = pd.DataFrame(index=mat.index)
    for c in atc["cutoffs"]:
        s = scores_from_matrix(mat, ref, c, atc["stress"]["first_dekad"], atc["min_observed_dekads"])
        out[f"score_{c}"], out[f"nobs_{c}"] = s.score, s.n_obs
    lo, hi = atc["baseline_ndvi_dekads"]
    out["ndvi_base"] = mat[list(range(lo, hi + 1))].mean(axis=1)
    out["ndvi_peak"] = mat.max(axis=1)
    out["n_dekads_obs"] = mat.notna().sum(axis=1)
    out["abrupt_drop"] = [stress.abrupt_drop(pd.DataFrame({"dekad": r.dropna().index, "value": r.dropna().to_numpy()}))
                          for _, r in mat.iterrows()]
    out["year"] = out.index.str.split("|").str[1].astype(int)
    return out.reset_index(names="fy_key")


def site_year_scores(fields: pd.DataFrame, cfg) -> pd.DataFrame:
    """Mean score over the valid fields of each site-year (>= min_fields_per_site_year, else NaN + flag)."""
    atc = cfg["at_test"]
    mem = pd.read_csv(repo_path("data/interim/at/membership.csv"))
    d = mem.merge(fields, on=["fy_key"], how="left", suffixes=("", "_f"))
    rows = []
    for (site, year), g in d.groupby(["site", "year"]):
        row = {"site": site, "year": int(year), "n_sampled": len(g)}
        for c in atc["cutoffs"]:
            v = g[f"score_{c}"].dropna()
            row[f"n_valid_{c}"] = len(v)
            row[f"score_{c}"] = float(v.mean()) if len(v) >= atc["min_fields_per_site_year"] else np.nan
        v = g["ndvi_base"].dropna()
        row["ndvi_base"] = float(v.mean()) if len(v) >= atc["min_fields_per_site_year"] else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------ yields
def trial_yields(cfg, path=None) -> pd.DataFrame:
    """Y(c,y) per site cluster and year (protocol section 2) -> columns site, year, y_t_ha."""
    atc = cfg["at_test"]
    t = pd.read_csv(path or repo_path("data/raw/at_trials.csv"))
    alias = {a: k for k, s in atc["sites"].items() for a in s["aliases"]}
    t = t[t.trial_type.isin(atc["trial_types"]) & t.site.isin(alias)].copy()
    t["cluster"] = t.site.map(alias)
    per_type = []
    for (c, y, tt), g in t.groupby(["cluster", "year", "trial_type"]):
        use = g[g.variant.isin(atc["trial_mean_variants"])]
        per_type.append({"site": c, "year": int(y), "trial_type": tt,
                         "y": float((use if len(use) else g).yield_t_ha.mean())})
    pt = pd.DataFrame(per_type)
    out = pt.groupby(["site", "year"]).y.mean().rename("y_t_ha").reset_index()
    out["n_trial_types"] = pt.groupby(["site", "year"]).size().to_numpy()
    return out


def yas_site(y: pd.DataFrame) -> pd.DataFrame:
    """YAS_site: 5 complete previous years (olympic mean) else mean of >= 3 other years (flagged)."""
    rows = []
    for site, g in y.groupby("site"):
        look = dict(zip(g.year, g.y_t_ha))
        for yr, val in look.items():
            prior = [look.get(yr - k) for k in range(1, 6)]
            if all(p is not None for p in prior):
                base, flag = rc.olympic_mean(prior), "prior5"
            else:
                others = [v for k, v in look.items() if k != yr]
                base, flag = (float(np.mean(others)), "baseline_short") if len(others) >= 3 else (np.nan, "none")
            rows.append({"site": site, "year": int(yr), "y_t_ha": val, "baseline": base,
                         "yas_site": val / base if base == base else np.nan, "baseline_kind": flag})
    return pd.DataFrame(rows)


def region_yields(cfg) -> pd.DataFrame:
    """Statistik Austria grain maize per Bundesland (t/ha, 14 %) and its YAS (5 previous years, olympic mean)."""
    s = pd.read_csv(repo_path("data/raw/stat_at_maize.csv"))
    s = s[s.bundesland.isin(NUTS_OF)].copy()
    s["adm_id"] = s.bundesland.map(NUTS_OF)
    s = s.rename(columns={"yield_t_ha": "yield"})[["adm_id", "year", "yield"]]
    s = s[s["yield"] > 0]
    return rc.add_yas(s, cfg["targets"]["yas_baseline_years"], cfg["cybench"]["trend_window_years"],
                      cfg["cybench"]["trend_min_years"])


# ------------------------------------------------------------------------------------------ regional model
def at_regional_features(cfg, cutoff: str, years: tuple[int, int] | None = None) -> pd.DataFrame:
    """Predictors of the five maize NUTS-2 regions (CY-Bench AT files) in the frozen feature layout."""
    cy, atc = cfg["cybench"], cfg["at_test"]["regional"]
    raw = repo_path(cy["raw_dir"]) / "AT"
    season_start, last = cfg["season"]["start_mmdd"], cfg["cutoffs"]["yield_model"][-1]
    feats = None
    for source, variables in cy["variables"].items():
        daily, _ = rc.read_daily_source(raw / f"{source}_maize_AT.csv", variables, tuple(years or atc["years"]), season_start, last,
                                        cy["availability_lag_days"].get(source, 0), cy["valid_ranges"])
        agg = rc.aggregate_asof(daily, variables, cy["sum_variables"], cutoff, season_start)
        feats = agg if feats is None else feats.merge(agg, on=["adm_id", "year"], how="outer")
    soil = pd.read_csv(raw / "soil_maize_AT.csv", usecols=["adm_id", *cy["static_features"]])
    feats = feats.merge(soil, on="adm_id", how="left")
    return feats[feats.adm_id.isin(NUTS_OF.values())].reset_index(drop=True)


def regional_predictions(cfg) -> pd.DataFrame:
    fz = cfg["cybench"]["freeze"]
    out = []
    for c in cfg["at_test"]["cutoffs"]:
        f = at_regional_features(cfg, c)
        f[f"pred_{c}"] = rc.predict_zero_shot(f, c, repo_path(fz["dir"]), repo_path(fz["protocol"]))
        out.append(f[["adm_id", "year", f"pred_{c}"]].set_index(["adm_id", "year"]))
    return pd.concat(out, axis=1).reset_index()


# ------------------------------------------------------------------------------------------ metrics
def rho_ci(x, y, clusters, cfg) -> dict:
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    n, ncl = int(ok.sum()), int(pd.Series(np.asarray(clusters)[ok]).nunique())
    if n < 4 or ncl < 3:
        return {"n": n, "clusters": ncl, "rho": np.nan, "lo": np.nan, "hi": np.nan}
    r, lo, hi = evaluate.spearman_ci(x[ok], y[ok], np.asarray(clusters)[ok], cfg["validation"]["bootstrap_n"], cfg["seed"])
    return {"n": n, "clusters": ncl, "rho": r, "lo": lo, "hi": hi}


def passed(m: dict, min_n: int = 0) -> str:
    if not np.isfinite(m["rho"]) or m["n"] < min_n:
        return "nicht auswertbar"
    return "bestanden" if m["lo"] > 0 else "nicht belegt"


def descriptive_within(df: pd.DataFrame, pred: str, target: str, by: str, min_n: int) -> dict:
    vals = {}
    for k, g in df.dropna(subset=[pred, target]).groupby(by):
        if len(g) >= min_n:
            vals[str(k)] = evaluate._spearman(g[pred].to_numpy(), g[target].to_numpy())
    v = np.array([x for x in vals.values() if np.isfinite(x)])
    return {"per_group": {k: round(x, 3) for k, x in vals.items()}, "median": float(np.median(v)) if len(v) else np.nan,
            "n_groups": int(len(v))}


def leave_one_year_out(df: pd.DataFrame, pred: str, target: str) -> dict:
    d = df.dropna(subset=[pred, target])
    return {int(y): round(evaluate._spearman(d[d.year != y][pred].to_numpy(), d[d.year != y][target].to_numpy()), 3)
            for y in sorted(d.year.unique()) if (d.year != y).sum() >= 5}


def qc_summary(fields: pd.DataFrame, sy: pd.DataFrame, cfg) -> dict:
    """Data-critique numbers (protocol section 5): validity, maize-likeness, early harvest, clouds, exclusions."""
    atc = cfg["at_test"]
    c = atc["primary_cutoff"]
    f = fields.copy()
    f["valid"] = f[f"score_{c}"].notna()
    by_year = f.groupby("year").agg(fields=("fy_key", "size"), valid_share=("valid", "mean"),
                                    median_dekads_obs=("n_dekads_obs", "median"),
                                    peak_lt_06=("ndvi_peak", lambda s: float((s < 0.6).mean())),
                                    abrupt_drop=("abrupt_drop", "mean"))
    low = sy[sy[f"score_{c}"].isna()][["site", "year", f"n_valid_{c}"]]
    mem = pd.read_csv(repo_path("data/interim/at/membership.csv"))
    sd_within = f.merge(mem, on="fy_key").groupby(["site", "year"])[f"score_{c}"].std().mean()
    return {"by_year": by_year.round(3).to_dict("index"),
            "share_not_maize_like_peak_lt_0.6": float((f.ndvi_peak < 0.6).mean()),
            "share_abrupt_drop": float(f.abrupt_drop.mean()),
            "share_valid_fields": float(f.valid.mean()),
            "site_years_total": int(len(sy)), "site_years_excluded_lt_min_fields": low.to_dict("records"),
            "score_sd_within_site_year": float(sd_within),
            "score_sd_between_site_year_means": float(sy[f"score_{c}"].std())}


def main() -> None:
    cfg = load_config()
    atc = cfg["at_test"]
    out = repo_path(f"results/{date.today().isoformat()}_at_test")
    out.mkdir(parents=True, exist_ok=True)
    fields = field_table(cfg)
    fields.to_parquet(out / "field_scores.parquet")
    sy = site_year_scores(fields, cfg)
    (out / "qc.json").write_text(json.dumps(qc_summary(fields, sy, cfg), indent=2, default=float), encoding="utf-8")

    # yields only now
    y = yas_site(trial_yields(cfg))
    sy = sy.merge(y, on=["site", "year"], how="left")
    sy["bundesland"] = sy.site.map({k: v["bundesland"] for k, v in atc["sites"].items()})
    sy["nuts2"] = sy.bundesland.map(atc["regional"]["site_region"])
    reg_pred = regional_predictions(cfg)
    reg_y = region_yields(cfg)
    reg = reg_y.merge(reg_pred, on=["adm_id", "year"], how="inner")
    reg = reg[reg.yas.notna()].copy()
    sy = sy.merge(reg_pred.rename(columns={"adm_id": "nuts2"}), on=["nuts2", "year"], how="left")
    # V1-A: mean of site-year mean scores per region and year (sites of that Bundesland)
    rev = {v: k for k, v in NUTS_OF.items()}
    sy["land"] = sy.nuts2.map(rev)
    for c in atc["cutoffs"]:
        m = sy.groupby(["nuts2", "year"])[f"score_{c}"].mean().rename(f"score_{c}").reset_index().rename(columns={"nuts2": "adm_id"})
        reg = reg.merge(m, on=["adm_id", "year"], how="left")
    sy.to_csv(out / "site_year.csv", index=False)
    reg.to_csv(out / "region_year.csv", index=False)

    res: dict = {"protocol": "reports/freeze_protocol_at.md", "tag": "freeze-at-1", "cutoffs": {}}
    v2 = sy[sy.yas_site.notna()]
    for c in atc["cutoffs"]:
        r: dict = {}
        r["V2-A_stress_score"] = rho_ci(v2[f"score_{c}"], v2.yas_site, v2.year, cfg)
        r["V2-A_stress_score"]["verdict"] = passed(r["V2-A_stress_score"], atc["min_site_years_v2"])
        r["V2-A_within_site"] = descriptive_within(v2, f"score_{c}", "yas_site", "site", atc["min_years_within_site"])
        r["V2-A_within_year"] = descriptive_within(v2, f"score_{c}", "yas_site", "year", 5)
        r["V2-A_leave_one_year_out"] = leave_one_year_out(v2, f"score_{c}", "yas_site")
        r["V2-B_regional_model"] = rho_ci(v2[f"pred_{c}"], v2.yas_site, v2.year, cfg)
        r["V2-B_regional_model"]["verdict"] = passed(r["V2-B_regional_model"], atc["min_site_years_v2"])
        r["V2-baseline_NDVI"] = rho_ci(v2.ndvi_base, v2.yas_site, v2.year, cfg) if c == atc["primary_cutoff"] else None
        r["V1_regional_model"] = rho_ci(reg[f"pred_{c}"], reg.yas, reg.year, cfg)
        ok = reg[f"pred_{c}"].notna() & reg.yas.notna()
        d, lo, hi = evaluate.rmse_diff_ci(reg.yas[ok], reg[f"pred_{c}"][ok], np.ones(ok.sum()), reg.year[ok], cfg["validation"]["bootstrap_n"], cfg["seed"])
        r["V1_regional_model"].update({"rmse_model": evaluate.rmse(reg.yas[ok], reg[f"pred_{c}"][ok]),
                                       "rmse_yas1": evaluate.rmse(reg.yas[ok], np.ones(ok.sum())),
                                       "rmse_diff": d, "rmse_diff_lo": lo, "rmse_diff_hi": hi})
        v1 = r["V1_regional_model"]
        v1["verdict"] = passed(v1)
        v1["strong"] = bool(v1["verdict"] == "bestanden" and hi < 0)
        r["V1-A_stress_score_region"] = rho_ci(reg[f"score_{c}"], reg.yas, reg.year, cfg)
        r["V1-A_stress_score_region"]["verdict"] = passed(r["V1-A_stress_score_region"])
        r["V1_within_year_regional_model"] = descriptive_within(reg, f"pred_{c}", "yas", "year", 4)
        res["cutoffs"][c] = r
    res["counts"] = {"site_years_with_yas": int(len(v2)), "site_years_with_score": int(sy[f"score_{atc['primary_cutoff']}"].notna().sum()),
                     "region_years": int(len(reg)), "sites_with_ge6_years": int((v2.groupby("site").size() >= atc["min_years_within_site"]).sum())}
    (out / "metrics.json").write_text(json.dumps(res, indent=2, default=float, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, default=float, ensure_ascii=False)[:6000])


if __name__ == "__main__":
    main()
