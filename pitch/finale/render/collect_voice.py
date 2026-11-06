"""Move the voice takes from the browser's download folder to ../export/voice/<id>.mp3 and check them.

ElevenLabs is driven by hand in the browser (no API key on this machine). The browser pane saves the files as <uuid>.tmp,
in the order of the clicks, so the order of voice_lines.tsv maps them to their line. Every take is checked: valid audio,
no duplicate, and a pace that fits its text (a wrong mapping shows up as an implausible number of characters per second).

Usage: python collect_voice.py --since "2026-11-06 14:22" [--apply]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "export" / "voice"
DOWNLOADS = Path.home() / "Downloads"


def probe(path: Path) -> tuple[str, float]:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name:format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.split()
    return (out[0], float(out[-1])) if len(out) >= 2 else ("?", 0.0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    since = dt.datetime.fromisoformat(a.since).timestamp()
    with open(HERE / "voice_lines.tsv", encoding="utf-8", newline="") as f:
        lines = list(csv.DictReader(f, delimiter="\t"))
    files = sorted((p for p in DOWNLOADS.iterdir() if p.is_file() and p.stat().st_mtime >= since and p.suffix in (".tmp", ".mp3")), key=lambda p: p.stat().st_mtime)
    print(f"{len(files)} files, {len(lines)} lines")
    seen: dict[str, str] = {}
    for line, path in zip(lines, files):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:10]
        codec, dur = probe(path)
        pace = len(line["text"]) / dur if dur else 0
        flag = ""
        if digest in seen:
            flag += f" DUPLICATE of {seen[digest]}"
        if codec != "mp3" or not 10 <= pace <= 21:
            flag += " CHECK"
        seen[digest] = line["id"]
        print(f"{line['id']}  {dur:6.2f} s  {len(line['text']):4d} Z  {pace:5.1f} Z/s  {codec} {digest}{flag}")
        if a.apply and not flag:
            OUT.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), OUT / f"{line['id']}.mp3")


if __name__ == "__main__":
    main()
