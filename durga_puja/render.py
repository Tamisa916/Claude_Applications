"""Durga Puja: 50 years of celebration. Frame renderer (1920x1080, 30 fps) + ffmpeg mux.

usage: python render.py [--preview t1,t2] [--fresh] [--out file.mp4]
"""
import os
import math
import pickle
import argparse
import subprocess
from multiprocessing import Pool

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

from flat import hexc, mix, paper_texture
import scenes
from timing import W, H, FPS, TOTAL, boundaries

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("DP_CACHE", os.path.join(HERE, "build"))


# ----------------------------------------------------------------------------- text (EN + Bengali)
FONTS = {"serif": "PlayfairDisplay.ttf", "serif_i": "PlayfairDisplay-Italic.ttf", "sans": "LibreFranklin.ttf",
         "bn": "NotoSerifBengali.ttf"}
_fc = {}


def font(kind, size, wght=400):
    k = (kind, size, wght)
    if k not in _fc:
        f = ImageFont.truetype(os.path.join(HERE, "fonts", FONTS[kind]), size, layout_engine=ImageFont.Layout.RAQM)
        try:
            axes = f.get_variation_axes()
            f.set_variation_by_axes([wght] + [a["default"] for a in axes[1:]])
        except Exception:
            pass
        _fc[k] = f
    return _fc[k]


def text_sprite(s, f, col, tracking=0, pad=8):
    asc, desc = f.getmetrics()
    if tracking:
        w = sum(f.getlength(ch) + tracking for ch in s)
    else:
        w = f.getlength(s)
    img = Image.new("RGBA", (int(w + pad * 2 + 4), asc + desc + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c8 = tuple(int(c * 255) for c in col) + (255,)
    if tracking:
        x = pad
        for ch in s:
            d.text((x, pad), ch, font=f, fill=c8)
            x += f.getlength(ch) + tracking
    else:
        d.text((pad, pad), s, font=f, fill=c8)
    a = np.asarray(img).astype(np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    return a


# ----------------------------------------------------------------------------- frame
X = None
TEX = None


def build_all(fresh=False):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, "assets.pkl")
    if os.path.exists(p) and not fresh:
        with open(p, "rb") as fh:
            return pickle.load(fh)
    print("building assets ...", flush=True)
    A = scenes.build(text_sprite, font)
    with open(p, "wb") as fh:
        pickle.dump(A, fh, protocol=4)
    return A


def render_frame(fidx):
    t = fidx / FPS
    fr = scenes.draw(X, t)
    fr *= TEX[..., None]
    fade = min(1.0, t / 0.3, max(0.0, (TOTAL - t) / 0.6))
    fr *= fade
    return (np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8)


def init(fresh=False):
    global X, TEX
    X = build_all(fresh)
    TEX = paper_texture(W, H)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", default=None)
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "durga_puja_50_years.mp4"))
    ap.add_argument("--audio", default=os.path.join(HERE, "build", "score.wav"))
    args = ap.parse_args()
    init(args.fresh)
    if args.preview:
        outdir = os.environ.get("DP_PREVIEW", os.path.join(HERE, "build", "preview"))
        os.makedirs(outdir, exist_ok=True)
        for ts in args.preview.split(","):
            img = render_frame(int(float(ts) * FPS))
            cv2.imwrite(os.path.join(outdir, f"f_{float(ts):06.2f}.png"), img[..., ::-1])
        return
    n = int(TOTAL * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
           str(FPS), "-i", "-"]
    if os.path.exists(args.audio):
        cmd += ["-i", args.audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-b:v", "7000k", "-maxrate", "9000k", "-bufsize", "16000k",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", args.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for j, img in enumerate(pool.imap(render_frame, range(n), chunksize=4)):
            proc.stdin.write(img.tobytes())
            if j % 150 == 0:
                print(f"frame {j}/{n}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", args.out)


if __name__ == "__main__":
    main()
