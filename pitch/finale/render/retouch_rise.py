"""Cut the stable end of the a14_rise clip and paint out the made-up lettering on the machine's rear.

The AI clip paints pseudo-letters on the green tailgate. Before START the machine still turns on
the spot, which is why only the end is used. Writes export/ai1080/a14_tail.mp4 and a copy in export/ai,
so both film widths find the clip. The result is an input of build_film.py and stays out of the repository.

After the first film build, export/mg/freeze1.png must be the last frame of build/w1920/o_rise.mp4, taken with
"scale=in_range=full:out_range=full" because the scene renderer writes RGB values straight into Y; then render the scene "freezescan" again.
"""
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter

EXPORT = Path(__file__).resolve().parent.parent / "export"
SRC, OUT = EXPORT / "ai1080" / "a14_rise.mp4", EXPORT / "ai1080" / "a14_tail.mp4"
START = 3.4     # seconds into the clip

# Lettering read off single frames: seconds in the clip, centre x, centre y, width (pixels at 1920x1080).
KEYS = np.array([
    (3.4, 955, 732, 110), (3.6, 951, 731, 100), (3.8, 955, 722, 90),
    (4.0, 969, 715, 84), (4.2, 980, 705, 76), (4.4, 987, 690, 70),
    (4.6, 989, 672, 64), (4.8, 990, 656, 58), (5.0, 988, 640, 52),
])


def paint_out(frame: np.ndarray, t: float) -> None:
    """Fill the lettering with the tailgate green just above it, with a feathered edge."""
    cx, cy, w = (np.interp(t, KEYS[:, 0], KEYS[:, i]) for i in (1, 2, 3))
    bw, bh = w * .62, w * .17
    x0, x1, y0, y1 = int(cx - bw) - 6, int(cx + bw) + 6, int(cy - bh) - 6, int(cy + bh) + 6
    above = frame[int(cy - bh) - int(2 * bh) - 2:int(cy - bh) - 2, int(cx - bw):int(cx + bw)]
    colour = np.median(above.reshape(-1, 3), axis=0)
    mask = np.zeros((y1 - y0, x1 - x0), np.float32)
    mask[6:-6, 6:-6] = 1
    mask = gaussian_filter(mask, 2.5)[..., None]
    frame[y0:y1, x0:x1] = (colour * mask + frame[y0:y1, x0:x1] * (1 - mask)).astype(np.uint8)


info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height,r_frame_rate", "-of", "json", str(SRC)],
                                 capture_output=True, text=True, check=True).stdout)["streams"][0]
W, H, rate = info["width"], info["height"], info["r_frame_rate"]
num, den = map(int, rate.split("/"))
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(START), "-i", str(SRC), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", rate, "-i", "-",
                        "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", str(OUT)], stdin=subprocess.PIPE)
n = 0
while raw := dec.stdout.read(W * H * 3):
    frame = np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy()
    paint_out(frame, START + n * den / num)
    enc.stdin.write(frame.tobytes())
    n += 1
enc.stdin.close()
enc.wait()
dec.wait()
shutil.copy(OUT, EXPORT / "ai" / OUT.name)
print(OUT, n, "frames")
