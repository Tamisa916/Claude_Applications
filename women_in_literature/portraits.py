"""Parametric painterly portrait generator (head + shoulders, 900x1200)."""
import math
import numpy as np
import cv2
from paint import Layer, painterize, hexc, mix, angle_radial, flow_field

PW, PH = 900, 1200
CX, CY = 450, 430
RX, RY = 145, 190

DEFAULT = dict(
    skin="#e4bfa5", shadow="#a97c68", blush="#d4887a", lips="#c4584a",
    hair="#1b1413", hair_hi="#4d4a55", brow=None, iris="#3a2418",
    hair_style="bob", eyes="closed", cloth="#1a1515", cloth_hi="#44322c",
    neckline="v", tilt=0.0, turn=0.0, acc=(), lift=0, seed=1, cloth_pattern=None,
)


def _p(pts, dx=0, dy=0):
    return [(CX + x + dx, CY + y + dy) for x, y in pts]


def _mirror(pts):
    return [(-x, y) for x, y in reversed(pts)]


def _bumpy(cx, cy, r, n, amp, seed, squash=1.0, start=0, end=2 * math.pi):
    rng = np.random.default_rng(seed)
    pts = []
    for i in range(n):
        t = start + (end - start) * i / n
        rr = r * (1 + amp * (rng.random() - 0.5) + amp * 0.6 * math.sin(i * 1.7))
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t) * squash))
    return pts


# --------------------------------------------------------------------------- hair
def hair_shapes(style, seed):
    """Return (back_polys, front_polys) in head-relative coords."""
    back, front = [], []
    if style == "bob":
        back.append([(-210, -40), (-188, -200), (-80, -270), (70, -270), (192, -196), (224, -30), (228, 110),
                     (205, 215), (150, 250), (95, 205), (-90, 205), (-150, 250), (-208, 215), (-232, 105)])
        front.append([(-150, -60), (-158, -200), (-60, -262), (75, -260), (172, -190), (178, -80), (150, -40),
                      (126, -112), (88, -92), (45, -132), (2, -112), (-40, -142), (-84, -118), (-122, -148)])
        front.append([(-150, -130), (-176, 0), (-166, 130), (-128, 190), (-124, 70), (-132, -50)])
        front.append(_mirror([(-150, -130), (-176, 0), (-166, 130), (-128, 190), (-124, 70), (-132, -50)]))
    elif style == "updo":
        front.append([(-160, -70), (-205, -170), (-160, -285), (0, -322), (160, -285), (205, -170), (160, -70),
                      (140, -125), (60, -160), (-60, -160), (-140, -125)])
        front.append(_bumpy(0, -330, 85, 18, 0.15, seed, 0.6))
        front.append([(-158, -90), (-165, 30), (-138, 10), (-140, -80)])
        front.append(_mirror([(-158, -90), (-165, 30), (-138, 10), (-140, -80)]))
    elif style == "scarf":
        back.append([(-170, -40), (-160, -180), (-60, -250), (60, -250), (160, -180), (170, -40), (150, 40),
                     (-150, 40)])
        front.append([(-140, -118), (0, -168), (140, -118), (128, -88), (60, -118), (0, -128), (-60, -118),
                      (-128, -88)])
    elif style == "wave":
        front.append([(-160, -40), (-172, -170), (-92, -252), (62, -256), (166, -180), (172, -40), (160, 60),
                      (132, 112), (122, 20), (112, -78), (60, -136), (-20, -146), (-110, -108), (-140, 0),
                      (-140, 92), (-168, 60)])
    elif style == "long":
        back.append([(-218, -60), (-196, -212), (-90, -278), (70, -278), (196, -206), (226, -40), (252, 200),
                     (288, 430), (226, 540), (150, 500), (112, 300), (-112, 300), (-150, 500), (-230, 540),
                     (-288, 430), (-254, 200)])
        side = [(8, -260), (-80, -242), (-152, -172), (-178, -40), (-172, 120), (-150, 240), (-134, 120),
                (-130, -40), (-100, -150), (-20, -205)]
        front.append(side)
        front.append(_mirror([(-x + 16, y) for x, y in side][::-1])[::-1])
    elif style == "victory":
        back.append([(-215, -50), (-190, -205), (-80, -270), (70, -270), (195, -202), (222, -40), (238, 120),
                     (252, 232), (202, 272), (140, 232), (-140, 232), (-202, 272), (-252, 232), (-238, 120)])
        for i in range(6):
            x = -230 + i * 30 if i < 3 else 140 + (i - 3) * 30
            back.append(_bumpy(x, 240, 34, 10, 0.25, seed + i))
        front.append([(-170, -60), (-190, -190), (-92, -264), (60, -264), (172, -192), (182, -80), (124, -150),
                      (20, -178), (-62, -152), (-122, -118)])
        front.append(_bumpy(-110, -205, 72, 14, 0.15, seed + 9, 0.8))
    elif style == "set":
        back.append([(-196, -40), (-186, -200), (-80, -266), (70, -266), (186, -200), (202, -40), (202, 80),
                     (162, 142), (-162, 142), (-202, 80)])
        for i in range(7):
            back.append(_bumpy(-180 + i * 60, 132, 36, 10, 0.2, seed + i))
        front.append([(-166, -70), (-176, -192), (-80, -260), (70, -260), (172, -192), (166, -70), (110, -142),
                      (0, -162), (-110, -142)])
        for i in range(5):
            front.append(_bumpy(-120 + i * 60, -175, 40, 10, 0.2, seed + 20 + i))
    elif style == "wild":
        rng = np.random.default_rng(seed)
        pts = []
        for i in range(40):
            t = math.pi * 0.95 + i / 40 * math.pi * 2
            r = 250 + 60 * rng.random()
            y = math.sin(t) * r * 0.95 + (150 if math.sin(t) > 0 else 0) * abs(math.sin(t)) * 1.8
            pts.append((math.cos(t) * r * (1.05 if math.sin(t) > 0 else 0.92), y - 30))
        back.append(pts)
        side = [(0, -262), (-90, -246), (-160, -170), (-186, -30), (-180, 140), (-200, 300), (-150, 200),
                (-136, 40), (-126, -80), (-80, -170)]
        front.append(side)
        front.append(_mirror(side))
    elif style == "curls":
        back.append(_bumpy(0, -40, 285, 44, 0.12, seed, 0.95))
        for i in range(9):
            ang = math.pi * (1.1 + i * 0.1)
            front.append(_bumpy(math.cos(ang) * 150, -60 + math.sin(ang) * 175, 42, 10, 0.25, seed + i))
    elif style == "bonnet":
        pass
    elif style == "messy":
        back.append([(-212, -50), (-190, -206), (-80, -272), (70, -272), (195, -204), (222, -40), (236, 140),
                     (262, 262), (210, 252), (226, 300), (150, 250), (-140, 250), (-210, 296), (-200, 250),
                     (-258, 262), (-236, 140)])
        front.append([(-150, -80), (-176, -196), (-86, -266), (66, -266), (174, -194), (184, -60), (164, 40),
                      (140, -60), (100, -140), (20, -168), (-30, -120), (-70, -150), (-120, -110)])
        front.append([(-150, -110), (-182, 20), (-170, 200), (-140, 260), (-130, 90), (-132, -40)])
    return back, front


# --------------------------------------------------------------------------- face
def face_outline():
    return _p([(0, -RY), (RX * 0.92, -RY * 0.58), (RX, -RY * 0.06), (RX * 0.94, RY * 0.34), (RX * 0.72, RY * 0.72),
               (RX * 0.30, RY * 0.97), (0, RY * 1.01), (-RX * 0.30, RY * 0.97), (-RX * 0.72, RY * 0.72),
               (-RX * 0.94, RY * 0.34), (-RX, -RY * 0.06), (-RX * 0.92, -RY * 0.58)])


def draw_portrait(spec):
    s = dict(DEFAULT)
    s.update(spec)
    C = {k: hexc(v) for k, v in s.items() if isinstance(v, str) and v.startswith("#")}
    brow = C.get("brow", None) if s["brow"] else mix(C["hair"], hexc("#3a2018"), 0.3)
    seed = s["seed"]
    turn = s["turn"]
    lift = s["lift"]
    fx = CX + turn * 60
    style = s["hair_style"]
    hair_ang = angle_radial(PW, PH, CX + 10, CY - 760 + lift)

    # ---------------- back hair ----------------
    back_polys, front_polys = hair_shapes(style, seed)
    BH = Layer(PW, PH)
    for poly in back_polys:
        BH.paint(BH.mpoly(_p(poly, dy=lift), blur=1.5), C["hair"])
    if BH.a.max() > 0:
        BH.shade(BH.mell((CX + 120, CY + lift), (160, 260), blur=60), C["hair_hi"], 0.25)
        painterize(BH, seed + 1, passes=((2500, 40, 6, 12), (3500, 22, 3, 6)), angle=hair_ang,
                   angle_noise=0.12, jitter=0.12, highlight=0.05, hl_col=C["hair_hi"])

    # ---------------- body ----------------
    B = Layer(PW, PH)
    neck = [(CX - 56, CY + 110 + lift), (CX + 56, CY + 110 + lift), (CX + 54, CY + 235), (CX + 78, CY + 335),
            (CX - 82, CY + 335), (CX - 56, CY + 235)]
    B.paint(B.mpoly(neck, smooth=False, blur=3), C["skin"])
    torso = [(CX - 74, CY + 300), (CX - 210, CY + 395), (CX - 370, CY + 470), (CX - 445, CY + 620),
             (CX - 470, PH + 40), (CX + 470, PH + 40), (CX + 445, CY + 620), (CX + 370, CY + 470),
             (CX + 210, CY + 395), (CX + 74, CY + 300)]
    B.paint(B.mpoly(torso, blur=2), C["skin"])
    B.shade(B.mell((CX + 30, CY + 205 + lift), (120, 70), blur=26), C["shadow"], 0.75)
    B.shade(B.mpoly([(CX + 20, CY + 120), (CX + 80, CY + 120), (CX + 90, CY + 360), (CX + 30, CY + 360)],
                    blur=18, smooth=False), C["shadow"], 0.45)
    B.shade(B.mell((CX - 30, CY + 300), (40, 60), blur=20), mix(C["skin"], hexc("#fff3e6"), 0.35), 0.4)
    B.shade(B.mline([(CX - 200, CY + 420), (CX - 110, CY + 400), (CX - 30, CY + 420)], 8, 4, blur=5),
            C["shadow"], 0.35)
    B.shade(B.mline([(CX + 30, CY + 420), (CX + 110, CY + 400), (CX + 200, CY + 420)], 8, 4, blur=5),
            C["shadow"], 0.35)
    nl = s["neckline"]
    if nl == "v":
        cloth = [(CX - 480, CY + 520), (CX - 330, CY + 450), (CX - 175, CY + 410), (CX - 20, CY + 640),
                 (CX + 175, CY + 410), (CX + 330, CY + 450), (CX + 480, CY + 520), (CX + 480, PH + 40),
                 (CX - 480, PH + 40)]
    elif nl == "round":
        cloth = [(CX - 480, CY + 500), (CX - 300, CY + 440), (CX - 170, CY + 410), (CX - 100, CY + 480),
                 (CX, CY + 510), (CX + 100, CY + 480), (CX + 170, CY + 410), (CX + 300, CY + 440),
                 (CX + 480, CY + 500), (CX + 480, PH + 40), (CX - 480, PH + 40)]
    elif nl == "boat":
        cloth = [(CX - 480, CY + 560), (CX - 330, CY + 500), (CX, CY + 530), (CX + 330, CY + 500),
                 (CX + 480, CY + 560), (CX + 480, PH + 40), (CX - 480, PH + 40)]
    elif nl == "high":
        cloth = [(CX - 480, CY + 470), (CX - 250, CY + 400), (CX - 90, CY + 330), (CX - 80, CY + 250),
                 (CX + 80, CY + 250), (CX + 90, CY + 330), (CX + 250, CY + 400), (CX + 480, CY + 470),
                 (CX + 480, PH + 40), (CX - 480, PH + 40)]
    else:  # strapless / off shoulder
        cloth = [(CX - 480, CY + 620), (CX - 300, CY + 600), (CX, CY + 640), (CX + 300, CY + 600),
                 (CX + 480, CY + 620), (CX + 480, PH + 40), (CX - 480, PH + 40)]
    cm = B.mpoly(cloth, smooth=(nl not in ("v",)), blur=1.5)
    B.paint(cm, C["cloth"])
    rng = np.random.default_rng(seed + 7)
    for i in range(7):  # folds
        x0 = CX - 420 + i * 140 + rng.uniform(-30, 30)
        B.shade(B.mline([(x0, PH), (x0 + rng.uniform(-40, 40), CY + 620), (x0 + rng.uniform(-60, 60), CY + 480)],
                        18, 6, blur=10) * cm, C["cloth_hi"], 0.5)
    pat = s["cloth_pattern"]
    if pat == "flowers":  # loose painted blossoms on the dress, like the reference
        for (x, y, col) in [(CX - 270, CY + 520, "#f2b8b0"), (CX - 230, CY + 610, "#fbeee4"),
                            (CX - 300, CY + 660, "#f3a58f"), (CX - 200, CY + 520, "#fff6ec"),
                            (CX + 300, CY + 560, "#f0b1a5")]:
            for k in range(6):
                a = k / 6 * math.tau
                B.paint(B.mell((x + 18 * math.cos(a), y + 18 * math.sin(a)), (16, 12), a * 57, blur=1.5) * cm,
                        hexc(col))
            B.paint(B.mell((x, y), (8, 8), blur=1) * cm, hexc("#e8c46a"))
    elif pat == "dots":
        for yy in range(int(CY + 440), PH, 46):
            for xx in range(30, PW, 46):
                B.paint(B.mell((xx + (yy // 46 % 2) * 23, yy), (7, 7), blur=1) * cm, C["cloth_hi"])
    elif pat == "stripes":
        for xx in range(-200, PW + 200, 70):
            B.paint(B.mline([(xx, PH), (xx + 220, CY + 400)], 22, 22, blur=1) * cm, C["cloth_hi"])
    if "lace" in s["acc"]:
        B.paint(B.mpoly([(CX - 95, CY + 230), (CX + 95, CY + 230), (CX + 105, CY + 340), (CX - 105, CY + 340)],
                        blur=1), hexc("#f6ead6"))
        for i in range(9):
            B.paint(B.mell((CX - 100 + i * 25, CY + 340), (14, 10), blur=1), hexc("#f6ead6"))
    if "collar" in s["acc"]:
        for sgn in (-1, 1):
            B.paint(B.mpoly([(CX, CY + 515), (CX + sgn * 175, CY + 410), (CX + sgn * 200, CY + 470),
                             (CX + sgn * 60, CY + 560)], blur=1), hexc("#fbf3e6"))
    if "cloak" in s["acc"]:
        B.shade(B.mpoly([(CX - 480, CY + 470), (CX - 120, CY + 300), (CX + 120, CY + 300), (CX + 480, CY + 470),
                         (CX + 480, PH), (CX - 480, PH)], blur=4), C["cloth"], 1.0)
    bang = flow_field(PW, PH, seed + 9, base=1.35, amp=0.5)
    yy0, xx0 = np.mgrid[0:PH, 0:PW].astype(np.float32)
    skin_zone = (yy0 < CY + 420) & (np.abs(xx0 - CX) < 120)
    bang = np.where(skin_zone, np.pi / 2 + 0.25 * np.sign(xx0 - CX), bang).astype(np.float32)
    painterize(B, seed + 2, passes=((2600, 60, 10, 18), (2400, 34, 6, 10)), angle=bang, angle_noise=0.25,
               highlight=0.0, soft=0.3)
    if "pearls" in s["acc"]:
        for i in range(23):
            t = i / 22
            x = CX - 120 + 240 * t
            y = CY + 340 + 70 * math.sin(t * math.pi)
            B.paint(B.mell((x, y), (11, 11), blur=0.8), hexc("#efe6da"))
            B.paint(B.mell((x - 3, y - 4), (3, 3), blur=1), hexc("#ffffff"))
            B.shade(B.mell((x + 3, y + 4), (6, 4), blur=2), hexc("#9e8f84"), 0.6)

    # ---------------- face ----------------
    F = Layer(PW, PH)
    # long oval face, defined cheekbones and jaw (after the yellow-dress reference)
    frx, fry = 128, 206
    fo = [(CX + x, CY + 6 + y + lift) for x, y in [
        (0, -fry), (frx * 0.9, -fry * 0.62), (frx, -fry * 0.12), (frx * 0.97, fry * 0.22),
        (frx * 0.80, fry * 0.58), (frx * 0.52, fry * 0.86), (frx * 0.2, fry * 0.99), (0, fry * 1.01),
        (-frx * 0.2, fry * 0.99), (-frx * 0.52, fry * 0.86), (-frx * 0.80, fry * 0.58), (-frx * 0.97, fry * 0.22),
        (-frx, -fry * 0.12), (-frx * 0.9, -fry * 0.62)]]
    fm = F.mpoly(fo, blur=1.2)
    for sgn in (-1, 1):  # ears
        F.paint(F.mell((CX + sgn * frx * 0.97, CY + 30 + lift), (20, 40), blur=1.5), mix(C["skin"], C["shadow"], 0.25))
    F.paint(fm, C["skin"])
    hi = mix(C["skin"], hexc("#fff4ea"), 0.35)   # highlight relative to this skin tone
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    ramp = np.clip((xx - (fx + 24)) / 110, 0, 1) * fm
    F.shade(cv2.GaussianBlur(ramp, (0, 0), 10), C["shadow"], 0.85)
    ey = CY + 4 + lift
    EX = 54
    for ex in (fx - EX, fx + EX):
        F.shade(F.mell((ex, ey - 6), (40, 22), blur=10), C["shadow"], 0.45)       # deep sockets, heavy lids
        F.shade(F.mell((ex - 2, ey + 64), (40, 26), blur=18), C["blush"], 0.35)    # soft blush
    F.shade(F.mell((fx + 96, ey + 82), (30, 62), ang=18, blur=20), C["shadow"], 0.35)   # cheek hollow
    F.shade(F.mell((fx - 92, ey + 82), (26, 56), ang=-18, blur=16), C["shadow"], 0.22)
    F.shade(F.mell((fx - 74, ey + 44), (34, 20), ang=-15, blur=16), hi, 0.18)          # cheekbone light
    # long straight nose
    F.shade(F.mline([(fx + 12, ey - 22), (fx + 15, ey + 60), (fx + 20, ey + 98)], 12, 9, blur=6), C["shadow"], 0.55)
    F.shade(F.mline([(fx - 4, ey - 26), (fx - 3, ey + 84)], 10, 9, blur=7), hi, 0.3)
    F.shade(F.mell((fx, ey + 100), (19, 13), blur=6), hi, 0.3)
    F.shade(F.mell((fx + 2, ey + 118), (24, 8), blur=5), C["shadow"], 0.6)
    for sgn in (-1, 1):
        F.shade(F.mell((fx + sgn * 20, ey + 106), (9, 8), blur=4), C["shadow"], 0.45)
    F.shade(F.mline([(fx, ey + 122), (fx, ey + 138)], 10, 10, blur=4), C["shadow"], 0.22)  # philtrum
    my = ey + 152
    F.shade(F.mell((fx, my + 24), (28, 8), blur=6), C["shadow"], 0.45)          # under-lip
    F.shade(F.mell((fx - 6, my + 56), (26, 14), blur=12), hi, 0.2)            # chin
    F.shade(F.mell((fx - 34, CY - 112 + lift), (70, 34), blur=30), hi, 0.15)   # forehead
    up = [(fx - 34, my), (fx - 15, my - 11), (fx, my - 6), (fx + 15, my - 11), (fx + 34, my), (fx, my + 2)]
    lo = [(fx - 32, my + 1), (fx - 15, my + 16), (fx + 15, my + 16), (fx + 32, my + 1), (fx, my + 3)]
    eyes = s["eyes"]
    AL = lambda ex: [(ex - 31, ey + 2), (ex - 10, ey - 11), (ex + 12, ey - 11), (ex + 31, ey - 1), (ex + 10, ey + 9),
                     (ex - 12, ey + 9)]
    painterize(F, seed + 3, passes=((3500, 22, 5, 9), (5000, 12, 3, 6)), jitter=0.025, hue=0.006,
               angle_noise=0.3, edge_fuzz=False, highlight=0.02, soft=0.3)
    if eyes in ("open", "down"):  # eye whites after the brushwork so strokes don't smear them
        for ex in (fx - EX, fx + EX):
            F.paint(F.mpoly(AL(ex), blur=1.8), mix(C["skin"], hexc("#efe4da"), 0.45))
    # soft gouache details: no outlines, just darker / lighter planes
    F.paint(F.mpoly(lo, blur=2.0), mix(C["lips"], hexc("#ffffff"), 0.08))
    F.paint(F.mpoly(up, blur=2.0), mix(C["lips"], hexc("#000000"), 0.18))
    dark = mix(hexc("#2c1915"), C["shadow"], 0.2)
    for side, ex in ((-1, fx - EX), (1, fx + EX)):
        inner = ex - side * 30
        outer = ex + side * 38
        bpts = [(inner, ey - 31), (ex - side * 4, ey - 39), (outer, ey - 34)]   # straight, close to the eye
        F.paint(F.mline(bpts, 11, 4, blur=2.2), mix(brow, C["skin"], 0.2), 0.9)
        if eyes == "closed":
            lid = [(ex - 30, ey - 1), (ex - 10, ey + 7), (ex + 12, ey + 8), (ex + 30, ey)]
            F.paint(F.mline(lid, 5, 6, blur=2.2), dark, 0.75)
        else:
            am = F.mpoly(AL(ex), blur=1.4)
            iy = ey - (1 if eyes == "open" else -4)
            F.paint(F.mell((ex + turn * 8, iy), (14, 14), blur=1.4) * am, C["iris"])
            F.paint(F.mell((ex + turn * 8, iy), (6, 6), blur=1.2) * am, hexc("#140b08"))
            F.paint(F.mell((ex + turn * 8 - 5, iy - 5), (3, 3), blur=1.0) * am, hexc("#f4ece4"), 0.8)
            lid_y = -11 if eyes == "open" else -2
            top = [(ex - 33, ey + 3), (ex - 10, ey + lid_y), (ex + 12, ey + lid_y), (ex + 33, ey)]
            if eyes == "down":
                F.paint(F.mpoly(top + [(ex + 12, ey - 14), (ex - 10, ey - 14)], blur=2), C["skin"])
            F.paint(F.mline(top, 6, 7, blur=2.0), dark, 0.9)
            F.shade(F.mline([(ex - 30, ey - 17), (ex, ey - 22), (ex + 30, ey - 15)], 5, 4, blur=2.5), C["shadow"], 0.7)
            F.paint(F.mline([(ex - 26, ey + 11), (ex, ey + 14), (ex + 26, ey + 10)], 4, 3, blur=2.5), C["shadow"], 0.35)
    for sgn in (-1, 1):
        F.paint(F.mell((fx + sgn * 11, ey + 110), (6, 4), ang=-sgn * 20, blur=2.5), C["shadow"] * 0.6, 0.75)
    F.paint(F.mline([(fx - 32, my + 1), (fx - 14, my + 3), (fx, my + 2), (fx + 14, my + 3), (fx + 32, my + 1)],
                    3, 2, blur=2.0), mix(C["lips"], hexc("#2a0c08"), 0.45), 0.8)
    F.paint(F.mell((fx + 4, my + 10), (13, 4), blur=3), hexc("#f6d8cc"), 0.4)

    # ---------------- front hair ----------------
    FH = Layer(PW, PH)
    for poly in front_polys:
        FH.paint(FH.mpoly(_p(poly, dy=lift), blur=1.5), C["hair"])
    if FH.a.max() > 0:
        FH.shade(FH.mell((CX - 70, CY - 210 + lift), (110, 50), blur=30), C["hair_hi"], 0.35)
        painterize(FH, seed + 4, passes=((2500, 36, 5, 11), (3500, 18, 3, 6)), angle=hair_ang,
                   angle_noise=0.14, jitter=0.12, highlight=0.06, hl_col=C["hair_hi"])
        rngh = np.random.default_rng(seed + 11)
        for _ in range(0):  # glossy strands (off: they fanned out at the crown)
            a0 = rngh.uniform(math.pi * 1.1, math.pi * 1.9)
            r0 = rngh.uniform(90, 170)
            pts = [(CX + math.cos(a0) * r0 * k / 2, CY - 300 + lift + 60 + math.sin(a0 + 0.5) * 0 + k * 45) for k in range(3)]
            FH.shade(FH.mline(pts, 3, 1, blur=1.2), C["hair_hi"], 0.4)

    # ---------------- accessories on head ----------------
    A = Layer(PW, PH)
    acc = s["acc"]
    if "headband" in acc:
        A.paint(A.mline([(CX - 165, CY - 95 + lift), (CX, CY - 132 + lift), (CX + 168, CY - 95 + lift)], 14, 14,
                        blur=1), hexc("#e9c87a"))
        A.paint(A.mell((CX + 110, CY - 115 + lift), (16, 16), blur=1), hexc("#b8322c"))
        feather = [(CX + 120, CY - 120 + lift), (CX + 190, CY - 260 + lift), (CX + 250, CY - 360 + lift),
                   (CX + 200, CY - 250 + lift), (CX + 140, CY - 130 + lift)]
        A.paint(A.mpoly(feather, blur=2), hexc("#f6e9dc"))
    if "hat" in acc:
        A.paint(A.mell((CX + 70, CY - 205 + lift), (230, 48), ang=-14, blur=1.5), C.get("cloth", hexc("#2a1a1a")))
        A.paint(A.mpoly([(CX - 60, CY - 210 + lift), (CX - 40, CY - 300 + lift), (CX + 140, CY - 330 + lift),
                         (CX + 190, CY - 260 + lift), (CX + 200, CY - 230 + lift)], blur=1.5),
                C.get("cloth", hexc("#2a1a1a")))
        A.paint(A.mline([(CX - 50, CY - 235 + lift), (CX + 80, CY - 270 + lift), (CX + 200, CY - 262 + lift)], 14,
                        14, blur=1), hexc("#b8322c"))
    if "bonnet" in acc:
        bon = [(-250, -10), (-238, -228), (-120, -312), (120, -312), (238, -228), (250, -10), (262, 200),
               (172, 214), (156, 10), (126, -118), (0, -160), (-126, -118), (-156, 10), (-172, 214), (-262, 200)]
        bon = [(x * 1.08, y * 1.04 - 8) for x, y in bon]
        A.paint(A.mpoly(_p(bon, dy=lift), blur=1.5), hexc("#f6f0e6"))
        A.shade(A.mpoly(_p([(150, 0), (126, -118), (0, -160), (-126, -118), (-150, 0), (-120, -90), (0, -130),
                            (120, -90)], dy=lift), blur=10), hexc("#c9b9a6"), 0.7)
        A.shade(A.mell((CX + 200, CY + 60 + lift), (60, 150), blur=30), hexc("#cdbfae"), 0.5)
    if "scarf" in acc:
        sc = [(-178, -60), (-172, -205), (-80, -282), (80, -282), (172, -205), (178, -60), (140, -118),
              (0, -170), (-140, -118)]
        A.paint(A.mpoly(_p(sc, dy=lift), blur=1.5), hexc("#a8452c"))
        for i in range(30):
            rr = np.random.default_rng(seed + 50 + i).random(2)
            A.shade(A.mell((CX - 150 + rr[0] * 300, CY - 260 + rr[1] * 140 + lift), (6, 6), blur=1),
                    hexc("#f2d39a"), 0.9)
        braid = [(CX + 158 + 14 * k, CY + 110 + 54 * k + lift * (1 - k / 8)) for k in range(9)]
        for k, (bx, by) in enumerate(braid):
            A.paint(A.mell((bx, by), (34, 40), ang=(25 if k % 2 else -25), blur=1.5), C["hair"])
            A.shade(A.mell((bx - 6, by - 8), (14, 10), ang=-25, blur=4), C["hair_hi"], 0.6)
    if "bonnet" in acc:
        painterize(A, seed + 5, passes=((2500, 40, 6, 12), (2500, 20, 3, 6)), jitter=0.02, edge_fuzz=False,
                   angle=angle_radial(PW, PH, CX, CY - 60 + lift) + np.float32(np.pi / 2), angle_noise=0.15,
                   soft=0.45)
    elif "headband" in acc or "hat" in acc or "scarf" in acc:
        painterize(A, seed + 5, passes=((2200, 22, 4, 9), (2500, 12, 2, 5)), jitter=0.05, highlight=0.03)
    if "earrings" in acc:
        for sgn in (-1, 1):
            A.paint(A.mell((CX + sgn * RX * 1.0, CY + 90 + lift), (10, 10), blur=0.8), hexc("#efe6da"))
    if "hoops" in acc:
        for sgn in (-1, 1):
            m = np.zeros((PH, PW), np.uint8)
            cv2.circle(m, (int(CX + sgn * RX * 1.02), int(CY + 120 + lift)), 40, 255, 6, cv2.LINE_AA)
            A.paint(m.astype(np.float32) / 255, hexc("#e2b44b"))
    if "clip" in acc:
        A.paint(A.mpoly([(CX - 140, CY - 160 + lift), (CX - 70, CY - 190 + lift), (CX - 64, CY - 172 + lift),
                         (CX - 134, CY - 142 + lift)], smooth=False, blur=1), hexc("#e9a23b"))

    # ---------------- assemble ----------------
    pivot = (CX, CY + 300)
    M = cv2.getRotationMatrix2D(pivot, -s["tilt"], 1.0)
    out = Layer(PW, PH)
    out.over(BH, M)
    out.over(B)
    head = Layer(PW, PH)
    head.over(F)
    head.over(FH)
    head.over(A)
    out.over(head, M)
    return out.rgba()


if __name__ == "__main__":
    import sys
    spec = dict(hair_style=sys.argv[1] if len(sys.argv) > 1 else "bob")
    img = draw_portrait(spec)
    bg = np.ones((PH, PW, 3), np.float32) * hexc("#e3b73a")
    comp = img[..., :3] + bg * (1 - img[..., 3:4])
    cv2.imwrite("/tmp/portrait.png", (np.clip(comp, 0, 1)[..., ::-1] * 255).astype(np.uint8))
