"""Timeline (seconds)."""
W, H, FPS = 1080, 1920, 30
BPM = 96
BEAT = 60.0 / BPM
# intro, then seven scenes (1975, 1985, 2000s, world, 2020, 2021, today/Bijoya)
LENGTHS = [5.0, 7.0, 7.0, 7.5, 8.0, 6.5, 7.0, 9.0]   # 57 s total (under 60)
TR = 0.8          # alpana transition length
TOTAL = sum(LENGTHS)


def boundaries():
    out, t = [], 0.0
    for d in LENGTHS:
        out.append(t)
        t += d
    return out
