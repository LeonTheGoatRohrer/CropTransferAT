"""Second Austria test: Styria (protocol `reports/freeze_protocol_at2.md`, tag freeze-at-2).

Reuses the frozen scores and regional predictions of the first test (`site_year.csv`, no recomputation) and
only adds the Styrian trial yields (fertilisation / tillage trials; the first test had no Styrian variety
trials). Same definitions as `at_test`: `YAS_site`, Spearman with cluster bootstrap over years, verdicts.

Usage:  python -m croptransfer.at_test_stmk
Writes: <results_dir>/{site_year.csv, metrics.json}
"""

from __future__ import annotations

import copy
import json

import numpy as np
import pandas as pd

from croptransfer import at_test
from croptransfer.config import load_config, repo_path

SCORE_COLS = ["site", "year", "bundesland", "nuts2", "ndvi_base"]


def styrian_rows(cfg, types: list[str], path=None) -> pd.DataFrame:
    """Frozen scores/predictions of the Styrian sites merged with `YAS_site` computed from the given trial types."""
    sc = cfg["at_test_stmk"]
    first = pd.read_csv(repo_path(sc["first_test_results"]))
    keep = [c for c in first.columns if c.startswith(("score_", "pred_", "n_valid_"))] + SCORE_COLS
    base = first.loc[first.site.isin(sc["sites"]), keep].copy()
    c2 = copy.deepcopy(cfg)
    c2["at_test"]["trial_types"] = types
    y = at_test.yas_site(at_test.trial_yields(c2, path))
    return base.merge(y[y.site.isin(sc["sites"])], on=["site", "year"], how="left")


def evaluate(df: pd.DataFrame, cfg, pooled_with: pd.DataFrame | None = None) -> dict:
    atc, sc = cfg["at_test"], cfg["at_test_stmk"]
    v = df[df.yas_site.notna()]
    res: dict = {"n_site_years": int(len(v)), "per_site": v.groupby("site").size().to_dict(),
                 "per_year": {int(k): int(n) for k, n in v.groupby("year").size().items()},
                 "baseline_kind": v.baseline_kind.value_counts().to_dict(), "cutoffs": {}}
    for c in atc["cutoffs"]:
        r = {"S-A_stress_score": at_test.rho_ci(v[f"score_{c}"], v.yas_site, v.year, cfg)}
        r["S-A_stress_score"]["verdict"] = at_test.passed(r["S-A_stress_score"], sc["min_site_years"])
        rb = v[v.year <= 2023]
        r["S-B_regional_model"] = at_test.rho_ci(rb[f"pred_{c}"], rb.yas_site, rb.year, cfg)
        r["S-B_regional_model"]["verdict"] = at_test.passed(r["S-B_regional_model"], sc["min_site_years"])
        r["S-A_within_site"] = at_test.descriptive_within(v, f"score_{c}", "yas_site", "site", sc["min_years_within_site"])
        r["S-A_within_year"] = at_test.descriptive_within(v, f"score_{c}", "yas_site", "year", 3)
        r["S-A_leave_one_year_out"] = at_test.leave_one_year_out(v, f"score_{c}", "yas_site")
        if c == atc["primary_cutoff"]:
            r["S-baseline_NDVI"] = at_test.rho_ci(v.ndvi_base, v.yas_site, v.year, cfg)
            if pooled_with is not None:
                p = pd.concat([v, pooled_with[pooled_with.yas_site.notna()]], ignore_index=True)
                r["pooled_Austria_stress_score_descriptive"] = at_test.rho_ci(p[f"score_{c}"], p.yas_site, p.year, cfg)
        res["cutoffs"][c] = r
    return res


def main() -> None:
    cfg = load_config()
    sc = cfg["at_test_stmk"]
    out = repo_path(sc["results_dir"])
    out.mkdir(parents=True, exist_ok=True)
    first = pd.read_csv(repo_path(sc["first_test_results"]))
    oo = first[~first.site.isin(sc["sites"])]
    res = {"protocol": "reports/freeze_protocol_at2.md", "tag": "freeze-at-2"}
    for name, types in [("primary", sc["trial_types_primary"]), ("sensitivity_all_types", sc["trial_types_sensitivity"])]:
        df = styrian_rows(cfg, types)
        if name == "primary":
            df.to_csv(out / "site_year.csv", index=False)
        res[name] = evaluate(df, cfg, pooled_with=oo)
        res[name]["trial_types"] = types
    (out / "metrics.json").write_text(json.dumps(res, indent=2, default=float, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, default=float, ensure_ascii=False)[:7000])


if __name__ == "__main__":
    main()
