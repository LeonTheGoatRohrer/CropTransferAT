"""Acceptance checks for a rendered film: length, picture and sound equally long, true peak, overlapping sentences, contact sheets.

Usage: python check_film.py ../export/DeltaGreen_Finale_Prototyp.mp4 [--step 5]
Writes contact sheets (one frame every --step seconds, with the time burnt in) next to the build folder.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path


def probe(path: Path, stream: str) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries", "stream=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("film", type=Path)
    ap.add_argument("--step", type=int, default=5)
    a = ap.parse_args()
    v, s = probe(a.film, "v:0"), probe(a.film, "a:0")
    print(f"Bild {v:.2f} s, Ton {s:.2f} s, Differenz {abs(v - s) * 1000:.0f} ms, Länge {int(v // 60)}:{v % 60:05.2f}")
    log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(a.film), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    summary = log[log.rfind("Summary:"):]
    print(" ".join(summary.split()))
    peak = float(re.search(r"Peak:\s*(-?[\d.]+) dBFS", summary).group(1))
    print("Abnahme:", "Spitze OK" if peak < -1 else f"SPITZE ZU HOCH {peak}", "|", "Länge OK" if 290 <= v <= 298 else "LÄNGE PRÜFEN", "|", "Gleich lang OK" if abs(v - s) < .05 else "UNGLEICH LANG")
    out = a.film.parent / "sheets" / a.film.stem
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    per = 6 * 6                                                 # 36 frames per sheet = 3 minutes at 5 s
    draw = "drawtext=text='%{pts\\:gmtime\\:0\\:%M\\\\\\:%S}':x=8:y=8:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6:fontfile='C\\:/Windows/Fonts/consola.ttf'"
    # select exact frames: the fps filter would pick a frame half a step away from the time it is labelled with
    pick = f"select='not(mod(n\\,{a.step * 25}))'"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(a.film), "-vf", f"{pick},scale=480:-1,{draw},tile=6x6:padding=2", "-fps_mode", "vfr", "-q:v", "4", str(out / "s%02d.jpg")], check=True)
    n = math.ceil(v / a.step / per)
    print(f"{n} Kontaktbögen in {out}")
    timeline = a.film.parent / "build" / ("w960_anon" if "ohne" in a.film.stem else "w960") / "timeline.json"
    if timeline.exists():
        print(" ".join(f"{e['id']}={int(e['start'] // 60)}:{e['start'] % 60:04.1f}" for e in json.loads(timeline.read_text(encoding='utf-8'))))


if __name__ == "__main__":
    main()
