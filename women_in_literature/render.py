"""Render the video frames (1080x1920, 30 fps) and mux with the generated score.

usage: python render.py [--preview t1,t2,...] [--out file.mp4]
"""
import os
import sys
import math
import pickle
import argparse
import subprocess
from multiprocessing import Pool

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

from paint import hexc, mix, canvas_texture, Layer
from portraits import draw_portrait, PW, PH
from content import DECADES, INTRO_PORTRAIT, OUTRO_LINES
import assets as A
from timing import (W, H, FPS, BEAT, INTRO, DEC, OUTRO, TOTAL, T_OUT, TR, N_DEC, CARD_IN, NAME_IN, WHO_IN,
                    TYPE_IN, TYPE_DUR, LINE_IN, LINE_DUR, boundaries)

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("WIL_CACHE", os.path.join(HERE, "build"))
INK = hexc("#2a1612")
CREAM = hexc("#fbf0dc")
RED = hexc("#b23a2a")
HL = ["#f3c14f", "#f6c76a", "#f2a29a", "#f2a06a", "#f08a7a", "#f6b08f", "#f3a04e", "#f2c14e", "#f2878a", "#f7c2a0"]
INTRO_BG = "#e8c23a"
OUTRO_BG = "#f0cf8e"


# =========================================================================== helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, start, dur):
    return clamp((t - start) / dur)


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_io(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_back(x, s=1.70158):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    c3 = s + 1
    return 1 + c3 * (x - 1) ** 3 + s * (x - 1) ** 2


def blit(dst, spr, x, y, scale=1.0, rot=0.0, alpha=1.0, anchor=(0.5, 0.5), clip=None):
    """Composite a premultiplied RGBA sprite onto an RGB frame."""
    if alpha <= 0.003 or scale <= 0.002:
        return
    h, w = spr.shape[:2]
    ax, ay = anchor[0] * w, anchor[1] * h
    r = math.radians(rot)
    c, s = math.cos(r) * scale, math.sin(r) * scale
    xs = [c * (u - ax) - s * (v - ay) + x for u, v in ((0, 0), (w, 0), (0, h), (w, h))]
    ys = [s * (u - ax) + c * (v - ay) + y for u, v in ((0, 0), (w, 0), (0, h), (w, h))]
    cx0, cy0, cx1, cy1 = clip if clip else (0, 0, dst.shape[1], dst.shape[0])
    x0, x1 = max(int(math.floor(min(xs))), cx0), min(int(math.ceil(max(xs))), cx1)
    y0, y1 = max(int(math.floor(min(ys))), cy0), min(int(math.ceil(max(ys))), cy1)
    if x1 <= x0 or y1 <= y0:
        return
    M = np.array([[c, -s, x - c * ax + s * ay - x0], [s, c, y - s * ax - c * ay - y0]], np.float32)
    patch = cv2.warpAffine(spr, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                           borderValue=(0, 0, 0, 0))
    a = patch[..., 3:4] * alpha
    reg = dst[y0:y1, x0:x1]
    reg *= (1 - a)
    reg += patch[..., :3] * alpha


# --------------------------------------------------------------------------- text
FONTS = {"serif": "PlayfairDisplay.ttf", "serif_i": "PlayfairDisplay-Italic.ttf", "sans": "LibreFranklin.ttf",
         "hand": "Caveat.ttf"}
_fc = {}


def font(kind, size, wght=400):
    k = (kind, size, wght)
    if k not in _fc:
        f = ImageFont.truetype(os.path.join(HERE, "fonts", FONTS[kind]), size)
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
        _fc[k] = f
    return _fc[k]


class Text:
    """Pre-rendered text sprite with per-character offsets (for typewriter reveals)."""

    def __init__(self, s, f, col, tracking=0, pad=10):
        self.s, self.f, self.tr, self.pad = s, f, tracking, pad
        asc, desc = f.getmetrics()
        self.offs = [pad]
        x = pad
        for ch in s:
            x += f.getlength(ch) + tracking
            self.offs.append(x)
        if not tracking:
            self.offs = [pad + f.getlength(s[:i]) for i in range(len(s) + 1)]
        wpx = int(self.offs[-1] + pad + 4)
        hpx = asc + desc + pad * 2
        img = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        col8 = tuple(int(c * 255) for c in col) + (255,)
        if tracking:
            for i, ch in enumerate(s):
                d.text((self.offs[i], pad), ch, font=f, fill=col8)
        else:
            d.text((pad, pad), s, font=f, fill=col8)
        a = np.asarray(img).astype(np.float32) / 255.0
        a[..., :3] *= a[..., 3:4]
        self.spr = a
        self.w = self.offs[-1] - pad
        self.h = hpx
        self.asc = asc

    def draw(self, dst, x, y, alpha=1.0, upto=None, frac=None, scale=1.0, rot=0.0, anchor=(0, 0)):
        spr = self.spr
        if upto is not None:
            n = max(0, min(len(self.s), int(upto)))
            cut = int(self.offs[n]) + 2
            if n == 0:
                return
            spr = spr[:, :cut]
        if frac is not None:
            if frac <= 0:
                return
            cut = int(self.pad + (self.w + 6) * frac)
            spr = spr[:, :max(1, cut)]
        sx = x - self.pad * scale
        sy = y - self.pad * scale
        blit(dst, spr, sx + anchor[0] * spr.shape[1] * scale * 0, sy, scale=scale, rot=rot, alpha=alpha,
             anchor=(0, 0))


def wrap(s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if f.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def fit_font(s, kind, size, wght, maxw):
    while size > 30 and font(kind, size, wght).getlength(s) > maxw:
        size -= 4
    return font(kind, size, wght)


# =========================================================================== assets
def _portrait_job(spec):
    return draw_portrait(spec)


def build_assets():
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "assets.pkl")
    if os.path.exists(path):
        with open(path, "rb") as fh:
            return pickle.load(fh)
    print("building assets ...", flush=True)
    specs = [INTRO_PORTRAIT] + [d["portrait"] for d in DECADES]
    bg_jobs = [(INTRO_BG, 900, None)] + [(d["bg"], 1000 + i * 10,
                                          {"noir": "spot", "wallpaper": "wallpaper", "diary": "paper"}.get(d["props"]))
                                         for i, d in enumerate(DECADES)] + [(OUTRO_BG, 2000, None)]
    with Pool(4) as pool:
        ports = pool.map(_portrait_job, specs)
        bgs = pool.starmap(A.build_bg, bg_jobs)
        fl_jobs = [("peony_pink", 1, 170), ("peony_white", 2, 170), ("rose_red", 3, 150), ("peony_pink", 4, 120),
                   ("hibiscus", 5, 150), ("blossom_white", 6, 50), ("blossom_pink", 7, 50), ("leaf", 8, 110),
                   ("rose_red", 9, 120), ("peony_white", 10, 130)]
        flowers = pool.starmap(A.build_flower, fl_jobs)
    X = {"ports": ports, "bgs": bgs}
    X["fl"] = dict(zip(["pink", "white", "red", "pink_s", "hibiscus", "bl_w", "bl_p", "leaf", "red_s", "white_s"],
                       flowers))
    X["cameo"] = A.build_cameo(ports[1])
    X["sun"] = A.build_sun()
    X["field"] = A.build_field()
    X["wheat"] = [A.build_wheat(30 + i) for i in range(3)]
    X["sunburst"] = A.build_sunburst(DECADES[2]["bg"])
    X["bubble"] = A.build_bubble()
    X["green"] = A.build_glow("#86d48a", 26)
    X["ember"] = A.build_glow("#ffd27a", 6)
    X["branchL"] = A.build_blossom_branch(-1, 40, X["fl"]["bl_w"], X["fl"]["bl_p"])
    X["branchR"] = A.build_blossom_branch(1, 41, X["fl"]["bl_w"], X["fl"]["bl_p"])
    X["petal"] = A.build_petal()
    X["house"] = A.build_house_picture()
    X["clock"] = A.build_clock()
    X["hand_h"] = A.build_hand(46, 8)
    X["hand_m"] = A.build_hand(66, 5)
    X["arcs"] = A.build_arcs()
    X["plane"] = A.build_plane()
    X["handmaid"] = A.build_handmaid()
    X["card"], X["card_pad"] = A.build_card(940, 600)
    X["hl"] = []
    X["polaroids"] = []
    for i, d in enumerate(DECADES):
        f = fit_font(d["arche"], "sans", 92, 900, 820)
        X["hl"].append(A.build_highlight(int(f.getlength(d["arche"])) + 34, 64, HL[i], seed=60 + i))
        X["polaroids"].append(build_polaroid(ports[i + 1], d["bg"], i))
    X["hl_title"] = A.build_highlight(640, 70, "#f08a6a", seed=90)
    X["hl_pen"] = A.build_highlight(700, 64, "#f2c14e", seed=91)
    X["tex"] = canvas_texture(W, H)
    with open(path, "wb") as fh:
        pickle.dump(X, fh, protocol=4)
    return X


def build_polaroid(port, bg, i):
    MW, MH = 330, 380
    L = Layer(MW + 60, MH + 60)
    o = 30
    L.paint(L.mpoly([(o + 14, o + 20), (o + MW + 14, o + 20), (o + MW + 14, o + MH + 20), (o + 14, o + MH + 20)],
                    smooth=False, blur=12), hexc("#2a1008"), 0.4)
    L.paint(L.mpoly([(o, o), (o + MW, o), (o + MW, o + MH), (o, o + MH)], smooth=False, blur=0.7), CREAM)
    photo = Layer(290, 290)
    photo.paint(np.ones((290, 290), np.float32), hexc(bg))
    crop = port[90:860, 65:835]
    crop = cv2.resize(crop, (290, 290), interpolation=cv2.INTER_AREA)
    photo.rgb = crop[..., :3] + photo.rgb * (1 - crop[..., 3:4])
    L.rgb[o + 20:o + 310, o + 20:o + 310] = photo.rgb
    L.a[o + 20:o + 310, o + 20:o + 310] = 1
    t = Text(DECADES[i]["year"], font("hand", 46, 700), INK)
    spr = t.spr
    x0 = int(o + MW / 2 - spr.shape[1] / 2)
    y0 = o + 308
    reg = L.rgb[y0:y0 + spr.shape[0], x0:x0 + spr.shape[1]]
    reg[:] = spr[..., :3] + reg * (1 - spr[..., 3:4])
    return L.rgba()


# =========================================================================== globals (filled in main / fork)
X = None
TEXT = None
GRAIN = None
WIPE = None


def build_text():
    T = {"dec": []}
    for i, d in enumerate(DECADES):
        ink = INK if d["ink"] == "dark" else CREAM
        e = {}
        e["label"] = Text(f"ARCHETYPE  ·  {i + 1:02d}/10", font("sans", 26, 700), RED, tracking=3)
        e["arche"] = Text(d["arche"], fit_font(d["arche"], "sans", 92, 900, 820), INK)
        e["who"] = Text(d["who"], font("serif_i", 58, 700), INK)
        e["book"] = Text(d["book"], fit_font(d["book"], "serif_i", 42, 400, 840), hexc("#5a2a1e"))
        e["auth"] = Text(f"{d['author'].upper()}  ·  {d['pub']}", font("sans", 28, 600), hexc("#7a4a3a"), tracking=2)
        hf = font("hand", 56, 700)
        e["line"] = [Text(s, hf, RED) for s in wrap(d["line"], hf, 840)]
        yf = font("serif", 200, 900)
        e["yink"] = ink
        T["dec"].append(e)
    yf = font("serif", 200, 900)
    T["digits"] = {}
    for col_name, col in (("dark", INK), ("light", CREAM)):
        T["digits"][col_name] = {ch: Text(ch, yf, col) for ch in "0123456789s"}
    T["yf"] = yf
    T["tl_lab"] = {c: (Text("1900", font("sans", 24, 700), v, tracking=1), Text("2000", font("sans", 24, 700), v, tracking=1))
                   for c, v in (("dark", INK), ("light", CREAM))}
    T["count"] = {c: Text(f"{i + 1:02d} / 10", font("sans", 30, 800), INK if DECADES[i]["ink"] == "dark" else CREAM,
                          tracking=2) for i, c in enumerate(range(10))}
    # intro
    T["t100"] = {str(n): Text(str(n), font("serif", 250, 900), INK) for n in range(0, 101)}
    T["years"] = Text("YEARS", font("sans", 110, 900), INK)
    T["of"] = Text("of women in", font("serif_i", 84, 500), INK)
    T["west"] = Text("Western fiction", font("serif_i", 96, 900), INK)
    T["sub"] = Text("ONE ARCHETYPE PER DECADE  ·  1900–1999", font("sans", 30, 700), RED, tracking=3)
    # outro
    T["o1"] = Text(OUTRO_LINES[0], font("serif", 86, 900), INK)
    T["o2"] = Text(OUTRO_LINES[1], font("serif_i", 56, 500), INK)
    T["o3"] = Text(OUTRO_LINES[2], font("serif_i", 62, 500), INK)
    T["o4"] = Text(OUTRO_LINES[3], font("serif_i", 76, 900), INK)
    # 1990s doodles
    T["doodles"] = [Text(s, font("hand", sz, 700), c) for s, sz, c in
                    (("Dear Diary,", 74, RED), ("Day 1.", 64, INK), ("new me!!", 60, RED), ("xoxo", 64, RED),
                     ("v.g.", 70, INK), ("!!!", 74, INK))]
    return T


def build_wipe():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    U = xx + 0.42 * (yy - H / 2)
    rng = np.random.default_rng(5)
    rows = rng.normal(0, 1, H).astype(np.float32)
    rows = cv2.GaussianBlur(rows.reshape(-1, 1), (0, 0), 1.2).ravel() * 55
    low = cv2.resize(rng.random((12, 1)).astype(np.float32), (1, H), interpolation=cv2.INTER_CUBIC).ravel() * 140
    U = U + (rows + low)[:, None]
    return U.astype(np.float32)


# =========================================================================== scene pieces
def cam(lt, dur):
    return 1.0 + 0.045 * clamp(lt / dur)


def zoom_bg(bg, z, dy=0.0):
    if abs(z - 1) < 1e-4 and dy == 0:
        return bg.copy()
    M = np.array([[z, 0, W / 2 * (1 - z)], [0, z, H / 2 * (1 - z) + dy]], np.float32)
    return cv2.warpAffine(bg, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def zp(x, y, z):
    return W / 2 + (x - W / 2) * z, H / 2 + (y - H / 2) * z


def zblit(dst, spr, x, y, z, scale=1.0, **kw):
    px, py = zp(x, y, z)
    blit(dst, spr, px, py, scale=scale * z, **kw)


def draw_timeline(fr, i, lt, inkname):
    ink = INK if inkname == "dark" else CREAM
    x0, x1, y = 90, 990, 96
    p_prev = (i - 1 + 0.5) / 10 if i > 0 else 0.0
    p_cur = (i + 0.5) / 10
    p = p_prev + (p_cur - p_prev) * ease_io(prog(lt, 0.15, 0.6))
    buf = np.zeros((60, W, 4), np.uint8)
    col = tuple(int(c * 255) for c in ink) + (255,)
    cv2.line(buf, (x0 * 4, 30 * 4), (x1 * 4, 30 * 4), (col[0], col[1], col[2], 110), 3, cv2.LINE_AA, shift=2)
    for k in range(11):
        xx = int((x0 + (x1 - x0) * k / 10) * 4)
        cv2.line(buf, (xx, 22 * 4), (xx, 38 * 4), (col[0], col[1], col[2], 150), 2, cv2.LINE_AA, shift=2)
    xp = x0 + (x1 - x0) * p
    cv2.line(buf, (x0 * 4, 30 * 4), (int(xp * 4), 30 * 4), col, 7, cv2.LINE_AA, shift=2)
    cv2.circle(buf, (int(xp * 4), 30 * 4), 13 * 4, col, -1, cv2.LINE_AA, shift=2)
    hlc = hexc(HL[i])
    cv2.circle(buf, (int(xp * 4), 30 * 4), 7 * 4, tuple(int(c * 255) for c in hlc) + (255,), -1, cv2.LINE_AA, shift=2)
    a = buf.astype(np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    # buf was drawn in RGB order already
    blit(fr, a, 0, y - 30, anchor=(0, 0))
    l0, l1 = TEXT["tl_lab"][inkname]
    l0.draw(fr, x0 - 4, y + 16, alpha=0.8)
    l1.draw(fr, x1 - l1.w + 4, y + 16, alpha=0.8)


def draw_year(fr, i, lt, inkname):
    """'19x0s' with the decade digit rolling in like an odometer."""
    D = TEXT["digits"][inkname]
    yf = TEXT["yf"]
    x, y = 74, 132
    p = ease_out(prog(lt, 0.12, 0.5))
    slide = (1 - ease_out(prog(lt, 0.0, 0.45))) * -60
    D["1"].draw(fr, x, y + slide)
    x2 = x + yf.getlength("1")
    D["9"].draw(fr, x2, y + slide)
    x3 = x2 + yf.getlength("9")
    dh = 230
    clip = (int(x3) - 4, int(y + 20), int(x3 + yf.getlength("0") + 10), int(y + dh))
    prev = str(max(i - 1, 0)) if i > 0 else "0"
    cur = str(i)
    if i > 0 and p < 1:
        blit(fr, D[prev].spr, x3 - D[prev].pad, y - D[prev].pad - p * dh, anchor=(0, 0), clip=clip)
        blit(fr, D[cur].spr, x3 - D[cur].pad, y - D[cur].pad + (1 - p) * dh, anchor=(0, 0), clip=clip)
    else:
        D[cur].draw(fr, x3, y + slide)
    w_prev, w_cur = yf.getlength(prev), yf.getlength(cur)
    x4 = x3 + (w_cur if p >= 1 or i == 0 else w_prev + (w_cur - w_prev) * p)
    D["0"].draw(fr, x4, y + slide)
    D["s"].draw(fr, x4 + yf.getlength("0"), y + slide)
    c = TEXT["count"][i]
    c.draw(fr, 990 - c.w, 230, alpha=0.85 * ease_out(prog(lt, 0.3, 0.4)))


def draw_card(fr, i, lt):
    e = TEXT["dec"][i]
    p = ease_back(prog(lt, CARD_IN, 0.5), 1.2)
    if p <= 0:
        return
    cx0, cy0 = 70, 1265 + (1 - p) * 760
    rot = -1.2
    card = X["card"]
    pad = X["card_pad"]
    blit(fr, card, cx0 - pad, cy0 - pad, anchor=(0, 0))
    lx = cx0 + 46
    e["label"].draw(fr, lx, cy0 + 36)
    # archetype name with highlighter swipe behind
    hp = ease_out(prog(lt, NAME_IN + 0.06, 0.38))
    if hp > 0:
        hl = X["hl"][i]
        cut = max(1, int(hl.shape[1] * hp))
        blit(fr, hl[:, :cut], lx - 18, cy0 + 112, anchor=(0, 0))
    np_ = prog(lt, NAME_IN, 0.3)
    if np_ > 0:
        s = 0.85 + 0.15 * ease_back(np_, 2.5)
        e["arche"].draw(fr, lx, cy0 + 72 + (1 - s) * 40, alpha=clamp(np_ * 3), scale=s)
    wp = ease_out(prog(lt, WHO_IN, 0.35))
    if wp > 0:
        e["who"].draw(fr, lx + (1 - wp) * 40, cy0 + 194, alpha=wp)
    tp = prog(lt, TYPE_IN, TYPE_DUR)
    if tp > 0:
        e["book"].draw(fr, lx, cy0 + 282, upto=len(e["book"].s) * clamp(tp * 1.6))
        e["auth"].draw(fr, lx, cy0 + 344, upto=len(e["auth"].s) * clamp(tp * 1.6 - 0.6))
    for k, ln in enumerate(e["line"]):
        lp = prog(lt, LINE_IN + k * LINE_DUR * 0.8, LINE_DUR)
        if lp > 0:
            ln.draw(fr, lx, cy0 + 398 + k * 62, frac=ease_io(lp))


def portrait_motion(lt, start=0.05):
    p = prog(lt, start, 0.85)
    dy = (1 - ease_back(p, 1.1)) * 900
    rot = 0.9 * math.sin(lt * 1.3)
    sc = 1 + 0.006 * math.sin(lt * 2.7)
    return dy, rot, sc


# ---------------------------------------------------------------------- per-decade props
def props_back(fr, i, lt, z):
    kind = DECADES[i]["props"]
    if kind == "wheat":
        p = ease_out(prog(lt, 0.0, 1.2))
        zblit(fr, X["sun"], 540, 860 - p * 120 + 200 * (1 - p), z, alpha=p)
        zblit(fr, X["field"], 540, 1700, z, anchor=(0.5, 0.5))
    elif kind == "deco":
        zblit(fr, X["sunburst"], 540, 860, z, rot=lt * 5, scale=1.0)
        pulse = 0.65 + 0.35 * math.sin(lt * 4)
        zblit(fr, X["green"], 955, 600, z, alpha=pulse * ease_out(prog(lt, 1.2, 0.6)))
    elif kind == "blossom":
        for spr, x, ax, sgn in ((X["branchL"], 0, 0.0, 1), (X["branchR"], W, 1.0, -1)):
            p = ease_out(prog(lt, 0.15, 0.9))
            zblit(fr, spr, x + sgn * (1 - p) * -300, 360, z, anchor=(ax, 0.05),
                  rot=sgn * (1.5 * math.sin(lt * 1.1)))
    elif kind == "wallpaper":
        p = ease_back(prog(lt, 0.3, 0.6))
        zblit(fr, X["house"], 870, 520, z, rot=4, scale=p)
        zblit(fr, X["clock"], 180, 520, z, scale=p)
        if p > 0.01:
            hx, hy = zp(180, 520, z)
            blit(fr, X["hand_h"], hx, hy, scale=p * z, rot=lt * 120, anchor=(0.5, 1 - 10 / X["hand_h"].shape[0]))
            blit(fr, X["hand_m"], hx, hy, scale=p * z, rot=lt * 720, anchor=(0.5, 1 - 10 / X["hand_m"].shape[0]))
    elif kind == "fire":
        draw_fire(fr, lt, z, back=True)
        for (x, y, s, ph) in ((80, 420, 0.9, 0), (1010, 360, 0.8, 1), (1020, 820, 0.6, 2)):
            p = ease_back(prog(lt, 0.3 + ph * 0.12, 0.6))
            zblit(fr, X["fl"]["hibiscus"], x, y, z, scale=s * p, rot=10 * math.sin(lt + ph))
    elif kind == "sunset":
        p = ease_out(prog(lt, 0.0, 1.0))
        zblit(fr, X["arcs"], 540, 1340 + (1 - p) * 500, z, anchor=(0.5, 0.5 * 1000 / X["arcs"].shape[0] + 0.4),
              rot=2 * math.sin(lt * 0.8))
    elif kind == "handmaids":
        for row, (y, sc, sp, al) in enumerate(((1020, 0.55, 40, 0.55), (1180, 0.8, 70, 0.9))):
            off = (lt * sp) % 170
            for k in range(-1, 9):
                x = k * 170 - off + row * 85
                zblit(fr, X["handmaid"], x, y, z, scale=sc, alpha=al * ease_out(prog(lt, 0.1 + row * 0.15, 0.6)),
                      anchor=(0.5, 1.0))
    elif kind == "noir":
        pass


def props_front(fr, i, lt, z):
    kind = DECADES[i]["props"]
    if kind == "frame":
        for (spr, x, y, s, d) in ((X["fl"]["white"], 150, 1180, 0.9, 0.5), (X["fl"]["pink_s"], 960, 1130, 1.0, 0.7),
                                  (X["fl"]["white_s"], 930, 470, 0.9, 0.9), (X["fl"]["leaf"], 70, 1050, 1.0, 0.4)):
            p = ease_back(prog(lt, d, 0.6))
            zblit(fr, spr, x, y, z, scale=s * p, rot=6 * math.sin(lt * 1.2 + x))
    elif kind == "wheat":
        for k, (x, rot0, sc) in enumerate(((40, -8, 1.0), (120, -3, 0.9), (190, 4, 0.8), (900, -5, 0.85),
                                           (980, 3, 1.0), (1050, 8, 0.95))):
            p = ease_out(prog(lt, 0.2 + k * 0.05, 0.7))
            zblit(fr, X["wheat"][k % 3], x, 1450 + (1 - p) * 500, z, scale=sc,
                  rot=rot0 + 4 * math.sin(lt * 2.1 + k), anchor=(0.5, 1.0))
    elif kind == "deco":
        rng = np.random.default_rng(7)
        for k in range(26):
            x0 = rng.uniform(40, 1040)
            sp = rng.uniform(120, 260)
            ph = rng.uniform(0, 3)
            y = 1500 - ((lt + ph) * sp) % 1300
            x = x0 + 18 * math.sin(lt * 3 + k)
            zblit(fr, X["bubble"], x, y, z, scale=rng.uniform(0.5, 1.3), alpha=0.8 * ease_out(prog(lt, 0.4, 0.5)))
    elif kind == "blossom":
        rng = np.random.default_rng(8)
        for k in range(24):
            x0 = rng.uniform(0, W)
            sp = rng.uniform(90, 170)
            ph = rng.uniform(0, 8)
            y = -40 + ((lt + ph) * sp) % 1500
            x = x0 + 50 * math.sin(lt * 1.4 + k)
            zblit(fr, X["petal"], x, y, z, rot=lt * 90 + k * 40, scale=rng.uniform(0.7, 1.3))
    elif kind == "noir":
        draw_smoke(fr, lt)
        draw_blinds(fr, lt)
    elif kind == "fire":
        rng = np.random.default_rng(9)
        for k in range(30):
            x0 = rng.uniform(0, W)
            sp = rng.uniform(150, 320)
            ph = rng.uniform(0, 6)
            y = 1500 - ((lt + ph) * sp) % 1300
            zblit(fr, X["ember"], x0 + 30 * math.sin(lt * 2 + k), y, z, alpha=0.9)
    elif kind == "sunset":
        p = prog(lt, 0.9, 2.6)
        if 0 < p < 1:
            pts = []
            for k in range(0, 40):
                q = p - k * 0.012
                if q < 0:
                    break
                pts.append(plane_path(q))
            for k in range(2, len(pts), 3):
                zblit(fr, X["ember"], pts[k][0], pts[k][1], z, alpha=0.9 * (1 - k / 40), scale=0.8)
            x, y = plane_path(p)
            x2, y2 = plane_path(min(1, p + 0.01))
            ang = math.degrees(math.atan2(y2 - y, x2 - x))
            zblit(fr, X["plane"], x, y, z, rot=ang - 12, scale=0.9)
    elif kind == "diary":
        spots = ((90, 360, -8), (720, 330, 6), (60, 620, -4), (860, 690, 10), (850, 960, -6), (80, 900, 8))
        for k, (tx, (x, y, r)) in enumerate(zip(TEXT["doodles"], spots)):
            p = ease_back(prog(lt, 0.6 + k * 0.28, 0.4), 2.2)
            if p > 0:
                px, py = zp(x, y, z)
                blit(fr, tx.spr, px, py, scale=p * z, rot=r, anchor=(0, 0))


def plane_path(p):
    x = -120 + p * 1360
    y = 760 - 420 * math.sin(p * math.pi * 0.9) + 90 * math.sin(p * math.pi * 3)
    return x, y


_ybl, _xbl = np.mgrid[0:H, 0:W].astype(np.float32)
_BLP = (_xbl * 0.42 + _ybl * 0.91)


def draw_blinds(fr, lt):
    s = np.sin((_BLP + lt * 40) / 64 * math.pi)
    m = np.clip((s - 0.1) * 2.5, 0, 1) * 0.5
    fr *= (1 - m[..., None] * (1 - hexc("#3a0c12") * 0.6))


def draw_smoke(fr, lt):
    sw, sh = W // 4, H // 4
    buf = np.zeros((sh, sw), np.uint8)
    for k in range(4):
        pts = []
        for j in range(40):
            yy = sh - j * 9
            xx = 225 + k * 6 + 18 * math.sin(j * 0.25 + lt * 1.6 + k) * (j / 40) * 2
            pts.append((int(xx * 4), int(yy * 4)))
        cv2.polylines(buf, [np.array(pts, np.int32)], False, 255, 2 + k % 2, cv2.LINE_AA, shift=2)
    m = cv2.GaussianBlur(buf.astype(np.float32) / 255, (0, 0), 1.6)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR) * 0.35
    fr[:] = fr * (1 - m[..., None]) + hexc("#f2e0d2") * m[..., None]


_FN = np.random.default_rng(3).random((96, 64)).astype(np.float32)
_FN = cv2.resize(_FN, (216, 384), interpolation=cv2.INTER_CUBIC)


def draw_fire(fr, lt, z, back=True):
    sw, sh = 216, 384
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    rise = ease_out(prog(lt, 0.0, 1.0))
    h = (0.46 + 0.08 * np.sin(xx / 9 + lt * 5) + 0.06 * np.sin(xx / 4.3 - lt * 7)) * rise
    h = h * (0.75 + 0.5 * (np.abs(xx - sw / 2) / (sw / 2)))
    n = np.roll(_FN, int(lt * 160) % sh, axis=0)
    v = (yy / sh) - (1 - h) + (n - 0.5) * 0.18
    inten = np.clip(v / 0.22, 0, 1)
    inten = cv2.resize(inten, (W, H), interpolation=cv2.INTER_CUBIC)
    inten = cv2.GaussianBlur(inten, (0, 0), 3)
    c1, c2, c3 = hexc("#a8201c"), hexc("#f0702a"), hexc("#ffd36a")
    col = np.where(inten[..., None] < 0.5, mix(c1, c2, (inten[..., None] * 2)), mix(c2, c3, inten[..., None] * 2 - 1))
    a = np.clip(inten * 1.6, 0, 1)[..., None] * 0.95
    fr[:] = fr * (1 - a) + col * a


# =========================================================================== scenes
def scene_intro(lt):
    z = cam(lt, INTRO + TR)
    fr = zoom_bg(X["bgs"][0], z)
    fl = X["fl"]
    for (spr, x, y, s, d) in ((fl["red"], 60, 930, 1.15, 0.25), (fl["white"], 40, 1180, 1.1, 0.45),
                              (fl["pink"], 1010, 860, 1.2, 0.35), (fl["leaf"], 960, 1080, 1.2, 0.55),
                              (fl["red_s"], 1030, 1350, 1.0, 0.6), (fl["pink_s"], 60, 1520, 1.0, 0.7)):
        p = ease_back(prog(lt, d, 0.7), 1.4)
        zblit(fr, spr, x, y, z, scale=s * p, rot=(1 - p) * 60 + 4 * math.sin(lt * 1.3 + x))
    dy, rot, sc = portrait_motion(lt, 0.15)
    zblit(fr, X["ports"][0], 540, 1940 + dy, z, scale=1.08 * sc, rot=rot, anchor=(0.5, 1.0))
    # title
    cp = ease_io(prog(lt, 0.25, 1.1))
    n = int(round(100 * cp))
    t100 = TEXT["t100"][str(n)]
    a0 = ease_out(prog(lt, 0.1, 0.3))
    t100.draw(fr, 70, 120 + (1 - a0) * 60, alpha=a0)
    t100f = TEXT["t100"]["100"]
    yp = ease_back(prog(lt, 0.9, 0.45), 2)
    if yp > 0:
        TEXT["years"].draw(fr, 70 + t100f.w + 26, 250 - (1 - yp) * 40, alpha=clamp(yp), scale=1)
    op = ease_out(prog(lt, 1.25, 0.4))
    TEXT["of"].draw(fr, 74 + (1 - op) * 60, 430, alpha=op)
    hp = ease_out(prog(lt, 1.7, 0.45))
    if hp > 0:
        hl = X["hl_title"]
        blit(fr, hl[:, :max(1, int(hl.shape[1] * hp))], 64, 568, anchor=(0, 0))
    wp = ease_out(prog(lt, 1.55, 0.4))
    TEXT["west"].draw(fr, 74 + (1 - wp) * 60, 520, alpha=wp)
    sp = prog(lt, 2.2, 0.8)
    TEXT["sub"].draw(fr, 80, 680, upto=len(TEXT["sub"].s) * sp)
    return fr


def scene_decade(i, lt):
    d = DECADES[i]
    z = cam(lt, DEC + TR)
    fr = zoom_bg(X["bgs"][i + 1], z)
    props_back(fr, i, lt, z)
    dy, rot, sc = portrait_motion(lt)
    if d["props"] == "frame":
        zblit(fr, X["cameo"], 540, 1420 + dy, z, scale=0.98 * sc, rot=rot * 2, anchor=(0.5, 0.95))
    else:
        zblit(fr, X["ports"][i + 1], 540, 1560 + dy, z, scale=sc, rot=rot, anchor=(0.5, 1.0))
    props_front(fr, i, lt, z)
    draw_card(fr, i, lt)
    draw_timeline(fr, i, lt, d["ink"])
    draw_year(fr, i, lt, d["ink"])
    return fr


POL_POS = [(220, 360, -6), (540, 330, 3), (860, 370, -2), (150, 730, 4), (420, 700, -5), (680, 740, 6),
           (940, 700, -4), (220, 1080, -3), (540, 1060, 5), (860, 1090, -6)]


def scene_outro(lt):
    z = cam(lt, OUTRO + 1)
    fr = zoom_bg(X["bgs"][-1], z)
    for k, (x, y, r) in enumerate(POL_POS):
        p = ease_back(prog(lt, 0.1 + k * 0.12, 0.5), 1.5)
        if p > 0:
            zblit(fr, X["polaroids"][k], x, y + (1 - p) * 300, z, scale=0.86 * (0.6 + 0.4 * p), rot=r + (1 - p) * 25,
                  alpha=clamp(p * 2))
    y0 = 1330
    p1 = ease_out(prog(lt, 1.6, 0.4))
    TEXT["o1"].draw(fr, 80, y0 + (1 - p1) * 40, alpha=p1)
    p2 = ease_out(prog(lt, 2.2, 0.4))
    TEXT["o2"].draw(fr, 80, y0 + 120 + (1 - p2) * 40, alpha=p2)
    p3 = ease_out(prog(lt, 3.3, 0.4))
    TEXT["o3"].draw(fr, 80, y0 + 230 + (1 - p3) * 40, alpha=p3)
    hp = ease_out(prog(lt, 4.15, 0.5))
    if hp > 0:
        hl = X["hl_pen"]
        blit(fr, hl[:, :max(1, int(hl.shape[1] * hp))], 66, y0 + 352, anchor=(0, 0))
    p4 = ease_out(prog(lt, 3.8, 0.45))
    TEXT["o4"].draw(fr, 80, y0 + 310 + (1 - p4) * 40, alpha=p4)
    return fr


def render_scene(k, lt):
    if k == 0:
        return scene_intro(lt)
    if k == N_DEC + 1:
        return scene_outro(lt)
    return scene_decade(k - 1, lt)


def finish(fr, t, fidx):
    fr *= X["tex"][..., None]
    fr += GRAIN[fidx % len(GRAIN)][..., None]
    fade = clamp((TOTAL - t) / 0.5)
    fin = clamp(t / 0.25)
    fr *= min(fade, fin) * 1.0
    return fr


def render_frame(fidx):
    t = fidx / FPS
    B = boundaries()
    k = max(j for j, b in enumerate(B) if t >= b)
    lt = t - B[k]
    fr = render_scene(k, lt)
    if k > 0 and lt < TR:
        old = render_scene(k - 1, t - B[k - 1])
        p = ease_io(lt / TR)
        front = WIPE.min() - 120 + p * (WIPE.max() - WIPE.min() + 260)
        m = np.clip((front - WIPE) / 22.0, 0, 1)[..., None]
        fr = old * (1 - m) + fr * m
    fr = finish(fr, t, fidx)
    return (np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8)


def init_globals():
    global X, TEXT, GRAIN, WIPE
    X = build_assets()
    TEXT = build_text()
    rng = np.random.default_rng(1)
    GRAIN = [cv2.GaussianBlur(rng.normal(0, 0.018, (H, W)).astype(np.float32), (0, 0), 0.6) for _ in range(6)]
    WIPE = build_wipe()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "women_in_western_literature.mp4"))
    ap.add_argument("--audio", default=os.path.join(HERE, "build", "score.wav"))
    ap.add_argument("--frames", default=None, help="start,end frame range (debug)")
    args = ap.parse_args()
    init_globals()
    if args.preview:
        outdir = os.environ.get("WIL_PREVIEW", os.path.join(HERE, "build", "preview"))
        os.makedirs(outdir, exist_ok=True)
        for ts in args.preview.split(","):
            f = int(float(ts) * FPS)
            img = render_frame(f)
            cv2.imwrite(os.path.join(outdir, f"f_{float(ts):06.2f}.png"), img[..., ::-1])
        return
    n = int(TOTAL * FPS)
    rng_ = range(n)
    if args.frames:
        a, b = map(int, args.frames.split(","))
        rng_ = range(a, b)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
           str(FPS), "-i", "-"]
    if os.path.exists(args.audio) and not args.frames:
        cmd += ["-i", args.audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            args.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for j, img in enumerate(pool.imap(render_frame, rng_, chunksize=4)):
            proc.stdin.write(img.tobytes())
            if j % 60 == 0:
                print(f"frame {j}/{len(rng_)}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", args.out)


if __name__ == "__main__":
    main()
