"""Timeline (seconds)."""
W, H, FPS = 1080, 1920, 30
BPM = 96
BEAT = 60.0 / BPM
# intro, then seven scenes (1975, 1985, 2000s, world, 2020, 2021, today/Bijoya)
LENGTHS = [8.0, 11.0, 11.0, 12.0, 13.0, 11.0, 11.0, 13.0]
TR = 1.0          # alpana transition length
TOTAL = sum(LENGTHS)


def boundaries():
    out, t = [], 0.0
    for d in LENGTHS:
        out.append(t)
        t += d
    return out
