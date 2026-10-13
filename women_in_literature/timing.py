"""Shared timeline (seconds). Everything is locked to the music grid."""
W, H, FPS = 1080, 1920, 30
BPM = 105
BEAT = 60.0 / BPM
BAR = 4 * BEAT                   # 2.2857 s
INTRO = 2 * BAR                  # title
DEC = 2 * BAR                    # one decade
OUTRO = 3 * BAR                  # collage + closing line
TAIL = 0.7                       # hold / fade
N_DEC = 10
T_OUT = INTRO + N_DEC * DEC
TOTAL = T_OUT + OUTRO + TAIL     # ~57.8 s
TR = 0.5                         # paint-wipe transition length

# per-decade beats (local time) used by both picture and sound
CARD_IN = 0.45
NAME_IN = 0.68
WHO_IN = 1.05
TYPE_IN = 1.30
TYPE_DUR = 0.65
LINE_IN = 2.05
LINE_DUR = 0.75


def boundaries():
    """Start time of every scene: intro, 10 decades, outro."""
    return [0.0] + [INTRO + i * DEC for i in range(N_DEC)] + [T_OUT]
