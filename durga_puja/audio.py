"""Calm, synthesized 'pujar sound' (48 kHz stereo): tanpura drone, harmonium, bansuri, soft dhak + kashor,
temple bell (ghanta) at scene changes and a shankh (conch) swell at the big moments. No samples are used."""
import os
import sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

from timing import TOTAL, BPM, BEAT, LENGTHS, boundaries

SR = 48000
N = int((TOTAL + 2) * SR)
rng = np.random.default_rng(11)
SA = 146.83  # D3


def place(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i < 0:
        return
    x = x[: N - i]
    buf[i:i + len(x), 0] += x * gain * np.sqrt(0.5 * (1 - pan))
    buf[i:i + len(x), 1] += x * gain * np.sqrt(0.5 * (1 + pan))


def bp(x, lo, hi, o=2):
    return signal.sosfilt(signal.butter(o, [lo, hi], btype="band", fs=SR, output="sos"), x)


def lp(x, f, o=2):
    return signal.sosfilt(signal.butter(o, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return signal.sosfilt(signal.butter(o, f, btype="high", fs=SR, output="sos"), x)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


# --------------------------------------------------------------------------- instruments
def tanpura(f, dur=3.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(1, 14):  # bright, buzzing (jawari) string
        x += (1 / k ** 0.9) * np.sin(2 * np.pi * f * k * t * (1 + 0.0007 * k) + rng.uniform(0, 6)) * \
            (1 + 0.3 * np.sin(2 * np.pi * (0.7 + k * 0.13) * t))
    return lp(x * env(n, 0.01, 1.6), 3500) * 0.12


def harmonium(fs, dur):
    n = int((dur + 0.6) * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f in fs:
        for det in (-0.25, 0.25):
            ph = 2 * np.pi * f * (1 + det / 100) * t
            x += np.sign(np.sin(ph)) * 0.3 + np.sin(ph) * 0.5 + 0.2 * np.sin(3 * ph)
    e = np.minimum(1, t / 0.4) * np.where(t > dur, np.exp(-(t - dur) / 0.3), 1.0)
    return lp(x * e, 1800) / (len(fs) * 6)


def bansuri(f, dur):
    n = int((dur + 0.4) * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.6)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    x = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
    breath = bp(rng.normal(0, 1, n), f * 1.5, min(f * 6, 9000)) * 0.12
    e = np.minimum(1, t / 0.12) * np.where(t > dur, np.exp(-(t - dur) / 0.15), 1.0)
    return (x + breath) * e * 0.16


def dhak(kind="D", vel=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    if kind == "D":  # low head: deep thump with pitch drop
        f = 68 + 60 * np.exp(-t / 0.03)
        out += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22) * 0.9
    m = int(0.08 * SR)  # stick on the high head: woody slap + short ring
    slap = bp(rng.normal(0, 1, m), 1500, 5000) * env(m, 0.0005, 0.012) * 0.8
    out[:m] += slap
    out += np.sin(2 * np.pi * 390 * t) * np.exp(-t / 0.05) * 0.3
    return lp(out, 6000) * vel


def kashor(vel=1.0):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t / d) for a, f, d in
            ((1, 820, 0.25), (0.7, 1433, 0.18), (0.5, 2210, 0.12), (0.35, 3170, 0.09), (0.2, 4410, 0.06)))
    x += hp(rng.normal(0, 1, n), 4000) * np.exp(-t / 0.02) * 0.3
    return x * 0.2 * vel


def ghanta(f=880, vel=1.0):
    n = int(4.0 * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) * (1 + 0.15 * np.sin(2 * np.pi * 3.5 * t)) for a, r, d in
            ((1, 1.0, 2.2), (0.6, 2.0, 1.4), (0.45, 2.76, 0.9), (0.3, 4.1, 0.5), (0.2, 5.4, 0.3)))
    x[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return x * 0.18 * vel


def shankh(dur=3.0, f=311.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sw = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    vib = 1 + 0.01 * np.sin(2 * np.pi * 4.6 * t) + 0.02 * (t / dur)     # slight upward bend
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    x = sum((1 / k ** 1.1) * np.sin(k * ph) for k in range(1, 12))
    x = np.tanh(x * 1.6)                                                   # brassy buzz
    breath = bp(rng.normal(0, 1, n), 600, 4000) * 0.25
    return lp((x + breath) * sw, 3200) * 0.22


def reverb(x, secs=3.0, wet=0.3):
    n = int(secs * SR)
    ir = rng.normal(0, 1, (n, 2)) * np.exp(-np.arange(n) / (0.6 * SR))[:, None]
    for c in range(2):
        ir[:, c] = lp(ir[:, c], 5000)
    ir /= np.sqrt((ir ** 2).sum(0))
    y = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + y * wet * 2.0


# --------------------------------------------------------------------------- score
def build():
    out = np.zeros((N, 2))
    B = boundaries()
    end = TOTAL
    # tanpura cycle: Pa  Sa' Sa' Sa
    t = 0.0
    k = 0
    while t < end:
        f = [SA * 1.5 / 2, SA, SA, SA / 2][k % 4]
        place(out, tanpura(f), t, 0.9, pan=[-0.4, -0.1, 0.1, 0.4][k % 4])
        t += BEAT * 1.25
        k += 1
    # harmonium chords: D - G - A - D over two bars each
    chords = [(SA, SA * 1.25, SA * 1.5), (SA * 4 / 3, SA * 5 / 3, SA * 2), (SA * 1.5, SA * 15 / 8, SA * 9 / 4),
              (SA, SA * 1.5, SA * 2)]
    bar = 4 * BEAT
    t, k = 0.0, 0
    while t < end:
        quiet = B[5] <= t < B[6]
        place(out, harmonium(chords[k % 4], bar * 2), t, 0.6 if quiet else 1.0)
        t += bar * 2
        k += 1
    # bansuri phrases (D major pentatonic), resting in the 2020 scene
    phrase = [(SA * 4, 2), (SA * 4.5, 1), (SA * 5, 1), (SA * 6, 2), (SA * 5, 1), (SA * 4.5, 1), (SA * 4, 4),
              (SA * 3, 2), (SA * 4, 2), (SA * 4.5, 3), (SA * 4, 1), (SA * 3.375, 4)]
    t, j = B[1] + 0.3, 0
    while t < end - 3:
        f, beats = phrase[j % len(phrase)]
        if not (B[5] <= t < B[6]):
            place(out, bansuri(f, beats * BEAT * 0.95), t, 1.0, pan=0.2)
        t += beats * BEAT
        j += 1
        if j % len(phrase) == 0:
            t += 2 * bar
    # dhak + kashor (soft) in the celebration scenes
    pattern = "D.tt.tD.D.t.Dtt."   # 16 sixteenths: a relaxed baul-like dhak groove
    vel = {1: 0.5, 2: 0.55, 3: 0.55, 4: 0.25, 5: 0.0, 6: 0.6, 7: 0.6}
    for s in range(1, 8):
        v = vel[s]
        if v <= 0:
            continue
        t0, t1 = B[s] + 0.1, (B[s + 1] if s + 1 < len(B) else end - 1.0)
        t = t0
        while t < t1:
            for i, ch in enumerate(pattern):
                tt = t + i * BEAT / 4
                if tt >= t1:
                    break
                if ch == "D":
                    place(out, dhak("D", v), tt, 1.0, pan=-0.25)
                elif ch == "t":
                    place(out, dhak("t", v * 0.6), tt, 1.0, pan=0.25)
            for b in (1, 3):
                place(out, kashor(v * 0.8), t + b * BEAT, 1.0, pan=0.45)
            t += 4 * BEAT
    # temple bell at every scene change, conch at intro / UNESCO / finale
    for k, b in enumerate(B[1:], 1):
        place(out, ghanta(880 if k % 2 else 990, 0.8), b - 0.05, 1.0, pan=0.3 if k % 2 else -0.3)
    for k in range(3):
        place(out, ghanta([1320, 1480, 1760][k], 0.35), B[5] + 0.4 + k * 0.8, 1.0, pan=[-0.6, 0.6, 0][k])
    place(out, shankh(2.6), 0.1, 1.0)
    place(out, shankh(2.2, 330), B[6] + 0.7, 0.9)
    place(out, shankh(2.8), end - 3.0, 0.9)
    out = reverb(out, 3.0, 0.3)
    out = np.stack([lp(out[:, c], 7000) for c in range(2)], 1)
    t = np.arange(N) / SR
    out *= (np.clip(t / 0.8, 0, 1) * np.clip((end - t) / 1.0, 0, 1))[:, None]
    out = out[: int(end * SR)]
    return out / np.abs(out).max() * 0.44  # ~ -20 LUFS: calm, not intense


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "build", "score.wav")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    x = build()
    wavfile.write(path, SR, (x * 32767).astype(np.int16))
    print("wrote", path, f"{len(x) / SR:.1f}s")
