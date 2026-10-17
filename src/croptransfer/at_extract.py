"""Austria test, step 2: HLS scene statistics of the sampled INVEKOS parcels (one GEE request per site-year).

Jobs are cached under data/interim/at/obs/ and skipped if present. Trial site-years (known from the
metadata columns of at_trials.csv only; the yield column is never read here) run first.

Usage:  python -m croptransfer.at_extract [--workers 4] [--limit N]
"""

from __future__ import annotations

import argparse
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import geopandas as gpd
import pandas as pd

from croptransfer import gee_extract
from croptransfer.config import load_config, repo_path


def trial_site_years(cfg) -> set[tuple[str, int]]:
    """(site cluster, year) pairs that have a trial row of a configured type; metadata columns only."""
    atc = cfg["at_test"]
    t = pd.read_csv(repo_path("data/raw/at_trials.csv"), usecols=["site", "year", "trial_type"])
    alias = {a: k for k, s in atc["sites"].items() for a in s["aliases"]}
    t = t[t.trial_type.isin(atc["trial_types"]) & t.site.isin(alias)]
    return {(alias[s], int(y)) for s, y in zip(t.site, t.year) if atc["years"][0] <= y <= atc["years"][1]}


def _stats(cfg, fields, year):
    """Scene statistics; halves the field set when a request exceeds the 5000-element limit of getInfo."""
    try:
        return gee_extract.scene_stats(fields, "HLS", f"{year}-04-01", f"{year}-11-01", cfg)
    except Exception as e:
        if "5000 elements" not in str(e) or len(fields) < 2:
            raise
        h = len(fields) // 2
        return pd.concat([_stats(cfg, fields.iloc[:h], year), _stats(cfg, fields.iloc[h:], year)], ignore_index=True)


def _job(cfg, fields, site, year, out):
    df = _stats(cfg, fields, year)
    df.to_parquet(out)
    return f"{out.name}: {len(df)} rows, {fields.fy_key.nunique()} fields"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    cfg = load_config()
    base = repo_path("data/interim/at")
    (base / "obs").mkdir(parents=True, exist_ok=True)
    gee_extract.init_ee()
    fields = gpd.read_parquet(base / "fields.parquet")
    mem = pd.read_csv(base / "membership.csv")
    trials = trial_site_years(cfg)
    order = sorted(mem.groupby(["site", "year"]).groups, key=lambda sy: (sy not in trials, sy[1], sy[0]))
    jobs = []
    for site, year in order:
        out = base / "obs" / f"{site}_{year}_HLS.parquet"
        if out.exists():
            continue
        keys = mem[(mem.site == site) & (mem.year == year)].fy_key
        jobs.append((cfg, fields[fields.fy_key.isin(keys)], site, year, out))
    if a.limit:
        jobs = jobs[: a.limit]
    print(f"{len(jobs)} jobs ({len(trials)} trial site-years first)", flush=True)
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(_job, *j): j for j in jobs}
        for fut in as_completed(futs):
            try:
                print("OK", fut.result(), flush=True)
            except Exception as e:  # failed jobs are re-run next time
                j = futs[fut]
                print("FAIL", j[2], j[3], repr(e)[:300], flush=True)
                traceback.print_exc()


if __name__ == "__main__":
    main()
