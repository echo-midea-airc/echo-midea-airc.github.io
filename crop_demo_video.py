"""Crop images/demo.mp4: top 70, bottom 35, left 83, right 130 (1280x720 source).

Writes H.264 + yuv420p (browser / Windows player friendly). OpenCV alone emits mp4v,
which many desktop players cannot open.
"""

import subprocess

import cv2
import imageio_ffmpeg
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "images" / "demo.mp4"
DST = ROOT / "images" / "demo_cropped.mp4"
TMP = ROOT / "images" / ".demo_cropped_tmp.mp4"

# Margins (pixels kept inside these insets). LEFT includes extra 50px trim vs first crop.
LEFT, TOP, RIGHT, BOTTOM = 143, 70, 130, 35


def main() -> None:
    cap = cv2.VideoCapture(str(SRC))
    if not cap.isOpened():
        raise SystemExit(f"Cannot open: {SRC}")

    iw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    ih = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or fps > 120:
        fps = 30.0

    x, y = LEFT, TOP
    w = iw - LEFT - RIGHT
    h = ih - TOP - BOTTOM
    if w <= 0 or h <= 0 or x < 0 or y < 0:
        raise SystemExit(f"Invalid crop for {iw}x{ih}: x={x} y={y} w={w} h={h}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(TMP), fourcc, fps, (w, h))
    if not out.isOpened():
        raise SystemExit(f"Cannot open writer: {TMP}")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            crop = frame[y : y + h, x : x + w]
            out.write(crop)
    finally:
        cap.release()
        out.release()

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(TMP),
            "-c:v",
            "libx264",
            "-crf",
            "20",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            str(DST),
        ],
        check=True,
    )
    TMP.unlink(missing_ok=True)

    print(f"Wrote {DST} ({w}x{h} @ {fps} fps, H.264)")


if __name__ == "__main__":
    main()
