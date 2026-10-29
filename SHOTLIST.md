# Shot list — The Golden Angle (as cut)

45 unique shots, each used **once**. `c_` = code plate (native 4K math render, [`code/render_code_v2.py`](code/render_code_v2.py)) · `h_` = nature plate (text-to-video at 2K → Real-ESRGAN 4K).

Source of truth: [`code/cutlist.json`](code/cutlist.json). Timecodes are picture time in the master (24 fps, 3840×2160).

| # | In | Out | Len (s) | Section | Shot | Source | What it shows |
|--:|---:|----:|--:|---|---|---|---|
| 1 | 0:00.00 | 0:09.51 | 9.51 | Intro | `c_intro_seed` | CODE | single glowing seed birth, slow grow |
| 2 | 0:09.51 | 0:20.93 | 11.42 | Intro | `c_intro_pair` | CODE | second seed at 137.5, arm appears |
| 3 | 0:20.93 | 0:27.43 | 6.50 | Intro | `h_daisy` | NATURE | macro daisy disc, florets in counter-spirals |
| 4 | 0:27.43 | 0:35.04 | 7.61 | Intro | `c_fib_syllables` | CODE | seeds drop on Fib syllable count |
| 5 | 0:35.04 | 0:39.80 | 4.76 | Intro | `c_fib_climb` | CODE | spiral densifies 1,1,2,3,5,8 |
| 6 | 0:39.80 | 0:45.80 | 6.00 | Verse 1 | `h_succulent` | NATURE | succulent rosette, leaf spiral |
| 7 | 0:45.80 | 0:51.44 | 5.64 | Verse 1 | `c_gaps_light` | CODE | rays of light through spiral gaps |
| 8 | 0:51.44 | 0:59.34 | 7.90 | Verse 1 | `c_voronoi` | CODE | Voronoi seed cells filling |
| 9 | 0:59.34 | 1:06.11 | 6.77 | Verse 1 | `c_grow_pulse` | CODE | whole head pulse grow |
| 10 | 1:06.11 | 1:11.18 | 5.08 | Verse 1 | `c_vogel_34` | CODE | vogel 34 cyan arms light |
| 11 | 1:11.18 | 1:16.60 | 5.42 | Verse 1 | `c_vogel_55` | CODE | vogel 55 gold arms light |
| 12 | 1:16.60 | 1:23.10 | 6.50 | Chorus 1 | `h_sunflower` | NATURE | macro sunflower rotate |
| 13 | 1:23.10 | 1:32.78 | 9.68 | Chorus 1 | `c_vogel_plain` | CODE | 3D vogel elev>=45 orbit plain gold |
| 14 | 1:32.78 | 1:38.78 | 6.00 | Chorus 1 | `h_fern` | NATURE | fern fiddlehead uncurling |
| 15 | 1:38.78 | 1:47.25 | 8.47 | Break | `c_turn_again_a` | CODE | rotating golden spiral hypnotic A |
| 16 | 1:47.25 | 1:53.30 | 6.05 | Break | `c_nautilus_code` | CODE | logarithmic spiral shell code |
| 17 | 1:53.30 | 1:58.30 | 5.00 | Verse 2 | `h_nautilus` | NATURE | macro nautilus shell golden spiral black bg |
| 18 | 1:58.30 | 2:03.12 | 4.82 | Verse 2 | `c_storm_code` | CODE | code hurricane spiral top-down |
| 19 | 2:03.12 | 2:08.12 | 5.00 | Verse 2 | `h_hurricane` | NATURE | hurricane from above spiral clouds |
| 20 | 2:08.12 | 2:13.13 | 5.01 | Verse 2 | `c_phyllotaxis_top` | CODE | top-down phyllotaxis spin |
| 21 | 2:13.13 | 2:18.34 | 5.20 | Verse 2 | `h_pinecone` | NATURE | macro pinecone Fibonacci spirals |
| 22 | 2:18.34 | 2:23.64 | 5.30 | Verse 2 | `c_galaxy_code` | CODE | golden spiral galaxy code |
| 23 | 2:23.64 | 2:29.14 | 5.50 | Verse 2 | `h_galaxy` | NATURE | spiral galaxy deep space |
| 24 | 2:29.14 | 2:34.44 | 5.30 | Chorus 2 | `c_water_code` | CODE | branching river, recursive tree |
| 25 | 2:34.44 | 2:39.94 | 5.50 | Chorus 2 | `h_river` | NATURE | aerial river delta branching |
| 26 | 2:39.94 | 2:45.73 | 5.79 | Chorus 2 | `c_spiral_dissolve` | CODE | sunflower dots dissolve/reform |
| 27 | 2:45.73 | 2:51.73 | 6.00 | Chorus 2 | `h_water_light` | NATURE | sunlight refracting through clear water ripples |
| 28 | 2:51.73 | 2:57.51 | 5.79 | Instrumental | `c_turn_again_b` | CODE | counter-rotate phyllotaxis B |
| 29 | 2:57.51 | 3:03.51 | 6.00 | Instrumental | `h_ammonite` | NATURE | ammonite fossil spiral |
| 30 | 3:03.51 | 3:09.30 | 5.79 | Instrumental | `c_rise_energy` | CODE | energy build dense particle spiral |
| 31 | 3:09.30 | 3:26.93 | 17.63 | Bridge | `c_bridge` | CODE | angle sweep 137.5→120→137.5 (phase1 keep) |
| 32 | 3:26.93 | 3:32.93 | 6.00 | Bridge | `h_whirlpool` | NATURE | aerial ocean whirlpool |
| 33 | 3:32.93 | 3:42.62 | 9.70 | Bridge | `c_angle_protractor` | CODE | pure protractor arm sweep no seeds |
| 34 | 3:42.62 | 3:48.62 | 6.00 | Rise | `h_romanesco` | NATURE | Romanesco broccoli fractal macro |
| 35 | 3:48.62 | 3:59.20 | 10.58 | Rise | `c_bridge_return` | CODE | bridge return golden only hold-motion |
| 36 | 3:59.20 | 4:05.70 | 6.50 | Rise | `h_flowers` | NATURE | field of sunflowers aerial slow |
| 37 | 4:05.70 | 4:16.27 | 10.58 | Rise | `c_fib_tiling` | CODE | Fibonacci rectangle tiling grow |
| 38 | 4:16.27 | 4:26.85 | 10.58 | Rise | `c_vogel_both` | CODE | vogel 34+55 dual light |
| 39 | 4:26.85 | 4:35.66 | 8.81 | Final chorus | `c_petal_math` | CODE | petal count Fib overlay math |
| 40 | 4:35.66 | 4:48.00 | 12.34 | Final chorus | `c_final_zoom_code` | CODE | zoom out nested spirals |
| 41 | 4:48.00 | 4:54.00 | 6.00 | Instrumental tag | `h_shell_side` | NATURE | chambered nautilus cross-section spiral |
| 42 | 4:54.00 | 5:00.00 | 6.00 | Instrumental tag | `h_pine_top` | NATURE | pinecone top-down rotating golden light |
| 43 | 5:00.00 | 5:06.00 | 6.00 | Outro | `h_light_glass` | NATURE | golden light bending through glass prism black |
| 44 | 5:06.00 | 5:12.00 | 6.00 | Outro | `c_field_code` | CODE | many tiny Vogel heads field |
| 45 | 5:12.00 | 5:18.67 | 6.67 | Outro | `c_outro_seed` | CODE | collapse to one seed fade |

**Totals:** 28 code shots (219.0s, 69%) · 17 nature shots (99.7s, 31%) · planned picture 318.67 s (the song length). The shipped master runs 316.58 s; see [LESSONS.md](LESSONS.md#audio-and-captions), lesson 18.

Planned mix was ~55% code / ~45% nature; the cut landed at the ratio above because the code plates carry the long intro, bridge and outro holds.

## Bank shots planned but not cut

Planned in the shot bank, then left out of the cut:

- `c_romanesco_code` — Romanesco fractal spiral code
- `c_seed_pair_orbit` — two seeds orbit at golden angle
