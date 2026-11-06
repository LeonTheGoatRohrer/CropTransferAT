"""Assemble the Delta Green finale film: AI mood clips, motion graphics from real data, the opener, app recording, voice, music, SFX.

The voice sets the timing: every segment is as long as its measured voice line plus LEAD and TAIL. The voice is never sped up.

Usage:  python build_film.py --plan             write ../export/mg/timeline.js and print the render list for render_mg.mjs
        python build_film.py [--width 960]      build the film (--width 1920 also needs the clips in ../export/ai1080)
        python build_film.py --anon             variant with aggregated values and without place names
        python build_film.py --audio-only       keep the picture, only remix the sound
Output: ../export/DeltaGreen_Finale_{Prototyp,1080p}[_ohne_Ortsnamen].mp4 (not in the repository).
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EXPORT = HERE.parent / "export"
BUILD = EXPORT / "build"
AI, MG, VOICE, SFX, MGDIR = EXPORT / "ai", EXPORT / "mgclips", EXPORT / "voice", EXPORT / "sfx", EXPORT / "mg"
FONTS = HERE.parent / ".cache" / "fonts"
OPENER = EXPORT / "DeltaGreen_Einstieg.mp4"
OPENER_AUDIO = EXPORT / "_opener_audio.wav"
OPENER_CUT = 5.55       # seconds into the opener where the film cuts in; the same value is used by export_data.py
FPS, SR = 25, 48000
AI_LABEL = "KI-generierte Illustration"

ap = argparse.ArgumentParser()
ap.add_argument("--width", type=int, default=960)
ap.add_argument("--plan", action="store_true")
ap.add_argument("--anon", action="store_true")
ap.add_argument("--audio-only", action="store_true")
args = ap.parse_args()
W, H = args.width, args.width * 9 // 16
if W >= 1920:
    AI = EXPORT / "ai1080"      # the mood clips in high resolution; same frames and length as the drafts, so all cuts stay
SUF = "_anon" if args.anon else ""
SWAP = {"f01": "x01", "f02": "x02"} if args.anon else {}
BUILD_DIR = BUILD / f"w{W}{SUF}"


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout
    return float(out)


def vd(name: str) -> float:
    return duration(VOICE / f"{SWAP.get(name, name)}.mp3")


def run(cmd: list[str]) -> None:
    subprocess.run(["ffmpeg", "-y", "-v", "error", *cmd], check=True)


def clip(name, start=0.0, dur=3.0, speed=1.0):
    return {"file": AI / f"{name}.mp4", "start": start, "dur": dur, "speed": speed}


def mg(sid, scene, voice=None, lead=0.3, tail=0.6, dur=None, variant=False):
    d = dur if dur is not None else lead + vd(voice) + tail
    return {"id": sid, "kind": "mg", "scene": scene, "dur": round(d, 2), "voice": (voice, lead) if voice else None, "lead": lead, "variant": variant}


def segments() -> list[dict]:
    b01 = vd("b01")
    c01 = vd("c01")
    return [
        # 1 cold open: cuts sit on the music accents, almost no speech
        {"id": "black0", "kind": "black", "dur": 0.25},
        {"id": "c_night", "kind": "film", "clips": [clip("a08_night", 2.4, 1.3)], "bars": True},
        {"id": "c_rain", "kind": "film", "clips": [clip("a03_rain", 1.3, 1.7)], "bars": True},
        {"id": "c_storm", "kind": "film", "clips": [clip("a09_storm", 1.0, 1.3)], "bars": True},
        {"id": "c_grain", "kind": "film", "clips": [clip("a11_grain", 1.0, 1.2)], "bars": True},
        {"id": "c_drone", "kind": "film", "clips": [clip("a10_rise", 0.3, 1.8)], "bars": True},
        {"id": "c_combine", "kind": "film", "clips": [clip("a01_combine", 0.5, 1.5)], "bars": True},
        mg("freeze", "freezescan", dur=1.7),
        # The opener's own fade starts at 24.5 s, too soon to read the title: hold its last clean frame, then fade.
        {"id": "opener", "kind": "file", "file": OPENER, "start": OPENER_CUT, "dur": 24.45 - OPENER_CUT, "hold": 2.3, "voice": ("a01", 9.0 - OPENER_CUT), "voice2": ("a02", 16.2 - OPENER_CUT)},
        # 2 problem
        {"id": "b_film", "kind": "film", "clips": [clip("a06_rows", 0.8, 3.4)], "plate": "p_ch0", "voice": ("b01", 0.3)},
        {"id": "spread", "kind": "mg", "scene": "spread", "dur": round(0.3 + b01 + 0.6 - 3.4, 2), "voice": None, "lead": -3.1},
        mg("nomap", "nomap", "b02"),
        # 3 solution: the scan into real pixels falls on "Sein Bild zeigt ..."
        {"id": "c_sat", "kind": "film", "clips": [clip("a12_sat", 0.0, 6.2, 0.97)], "plate": "p_sat", "voice": ("c01", 0.2)},
        {"id": "c_desc", "kind": "film", "clips": [clip("a05_descent", 3.9, 3.1)], "plate": "p_desc"},
        {"id": "zoom", "kind": "mg", "scene": "zoom", "dur": round(0.2 + c01 + 0.7 - 9.3, 2), "voice": None, "lead": -9.1},
        mg("wall", "wall", "c02", tail=1.0),
        mg("quart", "quart", "c03", tail=0.8),
        mg("tiles", "tiles", "c04", tail=0.9),
        mg("failed", "failed", "c05", tail=0.8),
        # 4 data
        mg("sources", "sources", "d01", lead=0.5, tail=0.8),
        mg("zero", "zero", "d02", tail=0.7),
        mg("freezeoo", "freezeoo", "d03", tail=1.0),
        mg("stmk", "stmk", "d04", tail=1.3),
        # 5 product
        # Shots follow the sentences of e01/e02. Crops stay inside the content, so that no control is cut off; the caption covers the page below.
        {"id": "app_d_map", "kind": "app", "file": EXPORT / "app" / "d_map.webm", "start": 0.0, "dur": 5.6, "voice": ("e01", 0.3),
         "z0": (0, 136, 1500, 844), "z1": (80, 156, 1340, 754), "caption": ("FELD D · USA", "Der Prototyp. Dieses Feld kannte das Verfahren nicht.")},
        {"id": "app_d_curve", "kind": "app", "file": EXPORT / "app" / "d_curve.webm", "start": 0.0, "dur": 3.0,
         "z0": (330, 70, 1260, 709), "z1": (352, 76, 1216, 684), "caption": ("IM JULI UNTER DER REFERENZ", "Orange: dieses Feld. Grau: gesunde Referenz.")},
        {"id": "app_d_alarm", "kind": "app", "file": EXPORT / "app" / "d_alarm.webm", "start": 0.0, "dur": round(0.3 + vd("e01") + 0.6 - 8.6, 2),
         "z0": (330, 70, 1260, 709), "z1": (352, 76, 1216, 684), "caption": ("ALARM", "Geerntet: 75 % des Üblichen. Risiko 0,54, Schwelle 0,53.")},
        {"id": "app_e_alarm", "kind": "app", "file": EXPORT / "app" / "e_alarm.webm", "start": 0.0, "dur": 3.8, "voice": ("e02", 0.2),
         "z0": (330, 70, 1260, 709), "z1": (352, 76, 1216, 684), "caption": ("NACHBARFELD E", "Kein Alarm: 77 % des Üblichen, Risiko knapp unter der Schwelle.")},
        {"id": "app_e_map", "kind": "app", "file": EXPORT / "app" / "e_map.webm", "start": 0.0, "dur": round(0.2 + vd("e02") + 1.2 - 3.8, 2),
         "z0": (0, 160, 1500, 844), "z1": (40, 170, 1420, 799), "caption": ("EINE WARNUNG ZEIGT, WO", "Nicht warum.")},
        # 6 climax
        {"id": "black1", "kind": "black", "dur": 0.7},
        mg("mail", "mail", "f01", lead=0.5, tail=0.8, variant=True),
        mg("hatz", "hatz", "f02", tail=0.7, variant=True),
        mg("stamp", "stamp", "f03", tail=0.9),
        {"id": "f_heat", "kind": "film", "clips": [clip("a07_heat", 0.5, 3.2)], "plate": "p_ch4", "extra_label": "Stimmungsbild, nicht die Versuchsflächen"},
        mg("scatter", "scatter", "f04", lead=2.4, tail=0.4, variant=True),
        mg("big", "big", "f05", lead=0.5, tail=1.1),
        mg("lines", "lines", "f06", tail=1.3),
        # 7 end
        # pull back from the field up to the orbit
        {"id": "g_rise", "kind": "film", "clips": [clip("a10_rise", 1.5, 5.6), clip("a12_sat", 3.0, 3.0)], "voice": ("g01", 0.4)},
        mg("end", "end", dur=6.4),
    ]


SEGMENTS = segments()
LABEL_FONT = ImageFont.truetype(str(FONTS / "instrument-sans-latin-wght-normal.ttf"), max(10, int(22 * W / 1920)))


def label_png(extra: str | None = None) -> Path:
    path = BUILD_DIR / f"label{'_x' if extra else ''}.png"
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    text = f"{AI_LABEL}  ·  {extra}" if extra else AI_LABEL
    ImageDraw.Draw(im).text((W - 28 * W / 1920, H - 22 * W / 1920), text, font=LABEL_FONT, fill=(255, 255, 255, 170), anchor="rs")
    im.save(path)
    return path


def caption_png(key: str, title: str, sub: str) -> Path:
    path = BUILD_DIR / f"cap_{key}.png"
    s = W / 1920
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    top = H - 118 * s
    d.rectangle((0, top, W, H), fill=(10, 14, 10, 255))     # opaque: the page below must not shine through
    d.text((60 * s, top + 14 * s), title, font=ImageFont.truetype(str(FONTS / "jetbrains-mono-latin-wght-normal.ttf"), int(30 * s)), fill=(157, 187, 92, 255))
    d.text((60 * s, top + 54 * s), sub, font=ImageFont.truetype(str(FONTS / "instrument-sans-latin-wght-normal.ttf"), int(40 * s)), fill=(238, 240, 228, 255))
    im.save(path)
    return path


GRADE = f"scale={W}:{H}:flags=lanczos,eq=contrast=1.05:saturation=0.94,vignette=PI/5,noise=alls=4:allf=t,fps={FPS},format=yuv420p"
ENC = ["-c:v", "libx264", "-preset", "medium" if W >= 1920 else "veryfast", "-crf", "16" if W >= 1920 else "19", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]


def render_film(seg: dict, out: Path) -> None:
    inputs, chains, total = [], [], 0.0
    for i, c in enumerate(seg["clips"]):
        inputs += ["-ss", str(c["start"]), "-t", f"{c['dur'] * c['speed']:.3f}", "-i", str(c["file"])]
        chains.append(f"[{i}:v]setpts=PTS/{c['speed']},{GRADE}[c{i}]")
        total += c["dur"]
    n = len(seg["clips"])
    graph = ";".join(chains) + ";" + "".join(f"[c{i}]" for i in range(n)) + f"concat=n={n}:v=1[base]"
    last, k = "base", n
    if seg.get("plate"):
        inputs += ["-i", str(MG / f"{seg['plate']}{plate_suffix(seg)}.mp4")]
        # Screen blend must run in RGB; on YUV planes it shifts the chroma and tints everything magenta.
        graph += f";[{k}:v]scale={W}:{H},fps={FPS},format=gbrp[pl];[{last}]format=gbrp[fb];[fb][pl]blend=all_mode=screen:shortest=1,format=yuv420p[bl]"
        last, k = "bl", k + 1
    if seg.get("bars"):
        bar = int(H * 0.12)
        graph += f";[{last}]drawbox=x=0:y=0:w={W}:h={bar}:color=black:t=fill,drawbox=x=0:y={H - bar}:w={W}:h={bar}:color=black:t=fill[bb]"
        last = "bb"
    inputs += ["-i", str(label_png(seg.get("extra_label")))]
    graph += f";[{last}][{k}:v]overlay=0:0[out]"
    run([*inputs, "-filter_complex", graph, "-map", "[out]", "-t", f"{total:.3f}", *ENC, str(out)])


def plate_suffix(seg: dict) -> str:
    return ""


def render_app(seg: dict, out: Path) -> None:
    (x0, y0, w0, h0), (x1, y1, w1, h1) = seg["z0"], seg["z1"]
    d = seg["dur"]
    n = int(d * FPS)
    k = f"min(on/{n},1)"
    p = f"({k}*{k}*(3-2*{k}))"                                  # slow virtual camera inside the recording
    # zoompan, not crop: crop evaluates its size only once, so the camera would pan without ever zooming.
    # The doubled input keeps the move from stepping in whole pixels.
    zoom = f"zoompan=z='1920/({w0}+({w1}-{w0})*{p})':x='2*({x0}+({x1}-{x0})*{p})':y='2*({y0}+({y1}-{y0})*{p})':d=1:s={W}x{H}:fps={FPS}"
    graph = f"[0:v]fps={FPS},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={d},scale=3840:2160:flags=lanczos,{zoom},format=yuv420p[v]"
    inputs, last = ["-ss", str(seg["start"]), "-i", str(seg["file"])], "v"
    if seg.get("caption"):
        inputs += ["-i", str(caption_png(seg["id"], *seg["caption"]))]
        graph += ";[v][1:v]overlay=0:0:format=auto[o]"
        last = "o"
    run([*inputs, "-filter_complex", graph, "-map", f"[{last}]", "-t", str(d), *ENC, str(out)])


def render_mg(seg: dict, out: Path) -> None:
    suffix = SUF if seg.get("variant") else ""
    run(["-i", str(MG / f"{seg['scene']}{suffix}.mp4"), "-vf", f"scale={W}:{H}:flags=lanczos,noise=alls=2:allf=t,format=yuv420p", "-t", str(seg["dur"]), *ENC, str(out)])


def render_file(seg: dict, out: Path) -> None:
    hold = seg.get("hold", 0)
    total = seg["dur"] + hold
    vf = f"scale={W}:{H}:flags=lanczos,fps={FPS},tpad=stop_mode=clone:stop_duration={hold},noise=alls=2:allf=t,fade=t=out:st={total - .5:.2f}:d=0.5,format=yuv420p"
    run(["-ss", str(seg["start"]), "-t", str(seg["dur"]), "-i", str(seg["file"]), "-vf", vf, "-t", str(total), *ENC, str(out)])


def render_black(seg: dict, out: Path) -> None:
    run(["-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}", "-t", str(seg["dur"]), *ENC, str(out)])


def load_audio(path: Path, loudnorm: bool = False) -> np.ndarray:
    """Decode to float stereo at SR; shape (n, 2)."""
    af = ["-af", "loudnorm=I=-16:TP=-2:LRA=7"] if loudnorm else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), *af, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def place(buf: np.ndarray, sound: np.ndarray, when_s: float, gain: float = 1.0) -> None:
    i = int(when_s * SR)
    if i < 0:
        sound, i = sound[-i:], 0
    if i >= len(buf):
        return
    n = min(len(sound), len(buf) - i)
    buf[i:i + n] += sound[:n] * gain


def ramp(n: int, points: list[tuple[float, float]]) -> np.ndarray:
    """Piecewise-linear gain curve from (seconds, gain) points."""
    xs, ys = zip(*points)
    return np.interp(np.arange(n) / SR, xs, ys)


def mix_audio(at: dict, total_s: float, out: Path) -> None:
    """Mix directly in NumPy (long ffmpeg filter chains cut the sound off in the template film)."""
    n = int(total_s * SR)
    voice, sfx, music = np.zeros((n, 2)), np.zeros((n, 2)), np.zeros((n, 2))
    prev_end, prev_name = 0.0, ""
    for seg in SEGMENTS:
        for key in ("voice", "voice2"):
            if seg.get(key):
                name, off = seg[key]
                name = SWAP.get(name, name)
                take = load_audio(VOICE / f"{name}.mp3", loudnorm=True)
                when = seg["t"] + off
                if when < prev_end:
                    raise SystemExit(f"Sätze überlappen: {name} beginnt {prev_end - when:.2f} s vor dem Ende von {prev_name}")
                place(voice, take, when)
                prev_end, prev_name = when + len(take) / SR, name
    title_hit = at["opener"] + 23.45 - OPENER_CUT
    # Cold open: rain and engine, then the opener's own synthesised sound
    rain = load_audio(SFX / "rain.mp3")
    bed_end = at["freeze"] + 1.0
    rl = int((bed_end - at["c_night"]) * SR)
    place(sfx, rain[:rl] * ramp(rl, [(0, 0), (.3, .4), (bed_end - at["c_night"] - 1, .4), (bed_end - at["c_night"], 0)])[:, None], at["c_night"])
    engine = load_audio(SFX / "engine.mp3")
    for name, gain, dur in (("c_night", .75, 1.3), ("c_combine", .9, 3.2)):
        el = int(dur * SR)
        place(sfx, engine[:el] * ramp(el, [(0, 0), (.1, gain), (dur - .4, gain), (dur, 0)])[:, None], at[name])
    place(sfx, load_audio(SFX / "scan.mp3"), at["freeze"], .7)
    op = load_audio(OPENER_AUDIO)[int(OPENER_CUT * SR):]
    place(sfx, op * ramp(len(op), [(0, 0), (.4, .7), (100, .7)])[:, None], at["opener"])
    # Impacts on the moments that carry the story
    boom = load_audio(SFX / "boom.mp3")
    place(sfx, boom, title_hit, 1.0)
    place(sfx, load_audio(SFX / "scan.mp3"), at["zoom"], .55)
    stamp = load_audio(SFX / "stamp.mp3")
    place(sfx, stamp, at["freezeoo"] + .55, .8)
    beats = json.loads((MGDIR / "data.js").read_text(encoding="utf-8")[len("const DATA = "):-1])["beats"]
    place(sfx, stamp, at["stamp"] + next(s for s in SEGMENTS if s["id"] == "stamp")["lead"] + beats["f03"]["s"][1] + .9, .8)     # same moment as in S.stamp
    scatter = next(s for s in SEGMENTS if s["id"] == "scatter")
    drop = at["scatter"] + scatter["lead"] + .9
    place(sfx, boom, drop + .28, .7)
    place(sfx, boom, drop + .68, .55)
    place(sfx, boom, at["big"] + .05, .9)
    place(sfx, stamp, at["big"] + next(s for s in SEGMENTS if s["id"] == "big")["lead"] + beats["f05"]["s"][1] + .4, .9)
    place(sfx, boom, at["end"] + .9, .75)
    # Music: cue 1 builds to the title impact, cue 2 carries the argument, cue 3 begins almost silent and peaks on the result.
    cue1, cue2, cue3 = (load_audio(SFX / f"music{i}.mp3") for i in (1, 2, 3))
    skip = 30.9 - title_hit                                # the strongest hit of cue 1 lands on the title
    c1 = cue1[int(skip * SR):]
    place(music, c1 * ramp(len(c1), [(0, .75), (title_hit + 2.6, .85), (title_hit + 3.5, .12), (title_hit + 6, 0), (1000, 0)])[:, None], 0)     # the voice starts 3.6 s after the hit
    start2 = title_hit + 3.0
    # Cue 2 fades out at the end of its 150 s, too early for the product part: from 142 s on a crossfade into its middle carries on.
    place(music, cue2 * ramp(len(cue2), [(0, 0), (3, .62), (142, .62), (145, 0), (1000, 0)])[:, None], start2)
    join = start2 + 142
    rest = at["black1"] - join
    c2b = cue2[int(70 * SR):int((70 + rest) * SR)]
    place(music, c2b * ramp(len(c2b), [(0, 0), (3, .62), (rest - 2, .62), (rest, 0)])[:, None], join)
    start3 = drop - 46.0                                    # cue 3 turns loud 46 s in: exactly when the blind points fall
    place(music, cue3 * ramp(len(cue3), [(0, .95), (60, .95), (62, .5), (72, .5), (78, 0), (1000, 0)])[:, None], start3)     # back down under the limits of the result
    end_m = at["g_rise"] - .5
    tail = cue2[int(20 * SR):int((20 + total_s - end_m) * SR)]
    place(music, tail * ramp(len(tail), [(0, 0), (1.5, .55), (total_s - end_m - 3, .55), (total_s - end_m - .3, 0)])[:, None], end_m)
    # Duck the music under the voice (fast attack, slow release): the voice stays understandable.
    active = (np.abs(voice).max(axis=1) > 0.01).astype(float)
    attack, release = np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.5 * SR))
    env = np.zeros(n)
    e = 0.0
    for i, v in enumerate(active):
        e = attack * e + (1 - attack) * v if v > e else release * e + (1 - release) * v
        env[i] = e
    bed = (sfx + music) * (1 - 0.82 * env)[:, None]
    mix = voice + bed
    # Nobody can listen here, so measure: over each sentence, how far is the voice above music and sound (only where it really speaks)?
    margins = []
    for seg in SEGMENTS:
        for key in ("voice", "voice2"):
            if seg.get(key):
                name, off = seg[key]
                i0 = int((seg["t"] + off) * SR)
                i1 = i0 + int(duration(VOICE / f"{SWAP.get(name, name)}.mp3") * SR)
                vals = []
                for w in range(i0, i1 - SR // 2, SR // 2):         # half-second windows: a short loud moment must not hide in the mean
                    on = active[w:w + SR // 2] > 0
                    if on.mean() < .4:
                        continue
                    rv = np.sqrt((voice[w:w + SR // 2][on] ** 2).mean())
                    rb = np.sqrt((bed[w:w + SR // 2][on] ** 2).mean()) + 1e-9
                    vals.append(20 * np.log10(rv / rb))
                margins.append((round(float(min(vals)), 1), round(float(np.median(vals)), 1), name))
    margins.sort()
    print("Stimme über Musik und Geräuschen je Zeile, (schlechtestes halbes Sekundenfenster, Median) in dB:", margins)
    peak = float(np.abs(mix).max())
    mix = mix * min(1.0, 0.84 / peak)                       # about -1.5 dB, headroom for AAC overshoot
    print(f"Mischung: Spitze vor Normierung {20 * np.log10(peak):.1f} dB, Faktor {min(1.0, .84 / peak):.3f}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "aac", "-b:a", "192k", str(out)], input=mix.astype(np.float32).tobytes(), check=True)


def plan() -> None:
    lead = {s.get("scene"): s["lead"] for s in SEGMENTS if s["kind"] == "mg"}
    lead["p_sat"] = 0.2
    lead["p_desc"] = 0.2 - 6.2
    MGDIR.mkdir(parents=True, exist_ok=True)
    (MGDIR / "timeline.js").write_text("const LEAD = " + json.dumps(lead) + ";", encoding="utf-8")
    scenes = [f"{s['scene']}:{s['dur']}" for s in SEGMENTS if s["kind"] == "mg"]
    plates = [f"{s['plate']}:{sum(c['dur'] for c in s['clips'])}" for s in SEGMENTS if s.get("plate")]
    variants = [f"{s['scene']}:{s['dur']}" for s in SEGMENTS if s.get("variant")]
    print("MAIN", ",".join(scenes + plates))
    print("VARIANT", ",".join(variants))
    total = sum((s["dur"] + s.get("hold", 0)) if s["kind"] != "film" else sum(c["dur"] for c in s["clips"]) for s in SEGMENTS)
    print("Gesamt", round(total, 2), "s =", f"{int(total // 60)}:{total % 60:04.1f}")


def main() -> None:
    if args.plan:
        plan()
        return
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    t, timeline, listing = 0.0, [], []
    for seg in SEGMENTS:
        out = BUILD_DIR / f"{seg['id']}.mp4"
        renderer = {"film": render_film, "app": render_app, "mg": render_mg, "black": render_black, "file": render_file}[seg["kind"]]
        if not args.audio_only:
            renderer(seg, out)
        real = duration(out)
        timeline.append({"id": seg["id"], "start": round(t, 3), "dur": round(real, 3)})
        listing.append(f"file '{out.as_posix()}'")
        seg["t"] = t
        t += real
    (BUILD_DIR / "concat.txt").write_text("\n".join(listing), encoding="utf-8")
    (BUILD_DIR / "timeline.json").write_text(json.dumps(timeline, indent=1), encoding="utf-8")
    picture = BUILD_DIR / "picture.mp4"
    if not args.audio_only:
        run(["-f", "concat", "-safe", "0", "-i", str(BUILD_DIR / "concat.txt"), *ENC, str(picture)])     # re-encode, so that picture and sound stay equally long
    total = duration(picture)
    audio = BUILD_DIR / "audio.m4a"
    mix_audio({s["id"]: s["t"] for s in SEGMENTS}, total, audio)
    name = ("DeltaGreen_Finale_1080p" if W >= 1920 else "DeltaGreen_Finale_Prototyp") + ("_ohne_Ortsnamen" if args.anon else "") + ".mp4"
    final = EXPORT / name
    run(["-i", str(picture), "-i", str(audio), "-c:v", "copy", "-c:a", "copy", "-t", f"{total:.3f}", "-movflags", "+faststart", str(final)])
    print("Film", final, round(duration(final), 2), "s", round(final.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
