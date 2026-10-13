"""Synthesise the score + sound design (48 kHz stereo WAV), locked to timing.py.

Warm felt-piano arpeggios, a soft pad and upright-ish bass at 105 BPM, a light
brushed groove under the decades, and Vox-style UI foley: paint-swipe whooshes,
paper slides, typewriter ticks and pen scribbles that land on the animation cues.
"""
import os
import sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

from timing import (BEAT, BAR, INTRO, DEC, OUTRO, TOTAL, T_OUT, TR, N_DEC, CARD_IN, NAME_IN, TYPE_IN, TYPE_DUR,
                    LINE_IN, LINE_DUR, boundaries)
from content import DECADES

SR = 48000
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(7)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    x = x[: N - i]
    l = gain * np.sqrt(0.5 * (1 - pan))
    r = gain * np.sqrt(0.5 * (1 + pan))
    buf[i:i + len(x), 0] += x * l
    buf[i:i + len(x), 1] += x * r


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


# --------------------------------------------------------------------------- instruments
def piano(m, dur, vel=0.6):
    f = mtof(m)
    n = int((dur + 1.6) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    tau = 1.8 * (220 / f) ** 0.45
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)
        if fk > 12000:
            break
        amp = (1 / k ** 1.4) * (0.6 + 0.4 * vel)
        out += amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t / (tau / (1 + 0.35 * k)))
    att = np.minimum(1, t / 0.004)
    rel = np.where(t > dur, np.exp(-(t - dur) / 0.25), 1.0)
    out *= att * rel
    ham = lp(rng.normal(0, 1, int(0.02 * SR)), 2500) * env_exp(int(0.02 * SR), 0.004) * 0.15
    out[: len(ham)] += ham
    return lp(out, 5200) * vel


def pad(ms, dur):
    n = int((dur + 1.0) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in ms:
        f = mtof(m)
        for det in (-0.12, 0.0, 0.11):
            ph = 2 * np.pi * f * (1 + det / 100) * t
            out += 0.5 * np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
    envl = np.minimum(1, t / 0.6) * np.where(t > dur, np.exp(-(t - dur) / 0.5), 1.0)
    return lp(out * envl, 1800) / (len(ms) * 3)


def bass(m, dur):
    f = mtof(m)
    n = int((dur + 0.5) * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    e = np.minimum(1, t / 0.008) * np.exp(-t / 0.9) * np.where(t > dur, np.exp(-(t - dur) / 0.08), 1.0)
    return lp(x * e, 900)


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 80 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.12) * 0.9


def shaker(v=1.0):
    n = int(0.09 * SR)
    x = hp(rng.normal(0, 1, n), 6000) * np.minimum(1, np.arange(n) / (0.01 * SR)) * env_exp(n, 0.025)
    return x * 0.25 * v


def snap():
    n = int(0.25 * SR)
    x = bp(rng.normal(0, 1, n), 1200, 5000) * env_exp(n, 0.05) * 0.5
    t = np.arange(n) / SR
    x += np.sin(2 * np.pi * 190 * t) * env_exp(n, 0.04) * 0.35
    return x


# --------------------------------------------------------------------------- foley
def whoosh(dur=0.7, lo=300, hi=3500):
    n = int(dur * SR)
    noise = rng.normal(0, 1, n)
    out = np.zeros(n)
    seg = 512
    for i in range(0, n, seg):
        p = i / n
        fc = lo * (hi / lo) ** (np.sin(np.pi * p) ** 1.2)
        chunk = noise[max(0, i - 2048):i + seg]
        y = bp(chunk, fc * 0.7, min(fc * 1.4, SR / 2 - 100))
        out[i:i + seg] = y[-len(noise[i:i + seg]):]
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.6
    return out * e * 0.9


def paper_slide():
    n = int(0.32 * SR)
    x = bp(rng.normal(0, 1, n), 900, 7000) * (np.linspace(0, 1, n) ** 0.3) * env_exp(n, 0.09)
    return x * 0.55


def pop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 520 + 600 * (1 - np.exp(-t / 0.02))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.035)
    return x * 0.5


def type_click():
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    x = hp(rng.normal(0, 1, n), 2500) * env_exp(n, 0.0035)
    x += np.sin(2 * np.pi * rng.uniform(1600, 2400) * t) * env_exp(n, 0.006) * 0.3
    return x * 0.6


def scribble(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 11 * t + 2 * np.sin(2 * np.pi * 1.7 * t)) ** 2
    x = bp(rng.normal(0, 1, n), 2500, 9000) * am * np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.06)
    return x * 0.22


def chime(m, vel=0.4):
    f = mtof(m)
    n = int(2.5 * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) for a, r, d in
            ((1, 1, 1.2), (0.4, 2.76, 0.5), (0.25, 5.4, 0.25)))
    return x * vel * np.minimum(1, t / 0.002)


def tick():
    n = int(0.04 * SR)
    return bp(rng.normal(0, 1, n), 3000, 9000) * env_exp(n, 0.004) * 0.6


def reverb(x, secs=2.4, wet=0.24):
    n = int(secs * SR)
    ir = rng.normal(0, 1, (n, 2)) * np.exp(-np.arange(n) / (0.45 * SR))[:, None]
    ir[:, 0] = lp(ir[:, 0], 6000)
    ir[:, 1] = lp(ir[:, 1], 6000)
    ir /= np.sqrt((ir ** 2).sum(0))
    y = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + y * wet * 2.2


# --------------------------------------------------------------------------- score
def build():
    music = np.zeros((N, 2))
    fx = np.zeros((N, 2))
    # F major colours: Fmaj9 | Dm9 | Bbmaj9 | C6/9 ; 2 chords per 2-bar phrase pair
    chords = [
        (53, [65, 69, 72, 76, 79]),   # Fmaj9
        (50, [62, 65, 69, 72, 76]),   # Dm9
        (46, [62, 65, 69, 70, 74]),   # Bbmaj9
        (48, [64, 67, 69, 72, 74]),   # C6/9
    ]
    n_bars = int(round((TOTAL - 0.7) / BAR))
    melody_notes = [81, 79, 77, 76, 77, 79, 84, 81, 79, 76, 74, 76, 77, 76, 72, 74]
    for b in range(n_bars):
        t0 = b * BAR
        root, tones = chords[b % 4]
        in_outro = t0 >= T_OUT
        drums = (INTRO - 0.01) <= t0 < T_OUT
        last = b == n_bars - 1
        place(music, pad([root + 12] + tones[:3], BAR * (2 if last else 1)), t0, 0.5)
        place(music, bass(root - 12 if root > 47 else root, BEAT * 1.6), t0, 0.55)
        if not last:
            place(music, bass(root - 12 if root > 47 else root, BEAT * 0.8), t0 + BEAT * 2.5, 0.35)
        # arpeggio in 8ths (up-down), sparse in intro & outro
        pattern = [0, 2, 1, 3, 2, 4, 3, 1]
        for k in range(8):
            if last and k > 0:
                break
            if (b < 1 or in_outro) and k % 2:
                continue
            m = tones[pattern[k]] + (12 if k in (5,) else 0)
            vel = 0.42 if k % 2 == 0 else 0.3
            place(music, piano(m, BEAT * 0.9, vel), t0 + k * BEAT / 2 + rng.normal(0, 0.004), 0.55,
                  pan=-0.25 + 0.5 * (k / 7))
        # melody: one note per half bar over the decades
        if drums or in_outro:
            for h in range(2):
                m = melody_notes[(b * 2 + h) % len(melody_notes)]
                place(music, piano(m, BEAT * 1.8, 0.55), t0 + h * 2 * BEAT + 0.01, 0.42, pan=0.1)
        if drums:
            for k in range(4):
                if k in (0, 2):
                    place(music, kick(), t0 + k * BEAT, 0.55)
                if k in (1, 3):
                    place(music, snap(), t0 + k * BEAT, 0.16, pan=0.1)
            for k in range(8):
                place(music, shaker(1.0 if k % 2 else 0.55), t0 + k * BEAT / 2, 0.5, pan=0.35)
        if last:
            place(music, piano(root - 12, 3.0, 0.6), t0, 0.5)
            for m in tones:
                place(music, piano(m, 3.0, 0.45), t0 + 0.02, 0.4)

    # ---- foley
    B = boundaries()
    for k, b in enumerate(B[1:], 1):
        place(fx, whoosh(0.75), b - 0.2, 0.55, pan=-0.3 + 0.6 * (k % 2))
    # intro
    for d in (0.25, 0.35, 0.45, 0.55, 0.6, 0.7):
        place(fx, pop(), d + 0.25, 0.25, pan=rng.uniform(-0.6, 0.6))
    for j in range(16):
        place(fx, tick(), 0.25 + 1.1 * (j / 16) ** 0.8, 0.5)
    place(fx, kick(), 0.92, 0.5)
    place(fx, paper_slide(), 1.25, 0.35)
    place(fx, scribble(0.45), 1.7, 0.6)
    for j in range(22):
        place(fx, type_click(), 2.2 + j * 0.036, 0.35, pan=0.2)
    # decades
    for i in range(N_DEC):
        b = B[i + 1]
        place(fx, tick(), b + 0.15, 0.4)
        place(fx, tick(), b + 0.55, 0.3)
        place(fx, paper_slide(), b + CARD_IN, 0.6, pan=-0.1)
        place(fx, pop(), b + NAME_IN + 0.05, 0.45)
        d = DECADES[i]
        nchars = len(d["book"]) + len(d["author"]) + 8
        n_clicks = min(26, nchars)
        for j in range(n_clicks):
            place(fx, type_click(), b + TYPE_IN + TYPE_DUR * 0.95 * j / n_clicks + rng.normal(0, 0.004), 0.3,
                  pan=rng.uniform(-0.2, 0.3))
        n_lines = 1 if len(d["line"]) < 34 else 2
        for k in range(n_lines):
            place(fx, scribble(LINE_DUR * 0.9), b + LINE_IN + k * LINE_DUR * 0.8, 0.7, pan=-0.15)
        if d["props"] == "deco":
            place(fx, chime(96, 0.2), b + 1.2, 0.5, pan=0.5)
        if d["props"] == "wallpaper":
            for j in range(10):
                place(fx, tick(), b + 0.9 + j * BEAT / 2, 0.25, pan=-0.6)
        if d["props"] == "fire":
            n = int(DEC * SR)
            crackle = (rng.random(n) < 0.0009) * rng.normal(0, 1, n)
            crackle = bp(crackle, 800, 6000) * 3 + lp(rng.normal(0, 1, n), 400) * 0.05
            place(fx, crackle, b, 0.35)
        if d["props"] == "sunset":
            place(fx, whoosh(1.4, 600, 2500), b + 1.6, 0.25, pan=0.6)
    # outro
    o = T_OUT
    for k in range(10):
        place(fx, paper_slide(), o + 0.1 + k * 0.12, 0.3, pan=-0.6 + 1.2 * (k / 9))
    place(fx, chime(84, 0.35), o + 4.15, 0.6)
    place(fx, chime(91, 0.25), o + 4.25, 0.5)
    place(fx, scribble(0.5), o + 4.15, 0.5)

    vinyl = (rng.random(N) < 0.0004) * rng.normal(0, 1, N)
    vinyl = hp(vinyl, 1500) * 0.4 + lp(rng.normal(0, 1, N), 300) * 0.004
    music[:, 0] += vinyl
    music[:, 1] += np.roll(vinyl, 37)

    music = reverb(music, wet=0.26)
    fx = reverb(fx, secs=1.2, wet=0.12)
    mix = music * 0.85 + fx * 0.9
    t = np.arange(N) / SR
    fade = np.clip((TOTAL - t) / 1.4, 0, 1) ** 1.5
    mix *= fade[:, None] * np.clip(t / 0.05, 0, 1)[:, None]
    mix = mix[: int(TOTAL * SR)]
    mix = np.tanh(mix / np.abs(mix).max() * 1.3) / np.tanh(1.3) * 0.89
    return mix


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "build", "score.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    x = build()
    wavfile.write(out, SR, (x * 32767).astype(np.int16))
    print("wrote", out, f"{len(x) / SR:.2f}s")
