"""Painterly drawing primitives.

Everything is drawn procedurally: shapes are filled as flat colour, then
re-painted with thousands of short oriented brush strokes so the result reads
like thick gouache / oil on canvas (the look of the reference painting).

Layers store *premultiplied* RGB (float32, 0..1) plus alpha.
"""
import math
import numpy as np
import cv2


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


def mix(a, b, t):
    return a * (1 - t) + b * t


def spline(pts, n=14, closed=True):
    """Catmull-Rom spline through control points -> dense polyline."""
    pts = np.asarray(pts, np.float32)
    N = len(pts)
    out = []
    segs = range(N) if closed else range(N - 1)
    for i in segs:
        if closed:
            p0, p1, p2, p3 = pts[(i - 1) % N], pts[i], pts[(i + 1) % N], pts[(i + 2) % N]
        else:
            p0, p1 = pts[max(i - 1, 0)], pts[i]
            p2, p3 = pts[i + 1], pts[min(i + 2, N - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed:
        out.append(pts[-1])
    return np.array(out, np.float32)


class Layer:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3), np.float32)
        self.a = np.zeros((h, w), np.float32)

    # ---------- masks ----------
    def _blank(self):
        return np.zeros((self.h, self.w), np.uint8)

    @staticmethod
    def _fin(m, blur):
        m = m.astype(np.float32) / 255.0
        if blur:
            m = cv2.GaussianBlur(m, (0, 0), blur)
        return m

    def mpoly(self, pts, blur=0, smooth=True, off=(0, 0)):
        m = self._blank()
        P = np.asarray(pts, np.float32) + np.asarray(off, np.float32)
        if smooth:
            P = spline(P)
        cv2.fillPoly(m, [np.round(P * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
        return self._fin(m, blur)

    def mell(self, c, ax, ang=0, blur=0):
        m = self._blank()
        cv2.ellipse(m, (int(round(c[0])), int(round(c[1]))), (max(1, int(ax[0])), max(1, int(ax[1]))),
                    ang, 0, 360, 255, -1, cv2.LINE_AA)
        return self._fin(m, blur)

    def mline(self, pts, th0, th1=None, blur=0, smooth=True):
        """Tapered stroke mask along a curve."""
        m = self._blank()
        P = spline(pts, n=10, closed=False) if smooth and len(pts) > 2 else np.asarray(pts, np.float32)
        th1 = th0 if th1 is None else th1
        n = len(P)
        for i in range(n - 1):
            t = i / max(1, n - 2)
            th = max(1, int(round(th0 + (th1 - th0) * t)))
            cv2.line(m, (int(P[i][0] * 16), int(P[i][1] * 16)), (int(P[i + 1][0] * 16), int(P[i + 1][1] * 16)),
                     255, th, cv2.LINE_AA, shift=4)
        return self._fin(m, blur)

    # ---------- painting ----------
    def paint(self, m, col, op=1.0):
        m = (m * op)[..., None]
        self.rgb = self.rgb * (1 - m) + np.asarray(col, np.float32) * m
        self.a = self.a * (1 - m[..., 0]) + m[..., 0]

    def shade(self, m, col, op=1.0):
        """Recolour inside existing paint without changing coverage."""
        m = (m * op)
        m3 = m[..., None]
        self.rgb = self.rgb * (1 - m3) + np.asarray(col, np.float32) * (m * self.a)[..., None]

    def erase(self, m):
        k = (1 - m)
        self.rgb *= k[..., None]
        self.a *= k

    def over(self, other, M=None):
        """Composite other layer on top (optionally through a 2x3 affine)."""
        if M is not None:
            rgb = cv2.warpAffine(other.rgb, M, (self.w, self.h), flags=cv2.INTER_LINEAR)
            a = cv2.warpAffine(other.a, M, (self.w, self.h), flags=cv2.INTER_LINEAR)
        else:
            rgb, a = other.rgb, other.a
        self.rgb = rgb + self.rgb * (1 - a[..., None])
        self.a = a + self.a * (1 - a)

    def rgba(self):
        return np.dstack([self.rgb, self.a]).astype(np.float32)


def angle_radial(w, h, cx, cy):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return np.arctan2(yy - cy, xx - cx)


def painterize(L, seed, passes=((6000, 26, 8, 16), (9000, 14, 4, 9)), jitter=0.035,
               angle=None, angle_noise=0.3, edge_fuzz=True, sample_thresh=0.4, hue=0.008,
               highlight=0.0, hl_col=None, soft=0.0):
    """Repaint a layer with oriented brush strokes sampled from its own colours."""
    rng = np.random.default_rng(seed)
    h, w = L.a.shape
    a = np.clip(L.a, 0, 1)
    straight = L.rgb / np.maximum(a, 1e-4)[..., None]
    wsum = cv2.GaussianBlur(a, (0, 0), 8) + 1e-4
    bleed = cv2.GaussianBlur(L.rgb, (0, 0), 8) / wsum[..., None]
    base = np.clip(straight * a[..., None] + bleed * (1 - a[..., None]), 0, 1)

    if angle is None:
        lum = cv2.GaussianBlur(base.mean(2), (0, 0), 5)
        gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=5)
        gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=5)
        ang = np.arctan2(gy, gx) + np.pi / 2
        mag = np.hypot(gx, gy)
        nz = cv2.resize(rng.random((h // 90 + 3, w // 90 + 3)).astype(np.float32), (w, h),
                        interpolation=cv2.INTER_CUBIC) * np.pi * 2
        thr = np.percentile(mag[a > 0.5], 60) if (a > 0.5).any() else 1
        ang = np.where(mag > thr, ang, nz)
    else:
        ang = angle

    canvas = np.ascontiguousarray((base * 255).astype(np.uint8))
    sa = np.zeros((h, w), np.uint8)
    ys, xs = np.nonzero(a > sample_thresh)
    if len(xs) == 0:
        return L
    for (n, Ln, w0, w1) in passes:
        n = int(n * min(1.0, len(xs) / (w * h * 0.35)) + 200)
        idx = rng.integers(0, len(xs), n)
        jit = rng.normal(0, jitter, n)
        hj = rng.normal(0, hue, (n, 3))
        an = rng.normal(0, angle_noise, n)
        ln = rng.uniform(0.45, 1.15, n) * Ln
        th = rng.integers(w0, w1 + 1, n)
        hl = rng.random(n) < highlight
        for k in range(n):
            y, x = ys[idx[k]], xs[idx[k]]
            c = base[y, x] * (1 + jit[k]) + hj[k]
            if hl[k]:
                c = c * 1.18 + 0.04 if hl_col is None else c * 0.5 + 0.5 * np.asarray(hl_col)
            c = np.clip(c, 0, 1) * 255
            t = ang[y, x] + an[k]
            dx, dy = math.cos(t) * ln[k] / 2, math.sin(t) * ln[k] / 2
            p1 = (int((x - dx) * 4), int((y - dy) * 4))
            p2 = (int((x + dx) * 4), int((y + dy) * 4))
            col = (int(c[0]), int(c[1]), int(c[2]))
            cv2.line(canvas, p1, p2, col, int(th[k]), cv2.LINE_AA, shift=2)
            cv2.line(sa, p1, p2, 255, int(th[k]), cv2.LINE_AA, shift=2)
    out = canvas.astype(np.float32) / 255.0
    if soft:
        out = out * (1 - soft) + cv2.GaussianBlur(out, (0, 0), 3) * soft
    if edge_fuzz:
        near = cv2.GaussianBlur((a > 0.05).astype(np.float32), (0, 0), 6) > 0.02
        na = np.maximum(a, sa.astype(np.float32) / 255.0 * near)
    else:
        na = a
    L.rgb = out * na[..., None]
    L.a = na
    return L


def canvas_texture(w, h, seed=3):
    """Linen-like weave + low-frequency mottling, centred around 1.0."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    weave = 0.5 * np.sin(xx * 1.9) * np.sin(yy * 1.9 + np.sin(xx * 0.05))
    fine = rng.normal(0, 1, (h, w)).astype(np.float32)
    fine = cv2.GaussianBlur(fine, (0, 0), 0.8)
    mott = cv2.resize(rng.random((h // 120 + 2, w // 120 + 2)).astype(np.float32), (w, h),
                      interpolation=cv2.INTER_CUBIC)
    t = 1.0 + 0.035 * weave + 0.03 * fine + 0.05 * (mott - 0.5)
    return t.astype(np.float32)


def flow_field(w, h, seed, base=1.25, amp=0.7, cell=160):
    """Smooth, low-frequency stroke direction field (for fabric / backgrounds)."""
    rng = np.random.default_rng(seed)
    nz = cv2.resize(rng.random((h // cell + 3, w // cell + 3)).astype(np.float32), (w, h),
                    interpolation=cv2.INTER_CUBIC)
    return (base + amp * (nz - 0.5) * 2).astype(np.float32)
