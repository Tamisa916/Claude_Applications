"""Pre-rendered painterly assets: backgrounds, flowers, props, paper cards."""
import math
import numpy as np
import cv2
from paint import Layer, painterize, hexc, mix, flow_field, angle_radial
from timing import W, H

INK = hexc("#2a1612")
CREAM = hexc("#fbf0dc")


# --------------------------------------------------------------------------- backgrounds
def build_bg(col, seed, kind=None):
    L = Layer(W, H)
    base = hexc(col)
    L.paint(np.ones((H, W), np.float32), base)
    rng = np.random.default_rng(seed)
    for i in range(16):
        light = rng.random() < 0.55
        c = mix(base, hexc("#fff2cf") if light else hexc("#4a1c0c"), 0.16 if light else 0.12)
        m = L.mell((rng.uniform(0, W), rng.uniform(0, H)), (rng.uniform(150, 420), rng.uniform(150, 420)),
                   rng.uniform(0, 180), blur=90)
        L.paint(m, c)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    edge = np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1)
    L.paint(edge * 0.5, mix(base, hexc("#3a1408"), 0.35))
    if kind == "spot":
        L.paint(L.mell((W / 2, 820), (520, 640), blur=160), mix(base, hexc("#e08a5a"), 0.45))
    if kind == "wallpaper":
        for r, y in enumerate(range(60, H, 130)):
            for x in range(-60 + (r % 2) * 75, W + 80, 150):
                for k in range(4):
                    a = k * math.pi / 2 + 0.4
                    L.paint(L.mell((x + 14 * math.cos(a), y + 14 * math.sin(a)), (11, 8), math.degrees(a), blur=1.5),
                            hexc("#fbe6cf"))
                L.paint(L.mell((x, y), (6, 6), blur=1), hexc("#d4573e"))
                L.paint(L.mline([(x + 50, y + 55), (x + 75, y + 70)], 4, 2, smooth=False, blur=1), hexc("#c98a5e"), 0.7)
    if kind == "paper":
        for y in range(240, H, 74):
            L.paint(L.mline([(0, y), (W, y + 3)], 3, 3, smooth=False, blur=0.8), hexc("#d98d86"), 0.55)
        L.paint(L.mline([(150, 0), (152, H)], 4, 4, smooth=False, blur=0.8), hexc("#c3423a"), 0.7)
        for y in (420, 960, 1500):
            L.paint(L.mell((70, y), (22, 22), blur=1), mix(base, hexc("#5a2a1a"), 0.35))
    painterize(L, seed + 1, passes=((5500, 95, 14, 26), (8000, 46, 6, 12)),
               angle=flow_field(W, H, seed, base=-0.55, amp=0.8, cell=320), angle_noise=0.18,
               jitter=0.035, edge_fuzz=False, soft=0.12, sample_thresh=0.0)
    return np.clip(L.rgb, 0, 1).astype(np.float32)


# --------------------------------------------------------------------------- flowers
def build_flower(kind, seed, R=170):
    rng = np.random.default_rng(seed)
    S = int(R * 2.7)
    L = Layer(S, S)
    c = S / 2
    if kind in ("peony_pink", "peony_white", "rose_red", "hibiscus"):
        light, dark, centre = {
            "peony_pink": ("#f8cfd3", "#e07a8a", "#e9c55a"),
            "peony_white": ("#fffaf2", "#d9cbb8", "#e2bf55"),
            "rose_red": ("#e0473f", "#7e1418", "#5a0c10"),
            "hibiscus": ("#f2603a", "#a8201c", "#f6d36a"),
        }[kind]
        light, dark, centre = hexc(light), hexc(dark), hexc(centre)
        for li, rr in enumerate([1.0, 0.86, 0.7, 0.54, 0.38, 0.24]):
            for k in range(11 - li):
                a = rng.uniform(0, math.tau)
                d = R * rr * 0.38
                px, py = c + math.cos(a) * d, c + math.sin(a) * d
                col = mix(dark, light, np.clip(0.35 + 0.65 * li / 5 + rng.normal(0, 0.12), 0, 1))
                if kind == "rose_red":
                    col = mix(light, dark, np.clip(li / 5 + rng.normal(0, 0.1), 0, 1))
                L.paint(L.mell((px, py), (R * rr * 0.62, R * rr * 0.42), math.degrees(a) + 90, blur=2.5), col)
                L.shade(L.mline([(px - math.cos(a + 1.57) * R * rr * 0.4, py - math.sin(a + 1.57) * R * rr * 0.4),
                                 (px + math.cos(a) * R * rr * 0.2, py + math.sin(a) * R * rr * 0.2),
                                 (px + math.cos(a + 1.57) * R * rr * 0.4, py + math.sin(a + 1.57) * R * rr * 0.4)],
                                4, 2, blur=2), mix(light, hexc("#ffffff"), 0.5), 0.5)
        if kind == "rose_red":
            for k in range(5):
                r0 = R * (0.08 + k * 0.07)
                L.shade(L.mline([(c + r0 * math.cos(t), c + r0 * math.sin(t) * 0.8)
                                 for t in np.linspace(k, k + 4.2, 8)], 6, 3, blur=1.5), dark * 0.7, 0.8)
        else:
            for k in range(26):
                a = rng.uniform(0, math.tau)
                d = rng.uniform(0, R * 0.16)
                L.paint(L.mell((c + math.cos(a) * d, c + math.sin(a) * d), (7, 4), math.degrees(a), blur=1), centre)
        painterize(L, seed, passes=((1800, R * 0.16, 4, 9), (2200, R * 0.08, 2, 5)), jitter=0.05, highlight=0.04)
    elif kind in ("blossom_white", "blossom_pink"):
        col = hexc("#fff7f0") if kind == "blossom_white" else hexc("#f6c2c6")
        for k in range(5):
            a = k / 5 * math.tau + rng.uniform(-0.2, 0.2)
            L.paint(L.mell((c + math.cos(a) * R * 0.45, c + math.sin(a) * R * 0.45), (R * 0.48, R * 0.36),
                           math.degrees(a), blur=1.5), mix(col, hexc("#e8a9b0"), rng.uniform(0, 0.3)))
        L.paint(L.mell((c, c), (R * 0.18, R * 0.18), blur=1.5), hexc("#c8603a"))
        painterize(L, seed, passes=((500, R * 0.3, 2, 5),), jitter=0.04)
    elif kind == "leaf":
        pts = [(c - R * 1.2, c), (c - R * 0.3, c - R * 0.42), (c + R * 0.6, c - R * 0.3), (c + R * 1.25, c),
               (c + R * 0.6, c + R * 0.3), (c - R * 0.3, c + R * 0.42)]
        L.paint(L.mpoly(pts, blur=2), hexc("#5f7a3e"))
        L.shade(L.mpoly([(p[0], min(p[1], c)) for p in pts], blur=6), hexc("#8ea25a"), 0.5)
        L.paint(L.mline([(c - R * 1.1, c), (c + R * 1.1, c)], 3, 1, smooth=False, blur=1), hexc("#3e5428"), 0.7)
        painterize(L, seed, passes=((900, R * 0.25, 3, 7),), jitter=0.06)
    return L.rgba()


# --------------------------------------------------------------------------- props
def build_cameo(portrait):
    """1900s: the portrait set inside a gilded oval frame (an 'ornament')."""
    SW, SH = 1000, 1240
    L = Layer(SW, SH)
    cx, cy = SW / 2, 600
    ax, ay = 400, 540
    L.paint(L.mell((cx, cy), (ax, ay), blur=2), hexc("#f3ddb0"))
    L.shade(L.mell((cx, cy + 120), (ax, ay), blur=120), hexc("#c99a4a"), 0.6)
    painterize(L, 5, passes=((2500, 50, 8, 16),), jitter=0.03, edge_fuzz=False, soft=0.2)
    P = Layer(SW, SH)
    off = ((SW - 900) // 2, 40)
    P.rgb[off[1]:off[1] + 1200, off[0]:off[0] + 900] = portrait[..., :3]
    P.a[off[1]:off[1] + 1200, off[0]:off[0] + 900] = portrait[..., 3]
    m = L.mell((cx, cy), (ax - 4, ay - 4), blur=1.5)
    P.rgb *= m[..., None]
    P.a *= m
    L.over(P)
    R = Layer(SW, SH)
    ring = np.zeros((SH, SW), np.uint8)
    cv2.ellipse(ring, (int(cx), int(cy)), (ax + 18, ay + 18), 0, 0, 360, 255, 54, cv2.LINE_AA)
    R.paint(ring.astype(np.float32) / 255, hexc("#d4a23c"))
    hl = np.zeros((SH, SW), np.uint8)
    cv2.ellipse(hl, (int(cx), int(cy)), (ax + 4, ay + 4), 0, 200, 340, 255, 10, cv2.LINE_AA)
    R.shade(cv2.GaussianBlur(hl.astype(np.float32) / 255, (0, 0), 3), hexc("#fbe7a6"), 0.8)
    sh = np.zeros((SH, SW), np.uint8)
    cv2.ellipse(sh, (int(cx), int(cy)), (ax + 34, ay + 34), 0, 20, 160, 255, 14, cv2.LINE_AA)
    R.shade(cv2.GaussianBlur(sh.astype(np.float32) / 255, (0, 0), 4), hexc("#8a5a18"), 0.7)
    for k in range(44):
        t = k / 44 * math.tau
        R.paint(R.mell((cx + (ax + 18) * math.cos(t), cy + (ay + 18) * math.sin(t)), (9, 9), blur=1),
                hexc("#f6d980"))
    R.paint(R.mpoly([(cx - 70, cy - ay - 10), (cx, cy - ay - 90), (cx + 70, cy - ay - 10), (cx, cy - ay + 20)],
                    blur=1.5), hexc("#d4a23c"))
    R.paint(R.mell((cx, cy - ay - 40), (20, 20), blur=1), hexc("#b8322c"))
    painterize(R, 6, passes=((2500, 16, 3, 7),), jitter=0.06, highlight=0.08, edge_fuzz=False)
    L.over(R)
    return L.rgba()


def build_sun(R=310, col="#f7cf6a"):
    S = int(R * 2.3)
    L = Layer(S, S)
    L.paint(L.mell((S / 2, S / 2), (R, R), blur=3), hexc(col))
    L.shade(L.mell((S / 2 - R * 0.2, S / 2 - R * 0.2), (R * 0.6, R * 0.6), blur=80), hexc("#fff0c0"), 0.6)
    painterize(L, 8, passes=((2500, 40, 8, 16),), angle=angle_radial(S, S, S / 2, S / 2) + np.float32(np.pi / 2),
               jitter=0.04, angle_noise=0.2)
    return L.rgba()


def build_field():
    L = Layer(W, 900)
    L.paint(L.mpoly([(0, 120), (300, 70), (700, 110), (W, 60), (W, 900), (0, 900)], blur=3), hexc("#b8762c"))
    for i in range(6):
        L.shade(L.mline([(0, 160 + i * 110), (W, 140 + i * 115)], 30, 30, smooth=False, blur=20),
                hexc("#e0a64a" if i % 2 else "#8e5420"), 0.5)
    painterize(L, 9, passes=((5000, 70, 8, 16),), angle=np.full((900, W), 0.05, np.float32), angle_noise=0.12)
    return L.rgba()


def build_wheat(seed, h=760):
    rng = np.random.default_rng(seed)
    L = Layer(160, h)
    base = (80, h)
    top = (80 + rng.uniform(-30, 30), 120)
    L.paint(L.mline([base, ((base[0] + top[0]) / 2 + rng.uniform(-10, 10), h * 0.5), top], 6, 3, blur=1),
            hexc("#c08a38"))
    for k in range(13):
        t = k / 13
        y = 120 - 110 * t + 0
        for sgn in (-1, 1):
            L.paint(L.mell((top[0] + sgn * 13, top[1] - t * 110 + 10), (10, 22), sgn * 25, blur=1.2),
                    mix(hexc("#e9b551"), hexc("#f8dc8a"), rng.random()))
    L.paint(L.mline([(top[0], top[1] - 110), (top[0] + 6, top[1] - 170)], 2, 1, smooth=False, blur=1), hexc("#e9c070"))
    painterize(L, seed, passes=((500, 14, 2, 5),), jitter=0.06)
    return L.rgba()


def build_sunburst(col):
    S = 2400
    L = Layer(S, S)
    base = hexc(col)
    c = S / 2
    for k in range(28):
        a0 = k / 28 * math.tau
        a1 = (k + 0.5) / 28 * math.tau
        pts = [(c, c), (c + S * math.cos(a0), c + S * math.sin(a0)), (c + S * math.cos(a1), c + S * math.sin(a1))]
        L.paint(L.mpoly(pts, smooth=False, blur=1.5), mix(base, hexc("#fff0d8"), 0.22))
    L.a[:] = np.maximum(L.a, 0)
    painterize(L, 12, passes=((6000, 60, 8, 14),), angle=angle_radial(S, S, c, c), angle_noise=0.08, jitter=0.03,
               edge_fuzz=False)
    for r in (420, 470, 520):
        m = np.zeros((S, S), np.uint8)
        cv2.circle(m, (int(c), int(c)), r, 255, 6, cv2.LINE_AA)
        L.paint(m.astype(np.float32) / 255, hexc("#f2cf7a"), 0.85)
    return L.rgba()


def build_bubble(r=18):
    S = r * 2 + 8
    L = Layer(S, S)
    m = np.zeros((S, S), np.uint8)
    cv2.circle(m, (S // 2, S // 2), r, 255, 3, cv2.LINE_AA)
    L.paint(m.astype(np.float32) / 255, hexc("#fff4dc"), 0.9)
    L.paint(L.mell((S / 2 - r * 0.4, S / 2 - r * 0.4), (r * 0.25, r * 0.18), -30, blur=1), hexc("#ffffff"))
    return L.rgba()


def build_glow(col, r=60):
    S = r * 6
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    d = np.hypot(xx - S / 2, yy - S / 2)
    a = np.exp(-(d / r) ** 2) * 0.9 + np.exp(-(d / (r * 0.25)) ** 2)
    a = np.clip(a, 0, 1)
    c = hexc(col)
    return np.dstack([c * a[..., None], a]).astype(np.float32)


def build_branch(side, seed):
    rng = np.random.default_rng(seed)
    BW, BH = 760, 760
    L = Layer(BW, BH)
    x0 = 0 if side < 0 else BW
    blossoms = []

    def grow(p, ang, length, th, depth):
        pts = [p]
        x, y = p
        for k in range(5):
            ang += rng.uniform(-0.25, 0.25)
            x += math.cos(ang) * length / 5
            y += math.sin(ang) * length / 5
            pts.append((x, y))
        L.paint(L.mline(pts, th, max(2, th * 0.4), blur=1), hexc("#4a2a1c"))
        for q in pts[2:]:
            if rng.random() < 0.8:
                blossoms.append(q)
        if depth > 0:
            for _ in range(2):
                grow(pts[rng.integers(2, 5)], ang + rng.uniform(-0.8, 0.8), length * 0.6, th * 0.55, depth - 1)

    grow((x0, 40), (0.35 if side < 0 else math.pi - 0.35), 620, 26, 2)
    painterize(L, seed, passes=((1200, 14, 3, 7),), jitter=0.06, edge_fuzz=False)
    return L, blossoms


def build_blossom_branch(side, seed, white, pink):
    L, blossoms = build_branch(side, seed)
    out = L.rgba()
    rng = np.random.default_rng(seed + 1)
    for (x, y) in blossoms:
        for _ in range(2):
            spr = white if rng.random() < 0.65 else pink
            s = rng.uniform(0.35, 0.6)
            sp = cv2.resize(spr, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
            h, w = sp.shape[:2]
            px, py = int(x + rng.uniform(-25, 25) - w / 2), int(y + rng.uniform(-25, 25) - h / 2)
            x0, y0, x1, y1 = max(px, 0), max(py, 0), min(px + w, out.shape[1]), min(py + h, out.shape[0])
            if x1 <= x0 or y1 <= y0:
                continue
            sub = sp[y0 - py:y1 - py, x0 - px:x1 - px]
            reg = out[y0:y1, x0:x1]
            reg[..., :3] = sub[..., :3] + reg[..., :3] * (1 - sub[..., 3:4])
            reg[..., 3] = sub[..., 3] + reg[..., 3] * (1 - sub[..., 3])
    return out


def build_house_picture():
    L = Layer(300, 250)
    L.paint(L.mpoly([(0, 0), (300, 0), (300, 250), (0, 250)], smooth=False), hexc("#c8963a"))
    L.paint(L.mpoly([(22, 22), (278, 22), (278, 228), (22, 228)], smooth=False), hexc("#fbe9c8"))
    L.paint(L.mpoly([(22, 170), (278, 160), (278, 228), (22, 228)], smooth=False, blur=1), hexc("#9cb36a"))
    L.paint(L.mpoly([(90, 120), (210, 120), (210, 190), (90, 190)], smooth=False, blur=1), hexc("#f6f0e6"))
    L.paint(L.mpoly([(78, 124), (150, 70), (222, 124)], smooth=False, blur=1), hexc("#c0392b"))
    L.paint(L.mpoly([(138, 150), (162, 150), (162, 190), (138, 190)], smooth=False, blur=1), hexc("#7a3a22"))
    for x in (102, 178):
        L.paint(L.mpoly([(x, 135), (x + 20, 135), (x + 20, 155), (x, 155)], smooth=False, blur=1), hexc("#7fb2c9"))
    painterize(L, 14, passes=((700, 12, 2, 5),), jitter=0.04, edge_fuzz=False)
    return L.rgba()


def build_clock():
    L = Layer(220, 220)
    L.paint(L.mell((110, 110), (100, 100), blur=1), hexc("#d4573e"))
    L.paint(L.mell((110, 110), (82, 82), blur=1), hexc("#fbf0dc"))
    for k in range(12):
        a = k / 12 * math.tau
        L.paint(L.mell((110 + 68 * math.cos(a), 110 + 68 * math.sin(a)), (5, 5), blur=1), INK)
    painterize(L, 15, passes=((500, 10, 2, 4),), jitter=0.04, edge_fuzz=False)
    return L.rgba()


def build_hand(length, th, col="#2a1612"):
    S = length + 20
    L = Layer(th + 8, S)
    L.paint(L.mline([((th + 8) / 2, S - 10), ((th + 8) / 2, 6)], th, max(2, th // 2), smooth=False, blur=0.8), hexc(col))
    return L.rgba()


def build_arcs():
    S = 2000
    L = Layer(S, S // 2 + 200)
    cols = ["#f5e1b4", "#f2c14e", "#ec9a3a", "#d9662b", "#a8461f", "#6e3a1e"]
    for i, r in enumerate(range(1000, 200, -110)):
        L.paint(L.mell((S / 2, S / 2), (r, r), blur=2), hexc(cols[i % len(cols)]))
    painterize(L, 16, passes=((6000, 70, 10, 18),),
               angle=angle_radial(S, S // 2 + 200, S / 2, S / 2) + np.float32(np.pi / 2), angle_noise=0.08,
               jitter=0.03)
    return L.rgba()


def build_plane():
    L = Layer(200, 120)
    L.paint(L.mpoly([(10, 60), (190, 20), (80, 70)], smooth=False, blur=1), hexc("#fbf3e6"))
    L.paint(L.mpoly([(80, 70), (190, 20), (100, 110)], smooth=False, blur=1), hexc("#e3d2b8"))
    L.paint(L.mline([(80, 70), (190, 20)], 2, 2, smooth=False, blur=0.5), hexc("#b49a7a"))
    return L.rgba()


def build_handmaid():
    L = Layer(160, 300)
    L.paint(L.mpoly([(80, 70), (130, 110), (150, 300), (10, 300), (30, 110)], blur=1.5), hexc("#b3161d"))
    L.shade(L.mpoly([(80, 70), (130, 110), (150, 300), (95, 300)], blur=6), hexc("#7a0e12"), 0.6)
    L.paint(L.mpoly([(28, 80), (40, 20), (80, 4), (120, 20), (132, 80), (112, 100), (80, 90), (48, 100)], blur=1.5),
            hexc("#f4ede2"))
    painterize(L, 17, passes=((500, 14, 3, 6),), jitter=0.04, edge_fuzz=False)
    return L.rgba()


def build_petal():
    L = Layer(40, 30)
    L.paint(L.mell((20, 15), (15, 9), 10, blur=1), hexc("#fbe4e2"))
    return L.rgba()


def build_card(w, h, seed=3):
    """Cream paper card + soft shadow (one sprite)."""
    pad = 60
    L = Layer(w + pad * 2, h + pad * 2)
    rng = np.random.default_rng(seed)
    pts = [(pad + rng.uniform(-4, 4), pad + rng.uniform(-4, 4)), (pad + w + rng.uniform(-4, 4), pad + rng.uniform(-4, 4)),
           (pad + w + rng.uniform(-4, 4), pad + h + rng.uniform(-4, 4)), (pad + rng.uniform(-4, 4), pad + h + rng.uniform(-4, 4))]
    sh = L.mpoly([(x + 14, y + 20) for x, y in pts], smooth=False, blur=18)
    L.paint(sh, hexc("#2a1008"), 0.45)
    P = Layer(w + pad * 2, h + pad * 2)
    P.paint(P.mpoly(pts, smooth=False, blur=0.8), CREAM)
    P.shade(P.mell((pad + w * 0.7, pad + h * 0.8), (w * 0.6, h * 0.6), blur=100), hexc("#ecd8b6"), 0.6)
    painterize(P, seed, passes=((2500, 60, 6, 12),), angle=np.full(P.a.shape, 0.05, np.float32), jitter=0.015,
               edge_fuzz=False, soft=0.4)
    L.over(P)
    return L.rgba(), pad


def build_highlight(w, h, col, seed=4):
    L = Layer(w + 20, h + 20)
    rng = np.random.default_rng(seed)
    top = [(10 + x, 10 + rng.uniform(-3, 5)) for x in np.linspace(0, w, 12)]
    bot = [(10 + x, 10 + h + rng.uniform(-5, 3)) for x in np.linspace(w, 0, 12)]
    L.paint(L.mpoly(top + bot, smooth=False, blur=1.2), hexc(col))
    painterize(L, seed, passes=((900, 40, 4, 9),), angle=np.full(L.a.shape, 0.02, np.float32), jitter=0.04,
               angle_noise=0.05)
    return L.rgba()


def build_polaroid(portrait, seed):
    """Square-ish crop of a portrait on a paper mount (for the outro collage)."""
    crop = portrait[100:880, 70:830]
    bg = np.ones((crop.shape[0], crop.shape[1], 3), np.float32)
    return crop, bg
