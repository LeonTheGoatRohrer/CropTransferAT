"""Sound for scene 1, fully synthesised (no samples, no licences). The narration is recorded later and sits on top.

Usage:  python opener_audio.py     -> ../export/_opener_audio.wav (48 kHz stereo)
"""

from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR, DUR = 48000, 25.0
t = np.arange(int(SR * DUR)) / SR
rng = np.random.default_rng(42)


def env(a: float, b: float, fade_in: float, fade_out: float) -> np.ndarray:
    up = np.clip((t - a) / fade_in, 0, 1)
    down = np.clip((b - t) / fade_out, 0, 1)
    return (up * up * (3 - 2 * up)) * (down * down * (3 - 2 * down))


def band(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return sosfilt(butter(4, [lo, hi], btype="band", fs=SR, output="sos"), x)


def low(x: np.ndarray, f: float) -> np.ndarray:
    return sosfilt(butter(4, f, fs=SR, output="sos"), x)


def stereo(left: np.ndarray, right: np.ndarray | None = None) -> np.ndarray:
    return np.column_stack([left, left if right is None else right])


# combine engine: low harmonics with a slow wobble, a little rumble; rises as the track accelerates
speed = np.clip((t - 1) / 12, 0, 1) ** 2
f0 = 46 + 9 * speed + 0.35 * np.sin(2 * np.pi * 0.31 * t)
phase = 2 * np.pi * np.cumsum(f0) / SR
engine = sum(a * np.sin(k * phase + k) for k, a in [(1, 1.0), (2, 0.55), (3, 0.33), (4, 0.2), (6, 0.1)])
engine *= 1 + 0.12 * np.sin(2 * np.pi * 7.3 * t)
rumble = low(rng.normal(0, 1, len(t)), 170) * 1.6
air = band(rng.normal(0, 1, len(t)), 700, 2600) * 0.06 * (0.3 + speed)
machine = (0.2 * engine + 0.12 * rumble + air) * env(0.2, 14.4, 1.6, 1.5) * (0.65 + 0.35 * speed)

# satellite: a thin, cold pad and a sweep that follows the scan line
pad_f = [220.0, 329.63, 493.88, 659.25]
pad = sum(np.sin(2 * np.pi * f * t + i) * (0.6 + 0.4 * np.sin(2 * np.pi * (0.07 + i * 0.03) * t)) for i, f in enumerate(pad_f))
sat = 0.045 * pad * env(13.6, 20.2, 1.6, 1.8)
sweep_f = 500 + 3000 * np.clip((t - 14) / 4.4, 0, 1)
sweep = np.sin(2 * np.pi * np.cumsum(sweep_f) / SR) * 0.006 * env(14.0, 18.5, 0.3, 0.6)
ticks = np.zeros_like(t)
for when in rng.uniform(14.0, 18.5, 170):
    i = int(when * SR)
    n = int(0.018 * SR)
    ticks[i:i + n] += rng.choice([-1, 1]) * np.exp(-np.arange(n) / (0.004 * SR)) * np.sin(2 * np.pi * rng.uniform(1800, 4200) * np.arange(n) / SR)
ticks = 0.05 * ticks

# low impact when the weak zones appear, and a softer one under the logo
def hit(at: float, f: float, decay: float, gain: float) -> np.ndarray:
    x = np.clip(t - at, 0, None)
    return gain * np.sin(2 * np.pi * (f + 20 * np.exp(-x * 12)) * x) * np.exp(-x / decay) * (t >= at)

impact = hit(20.3, 38, 1.5, 0.62) + hit(23.45, 44, 1.2, 0.34)

# title chord
chord_f = [110.0, 164.81, 220.0, 277.18, 329.63]
chord = sum(np.sin(2 * np.pi * f * t + i * 0.7) for i, f in enumerate(chord_f))
title = 0.05 * low(chord, 900) * env(22.7, 25.0, 1.1, 1.2)

mix = stereo(machine + impact + title * 0.9) + stereo(sat + sweep + ticks * 0.8, np.roll(sat, 300) + sweep + ticks * 1.2)
mix = mix / np.abs(mix).max() * 0.56
out = Path(__file__).resolve().parent.parent / "export"
out.mkdir(parents=True, exist_ok=True)
wavfile.write(out / "_opener_audio.wav", SR, (mix * 32767).astype(np.int16))
print("written", out / "_opener_audio.wav")
