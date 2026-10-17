"""Data criticism of the new features M1-M4 (AGENTS.md §3) before the ablation.

Writes results/<date>_feinjust_review/review.json and reports/figures/fj_*.png.
Usage:  python -m croptransfer.fj_review
"""

from __future__ import annotations

import json
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from croptransfer import feinjust, fj_features as fjf, timeseries as ts
from croptransfer.config import load_config, repo_path


def main() -> None:
    cfg = load_config()
    interim = repo_path(cfg["paths"]["interim"])
    figs = repo_path(cfg["paths"]["figures"])
    run = repo_path(cfg["paths"]["results"]) / f"{date.today().isoformat()}_feinjust_review"
    run.mkdir(parents=True, exist_ok=True)
    inp = feinjust.load_inputs(cfg)
    df = inp["df"]
    feat, bins = feinjust.build_features(cfg, inp)
    meta = df[["fy_key", "dataset", "year", "RY_descr", "sensor_era"]]
    f = feat.merge(meta, on="fy_key")
    ev = f[f.RY_descr.notna()]
    out: dict = {"n_field_years": int(len(f)), "n_eval": int(len(ev))}
    cols = [c for m in feinjust.FEATURE_SETS.values() for c in m if c != "stress_gdd"]
    out["missing_share_eval"] = ev[cols].isna().mean().round(3).to_dict()
    out["missing_by_site_year"] = ev.groupby(["dataset", "year"])[cols].apply(lambda g: g.isna().mean().round(2)) \
        .reset_index().to_dict("records")
    out["describe"] = f[cols + ["s1_n_scenes", "lst_n_scenes"]].describe().round(3).to_dict()
    # scene counts and platforms (sensor change S1A/S1B, Landsat 8/9)
    s1 = pd.concat([pd.read_parquet(p) for p in sorted((interim / "obs_s1").glob("*.parquet"))])
    s1["year"] = pd.to_datetime(s1.date).dt.year
    out["s1_scenes_by_year_platform"] = s1.drop_duplicates(["date", "img_id"]).groupby(["year", "platform"]).size() \
        .rename("n").reset_index().to_dict("records")
    out["s1_db_range"] = {"vv": [float(s1.vv_db.min()), float(s1.vv_db.max())],
                          "vh": [float(s1.vh_db.min()), float(s1.vh_db.max())]}
    tab = fjf.s1_scene_table(s1, cfg)
    tab["year"] = pd.to_datetime(tab.date).dt.year
    tab["dataset"] = tab.fy_key.str.split("|").str[0]
    out["s1_rvi_mean_by_site_year"] = tab.groupby(["dataset", "year"]).rvi.mean().round(3).reset_index() \
        .to_dict("records")
    lst = pd.concat([pd.read_parquet(p) for p in sorted((interim / "obs_lst").glob("*.parquet"))])
    lst["clear"] = lst.n_clear / lst.n_total >= cfg["lst"]["clear_frac_min"]
    lst["lst_c"] = lst.lst_k - 273.15
    out["lst_range_c_clear"] = [float(lst[lst.clear].lst_c.min()), float(lst[lst.clear].lst_c.max())]
    out["lst_clear_scenes_by_site_year"] = f.groupby(["dataset", "year"]).lst_n_scenes.median().reset_index() \
        .to_dict("records")
    # site-level features: is there any between-field variation within a site-year?
    out["within_site_year_sd"] = f.groupby(["dataset", "year"])[["modis_et_ratio", "era5_et_ratio", "lst_dt_mean"]] \
        .std().round(4).reset_index().to_dict("records")
    # cloud bias: clear-scene counts vs RY within site-years
    rr = []
    for (ds, yr), g in ev.groupby(["dataset", "year"]):
        if len(g) >= 5 and g.lst_n_scenes.nunique() > 1:
            rr.append(float(g[["lst_n_scenes", "RY_descr"]].corr("spearman").iloc[0, 1]))
    out["cloud_bias_lst_nscenes_vs_RY_within_site_year"] = rr
    out["corr_features_eval"] = ev[cols].corr("spearman").round(2).to_dict()
    out["emerge_doy_by_site_year"] = f.groupby(["dataset", "year"]).emerge_doy.describe()[["count", "min", "50%", "max"]] \
        .round(1).reset_index().to_dict("records")
    (run / "review.json").write_text(json.dumps(out, indent=2, default=float))
    # visual check: 24 S2 NDVI curves with the emergence marker
    keys = f[f.emerge_doy.notna()].groupby(["dataset", "year"]).head(3).fy_key.head(24)
    fig, axes = plt.subplots(4, 6, figsize=(15, 8), sharey=True)
    for ax, k in zip(axes.ravel(), keys):
        o = inp["s2"].get(k)
        yr = int(k.split("|")[-1])
        comp = ts.dekad_composite(o, date(yr, 9, 1), "ndvi")
        x = pd.Timestamp(f"{yr}-04-01").dayofyear + 10 * comp.dekad + 5
        ax.plot(x, comp.value, color="#3b6ea8")
        oo = o[pd.to_datetime(o.date).dt.date <= date(yr, 9, 1)]
        ax.scatter(pd.to_datetime(oo.date).dt.dayofyear, oo.ndvi, s=6, color="#555")
        e = f.set_index("fy_key").emerge_doy[k]
        ax.axvline(e, color="#a86a00", ls="--")
        ax.set_title(k.replace("|", " ")[:34], fontsize=7)
        ax.set_xlim(90, 250)
    for ax in axes[:, 0]:
        ax.set_ylabel("NDVI (S2)")
    fig.suptitle("Auflaufdatum (gestrichelt, 20 % Amplitude) auf S2-NDVI-Kurven bis 1.9.", fontsize=10)
    fig.tight_layout()
    fig.savefig(figs / "fj_emergence_check.png", dpi=100)
    plt.close(fig)
    print(json.dumps({k: out[k] for k in ["missing_share_eval", "s1_db_range", "lst_range_c_clear",
                                          "cloud_bias_lst_nscenes_vs_RY_within_site_year"]}, indent=1))


if __name__ == "__main__":
    main()
