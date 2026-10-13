"""Set pieces: thakur-dalan facade, ek-chala protima, garlands, floors."""
import math
import numpy as np
import cv2
from flat import Layer, hexc, mix, INK, pat_checks, pat_dots, pat_stripes, pat_buti
from figures import Fig, head, woman, man, _c, SKINS

from timing import W, H
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


# ----------------------------------------------------------------------------- Durga on the lion (folk style)
class Canvas(Fig):
    """Free canvas in design units (origin top-left), scaled to a pixel height."""

    def __init__(self, height, uw=610, uh=640):
        self.k = height / uh
        self.W, self.H = int(uw * self.k) + 8, int(uh * self.k) + 8
        self.ox, self.oy = 4, 4
        self.L = Layer(self.W, self.H)
        self.lw = max(1.4, 2.6 * self.k)


def _arm(F, sh, hand, skin, elbow_bend=18):
    mx, my = (sh[0] + hand[0]) / 2, (sh[1] + hand[1]) / 2
    nx, ny = -(hand[1] - sh[1]), hand[0] - sh[0]
    n = math.hypot(nx, ny) + 1e-6
    el = (mx + nx / n * elbow_bend, my + ny / n * elbow_bend)
    F.limb([sh, el, hand], 13, skin)
    for t in (0.78, 0.86):  # bangles
        bx, by = el[0] + (hand[0] - el[0]) * t, el[1] + (hand[1] - el[1]) * t
        F.ell((bx, by), (7, 7), "#e7b23a", lw=max(1, F.lw * 0.6))
    F.ell(hand, (8, 8), skin)


def durga_riding(height):
    F = Canvas(height)
    skin, gold, red, blue = "#f3c98b", "#e7b23a", "#c8281e", "#2f5fa8"
    # --- halo
    for k in range(28):
        a = k / 28 * math.tau
        F.ell((268 + math.cos(a) * 92, 150 + math.sin(a) * 92), (13, 13), red, lw=max(1, F.lw * 0.7))
    F.ell((268, 150), (90, 90), gold)
    F.ell((268, 150), (72, 72), "#f6d77a", lw=max(1, F.lw * 0.5))
    # --- buffalo with Mahishasura (lower right, behind the lion's head)
    F.ell((520, 586), (78, 44), "#6b6b70")
    for x in (470, 560):
        F.shape([(x - 10, 600), (x + 10, 600), (x + 10, 636), (x - 10, 636)], "#5a5a60")
    F.shape([(512, 470), (562, 470), (566, 560), (508, 560)], "#8a5536")                          # torso
    F.limb([(556, 480), (580, 430), (570, 372)], 14, "#8a5536")                                   # raised arm
    F.shape([(560, 352), (590, 342), (594, 366), (566, 372)], "#d9d4cc")                          # axe head
    F.ln([(572, 360), (568, 410)], 1.0, "#7a4a2a")
    F.ell((538, 446), (22, 26), "#8a5536")
    F.shape([(516, 436), (538, 416), (560, 436), (552, 424), (522, 424)], "#1d1512", smooth=True)
    F.shape([(524, 456), (538, 451), (552, 456), (538, 460)], "#1d1512", lw=0)                    # moustache
    F.ell((531, 444), (3, 2.5), INK, lw=0)
    F.ell((545, 444), (3, 2.5), INK, lw=0)
    F.ell((468, 582), (30, 26), "#6b6b70")                                                         # buffalo head
    F.shape([(446, 566), (414, 540), (424, 536), (456, 560)], "#2a2420")                          # horns
    F.shape([(490, 566), (522, 540), (512, 536), (480, 560)], "#2a2420")
    F.ell((468, 596), (14, 10), "#8a7f86")
    for sg in (-1, 1):
        F.ell((468 + sg * 12, 576), (3.5, 3), "#ffffff", lw=0)
    # --- lion (striding right), tail attached at the rump
    F.shape([(92, 470), (60, 420), (44, 340), (58, 300), (70, 320), (64, 360), (80, 420), (108, 462)],
            "#e9a63a", smooth=True)
    F.ell((58, 296), (14, 20), "#b5562c")
    for x in (118, 160):
        F.shape([(x - 15, 480), (x + 15, 480), (x + 12, 600), (x - 12, 600)], "#e9a63a")
        F.ell((x + 4, 604), (19, 9), "#e9a63a")
    F.shape([(86, 470), (140, 430), (290, 424), (370, 440), (392, 486), (372, 535), (310, 548), (140, 548),
             (90, 520)], "#e9a63a", smooth=True)
    F.ln([(150, 500), (300, 500)], 0.4, "#c9862a")
    for x in (330, 368):
        F.shape([(x - 15, 500), (x + 15, 500), (x + 12, 600), (x - 12, 600)], "#e9a63a")
        F.ell((x + 6, 604), (19, 9), "#e9a63a")
    mane = [(396 + math.cos(a) * (62 + 10 * (k % 2)), 418 + math.sin(a) * (66 + 10 * (k % 2)))
            for k, a in enumerate(np.linspace(0, math.tau, 26, endpoint=False))]
    F.shape(mane, "#b5562c")
    for a in np.linspace(0, math.tau, 18, endpoint=False):
        F.ln([(396 + math.cos(a) * 42, 418 + math.sin(a) * 44), (396 + math.cos(a) * 62, 418 + math.sin(a) * 66)],
             0.45, "#7a3216")
    F.ell((404, 422), (40, 40), "#f0b44a")                                                         # face
    F.ell((432, 444), (24, 18), "#f6cf7a")                                                         # muzzle
    F.shape([(420, 452), (446, 452), (440, 466), (424, 466)], "#c8281e")                           # open mouth
    F.shape([(430, 430), (444, 430), (437, 440)], "#5a2a1a")                                       # nose
    for ex in (392, 420):
        F.ell((ex, 410), (7, 5), "#ffffff")
        F.ell((ex + 2, 410), (3, 3.5), INK, lw=0)
        F.ln([(ex - 8, 400), (ex + 8, 398)], 0.5)
    # --- Durga: hair, ten arms, body, saree, head
    F.shape([(222, 150), (230, 120), (306, 120), (314, 150), (322, 300), (300, 340), (236, 340), (214, 300)],
            "#1d1512", smooth=True)
    arms = [((236, 262), (138, 96), "trident"), ((236, 266), (112, 158), "chakra"), ((236, 272), (104, 222), "sword"),
            ((236, 280), (120, 284), "conch"), ((236, 288), (150, 336), "lotus"),
            ((300, 262), (398, 96), "bow"), ((300, 266), (424, 160), "shield"), ((300, 272), (432, 226), "axe"),
            ((300, 280), (418, 290), "mace")]
    for sh, hand, wpn in arms:
        _arm(F, sh, hand, skin)
        x, y = hand
        if wpn == "trident":
            F.shape([(x - 3, y - 70), (x + 3, y - 70), (x + 3, y + 30), (x - 3, y + 30)], "#d9d4cc")
            F.ln([(x - 16, y - 92), (x - 14, y - 70), (x + 14, y - 70), (x + 16, y - 92)], 1.0, "#d9d4cc")
            F.ln([(x, y - 98), (x, y - 70)], 1.0, "#d9d4cc")
        elif wpn == "chakra":
            F.ell((x - 2, y - 22), (18, 18), gold)
            F.ell((x - 2, y - 22), (7, 7), red, lw=1)
        elif wpn == "sword":
            F.shape([(x - 4, y), (x + 4, y), (x - 30, y - 80), (x - 36, y - 76)], "#d9d4cc")
        elif wpn == "conch":
            F.shape([(x - 22, y - 10), (x + 4, y - 18), (x + 8, y - 4), (x - 18, y + 4)], "#fbf7ee", smooth=True)
        elif wpn == "lotus":
            for j in range(5):
                F.ell((x - 18 + j * 9, y - 18), (6, 15), "#f07a8a", ang=(j - 2) * 18, lw=1)
        elif wpn == "bow":
            F.L.arc((F.ox + (x + 6) * F.k, F.oy + y * F.k), (14 * F.k, 64 * F.k), -100, 100, w=max(2, 4 * F.k),
                    col=hexc("#9a5a2a"))
        elif wpn == "shield":
            F.ell((x + 6, y), (26, 26), "#1d1a1a")
            for a in np.linspace(0, math.tau, 4, endpoint=False):
                F.ell((x + 6 + math.cos(a) * 12, y + math.sin(a) * 12), (4, 4), gold, lw=1)
        elif wpn == "axe":
            F.ln([(x, y + 20), (x + 6, y - 50)], 1.2, "#7a4a2a")
            F.shape([(x + 2, y - 52), (x + 26, y - 62), (x + 22, y - 32)], "#d9d4cc")
        elif wpn == "mace":
            F.ln([(x, y + 10), (x + 10, y - 40)], 1.2, "#7a4a2a")
            F.ell((x + 12, y - 46), (12, 12), gold)
    # saree skirt draped over the lion's back, one foot forward
    F.shape([(232, 330), (304, 330), (330, 400), (352, 470), (300, 486), (200, 492), (168, 470), (196, 400)], red,
            smooth=False, pattern=_buti_gold(F))
    F.shape([(168, 466), (200, 488), (300, 482), (352, 466), (356, 480), (302, 500), (198, 506), (164, 482)], gold)
    for x in (240, 262, 284):
        F.ln([(x, 340), (x - 20 + (x - 262) * 0.6, 484)], 0.5)
    F.ell((322, 512), (16, 8), skin)                                                               # foot
    F.ell((322, 506), (16, 3), "#c8281e", lw=0)                                                    # alta
    F.shape([(234, 248), (302, 248), (306, 334), (230, 334)], blue)                                # blouse
    F.shape([(238, 252), (300, 252), (304, 334), (276, 334), (238, 272)], red)                     # pallu
    F.shape([(238, 252), (252, 252), (300, 326), (288, 334)], gold)
    for j in range(3):  # necklaces
        F.L.arc((F.ox + 268 * F.k, F.oy + 246 * F.k), ((24 + j * 9) * F.k, (16 + j * 9) * F.k), 10, 170,
                w=max(1.5, 3 * F.k), col=hexc(gold))
    _arm(F, (300, 284), (330, 300), skin, elbow_bend=-10)                                          # spear hand
    F.shape([(326, 292), (334, 288), (514, 486), (506, 492)], "#d9d4cc")                           # spear
    F.shape([(506, 486), (522, 482), (520, 504)], "#d9d4cc")
    F.shape([(256, 214), (280, 214), (282, 250), (254, 250)], skin)                                # neck
    F.ell((268, 172), (40, 50), skin)                                                               # face
    F.shape([(228, 150), (240, 126), (268, 118), (296, 126), (308, 150), (290, 138), (268, 134), (246, 138)],
            "#1d1512", smooth=True)                                                                 # hair line
    for sg in (-1, 1):  # big fish-shaped eyes, arched brows
        cx = 268 + sg * 17
        F.ln([(cx - 13, 154), (cx, 149), (cx + 13, 154)], 0.7, smooth=True)
        F.shape([(cx - 15, 166), (cx - 4, 159), (cx + 8, 160), (cx + 17, 165), (cx + 6, 171), (cx - 6, 171)],
                "#fbf7ee", smooth=True, lw=max(1, F.lw * 0.8))
        F.ell((cx + 3, 165), (5, 5.5), INK, lw=0)
        F.ln([(cx + sg * 15, 165), (cx + sg * 24, 162)], 0.7)
    F.ell((268, 147), (3, 7), "#c8281e", lw=max(1, F.lw * 0.5))                                    # third eye
    F.ln([(268, 170), (270, 188), (264, 190)], 0.5)
    F.L.arc((F.ox + 276 * F.k, F.oy + 190 * F.k), (7 * F.k, 7 * F.k), -40, 260, w=max(1.5, 2.5 * F.k),
            col=hexc(gold))                                                                         # nose ring
    F.shape([(256, 202), (268, 199), (280, 202), (268, 208)], "#c8281e", lw=max(1, F.lw * 0.5))     # lips
    for sg in (-1, 1):
        F.ell((268 + sg * 40, 190), (6, 10), gold, lw=max(1, F.lw * 0.6))                          # earrings
    # crown (mukut)
    crown = [(222, 136), (228, 96), (246, 90), (254, 60), (268, 36), (282, 60), (290, 90), (308, 96), (314, 136),
             (268, 124)]
    F.shape(crown, gold)
    for x, y in ((246, 112), (268, 92), (290, 112), (268, 64)):
        F.ell((x, y), (6, 7), "#c8281e", lw=1)
    for x in range(232, 306, 10):
        F.ell((x, 130), (3, 3), "#fbf7ee", lw=0)
    return F.L.rgba()


def _buti_gold(F):
    from flat import pat_buti
    return pat_buti(hexc("#e7b23a"), None, step=max(8, int(24 * F.k)), r=max(2, 4 * F.k))


# ----------------------------------------------------------------------------- Durga v3 (detailed, iconographic)
GOLD, GOLD_D, RED_, GREEN_ = "#e7b23a", "#b07a1a", "#c8281e", "#2f7a47"


def _bangles(F, a, b, n=3, col=GOLD):
    for j in range(n):
        t = 0.72 + j * 0.07
        F.ell((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), (7.5, 7.5), col if j % 2 == 0 else RED_,
              lw=max(1, F.lw * 0.6))


def _arm3(F, sh, hand, skin, bend=20):
    mx, my = (sh[0] + hand[0]) / 2, (sh[1] + hand[1]) / 2
    nx, ny = -(hand[1] - sh[1]), hand[0] - sh[0]
    n = math.hypot(nx, ny) + 1e-6
    el = (mx + nx / n * bend, my + ny / n * bend)
    F.limb([sh, el, hand], 15, skin)
    ax, ay = sh[0] + (el[0] - sh[0]) * 0.45, sh[1] + (el[1] - sh[1]) * 0.45
    F.ell((ax, ay), (9, 9), GOLD, lw=max(1, F.lw * 0.6))                   # armlet (bajuband)
    F.ell((ax, ay), (3.5, 3.5), RED_, lw=0)
    _bangles(F, el, hand)
    F.ell(hand, (10, 9), skin)                                             # closed hand
    F.ln([(hand[0] - 5, hand[1] - 3), (hand[0] + 5, hand[1] - 3)], 0.4)
    return el


def _weapon(F, kind, x, y):
    steel, wood = "#d9d4cc", "#8a5a2a"
    if kind == "khadga":       # sword
        F.shape([(x - 3, y + 14), (x + 3, y + 14), (x - 34, y - 96), (x - 42, y - 92), (x - 40, y - 80)], steel)
        F.shape([(x - 14, y - 4), (x + 12, y + 6), (x + 10, y + 12), (x - 16, y + 2)], GOLD)
    elif kind == "chakra":
        F.ell((x - 4, y - 26), (22, 22), GOLD)
        F.ell((x - 4, y - 26), (13, 13), RED_, lw=max(1, F.lw * 0.6))
        for a in np.linspace(0, math.tau, 8, endpoint=False):
            F.ln([(x - 4, y - 26), (x - 4 + math.cos(a) * 20, y - 26 + math.sin(a) * 20)], 0.4)
            F.ell((x - 4 + math.cos(a) * 26, y - 26 + math.sin(a) * 26), (4, 4), GOLD, lw=1)
    elif kind == "baan":       # arrow
        F.ln([(x + 10, y + 30), (x - 40, y - 70)], 1.0, wood)
        F.shape([(x - 40, y - 70), (x - 52, y - 86), (x - 34, y - 78)], steel)
        F.shape([(x + 10, y + 30), (x + 18, y + 44), (x + 4, y + 36)], RED_)
    elif kind == "shakti":     # lance with leaf blade
        F.ln([(x + 6, y + 40), (x - 30, y - 80)], 1.1, wood)
        F.shape([(x - 30, y - 80), (x - 44, y - 104), (x - 32, y - 120), (x - 22, y - 100)], steel)
    elif kind == "khetak":     # shield
        F.ell((x + 10, y - 6), (32, 32), "#2a2420")
        F.ell((x + 10, y - 6), (24, 24), None, lw=max(1, F.lw * 0.6), ink=hexc(GOLD))
        for a in np.linspace(0, math.tau, 4, endpoint=False):
            F.ell((x + 10 + math.cos(a + 0.8) * 13, y - 6 + math.sin(a + 0.8) * 13), (5, 5), GOLD, lw=1)
        F.ell((x + 10, y - 6), (6, 6), GOLD, lw=1)
    elif kind == "dhanu":      # bow with string
        F.L.arc((F.ox + (x + 4) * F.k, F.oy + y * F.k), (18 * F.k, 78 * F.k), -95, 95, w=max(2, 5 * F.k),
                col=hexc("#9a5a2a"))
        F.ln([(x + 4, y - 78), (x + 4, y + 78)], 0.3, "#f6ecd6")
    elif kind == "pash":       # noose / lasso
        F.L.arc((F.ox + (x + 26) * F.k, F.oy + (y - 30) * F.k), (22 * F.k, 22 * F.k), 0, 360, w=max(2, 4 * F.k),
                col=hexc("#c9862a"))
        F.ln([(x, y), (x + 14, y - 14)], 0.8, "#c9862a")
    elif kind == "ankush":     # elephant goad
        F.ln([(x - 2, y + 30), (x + 18, y - 70)], 1.1, wood)
        F.shape([(x + 18, y - 70), (x + 26, y - 96), (x + 22, y - 72)], steel)
        F.L.arc((F.ox + (x + 8) * F.k, F.oy + (y - 76) * F.k), (10 * F.k, 10 * F.k), -60, 160, w=max(2, 4 * F.k),
                col=hexc(steel))


def _lion3(F):
    body, mane1, mane2, mane3 = "#e9a63a", "#8a3a16", "#b5562c", "#d9772e"
    # tail rising from the rump with a tuft
    F.shape([(118, 520), (80, 470), (58, 390), (66, 330), (84, 342), (78, 392), (96, 458), (134, 506)], body,
            smooth=True)
    F.ell((70, 322), (16, 24), mane2)
    # back legs
    for x in (140, 186):
        F.shape([(x - 17, 540), (x + 17, 540), (x + 14, 690), (x - 14, 690)], body)
        F.ell((x + 4, 694), (22, 10), body)
        for c in (-8, 0, 8):
            F.ln([(x + 4 + c, 690), (x + 4 + c, 702)], 0.4)
    F.shape([(110, 530), (170, 488), (330, 478), (420, 492), (448, 540), (430, 600), (360, 616), (170, 616),
             (114, 584)], body, smooth=True)
    for t in np.linspace(0.15, 0.85, 6):  # body fur strokes
        x = 150 + 260 * t
        F.ln([(x, 560), (x + 14, 590)], 0.35, "#c9862a")
    # front legs (one raised paw toward the buffalo)
    F.shape([(392, 560), (424, 560), (420, 690), (392, 690)], body)
    F.ell((410, 694), (22, 10), body)
    F.limb([(430, 570), (500, 650), (548, 662)], 26, body)
    F.ell((554, 664), (16, 14), body)
    for c in (-6, 2, 10):
        F.shape([(558 + c, 652), (568 + c, 656), (560 + c, 660)], "#fbf7ee", lw=1)       # claws
    # mane in three layers of tufts
    hx, hy = 486, 588
    for R, col, n in ((92, mane1, 22), (76, mane2, 20), (60, mane3, 18)):
        pts = [(hx + math.cos(a) * (R + 12 * (k % 2)), hy + math.sin(a) * (R * 0.95 + 12 * (k % 2)))
               for k, a in enumerate(np.linspace(0, math.tau, n * 2, endpoint=False))]
        F.shape(pts, col)
    F.ell((hx + 8, hy + 4), (46, 44), "#f0b44a")                       # face
    F.ell((hx + 36, hy + 26), (28, 20), "#f8d48a")                     # muzzle
    F.shape([(hx + 18, hy + 34), (hx + 58, hy + 32), (hx + 52, hy + 58), (hx + 22, hy + 56)], "#b51e1a")  # roar
    for c in (24, 36, 48):
        F.shape([(hx + c, hy + 34), (hx + c + 6, hy + 34), (hx + c + 3, hy + 42)], "#fbf7ee", lw=1)        # teeth
    F.shape([(hx + 36, hy + 10), (hx + 54, hy + 10), (hx + 45, hy + 22)], "#5a2a1a")                 # nose
    for sg in (-1, 1):
        for j in range(3):  # whiskers
            F.ln([(hx + 40 + sg * 10, hy + 22 + j * 4), (hx + 40 + sg * 40, hy + 14 + j * 8)], 0.3)
    for ex in (hx - 6, hx + 24):
        F.shape([(ex - 10, hy - 10), (ex + 10, hy - 12), (ex + 8, hy - 2), (ex - 8, hy - 2)], "#ffffff",
                lw=max(1, F.lw * 0.6))
        F.ell((ex + 2, hy - 6), (4, 4), INK, lw=0)
        F.ln([(ex - 12, hy - 20), (ex + 10, hy - 24)], 0.6)
    F.ell((hx - 30, hy - 40), (12, 14), "#f0b44a")                     # ears
    F.ell((hx + 40, hy - 44), (12, 14), "#f0b44a")


def _buffalo_asura(F):
    """Water buffalo (mahish) kneeling at lower right, Mahishasura mounted on it."""
    hide, horn, skin = "#3c3b40", "#e8dcc4", "#5e8a5a"
    F.ell((640, 690), (110, 64), hide)                                 # body
    for x in (570, 690):
        F.shape([(x - 14, 700), (x + 14, 700), (x + 12, 752), (x - 12, 752)], hide)
        F.shape([(x - 14, 748), (x + 12, 748), (x + 10, 760), (x - 12, 760)], "#1d1a1a")   # hooves
    F.shape([(740, 660), (752, 610), (758, 622), (746, 672)], hide)    # tail
    # head low and forward, big swept-back horns
    hx, hy = 556, 716
    F.shape([(hx - 6, hy - 20), (hx - 70, hy - 54), (hx - 100, hy - 40), (hx - 76, hy - 32), (hx - 30, hy - 8)], horn)
    F.shape([(hx + 28, hy - 24), (hx + 70, hy - 66), (hx + 104, hy - 60), (hx + 74, hy - 44), (hx + 40, hy - 8)], horn)
    F.ell((hx, hy), (40, 36), hide)
    F.ell((hx - 6, hy + 26), (26, 16), "#6a6670")                      # muzzle
    for sg in (-1, 1):
        F.ell((hx - 6 + sg * 9, hy + 28), (4, 3), INK, lw=0)
        F.ell((hx + sg * 34, hy - 18), (16, 8), hide, ang=sg * 20)       # ears
        F.ell((hx + sg * 15, hy - 6), (5, 4), "#ffffff", lw=1)
        F.ell((hx + sg * 15, hy - 6), (2.4, 2.4), INK, lw=0)
    F.ln([(hx - 20, hy - 26), (hx + 20, hy - 26)], 0.5, "#c8281e")      # vermilion tilak
    # Mahishasura seated astride
    ax, ay = 652, 570
    F.shape([(ax - 40, ay + 70), (ax + 40, ay + 70), (ax + 50, ay + 130), (ax - 50, ay + 130)], "#7a1f22")  # dhoti
    F.shape([(ax - 44, ay - 50), (ax + 44, ay - 50), (ax + 40, ay + 74), (ax - 40, ay + 74)], skin)        # torso
    F.ln([(ax - 20, ay - 20), (ax - 6, ay - 8)], 0.4)
    F.ln([(ax + 20, ay - 20), (ax + 6, ay - 8)], 0.4)
    F.ln([(ax, ay + 10), (ax, ay + 50)], 0.4)
    F.shape([(ax - 44, ay + 66), (ax + 44, ay + 66), (ax + 44, ay + 80), (ax - 44, ay + 80)], GOLD)        # belt
    F.limb([(ax + 40, ay - 40), (ax + 76, ay - 90), (ax + 70, ay - 150)], 22, skin)                       # sword arm
    _bangles(F, (ax + 76, ay - 90), (ax + 70, ay - 150), n=2)
    F.shape([(ax + 66, ay - 150), (ax + 74, ay - 150), (ax + 60, ay - 262), (ax + 52, ay - 258)], "#d9d4cc")
    F.shape([(ax + 54, ay - 154), (ax + 88, ay - 148), (ax + 86, ay - 140), (ax + 52, ay - 146)], GOLD)
    F.limb([(ax - 40, ay - 40), (ax - 70, ay + 0), (ax - 60, ay + 30)], 22, skin)                         # shield arm
    F.ell((ax - 70, ay + 20), (36, 36), "#7a1f22")
    F.ell((ax - 70, ay + 20), (26, 26), None, lw=max(1, F.lw * 0.6), ink=hexc(GOLD))
    for a in np.linspace(0, math.tau, 5, endpoint=False):
        F.ell((ax - 70 + math.cos(a) * 14, ay + 20 + math.sin(a) * 14), (4, 4), GOLD, lw=1)
    F.shape([(ax - 12, ay - 66), (ax + 12, ay - 66), (ax + 12, ay - 48), (ax - 12, ay - 48)], skin)
    F.ell((ax, ay - 96), (34, 38), skin)                                                                 # head
    F.shape([(ax - 40, ay - 92), (ax - 36, ay - 130), (ax - 14, ay - 146), (ax + 14, ay - 146), (ax + 36, ay - 130),
             (ax + 40, ay - 92), (ax + 28, ay - 116), (ax, ay - 124), (ax - 28, ay - 116)], "#1d1512", smooth=True)
    for sg in (-1, 1):
        F.ln([(ax + sg * 6, ay - 108), (ax + sg * 22, ay - 112)], 0.9)          # fierce brows
        F.shape([(ax + sg * 14 - 8, ay - 98), (ax + sg * 14 + 8, ay - 98), (ax + sg * 14, ay - 92)], "#ffffff",
                lw=max(1, F.lw * 0.5))
        F.ell((ax + sg * 14, ay - 97), (2.4, 2.4), INK, lw=0)
        F.ell((ax + sg * 34, ay - 84), (5, 7), GOLD, lw=1)                      # earrings
    F.shape([(ax - 24, ay - 78), (ax - 6, ay - 84), (ax, ay - 80), (ax + 6, ay - 84), (ax + 24, ay - 78),
             (ax + 26, ay - 70), (ax + 6, ay - 76), (ax - 6, ay - 76), (ax - 26, ay - 70)], "#1d1512", lw=0)  # moustache
    F.ln([(ax - 6, ay - 68), (ax + 6, ay - 68)], 0.5, "#7a1f22")
    for j in range(2):
        F.L.arc((F.ox + ax * F.k, F.oy + (ay - 50) * F.k), ((20 + j * 9) * F.k, (12 + j * 8) * F.k), 10, 170,
                w=max(1.5, 3 * F.k), col=hexc(GOLD))


def durga_v3(height):
    F = Canvas(height, uw=760, uh=770)
    skin = "#f3c98b"
    _buffalo_asura(F)
    _lion3(F)
    # --- halo with petal and dot rings
    hx, hy = 300, 178
    for k in range(32):
        a = k / 32 * math.tau
        F.ell((hx + math.cos(a) * 124, hy + math.sin(a) * 124), (16, 11), RED_, ang=math.degrees(a),
              lw=max(1, F.lw * 0.6))
    F.ell((hx, hy), (116, 116), GOLD)
    F.ell((hx, hy), (100, 100), "#f6d77a", lw=max(1, F.lw * 0.6))
    for k in range(40):
        a = k / 40 * math.tau
        F.ell((hx + math.cos(a) * 108, hy + math.sin(a) * 108), (3, 3), RED_, lw=0)
    F.ell((hx, hy), (82, 82), "#f9e3a0", lw=max(1, F.lw * 0.5))
    # --- long hair behind
    F.shape([(250, 170), (258, 140), (342, 140), (350, 170), (362, 330), (352, 400), (330, 410), (270, 410),
             (246, 400), (238, 330)], "#1d1512", smooth=True)
    for x in (252, 262, 338, 348):
        F.ln([(x, 230), (x + (6 if x < 300 else -6), 400)], 0.35, "#4a3a36", smooth=False)
    # --- right hands (viewer left), top to bottom
    shR, shL = (268, 292), (332, 292)
    right = [((152, 112), "khadga"), ((112, 182), "chakra"), ((98, 252), "baan"), ((112, 322), "shakti")]
    left = [((452, 112), "khetak"), ((494, 182), "dhanu"), ((506, 252), "pash"), ((494, 322), "ankush")]
    for (hand, wpn) in right:
        _arm3(F, shR, hand, skin)
        _weapon(F, wpn, *hand)
    for (hand, wpn) in left:
        _arm3(F, shL, hand, skin, bend=-20)
        _weapon(F, wpn, *hand)
    # --- saree skirt draped over the lion's back
    sk_pts = [(264, 378), (338, 378), (372, 450), (410, 530), (360, 552), (240, 560), (188, 546), (222, 450)]
    F.shape(sk_pts, RED_, pattern=_buti_gold(F))
    F.shape([(188, 540), (240, 554), (360, 546), (410, 524), (416, 540), (362, 566), (238, 574), (182, 556)], GOLD)
    F.shape([(186, 556), (238, 572), (362, 564), (416, 540), (418, 550), (362, 576), (238, 584), (184, 566)],
            GREEN_)
    for x in (270, 290, 310, 330):  # pleat fan
        F.ln([(x, 392), (x - 40 + (x - 300) * 0.9, 548)], 0.45)
    F.ell((396, 586), (20, 10), skin)                                                       # foot on the lion
    F.ell((396, 580), (20, 4), RED_, lw=0)                                                  # alta
    F.ell((390, 586), (18, 4), GOLD, lw=1)                                                  # anklet
    # --- blouse, pallu, ornaments
    F.shape([(268, 276), (332, 276), (338, 380), (262, 380)], "#2f5fa8", pattern=pat_dots_gold(F))
    F.shape([(272, 280), (330, 280), (338, 380), (306, 380), (272, 304)], RED_, pattern=_buti_gold(F))
    F.shape([(272, 280), (288, 280), (338, 368), (324, 380)], GOLD)
    F.shape([(262, 372), (338, 372), (340, 390), (260, 390)], GOLD)                         # waist belt
    for x in range(268, 336, 12):
        F.ell((x, 381), (3.5, 3.5), RED_, lw=0)
    for j in range(4):  # layered necklaces + long haar
        F.L.arc((F.ox + 300 * F.k, F.oy + 272 * F.k), ((20 + j * 8) * F.k, (14 + j * 9 + (24 if j == 3 else 0)) * F.k),
                8, 172, w=max(1.5, 3.2 * F.k), col=hexc(GOLD if j % 2 == 0 else "#f6ecd6"))
    F.ell((300, 318), (7, 9), RED_, lw=1)
    # --- lowest hands: trishul into Mahishasura (right) and naagpash binding him (left)
    _arm3(F, shR, (238, 398), skin, bend=-14)
    F.shape([(196, 352), (203, 346), (626, 572), (621, 580)], "#d9d4cc")                   # trishul shaft
    F.shape([(616, 564), (632, 556), (642, 580), (628, 588)], "#d9d4cc")                   # prongs into the chest
    F.ln([(626, 558), (640, 542)], 1.0, "#d9d4cc")
    F.ln([(632, 578), (650, 572)], 1.0, "#d9d4cc")
    F.ell((238, 398), (10, 9), skin)
    _arm3(F, shL, (366, 404), skin, bend=14)
    snake = [(366, 404), (410, 440), (460, 420), (510, 470), (560, 480), (600, 516), (628, 520)]
    F.L.line(F.P(snake), w=11 * F.k + 2 * F.lw, col=INK, smooth=True)
    F.L.line(F.P(snake), w=11 * F.k, col=hexc("#3f7a3a"), smooth=True)
    F.ell((634, 520), (10, 7), "#3f7a3a")
    F.ell((366, 404), (10, 9), skin)
    # --- head
    F.shape([(288, 236), (312, 236), (314, 280), (286, 280)], skin)
    F.ell((300, 198), (44, 54), skin)
    F.shape([(256, 176), (270, 148), (300, 140), (330, 148), (344, 176), (324, 162), (300, 158), (276, 162)],
            "#1d1512", smooth=True)
    for sg in (-1, 1):
        cx = 300 + sg * 19
        F.ln([(cx - 15, 178), (cx, 172), (cx + 15, 178)], 0.8, smooth=True)
        F.shape([(cx - 17, 192), (cx - 5, 184), (cx + 9, 185), (cx + 19, 191), (cx + 7, 198), (cx - 7, 198)],
                "#fbf7ee", smooth=True, lw=max(1, F.lw * 0.8))
        F.ell((cx + 3, 191), (6, 6), INK, lw=0)
        F.ln([(cx + sg * 17, 191), (cx + sg * 28, 187)], 0.8)                               # kohl wing
        F.ell((300 + sg * 46, 222), (7, 12), GOLD, lw=max(1, F.lw * 0.6))                  # jhumka
        F.ell((300 + sg * 46, 236), (9, 6), GOLD, lw=max(1, F.lw * 0.6))
    F.ell((300, 172), (3.5, 8), RED_, lw=max(1, F.lw * 0.5))                                # third eye
    F.ln([(300, 158), (300, 168)], 0.5, GOLD)                                               # maang tikka
    F.ell((300, 158), (5, 5), GOLD, lw=1)
    F.ln([(300, 196), (302, 214), (296, 216)], 0.5)
    F.L.arc((F.ox + 310 * F.k, F.oy + 216 * F.k), (8 * F.k, 8 * F.k), -40, 260, w=max(1.5, 2.5 * F.k),
            col=hexc(GOLD))                                                                  # nose ring
    F.ln([(316, 214), (334, 196), (344, 208)], 0.35, GOLD, smooth=True)                      # nath chain
    F.shape([(287, 230), (300, 226), (313, 230), (300, 237)], RED_, lw=max(1, F.lw * 0.5))
    # --- crown (mukut): tiers with spikes and gems
    F.shape([(252, 160), (258, 120), (342, 120), (348, 160), (300, 150)], GOLD)
    spikes = [(258, 122), (266, 84), (280, 110), (290, 62), (300, 30), (310, 62), (320, 110), (334, 84),
              (342, 122)]
    F.shape(spikes, GOLD)
    for (x, y) in ((266, 100), (290, 84), (300, 56), (310, 84), (334, 100)):
        F.ell((x, y), (5, 6), RED_, lw=1)
    for x in range(262, 340, 9):
        F.ell((x, 140), (3, 3), "#fbf7ee", lw=0)
        F.ell((x + 4, 128), (2.5, 2.5), GREEN_, lw=0)
    F.ell((300, 104), (12, 14), "#fbf7ee", lw=max(1, F.lw * 0.6))
    F.ell((300, 104), (6, 7), RED_, lw=0)
    return F.L.rgba()


def pat_dots_gold(F):
    from flat import pat_dots
    return pat_dots(hexc(GOLD), step=max(6, int(14 * F.k)), r=max(1.2, 2.2 * F.k))


# ----------------------------------------------------------------------------- vertical (9:16) thakur-dalan
def lantern(L, x, y, s=1.0):
    L.line([(x, 0), (x, y - 40 * s)], 2)
    L.shape([(x - 22 * s, y - 40 * s), (x + 22 * s, y - 40 * s), (x + 30 * s, y), (x + 22 * s, y + 46 * s),
             (x - 22 * s, y + 46 * s), (x - 30 * s, y)], C["gold"], lw=3)
    L.shape([(x - 14 * s, y - 26 * s), (x + 14 * s, y - 26 * s), (x + 20 * s, y + 4 * s), (x + 14 * s, y + 34 * s),
             (x - 14 * s, y + 34 * s), (x - 20 * s, y + 4 * s)], hexc("#ffd76a"), lw=2)
    L.ellipse((x, y + 4 * s), (6 * s, 10 * s), C["orange"], lw=0)
    L.shape([(x - 8 * s, y + 46 * s), (x + 8 * s, y + 46 * s), (x, y + 64 * s)], C["red"], lw=2)


def thakur_dalan_v():
    L = Layer(W, H)
    L.paint(np.ones((H, W), np.float32), C["wall"])
    L.shape([(0, 120), (W, 120), (W, 1060), (0, 1060)], C["wall"], lw=0,
            pattern=pat_buti(mix(C["wall"], C["orange"], 0.28), None, step=40, r=6))
    cornice(L)
    cx, spring, r = W / 2, 560, 380
    L.shape([(cx - r - 46, spring), (cx + r + 46, spring), (cx + r + 46, 1060), (cx - r - 46, 1060)], C["orange"],
            lw=3)
    for rr, col in ((r + 46, C["orange"]), (r + 30, C["blue"]), (r + 16, C["white"])):
        L.ellipse((cx, spring), (rr, rr), col, lw=3)
    for k in range(31):
        a = math.pi + k / 30 * math.pi
        L.ellipse((cx + math.cos(a) * (r + 38), spring + math.sin(a) * (r + 38)), (9, 9), C["gold"], lw=2)
    L.ellipse((cx, spring), (r, r), C["interior"], lw=3)
    L.shape([(cx - r, spring), (cx + r, spring), (cx + r, 1060), (cx - r, 1060)], C["interior"], lw=0)
    # painted interior: faint lotus stencil on the sanctum wall
    for j, y in enumerate(range(260, 1040, 90)):
        for x in range(int(cx - r + 40 + (j % 2) * 45), int(cx + r - 20), 90):
            if (x - cx) ** 2 + (y - spring) ** 2 < (r - 30) ** 2 or y > spring:
                L.ellipse((x, y), (10, 16), mix(C["interior"], C["gold"], 0.25), lw=0)
    L.line([(cx - r, spring), (cx - r, 1060)], 3)
    L.line([(cx + r, spring), (cx + r, 1060)], 3)
    for x in (40, W - 40):
        column(L, x, 150, 1060, w=44)
    # dalan floor, steps, courtyard
    L.shape([(0, 1060), (W, 1060), (W, 1170), (0, 1170)], C["white"], lw=3,
            pattern=pat_checks(hexc("#2a2420"), hexc("#f4efe6"), step=34))
    for y, col in ((1170, C["white"]), (1194, mix(C["white"], C["wall"], 0.6))):
        L.shape([(0, y), (W, y), (W, y + 24), (0, y + 24)], col, lw=3)
    L.shape([(0, 1218), (W, 1218), (W, H), (0, H)], C["vermilion"], lw=3,
            pattern=pat_dots(mix(C["vermilion"], C["red"], 0.6), step=30, r=3))
    return L


def chandelier(L, x, y):
    L.line([(x, 150), (x, y)], 2)
    for k, w in enumerate((90, 70, 50)):
        yy = y + k * 34
        L.shape([(x - w, yy), (x + w, yy), (x + w * 0.8, yy + 18), (x - w * 0.8, yy + 18)], C["gold"], lw=3)
        for j in range(-3, 4):
            L.ellipse((x + j * w / 3.4, yy + 30), (5, 12), hexc("#eaf4fb"), lw=2)
