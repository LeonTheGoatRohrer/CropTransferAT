"""Austria test, step 1: INVEKOS grain-maize parcels around the trial sites (PLAN Phase 6, protocol freeze-at-1).

Selection rules are fixed in `config.yaml: at_test` / `reports/freeze_protocol_at.md` and are applied unchanged:
SNAR_CODE 105, area >= 1 ha, valid geometry, parcel centroid within `radius_km` of the site position, at most
`max_fields_per_site_year` per site-year drawn at random (seed 42, candidates sorted by coordinates), inner buffer -10 m.
No yield and no satellite value is read here.

Usage:  python -m croptransfer.at_fields
Writes: data/interim/at/fields.parquet (one row per sampled parcel-year, EPSG:4326, buffered)
        data/interim/at/selection.csv   (candidates / sampled per site-year)
        data/interim/at/membership.csv  (site, year, fy_key)
"""

from __future__ import annotations

import json

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio

from croptransfer import invekos
from croptransfer.config import load_config, repo_path


def read_maize(path, code: str) -> gpd.GeoDataFrame:
    """All parcels of one crop code with a stable id (GeoPackage fid), EPSG:31287."""
    g = pyogrio.read_dataframe(path, columns=[invekos.AREA_COL], where=f"{invekos.CROP_CODE_COL} = '{code}'",
                               fid_as_index=True)
    if g.crs is None or g.crs.to_epsg() != 31287:
        g = g.set_crs(31287, allow_override=True)
    return g


def select_year(g: gpd.GeoDataFrame, year: int, sites: dict, centroids: dict, atc: dict) -> tuple[list, list]:
    """Candidates and sample per site for one year -> (selection rows, membership rows)."""
    g = g[(g[invekos.AREA_COL] >= 1.0) & g.geometry.is_valid & ~g.geometry.is_empty].copy()
    cen = g.geometry.centroid
    cx, cy = cen.x.to_numpy(), cen.y.to_numpy()
    sel_rows, mem_rows = [], []
    for k, site in enumerate(sorted(sites)):
        c = centroids[site]
        d = np.hypot(cx - c["x_31287"], cy - c["y_31287"])
        cand = g.index[d <= atc["radius_km"] * 1000.0]
        order = np.lexsort((cy[g.index.get_indexer(cand)], cx[g.index.get_indexer(cand)]))
        cand = cand[order]
        rng = np.random.default_rng(42 + year * 1000 + k)
        n = min(len(cand), atc["max_fields_per_site_year"])
        pick = cand[np.sort(rng.choice(len(cand), n, replace=False))] if n else cand[:0]
        sel_rows.append({"site": site, "year": year, "n_candidates": int(len(cand)), "n_sampled": int(len(pick)),
                         "area_ha_candidates": float(g.loc[cand, invekos.AREA_COL].sum())})
        mem_rows += [{"site": site, "year": year, "fid": int(f)} for f in pick]
    return sel_rows, mem_rows


def main() -> None:
    cfg = load_config()
    atc = cfg["at_test"]
    out = repo_path("data/interim/at")
    out.mkdir(parents=True, exist_ok=True)
    cent = json.loads(repo_path("reports/freeze_at/site_centroids.json").read_text(encoding="utf-8"))
    gpkgs = invekos.find_gpkgs(repo_path("data/raw/invekos"))
    sel, mem, polys = [], [], []
    for year in range(atc["years"][0], atc["years"][1] + 1):
        g = read_maize(gpkgs[year], atc["invekos_code"])
        s, m = select_year(g, year, atc["sites"], cent, atc)
        sel += s
        mem += m
        fids = sorted({r["fid"] for r in m})
        sub = g.loc[fids].copy()
        sub["year"], sub["fid"] = year, sub.index.astype(int)
        sub["fy_key"] = "AT|" + str(year) + "|" + sub["fid"].astype(str)
        buf = sub.geometry.buffer(cfg["field"]["inner_buffer_m"])
        sub["area_buffered_ha"] = buf.area / 1e4
        sub = sub.assign(geometry=buf)
        sub = sub[~sub.geometry.is_empty & sub.geometry.notna()]
        polys.append(sub.to_crs(4326)[["fy_key", "year", "fid", invekos.AREA_COL, "area_buffered_ha", "geometry"]])
        print(year, f"parcels {len(g)}, sampled union {len(fids)}", flush=True)
    pd.DataFrame(sel).to_csv(out / "selection.csv", index=False)
    mem = pd.DataFrame(mem)
    mem["fy_key"] = "AT|" + mem.year.astype(str) + "|" + mem.fid.astype(str)
    mem.to_csv(out / "membership.csv", index=False)
    pd.concat(polys, ignore_index=True).to_parquet(out / "fields.parquet")
    print(pd.DataFrame(sel).pivot(index="site", columns="year", values="n_sampled").to_string())


if __name__ == "__main__":
    main()
