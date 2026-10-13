"""Scene building (static sprites, cached) and per-frame drawing with motion."""
import math
import numpy as np
import cv2

from flat import Layer, hexc, mix, INK
from figures import make_figure, SKINS
import sets
from sets import C
from content import SCENES
from timing import W, H, LENGTHS, TR, boundaries


# ----------------------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, s, d):
    return clamp((t - s) / d)


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_io(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def blit(dst, spr, x, y, scale=1.0, rot=0.0, alpha=1.0, anchor=(0.5, 0.5)):
    if alpha <= 0.003 or scale <= 0.002:
        return
    h, w = spr.shape[:2]
    ax, ay = anchor[0] * w, anchor[1] * h
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


def caption_card(ts, font, cap):
    """Cream ribbon with an alpana-dot border: small caps place/year, English line, Bengali line."""
    a = ts(cap["when"], font("sans", 28, 700), hexc("#b23a2a"), tracking=4)
    b = ts(cap["en"], font("serif_i", 50, 600), INK)
    c = ts(cap["bn"], font("bn", 46, 600), hexc("#5a2a1e"))
    w = int(max(a.shape[1], b.shape[1], c.shape[1]) + 70)
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
        reg = spr[y:y + hh, 40:40 + ww]
        reg[:] = t + reg * (1 - t[..., 3:4])
        y += hh - (10 if t is a else 6)
    return spr


# ----------------------------------------------------------------------------- scene 1: 1975 bonedi bari
LAAL_PAAR = dict(saree="#f6efe2", border="#c8281e", blouse="#c8281e", sindoor=True)


def S1_PEOPLE():
    sk = SKINS
    return [
        # (spec, height, x, feet_y, anim, flip)
        (dict(kind="priest", skin=sk[2], hair="bald"), 230, 1310, 708, "sway", True),
        (dict(kind="seated_woman", **LAAL_PAAR, skin=sk[1], arms="fold"), 190, 560, 712, None, False),
        (dict(kind="seated_woman", saree="#f6efe2", border="#3f6fb5", blouse="#f6efe2", hair="grey_bun",
              hair_col="#d9d4cc", glasses=True, skin=sk[0], arms="fold"), 190, 1390, 712, None, False),
        (dict(kind="woman", saree="#f2c14e", border="#c8281e", blouse="#2f7a6e", hair="braid", skin=sk[1],
              pattern="dots", pat_col="#c8281e"), 150, 1520, 712, "clap", False),
        (dict(kind="dhaki", kurta="#f6f0e2", hair="short", mustache=True, skin=sk[3]), 300, 250, 880, "drum", False),
        (dict(kind="dhaki", kurta="#f2d27a", hair="short", mustache=True, skin=sk[2]), 300, 1690, 880, "drum", True),
        (dict(kind="woman", **LAAL_PAAR, skin=sk[0], arms="clap"), 290, 470, 920, "clap", False),
        (dict(kind="man", kurta="#f6f0e2", hair="short", mustache=True, skin=sk[2], arms="fold"), 300, 640, 935,
         None, False),
        (dict(kind="woman", **LAAL_PAAR, skin=sk[2], arms="fold", hair="open"), 290, 1260, 930, None, False),
        (dict(kind="woman", saree="#e3567e", border="#f2c14e", blouse="#f2c14e", pattern="buti", pat_col="#f8e3a0",
              skin=sk[1], arms="clap", sindoor=True), 290, 1450, 920, "clap", False),
        (dict(kind="woman", **LAAL_PAAR, skin=sk[1], arms="clap"), 380, 130, 1150, "clap", False),
        (dict(kind="man", kurta="#c8d8ec", pattern="checks", pat_col="#3f6fb5", hair="short", skin=sk[3]), 330,
         900, 1150, None, False),
        (dict(kind="woman", saree="#2f7a6e", border="#f2c14e", blouse="#f2c14e", pattern="dots",
              pat_col="#f6efe2", skin=sk[2], hair="braid"), 200, 1060, 1085, "clap", False),
        (dict(kind="woman", **LAAL_PAAR, skin=sk[3], arms="fold"), 380, 1790, 1150, None, False),
    ]


SAREES_1975 = [("#f6efe2", "#c8281e", None, None), ("#f6efe2", "#c8281e", None, None),
               ("#f6efe2", "#2f7a6e", None, None), ("#e3567e", "#f2c14e", "buti", "#f8e3a0"),
               ("#2f7a6e", "#f2c14e", "dots", "#f6efe2"), ("#f2c14e", "#c8281e", "dots", "#c8281e"),
               ("#3a6db0", "#f2c14e", "buti", "#f6efe2"), ("#f6efe2", "#3f6fb5", "stripes", "#9cc0e4"),
               ("#7a1f22", "#f2c14e", "buti", "#f2c14e"), ("#f39ab4", "#c8281e", "dots", "#fbf7ee")]
KURTAS_1975 = [("#f6f0e2", None, None), ("#f6f0e2", None, None), ("#f2d27a", None, None),
               ("#c8d8ec", "checks", "#3f6fb5"), ("#e9dcc4", "dots", "#7a1f22")]


def random_person(rng, h, era="1975"):
    sk = SKINS[rng.integers(0, len(SKINS))]
    r = rng.random()
    if r < 0.58:
        sa, bo, pa, pc = SAREES_1975[rng.integers(0, len(SAREES_1975))]
        spec = dict(kind="woman", saree=sa, border=bo, blouse=[bo, "#2f7a6e", "#f2c14e", "#c8281e"][rng.integers(0, 4)],
                    pattern=pa, pat_col=pc, skin=sk, sindoor=rng.random() < 0.6,
                    hair=["bun", "bun", "braid", "open", "grey_bun"][rng.integers(0, 5)],
                    arms=["fold", "clap", "down", "clap"][rng.integers(0, 4)])
        if spec["hair"] == "grey_bun":
            spec.update(hair_col="#d9d4cc", glasses=rng.random() < 0.5)
    else:
        ku, pa, pc = KURTAS_1975[rng.integers(0, len(KURTAS_1975))]
        spec = dict(kind="man", kurta=ku, pattern=pa, pat_col=pc, skin=sk, hair="short",
                    mustache=rng.random() < 0.6, glasses=rng.random() < 0.25,
                    arms=["fold", "down", "clap"][rng.integers(0, 3)])
    if rng.random() < 0.12:
        h = h * 0.62  # child
        spec["sindoor"] = False
    return spec, h


def crowd_1975(rng):
    out = []
    # seated / standing rows on the dalan, kept clear of the protima
    for x in list(np.linspace(40, 560, 6)) + list(np.linspace(1360, 1880, 6)):
        spec, h = random_person(rng, rng.uniform(170, 200))
        if rng.random() < 0.4 and spec["kind"] == "woman":
            spec["kind"] = "seated_woman"
        out.append((spec, h, x + rng.uniform(-20, 20), 712, spec["arms"] if spec["arms"] == "clap" else None, False))
    # courtyard: three loose rows, bigger as they come forward
    for y, n, h0 in ((820, 9, 250), (960, 9, 300), (1110, 8, 370)):
        xs = np.linspace(60, 1860, n) + rng.uniform(-55, 55, n)
        for x in xs:
            if y < 900 and 760 < x < 1160:
                continue  # keep the view to the goddess open
            spec, h = random_person(rng, h0 * rng.uniform(0.94, 1.06))
            out.append((spec, h, x, y + rng.uniform(-20, 20), "clap" if spec["arms"] == "clap" else None,
                        rng.random() < 0.5))
    return out


def build_people(people, nphase=8):
    out = []
    for spec, h, x, y, anim, fl in people:
        frames = []
        for p in range(nphase if anim in ("clap",) else 1):
            s = dict(spec)
            if anim == "clap":
                s["arms"] = "clap"
                s["phase"] = p / nphase
            spr = make_figure(s, h)
            frames.append(flip(spr) if fl else spr)
        out.append(dict(frames=frames, x=x, y=y, anim=anim, seed=hash((x, y)) % 100 / 100))
    return out


def build_scene1():
    bg = sets.thakur_dalan()
    gl = Layer(W, H)
    sets.garland_swag(gl, 60, 1860, 128, sag=70)
    A = dict(bg=bg.rgba(), garland=gl.rgba())
    A["halo"] = sets.chalchitra(292)
    A["durga"] = sets.durga_riding(470)
    A["lakshmi"] = sets.deity_woman(235, "#f39ab4", "#e7b23a", attr="lotus")
    A["saraswati"] = sets.deity_woman(235, "#fbf7ee", "#3f6fb5", skin="#f6e7c8", attr="veena")
    A["ganesh"] = sets.ganesh(210)
    A["kartik"] = sets.kartik(215)
    A["lion"] = sets.lion(110)
    A["people"] = build_people(S1_PEOPLE() + crowd_1975(np.random.default_rng(1975)))
    return A


def draw_people(fr, people, t, beat=0.625):
    for p in sorted(people, key=lambda q: q["y"]):
        fs = p["frames"]
        rot = 0.0
        if p["anim"] == "clap":
            spr = fs[int((t / beat + p["seed"]) * len(fs)) % len(fs)]
        else:
            spr = fs[0]
        if p["anim"] in ("sway", "drum"):
            rot = 2.5 * math.sin((t / beat + p["seed"]) * math.pi)
        blit(fr, spr, p["x"], p["y"], rot=rot, anchor=(0.5, 1.0 - 18 / spr.shape[0]))


def draw_scene1(A, lt):
    fr = A["bg"][..., :3].copy()
    blit(fr, A["halo"], W / 2, 540, anchor=(0.5, 1.0 - 20 / A["halo"].shape[0]))
    bob = 3 * math.sin(lt * 1.2)
    for key, x, y in (("lakshmi", 752, 612), ("saraswati", 1192, 612), ("ganesh", 690, 612), ("kartik", 1236, 612),
                      ("durga", 958, 612)):
        spr = A[key]
        blit(fr, spr, x, y + (bob if key == "durga" else 0), anchor=(0.5, 1.0 - 18 / spr.shape[0]))
    blit(fr, A["garland"], W / 2, H / 2)
    draw_people(fr, A["people"], lt)
    return fr


# ----------------------------------------------------------------------------- assembly
def build(ts, font):
    A = {"s1": build_scene1()}
    A["caps"] = [caption_card(ts, font, s["caption"]) if s.get("caption") else None for s in SCENES]
    return A


def camera(fr, z, cx=W / 2, cy=H / 2, dx=0.0):
    M = np.array([[z, 0, cx * (1 - z) + dx], [0, z, cy * (1 - z)]], np.float32)
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def draw(A, t):
    B = boundaries()
    k = max(j for j, b in enumerate(B) if t >= b)
    lt = t - B[k]
    k = 1  # TODO: other scenes; checkpoint renders scene 1 only
    fr = draw_scene1(A["s1"], lt)
    fr = camera(fr, 1.0 + 0.04 * clamp(lt / LENGTHS[1]), cy=H * 0.42)
    cap = A["caps"][k]
    if cap is not None:
        p = ease_out(prog(lt, 0.8, 0.8))
        blit(fr, cap, 48, 44 + (1 - p) * -40, alpha=p, anchor=(0, 0))
    return fr
