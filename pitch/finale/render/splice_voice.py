"""Join new voice takes with sentences kept from the old takes, so that only the changed sentences cost ElevenLabs credits.

Reads export/voice/takes_v4/ (new takes n*.mp3, old takes <id>_alt.mp3) and writes export/voice/<id>.mp3.
Cuts lie in the pauses between sentences; each new take is brought to the loudness of the old one.
The audio stays out of the repository.
"""
import subprocess
from pathlib import Path

import numpy as np

VOICE = Path(__file__).resolve().parent.parent / "export" / "voice"
TAKES = VOICE / "takes_v4"
SR = 44100
GAP = 0.45      # pause between sentences, as in the old takes

# A number pair is a stretch of the old take in seconds (end None = to the end), a string a new take.
PLAN = {
    "c02": [(0.0, 10.09), "n1", GAP, (13.28, None)],
    "c03": ["n2", GAP, (6.81, None)],
    "c04": ["n4", GAP, (3.39, None)],
    "d03": [(0.0, 3.63), "n5"],
    "f04": ["n6", GAP, (6.11, None)],
    "f06": ["n7", GAP, (9.76, None)],
}


def load(path: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def trim(x: np.ndarray) -> np.ndarray:
    """Remove the silence around a new take, keeping 20 ms."""
    loud = np.flatnonzero(np.abs(x) > 0.01)
    margin = int(.02 * SR)
    return x[max(loud[0] - margin, 0):loud[-1] + margin]


def voiced_rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x[np.abs(x) > 0.02] ** 2)))


def soft(x: np.ndarray) -> np.ndarray:
    """A 10 ms fade at both ends, so that the joints do not click."""
    n = min(int(.01 * SR), len(x) // 2)
    x = x.copy()
    x[:n] *= np.linspace(0, 1, n)
    x[-n:] *= np.linspace(1, 0, n)
    return x


def main() -> None:
    for name, parts in PLAN.items():
        old = load(TAKES / f"{name}_alt.mp3")
        target, pieces = voiced_rms(old), []
        for p in parts:
            if isinstance(p, float):
                pieces.append(np.zeros(int(p * SR), dtype=np.float32))
            elif isinstance(p, str):
                new = trim(load(TAKES / f"{p}.mp3"))
                pieces.append(soft(new * (target / voiced_rms(new))))
            else:
                a, b = p
                pieces.append(soft(old[int(a * SR):None if b is None else int(b * SR)]))
        out = np.concatenate(pieces)
        peak = float(np.abs(out).max())
        if peak > .99:
            out = out * (.99 / peak)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "libmp3lame", "-q:a", "2", str(VOICE / f"{name}.mp3")],
                       input=out.astype(np.float32).tobytes(), check=True)
        print(f"{name}: {len(old) / SR:.2f} s -> {len(out) / SR:.2f} s, peak {peak:.2f}")


if __name__ == "__main__":
    main()
