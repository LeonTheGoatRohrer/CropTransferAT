"""Austria test III: data critique of the 2026 scores (AGENTS section 3). Descriptive only; nothing here changes the test.

Question: are the very low 2026 scores real crop stress, or an artefact (single hazy scene, one sensor, early harvest,
a 2026-wide shift, the first INVEKOS version)? Control sites are read without yields.

Usage:  python -m croptransfer.at_test3_review
Writes: <results_dir>/review_2026.json, reports/figures/at_test3_curves.png, reports/figures/at_test3_scatter.png
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from croptransfer import at_test, at_test3, gee_extract, stress
from croptransfer import timeseries as ts
from croptransfer.config import load_config, repo_path

# Upper Austria, descriptive. Linden and Mauthausen were chosen before any 2026 value was computed; the other three were
# added afterwards because they are the remaining sites with a 2026 trial yield (protocol review of 2026-11-06).
CONTROL_SITES = ["linden", "mauthausen", "walding", "wimsbach", "innviertel"]
CONTROL_BASE = "data/interim/at3/control_2026"
SCORE_CUTOFF = "09-01"


def read_obs(cfg, site: str, year: int, base: str | None = None) -> pd.DataFrame:
    base = base or ("data/interim/at3/2026" if year == 2026 else "data/interim/at")
    o = pd.read_parquet(repo_path(base) / "obs" / f"{site}_{year}_HLS.parquet").drop_duplicates(["fy_key", "date", "img_id"])
    return ts.valid_obs(ts.add_indices(ts.to_reflectance(o)), cfg["field"]["clear_frac_min"])


def mean_score(mat: pd.DataFrame, ref: pd.Series, cfg) -> float:
    atc = cfg["at_test"]
    s = at_test.scores_from_matrix(mat, ref, SCORE_CUTOFF, atc["stress"]["first_dekad"], atc["min_observed_dekads"]).score.dropna()
    return float(s.mean()) if len(s) >= atc["min_fields_per_site_year"] else float("nan")


def drops(mat: pd.DataFrame) -> pd.Series:
    return pd.Series([stress.abrupt_drop(pd.DataFrame({"dekad": r.dropna().index, "value": r.dropna().to_numpy()}))
                      for _, r in mat.iterrows()], index=mat.index)


def site_year_row(cfg, ref: pd.Series, site: str, year: int, base: str | None = None) -> tuple[dict, pd.Series]:
    """Field-level checks of one site-year -> summary row, median NDVI per dekad."""
    obs = read_obs(cfg, site, year, base)
    mat = at_test.dekad_matrix(obs)
    dropped = drops(mat)
    row = {"site": site, "year": year, "fields": len(mat), "scenes": int(obs.img_id.nunique()),
           "median_dekads": float(mat.notna().sum(axis=1).median()), "peak_lt_06": float((mat.max(axis=1) < 0.6).mean()),
           "abrupt_drop": float(dropped.mean()), "score": mean_score(mat, ref, cfg),
           "score_without_abrupt_drop": mean_score(mat[~dropped], ref, cfg)}
    for dk in (11, 12, 13, 14):                 # mean shortfall below the reference in the last dekads of the 1 Sep score
        row[f"shortfall_dk{dk}"] = float(np.nanmean(np.minimum(mat[dk].to_numpy() - ref[dk], 0.0)))
    for src in ("S30", "L30"):
        row[f"score_{src}"] = mean_score(at_test.dekad_matrix(obs[obs.source == src]), ref, cfg)
    late = mat[13].notna() & mat[14].notna()    # scene density grew over the years: are the late dekads observed equally often?
    row["observed_dk13"], row["observed_dk14"] = float(mat[13].notna().mean()), float(mat[14].notna().mean())
    row["score_late_dekads_observed"] = mean_score(mat[late], ref, cfg)
    return row, mat.median()


def august_scenes(cfg, site: str, year: int) -> list[dict]:
    """Per scene, 1-31 Aug: date, sensor, fields observed, median NDVI. One hazy scene would stand out here."""
    o = read_obs(cfg, site, year)
    o = o[o.date.astype(str).str[5:7] == "08"]
    g = o.groupby(["date", "source", "img_id"]).ndvi.agg(["size", "median"]).reset_index()
    return [{"date": str(r.date), "source": r.source, "fields": int(r["size"]), "ndvi": round(float(r["median"]), 3)}
            for _, r in g.iterrows() if r["size"] >= 10]


def weather(cfg, sites: list[str], years: range) -> pd.DataFrame:
    """ERA5-Land June-August at the site centroids: rain (mm), mean daily maximum (deg C), water balance (rain - potential ET)."""
    cent = json.loads(repo_path("reports/freeze_at/site_centroids.json").read_text(encoding="utf-8"))
    points = {s: (cent[s]["lon"], cent[s]["lat"]) for s in sites}
    rows = []
    for y in years:
        d = gee_extract.era5_daily(points, f"{y}-06-01", f"{y}-09-01", cfg)
        for site, g in d.groupby("pt"):
            aug = g[g.date.str[5:7] == "08"]
            rows.append({"site": site, "year": y, "days": len(g), "rain_jja_mm": g.prec_m.sum() * 1000,
                         "tmax_jja_c": g.tmax_K.mean() - 273.15, "rain_aug_mm": aug.prec_m.sum() * 1000,
                         "tmax_aug_c": aug.tmax_K.mean() - 273.15, "last_date": g.date.max()})
    return pd.DataFrame(rows)


def figures(curves: dict, ref: pd.Series, df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, site in zip(axes, ("wagna", "kalsdorf")):
        for (s, y), c in curves.items():
            if s == site:
                ax.plot(c.index, c.values, color="tab:red" if y == 2026 else "0.75", lw=2.2 if y == 2026 else 1, label=str(y) if y == 2026 else None)
        ax.plot(ref.index, ref.values, "k--", lw=1.2, label="Referenz")
        ax.axvspan(5.5, 14.5, color="tab:green", alpha=0.06)
        ax.set_title(site.capitalize())
        ax.set_xlabel("Dekade seit 1. April (grün: Fenster des Scores am 1.9.)")
        ax.legend(frameon=False)
    axes[0].set_ylabel("Median-NDVI der Maisschläge")
    fig.tight_layout()
    fig.savefig(repo_path("reports/figures/at_test3_curves.png"), dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    d = df.dropna(subset=["yas_site"])
    for site, marker in (("wagna", "o"), ("kalsdorf", "s")):
        g = d[d.site == site]
        ax.scatter(g[f"score_{SCORE_CUTOFF}"], g.yas_site, marker=marker, c=["tab:red" if y == 2026 else "0.45" for y in g.year], label=site.capitalize())
        for _, r in g.iterrows():
            ax.annotate(str(r.year)[2:], (r[f"score_{SCORE_CUTOFF}"], r.yas_site), xytext=(4, 3), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Stress-Score am 1.9. (rot: 2026, blind)")
    ax.set_ylabel("YAS_site (Ertrag / übliches Niveau)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(repo_path("reports/figures/at_test3_scatter.png"), dpi=130)
    plt.close(fig)


def main() -> None:
    cfg = load_config()
    t3 = cfg["at_test3"]
    ref = pd.read_csv(repo_path("reports/freeze_at/stress_reference_hls_ndvi.csv"), index_col=0)["ndvi_median"]
    rows, curves = [], {}
    for site in t3["sites"]:
        for year in range(2018, 2027):
            row, curve = site_year_row(cfg, ref, site, year)
            rows.append(row)
            curves[(site, year)] = curve
    checks = pd.DataFrame(rows)

    at_test3.sample_parcels(cfg, 2026, CONTROL_BASE, CONTROL_SITES)
    at_test3.extract_and_score(cfg, 2026, CONTROL_BASE)
    control = []
    for site in CONTROL_SITES:
        control.append(site_year_row(cfg, ref, site, 2026, CONTROL_BASE)[0])
        control += [site_year_row(cfg, ref, site, y)[0] for y in range(2018, 2026)]

    gee_extract.init_ee()
    climate = weather(cfg, t3["sites"] + CONTROL_SITES, range(2018, 2027))

    df = pd.read_csv(repo_path(t3["results_dir"]) / "site_year.csv")
    v = df[df.yas_site.notna()]
    without_2026 = v[v.year != 2026]
    c = SCORE_CUTOFF
    late = v.merge(checks[["site", "year", "score_late_dekads_observed"]], on=["site", "year"])
    trial = at_test.yas_site(at_test.trial_yields(cfg)[["site", "year", "y_t_ha"]])      # descriptive, outside the protocol
    seen = (without_2026.site + "|" + without_2026.year.astype(str)).isin(t3["seen_new_points"])
    known = without_2026[~seen]         # post-hoc: neither blind nor new points, how much rests on the extremes?
    report = {
        "rho_without_2026": at_test.rho_ci(without_2026[f"score_{c}"], without_2026.yas_site, without_2026.year, cfg),
        "rho_ndvi_without_2026": at_test.rho_ci(without_2026.ndvi_base, without_2026.yas_site, without_2026.year, cfg),
        "rho_without_2026_and_seen_points": at_test.rho_ci(known[f"score_{c}"], known.yas_site, known.year, cfg),
        "rho_ndvi_without_2026_and_seen_points": at_test.rho_ci(known.ndvi_base, known.yas_site, known.year, cfg),
        "rho_late_dekads_observed": at_test.rho_ci(late.score_late_dekads_observed, late.yas_site, late.year, cfg),
        "control_yields": trial[trial.site.isin(CONTROL_SITES) & trial.year.between(2018, 2026)].round(3).to_dict("records"),
        "site_year_checks": checks.round(4).to_dict("records"),
        "control_sites_no_yields": pd.DataFrame(control).round(4).to_dict("records"),
        "august_scenes_2026": {s: august_scenes(cfg, s, 2026) for s in t3["sites"]},
        "august_scenes_2025": {s: august_scenes(cfg, s, 2025) for s in t3["sites"]},
        "weather_era5": climate.round(2).to_dict("records"),
    }
    (repo_path(t3["results_dir"]) / "review_2026.json").write_text(json.dumps(report, indent=2, default=float, ensure_ascii=False), encoding="utf-8")
    figures(curves, ref, df)

    pd.set_option("display.width", 250, "display.max_columns", 40)
    print(checks.round(3)[["site", "year", "scenes", "observed_dk13", "observed_dk14", "score", "score_late_dekads_observed", "score_without_abrupt_drop"]].to_string(index=False))
    print(pd.DataFrame(control).round(3)[["site", "year", "scenes", "observed_dk14", "score", "score_late_dekads_observed"]].to_string(index=False))
    print(pd.DataFrame(report["control_yields"]).to_string(index=False))
    print(json.dumps({k: v for k, v in report.items() if k.startswith("rho_")}, default=float, ensure_ascii=False))


if __name__ == "__main__":
    main()
