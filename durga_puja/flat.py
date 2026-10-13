"""Flat illustration engine: filled shapes with bold dark outlines and textile pattern fills.

Layers hold premultiplied RGB + alpha (float32), like the painterly project, but everything here is
drawn as clean vector-ish shapes in the manner of contemporary Bengali poster illustration.
"""
import math
import numpy as np
import cv2

INK = None  # set below


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


INK = hexc("#2a1a14")


def mix(a, b, t):
    return a * (1 - t) + b * t


def spline(pts, n=12, closed=True):
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


def _ip(P):
    return np.round(np.asarray(P, np.float32) * 16).astype(np.int32)


class Layer:
    def __init__(self, w, h):
        self.w, self.h = int(w), int(h)
        self.rgb = np.zeros((self.h, self.w, 3), np.float32)
        self.a = np.zeros((self.h, self.w), np.float32)

    # ------------------------------------------------------------------ masks
    def _blank(self):
        return np.zeros((self.h, self.w), np.uint8)

    def mpoly(self, pts, smooth=False):
        m = self._blank()
        P = spline(pts) if smooth else np.asarray(pts, np.float32)
        cv2.fillPoly(m, [_ip(P)], 255, cv2.LINE_AA, shift=4)
        return m.astype(np.float32) / 255

    def mell(self, c, ax, ang=0, a0=0, a1=360):
        m = self._blank()
        cv2.ellipse(m, (int(c[0] * 16), int(c[1] * 16)), (max(1, int(ax[0] * 16)), max(1, int(ax[1] * 16))),
                    ang, a0, a1, 255, -1, cv2.LINE_AA, shift=4)
        return m.astype(np.float32) / 255

    def mline(self, pts, w, smooth=False, closed=False):
        m = self._blank()
        P = spline(pts, closed=closed) if smooth and len(pts) > 2 else np.asarray(pts, np.float32)
        cv2.polylines(m, [_ip(P)], closed, 255, max(1, int(round(w))), cv2.LINE_AA, shift=4)
        return m.astype(np.float32) / 255

    def outline_of(self, m, w):
        """Outline mask from a fill mask (morphological edge), for complex fills."""
        k = max(1, int(round(w)))
        er = cv2.erode((m > 0.5).astype(np.uint8), np.ones((k, k), np.uint8))
        edge = np.clip(m - er.astype(np.float32), 0, 1)
        return cv2.GaussianBlur(edge, (0, 0), 0.5)

    # ------------------------------------------------------------------ paint
    def paint(self, m, col, op=1.0):
        m = np.clip(m * op, 0, 1)
        self.rgb = self.rgb * (1 - m[..., None]) + np.asarray(col, np.float32) * m[..., None]
        self.a = self.a * (1 - m) + m

    def shape(self, pts, fill, lw=4, smooth=False, pattern=None, ink=INK, closed=True):
        m = self.mpoly(pts, smooth)
        if fill is not None:
            self.paint(m, fill)
        if pattern is not None:
            pattern(self, m)
        if lw:
            P = spline(pts) if smooth else np.asarray(pts, np.float32)
            o = self._blank()
            cv2.polylines(o, [_ip(P)], closed, 255, int(lw), cv2.LINE_AA, shift=4)
            self.paint(o.astype(np.float32) / 255, ink)
        return m

    def ellipse(self, c, ax, fill, lw=4, ang=0, pattern=None, ink=INK):
        m = self.mell(c, ax, ang)
        if fill is not None:
            self.paint(m, fill)
        if pattern is not None:
            pattern(self, m)
        if lw:
            o = self._blank()
            cv2.ellipse(o, (int(c[0] * 16), int(c[1] * 16)), (int(ax[0] * 16), int(ax[1] * 16)), ang, 0, 360, 255,
                        int(lw), cv2.LINE_AA, shift=4)
            self.paint(o.astype(np.float32) / 255, ink)
        return m

    def line(self, pts, w=3, col=None, smooth=False, closed=False):
        self.paint(self.mline(pts, w, smooth, closed), INK if col is None else col)

    def arc(self, c, ax, a0, a1, w=3, col=None, ang=0):
        o = self._blank()
        cv2.ellipse(o, (int(c[0] * 16), int(c[1] * 16)), (int(ax[0] * 16), int(ax[1] * 16)), ang, a0, a1, 255,
                    int(w), cv2.LINE_AA, shift=4)
        self.paint(o.astype(np.float32) / 255, INK if col is None else col)

    def over(self, other, x=0, y=0):
        """Composite another layer (premultiplied) at an integer offset."""
        x, y = int(x), int(y)
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + other.w), min(self.h, y + other.h)
        if x1 <= x0 or y1 <= y0:
            return
        sr = other.rgb[y0 - y:y1 - y, x0 - x:x1 - x]
        sa = other.a[y0 - y:y1 - y, x0 - x:x1 - x]
        self.rgb[y0:y1, x0:x1] = sr + self.rgb[y0:y1, x0:x1] * (1 - sa[..., None])
        self.a[y0:y1, x0:x1] = sa + self.a[y0:y1, x0:x1] * (1 - sa)

    def rgba(self):
        """Premultiplied RGBA sprite."""
        return np.dstack([self.rgb, self.a]).astype(np.float32)


# ---------------------------------------------------------------------- textile patterns
def pat_dots(col, step=14, r=2.6, offset=True):
    def f(L, m):
        o = L._blank()
        ys, xs = np.nonzero(m > 0.5)
        if not len(xs):
            return
        for y in range(ys.min() - step, ys.max() + step, step):
            sh = (step // 2) if offset and (y // step) % 2 else 0
            for x in range(xs.min() - step + sh, xs.max() + step, step):
                cv2.circle(o, (int(x * 16), int(y * 16)), int(r * 16), 255, -1, cv2.LINE_AA, shift=4)
        L.paint(o.astype(np.float32) / 255 * m, col)
    return f


def pat_stripes(col, step=16, w=5, ang=0.0):
    def f(L, m):
        yy, xx = np.mgrid[0:L.h, 0:L.w].astype(np.float32)
        u = xx * math.cos(ang) + yy * math.sin(ang)
        s = (np.mod(u, step) < w).astype(np.float32)
        L.paint(cv2.GaussianBlur(s, (0, 0), 0.6) * m, col)
    return f


def pat_checks(c1, c2, step=40):
    def f(L, m):
        yy, xx = np.mgrid[0:L.h, 0:L.w]
        s = (((xx // step) + (yy // step)) % 2).astype(np.float32)
        L.paint(m * s, c1)
        L.paint(m * (1 - s), c2)
    return f


def pat_buti(col, col2=None, step=26, r=5):
    """Small four-petal flower stamps, like printed saree motifs."""
    def f(L, m):
        o = L._blank()
        o2 = L._blank()
        ys, xs = np.nonzero(m > 0.5)
        if not len(xs):
            return
        for j, y in enumerate(range(ys.min() - step, ys.max() + step, step)):
            for x in range(xs.min() - step + (step // 2) * (j % 2), xs.max() + step, step):
                for k in range(4):
                    a = k * math.pi / 2 + 0.6
                    cv2.circle(o, (int((x + r * math.cos(a)) * 16), int((y + r * math.sin(a)) * 16)),
                               int(r * 0.75 * 16), 255, -1, cv2.LINE_AA, shift=4)
                cv2.circle(o2, (int(x * 16), int(y * 16)), int(r * 0.45 * 16), 255, -1, cv2.LINE_AA, shift=4)
        L.paint(o.astype(np.float32) / 255 * m, col)
        if col2 is not None:
            L.paint(o2.astype(np.float32) / 255 * m, col2)
    return f


def pat_combo(*fs):
    def f(L, m):
        for g in fs:
            g(L, m)
    return f


def paper_texture(w, h, seed=2):
    """Offset-print paper: fine grain + faint fibres, centred around 1.0."""
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 1, (h, w)).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 0.7) * 0.025
    fib = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 6) * 0.03
    return (1.0 + g + fib).astype(np.float32)
