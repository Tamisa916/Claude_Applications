"""Timeline (seconds)."""
W, H, FPS = 1080, 1920, 30
BPM = 96
BEAT = 60.0 / BPM
# intro, then seven scenes (1975, 1985, 2000s, world, 2020, 2021, today/Bijoya)
LENGTHS = [3.0] * 8   # every scene 3 s -> 24 s total
TR = 0.45         # alpana transition length
TOTAL = sum(LENGTHS)


def boundaries():
    out, t = [], 0.0
    for d in LENGTHS:
        out.append(t)
        t += d
    return out
