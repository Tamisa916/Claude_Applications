"""Dense decorative backgrounds and set pieces for the later scenes (all 9:16)."""
import math
import numpy as np
import cv2
from flat import Layer, hexc, mix, INK, pat_dots, pat_stripes, pat_buti, pat_checks
from sets import C, chalchitra
from timing import W, H


# ------------------------------------------------------------------------------------- folk motifs
def lotus(L, x, y, s=1.0, col="#e2563e", col2="#f39a7a"):
    for k, a in enumerate(np.linspace(-1.1, 1.1, 5)):
        L.ellipse((x + math.sin(a) * 16 * s, y - math.cos(a) * 16 * s), (8 * s, 22 * s), hexc(col if k % 2 else col2),
                  ang=math.degrees(a), lw=2)
    L.shape([(x - 26 * s, y), (x + 26 * s, y), (x + 16 * s, y + 12 * s), (x - 16 * s, y + 12 * s)], hexc("#c94a2c"), lw=2)
    L.ellipse((x, y - 6 * s), (6 * s, 5 * s), C["gold"], lw=1)


def leaf(L, x, y, ang, s=1.0, col="#4f7a3a"):
    c, sn = math.cos(ang), math.sin(ang)
    pts = [(x, y), (x + (c * 18 - sn * 8) * s, y + (sn * 18 + c * 8) * s), (x + c * 40 * s, y + sn * 40 * s),
           (x + (c * 18 + sn * 8) * s, y + (sn * 18 - c * 8) * s)]
    L.shape(pts, hexc(col), lw=2, smooth=True)
    L.line([(x, y), (x + c * 34 * s, y + sn * 34 * s)], 1, hexc("#2f4f22"))


def vine(L, x0, y0, x1, y1, rng, s=1.0):
    pts = []
    for t in np.linspace(0, 1, 9):
        pts.append((x0 + (x1 - x0) * t + math.sin(t * 9 + x0) * 30 * s, y0 + (y1 - y0) * t))
    L.line(pts, max(2, 4 * s), hexc("#3f6a32"), smooth=True)
    for k, (x, y) in enumerate(pts[1:-1]):
        leaf(L, x, y, (k % 2) * math.pi + rng.uniform(-0.6, 0.6), s)
        if k % 2 == 0:
            L.ellipse((x + 10 * s, y - 8 * s), (4 * s, 4 * s), C["gold"], lw=1)


def peacock(L, x, y, s=1.0, flip=False):
    d = -1 if flip else 1
    for k in range(9):  # tail fan
        a = math.radians(200 + k * 12) if not flip else math.radians(-20 - k * 12)
        ex, ey = x - d * 20 * s + math.cos(a) * 110 * s, y + 30 * s + math.sin(a) * 60 * s
        L.line([(x - d * 10 * s, y + 20 * s), (ex, ey)], max(2, 4 * s), hexc("#2f6b47"))
        L.ellipse((ex, ey), (12 * s, 9 * s), hexc("#2f6b47"), lw=2)
        L.ellipse((ex, ey), (6 * s, 5 * s), hexc("#3f6fb5"), lw=1)
        L.ellipse((ex, ey), (2.5 * s, 2.5 * s), C["gold"], lw=0)
    L.ellipse((x, y + 10 * s), (34 * s, 20 * s), hexc("#2f5fa8"), lw=3)
    L.shape([(x + d * 18 * s, y + 4 * s), (x + d * 30 * s, y - 40 * s), (x + d * 40 * s, y - 40 * s),
             (x + d * 30 * s, y + 4 * s)], hexc("#2f5fa8"), lw=3)
    L.ellipse((x + d * 36 * s, y - 46 * s), (9 * s, 8 * s), hexc("#2f5fa8"), lw=2)
    L.shape([(x + d * 44 * s, y - 48 * s), (x + d * 54 * s, y - 45 * s), (x + d * 44 * s, y - 42 * s)], C["gold"], lw=1)
    for j in range(3):
        L.line([(x + d * 34 * s, y - 54 * s), (x + d * (28 + j * 5) * s, y - 68 * s)], 1)
    L.ellipse((x + d * 38 * s, y - 48 * s), (2 * s, 2 * s), INK, lw=0)
    L.shape([(x - d * 4 * s, y + 6 * s), (x + d * 20 * s, y + 4 * s), (x, y + 22 * s)], hexc("#c9862a"), lw=2)


def sun(L, x, y, r):
    for k in range(16):
        a = k / 16 * math.tau
        L.shape([(x + math.cos(a - 0.12) * r, y + math.sin(a - 0.12) * r),
                 (x + math.cos(a) * r * 1.5, y + math.sin(a) * r * 1.5),
                 (x + math.cos(a + 0.12) * r, y + math.sin(a + 0.12) * r)], C["saffron"], lw=2)
    L.ellipse((x, y), (r, r), C["gold"], lw=3)
    L.ellipse((x - r * 0.3, y - r * 0.15), (r * 0.12, r * 0.08), INK, lw=0)
    L.ellipse((x + r * 0.3, y - r * 0.15), (r * 0.12, r * 0.08), INK, lw=0)
    L.arc((x, y + r * 0.1), (r * 0.35, r * 0.25), 20, 160, w=3)


def moon(L, x, y, r):
    L.ellipse((x, y), (r * 1.5, r * 1.5), hexc("#2f4f9a"), lw=3)
    L.ellipse((x, y), (r, r), hexc("#f6ecd6"), lw=2)
    L.ellipse((x + r * 0.4, y - r * 0.2), (r * 0.9, r * 0.9), hexc("#2f4f9a"), lw=0)
    for k in range(5):
        a = k * 1.3
        L.ellipse((x + math.cos(a) * r * 1.25, y + math.sin(a) * r * 1.25), (3, 3), hexc("#f6ecd6"), lw=0)


def folk_panel(w, h, seed=3, base="#f3e6cc"):
    """Dense lotus-vine field with peacocks, like a pattachitra / folk painting ground."""
    rng = np.random.default_rng(seed)
    L = Layer(w, h)
    L.paint(np.ones((h, w), np.float32), hexc(base))
    for x in range(-40, w + 60, 120):
        vine(L, x, -20, x + rng.uniform(-40, 40), h + 20, rng, s=1.1)
    for j, y in enumerate(range(40, h, 140)):
        for x in range(30 + (j % 2) * 60, w, 120):
            lotus(L, x + rng.uniform(-15, 15), y + rng.uniform(-15, 15), rng.uniform(0.8, 1.2),
                  col=["#e2563e", "#d8452b", "#f07a8a"][rng.integers(0, 3)])
    return L


def border_band(L, x0, y0, x1, y1, horizontal=True):
    """Fish / elephant-like alternating cartouches in a red-cream band."""
    L.shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], hexc("#f3e6cc"), lw=3)
    n = int((x1 - x0) / 90) if horizontal else int((y1 - y0) / 90)
    for k in range(max(1, n)):
        if horizontal:
            cx, cy = x0 + (k + 0.5) * (x1 - x0) / n, (y0 + y1) / 2
        else:
            cx, cy = (x0 + x1) / 2, y0 + (k + 0.5) * (y1 - y0) / n
        if k % 2 == 0:
            L.ellipse((cx, cy), (26, 13), hexc("#8a8f96"), lw=2)                    # fish
            L.shape([(cx + 24, cy), (cx + 38, cy - 10), (cx + 38, cy + 10)], hexc("#8a8f96"), lw=2)
            L.ellipse((cx - 14, cy - 3), (2.5, 2.5), INK, lw=0)
            for j in range(3):
                L.arc((cx - 4 + j * 9, cy), (6, 9), -60, 60, w=1)
        else:
            L.shape([(cx - 16, cy - 16), (cx + 16, cy - 16), (cx + 16, cy + 16), (cx - 16, cy + 16)], C["red"], lw=2)
            L.ellipse((cx, cy), (9, 9), hexc("#f3e6cc"), lw=2)
            L.ellipse((cx, cy), (3, 3), C["red"], lw=0)


def chalchitra_rich(r):
    """Multi-band painted halo: scallops, tiny deity medallions, lotus band, vine band, gold dots."""
    S = int(r * 2 + 60)
    L = Layer(S, int(r + 60))
    c = (S / 2, r + 30)
    L.ellipse(c, (r, r), C["gold"], lw=3)
    for k in range(56):                                   # outer scallop beads
        a = math.pi + (k + 0.5) / 56 * math.pi
        L.ellipse((c[0] + math.cos(a) * (r + 8), c[1] + math.sin(a) * (r + 8)), (11, 11), C["red"], lw=2)
    L.ellipse(c, (r - 18, r - 18), C["red"], lw=3)
    for k in range(24):                                   # medallions with little crowned faces
        a = math.pi + (k + 0.5) / 24 * math.pi
        x, y = c[0] + math.cos(a) * (r - 46), c[1] + math.sin(a) * (r - 46)
        L.ellipse((x, y), (19, 19), C["cream"], lw=2)
        L.ellipse((x, y + 3), (9, 10), hexc("#f3c98b"), lw=1)
        L.shape([(x - 9, y - 6), (x - 6, y - 16), (x, y - 12), (x + 6, y - 16), (x + 9, y - 6)], C["gold"], lw=1)
        L.ellipse((x, y + 3), (1.5, 1.5), INK, lw=0)
    L.ellipse(c, (r - 76, r - 76), C["cream"], lw=3)
    for k in range(40):                                   # lotus petal band
        a = math.pi + (k + 0.5) / 40 * math.pi
        L.ellipse((c[0] + math.cos(a) * (r - 92), c[1] + math.sin(a) * (r - 92)), (7, 14), C["pink"],
                  ang=math.degrees(a) + 90, lw=2)
    L.ellipse(c, (r - 110, r - 110), C["teal"], lw=3)
    for k in range(60):                                   # vine scroll band
        a = math.pi + (k + 0.5) / 60 * math.pi
        L.ellipse((c[0] + math.cos(a) * (r - 124), c[1] + math.sin(a) * (r - 124)), (5, 3), hexc("#bfe0c4"),
                  ang=math.degrees(a), lw=1)
    L.ellipse(c, (r - 140, r - 140), C["maroon"], lw=3)
    for k in range(30):
        a = math.pi + (k + 0.5) / 30 * math.pi
        L.ellipse((c[0] + math.cos(a) * (r - 156), c[1] + math.sin(a) * (r - 156)), (4, 4), C["gold"], lw=0)
    L.a[int(c[1]):, :] = 0
    L.rgb[int(c[1]):, :] = 0
    return L.rgba()


def sanctum_backdrop(w, h, seed=5):
    """Dark-red sanctum wall covered in gold lotus-vine stencil + peacocks, sun and moon."""
    L = folk_panel(w, h, seed, base="#5a1e1c")
    tint = Layer(w, h)
    tint.paint(np.ones((h, w), np.float32), hexc("#5a1e1c"))
    L.rgb = L.rgb * 0.55 + tint.rgb * 0.45
    peacock(L, 150, 330, 1.0)
    peacock(L, w - 150, 330, 1.0, flip=True)
    sun(L, 110, 110, 46)
    moon(L, w - 110, 110, 40)
    return L


# ------------------------------------------------------------------------------------- pandal pieces
def string_lights(L, y, sag, n=30, seed=1, x0=0, x1=None):
    x1 = W if x1 is None else x1
    pts = [(x0 + (x1 - x0) * t, y + sag * math.sin(t * math.pi)) for t in np.linspace(0, 1, n)]
    L.line(pts, 2)
    return pts


def loudspeaker(L, x, y, s=1.0, d=1):
    L.shape([(x, y - 14 * s), (x + d * 70 * s, y - 34 * s), (x + d * 70 * s, y + 34 * s), (x, y + 14 * s)],
            hexc("#c9ccd1"), lw=3)
    L.ellipse((x + d * 70 * s, y), (10 * s, 34 * s), hexc("#8a8f96"), lw=3)
    L.shape([(x - d * 16 * s, y - 12 * s), (x, y - 12 * s), (x, y + 12 * s), (x - d * 16 * s, y + 12 * s)],
            hexc("#5a5f66"), lw=2)


def bamboo(L, x, y0, y1, w=18):
    L.shape([(x - w / 2, y0), (x + w / 2, y0), (x + w / 2, y1), (x - w / 2, y1)], hexc("#d9b26a"), lw=3)
    for y in range(int(y0) + 60, int(y1), 90):
        L.line([(x - w / 2, y), (x + w / 2, y)], 3)


def pandal_1985():
    L = Layer(W, H)
    sky = np.linspace(0, 1, H, dtype=np.float32)[:, None] * np.ones((1, W), np.float32)
    L.paint(np.ones((H, W), np.float32), hexc("#f5c48a"))
    L.paint(np.clip(1 - sky * 3, 0, 1), hexc("#f0946a"))
    # neighbourhood houses at the sides
    for x0, x1, col in ((0, 140, "#e8d4b0"), (940, W, "#d9c39a")):
        L.shape([(x0, 220), (x1, 220), (x1, 1200), (x0, 1200)], hexc(col), lw=3)
        for y in range(280, 1150, 160):
            L.shape([(x0 + 30, y), (x1 - 30, y), (x1 - 30, y + 100), (x0 + 30, y + 100)], C["green"], lw=3,
                    pattern=pat_stripes(C["dgreen"], 14, 5, math.pi / 2))
    # cloth pandal: striped facade + pagoda roof with fringe
    L.shape([(100, 420), (980, 420), (980, 1190), (100, 1190)], C["red"], lw=4,
            pattern=pat_stripes(hexc("#f6ecd6"), 64, 30, math.pi / 2))
    L.shape([(60, 430), (540, 170), (1020, 430)], C["saffron"], lw=4, pattern=pat_stripes(C["red"], 40, 16, 0.6))
    L.shape([(240, 300), (540, 120), (840, 300)], C["gold"], lw=4)
    L.ellipse((540, 116), (22, 22), C["red"], lw=3)
    for x in range(70, 1020, 36):  # jhalar fringe
        L.shape([(x, 426), (x + 36, 426), (x + 18, 462)], C["gold"] if (x // 36) % 2 else C["teal"], lw=2)
    # entrance arch opening
    L.shape([(220, 720), (860, 720), (860, 1190), (220, 1190)], hexc("#3a1a18"), lw=4)
    L.ellipse((540, 720), (320, 120), hexc("#3a1a18"), lw=4)
    L.shape([(222, 720), (858, 720), (858, 740), (222, 740)], hexc("#3a1a18"), lw=0)
    # banner
    L.shape([(170, 480), (910, 480), (910, 580), (170, 580)], hexc("#fbf7ee"), lw=4)
    for x in (130, 950):
        bamboo(L, x, 300, 1200)
        loudspeaker(L, x + (14 if x < 500 else -14), 330, 0.9, d=-1 if x < 500 else 1)
    L.shape([(0, 1190), (W, 1190), (W, H), (0, H)], hexc("#b9a184"), lw=3,
            pattern=pat_dots(hexc("#a58c70"), 36, 3))
    return L


def theme_pandal_2000s():
    L = Layer(W, H)
    L.paint(np.ones((H, W), np.float32), hexc("#1d2350"))
    rng = np.random.default_rng(7)
    for _ in range(140):
        L.ellipse((rng.uniform(0, W), rng.uniform(0, 700)), (2, 2), hexc("#f6ecd6"), lw=0)
    L.ellipse((880, 170), (60, 60), hexc("#f6ecd6"), lw=3)
    # terracotta-temple theme facade: stacked curved roofs (bangla chala) with relief tiles
    tc, tc2 = hexc("#c4643a"), hexc("#a24e2c")
    for k, (y, w) in enumerate(((300, 360), (430, 460), (570, 560))):
        L.shape([(540 - w, y + 120), (540 - w * 0.9, y + 30), (540, y - 30), (540 + w * 0.9, y + 30),
                 (540 + w, y + 120)], tc, lw=4, smooth=True)
        for j in range(-6, 7):
            L.ellipse((540 + j * w / 7.2, y + 70 - abs(j) * 4), (14, 12), tc2, lw=2)
    L.shape([(60, 680), (1020, 680), (1020, 1200), (60, 1200)], tc, lw=4)
    for y in range(700, 1190, 64):          # relief tile panels
        for x in range(80, 1010, 64):
            if 250 < x < 830 and y > 760:
                continue
            L.shape([(x, y), (x + 56, y), (x + 56, y + 56), (x, y + 56)], tc2, lw=2)
            L.ellipse((x + 28, y + 30), (12, 16), tc, lw=2)
            L.ellipse((x + 28, y + 18), (6, 6), hexc("#e08a5a"), lw=1)
    L.shape([(250, 760), (830, 760), (830, 1200), (250, 1200)], hexc("#2a1210"), lw=4)
    L.ellipse((540, 760), (290, 120), hexc("#2a1210"), lw=4)
    L.shape([(252, 760), (828, 760), (828, 780), (252, 780)], hexc("#2a1210"), lw=0)
    L.shape([(0, 1200), (W, 1200), (W, H), (0, H)], hexc("#3a3550"), lw=3)
    return L


def skyline(L, kind, x0, y0, x1, y1, sky, ground):
    L.shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], hexc(sky), lw=3)
    base = y1 - 120
    sil = hexc("#5a4a6a")
    if kind == "london":
        L.shape([(x0 + 60, base), (x0 + 60, y0 + 90), (x0 + 80, y0 + 60), (x0 + 100, y0 + 90), (x0 + 100, base)], sil, lw=3)
        L.ellipse((x0 + 80, y0 + 120), (14, 14), hexc("#f6ecd6"), lw=2)
        L.shape([(x0 + 160, base), (x0 + 160, base - 90), (x0 + 330, base - 90), (x0 + 330, base)], sil, lw=3)
        L.shape([(x0 + 360, base - 40), (x0 + 470, base - 40), (x0 + 470, base), (x0 + 360, base)], C["red"], lw=3)
        for k in range(3):
            L.shape([(x0 + 368 + k * 34, base - 34), (x0 + 392 + k * 34, base - 34), (x0 + 392 + k * 34, base - 16),
                     (x0 + 368 + k * 34, base - 16)], hexc("#f6ecd6"), lw=2)
    elif kind == "newyork":
        for k, (w, h) in enumerate(((60, 160), (80, 230), (50, 120), (70, 260), (60, 180), (90, 140))):
            x = x0 + 30 + k * 85
            L.shape([(x, base), (x, base - h), (x + w, base - h), (x + w, base)], sil, lw=3,
                    pattern=pat_dots(hexc("#f2c14e"), 16, 2.2))
        L.shape([(x0 + 300, base - 260), (x0 + 310, base - 330), (x0 + 320, base - 260)], sil, lw=3)
    elif kind == "toronto":
        L.shape([(x0 + 200, base), (x0 + 210, y0 + 60), (x0 + 220, base)], sil, lw=3)
        L.ellipse((x0 + 210, y0 + 150), (26, 14), sil, lw=3)
        for k, (w, h) in enumerate(((70, 120), (60, 170), (80, 140), (60, 100))):
            x = x0 + 300 + k * 90
            L.shape([(x, base), (x, base - h), (x + w, base - h), (x + w, base)], sil, lw=3)
    elif kind == "sydney":
        for k in range(4):
            x = x0 + 120 + k * 70
            L.shape([(x, base), (x + 20, base - 70 - k * 20), (x + 80, base)], hexc("#fbf7ee"), lw=3, smooth=False)
        L.shape([(x0, base + 10), (x1, base + 10), (x1, base + 40), (x0, base + 40)], hexc("#3f6fb5"), lw=3)
    L.shape([(x0, base), (x1, base), (x1, y1), (x0, y1)], hexc(ground), lw=3)


def kumartuli(L, y0, y1):
    L.shape([(0, y0), (W, y0), (W, y1), (0, y1)], hexc("#d9c39a"), lw=3)
    L.shape([(0, y0), (W, y0), (W, y0 + 60), (0, y0 + 60)], hexc("#8a5a2a"), lw=3,
            pattern=pat_stripes(hexc("#6a4420"), 30, 10, math.pi / 2))
    for k, x in enumerate((110, 300)):     # unpainted clay idols (straw + clay)
        L.shape([(x - 60, y1 - 30), (x - 40, y0 + 160), (x + 40, y0 + 160), (x + 60, y1 - 30)], hexc("#b08a5a"), lw=3)
        L.ellipse((x, y0 + 130), (34, 40), hexc("#b08a5a"), lw=3)
        for j in range(4):
            L.line([(x - 30, y0 + 120 + j * 8), (x - 80 - j * 10, y0 + 90 + j * 22)], 3, hexc("#b08a5a"))
            L.line([(x + 30, y0 + 120 + j * 8), (x + 80 + j * 10, y0 + 90 + j * 22)], 3, hexc("#b08a5a"))
    for k, (x, lab) in enumerate(((470, "LONDON"), (650, "NEW YORK"), (830, "TORONTO"), (1000, "SYDNEY"))):
        y = y1 - 30 - (k % 2) * 40
        L.shape([(x - 80, y - 120), (x + 70, y - 120), (x + 70, y), (x - 80, y)], hexc("#c9a46a"), lw=3,
                pattern=pat_stripes(hexc("#a8844a"), 30, 4, 0.0))
        L.line([(x - 80, y - 120), (x + 70, y)], 2, hexc("#8a6a3a"))
        L.line([(x + 70, y - 120), (x - 80, y)], 2, hexc("#8a6a3a"))
    return [(470, "LONDON"), (650, "NEW YORK"), (830, "TORONTO"), (1000, "SYDNEY")]


def barricade(L, y, x0=0, x1=None):
    x1 = W if x1 is None else x1
    L.shape([(x0, y), (x1, y), (x1, y + 34), (x0, y + 34)], hexc("#f2c14e"), lw=3,
            pattern=pat_stripes(hexc("#2a2420"), 60, 24, 0.8))
    for x in np.linspace(x0 + 40, x1 - 40, 6):
        L.shape([(x - 8, y + 34), (x + 8, y + 34), (x + 8, y + 160), (x - 8, y + 160)], hexc("#d9d4cc"), lw=3)


def phone(L, x, y, w, h):
    L.shape([(x - w / 2 - 14, y - h / 2 - 30), (x + w / 2 + 14, y - h / 2 - 30), (x + w / 2 + 14, y + h / 2 + 40),
             (x - w / 2 - 14, y + h / 2 + 40)], hexc("#22252e"), lw=4)
    L.ellipse((x, y + h / 2 + 18), (12, 12), hexc("#3a3f4a"), lw=2)
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)


def seal(r):
    S = int(r * 2.6)
    L = Layer(S, S)
    c = (S / 2, S / 2)
    for k in range(36):
        a = k / 36 * math.tau
        L.ellipse((c[0] + math.cos(a) * r * 1.12, c[1] + math.sin(a) * r * 1.12), (r * 0.09, r * 0.05),
                  hexc("#3f7a3a"), ang=math.degrees(a) + 90, lw=2)
    L.ellipse(c, (r, r), hexc("#f6ecd6"), lw=4)
    L.ellipse(c, (r * 0.86, r * 0.86), None, lw=3, ink=C["red"])
    L.ellipse(c, (r * 0.56, r * 0.56), C["red"], lw=3)
    for k in range(8):
        a = k / 8 * math.tau
        L.ellipse((c[0] + math.cos(a) * r * 0.3, c[1] + math.sin(a) * r * 0.3), (r * 0.08, r * 0.2), C["gold"],
                  ang=math.degrees(a) + 90, lw=2)
    L.ellipse(c, (r * 0.12, r * 0.12), C["gold"], lw=2)
    return L.rgba(), c


def ghat(L, y0):
    for k in range(5):                    # river ghat steps
        y = y0 + k * 34
        L.shape([(0, y), (W, y), (W, y + 34), (0, y + 34)], hexc("#d9c8aa") if k % 2 else hexc("#c9b69a"), lw=3)
    L.shape([(0, y0 + 170), (W, y0 + 170), (W, H), (0, H)], hexc("#3f6fb5"), lw=3)
