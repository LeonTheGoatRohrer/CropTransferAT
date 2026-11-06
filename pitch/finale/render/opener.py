"""Finale video, scene 1 (0:00-0:25): the real combine track, then the real Sentinel-2 pixels of the same field.

Every map value is measured data (USDA BARC, public domain). The field was chosen by rule: rho next to the median of all
41 field-years (0,68) and practically no cell far from a combine point (results/2026-11-06_within_field_coverage). Colours show the rank inside the
field, so both maps use the same scale. Nothing is generated.

Usage:  python opener.py --preview 3,9,16,21,24     (PNG frames at these seconds)
        python opener.py [--captions]               (1080p60 video, audio from opener_audio.py if present)
Needs:  fontTools + brotli (fonts are converted once from web/node_modules), matplotlib/contourpy, scipy, Pillow.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import zipfile
from pathlib import Path

import contourpy
import geopandas as gpd
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter, zoom
from scipy.stats import rankdata, spearmanr

MAIN = Path(os.environ.get("DG_MAIN", r"C:\Users\mario\CropTransferAT"))
HERE = Path(__file__).resolve().parent
CACHE = HERE.parent / ".cache"
EXPORT = HERE.parent / "export"
W, H, FPS, DURATION = 1920, 1080, 60, 25.0
FIELD = {"zip": "2021.zip", "raw": "2021/1B--FarmServices_Raw_Yield_Data_PointShapefile_UTM/USDA_EastFarm_5_12_2021_Corn_utm",
         "pixels": "BARC_BARC_EastFarm_5_12_2021.parquet", "id": "EastFarm_5_12", "year": 2021, "label": "Feld 5-12, 2021"}
M = 4.0                                     # master layers: pixels per metre
BG = (10, 14, 10)
INK = (238, 240, 228)
MUTED = (150, 158, 140)
RAMP = [(0.0, (228, 88, 62)), (0.28, (214, 152, 66)), (0.5, (196, 188, 92)), (0.72, (112, 170, 88)), (1.0, (26, 118, 78))]
LOGO = [((32, 8.31), (24, 22.18), (40, 22.18), "#23704a"), ((22, 25.64), (14, 39.51), (30, 39.51), "#55a05a"),
        ((24, 24.49), (40, 24.49), (32, 38.36), "#9dbb5c"), ((42, 25.64), (34, 39.51), (50, 39.51), "#e4694a"),
        ((12, 42.98), (4, 56.84), (20, 56.84), "#9dbb5c"), ((14, 41.82), (30, 41.82), (22, 55.69), "#55a05a"),
        ((32, 42.98), (24, 56.84), (40, 56.84), "#c4a44b"), ((34, 41.82), (50, 41.82), (42, 55.69), "#55a05a"),
        ((52, 42.98), (44, 56.84), (60, 56.84), "#8a6a36")]
CAPTIONS = [(6.0, 9.2, "Das hier hat ein Mähdrescher im Herbst gemessen."),
            (14.2, 18.6, "Und das hier hat ein Satellit gesehen. Aus 786 Kilometern Höhe, mitten im Sommer."),
            (20.2, 22.4, "Beide wussten nichts voneinander.")]


# ------------------------------------------------------------------------------------- helpers
def ease(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def window(t: float, a: float, b: float, fade: float = 0.5) -> float:
    return ease((t - a) / fade) * (1 - ease((t - (b - fade)) / fade))


def ramp_colour(r: np.ndarray) -> np.ndarray:
    xs = [p for p, _ in RAMP]
    return np.stack([np.interp(r, xs, [c[i] for _, c in RAMP]) for i in range(3)], axis=-1)


def font(kind: str, size: int, weight: int = 500) -> ImageFont.FreeTypeFont:
    names = {"display": ("bricolage-grotesque", "bricolage-grotesque-latin-wght-normal"),
             "sans": ("instrument-sans", "instrument-sans-latin-wght-normal"),
             "mono": ("jetbrains-mono", "jetbrains-mono-latin-wght-normal")}
    package, stem = names[kind]
    ttf = CACHE / "fonts" / f"{stem}.ttf"
    if not ttf.exists():
        from fontTools.ttLib import TTFont
        ttf.parent.mkdir(parents=True, exist_ok=True)
        f = TTFont(MAIN / "web/node_modules/@fontsource-variable" / package / "files" / f"{stem}.woff2")
        f.flavor = None
        f.save(ttf)
    out = ImageFont.truetype(str(ttf), size)
    out.set_variation_by_axes([weight])
    return out


def text_layer(text: str, fnt, fill=INK, tracking: int = 0) -> Image.Image:
    """Tight RGBA image of a text line, cached by the caller."""
    widths = [fnt.getlength(c) + tracking for c in text] if tracking else [fnt.getlength(text)]
    w, h = int(sum(widths)) + 8, int(fnt.size * 1.5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tracking:
        x = 2.0
        for c, cw in zip(text, widths):
            d.text((x, 2), c, font=fnt, fill=fill)
            x += cw
    else:
        d.text((2, 2), text, font=fnt, fill=fill)
    return im


def with_alpha(im: Image.Image, a: float) -> Image.Image:
    out = im.copy()
    out.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return out


# ------------------------------------------------------------------------------------- data
def load_data() -> dict:
    data = MAIN / "data"
    stem = FIELD["raw"]
    CACHE.mkdir(parents=True, exist_ok=True)
    if not (CACHE / f"{stem}.shp").exists():
        with zipfile.ZipFile(data / "raw/barc" / FIELD["zip"]) as z:
            for ext in (".shp", ".shx", ".dbf", ".prj"):
                z.extract(stem + ext, CACHE)
    raw = gpd.read_file(CACHE / f"{stem}.shp").sort_values("Obj__Id")       # acquisition order = the real driving path
    raw = raw[raw.Area_Count == "On"]
    x, y = raw.geometry.x.to_numpy(), raw.geometry.y.to_numpy()
    yld = raw.Yld_Vol_Dr.to_numpy()
    swath_m = float(raw.Swth_Wdth_.median()) * 0.3048       # header width in the raw file, feet
    harvest = pd.to_datetime(raw.Time).dt.date.mode().iloc[0]

    px = pd.read_parquet(data / "interim/pixels" / FIELD["pixels"])
    pts = pd.read_parquet(data / "processed/gt_yield_points.parquet")
    pts = pts[(pts.dataset == "BARC") & (pts.field_id == FIELD["id"]) & (pts.year == FIELD["year"])].copy()
    pts["x"], pts["y"] = pts.x.round(1), pts.y.round(1)
    px["x"], px["y"] = px.x.round(1), px.y.round(1)
    both = px.merge(pts[["x", "y", "yield_t_ha"]], on=["x", "y"], how="inner")
    both["rel"] = both.yield_t_ha / both.yield_t_ha.mean()
    rho = float(spearmanr(both.ndvi_w2, both.rel).statistic)

    x0, y0 = min(x.min(), px.x.min()) - 12, min(y.min(), px.y.min()) - 12
    x1, y1 = max(x.max(), px.x.max()) + 12, max(y.max(), px.y.max()) + 12
    to_m = lambda ex, ny: ((ny - y0) * M, (ex - x0) * M)    # rotate 90 deg clockwise: north -> right, long axis horizontal
    size = (int((y1 - y0) * M), int((x1 - x0) * M))

    # weak zones: measured relative yield < 0.85 on the 10 m grid, lightly smoothed only to draw a clean line
    xs, ys = np.sort(both.x.unique()), np.sort(both.y.unique())
    grid, mask = np.zeros((len(ys), len(xs))), np.zeros((len(ys), len(xs)))
    ix, iy = np.searchsorted(xs, both.x), np.searchsorted(ys, both.y)
    grid[iy, ix], mask[iy, ix] = both.rel, 1
    weight = gaussian_filter(mask, 1.0)
    smooth = gaussian_filter(grid, 1.0) / np.maximum(weight, 1e-3)
    smooth[weight < 0.35] = 2.0
    factor = 4                                              # finer grid only so that the drawn line is not stair-stepped
    fine = zoom(smooth, factor, order=3)
    fx, fy = np.linspace(xs[0], xs[-1], fine.shape[1]), np.linspace(ys[0], ys[-1], fine.shape[0])
    lines = contourpy.contour_generator(fx, fy, fine).lines(0.85)
    contours = [np.column_stack(to_m(c[:, 0], c[:, 1])) for c in lines if len(c) >= 90]   # no specks

    return {"track": np.column_stack(to_m(x, y)), "track_rank": (rankdata(yld) - 1) / (len(yld) - 1), "n_points": len(raw),
            "harvest": harvest, "pix": np.column_stack(to_m(both.x.to_numpy(), both.y.to_numpy())),
            "pix_rank": (rankdata(both.ndvi_w2) - 1) / (len(both) - 1), "rho": rho, "n_pix": len(both), "contours": contours,
            "size": size, "swath_m": swath_m}


# ------------------------------------------------------------------------------------- renderer
class Opener:
    def __init__(self, d: dict, captions: bool = False):
        self.d, self.captions = d, captions
        self.size = d["size"]
        self.tracks = Image.new("RGBA", self.size, (0, 0, 0, 0))
        self.tracks_draw = ImageDraw.Draw(self.tracks)
        self.drawn = 1
        self.colours = ramp_colour(d["track_rank"]).astype(int)
        self.pixels = Image.new("RGBA", self.size, (0, 0, 0, 0))
        self.pix_draw = ImageDraw.Draw(self.pixels)
        self.pix_col = ramp_colour(d["pix_rank"]).astype(int)
        seed = np.random.default_rng(42)
        self.pix_delay = seed.uniform(0, 0.25, len(d["pix"]))
        self.pix_done = np.zeros(len(d["pix"]), bool)
        self.grain = [np.random.default_rng(i).normal(0, 2.4, (H, W, 1)).astype(np.float32) for i in range(6)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
        self.vignette = (1 - 0.42 * np.clip(r - 0.35, 0, 1) ** 1.6)[..., None]
        self.bg = Image.new("RGBA", (W, H), BG + (255,))
        self.txt: dict = {}

    def label(self, key, text, kind="mono", size=26, weight=500, fill=INK, tracking=0):
        k = (key, text, size)
        if k not in self.txt:
            self.txt[k] = text_layer(text, font(kind, size, weight), fill, tracking)
        return self.txt[k]

    def draw_tracks_until(self, k: int) -> None:
        p, c = self.d["track"], self.colours
        width = int(self.d["swath_m"] * M) + 3
        for i in range(self.drawn, k):
            if np.hypot(*(p[i] - p[i - 1])) < 22 * M:       # skip jumps between passes
                self.tracks_draw.line([tuple(p[i - 1]), tuple(p[i])], fill=tuple(c[i]) + (255,), width=width)
        self.drawn = max(self.drawn, k)

    @staticmethod
    def place(frame: Image.Image, layer: Image.Image, scale: float, ox: float, oy: float, alpha: float = 1.0) -> None:
        if alpha <= 0.003:
            return
        w, h = max(1, int(layer.width * scale)), max(1, int(layer.height * scale))
        r = layer.resize((w, h), Image.BICUBIC)
        if alpha < 0.997:
            r = with_alpha(r, alpha)
        frame.alpha_composite(r, (int(ox), int(oy))) if ox >= 0 and oy >= 0 else frame.paste(r, (int(ox), int(oy)), r)

    def frame(self, t: float) -> np.ndarray:
        d = self.d
        f = self.bg.copy()
        sw, sh = self.size
        n = len(d["track"])

        # --- camera: slow push-in on the full map, then the two stacked strips
        fit = min(1720 / sw, 900 / sh)
        push = fit * (1 + 0.035 * ease(t / 18.8))
        split = ease((t - 18.8) / 1.6)
        strip_scale = min(860 / sw, 720 / sh)
        scale = push + (strip_scale - push) * split
        cx0, cy0 = W / 2 - sw * push / 2, H / 2 - sh * push / 2 + 18
        left_x, right_x = W / 2 - 40 - sw * strip_scale, W / 2 + 40
        strip_y = 218

        # --- combine track, real driving order (accelerating)
        prog = ((min(t, 13.0) - 1.0) / 12.0) ** 2.6 if t > 1.0 else 0.0
        k = int(1 + prog * (n - 1))
        self.draw_tracks_until(k)
        ppos_alpha = 1 - 0.8 * ease((t - 14.0) / 2.5)
        tracks_x = cx0 + (left_x - cx0) * split
        tracks_y = cy0 + (strip_y - cy0) * split
        tracks_alpha = ppos_alpha if t < 18.8 else min(1.0, 0.2 + 0.8 * split)
        self.place(f, self.tracks, scale, tracks_x, tracks_y, tracks_alpha)

        # head of the combine: bright point with a blurred trail
        if 1.0 < t < 13.25:
            head = d["track"][min(k, n - 1)] * scale + (tracks_x, tracks_y)
            trail = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            td = ImageDraw.Draw(trail)
            for j in range(max(1, k - 26), min(k, n - 1)):
                if np.hypot(*(d["track"][j] - d["track"][j - 1])) < 22 * M:
                    a = d["track"][j - 1] * scale + (tracks_x, tracks_y)
                    b = d["track"][j] * scale + (tracks_x, tracks_y)
                    td.line([tuple(a), tuple(b)], fill=(255, 250, 225, int(60 + 180 * (j - k + 26) / 26)), width=7)
            td.ellipse([head[0] - 7, head[1] - 7, head[0] + 7, head[1] + 7], fill=(255, 255, 240, 255))
            box = (int(max(head[0] - 260, 0)), int(max(head[1] - 260, 0)), int(min(head[0] + 260, W)), int(min(head[1] + 260, H)))
            f.alpha_composite(trail.crop(box).filter(ImageFilter.GaussianBlur(16)), box[:2])
            f.alpha_composite(trail.crop(box).filter(ImageFilter.GaussianBlur(1.2)), box[:2])

        # --- satellite pixels, swept in by a scan line
        beam = (t - 14.0) / 4.4
        if beam > 0:
            bx = beam * (sw + 400) - 200
            arrive = (d["pix"][:, 0] + 200) / (sw + 400) * 4.4 + 14.0 + self.pix_delay
            half = 5 * M
            pop = 0.32
            live = Image.new("RGBA", self.size, (0, 0, 0, 0))
            ld = ImageDraw.Draw(live)
            for i, (pos, c) in enumerate(zip(d["pix"], self.pix_col)):
                if self.pix_done[i] or t < arrive[i]:
                    continue
                age = (t - arrive[i]) / pop
                if age >= 1:
                    self.pix_draw.rectangle([pos[0] - half + 1.5, pos[1] - half + 1.5, pos[0] + half - 1.5, pos[1] + half - 1.5], fill=tuple(c) + (255,))
                    self.pix_done[i] = True
                else:
                    e = ease(age)
                    h2 = half * (0.35 + 0.65 * e) - 1.5
                    flash = (c + (255 - c) * (1 - e) * 0.85).astype(int)
                    ld.rectangle([pos[0] - h2, pos[1] - h2, pos[0] + h2, pos[1] + h2], fill=tuple(flash) + (int(255 * e),))
            pix_x = cx0 + (right_x - cx0) * split
            pix_y = cy0 + (strip_y - cy0) * split
            self.place(f, self.pixels, scale, pix_x, pix_y)
            self.place(f, live, scale, pix_x, pix_y)
            if beam < 1:
                x = pix_x + bx * scale
                glow = Image.new("RGBA", (260, H), (0, 0, 0, 0))
                ImageDraw.Draw(glow).rectangle([126, 0, 133, H], fill=(175, 225, 255, 170))
                f.alpha_composite(glow.filter(ImageFilter.GaussianBlur(26)), (int(np.clip(x - 130, 0, W - 260)), 0))
                ImageDraw.Draw(f).line([(x, 0), (x, H)], fill=(215, 240, 255, 255), width=2)

            # --- weak zones measured by the combine, drawn on both strips
            reveal = ease((t - 20.3) / 1.5)
            if reveal > 0:
                od = ImageDraw.Draw(f)
                total = sum(len(c) for c in d["contours"])
                left = reveal * total
                for c in d["contours"]:
                    m = int(min(len(c), left))
                    left -= m
                    if m < 2:
                        continue
                    for ox in (left_x, right_x):
                        od.line([tuple(q) for q in (c[:m] * strip_scale + (ox, strip_y))], fill=(255, 255, 255, 255), width=3, joint="curve")

        self.overlays(f, t, k)
        arr = np.asarray(f.convert("RGB"), dtype=np.float32)

        # --- title: logo assembles, the map falls back
        title = ease((t - 22.6) / 0.8)
        if title > 0:
            arr = arr * (1 - 0.95 * title) + np.array(BG, np.float32) * 0.95 * title
            g = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")
            self.title(g, t)
            arr = np.asarray(g.convert("RGB"), dtype=np.float32)

        arr = arr * self.vignette + self.grain[int(t * FPS) % len(self.grain)]
        fade = ease(t / 0.4) * (1 - ease((t - (DURATION - 0.5)) / 0.5))
        return (arr * fade).clip(0, 255).astype(np.uint8)

    def overlays(self, f: Image.Image, t: float, k: int) -> None:
        d = self.d
        d1 = d["harvest"].strftime("%d.%m.%Y")
        main = window(t, 1.6, 13.9, 0.6)
        if main > 0:
            f.alpha_composite(with_alpha(self.label("a", "HERBST · MÄHDRESCHER", size=24, tracking=3), main), (92, 52))
            count = f"{min(int(1 + ((min(t, 13) - 1) / 12) ** 2.6 * (d['n_points'] - 1)), d['n_points']):,}".replace(",", ".")
            f.alpha_composite(with_alpha(self.label("b", f"{count} GPS-Messpunkte  ·  Ernte {d1}", size=20, fill=MUTED), main), (92, 88))
        sat = window(t, 14.3, 18.9, 0.5)
        if sat > 0:
            f.alpha_composite(with_alpha(self.label("c", "HOCHSOMMER · SENTINEL-2", size=24, tracking=3), sat), (92, 52))
            f.alpha_composite(with_alpha(self.label("d", f"16.7.–15.8.{FIELD['year']}  ·  786 km Höhe  ·  10-m-Zellen", size=20, fill=MUTED), sat), (92, 88))
        split = window(t, 19.7, 23.2, 0.6)
        if split > 0:
            sw = self.size[0] * min(860 / self.size[0], 720 / self.size[1])
            lx, rx = int(W / 2 - 40 - sw), int(W / 2 + 40)
            f.alpha_composite(with_alpha(self.label("e", "GEMESSEN IM HERBST", size=22, tracking=3), split), (lx, 72))
            f.alpha_composite(with_alpha(self.label("f", "Mähdrescher am Boden", "display", 52, 600), split), (lx - 3, 104))
            f.alpha_composite(with_alpha(self.label("g", "GESEHEN IM SOMMER", size=22, tracking=3), split), (rx, 72))
            f.alpha_composite(with_alpha(self.label("h", "Satellit im Orbit", "display", 52, 600), split), (rx - 3, 104))
            zones = window(t, 20.8, 23.2, 0.6)
            if zones > 0:
                n_cells = f"{d['n_pix']:,}".replace(",", ".")
                rho = f"{d['rho']:.2f}".replace(".", ",")
                cap = self.label("i", f"Weiße Linie: schwache Zonen laut Mähdrescher  ·  Dieses Feld: Rangkorrelation {rho}  ·  {n_cells} Zellen", "sans", 22, fill=MUTED)
                f.alpha_composite(with_alpha(cap, zones), ((W - cap.width) // 2, 910))
        src = window(t, 2.2, 22.8, 0.8)
        if src > 0:
            f.alpha_composite(with_alpha(self.label("s", f"Echte Daten  ·  USDA BARC, Beltsville  ·  {FIELD['label']}  ·  Farbe = Rang im Feld", size=15, fill=(112, 120, 104)), src * 0.9), (92, H - 44))
        if self.captions:
            for a, b, text in CAPTIONS:
                v = window(t, a, b, 0.2)
                if v > 0:
                    im = self.label("cap", text, "sans", 34, 500)
                    pad = Image.new("RGBA", (im.width + 40, im.height + 14), (0, 0, 0, 170))
                    pad.alpha_composite(im, (20, 7))
                    f.alpha_composite(with_alpha(pad, v), ((W - pad.width) // 2, H - 128))

    def title(self, g: Image.Image, t: float) -> None:
        size = 3.2
        cx, cy = W / 2, 412
        draw = ImageDraw.Draw(g, "RGBA")
        for i, (a, b, c, col) in enumerate(LOGO):
            e = ease((t - 22.75 - i * 0.07) / 0.5)
            if e <= 0:
                continue
            pts = np.array([a, b, c], float) - (32, 32)
            tri_c = pts.mean(axis=0)
            spread = 1 + (1 - e) * 1.6
            pts = (pts - tri_c) * (0.5 + 0.5 * e) + tri_c * spread
            rgb = tuple(int(col[j:j + 2], 16) for j in (1, 3, 5))
            draw.polygon([tuple(p * size + (cx, cy)) for p in pts], fill=rgb + (int(255 * e),))
        e = ease((t - 23.45) / 0.55)
        if e > 0:
            f = font("display", 112, 650)
            w1, w2 = f.getlength("Delta "), f.getlength("Green")
            x = W / 2 - (w1 + w2) / 2
            y = 546 + (1 - e) * 16
            g.alpha_composite(with_alpha(self.label("t1", "Delta ", "display", 112, 650), e), (int(x), int(y)))
            g.alpha_composite(with_alpha(self.label("t2", "Green", "display", 112, 650, fill=(157, 187, 92)), e), (int(x + w1), int(y)))
        e = ease((t - 23.85) / 0.5)
        if e > 0:
            sub = self.label("t3", "Sichtbar machen, wo im Feld Ertrag fehlt.", "sans", 32, 400, fill=(190, 196, 178))
            g.alpha_composite(with_alpha(sub, e), (int((W - sub.width) / 2), 712))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--preview", default=None, help="comma separated seconds")
    ap.add_argument("--captions", action="store_true", help="burn in the narration text (review only)")
    a = ap.parse_args()
    d = load_data()
    print(f"points {d['n_points']}, cells {d['n_pix']}, rho {d['rho']:.3f}, harvest {d['harvest']}, contours {len(d['contours'])}, master {d['size']}", flush=True)
    r = Opener(d, a.captions)
    if a.preview:
        out = CACHE / "preview"
        out.mkdir(parents=True, exist_ok=True)
        times = sorted(float(x) for x in a.preview.split(","))
        step = 0.1
        tnow = 0.0
        for s in times:
            while tnow < s - step:              # stateful layers need the earlier frames to have happened
                tnow += step
                r.frame(tnow)
            Image.fromarray(r.frame(s)).save(out / f"t{s:05.1f}.png")
            tnow = s
            print("saved", s, flush=True)
        return
    EXPORT.mkdir(parents=True, exist_ok=True)
    silent = EXPORT / "_opener_video.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", str(silent)]
    pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(DURATION * FPS)
    for i in range(total):
        pipe.stdin.write(r.frame(i / FPS).tobytes())
        if i % 300 == 0:
            print(f"{i}/{total}", flush=True)
    pipe.stdin.close()
    pipe.wait()
    audio = EXPORT / "_opener_audio.wav"
    name = "DeltaGreen_Einstieg_mit_Text.mp4" if a.captions else "DeltaGreen_Einstieg.mp4"
    mux = ["ffmpeg", "-y", "-v", "error", "-i", str(silent)] + (["-i", str(audio), "-c:a", "aac", "-b:a", "256k", "-shortest"] if audio.exists() else []) + ["-c:v", "copy", "-movflags", "+faststart", str(EXPORT / name)]
    subprocess.run(mux, check=True)
    print("done", EXPORT / name, flush=True)


if __name__ == "__main__":
    main()
