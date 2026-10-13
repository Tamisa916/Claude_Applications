# Editing template

Everything you can see or read in the video lives in **`content.py`**. Change the values there, then re-render. You don't need to touch the drawing code.

## 1. Re-render

```bash
cd women_in_literature
pip install numpy opencv-python-headless scipy pillow    # once (also needs ffmpeg)

python audio.py build/score.wav            # music (only needed if timing.py changed)
python render.py --preview 9,33,80         # quick stills (seconds) -> build/preview/
python render.py                           # full video -> women_in_western_literature.mp4
```

Use **`--fresh`** whenever you change how a portrait or background looks: colours, hair, clothes, `bg`, and so on. Those are cached, and without `--fresh` the old ones are reused. Text-only edits don't need it.

| You changed | Command |
|---|---|
| Any text (names, books, lines, title, outro) | `python render.py` |
| Portrait look, `bg`, `INTRO_BG`/`OUTRO_BG`, highlight colours | `python render.py --fresh` |
| `timing.py` (pace) | `python audio.py build/score.wav`, then `python render.py` |

A full render takes about 10 minutes. Building fresh assets adds about 3 minutes.

## 2. The decade card: one `dict(...)` per scene in `DECADES`

```python
dict(year="1930s",                      # big heading; keep the "19x0s" shape
     arche="THE SEEKER",                # archetype name, auto-shrinks to fit
     who="Janie Crawford",              # character
     book="Their Eyes Were Watching God",
     author="Zora Neale Hurston", pub="1937",
     line="Under a pear tree, she dreams of a life of her own.",   # handwritten line, wraps to 2 lines max
     bg="#c8613a",                      # background colour (muted automatically)
     ink="light",                       # "light" = cream heading/timeline (dark bg), "dark" = brown (light bg)
     props="blossom",                   # scene decoration, see list below
     portrait=dict(...)),               # the woman, see section 3
```

**Keep exactly 10 entries.** The timeline ticks, the "04 / 10" counters, the outro collage and `HIGHLIGHTS` all assume ten. You can swap any entry for another book or character, though.

Keep `line` under about 55 characters so it stays within two lines.

### `props`: scene decoration

| Value | What appears |
|---|---|
| `frame` | gilded oval cameo frame and peonies |
| `wheat` | rising sun, field, swaying wheat |
| `deco` | rotating art-deco sunburst, champagne bubbles, small green light |
| `blossom` | pear-blossom branches and falling petals |
| `noir` | spotlight and venetian-blind shadows |
| `wallpaper` | patterned wallpaper, house picture, spinning clock |
| `fire` | flames, embers, red hibiscus |
| `sunset` | 70s rainbow arcs and a paper plane |
| `handmaids` | rows of red-cloaked figures walking |
| `diary` | lined paper and handwritten doodles (`DOODLES`) |

You can reuse a value in more than one decade.

## 3. The portrait: `portrait=dict(...)`

```python
portrait=dict(
    hair_style="long",            # see list
    hair="#1c1210", hair_hi="#5a4038",   # hair colour + its highlight
    skin="#8a5638", shadow="#5e3622", blush="#a5503a", lips="#8e3a2e",
    eyes="open",                  # "open" | "down" (half-lidded) | "closed"
    iris="#3a2418",
    neckline="round",             # "v" | "round" | "boat" | "high" | "strapless"
    cloth="#e9b949", cloth_hi="#c9902a",  # garment colour + fold/pattern colour
    cloth_pattern=None,           # None | "flowers" | "dots" | "stripes"
    acc=("pearls", "earrings"),   # accessories, any mix (see list)
    tilt=-9,                      # head tilt in degrees (- = left)
    turn=0.0,                     # -0.3..0.3: head turned slightly left/right
    seed=51,                      # change for a different brush pattern
)
```

Any key you leave out falls back to the default.

**`hair_style`:** `bob` · `updo` · `scarf` (use with acc `"scarf"`) · `wave` · `long` · `victory` · `set` · `wild` · `curls` · `bonnet` (use with acc `"bonnet"`, `"cloak"`) · `messy`

**`acc`:** `pearls` · `earrings` · `hoops` · `lace` (high lace collar) · `collar` (white Peter-Pan collar) · `headband` (with feather) · `hat` · `scarf` (headscarf with braid) · `bonnet` · `cloak` · `clip` (hair clip)

**Skin presets** (`skin`, `shadow`, `blush`):

| Tone | `skin` | `shadow` | `blush` |
|---|---|---|---|
| Fair | `#e4bfa5` | `#a97c68` | `#d4887a` (the default) |
| Olive | `#e6c2a2` | `#b07e62` | `#d4887a` |
| Deep | `#8a5638` | `#5e3622` | `#a5503a` |

The shoulder width is set by `SHOULDER = 0.72` at the top of `portraits.py`; lower means narrower.

## 4. Intro and outro (top and bottom of `content.py`)

- **`INTRO_TEXT`:** the counter number, the words around it, and the small subtitle.
- **`INTRO_PORTRAIT`:** the woman on the title card, using the same keys as section 3.
- **`INTRO_BG` / `OUTRO_BG`:** background colours for the title and closing screens.
- **`OUTRO_LINES`:** four closing lines. The last one gets the yellow highlighter.
- **`HIGHLIGHTS`:** the highlighter colour behind each archetype name, one per decade.

## 5. Pace and sound (`timing.py`, `audio.py`)

- **`timing.py`:**
  - `BPM`, and the length of each part in beats: `INTRO`, `DEC`, `OUTRO`.
  - The card cues inside a decade, in seconds: `CARD_IN`, `NAME_IN`, `WHO_IN`, `TYPE_IN`, `LINE_IN`.
  - With `DEC = 10 * BEAT` at 84 BPM, each decade lasts about 7.1 s and the whole video about 87 s.
  - For a video under 60 s, use `BPM = 105` and `DEC = 8 * BEAT`.
- **`audio.py`:** the chords are in `chords` and the melody in `melody_notes` (MIDI numbers). The sound effects are listed under `# ---- foley`; change a `place(...)` gain, or delete the line to drop that effect.

## 6. Blank decade to copy

```python
dict(year="19_0s", arche="THE ___", who="Character Name", book="Book Title",
     author="Author Name", pub="19__", line="One short sentence about her.",
     bg="#d9a55b", ink="dark", props="wheat",
     portrait=dict(hair_style="long", hair="#3a2016", hair_hi="#7a4a30", eyes="open", neckline="round",
                   cloth="#9c3a24", cloth_hi="#c0573a", acc=("earrings",), tilt=0, seed=123)),
```
