# Durga Puja · দুর্গাপূজা: fifty years of celebration (1975–2025)

A 25-second, 9:16 motion-design film (3 s per scene, soft 1 s transitions). Every frame is drawn in code as flat Bengali poster illustration (bold outlines, flat colour, saree-print textiles, crowded compositions), and it is scored with a calm, synthesized *pujar sound*.

| # | Scene | Caption |
|---|---|---|
| 0 | Title: Durga on the lion against a folk-painting lotus field | Durga Puja · দুর্গাপূজা |
| 1 | 1975 · the family thakur-dalan | ঠাকুরদালানের পুজো |
| 2 | 1985 · street (baroari) pandal, loudspeakers and string lights | বারোয়ারি পুজো |
| 3 | 2000s · night-time theme pandal with an LED gate | থিম পুজো |
| 4 | Kumartuli idols shipped to London, New York, Toronto and Sydney | প্রবাসে পুজো |
| 5 | 2020 · barricades, masks, darshan on a phone | দূর থেকে দর্শন |
| 6 | 2021 · UNESCO Intangible Cultural Heritage | ইউনেস্কো স্বীকৃতি |
| 7 | Today · Bijoya: sindoor khela, dhunuchi, the idol carried to the river | শুভ বিজয়া |

**Durga's iconography.** Her right hands, top to bottom, hold the sword, discus, arrow and lance, with the trishul in the lowest hand driven into Mahishasura. Her left hands, top to bottom, hold the shield, bow, noose and goad, with the snake (naagpash) in the lowest hand. She rides the lion, and Mahishasura is mounted on the buffalo.

**Sound.** Everything is synthesized: a tanpura drone, harmonium, bansuri, soft dhak and kashor, a ghanta bell at each scene change and a shankh at the big moments. It is mixed to about −20 LUFS.

## Rebuild
```bash
pip install numpy opencv-python-headless scipy pillow   # + ffmpeg; Pillow needs Raqm for Bengali shaping
python audio.py build/score.wav
python render.py --fresh                 # builds assets (~9 min), then renders durga_puja_50_years.mp4
python render.py --preview 14,36,74      # stills only (seconds)
```

## Files
| File | What it holds |
|---|---|
| `content.py` | Captions (English and Bengali) and the title |
| `timing.py` | Scene lengths |
| `flat.py` | Shape, outline and textile-pattern engine |
| `figures.py` | Parametric people (sarees, panjabi-dhoti, dhakis, dhunuchi dancers, priest) |
| `sets.py` | Thakur-dalan building and Durga (`durga_v3`) |
| `decor.py` | Folk lotus fields, peacocks, chalchitra, pandals, skylines and the phone |
| `scenes.py` | Composition and motion |
| `audio.py` | Score and sound effects |

Fonts are Playfair Display, Libre Franklin and Noto Serif Bengali, all under the SIL OFL.
