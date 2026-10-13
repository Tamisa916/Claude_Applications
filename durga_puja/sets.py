"""Set pieces: thakur-dalan facade, ek-chala protima, garlands, floors."""
import math
import numpy as np
import cv2
from flat import Layer, hexc, mix, INK, pat_checks, pat_dots, pat_stripes, pat_buti
from figures import Fig, head, woman, man, _c, SKINS

W, H = 1920, 1080
C = {k: hexc(v) for k, v in dict(
    wall="#f3ead8", white="#fbf7ee", blue="#3f6fb5", lblue="#9cc0e4", orange="#e2672b", saffron="#f08a24",
    gold="#e7b23a", red="#c8281e", vermilion="#d8452b", green="#2f6b47", dgreen="#1f4a33", teal="#2f7a6e",
    pink="#e3567e", cream="#f6ecd6", maroon="#7a1f22", interior="#4a2c26", marigold="#f5a623").items()}


# ----------------------------------------------------------------------------------------- facade
def column(L, x, y0, y1, w=46):
    L.shape([(x - w / 2, y0), (x + w / 2, y0), (x + w / 2, y1), (x - w / 2, y1)], C["white"], lw=3)
    for dx in (-w / 4, 0, w / 4):
        L.line([(x + dx, y0 + 30), (x + dx, y1 - 30)], 2, mix(C["blue"], C["white"], 0.3))
    for yy, hh in ((y0, 34), (y1 - 34, 34)):  # capital & base
        L.shape([(x - w / 2 - 10, yy), (x + w / 2 + 10, yy), (x + w / 2 + 10, yy + hh), (x - w / 2 - 10, yy + hh)],
                C["orange"], lw=3)
        L.shape([(x - w / 2 - 4, yy + 8), (x + w / 2 + 4, yy + 8), (x + w / 2 + 4, yy + hh - 8),
                 (x - w / 2 - 4, yy + hh - 8)], C["blue"], lw=2)


def window(L, cx, top, w=300, h=280):
    x0, x1 = cx - w / 2, cx + w / 2
    L.shape([(x0 - 18, top + w / 2 - 10), (x1 + 18, top + w / 2 - 10), (x1 + 18, top + h + 20),
             (x0 - 18, top + h + 20)], C["blue"], lw=3)
    L.ellipse((cx, top + w / 2), (w / 2 + 18, w / 2 + 18), C["blue"], lw=3)
    L.ellipse((cx, top + w / 2), (w / 2, w / 2), C["dgreen"], lw=3)
    L.shape([(x0, top + w / 2), (x1, top + w / 2), (x1, top + h), (x0, top + h)], C["green"], lw=3,
            pattern=pat_stripes(C["dgreen"], step=16, w=6, ang=math.pi / 2))
    L.line([(cx, top + w / 2), (cx, top + h)], 3)
    m = L.mell((cx, top + w / 2), (w / 2 - 6, w / 2 - 6), 0, 180, 360)
    L.paint(m, C["gold"])
    for k in range(9):  # fanlight spokes
        a = math.pi + k / 8 * math.pi
        L.line([(cx, top + w / 2), (cx + math.cos(a) * (w / 2 - 6), top + w / 2 + math.sin(a) * (w / 2 - 6))], 3)
    L.ellipse((cx, top + w / 2), (26, 26), C["orange"], lw=3)
    L.shape([(x0 - 24, top + h + 12), (x1 + 24, top + h + 12), (x1 + 24, top + h + 30), (x0 - 24, top + h + 30)],
            C["white"], lw=3)


def cornice(L, y0=0, y1=110):
    L.shape([(0, y0), (W, y0), (W, y1), (0, y1)], C["white"], lw=0)
    for x in range(-60, W + 120, 120):  # scalloped arches row
        L.ellipse((x + 60, y1 - 10), (56, 56), C["orange"], lw=3)
        L.ellipse((x + 60, y1 - 10), (40, 40), C["white"], lw=3)
        L.ellipse((x + 60, y1 - 10), (24, 24), C["lblue"], lw=2)
    L.shape([(0, y1 - 10), (W, y1 - 10), (W, y1 + 16), (0, y1 + 16)], C["blue"], lw=3)
    for x in range(10, W, 40):
        L.ellipse((x, y1 + 3), (6, 6), C["white"], lw=0)
    for x in range(0, W + 60, 60):  # leaf scroll at the very top
        L.ellipse((x, y0 + 22), (22, 12), C["lblue"], ang=25, lw=2)


def thakur_dalan():
    L = Layer(W, H)
    L.paint(np.ones((H, W), np.float32), C["wall"])
    # wall paper motif
    L.shape([(0, 120), (W, 120), (W, 610), (0, 610)], C["wall"], lw=0,
            pattern=pat_buti(mix(C["wall"], C["orange"], 0.25), None, step=46, r=6))
    cornice(L)
    window(L, 265, 170)
    window(L, W - 265, 170)
    # central arch opening (dark sanctum)
    cx, spring, r = W / 2, 330, 300
    L.shape([(cx - r - 46, spring), (cx + r + 46, spring), (cx + r + 46, 612), (cx - r - 46, 612)], C["orange"], lw=3)
    for rr, col in ((r + 46, C["orange"]), (r + 30, C["blue"]), (r + 16, C["white"])):
        L.ellipse((cx, spring), (rr, rr), col, lw=3)
    for k in range(25):  # scallops around the arch
        a = math.pi + k / 24 * math.pi
        L.ellipse((cx + math.cos(a) * (r + 38), spring + math.sin(a) * (r + 38)), (9, 9), C["gold"], lw=2)
    L.ellipse((cx, spring), (r, r), C["interior"], lw=3)
    L.shape([(cx - r, spring), (cx + r, spring), (cx + r, 612), (cx - r, 612)], C["interior"], lw=0)
    L.line([(cx - r, spring), (cx - r, 612)], 3)
    L.line([(cx + r, spring), (cx + r, 612)], 3)
    L.shape([(cx - 46, spring - r - 64), (cx, spring - r - 104), (cx + 46, spring - r - 64), (cx, spring - r - 30)],
            C["orange"], lw=3)
    for x in (70, 480, 580, W - 580, W - 480, W - 70):
        column(L, x, 150, 612)
    # dalan floor: black & white diamonds, then steps, then the red courtyard
    L.shape([(0, 612), (W, 612), (W, 712), (0, 712)], C["white"], lw=3,
            pattern=pat_checks(hexc("#2a2420"), hexc("#f4efe6"), step=34))
    for y, col in ((712, C["white"]), (736, mix(C["white"], C["wall"], 0.6))):
        L.shape([(0, y), (W, y), (W, y + 24), (0, y + 24)], col, lw=3)
    L.shape([(0, 760), (W, 760), (W, H), (0, H)], C["vermilion"], lw=3,
            pattern=pat_dots(mix(C["vermilion"], C["red"], 0.6), step=30, r=3))
    # alpana in the courtyard
    ax, ay = W / 2, 930
    for rr in (150, 115, 80):
        L.ellipse((ax, ay), (rr * 1.9, rr * 0.55), None, lw=4, ink=C["white"])
    for k in range(16):
        a = k / 16 * math.tau
        L.ellipse((ax + math.cos(a) * 230, ay + math.sin(a) * 66), (22, 9), C["white"], ang=math.degrees(a), lw=0)
    return L


def garland_swag(L, x0, x1, y, sag=60):
    pts = [(x0 + (x1 - x0) * t, y + sag * math.sin(t * math.pi)) for t in np.linspace(0, 1, 26)]
    for k, (x, yy) in enumerate(pts):
        L.ellipse((x, yy), (9, 9), C["marigold"] if k % 2 else C["saffron"], lw=2)
    for x in np.linspace(x0, x1, 7)[1:-1]:  # mango-leaf toran
        L.shape([(x - 8, y + 4), (x + 8, y + 4), (x, y + 44)], C["green"], lw=2, smooth=False)


# ----------------------------------------------------------------------------------------- protima
def _crown(F, x, top, w, col_main="#fbf7ee", col_gold="#e7b23a"):
    pts = [(x - w, top + 40), (x - w * 0.8, top + 6), (x - w * 0.45, top + 18), (x - w * 0.2, top - 20), (x, top - 44),
           (x + w * 0.2, top - 20), (x + w * 0.45, top + 18), (x + w * 0.8, top + 6), (x + w, top + 40)]
    F.shape(pts, col_main)
    for k in range(5):
        F.ell((x - w * 0.6 + k * w * 0.3, top + 24), (4, 4), col_gold, lw=1)
    F.ell((x, top - 6), (7, 9), "#c8281e")


def deity_woman(height, saree, border, skin="#f0b43c", attr=None):
    F = Fig(height)
    s = dict(saree=saree, border=border, blouse=border, skin=skin, hair="open", sindoor=False, bindi=True,
             arms="fold" if attr is None else "down", pattern="buti", pat_col=border, lips="#c8281e")
    woman(F, s)
    _crown(F, 0, -500, 34)
    if attr == "veena":
        F.shape([(-60, -230), (60, -380), (68, -370), (-52, -220)], "#9a5a2a")
        F.ell((-60, -228), (24, 24), "#c97a3a")
        F.ell((60, -380), (14, 14), "#c97a3a")
    if attr == "lotus":
        for k in range(5):
            F.ell((-40 + (k - 2) * 7, -250), (6, 14), "#f39ab4", ang=(k - 2) * 20, lw=1)
    return F.L.rgba()


def ganesh(height):
    F = Fig(height)
    man(F, dict(kurta="#f2c14e", dhoti="#e3567e", skin="#f2a37a", hair="bald", arms="down", pattern="dots",
                pat_col="#c8281e"))
    F.ell((0, -260), (52, 46), "#f2a37a")                         # belly
    for sg in (-1, 1):
        F.ell((sg * 44, -440), (32, 40), "#f2a37a")               # ears
    F.ell((0, -436), (36, 40), "#f2a37a")
    F.shape([(-8, -420), (8, -420), (12, -360), (24, -330), (14, -326), (0, -356), (-6, -410)], "#f2a37a")
    F.ell((-14, -446), (4, 3), "#2a1a14", lw=0)
    F.ell((14, -446), (4, 3), "#2a1a14", lw=0)
    F.shape([(14, -418), (30, -410), (16, -404)], "#fbf7ee")      # tusk
    _crown(F, 0, -500, 30)
    return F.L.rgba()


def kartik(height):
    F = Fig(height)
    man(F, dict(kurta="#3f6fb5", dhoti="#f2c14e", skin="#f0b43c", hair="short", mustache=True, arms="down",
                pattern="dots", pat_col="#f2c14e"))
    _crown(F, 0, -500, 30)
    F.L.arc((F.ox + 52 * F.k, F.oy - 300 * F.k), (16 * F.k, 90 * F.k), -90, 90, w=4 * F.k)  # bow
    return F.L.rgba()


def durga(height):
    F = Fig(height)
    gold = "#f0b43c"
    # ten arms fanning out behind the body
    for sg in (-1, 1):
        for j in range(5):
            a = math.radians(-160 + j * 26) if sg < 0 else math.radians(-20 - j * 26)
            sx, sy = sg * 34, -378
            ex, ey = sx + math.cos(a) * 150, sy + math.sin(a) * 120
            F.limb([(sx, sy), ((sx + ex) / 2, (sy + ey) / 2 - 10), (ex, ey)], 11, gold)
            F.ell((ex, ey), (7, 7), gold)
            wpn = j % 3
            if wpn == 0:
                F.shape([(ex - 3, ey - 40), (ex + 3, ey - 40), (ex + 3, ey + 10), (ex - 3, ey + 10)], "#d9d4cc")
            elif wpn == 1:
                F.ell((ex, ey - 16), (14, 14), "#e7b23a")
                F.ell((ex, ey - 16), (6, 6), "#c8281e", lw=1)
            else:
                F.ell((ex, ey - 14), (8, 16), "#f39ab4", lw=1)
    s = dict(saree="#c8281e", border="#e7b23a", blouse="#e7b23a", skin=gold, hair="open", bindi=False,
             third_eye=True, pattern="buti", pat_col="#e7b23a", arms="down", lips="#c8281e")
    woman(F, s)
    F.shape([(56, -300), (63, -302), (118, -60), (111, -58)], "#d9d4cc")   # trishul
    F.shape([(100, -86), (128, -98), (122, -70)], "#d9d4cc")
    _crown(F, 0, -520, 46)
    return F.L.rgba()


def lion(height):
    F = Fig(height)
    F.shape([(-110, -120), (60, -140), (110, -90), (100, -20), (-90, -20), (-120, -60)], "#e7b23a", smooth=True)
    F.ell((-110, -150), (54, 50), "#f08a24", pattern=None)
    F.ell((-114, -146), (34, 32), "#e7b23a")
    F.ell((-124, -154), (4, 4), "#2a1a14", lw=0)
    for x in (-80, -30, 40, 80):
        F.shape([(x - 12, -40), (x + 12, -40), (x + 12, 0), (x - 12, 0)], "#e7b23a")
    return F.L.rgba()


def chalchitra(r):
    """Semicircular painted halo behind the ek-chala protima."""
    S = int(r * 2 + 40)
    L = Layer(S, int(r + 40))
    c = (S / 2, r + 20)
    bands = [(r, C["gold"]), (r - 26, C["red"]), (r - 70, C["cream"]), (r - 96, C["gold"]), (r - 112, C["maroon"])]
    for rr, col in bands:
        L.ellipse(c, (rr, rr), col, lw=3)
    for k in range(30):
        a = math.pi + (k + 0.5) / 30 * math.pi
        L.ellipse((c[0] + math.cos(a) * (r - 48), c[1] + math.sin(a) * (r - 48)), (9, 14), C["pink"],
                  ang=math.degrees(a) + 90, lw=2)
    for k in range(48):
        a = math.pi + k / 47 * math.pi
        L.ellipse((c[0] + math.cos(a) * (r + 4), c[1] + math.sin(a) * (r + 4)), (8, 8), C["white"], lw=2)
    L.a[int(c[1]):, :] = 0
    L.rgb[int(c[1]):, :] = 0
    return L.rgba()
