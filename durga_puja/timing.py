"""Timeline (seconds)."""
W, H, FPS = 1080, 1920, 30
BPM = 96
BEAT = 60.0 / BPM
# intro, then seven scenes (1975, 1985, 2000s, world, 2020, 2021, today/Bijoya)
LENGTHS = [3.0] * 7 + [4.0]   # 3 s per scene, Bijoya card holds 1 s longer -> 25 s
TR = 1.0          # transition length, centred on each cut (0.5 s either side)
TOTAL = sum(LENGTHS)


def boundaries():
    out, t = [], 0.0
    for d in LENGTHS:
        out.append(t)
        t += d
    return out
