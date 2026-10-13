"""Parametric flat figures: women in sarees, men in panjabi-dhoti, dhakis, a priest, seated & children.

Each figure is drawn into its own Layer at the requested height so outlines stay crisp. Units below are
in a 480-unit-tall standing body with feet centred at (0, 0) and y going up negative.
"""
import math
import numpy as np
from flat import Layer, hexc, mix, INK, pat_dots, pat_buti, pat_stripes, pat_combo

SKINS = ["#f1c7a3", "#e3ad85", "#c98a62", "#a96d48", "#8a5536"]
RED = hexc("#c8281e")


def _c(x):
    return hexc(x) if isinstance(x, str) else x


def _pattern(kind, col, k):
    if kind is None:
        return None
    col = _c(col)
    if kind == "dots":
        return pat_dots(col, step=max(6, int(14 * k)), r=max(1.2, 2.6 * k))
    if kind == "buti":
        return pat_buti(col, None, step=max(8, int(26 * k)), r=max(2, 5 * k))
    if kind == "stripes":
        return pat_stripes(col, step=max(6, int(16 * k)), w=max(2, int(5 * k)), ang=1.2)
    if kind == "checks":
        return pat_combo(pat_stripes(col, step=max(6, int(18 * k)), w=max(2, int(4 * k)), ang=0.0),
                         pat_stripes(col, step=max(6, int(18 * k)), w=max(2, int(4 * k)), ang=math.pi / 2))
    return None


class Fig:
    def __init__(self, height):
        self.k = height / 480.0
        k = self.k
        self.W, self.H = int(300 * k) + 8, int(640 * k) + 8
        self.ox, self.oy = self.W / 2, self.H - 14 * k - 4
        self.L = Layer(self.W, self.H)
        self.lw = max(1.6, 3.2 * k)

    def P(self, pts, dy=0):
        return [(self.ox + x * self.k, self.oy + (y + dy) * self.k) for x, y in pts]

    def shape(self, pts, fill, pattern=None, smooth=False, dy=0, lw=None):
        return self.L.shape(self.P(pts, dy), _c(fill), lw=self.lw if lw is None else lw, smooth=smooth,
                            pattern=pattern)

    def ell(self, c, ax, fill, ang=0, dy=0, lw=None, pattern=None, ink=INK):
        (cx, cy), = self.P([c], dy)
        return self.L.ellipse((cx, cy), (ax[0] * self.k, ax[1] * self.k), _c(fill), lw=self.lw if lw is None else lw,
                              ang=ang, pattern=pattern, ink=ink)

    def limb(self, pts, w, col, dy=0):
        P = self.P(pts, dy)
        self.L.line(P, w=w * self.k + 2 * self.lw, col=INK)
        self.L.line(P, w=w * self.k, col=_c(col))

    def ln(self, pts, w=1.0, col=None, dy=0, smooth=False):
        self.L.line(self.P(pts, dy), w=max(1, w * self.lw), col=INK if col is None else _c(col), smooth=smooth)


# ------------------------------------------------------------------------------------------- parts
def head(F, s, dy=0):
    skin = _c(s.get("skin", SKINS[1]))
    hair = _c(s.get("hair_col", "#1d1512"))
    style = s.get("hair", "bun")
    turn = s.get("turn", 0) * 6
    # hair behind head
    if style in ("bun", "grey_bun"):
        F.ell((24 + turn, -452), (17, 15), hair, dy=dy)
    if style == "braid":
        F.shape([(-10, -440), (10, -440), (8, -330), (-8, -330)], hair, dy=dy)
    if style == "open":
        F.shape([(-34, -470), (34, -470), (40, -360), (-40, -360)], hair, smooth=True, dy=dy)
    F.shape([(-9, -404), (9, -404), (10, -382), (-10, -382)], skin, dy=dy)                     # neck
    F.ell((0 + turn * 0.3, -432), (27, 33), skin, dy=dy)                                      # face
    # hair cap with centre parting
    if style == "short":
        F.shape([(-28, -440), (-26, -462), (-12, -470), (12, -470), (26, -462), (28, -440), (20, -452),
                 (-20, -452)], hair, smooth=True, dy=dy)
    elif style == "bald":
        pass
    else:
        F.shape([(-28, -428), (-27, -458), (-14, -468), (0, -466), (14, -468), (27, -458), (28, -428),
                 (19, -450), (2, -458), (-19, -450)], hair, smooth=True, dy=dy)
    if s.get("sindoor"):
        F.ln([(1, -466), (1, -455)], 1.6, RED, dy=dy)
    if s.get("bindi", s.get("sindoor")):
        F.ell((turn * 0.3, -445), (3.2, 3.2), RED, dy=dy, lw=0)
    if s.get("third_eye"):
        F.ell((0, -447), (2.4, 6), INK, dy=dy, lw=0)
    # face features: brows, eyes, nose, mouth (simple poster-style lines)
    ex = 10
    for sg in (-1, 1):
        cx = sg * ex + turn * 0.4
        F.ln([(cx - 6, -440), (cx, -442), (cx + 6, -440)], 0.55, dy=dy, smooth=True)
        if s.get("eyes", "open") == "open":
            F.ell((cx, -431), (4, 2.2), "#ffffff", dy=dy, lw=max(1, F.lw * 0.45))
            F.ell((cx + turn * 0.15, -431), (1.8, 1.9), INK, dy=dy, lw=0)
        else:
            F.ln([(cx - 5, -431), (cx, -429), (cx + 5, -431)], 0.5, dy=dy, smooth=True)
    F.ln([(turn * 0.5, -430), (turn * 0.5 + 2, -418), (turn * 0.5 - 1, -416)], 0.45, dy=dy)
    F.shape([(-6 + turn * 0.4, -409), (0 + turn * 0.4, -411), (6 + turn * 0.4, -409), (0 + turn * 0.4, -405)],
            s.get("lips", "#b8322a"), dy=dy, lw=max(1, F.lw * 0.4))
    if s.get("mustache"):
        F.shape([(-9, -414), (0, -417), (9, -414), (0, -412)], hair, dy=dy, lw=0)
    if s.get("glasses"):
        for sg in (-1, 1):
            F.ell((sg * 10, -431), (7, 6), None, dy=dy, lw=max(1, F.lw * 0.5))
    if s.get("sindoor_khela"):  # vermilion smeared on cheeks and forehead after Bijoya
        for (cx, cy, rx, ry) in ((-14, -420, 9, 6), (14, -420, 9, 6), (0, -452, 14, 5)):
            F.ell((cx, cy), (rx, ry), "#d4231c", dy=dy, lw=0)
    if s.get("mask"):
        F.shape([(-22, -424), (22, -424), (18, -400), (-18, -400)], "#a9d3e0", dy=dy)


def arms(F, s, sleeve, dy=0):
    skin = s.get("skin", SKINS[1])
    pose = s.get("arms", "down")
    ph = s.get("phase", 0.0)
    for sg in (-1, 1):
        sh = (sg * 36, -378)
        if pose == "down":
            pts = [sh, (sg * 46, -310), (sg * 40, -238)]
        elif pose == "fold":       # namaskar
            pts = [sh, (sg * 40, -320), (sg * 4, -350)]
        elif pose == "clap":
            a = 0.5 + 0.5 * math.sin(ph * math.tau)
            pts = [sh, (sg * 46, -330), (sg * (6 + 10 * a), -372)]
        elif pose == "up":
            pts = [sh, (sg * 58, -430), (sg * 50, -500)]
        elif pose == "dhunuchi":
            if sg > 0:
                sw = math.sin(ph * math.tau)
                pts = [sh, (60, -430 + 10 * sw), (36 + 30 * sw, -500)]
            else:
                pts = [sh, (-50, -320), (-30, -270)]
        elif pose == "aarti":
            pts = [sh, (sg * 40, -320), (sg * 14, -345)] if sg < 0 else [sh, (52, -360), (38, -420)]
        elif pose == "phone":
            pts = [sh, (sg * 40, -320), (sg * 12, -380)] if sg > 0 else [sh, (-46, -310), (-40, -238)]
        elif pose == "drum":
            pts = [sh, (-44, -320), (-6, -300)] if sg < 0 else [sh, (60, -420), (40, -470)]
        else:
            pts = [sh, (sg * 46, -310), (sg * 40, -238)]
        F.limb(pts, 13, skin, dy=dy)
        if s.get("bangles"):
            bx = pts[1][0] + (pts[2][0] - pts[1][0]) * 0.8
            by = pts[1][1] + (pts[2][1] - pts[1][1]) * 0.8
            F.ell((bx, by), (7.5, 7.5), "#c8281e", dy=dy, lw=max(1, F.lw * 0.5))     # shakha-pola
            F.ell((bx + (pts[2][0] - bx) * 0.4, by + (pts[2][1] - by) * 0.4), (7, 7), "#fbf8f2", dy=dy,
                  lw=max(1, F.lw * 0.5))
        F.ell(pts[-1], (6.5, 6.5), skin, dy=dy)
        if sleeve is not None:
            F.limb([sh, ((sh[0] + pts[1][0]) / 2, (sh[1] + pts[1][1]) / 2)], 18, sleeve, dy=dy)
    return pose


def props_in_hands(F, s, dy=0):
    pose = s.get("arms", "down")
    ph = s.get("phase", 0.0)
    if pose == "dhunuchi":
        sw = math.sin(ph * math.tau)
        x, y = 36 + 30 * sw, -512
        F.shape([(x - 16, y), (x + 16, y), (x + 8, y + 16), (x - 8, y + 16)], "#b5562c", dy=dy)
        F.ell((x, y - 2), (16, 5), "#3a2a22", dy=dy)
        for k in range(3):  # smoke puffs
            F.ell((x - 8 + k * 9 + 6 * math.sin(ph * 6 + k), y - 22 - k * 20), (10 + k * 3, 8 + k * 2), "#ece6dc",
                  dy=dy, lw=max(1, F.lw * 0.5))
    if pose == "aarti":
        x, y = 38, -432
        F.shape([(x - 20, y), (x + 20, y), (x + 10, y + 12), (x - 10, y + 12)], "#e3a82b", dy=dy)
        for j in range(5):
            F.ell((x - 16 + j * 8, y - 8), (3.5, 7), "#ffcf4a", dy=dy, lw=max(1, F.lw * 0.4))
    if pose == "phone":
        F.shape([(4, -398), (22, -398), (22, -366), (4, -366)], "#2b2f3a", dy=dy)
        F.shape([(7, -395), (19, -395), (19, -369), (7, -369)], "#ffd27a", dy=dy, lw=0)
    if pose == "fold":
        F.ell((0, -352), (7, 11), s.get("skin", SKINS[1]), dy=dy)


# ------------------------------------------------------------------------------------------- bodies
def woman(F, s, dy=0, seated=False):
    s = dict(s)
    s.setdefault("bangles", True)
    base = s.get("saree", "#f4ece0")
    border = s.get("border", "#c8281e")
    pat = _pattern(s.get("pattern"), s.get("pat_col", border), F.k)
    blouse = s.get("blouse", border)
    if seated:
        F.shape([(-34, -300), (34, -300), (60, -230), (96, -150), (100, -122), (-100, -122), (-96, -150),
                 (-60, -230)], base, pattern=pat, smooth=False, dy=dy)
        F.shape([(-100, -140), (100, -140), (100, -122), (-100, -122)], border, dy=dy)
    else:
        F.shape([(-34, -300), (34, -300), (44, -150), (54, -18), (-54, -18), (-44, -150)], base, pattern=pat,
                dy=dy)
        for x in (-6, 2, 10):  # front pleats
            F.ln([(x, -270), (x + 3, -20)], 0.5, dy=dy)
        F.shape([(-54, -40), (54, -40), (55, -16), (-55, -16)], border, dy=dy)
        F.ell((-18, -10), (11, 6), s.get("skin", SKINS[1]), dy=dy)
        F.ell((18, -10), (11, 6), s.get("skin", SKINS[1]), dy=dy)
    F.shape([(-36, -386), (36, -386), (34, -300), (-34, -300)], blouse, dy=dy)
    arms(F, s, blouse, dy=dy)
    # pallu: diagonal drape over the left shoulder with border
    F.shape([(-38, -392), (-14, -394), (36, -318), (38, -270), (14, -300)], base, pattern=pat, dy=dy)
    F.shape([(-14, -394), (-4, -394), (38, -296), (36, -280)], border, dy=dy)
    F.L.arc((F.ox, F.oy + (-384 + dy) * F.k), (14 * F.k, 10 * F.k), 10, 170, w=max(1.5, 2.6 * F.k),
            col=hexc("#e7b23a"))                                         # necklace
    head(F, s, dy=dy)
    if s.get("hair", "bun") in ("bun",):
        for j in range(5):                                              # jasmine gajra round the bun
            a = j / 4 * math.pi - math.pi / 2
            F.ell((24 + math.cos(a) * 17, -452 + math.sin(a) * 15), (3.5, 3.5), "#fbf8f2", dy=dy,
                  lw=max(1, F.lw * 0.4))
    props_in_hands(F, s, dy=dy)


def man(F, s, dy=0, seated=False):
    kurta = s.get("kurta", "#f4ece0")
    pat = _pattern(s.get("pattern"), s.get("pat_col", "#5a6fa8"), F.k)
    dhoti = s.get("dhoti", "#f7f2e8")
    if not s.get("trousers"):
        F.shape([(-30, -170), (30, -170), (40, -16), (6, -16), (0, -120), (-6, -16), (-40, -16)], dhoti, dy=dy)
        F.ln([(-2, -160), (-3, -40)], 0.5, dy=dy)
    else:
        F.shape([(-30, -170), (30, -170), (34, -16), (4, -16), (0, -130), (-4, -16), (-34, -16)], s["trousers"], dy=dy)
    F.ell((-20, -10), (12, 6), "#3a2a22", dy=dy)
    F.ell((20, -10), (12, 6), "#3a2a22", dy=dy)
    if s.get("bare"):  # priest: bare chest, white uttariya
        F.shape([(-34, -386), (34, -386), (32, -170), (-32, -170)], s.get("skin", SKINS[1]), dy=dy)
        F.ln([(-30, -384), (26, -200)], 0.5, "#f6f0e2", dy=dy)
        F.shape([(-36, -388), (-20, -390), (30, -250), (20, -230)], "#f6f0e2", dy=dy)
        sleeve = None
    else:
        F.shape([(-36, -386), (36, -386), (42, -150), (-42, -150)], kurta, pattern=pat, dy=dy)
        F.ln([(0, -384), (0, -330)], 0.5, dy=dy)
        sleeve = kurta
    if s.get("shawl"):
        F.shape([(-38, -390), (-22, -392), (30, -230), (14, -226)], s["shawl"], dy=dy)
    arms(F, s, sleeve, dy=dy)
    if s.get("dhak"):
        dhak(F, dy)
    head(F, s, dy=dy)
    props_in_hands(F, s, dy=dy)


def dhak(F, dy=0):
    """Big barrel drum slung across the hip, white skins, kash-phool feather plume on the top end."""
    cx, cy, ang, L, R = -28, -290, math.radians(-24), 170, 44
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    a = (cx - ux * L / 2, cy - uy * L / 2)
    b = (cx + ux * L / 2, cy + uy * L / 2)
    body = [(a[0] + px * R, a[1] + py * R), (b[0] + px * R, b[1] + py * R), (b[0] - px * R, b[1] - py * R),
            (a[0] - px * R, a[1] - py * R)]
    F.shape(body, "#b8372a", dy=dy)
    for t in np.linspace(0.1, 0.9, 7):  # lacing
        x0, y0 = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        F.ln([(x0 + px * R, y0 + py * R), (x0 - px * R + ux * 10, y0 - py * R + uy * 10)], 0.5, "#f2d27a", dy=dy)
    F.ell(a, (12, R), "#f4ecdc", ang=math.degrees(ang), dy=dy)
    F.ell(b, (12, R), "#f4ecdc", ang=math.degrees(ang), dy=dy)
    for j in range(9):  # feather plume rising from the upper end
        t = j / 8
        F.ell((a[0] + 6 + 30 * t, a[1] - R - 26 - 18 * math.sin(t * math.pi)), (9, 26), "#fbf8f2",
              ang=-35 + 70 * t, dy=dy, lw=max(1, F.lw * 0.5))


def make_figure(spec, height):
    F = Fig(height)
    kind = spec.get("kind", "woman")
    if kind == "woman":
        woman(F, spec)
    elif kind == "seated_woman":
        woman(F, spec, dy=118, seated=True)
    elif kind == "man":
        man(F, spec)
    elif kind == "dhaki":
        s = dict(spec)
        s.setdefault("arms", "drum")
        s["dhak"] = True
        man(F, s)
    elif kind == "priest":
        s = dict(spec)
        s.setdefault("arms", "aarti")
        s["bare"] = True
        s.setdefault("hair", "short")
        man(F, s)
    return F.L.rgba()
