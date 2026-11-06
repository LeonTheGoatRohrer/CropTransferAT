"""Third Austria test: Styria with the Hatzendorf Excel series (protocol `reports/freeze_protocol_at3.md`, tag freeze-at-3).

New compared with freeze-at-2: the yields come from the long N-fertilisation series of Wagna and Kalsdorf
(Excel files of the Hatzendorf station, received 2026-10-28) instead of the hand-transcribed report rows,
and 2026 is added. Scores 2018-2025 are taken unchanged from the first test (`site_year.csv`); 2026 scores
are computed later with the frozen rules (same parcel sampling, HLS extraction and stress score).

Usage:  python -m croptransfer.at_test3 --yields-only   (tidy yield table + site-year yields, no scores read)
        python -m croptransfer.at_test3 --replicate Y   (check: recompute year Y, must repeat the first test; no yield read)
        python -m croptransfer.at_test3 --scores-2026   (frozen rules on INVEKOS 2026-1; only after the check passed)
        python -m croptransfer.at_test3                 (full evaluation, only after freeze-at-3)
"""

from __future__ import annotations

import argparse
import json
import re

import geopandas as gpd
import numpy as np
import pandas as pd
from openpyxl import load_workbook

from croptransfer import at_extract, at_fields, at_test, gee_extract, invekos
from croptransfer.at_test_stmk import evaluate
from croptransfer.config import load_config, repo_path

YEAR_HEADER = re.compile(r"^Ertrag (\d{4})(?!.*t/ha)")


def read_excel_yields(path, sheet: str, header_row: int, variant_col: int) -> pd.DataFrame:
    """Variant x year grain yields (dt/ha) of one 'Daten Ertrag' sheet -> site-less long table.

    Year columns are the header cells 'Ertrag YYYY ...' (t/ha duplicates skipped); the header text after
    the year is kept as `header_note` (e.g. 'nicht mitgewertet'). Empty or non-numeric cells are dropped.
    """
    ws = load_workbook(path, data_only=True, read_only=True)[sheet]
    rows = list(ws.iter_rows(values_only=True))
    header = rows[header_row - 1]
    years = {}
    for j, h in enumerate(header):
        m = YEAR_HEADER.match(str(h or "").strip())
        if m and int(m.group(1)) not in years.values():
            years[j] = int(m.group(1))
    out, seen = [], set()
    for r in rows[header_row:]:
        var = r[variant_col - 1]
        if var is None or str(var).strip() == "" or str(var).strip() in seen:
            continue                                    # later blocks of the sheet reuse codes (sums, helper tables)
        seen.add(str(var).strip())
        for j, yr in years.items():
            v = r[j]
            if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
                note = str(header[j]).split(str(yr), 1)[1].strip()
                out.append({"variant": str(var).strip(), "year": yr, "yield_dt_ha": float(v), "header_note": note})
    return pd.DataFrame(out)


def tidy_yields(cfg) -> pd.DataFrame:
    """All configured Excel files -> site, year, variant, yield_dt_ha, header_note, excluded."""
    t3 = cfg["at_test3"]
    parts = []
    for site, s in t3["excel"].items():
        d = read_excel_yields(repo_path(s["path"]), s["sheet"], s["header_row"], s["variant_col"])
        d.insert(0, "site", site)
        d["excluded"] = d.year.isin(s.get("exclude_years", []))
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def site_year_yields(tidy: pd.DataFrame, first_year: int, core_only: bool = True) -> pd.DataFrame:
    """Y(c,y) in t/ha: mean over the core variants (yield in every counted year >= first_year), else all variants."""
    d = tidy[~tidy.excluded & (tidy.year >= first_year)]
    out = []
    for site, g in d.groupby("site"):
        years = g.year.nunique()
        core = g.groupby("variant").year.nunique()
        use = g[g.variant.isin(core[core == years].index)] if core_only else g
        m = use.groupby("year").yield_dt_ha.agg(["mean", "size"]).reset_index()
        out += [{"site": site, "year": int(r.year), "y_t_ha": r["mean"] / 10.0, "n_variants": int(r["size"])}
                for _, r in m.iterrows()]
    return pd.DataFrame(out)


def rows(cfg, scores: pd.DataFrame, core_only: bool = True) -> pd.DataFrame:
    """Frozen site-year scores merged with YAS_site from the Excel series (rule of `at_test.yas_site`, unchanged)."""
    t3 = cfg["at_test3"]
    y = at_test.yas_site(site_year_yields(tidy_yields(cfg), t3["first_yield_year"], core_only)[["site", "year", "y_t_ha"]])
    base = scores[scores.site.isin(t3["sites"]) & scores.year.between(*t3["years"])]
    return base.merge(y, on=["site", "year"], how="left")


def load_scores(cfg) -> pd.DataFrame:
    """Scores 2018-2025 from the first test plus the 2026 scores file (computed after the freeze)."""
    t3 = cfg["at_test3"]
    keep = ["site", "year", "ndvi_base"] + [f"{p}_{c}" for c in cfg["at_test"]["cutoffs"] for p in ("score", "pred", "n_valid")]
    first = pd.read_csv(repo_path(cfg["at_test_stmk"]["first_test_results"]))
    new = pd.read_csv(repo_path(t3["scores_2026"]))
    return pd.concat([first[[c for c in keep if c in first]], new[[c for c in keep if c in new]]], ignore_index=True)


def sample_parcels(cfg, year: int, base: str, sites: list[str] | None = None) -> pd.DataFrame:
    """Frozen parcel sampling of `at_fields` for one year, kept for the given sites (default: test sites); writes fields + membership."""
    atc, t3 = cfg["at_test"], cfg["at_test3"]
    keep = sites or t3["sites"]
    out = repo_path(base)
    (out / "obs").mkdir(parents=True, exist_ok=True)
    cent = json.loads(repo_path("reports/freeze_at/site_centroids.json").read_text(encoding="utf-8"))
    g = at_fields.read_maize(invekos.find_gpkgs(repo_path("data/raw/invekos"))[year], atc["invekos_code"])
    sel, mem = at_fields.select_year(g, year, atc["sites"], cent, atc)    # all sites: the seed offset depends on the full list
    mem = pd.DataFrame(mem)
    mem = mem[mem.site.isin(keep)].copy()
    mem["fy_key"] = "AT|" + mem.year.astype(str) + "|" + mem.fid.astype(str)
    sub = g.loc[sorted(set(mem.fid))].copy()
    sub["year"], sub["fid"] = year, sub.index.astype(int)
    sub["fy_key"] = "AT|" + str(year) + "|" + sub["fid"].astype(str)
    buf = sub.geometry.buffer(cfg["field"]["inner_buffer_m"])
    sub["area_buffered_ha"] = buf.area / 1e4
    sub = sub.assign(geometry=buf)
    sub = sub[~sub.geometry.is_empty & sub.geometry.notna()]
    sub.to_crs(4326)[["fy_key", "year", "fid", invekos.AREA_COL, "area_buffered_ha", "geometry"]].to_parquet(out / "fields.parquet")
    mem.to_csv(out / "membership.csv", index=False)
    pd.DataFrame([r for r in sel if r["site"] in keep]).to_csv(out / "selection.csv", index=False)
    return mem


def extract_and_score(cfg, year: int, base: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """HLS scene statistics (cached per site-year) and the frozen stress score -> field table, site-year table."""
    out = repo_path(base)
    fields, mem = gpd.read_parquet(out / "fields.parquet"), pd.read_csv(out / "membership.csv")
    gee_extract.init_ee()
    for site, keys in mem.groupby("site").fy_key:
        path = out / "obs" / f"{site}_{year}_HLS.parquet"
        if not path.exists():
            at_extract._stats(cfg, fields[fields.fy_key.isin(keys)], year).to_parquet(path)
            print("extracted", path.name, flush=True)
    table = at_test.field_table(cfg, base)
    return table, at_test.site_year_scores(table, cfg, base)


def replication_gaps(new: pd.DataFrame, old: pd.DataFrame, cutoffs: list[str], tol: float = 1e-9) -> list[str]:
    """Protocol section 2 check: which site-year scores differ from the first test? Empty list = exact repeat."""
    a, b = new.set_index(["site", "year"]), old.set_index(["site", "year"])
    gaps = []
    for key in a.index:
        for col in [f"score_{c}" for c in cutoffs] + ["ndvi_base"]:
            x, y = a.at[key, col], b.at[key, col]
            if not ((np.isnan(x) and np.isnan(y)) or abs(x - y) <= tol):
                gaps.append(f"{key[0]} {key[1]} {col}: {x} vs {y}")
    return gaps


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--yields-only", action="store_true")
    ap.add_argument("--replicate", type=int, default=None)
    ap.add_argument("--scores-2026", action="store_true")
    a = ap.parse_args()
    cfg = load_config()
    t3 = cfg["at_test3"]
    if a.yields_only:
        tidy = tidy_yields(cfg)
        tidy.to_csv(repo_path(t3["tidy_csv"]), index=False)
        print(site_year_yields(tidy, t3["first_yield_year"]).to_string(index=False))
        return
    if a.replicate:
        base = f"data/interim/at3/check_{a.replicate}"
        mem = sample_parcels(cfg, a.replicate, base)
        first_mem = pd.read_csv(repo_path("data/interim/at/membership.csv"))
        first_mem = first_mem[(first_mem.year == a.replicate) & first_mem.site.isin(t3["sites"])]
        same = set(zip(mem.site, mem.fid)) == set(zip(first_mem.site, first_mem.fid))
        print("same parcels as the first test:", same, len(mem), flush=True)
        _, sy = extract_and_score(cfg, a.replicate, base)
        first = pd.read_csv(repo_path(cfg["at_test_stmk"]["first_test_results"]), usecols=["site", "year", "ndvi_base"] + [f"score_{c}" for c in cfg["at_test"]["cutoffs"]])
        gaps = replication_gaps(sy, first, cfg["at_test"]["cutoffs"])
        print("score gaps:", gaps or "none", flush=True)
        raise SystemExit(0 if same and not gaps else 1)
    if a.scores_2026:
        base = "data/interim/at3/2026"
        sample_parcels(cfg, 2026, base)
        table, sy = extract_and_score(cfg, 2026, base)
        path = repo_path(t3["scores_2026"])
        path.parent.mkdir(parents=True, exist_ok=True)
        table.to_parquet(path.parent / "field_scores_2026.parquet")
        sy.to_csv(path, index=False)
        print(sy.to_string(index=False))
        return
    out = repo_path(t3["results_dir"])
    out.mkdir(parents=True, exist_ok=True)
    scores = load_scores(cfg)
    first = pd.read_csv(repo_path(cfg["at_test_stmk"]["first_test_results"]))
    upper_austria = first[~first.site.isin(cfg["at_test_stmk"]["sites"])]     # descriptive pool (protocol section 3), not independent
    res = {"protocol": "reports/freeze_protocol_at3.md", "tag": "freeze-at-3"}
    for name, core in [("primary_core_variants", True), ("sensitivity_all_variants", False)]:
        df = rows(cfg, scores, core)
        if core:
            df.to_csv(out / "site_year.csv", index=False)
        res[name] = evaluate(df, cfg, pooled_with=upper_austria)    # same metrics and thresholds as freeze-at-2 (min 15 site-years)
        if core:
            seen = (df.site + "|" + df.year.astype(str)).isin(t3["seen_new_points"])
            res["sensitivity_without_seen_new_points"] = evaluate(df[~seen], cfg)
            res["blind_site_years_2026"] = df[df.year == 2026].to_dict("records")
    (out / "metrics.json").write_text(json.dumps(res, indent=2, default=float, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, default=float, ensure_ascii=False)[:6000])


if __name__ == "__main__":
    main()
