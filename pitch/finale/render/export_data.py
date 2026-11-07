"""Collect the real data the motion graphics draw, and check every number of the film against the saved reports.

Writes ../export/mg/data.js (gitignored: contains the non-public Hatzendorf relative yields). Stops if a number on screen no
longer matches its source. Numbers shown in the film live in FACTS, see reports/finale_video/FAKTENCHECK.md.

Usage: python export_data.py
"""
from __future__ import annotations

import csv
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

MAIN = Path(os.environ.get("DG_MAIN", r"C:\Users\mario\CropTransferAT"))
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = HERE.parent / "export" / "mg"
RES = REPO / "results"

# Tiles of the "782" scene: hauptergebnis.md section 5 (main checkout, stand 2026-10-18).
BLOCKS = [("Basismodelle", 336), ("Zusatzfragen", 72), ("Verbesserungsrunden", 168), ("Problemfelder", 7), ("Innerhalb des Feldes", 54),
          ("One Acre Fund", 56), ("EU-Regionalmodell", 28), ("Mehr-Kulturen", 16), ("Feinjustierung", 4), ("Drei Standorte", 36), ("Österreich, explorativ", 5)]


def find(tree, key):
    """First value stored under `key` anywhere in a nested dict."""
    if isinstance(tree, dict):
        if key in tree:
            return tree[key]
        for v in tree.values():
            hit = find(v, key)
            if hit is not None:
                return hit
    return None


def check(name: str, value, expected, digits: int = 2) -> None:
    ok = round(float(value), digits) == round(float(expected), digits)
    print(f"{'ok ' if ok else 'FEHLER'} {name}: {value:.4f} -> Film {expected}")
    if not ok:
        raise SystemExit(f"Zahl stimmt nicht mehr mit der Quelle überein: {name}")


def cells_to_rows(ix, iy, values, levels=10):
    """Compact raster: one string per row, a digit per cell, '.' where there is no cell."""
    w, h = int(ix.max()) + 1, int(iy.max()) + 1
    grid = [["."] * w for _ in range(h)]
    for x, y, v in zip(ix, iy, values):
        grid[int(y)][int(x)] = str(min(levels - 1, int(v * levels)))
    return ["".join(r) for r in grid]


def barc_field_years() -> list[dict]:
    pts = pd.read_parquet(MAIN / "data/processed/gt_yield_points.parquet")
    pts = pts[pts.dataset == "BARC"].copy()
    pts["x"], pts["y"] = pts.x.round(1), pts.y.round(1)
    out = []
    for path in sorted(glob.glob(str(MAIN / "data/interim/pixels/BARC_BARC_*.parquet"))):
        m = re.search(r"BARC_BARC_(.+)_(\d{4})\.parquet", path)
        fid, year = m.group(1), int(m.group(2))
        px = pd.read_parquet(path)
        px["x"], px["y"] = px.x.round(1), px.y.round(1)
        both = px.merge(pts[(pts.field_id == fid) & (pts.year == year)][["x", "y", "yield_t_ha"]], on=["x", "y"]).dropna(subset=["ndvi_w2", "yield_t_ha"])
        if len(both) < 30:
            continue
        both["rel"] = both.yield_t_ha / both.yield_t_ha.mean()
        xs, ys = np.sort(both.x.unique()), np.sort(both.y.unique())
        ix, iy = np.searchsorted(xs, both.x), np.searchsorted(ys, both.y)
        if len(ys) > len(xs):                               # long axis horizontal, so every tile fits the same slot
            ix, iy = iy, ix
        ry = (rankdata(both.rel) - 1) / (len(both) - 1)
        rn = (rankdata(both.ndvi_w2) - 1) / (len(both) - 1)
        out.append({"id": fid, "year": year, "n": len(both), "rho": round(float(spearmanr(both.ndvi_w2, both.rel).statistic), 3),
                    "yield": cells_to_rows(ix, iy, ry), "ndvi": cells_to_rows(ix, iy, rn), "_both": both, "_ix": ix, "_iy": iy})
    return out


def main_field(fys: list[dict]) -> dict:
    f = next(x for x in fys if x["id"] == "EastFarm_5_12" and x["year"] == 2021)
    b, ix, iy = f["_both"], f["_ix"], f["_iy"]
    ndvi_rank = (rankdata(b.ndvi_w2) - 1) / (len(b) - 1)
    rel_rank = (rankdata(b.rel) - 1) / (len(b) - 1)
    return {"w": int(ix.max()) + 1, "h": int(iy.max()) + 1, "x": ix.tolist(), "y": iy.tolist(), "rel": b.rel.round(3).tolist(), "relr": rel_rank.round(3).tolist(), "ndvi": ndvi_rank.round(3).tolist(),
            "min": round(float(b.rel.min()), 2), "max": round(float(b.rel.max()), 2), "rho": f["rho"], "n": f["n"]}


def austria() -> dict:
    files = glob.glob(str(MAIN / "data/raw/**/STATISTIK_AUSTRIA_GEM_20*.shp"), recursive=True)
    gem = gpd.read_file(sorted(files)[-1]).to_crs(4326)
    code = gem.columns[gem.columns.str.lower().isin(["g_id", "id", "gkz"])][0]
    gem["land"] = gem[code].astype(str).str[0]
    simplify = 0.012
    def ring(geom):
        geom = geom.simplify(simplify)
        poly = max(geom.geoms, key=lambda p: p.area) if geom.geom_type == "MultiPolygon" else geom
        return [[round(x, 3), round(y, 3)] for x, y in poly.exterior.coords]
    sites = {"Innviertel": ["41210", "41207"], "Mauthausen": ["41111"], "Walding": ["41626"], "Linden": ["41821"], "Bad Wimsbach": ["41803"]}
    pts = {}
    for name, ids in sites.items():
        c = gem[gem[code].astype(str).isin(ids)].geometry.union_all().centroid
        pts[name] = [round(c.x, 3), round(c.y, 3)]
    return {"at": ring(gem.geometry.union_all()), "oo": ring(gem[gem.land == "4"].geometry.union_all()), "st": ring(gem[gem.land == "6"].geometry.union_all()), "sites_oo": pts}


def scatter() -> list[dict]:
    df = pd.read_csv(RES / "2026-10-28_at_test3/site_year.csv").dropna(subset=["yas_site", "score_09-01"])
    return [{"site": r.site, "year": int(r.year), "score": round(r["score_09-01"], 4), "yas": round(r.yas_site, 3)} for _, r in df.iterrows()]


def verify(fys: list[dict], sc: list[dict]) -> None:
    rhos = [f["rho"] for f in fys]
    print(f"BARC: {len(fys)} Feld-Jahre, Felder {len({f['id'] for f in fys})}, positiv {sum(r > 0 for r in rhos)}")
    check("Median-rho BARC (Rohwerte neu gerechnet)", np.median(rhos), 0.68)
    assert len(fys) == 41 and all(r > 0 for r in rhos), "41 Feld-Jahre, alle positiv"
    product = json.loads((RES / "2026-10-16_feinjust_ablation/product.json").read_text(encoding="utf-8"))["within_field_map"]
    check("Schwächstes Viertel trifft Problemzone", product["median_precision"], 0.58)
    check("Zufallswert", product["median_prevalence"], 0.27)
    assert sum(n for _, n in BLOCKS) == 782, "Summe Modellvarianten"
    check("Oberösterreich rho", find(json.loads((RES / "2026-10-17_at_test/metrics.json").read_text(encoding="utf-8")), "cutoffs")["09-01"]["V2-A_stress_score"]["rho"], 0.50)
    stmk = json.loads((RES / "2026-10-17_at_test_stmk/metrics.json").read_text(encoding="utf-8"))
    assert find(stmk, "09-01")["S-A_stress_score"]["n"] == 12, "Steiermark: 12 Standort-Jahre"
    at3 = json.loads((RES / "2026-10-28_at_test3/metrics.json").read_text(encoding="utf-8"))["primary_core_variants"]
    main = at3["cutoffs"]["09-01"]
    check("Test III rho", main["S-A_stress_score"]["rho"], 0.77)
    check("Test III KI unten", main["S-A_stress_score"]["lo"], 0.30)
    check("Test III KI oben", main["S-A_stress_score"]["hi"], 0.97)
    assert at3["n_site_years"] == 15 and main["S-A_stress_score"]["verdict"] == "bestanden"
    ndvi = next(v for k, v in main.items() if "ndvi" in k.lower())
    check("Test III NDVI", ndvi["rho"], 0.72)
    assert len(sc) == 15, "15 Standort-Jahre"
    lowest = sorted(sc, key=lambda p: p["score"])[:2]
    assert {p["year"] for p in lowest} == {2026}, "die zwei niedrigsten Scores stammen aus 2026"
    print("niedrigste Scores:", lowest)


def voice_beats() -> dict:
    """Start time of every sentence of every take, from the pauses in the audio, so that the pictures follow the voice."""
    beats = {}
    with open(HERE / "voice_lines.tsv", encoding="utf-8", newline="") as f:
        lines = list(csv.DictReader(f, delimiter="\t"))
    for line in lines:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(HERE.parent / "export/voice" / f"{line['id']}.mp3"), "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, dtype=np.float32)
        hop = 80                                            # 10 ms
        level = np.array([np.abs(x[i:i + hop]).max() for i in range(0, len(x) - hop, hop)])
        quiet = level < 0.02
        gaps, i = [], 0
        while i < len(quiet):
            if quiet[i]:
                j = i
                while j < len(quiet) and quiet[j]:
                    j += 1
                if i > 0 and j < len(quiet) and j - i >= 6:
                    gaps.append((j - i, j * 0.01))
                i = j
            else:
                i += 1
        # Each sentence end is expected where its share of the characters says; take the pause nearest to that, longer ones preferred.
        dur = len(x) / 8000
        ends = [m.end() for m in re.finditer(r"[.?!](?:\s|$)", line["text"])][:-1]
        starts = []
        for e in ends:
            expected = e / len(line["text"]) * dur
            starts.append(min(gaps, key=lambda g: abs(g[1] - expected) - min(g[0], 50) * 0.03)[1])
        first = float(np.argmax(~quiet) * 0.01)
        beats[line["id"]] = {"dur": round(dur, 2), "s": [round(first, 2)] + [round(s, 2) for s in starts]}
    # Two takes where a comma pause is longer than the sentence pause: measured pause positions, set by hand.
    beats["b01"]["s"] = [0.05, 4.11, 6.37, 11.43]
    beats["b02"]["s"] = [0.08, 3.96, 5.36]
    # b01 is cut in two in the pause after "... Delta Green." (3.38-4.11 s): the name falls on the title, the rest opens the problem chapter. Same indices as b01.
    cut = 3.85
    beats["b01b"] = {"dur": round(beats["b01"]["dur"] - cut, 2), "s": [round(4.11 - cut, 2)] + [round(s - cut, 2) for s in beats["b01"]["s"][1:]]}
    return beats


def opener_track() -> dict:
    """The combine track exactly as opener.py draws it, so that the scan transition cuts seamlessly into the opener."""
    sys.path.insert(0, str(HERE))
    import opener
    d = opener.load_data()
    n = len(d["track"])
    k = int(1 + ((opener_cut() - 1.0) / 12.0) ** 2.6 * (n - 1))             # progress of opener.py at the cut point
    return {"size": d["size"], "swath": d["swath_m"], "M": opener.M, "k": k, "n": n,
            "xy": np.round(d["track"][:k], 1).tolist(), "rank": np.round(d["track_rank"][:k], 3).tolist(), "cut": opener_cut()}


def opener_cut() -> float:
    return 5.55                                             # seconds into the opener where the film cuts in (see build_film.py)


def main() -> None:
    fys = barc_field_years()
    sc = scatter()
    verify(fys, sc)
    data = {"field": main_field(fys), "wall": [{k: v for k, v in f.items() if not k.startswith("_")} for f in fys], "map": austria(), "scatter": sc,
            "blocks": BLOCKS, "freeze": {"tag": "freeze-at-3", "commit": "5c716a9"}, "beats": voice_beats(), "track": opener_track()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "data.js").write_text("const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")
    print("data.js", round((OUT / "data.js").stat().st_size / 1024), "KB")


if __name__ == "__main__":
    main()
