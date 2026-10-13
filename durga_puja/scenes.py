"""All scenes: static assets are built once (cached); draw() composes a frame with motion."""
import math
import numpy as np
import cv2

from flat import Layer, hexc, mix, INK, pat_stripes
from figures import make_figure, SKINS
import sets
import decor
from sets import C
from content import SCENES, TITLE
from timing import W, H, LENGTHS, TR, boundaries


# ============================================================================ helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, s, d):
    return clamp((t - s) / d)


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_io(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_back(x, s=1.7):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def paste(dst, spr, x0, y0, alpha=1.0):
    h, w = spr.shape[:2]
    X0, Y0 = max(x0, 0), max(y0, 0)
    X1, Y1 = min(x0 + w, dst.shape[1]), min(y0 + h, dst.shape[0])
    if X1 <= X0 or Y1 <= Y0:
        return
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    reg = dst[Y0:Y1, X0:X1]
    a = s[..., 3:4] * alpha
    if dst.shape[2] == 4:
        reg[...] = s * alpha + reg * (1 - a)
    else:
        reg *= (1 - a)
        reg += s[..., :3] * alpha


def blit(dst, spr, x, y, scale=1.0, rot=0.0, alpha=1.0, anchor=(0.5, 0.5)):
    if alpha <= 0.003 or scale <= 0.002:
        return
    h, w = spr.shape[:2]
    ax, ay = anchor[0] * w, anchor[1] * h
    if rot == 0 and abs(scale - 1) < 1e-6:
        paste(dst, spr, int(round(x - ax)), int(round(y - ay)), alpha)
        return
    r = math.radians(rot)
    c, s = math.cos(r) * scale, math.sin(r) * scale
    xs = [c * (u - ax) - s * (v - ay) + x for u, v in ((0, 0), (w, 0), (0, h), (w, h))]
    ys = [s * (u - ax) + c * (v - ay) + y for u, v in ((0, 0), (w, 0), (0, h), (w, h))]
    x0, x1 = max(int(math.floor(min(xs))), 0), min(int(math.ceil(max(xs))), dst.shape[1])
    y0, y1 = max(int(math.floor(min(ys))), 0), min(int(math.ceil(max(ys))), dst.shape[0])
    if x1 <= x0 or y1 <= y0:
        return
    M = np.array([[c, -s, x - c * ax + s * ay - x0], [s, c, y - s * ax - c * ay - y0]], np.float32)
    patch = cv2.warpAffine(spr, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                           borderValue=(0, 0, 0, 0))
    a = patch[..., 3:4] * alpha
    reg = dst[y0:y1, x0:x1]
    reg *= (1 - a)
    reg += patch[..., :3] * alpha


def flip(spr):
    return np.ascontiguousarray(spr[:, ::-1])


def glow(col, r):
    S = int(r * 6)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    d = np.hypot(xx - S / 2, yy - S / 2)
    a = np.clip(np.exp(-(d / r) ** 2) * 0.8 + (d < r * 0.45) * 1.0, 0, 1)
    c = hexc(col)
    return np.dstack([c * a[..., None], a]).astype(np.float32)


def mask_into(bg, spr, mask, x0, y0):
    """Paste a sprite into an RGBA background only where mask (bg-sized) allows."""
    h, w = spr.shape[:2]
    m = mask[y0:y0 + h, x0:x0 + w][..., None]
    s = spr[:m.shape[0], :m.shape[1]] * m
    reg = bg[y0:y0 + m.shape[0], x0:x0 + m.shape[1]]
    reg[...] = s + reg * (1 - s[..., 3:4])


# ============================================================================ text cards
def caption_card(ts, font, cap):
    a = ts(cap["when"], font("sans", 28, 700), hexc("#b23a2a"), tracking=4)
    b = ts(cap["en"], font("serif_i", 52, 600), INK)
    c = ts(cap["bn"], font("bn", 48, 600), hexc("#5a2a1e"))
    w = int(max(a.shape[1], b.shape[1], c.shape[1]) + 80)
    h = 30 + a.shape[0] - 10 + b.shape[0] - 6 + c.shape[0] + 14
    L = Layer(w + 20, h + 20)
    L.shape([(10, 10), (w + 10, 10), (w + 10, h + 10), (10, h + 10)], C["cream"], lw=3)
    L.shape([(20, 20), (w, 20), (w, h), (20, h)], None, lw=2)
    for x in range(30, w, 22):
        L.ellipse((x, 15), (3, 3), C["red"], lw=0)
        L.ellipse((x, h + 5), (3, 3), C["red"], lw=0)
    spr = L.rgba()
    y = 26
    for t in (a, b, c):
        hh, ww = t.shape[:2]
        x = (spr.shape[1] - ww) // 2
        reg = spr[y:y + hh, x:x + ww]
        reg[:] = t + reg * (1 - t[..., 3:4])
        y += hh - (10 if t is a else 6)
    return spr


def stack_text(parts, pad=30, bg="#f6ecd6"):
    w = max(p.shape[1] for p in parts) + pad * 2
    h = sum(p.shape[0] for p in parts) + pad * 2 - 10 * (len(parts) - 1)
    L = Layer(w + 20, h + 20)
    L.shape([(10, 10), (w + 10, 10), (w + 10, h + 10), (10, h + 10)], hexc(bg), lw=4)
    L.shape([(22, 22), (w - 2, 22), (w - 2, h - 2), (22, h - 2)], None, lw=2)
    for x in range(34, w - 10, 26):
        L.ellipse((x, 16), (4, 4), C["red"], lw=0)
        L.ellipse((x, h + 4), (4, 4), C["red"], lw=0)
    spr = L.rgba()
    y = pad + 4
    for p in parts:
        x = (spr.shape[1] - p.shape[1]) // 2
        reg = spr[y:y + p.shape[0], x:x + p.shape[1]]
        reg[:] = p + reg * (1 - p[..., 3:4])
        y += p.shape[0] - 10
    return spr


# ============================================================================ crowds
SAREES = {
    "1975": [("#f6efe2", "#c8281e", None, None), ("#f6efe2", "#c8281e", None, None),
             ("#f6efe2", "#2f7a6e", None, None), ("#e3567e", "#f2c14e", "buti", "#f8e3a0"),
             ("#2f7a6e", "#f2c14e", "dots", "#f6efe2"), ("#f2c14e", "#c8281e", "dots", "#c8281e"),
             ("#3a6db0", "#f2c14e", "buti", "#f6efe2"), ("#f6efe2", "#3f6fb5", "stripes", "#9cc0e4"),
             ("#7a1f22", "#f2c14e", "buti", "#f2c14e"), ("#f39ab4", "#c8281e", "dots", "#fbf7ee")],
    "modern": [("#e3567e", "#f2c14e", "buti", "#f8e3a0"), ("#2f7a6e", "#f2c14e", "dots", "#f6efe2"),
               ("#f08a24", "#7a1f22", "stripes", "#f2c14e"), ("#7a3fa0", "#f2c14e", "buti", "#f39ab4"),
               ("#3a6db0", "#f2c14e", "checks", "#9cc0e4"), ("#c8281e", "#f2c14e", "buti", "#f2c14e"),
               ("#f6efe2", "#c8281e", None, None), ("#1f6b5a", "#e3567e", "dots", "#f39ab4"),
               ("#f2c14e", "#2f7a6e", "dots", "#2f7a6e"), ("#d94f6a", "#3f6fb5", "stripes", "#fbf7ee")],
}
KURTAS = {
    "1975": [("#f6f0e2", None, None), ("#f6f0e2", None, None), ("#f2d27a", None, None),
             ("#c8d8ec", "checks", "#3f6fb5"), ("#e9dcc4", "dots", "#7a1f22")],
    "modern": [("#f2d27a", "buti", "#c8281e"), ("#c8d8ec", "checks", "#3f6fb5"), ("#e3567e", "dots", "#f6efe2"),
               ("#2f7a6e", "dots", "#f2c14e"), ("#f6f0e2", "stripes", "#c8281e"), ("#7a1f22", "buti", "#f2c14e"),
               ("#3f6fb5", None, None), ("#f08a24", None, None)],
}
LAAL_PAAR = dict(saree="#f6efe2", border="#c8281e", blouse="#c8281e", sindoor=True)


def random_person(rng, h, era="1975"):
    sk = SKINS[rng.integers(0, len(SKINS))]
    key = "1975" if era == "1975" else "modern"
    female = rng.random() < (0.8 if era == "bijoya" else 0.6)
    if female:
        sa, bo, pa, pc = SAREES[key][rng.integers(0, len(SAREES[key]))]
        if era == "bijoya":
            sa, bo, pa, pc = "#f6efe2", "#c8281e", (None if rng.random() < 0.6 else "buti"), "#c8281e"
        spec = dict(kind="woman", saree=sa, border=bo,
                    blouse=[bo, "#2f7a6e", "#f2c14e", "#c8281e", "#3f6fb5"][rng.integers(0, 5)],
                    pattern=pa, pat_col=pc, skin=sk, sindoor=rng.random() < 0.6,
                    hair=["bun", "bun", "braid", "open", "grey_bun"][rng.integers(0, 5)],
                    arms=["fold", "clap", "down", "clap"][rng.integers(0, 4)])
        if spec["hair"] == "grey_bun":
            spec.update(hair_col="#d9d4cc", glasses=rng.random() < 0.5)
        if era == "bijoya":
            spec.update(sindoor_khela=True, sindoor=True, arms=["up", "clap", "clap", "fold"][rng.integers(0, 4)])
    else:
        ku, pa, pc = KURTAS[key][rng.integers(0, len(KURTAS[key]))]
        spec = dict(kind="man", kurta=ku, pattern=pa, pat_col=pc, skin=sk, hair="short",
                    mustache=rng.random() < (0.6 if era == "1975" else 0.35), glasses=rng.random() < 0.25,
                    arms=["fold", "down", "clap"][rng.integers(0, 3)])
        if era != "1975" and rng.random() < 0.5:
            spec["trousers"] = ["#2f4f7a", "#3a3a44", "#5a6a8a", "#c9b69a"][rng.integers(0, 4)]
        if era == "world" and rng.random() < 0.4:
            spec.update(kurta=["#3a3a44", "#7a1f22", "#2f4f7a"][rng.integers(0, 3)], pattern=None)
    if era in ("2000s", "2021", "world") and rng.random() < 0.18:
        spec["arms"] = "phone"
    if era == "2020":
        spec["mask"] = True
        spec["arms"] = ["fold", "down", "phone"][rng.integers(0, 3)]
    if rng.random() < 0.12:
        h *= 0.62
        spec["sindoor"] = False
    return spec, h


def crowd_rows(rng, rows, era, skip=None):
    out = []
    for y, n, h0 in rows:
        xs = np.linspace(-30, W + 30, n) + rng.uniform(-35, 35, n)
        for x in xs:
            if skip and skip(x, y):
                continue
            spec, h = random_person(rng, h0 * rng.uniform(0.94, 1.06), era)
            anim = "clap" if spec["arms"] == "clap" and rng.random() < 0.6 else None
            out.append((spec, h, x, y + rng.uniform(-16, 16), anim, rng.random() < 0.5))
    return out


def compose_crowd(people, nphase=6):
    """Merge non-animated figures into a few big sprites (depth order); keep animated ones separate."""
    items = sorted(people, key=lambda p: p[3])
    out = []
    pad = 700
    batch = [None]

    def flush():
        b = batch[0]
        if b is None:
            return
        ys, xs = np.nonzero(b[..., 3] > 0.002)
        if len(xs):
            x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
            out.append(dict(kind="static", spr=np.ascontiguousarray(b[y0:y1, x0:x1]), x=int(x0), y=int(y0) - pad))
        batch[0] = None

    for spec, h, x, y, anim, fl in items:
        if anim:
            flush()
            frames = []
            for p in range(nphase if anim in ("clap", "dhunuchi") else 1):
                s = dict(spec)
                if anim in ("clap", "dhunuchi"):
                    s["arms"] = anim
                    s["phase"] = p / nphase
                spr = make_figure(s, h)
                frames.append(flip(spr) if fl else spr)
            out.append(dict(kind="anim", frames=frames, x=x, y=y, anim=anim, seed=(x * 0.013 + y * 0.007) % 1))
        else:
            if batch[0] is None:
                batch[0] = np.zeros((H + pad * 2, W, 4), np.float32)
            spr = make_figure(spec, h)
            if fl:
                spr = flip(spr)
            sh, sw = spr.shape[:2]
            paste(batch[0], spr, int(x - sw / 2), int(y + pad - (sh - 18)))
    flush()
    return out


def draw_crowd(fr, items, t, beat=0.625, dx=0, dy=0):
    for it in items:
        if it["kind"] == "static":
            paste(fr, it["spr"], it["x"] + dx, it["y"] + dy)
            continue
        fs = it["frames"]
        rot = 0.0
        if it["anim"] in ("clap", "dhunuchi"):
            spd = 1.0 if it["anim"] == "clap" else 0.5
            spr = fs[int((t / beat * spd + it["seed"]) * len(fs)) % len(fs)]
        else:
            spr = fs[0]
        if it["anim"] in ("sway", "drum"):
            rot = 2.5 * math.sin((t / beat + it["seed"]) * math.pi)
        blit(fr, spr, it["x"] + dx, it["y"] + dy, rot=rot, anchor=(0.5, 1.0 - 18 / spr.shape[0]))


def performers(rng, era, spots):
    out = []
    for kind, x, y, h in spots:
        if kind == "dhaki":
            out.append((dict(kind="dhaki", kurta=["#f6f0e2", "#f2d27a", "#e9dcc4"][rng.integers(0, 3)], hair="short",
                             mustache=True, skin=SKINS[rng.integers(2, 5)]), h, x, y, "drum", x > W / 2))
        else:
            sp = [dict(saree="#e3567e", border="#f2c14e", blouse="#2f7a6e", pattern="buti", pat_col="#f8e3a0"),
                  dict(LAAL_PAAR), dict(saree="#2f7a6e", border="#f2c14e", blouse="#f2c14e", pattern="dots",
                                        pat_col="#f6efe2")][rng.integers(0, 3)]
            if era == "bijoya":
                sp = dict(LAAL_PAAR, sindoor_khela=True)
            out.append((dict(kind="woman", arms="dhunuchi", skin=SKINS[rng.integers(0, 4)], **sp), h, x, y,
                        "dhunuchi", False))
    return out


# ============================================================================ shared art
def arch_mask():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, spring, r = W / 2, 560, 380
    m = (((xx - cx) ** 2 + (yy - spring) ** 2) < (r - 2) ** 2) | \
        ((yy >= spring) & (np.abs(xx - cx) < r - 2) & (yy < 1060))
    return m.astype(np.float32)


def opening_mask(cx, top, rx, ry, bottom):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    m = ((((xx - cx) / rx) ** 2 + ((yy - top) / ry) ** 2) < 1) | ((yy >= top) & (np.abs(xx - cx) < rx) & (yy < bottom))
    return m.astype(np.float32)


def deities():
    return dict(lakshmi=sets.deity_woman(300, "#f39ab4", "#e7b23a", attr="lotus"),
                saraswati=sets.deity_woman(300, "#fbf7ee", "#3f6fb5", skin="#f6e7c8", attr="veena"),
                ganesh=sets.ganesh(250), kartik=sets.kartik(255))


# ============================================================================ scene builders
def build_intro(ts, font):
    bg = decor.folk_panel(W, H, seed=11)
    decor.sun(bg, 190, 200, 60)
    decor.moon(bg, W - 190, 200, 52)
    decor.peacock(bg, 210, 1150, 1.2)
    decor.peacock(bg, W - 210, 1150, 1.2, flip=True)
    decor.border_band(bg, 0, 0, W, 70)
    decor.border_band(bg, 0, H - 70, W, H)
    decor.border_band(bg, 0, 70, 70, H - 70, horizontal=False)
    decor.border_band(bg, W - 70, 70, W, H - 70, horizontal=False)
    A = dict(bg=bg.rgba()[..., :3].copy(), halo=decor.chalchitra_rich(470), durga=sets.durga_v3(1040))
    A["title"] = stack_text([ts(TITLE["en"], font("serif", 120, 900), INK),
                             ts(TITLE["bn"], font("bn", 112, 700), hexc("#b23a2a")),
                             ts(TITLE["sub"], font("sans", 30, 700), hexc("#5a2a1e"), tracking=3)])
    return A


def build_1975():
    bg = sets.thakur_dalan_v().rgba()
    mask_into(bg, decor.sanctum_backdrop(760, 900, seed=5).rgba(), arch_mask(), 160, 170)
    deco = Layer(W, H)
    sets.garland_swag(deco, 0, W, 136, sag=60)
    sets.garland_swag(deco, 120, W - 120, 230, sag=90)
    for x in (110, W - 110):
        sets.lantern(deco, x, 420, 1.1)
    A = dict(bg=bg[..., :3].copy(), deco=deco.rgba(), halo=decor.chalchitra_rich(372), durga=sets.durga_v3(770))
    A.update(deities())
    rng = np.random.default_rng(1975)
    people = [(dict(kind="priest", skin=SKINS[2], hair="bald"), 230, 300, 1166, "sway", False),
              (dict(LAAL_PAAR, kind="seated_woman", skin=SKINS[1], arms="fold"), 200, 780, 1168, None, False)]
    people += performers(rng, "1975", [("dhaki", 150, 1330, 330), ("dhaki", 930, 1330, 330),
                                       ("dhunuchi", 420, 1420, 340), ("dhunuchi", 680, 1440, 340)])
    people += crowd_rows(rng, ((1262, 10, 255), (1360, 9, 290), (1500, 9, 330), (1650, 8, 380), (1810, 8, 430),
                               (1990, 7, 490)), "1975",
                         skip=lambda x, y: y < 1450 and 330 < x < 760 and rng.random() < 0.5)
    A["crowd"] = compose_crowd(people)
    return A


def build_1985(ts, font):
    bg = decor.pandal_1985().rgba()
    mask_into(bg, decor.sanctum_backdrop(640, 600, seed=8).rgba(), opening_mask(540, 720, 318, 118, 1188), 220, 600)
    ban = ts("সর্বজনীন দুর্গোৎসব", font("bn", 58, 800), hexc("#b23a2a"))
    paste(bg, ban, 540 - ban.shape[1] // 2, 528 - ban.shape[0] // 2)
    A = dict(bg=bg[..., :3].copy(), halo=decor.chalchitra_rich(290), durga=sets.durga_v3(500))
    lights = Layer(W, H)
    pts = []
    for y, sag in ((250, 60), (340, 80), (610, 40)):
        pts += decor.string_lights(lights, y, sag, n=26)
    A["lights_wire"], A["bulbs"] = lights.rgba(), pts
    A["bulb"] = [glow(c, 9) for c in ("#ffd76a", "#ff6a5a", "#7ad1ff", "#9cff8a")]
    rng = np.random.default_rng(1985)
    people = performers(rng, "1985", [("dhaki", 120, 1340, 320), ("dhaki", 960, 1340, 320)])
    people += crowd_rows(rng, ((1250, 11, 240), (1340, 10, 280), (1470, 9, 320), (1620, 9, 370), (1790, 8, 420),
                               (1970, 7, 480)), "1985")
    A["crowd"] = compose_crowd(people)
    return A


def build_2000s():
    bg = decor.theme_pandal_2000s().rgba()
    mask_into(bg, decor.sanctum_backdrop(580, 560, seed=12).rgba(), opening_mask(540, 760, 288, 118, 1198), 250, 640)
    A = dict(bg=bg[..., :3].copy(), halo=decor.chalchitra_rich(270), durga=sets.durga_v3(520))
    gate = []
    for t in np.linspace(0, 1, 70):
        a = math.pi * t
        gate.append((540 - math.cos(a) * 500, 1260 - math.sin(a) * 700))
    for t in np.linspace(0, 1, 50):
        a = math.pi * t
        gate.append((540 - math.cos(a) * 440, 1260 - math.sin(a) * 620))
    A["gate"] = gate
    A["bulb"] = [glow(c, 8) for c in ("#ffd76a", "#ff5ab4", "#5ad1ff", "#9cff8a", "#ff8a3a")]
    rng = np.random.default_rng(2005)
    people = crowd_rows(rng, ((1250, 11, 230), (1330, 11, 265), (1440, 10, 300), (1580, 9, 345), (1740, 8, 400),
                              (1920, 7, 460)), "2000s")
    A["crowd"] = compose_crowd(people)
    return A


CITY = [("london", "LONDON", "#b9c8d8", "#7a8a6a"), ("newyork", "NEW YORK", "#f2b59a", "#8a7a6a"),
        ("toronto", "TORONTO", "#c9b8e0", "#7a6a8a"), ("sydney", "SYDNEY", "#9cd0e4", "#c9b69a")]


def build_world(ts, font):
    bg = Layer(W, H)
    bg.paint(np.ones((H, W), np.float32), hexc("#f3e6cc"))
    decor.kumartuli(bg, 250, 660)
    A = dict(bg=bg.rgba()[..., :3].copy(), strips=[], mini=sets.durga_v3(210),
             crate_lab=[ts(l, font("sans", 22, 800), INK, tracking=2) for l in ("LONDON", "NEW YORK", "TORONTO",
                                                                                 "SYDNEY")])
    rng = np.random.default_rng(42)
    for k, (kind, label, sky, ground) in enumerate(CITY):
        y0 = 660 + k * 315
        L = Layer(W, 315)
        decor.skyline(L, kind, 0, 0, W, 315, sky, ground)
        side = 1 if k % 2 == 0 else -1
        hx = 860 if side > 0 else 220
        L.shape([(hx - 150, 70), (hx + 150, 70), (hx + 150, 300), (hx - 150, 300)], hexc("#5a1e1c"), lw=3)
        L.shape([(hx - 150, 70), (hx + 150, 70), (hx + 150, 96), (hx - 150, 96)], C["gold"], lw=3)
        spr = L.rgba()
        lab = ts(label, font("sans", 30, 800), hexc("#fbf7ee"), tracking=5)
        lb = Layer(lab.shape[1] + 30, lab.shape[0] + 10)
        lb.shape([(4, 4), (lab.shape[1] + 26, 4), (lab.shape[1] + 26, lab.shape[0] + 6), (4, lab.shape[0] + 6)],
                 C["red"], lw=3)
        lbs = lb.rgba()
        paste(lbs, lab, 15, 5)
        paste(spr, lbs, 30 if side > 0 else W - lbs.shape[1] - 30, 16)
        paste(spr, A["mini"], hx - A["mini"].shape[1] // 2, 300 - A["mini"].shape[0])
        people = []
        for x in np.linspace(20, W - 20, 13):
            if abs(x - hx) < 140:
                continue
            spec, h = random_person(rng, rng.uniform(150, 175), "world")
            people.append((spec, h, x + rng.uniform(-20, 20), 312, None, rng.random() < 0.5))
        for it in compose_crowd(people):
            paste(spr, it["spr"], it["x"], it["y"])
        A["strips"].append(dict(spr=spr, y=y0, side=side))
    return A


def build_2020(ts, font):
    p = decor.pandal_1985()
    gray = p.rgb.mean(axis=2, keepdims=True)
    p.rgb = (p.rgb * 0.35 + gray * 0.65) * 0.8
    decor.barricade(p, 1150, 60, W - 60)
    spots = ((180, 1500), (540, 1440), (900, 1500), (300, 1760), (780, 1760))
    for x, y in spots:
        p.ellipse((x, y), (90, 28), None, lw=4, ink=hexc("#f6ecd6"))
    A = dict(bg=p.rgba()[..., :3].copy())
    ph = Layer(W, H)
    A["screen"] = decor.phone(ph, 540, 1230, 460, 760)
    A["phone"] = ph.rgba()
    scr = decor.sanctum_backdrop(460, 760, seed=20).rgba()
    d = sets.durga_v3(560)
    paste(scr, d, 230 - d.shape[1] // 2, 700 - d.shape[0])
    A["screen_img"] = scr
    live = ts("● LIVE", font("sans", 28, 800), hexc("#fbf7ee"), tracking=2)
    lb = Layer(live.shape[1] + 20, live.shape[0] + 6)
    lb.shape([(2, 2), (live.shape[1] + 18, 2), (live.shape[1] + 18, live.shape[0] + 4), (2, live.shape[0] + 4)],
             C["red"], lw=2)
    A["live"] = lb.rgba()
    paste(A["live"], live, 10, 3)
    heart = Layer(60, 56)
    heart.shape([(30, 52), (4, 24), (6, 10), (18, 4), (30, 14), (42, 4), (54, 10), (56, 24)], C["red"], lw=3,
                smooth=True)
    A["heart"] = heart.rgba()
    hand = Layer(W, 420)
    sk = SKINS[2]
    hand.shape([(250, 420), (300, 120), (340, 60), (380, 90), (370, 200), (400, 420)], hexc(sk), lw=4, smooth=True)
    hand.shape([(830, 420), (780, 120), (740, 60), (700, 90), (710, 200), (680, 420)], hexc(sk), lw=4, smooth=True)
    hand.shape([(230, 420), (420, 420), (420, 380), (230, 380)], C["red"], lw=3)
    hand.shape([(660, 420), (850, 420), (850, 380), (660, 380)], hexc("#fbf7ee"), lw=3)
    A["hands"] = hand.rgba()
    rng = np.random.default_rng(2020)
    people = []
    for x, y in spots:
        spec, h = random_person(rng, 300 + (y - 1440) * 0.4, "2020")
        people.append((spec, h, x, y, None, rng.random() < 0.5))
    A["crowd"] = compose_crowd(people)
    return A


def build_2021():
    bg = decor.folk_panel(W, H, seed=21)
    decor.peacock(bg, 190, 980, 1.0)
    decor.peacock(bg, W - 190, 980, 1.0, flip=True)
    decor.border_band(bg, 0, 0, W, 70)
    decor.border_band(bg, 0, 70, 70, 1300, horizontal=False)
    decor.border_band(bg, W - 70, 70, W, 1300, horizontal=False)
    bg.shape([(0, 1290), (W, 1290), (W, H), (0, H)], C["vermilion"], lw=3)
    A = dict(bg=bg.rgba()[..., :3].copy(), halo=decor.chalchitra_rich(440), durga=sets.durga_v3(900))
    A["seal"], _ = decor.seal(120)
    A["spark"] = [glow(c, 5) for c in ("#ffd76a", "#ff6a5a", "#ffffff", "#9cff8a")]
    rng = np.random.default_rng(2021)
    people = performers(rng, "2021", [("dhaki", 110, 1420, 330), ("dhaki", 970, 1420, 330),
                                      ("dhunuchi", 380, 1470, 340), ("dhunuchi", 700, 1480, 340)])
    people += crowd_rows(rng, ((1330, 11, 240), (1420, 10, 280), (1560, 9, 330), (1720, 8, 390), (1900, 7, 450),
                               (2060, 7, 500)), "2021",
                         skip=lambda x, y: y < 1500 and 300 < x < 780 and rng.random() < 0.6)
    A["crowd"] = compose_crowd(people)
    return A


def build_today(ts, font):
    bg = Layer(W, H)
    sky = np.linspace(0, 1, H, dtype=np.float32)[:, None] * np.ones((1, W), np.float32)
    bg.paint(np.ones((H, W), np.float32), hexc("#f6b37a"))
    bg.paint(np.clip(1 - sky * 2.2, 0, 1), hexc("#e86a4a"))
    decor.sun(bg, 820, 330, 70)
    bg.shape([(0, 560), (W, 560), (W, 760), (0, 760)], hexc("#3f6fb5"), lw=3,
             pattern=pat_stripes(hexc("#5a86c8"), 34, 6, 0.0))
    for k in range(3):
        x = 150 + k * 330
        bg.shape([(x - 60, 600), (x + 60, 600), (x + 40, 626), (x - 40, 626)], hexc("#6a4420"), lw=3)
        bg.shape([(x - 4, 520), (x + 4, 520), (x + 4, 600), (x - 4, 600)], hexc("#6a4420"), lw=2)
        bg.shape([(x + 4, 526), (x + 50, 580), (x + 4, 590)], hexc("#f6ecd6"), lw=2)
    decor.ghat(bg, 760)
    bg.shape([(0, 1100), (W, 1100), (W, H), (0, H)], C["vermilion"], lw=3)
    A = dict(bg=bg.rgba()[..., :3].copy(), durga=sets.durga_v3(380))
    plat = Layer(560, 40)
    plat.shape([(10, 6), (550, 6), (550, 30), (10, 30)], hexc("#d9b26a"), lw=3)
    A["platform"] = plat.rgba()
    rng = np.random.default_rng(2025)
    bearers = []
    for x in (330, 430, 650, 750):
        spec, h = random_person(rng, 230, "today")
        spec = dict(kind="man", kurta=["#f6f0e2", "#f2d27a"][rng.integers(0, 2)], hair="short", skin=spec["skin"],
                    arms="up", mustache=True)
        bearers.append((spec, 230, x, 1100, None, x > 540))
    A["bearers"] = compose_crowd(bearers)
    people = performers(rng, "bijoya", [("dhaki", 110, 1330, 330), ("dhaki", 970, 1330, 330),
                                        ("dhunuchi", 400, 1400, 340), ("dhunuchi", 690, 1410, 340)])
    people += crowd_rows(rng, ((1220, 11, 250), (1310, 10, 285), (1450, 9, 330), (1610, 8, 380), (1790, 8, 440),
                               (1980, 7, 500)), "bijoya",
                         skip=lambda x, y: y < 1450 and 320 < x < 770 and rng.random() < 0.6)
    A["crowd"] = compose_crowd(people)
    A["sindoor"] = glow("#d4231c", 6)
    A["final"] = stack_text([ts("শুভ বিজয়া", font("bn", 130, 800), hexc("#b23a2a")),
                             ts("Shubho Bijoya", font("serif_i", 70, 700), INK),
                             ts(TITLE["sub"], font("sans", 28, 700), hexc("#5a2a1e"), tracking=3)])
    return A


# ============================================================================ scene drawers
def camera(fr, z, cx=W / 2, cy=H / 2, dx=0.0):
    if abs(z - 1) < 1e-4:
        return fr
    M = np.array([[z, 0, cx * (1 - z) + dx], [0, z, cy * (1 - z)]], np.float32)
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def halo_and_durga(fr, A, halo_y, feet_y, lt, dx=6):
    blit(fr, A["halo"], W / 2, halo_y, anchor=(0.5, 1.0 - 30 / A["halo"].shape[0]))
    blit(fr, A["durga"], W / 2 + dx, feet_y + 3 * math.sin(lt * 1.2), anchor=(0.5, 1.0))


def d_intro(A, lt):
    fr = A["bg"].copy()
    halo_and_durga(fr, A, 900, 1320, lt, dx=10)
    z = 1.28 - 0.28 * ease_io(prog(lt, 0, LENGTHS[0] * 0.8))
    fr = camera(fr, z, cy=760)
    p = ease_out(prog(lt, 2.4, 1.0))
    blit(fr, A["title"], W / 2, 1640 + (1 - p) * 80, alpha=p)
    return fr


def d_1975(A, lt):
    fr = A["bg"].copy()
    blit(fr, A["halo"], W / 2, 900, anchor=(0.5, 1.0 - 30 / A["halo"].shape[0]))
    blit(fr, A["deco"], W / 2, H / 2)
    blit(fr, A["durga"], W / 2 + 6, 1062 + 3 * math.sin(lt * 1.2), anchor=(0.5, 1.0))
    for key, x in (("lakshmi", 150), ("ganesh", 70), ("saraswati", 930), ("kartik", 1012)):
        blit(fr, A[key], x, 1168, anchor=(0.5, 1.0 - 18 / A[key].shape[0]))
    draw_crowd(fr, A["crowd"], lt)
    return camera(fr, 1.0 + 0.035 * clamp(lt / LENGTHS[1]), cy=H * 0.40)


def d_1985(A, lt):
    fr = A["bg"].copy()
    halo_and_durga(fr, A, 1000, 1186, lt, dx=4)
    blit(fr, A["lights_wire"], W / 2, H / 2)
    for k, (x, y) in enumerate(A["bulbs"]):
        on = (k + int(lt * 4)) % 3 != 0
        blit(fr, A["bulb"][k % 4], x, y + 8, alpha=1.0 if on else 0.35)
    draw_crowd(fr, A["crowd"], lt)
    return camera(fr, 1.0 + 0.035 * clamp(lt / LENGTHS[2]), cy=H * 0.45)


def d_2000s(A, lt):
    fr = A["bg"].copy()
    halo_and_durga(fr, A, 1080, 1196, lt, dx=4)
    for k, (x, y) in enumerate(A["gate"]):
        blit(fr, A["bulb"][(k + int(lt * 10)) % 5], x, y, alpha=0.95)
    draw_crowd(fr, A["crowd"], lt)
    fr *= np.array([0.9, 0.92, 1.0], np.float32)
    return camera(fr, 1.0 + 0.035 * clamp(lt / LENGTHS[3]), cy=H * 0.5)


def d_world(A, lt):
    fr = A["bg"].copy()
    for k, x in enumerate((470, 650, 830, 1000)):
        sp = A["crate_lab"][k]
        y = 660 - 30 - (k % 2) * 40 - 60
        bob = -abs(math.sin(lt * 3 + k)) * 8
        paste(fr, sp, int(x - 5 - sp.shape[1] / 2), int(y + bob - sp.shape[0] / 2))
    for k, s in enumerate(A["strips"]):
        p = ease_out(prog(lt, 0.4 + k * 0.7, 1.0))
        paste(fr, s["spr"], int((1 - p) * W * s["side"]), s["y"])
    return camera(fr, 1.0 + 0.02 * clamp(lt / LENGTHS[4]), cy=H * 0.5)


def d_2020(A, lt):
    fr = A["bg"].copy()
    draw_crowd(fr, A["crowd"], lt)
    x0, y0, x1, y1 = [int(v) for v in A["screen"]]
    p = ease_out(prog(lt, 0.6, 1.2))
    yoff = int((1 - p) * 900)
    paste(fr, A["phone"], 0, yoff)
    paste(fr, A["screen_img"][: y1 - y0, : x1 - x0], x0, y0 + yoff)
    paste(fr, A["live"], x0 + 20, y0 + 20 + yoff)
    for k in range(6):
        t = (lt * 0.5 + k / 6) % 1.0
        blit(fr, A["heart"], x1 - 60 + 20 * math.sin(t * 9 + k), y1 - 40 - t * 520 + yoff, scale=0.6 + 0.3 * t,
             alpha=(1 - t) * p)
    paste(fr, A["hands"], 0, H - 420 + yoff)
    return camera(fr, 1.0 + 0.03 * clamp(lt / LENGTHS[5]), cy=H * 0.55)


def d_2021(A, lt):
    fr = A["bg"].copy()
    for b in range(3):
        t = (lt * 0.8 + b * 0.37) % 1.0
        cx, cy = [(220, 320), (860, 280), (540, 170)][b]
        for j in range(18):
            a = j / 18 * math.tau
            blit(fr, A["spark"][(j + b) % 4], cx + math.cos(a) * 160 * t, cy + math.sin(a) * 160 * t + 60 * t * t,
                 alpha=(1 - t))
    halo_and_durga(fr, A, 1110, 1300, lt, dx=8)
    draw_crowd(fr, A["crowd"], lt)
    p = prog(lt, 2.2, 0.6)
    if p > 0:
        blit(fr, A["seal"], 880, 470, scale=1.0 + 1.4 * (1 - ease_back(p, 2.0)), rot=-12, alpha=clamp(p * 3))
    return camera(fr, 1.0 + 0.035 * clamp(lt / LENGTHS[6]), cy=H * 0.5)


def d_today(A, lt):
    fr = A["bg"].copy()
    px = 540 + 120 * ease_io(prog(lt, 0.5, 9.0))
    bob = 5 * math.sin(lt * 4)
    blit(fr, A["durga"], px, 960 + bob, anchor=(0.5, 1.0))
    blit(fr, A["platform"], px, 950 + bob, anchor=(0.5, 0))
    draw_crowd(fr, A["bearers"], lt, dx=int(px - 540), dy=int(bob * 0.5))
    draw_crowd(fr, A["crowd"], lt)
    rng = np.random.default_rng(7)
    for k in range(40):
        x0 = rng.uniform(0, W)
        sp = rng.uniform(40, 90)
        y = 1900 - ((lt + rng.uniform(0, 10)) * sp) % 900
        blit(fr, A["sindoor"], x0 + 30 * math.sin(lt + k), y, alpha=0.7)
    fr = camera(fr, 1.0 + 0.03 * clamp(lt / LENGTHS[7]), cy=H * 0.5)
    p = ease_out(prog(lt, LENGTHS[7] - 4.6, 1.2))
    if p > 0:
        fr *= (1 - 0.35 * p)
        blit(fr, A["final"], W / 2, 900 + (1 - p) * 60, alpha=p)
    return fr


DRAW = [d_intro, d_1975, d_1985, d_2000s, d_world, d_2020, d_2021, d_today]


# ============================================================================ assembly
def build(ts, font):
    A = {"s": [build_intro(ts, font), build_1975(), build_1985(ts, font), build_2000s(), build_world(ts, font),
               build_2020(ts, font), build_2021(), build_today(ts, font)]}
    A["caps"] = [caption_card(ts, font, s["caption"]) if s.get("caption") else None for s in SCENES]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot(xx - W / 2, yy - H / 2)
    th = np.arctan2(yy - H / 2, xx - W / 2)
    A["wipe"] = (d + 46 * np.sin(th * 12) + 20 * np.sin(th * 5)).astype(np.float32)
    return A


def scene_frame(A, k, lt):
    fr = DRAW[k](A["s"][k], lt)
    cap = A["caps"][k]
    if cap is not None:
        p = ease_out(prog(lt, 0.9, 0.8))
        if k == 7:
            p *= 1 - prog(lt, LENGTHS[7] - 4.8, 0.6)
        blit(fr, cap, W / 2, 26 + (1 - p) * -40, alpha=p, anchor=(0.5, 0))
    return fr


def draw(A, t):
    B = boundaries()
    k = max(j for j, b in enumerate(B) if t >= b)
    lt = t - B[k]
    fr = scene_frame(A, k, lt)
    if k > 0 and lt < TR:  # alpana-petal radial wipe with a cream rim
        old = scene_frame(A, k - 1, t - B[k - 1])
        rad = ease_io(lt / TR) * (A["wipe"].max() + 60)
        m = np.clip((rad - A["wipe"]) / 14.0, 0, 1)[..., None]
        ring = np.clip(1 - np.abs(rad - 30 - A["wipe"]) / 16.0, 0, 1)[..., None]
        fr = old * (1 - m) + fr * m
        fr = fr * (1 - ring) + hexc("#f6ecd6") * ring
    return fr
