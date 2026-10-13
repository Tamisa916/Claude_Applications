# 100 Years of Women in Western Fiction

An 87-second, 9:16 Vox-style explainer: one archetype per decade, 1900–1999. Every frame is drawn in code in a soft gouache style, over a gentle synthesized piano score.

**To change the text, people, colours or pace, see [TEMPLATE.md](TEMPLATE.md).**

| Decade | Archetype | Character · Book |
|---|---|---|
| 1900s | The Ornament | Lily Bart · *The House of Mirth* (1905) |
| 1910s | The Pioneer | Ántonia Shimerda · *My Ántonia* (1918) |
| 1920s | The Flapper | Daisy Buchanan · *The Great Gatsby* (1925) |
| 1930s | The Seeker | Janie Crawford · *Their Eyes Were Watching God* (1937) |
| 1940s | The Femme Fatale | Phyllis Nirdlinger · *Double Indemnity* (1943) |
| 1950s | The Housewife | Marjorie Morgenstern · *Marjorie Morningstar* (1955) |
| 1960s | The Madwoman | Antoinette Cosway · *Wide Sargasso Sea* (1966) |
| 1970s | The Liberated | Isadora Wing · *Fear of Flying* (1973) |
| 1980s | The Witness | Offred · *The Handmaid's Tale* (1985) |
| 1990s | The Narrator | Bridget Jones · *Bridget Jones's Diary* (1996) |

## Rebuild
```
pip install numpy opencv-python-headless scipy pillow   # plus ffmpeg on PATH
python audio.py build/score.wav
python render.py                 # -> women_in_western_literature.mp4
python render.py --preview 8,20  # stills only
```
Files: `paint.py` is the brushstroke engine, `portraits.py` the parametric portraits, `assets.py` the backgrounds, flowers and props, `render.py` the scenes, type and transitions, `audio.py` the score and sound effects, and `content.py` the script. Fonts are under the SIL OFL.
