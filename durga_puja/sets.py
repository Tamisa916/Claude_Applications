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
