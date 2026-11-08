"""Assemble the Delta Green finale film: AI mood clips, motion graphics from real data, the opener, app recording, voice, music, SFX.

The voice sets the timing: every segment is as long as its measured voice line plus LEAD and TAIL. The voice is never sped up.

Usage:  python build_film.py --plan             write ../export/mg/timeline.js and print the render list for render_mg.mjs
        python build_film.py [--width 960]      build the film (--width 1920 also needs the clips in ../export/ai1080)
        python build_film.py --anon             variant with aggregated values and without place names
        python build_film.py --audio-only       keep the picture, only remix the sound
        python build_film.py --opening          only the opening up to the title, for review
Output: ../export/DeltaGreen_{Anfang,Finale_v6}_{540p,1080p}[_ohne_Ortsnamen].mp4 (not in the repository).
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
OPENER_CUT = 5.55       # seconds into the opener where the film cuts in; the same value is used by export_data.py
FPS, SR = 25, 48000
AI_LABEL = "KI-generierte Illustration"

ap = argparse.ArgumentParser()
ap.add_argument("--width", type=int, default=960)
ap.add_argument("--plan", action="store_true")
ap.add_argument("--anon", action="store_true")
ap.add_argument("--audio-only", action="store_true")
ap.add_argument("--opening", action="store_true", help="build only the opening up to the title, for review")
args = ap.parse_args()
W, H = args.width, args.width * 9 // 16
if W >= 1920:
    AI = EXPORT / "ai1080"      # the mood clips in high resolution; same frames and length as the drafts, so all cuts stay
SUF = "_anon" if args.anon else ""
SWAP = {"f01": "x01", "f02": "x02", "f10": "x10"} if args.anon else {}
BUILD_DIR = BUILD / f"w{W}{SUF}"


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout
    return float(out)


def vd(name: str) -> float:
    return duration(VOICE / f"{SWAP.get(name, name)}.mp3")


def run(cmd: list[str]) -> None:
    subprocess.run(["ffmpeg", "-y", "-v", "error", *cmd], check=True)


SLOWMO = f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,setsar=1"      # new in-between frames, so slow motion does not stutter


def clip(name, start=0.0, dur=3.0, speed=1.0, vf=""):
    return {"file": AI / f"{name}.mp4", "start": start, "dur": dur, "speed": speed, "vf": vf}


def mg(sid, scene, voice=None, lead=0.3, tail=0.6, dur=None, variant=False):
    d = dur if dur is not None else lead + vd(voice) + tail     # a voice line may run on into the next segment when dur is given
    return {"id": sid, "kind": "mg", "scene": scene, "dur": round(d, 2), "voice": (voice, lead) if voice else None, "lead": lead, "variant": variant}


def segments() -> list[dict]:
    c01 = vd("c01")
    return [
        # 1 opening, 30 s: what is the problem, what is already there, what the product is meant to do; then the title.
        # Cuts sit on the three hits of the music (6.2, 18.2, 30.2 s) and on the words of the voice.
        {"id": "black0", "kind": "black", "dur": 0.15},
        {"id": "o_rows", "kind": "film", "clips": [clip("a06_rows", 0.8, 2.85)], "bars": True, "voice": ("o1", 0.15)},
        {"id": "o_drone", "kind": "film", "clips": [clip("a13_drone", 0.6, 3.2)], "bars": True, "voice": ("o2", 0.05)},
        {"id": "o_heat", "kind": "film", "clips": [clip("a07_heat", 1.0, 1.06)], "bars": True, "plate": "p_duerre", "voice": ("o3", 0.0)},
        {"id": "o_leaf", "kind": "film", "clips": [clip("a07_heat", 3.0, 1.07, vf="crop=959:540:560:120")], "bars": True, "plate": "p_befall"},
        {"id": "o_storm", "kind": "film", "clips": [clip("a09_storm", 1.5, 0.87)], "bars": True, "plate": "p_unwetter"},
        {"id": "o_night", "kind": "film", "clips": [clip("a08_night", 3.0, 1.2)], "bars": True, "voice": ("o4", 0.1)},
        {"id": "o_grain", "kind": "film", "clips": [clip("a11_grain", 1.0, 1.2)], "bars": True},
        # The AI flight over the combine (a14_rise) is out (feedback 2026-11-08: too weak); the scan line runs over black into the real track.
        mg("o_scan", "freezescan", "o9", lead=0.1, dur=1.5),
        # The real track, now slow enough to follow and explained in the picture.
        {"id": "o_tracks", "kind": "file", "file": OPENER, "start": OPENER_CUT, "dur": 5.0, "speed": 1.5, "plate": "p_tracks"},
        {"id": "o_sat", "kind": "film", "clips": [clip("a12_sat", 0.0, 3.0)], "voice": ("o5", 0.1)},
        {"id": "o_pixels", "kind": "file", "file": OPENER, "start": 14.2, "dur": 2.85, "speed": 1.6, "voice": ("o6", 0.05)},
        {"id": "o_split", "kind": "file", "file": OPENER, "start": 20.0, "dur": 2.0, "speed": 1.25, "voice": ("o7", 0.2)},
        mg("phone", "phone", "o8", lead=0.15, tail=0.1),
        mg("titlecard", "titlecard", "b01a", lead=0.4, tail=0.6),
        # 2 problem
        mg("spread", "spread", "b01b"),
        mg("nomap", "nomap", "b02"),
        # 3 solution: the satellite was just introduced in the opening, so this starts at "Zehn Meter pro Pixel"; the scan into real pixels falls on "Sein Bild zeigt ..."
        {"id": "c_desc", "kind": "film", "clips": [clip("a05_descent", 3.9, 3.1)], "plate": "p_desc", "voice": ("c01c", 0.1)},
        {"id": "zoom", "kind": "mg", "scene": "zoom", "dur": round(0.2 + c01 + 0.7 - 9.3, 2), "voice": None, "lead": -9.1},
        mg("wall", "wall", "c02", tail=0.7),
        mg("tiles", "tiles", "c04", tail=0.7),
        mg("failed", "failed", "c05", tail=0.8),
        # 4 data
        mg("sources", "sources", "d01", lead=0.5, tail=0.7),
        mg("zero", "zero", "d02", tail=0.7),
        mg("freezeoo", "freezeoo", "d03", tail=1.0),
        mg("stmk", "stmk", "d04", tail=1.0),
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
        # 6 after the hand-in, kept short (feedback 2026-11-08): what arrived, then only how far the result rose
        {"id": "black1", "kind": "black", "dur": 0.7},
        mg("mail", "mail", "f10", lead=0.5, tail=1.0, variant=True),
        mg("big", "big", "f11", lead=0.4, tail=1.4),
        # 7 end
        # pull back from the field up to the orbit
        {"id": "g_rise", "kind": "film", "clips": [clip("a10_rise", 1.5, 5.6), clip("a12_sat", 3.0, 3.0)], "voice": ("g01", 0.4)},
        mg("end", "end", dur=6.4),
    ]


SEGMENTS = segments()
if args.opening:
    SEGMENTS = SEGMENTS[:[s["id"] for s in SEGMENTS].index("titlecard") + 1]
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
        chains.append(f"[{i}:v]setpts=PTS/{c['speed']},{c['vf'] + ',' if c['vf'] else ''}{GRADE}[c{i}]")
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
    """A slow virtual camera inside the recording, computed per frame with subpixel precision.

    ffmpeg's zoompan rounds the crop to whole pixels, which made the picture jump back and forth by a pixel per frame.
    """
    z0, z1 = np.array(seg["z0"], float), np.array(seg["z1"], float)     # x, y, w, h in the 1920x1080 space of the page
    d = seg["dur"]
    n = round(d * FPS)
    SW, SH = 3840, 2160
    source = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(seg["start"]), "-i", str(seg["file"]),
                               "-vf", f"fps={FPS},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={d},scale={SW}:{SH}:flags=lanczos,format=rgb24",
                               "-frames:v", str(n), "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    inputs, graph, maps = ["-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"], [], ["-map", "0:v"]
    if seg.get("caption"):
        inputs += ["-i", str(caption_png(seg["id"], *seg["caption"]))]
        graph, maps = ["-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[o]"], ["-map", "[o]"]
    sink = subprocess.Popen(["ffmpeg", "-y", "-v", "error", *inputs, *graph, *maps, "-t", str(d), *ENC, str(out)], stdin=subprocess.PIPE)
    size = SW * SH * 3
    for i in range(n):
        data = source.stdout.read(size)
        if len(data) < size:
            break
        k = min(i / n, 1.0)
        x, y, w, h = z0 + (z1 - z0) * (k * k * (3 - 2 * k))
        frame = Image.frombuffer("RGB", (SW, SH), data, "raw", "RGB", 0, 1)
        sx, sy = SW / 1920, SH / 1080
        view = frame.transform((W, H), Image.Transform.AFFINE, (w * sx / W, 0, x * sx, 0, h * sy / H, y * sy), Image.Resampling.BICUBIC)
        sink.stdin.write(view.tobytes())
    source.stdout.close()
    source.wait()
    sink.stdin.close()
    if sink.wait() != 0:
        raise RuntimeError(f"encoding {seg['id']} failed")


def render_mg(seg: dict, out: Path) -> None:
    suffix = SUF if seg.get("variant") else ""
    run(["-i", str(MG / f"{seg['scene']}{suffix}.mp4"), "-vf", f"scale={W}:{H}:flags=lanczos,noise=alls=2:allf=t,format=yuv420p", "-t", str(seg["dur"]), *ENC, str(out)])


def render_file(seg: dict, out: Path) -> None:
    speed = seg.get("speed", 1.0)                               # the opener's real data, shortened for the 30 s opening
    base = f"setpts=PTS/{speed},scale={W}:{H}:flags=lanczos,fps={FPS},noise=alls=2:allf=t,format=gbrp"
    inputs = ["-ss", str(seg["start"]), "-t", f"{seg['dur'] * speed:.3f}", "-i", str(seg["file"])]
    if seg.get("plate"):
        inputs += ["-i", str(MG / f"{seg['plate']}.mp4")]
        graph = f"[0:v]{base}[b];[1:v]scale={W}:{H},fps={FPS},format=gbrp[p];[b][p]blend=all_mode=screen:shortest=1,format=yuv420p[o]"
    else:
        graph = f"[0:v]{base},format=yuv420p[o]"
    run([*inputs, "-filter_complex", graph, "-map", "[o]", "-t", str(seg["dur"]), *ENC, str(out)])


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
    title_hit = at["titlecard"]
    phone = at["phone"]
    beats = json.loads((MGDIR / "data.js").read_text(encoding="utf-8")[len("const DATA = "):-1])["beats"]
    # Opening: the field, the storm, the machine, the scans, the phone
    boom, scan = load_audio(SFX / "boom.mp3"), load_audio(SFX / "scan.mp3")
    rain = load_audio(SFX / "rain.mp3")
    rl = int(1.6 * SR)
    place(sfx, rain[:rl] * ramp(rl, [(0, .6), (1.0, .6), (1.6, 0)])[:, None], at["o_storm"])
    engine = load_audio(SFX / "engine.mp3")
    for name, gain, dur in (("o_night", .5, 2.4), ("o_scan", .6, 6.5)):     # the engine stays under the real track
        el = int(dur * SR)
        take = np.tile(engine, (el // len(engine) + 1, 1))[:el]
        place(sfx, take * ramp(el, [(0, 0), (.2, gain), (dur - .6, gain), (dur, 0)])[:, None], at[name])
    place(sfx, scan, at["o_scan"], .8)
    place(sfx, scan, at["o_pixels"], .3)
    place(sfx, boom, at["o_heat"], .3)
    # While the real track is drawn: a dense crackle of short ticks, one per yield point, as in the opener (opener_audio.py).
    rt, tl = np.random.default_rng(42), int(.018 * SR)
    tk = np.zeros((int(5.0 * SR), 2))
    for when in rt.uniform(.2, 4.6, 190):
        i, f = int(when * SR), rt.uniform(1800, 4200)
        tk[i:i + tl] += (rt.choice([-1, 1]) * np.exp(-np.arange(tl) / (.004 * SR)) * np.sin(2 * np.pi * f * np.arange(tl) / SR))[:, None]
    place(sfx, tk, at["o_tracks"], .35)
    place(sfx, boom, at["o_pixels"], .2)
    place(sfx, boom, title_hit, 1.0)
    tn = np.arange(int(.09 * SR)) / SR
    tick = np.sin(2 * np.pi * 2300 * tn) * np.exp(-tn * 70)
    for i in range(6):                                      # one tap per corner of the parcel, same times as S.phone
        place(sfx, np.column_stack([tick, tick]), phone + 1.25 + i * .24, .22)
    message = phone + next(s for s in SEGMENTS if s["id"] == "phone")["lead"] + beats["o8"]["s"][1] + 1.15     # same moment as in S.phone
    place(sfx, scan, message - 1.0, .35)
    tp = np.arange(int(.5 * SR)) / SR
    ping = (np.sin(2 * np.pi * 1320 * tp) * np.exp(-tp * 9) * (tp < .12) + np.sin(2 * np.pi * 1760 * tp) * np.exp(-(tp - .12).clip(0) * 7) * (tp >= .12))
    place(sfx, np.column_stack([ping, ping]), message, .3)
    tb = np.arange(int(.55 * SR)) / SR
    bz = np.sign(np.sin(2 * np.pi * 165 * tb)) * .5 * (np.sin(2 * np.pi * 7 * tb) > -.3) * np.exp(-tb * 1.5)
    place(sfx, np.column_stack([bz, bz]), message, .22)
    # Music: the new cue builds to the title, its biggest hit (36.0 s in the file) lands exactly on the name.
    cue1 = load_audio(SFX / "music1b.mp3")
    # The opening is longer than the cue's 36 s: its sections repeat every 12 s, so the first seconds come from the end of the first section.
    lead_in = title_hit - 36.0
    c1 = np.concatenate([cue1[int((12.0 - lead_in) * SR):int(12.0 * SR)], cue1]) if lead_in > 0 else cue1[int(-lead_in * SR):]
    fall = title_hit + 3.6                                  # the title's voice ends about here; cue 2 takes over
    first_hit = title_hit - 36.0                            # falls into the very first sentence: taken back, the voice comes first
    dip = [(first_hit - .15, 1.0), (first_hit, .3), (first_hit + 1.0, .3), (first_hit + 1.6, 1.0)] if first_hit > .5 else []
    place(music, c1 * ramp(len(c1), [(0, 0), (.3, 1.0), *dip, (fall - 1.2, 1.0), (fall, .2), (fall + 2.4, 0), (1000, 0)])[:, None], 0)
    if "end" in at:
        place(sfx, scan, at["zoom"], .55)
        stamp = load_audio(SFX / "stamp.mp3")
        place(sfx, stamp, at["freezeoo"] + .55, .8)
        big = at["big"] + next(s for s in SEGMENTS if s["id"] == "big")["lead"]
        drop = big + beats["f11"]["s"][1] + 5.9                # the 0,77 appears, same moment as in S.big
        place(sfx, boom, big + beats["f11"]["s"][1] + 4.2, .5)
        place(sfx, boom, drop, .9)
        place(sfx, stamp, big + beats["f11"]["s"][2] + .6, .9)
        place(sfx, boom, at["end"] + .9, .75)
        mix_rest(at, total_s, music, title_hit, drop)
    finish_mix(voice, sfx, music, n, title_hit, total_s, out)


def mix_rest(at: dict, total_s: float, music: np.ndarray, title_hit: float, drop: float) -> None:
    """Music after the title: cue 2 carries the argument, cue 3 begins almost silent and peaks on the result."""
    cue2, cue3 = load_audio(SFX / "music2.mp3"), load_audio(SFX / "music3.mp3")
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


def finish_mix(voice: np.ndarray, sfx: np.ndarray, music: np.ndarray, n: int, title_hit: float, total_s: float, out: Path) -> None:
    # Duck the music under the voice (fast attack, slow release): the voice stays understandable.
    active = (np.abs(voice).max(axis=1) > 0.01).astype(float)
    attack, release = np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.5 * SR))
    env = np.zeros(n)
    e = 0.0
    for i, v in enumerate(active):
        e = attack * e + (1 - attack) * v if v > e else release * e + (1 - release) * v
        env[i] = e
    depth = ramp(n, [(0, .78), (title_hit, .78), (title_hit + .3, .8), (title_hit + 4, .82), (total_s + 1, .82)])
    bed = (sfx + music) * (1 - depth * env)[:, None]
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
    plates = [f"{s['plate']}:{sum(c['dur'] for c in s['clips']) if s['kind'] == 'film' else s['dur']}" for s in SEGMENTS if s.get("plate")]
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
    name = ("DeltaGreen_Anfang" if args.opening else "DeltaGreen_Finale_v6") + ("_1080p" if W >= 1920 else "_540p") + ("_ohne_Ortsnamen" if args.anon else "") + ".mp4"
    final = EXPORT / name
    run(["-i", str(picture), "-i", str(audio), "-c:v", "copy", "-c:a", "copy", "-t", f"{total:.3f}", "-movflags", "+faststart", str(final)])
    print("Film", final, round(duration(final), 2), "s", round(final.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
