"""Shared timeline (seconds). Everything is locked to the music grid."""
W, H, FPS = 1080, 1920, 30
BPM = 84
BEAT = 60.0 / BPM
BAR = 4 * BEAT                   # 2.2857 s
INTRO = 8 * BEAT                 # title
DEC = 10 * BEAT                   # one decade
OUTRO = 12 * BEAT                 # collage + closing line
TAIL = 1.0                       # hold / fade
N_DEC = 10
T_OUT = INTRO + N_DEC * DEC
TOTAL = T_OUT + OUTRO + TAIL     # ~87 s
TR = 0.8                         # paint-wipe transition length

# per-decade beats (local time) used by both picture and sound
CARD_IN = 0.60
NAME_IN = 0.95
WHO_IN = 1.50
TYPE_IN = 1.90
TYPE_DUR = 1.00
LINE_IN = 3.00
LINE_DUR = 0.90


def boundaries():
    """Start time of every scene: intro, 10 decades, outro."""
    return [0.0] + [INTRO + i * DEC for i in range(N_DEC)] + [T_OUT]
