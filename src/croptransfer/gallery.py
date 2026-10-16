"""Sentinel-2 galleries of training fields for the website (reports/figures/overview_*.png).

Needs Earth Engine access (init_ee). Reads data/processed/gt_field_years.parquet, gt_yield_points.parquet
and features_0901.parquet (for RY). Usage:

    python -m croptransfer.gallery barc   # one BARC field, bad vs good year
    python -m croptransfer.gallery kbs    # KBS plots 2017 coloured by RY
"""
from __future__ import annotations

import io
import sys
import urllib.request
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import shapely.wkb
from PIL import Image
from shapely.ops import unary_union

from croptransfer.config import load_config
from croptransfer.gee_extract import init_ee

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

S2 = "COPERNICUS/S2_SR_HARMONIZED"
CS = "GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED"
NDVI_PALETTE = ["a50026", "f46d43", "fee08b", "d9ef8b", "66bd63", "006837"]
RGB_VIS = dict(bands=["B4", "B3", "B2"], min=0, max=1800, gamma=1.3)

BARC_FIELD = "EastFarm_5_12"
BARC_YEARS = {2018: "RY 0,53 (schlechtes Jahr)", 2021: "RY 1,42 (gutes Jahr)"}
MONTHS = [(6, "Juni"), (7, "Juli"), (8, "August"), (9, "September")]
KBS_YEAR = 2017
RISK_RY = 0.85


def _paths() -> tuple[Path, Path]:
    cfg = load_config()
    return Path(cfg["paths"]["processed"]), Path(cfg["paths"]["figures"])


def _s2_median(region, start: str, end: str, cs_min: float):
    """Cloud-masked Sentinel-2 median composite in [start, end)."""
    import ee

    col = ee.ImageCollection(S2).filterBounds(region).filterDate(start, end)
    col = col.linkCollection(ee.ImageCollection(CS), ["cs_cdf"])
    col = col.map(lambda i: i.updateMask(i.select("cs_cdf").gte(cs_min)))
    return col.median(), col.size()


def _thumb(img, region, dimensions: int = 300) -> np.ndarray:
    url = img.getThumbURL({"region": region, "dimensions": dimensions, "format": "png"})
    return np.array(Image.open(io.BytesIO(urllib.request.urlopen(url).read())).convert("RGBA"))


def _ndvi_vis(img):
    return img.normalizedDifference(["B8", "B4"]).visualize(min=0.2, max=0.9, palette=NDVI_PALETTE)


def gallery_barc(out: Path, cs_min: float) -> Path:
    """Same BARC field in a bad and a good year: RGB per month, NDVI Jul/Aug, combine yield map."""
    import ee

    proc, _ = _paths()
    gt = pd.read_parquet(proc / "gt_field_years.parquet")
    pts = pd.read_parquet(proc / "gt_yield_points.parquet")
    fig, axes = plt.subplots(2, 7, figsize=(21, 6.6))
    for r, (year, label) in enumerate(BARC_YEARS.items()):
        row = gt[(gt.field_id == BARC_FIELD) & (gt.year == year)].iloc[0]
        geom = shapely.wkb.loads(row.geometry)
        region = ee.Geometry.Rectangle(list(geom.buffer(0.0015).envelope.bounds))
        outline = ee.Image().byte().paint(ee.FeatureCollection([ee.Feature(ee.Geometry(geom.__geo_interface__))]), 1, 2)
        for c, (m, mname) in enumerate(MONTHS):
            start = ee.Date.fromYMD(year, m, 1)
            img, n = _s2_median(region, start, start.advance(1, "month"), cs_min)
            rgb = img.visualize(**RGB_VIS).blend(outline.visualize(palette=["ffff00"]))
            ax = axes[r, c]
            ax.imshow(_thumb(rgb, region))
            ax.set_title(f"{year} {mname} (n={n.getInfo()} Szenen)", fontsize=9)
            ax.axis("off")
        for c, (m, mname) in zip([4, 5], [(7, "Juli"), (8, "August")]):
            start = ee.Date.fromYMD(year, m, 1)
            img, _ = _s2_median(region, start, start.advance(1, "month"), cs_min)
            ndvi = _ndvi_vis(img).blend(outline.visualize(palette=["000000"]))
            ax = axes[r, c]
            ax.imshow(_thumb(ndvi, region))
            ax.set_title(f"{year} NDVI {mname} (0,2–0,9)", fontsize=9)
            ax.axis("off")
        p = pts[(pts.field_id == BARC_FIELD) & (pts.year == year)]
        ax = axes[r, 6]
        sc = ax.scatter(p.x, p.y, c=p.yield_t_ha, s=6, cmap="RdYlGn", vmin=2, vmax=14, marker="s")
        ax.set_aspect("equal")
        ax.set_title(f"{year} Mähdrescher-Ertrag, Mittel {row.Y_t_ha:.1f} t/ha", fontsize=9)
        ax.axis("off")
        fig.colorbar(sc, ax=ax, fraction=0.04, label="t/ha")
        axes[r, 0].text(-0.08, 0.5, label, transform=axes[r, 0].transAxes, rotation=90, va="center",
                        ha="right", fontsize=11, weight="bold")
    fig.suptitle(f"BARC (Maryland) Feld {BARC_FIELD}: dasselbe Feld in einem schlechten und einem guten Jahr – "
                 "Sentinel-2 Echtfarbe (Monatsmedian, gelb = Feldgrenze), NDVI und gemessener Ertrag", fontsize=12)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


def gallery_kbs(out: Path, cs_min: float) -> Path:
    """KBS MCSE plots in one year, outlined by RY class (magenta = at risk)."""
    import ee

    proc, _ = _paths()
    gt = pd.read_parquet(proc / "gt_field_years.parquet").drop(columns=["RY_descr"], errors="ignore")
    f = pd.read_parquet(proc / "features_0901.parquet")[["fy_key", "RY_descr"]]
    k = gt[(gt.dataset == "KBS") & (gt.year == KBS_YEAR)].merge(f, on="fy_key")
    geoms = [shapely.wkb.loads(g) for g in k.geometry]
    region = ee.Geometry.Rectangle(list(unary_union(geoms).buffer(0.0008).envelope.bounds))
    feats = [ee.Feature(ee.Geometry(g.__geo_interface__), {"c": 2 if ry < RISK_RY else 1})
             for g, ry in zip(geoms, k.RY_descr)]
    ov = ee.Image().byte().paint(ee.FeatureCollection(feats), "c", 2).visualize(min=1, max=2, palette=["00ffff", "ff00ff"])
    img, _ = _s2_median(region, f"{KBS_YEAR}-07-20", f"{KBS_YEAR}-08-31", cs_min)
    rgb = img.visualize(**RGB_VIS).blend(ov)
    ndvi = _ndvi_vis(img).blend(ov)
    fig, ax = plt.subplots(1, 2, figsize=(13, 6.4))
    ax[0].imshow(_thumb(rgb, region, 500))
    ax[0].set_title(f"Sentinel-2 Echtfarbe, Median 20.7.–31.8.{KBS_YEAR}")
    ax[1].imshow(_thumb(ndvi, region, 500))
    ax[1].set_title("NDVI (0,2 rot – 0,9 grün)")
    for a in ax:
        a.axis("off")
    n_risk = int((k.RY_descr < RISK_RY).sum())
    fig.suptitle(f"KBS Michigan, {len(k)} Versuchsparzellen à ~0,58 ha (≈ 58 S2-Pixel, ≈ 6 HLS-Pixel) – "
                 f"magenta = gefährdet {KBS_YEAR} (RY < 0,85, n = {n_risk}), cyan = normal", fontsize=11)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


def main(argv: list[str] | None = None) -> int:
    which = (argv or sys.argv[1:] or ["barc", "kbs"])
    cfg = load_config()
    cs_min = float(cfg["gee"]["s2_cloudscore_min"])
    _, figures = _paths()
    figures.mkdir(parents=True, exist_ok=True)
    init_ee()
    for w in which:
        if w == "barc":
            print("saved", gallery_barc(figures / "overview_s2_gallery_barc.png", cs_min))
        elif w == "kbs":
            print("saved", gallery_kbs(figures / "overview_s2_gallery_kbs.png", cs_min))
        else:
            raise SystemExit(f"unknown gallery: {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
