"""Join new voice takes with sentences kept from the old takes, so that only the changed sentences cost ElevenLabs credits.

Reads export/voice/takes_v4/ (new takes n*.mp3, old takes <id>_alt.mp3) and writes export/voice/<id>.mp3.
Cuts lie in the pauses between sentences; each new take is brought to the loudness of the old one.
The audio stays out of the repository.
"""
import subprocess
from pathlib import Path

import numpy as np

import sys

VOICE = Path(__file__).resolve().parent.parent / "export" / "voice"
V6 = "--v6" in sys.argv
V5 = "--v5" in sys.argv or V6
TAKES = VOICE / ("takes_v6" if V6 else "takes_v5" if V5 else "takes_v4")
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
# v5 (2026-11-08): ElevenLabs had no credits left; the new takes are Higgsfield Seed Audio, cloned from c05+d01 of the old voice.
# v6 (same day): the Seed Audio takes did not sound like the film; same lines again via Higgsfield text2speech_v2 (ElevenLabs engine),
# voice element cloned from 67 s of the original ElevenLabs takes (d01, c05, e01, f01, d03). Same plan, no END cut.
# b01b loses its last sentence ("... der Durchschnitt."); f10/x10/f11 are new lines, f01 only serves as their loudness reference (<id>_alt.mp3).
if V5:
    PLAN = {
        "b01b": [(0.0, 7.40)],
        "c04": ["c04a", GAP, (4.52, None)],
        "c05": ["c05_new"],
        "f10": ["f10"],
        "x10": ["x10"],
        "f11": ["f11"],
    }
END = {"f11": 12.95} if V5 and not V6 else {}      # the f11 take ends in a click after a long pause


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
        if name in END:
            out = soft(out[:int(END[name] * SR)])
        peak = float(np.abs(out).max())
        if peak > .99:
            out = out * (.99 / peak)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "libmp3lame", "-q:a", "2", str(VOICE / f"{name}.mp3")],
                       input=out.astype(np.float32).tobytes(), check=True)
        print(f"{name}: {len(old) / SR:.2f} s -> {len(out) / SR:.2f} s, peak {peak:.2f}")


if __name__ == "__main__":
    main()
