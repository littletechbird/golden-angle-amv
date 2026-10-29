# Formulas — The Golden Angle

Every number in this cut comes from one of the formulas below. Where code uses the formula, the file is named.

**Contents**

1. [The golden angle](#1-the-golden-angle)
2. [Vogel's sunflower (phyllotaxis)](#2-vogels-sunflower-phyllotaxis)
3. [Why 34 one way and 55 the other](#3-why-34-one-way-and-55-the-other)
4. [Why the angle that never lines up makes it fit](#4-why-the-angle-that-never-lines-up-makes-it-fit)
5. [The bridge: drift and collapse](#5-the-bridge-drift-and-collapse)
6. [Other spirals in the cut](#6-other-spirals-in-the-cut)
7. [Picture-planning math (G_plan, pockets, mix)](#7-picture-planning-math)
8. [Assembly guards](#8-assembly-guards)
9. [The grade (code plates match nature plates)](#9-the-grade)
10. [Song clock and caption timing](#10-song-clock-and-caption-timing)

---

## 1. The golden angle

```
φ = (1 + √5) / 2 ≈ 1.6180339887

golden angle  g = 360° · (1 − 1/φ)
                = 360° / φ²
                ≈ 137.5077640500°        (the other way round: 222.49°)
```

In code: `GOLDEN = 137.5077640500378` ([`code/render_code_v2.py`](code/render_code_v2.py)).

The bridge readout shows `137.51°`. The lyric rounds it to "one thirty-seven point five".

---

## 2. Vogel's sunflower (phyllotaxis)

Helmut Vogel's 1979 model places seed *n* at:

```
θₙ = n · g                (turn by the golden angle every seed)
rₙ = c · √n               (radius grows with the square root)

xₙ = rₙ cos θₙ
yₙ = rₙ sin θₙ
```

**Why √n:** the area of a disc grows as r². If r ∝ √n, then area ∝ n, so every new seed gets the same share of area. The head packs evenly from center to rim.

**Scale used in the cut:** `c = 0.44 · min(W, H) / √N`, so N seeds fill about 88% of the frame height.

```python
def vogel(n, angle=GOLDEN, scale=None):
    if scale is None: scale = (min(W, H) * 0.44) / math.sqrt(max(n, 1))
    i = np.arange(n); th = np.deg2rad(angle) * i; r = scale * np.sqrt(i)
    return r * np.cos(th), r * np.sin(th), i
```

**3D sunflower** (`g_vogel3d`): the same seeds lifted onto a gentle dome, then orbited by a pinhole camera.

```
Z = 0.13 · (1 − (r / r_max)²)         dome
camera: half-turn azimuth orbit, elevation 52° ± 10°, field of view 36°
brightness falls off with depth from the median (soft depth of field)
```

The elevation floor matters. See [LESSONS.md](LESSONS.md#picture): below about 45° the disc goes edge-on and the arms vanish.

---

## 3. Why 34 one way and 55 the other

The eye does not see a single spiral. It sees families of arms (parastichies). Seeds *n* and *n + k* sit next to each other when *k* golden-angle turns come out close to a whole number of full turns:

| k | k · g | Nearest whole turns | Miss | Arm direction |
|--:|------:|--------------------:|-----:|---------------|
| 21 | 2887.66° | 8 | +7.66° | clockwise family |
| **34** | 4675.26° | **13** | **−4.74°** | **one way** |
| **55** | 7562.93° | **21** | **+2.93°** | **the other** |
| 89 | 12238.19° | 34 | −1.81° | one way again (rim of big heads) |

The sign of the miss flips at every step, so neighbouring Fibonacci families curl in opposite directions. The whole-turn counts (8, 13, 21, 34) are Fibonacci numbers too. That happens because g/360° = 1/φ², and Fₖ/φ² is very close to Fₖ₋₂.

**In code:** the chorus lights the arms by index modulo the Fibonacci number.

```python
col[(i % 34) < 2] = CYAN                       # 34 arms, cyan
col[(i % 55) < 2] = GOLD*0.25 + AMBER*0.75     # 55 arms, warm gold
```

That is the lyric "Thirty-four one way, fifty-five the other / Nobody counted, still the numbers come". Nobody coded 34 or 55 spirals. Only the angle was coded. The arms appear by themselves.

---

## 4. Why the angle that never lines up makes it fit

Any angle that is a rational fraction of a turn, 360° · p/q, puts seed *q* exactly on top of seed 0. The head then grows *q* straight spokes with empty wedges between them, and light falls through the gaps.

φ is the irrational number that is hardest to approximate with fractions. Its continued fraction is all ones:

```
φ = 1 + 1/(1 + 1/(1 + 1/(1 + …)))     best fractions: 1/1, 2/1, 3/2, 5/3, 8/5, 13/8, 21/13, …
```

Every approximation is as poor as possible, so no seed ever lands on an earlier seed's ray. Each gap gets filled by the next seed. That is verse 1 ("Never quite repeat / nothing blocks the light behind it / every gap gets filled") and the bridge thesis ("The angle that never lines up / is the reason it all fits").

Nearby angles and the spoke count they collapse to (best fraction with q ≤ 100):

| Angle | Fraction of a turn | Spokes |
|------:|-------------------:|-------:|
| 120° | 1/3 | **3**, the COLLAPSE frame |
| 135° | 3/8 | 8 |
| 138° | 23/60 | 60 (visible spokes at the rim) |
| 144° | 2/5 | 5 |
| **137.5077…°** | irrational | **none** |

---

## 5. The bridge: drift and collapse

`g_bridge` ([`code/render_code_v2.py`](code/render_code_v2.py)); the phase-1 test version is [`code/render_bridge_angle.py`](code/render_bridge_angle.py).

Timeline over normalized shot time t ∈ [0, 1], with the smoothstep ease `e(t) = t²(3 − 2t)`:

| t | Angle |
|---|-------|
| 0.00–0.22 | hold 137.5077° (dense packing) |
| 0.22–0.48 | ease 137.5077° → 120° |
| 0.48–0.65 | hold 120° (three spokes) |
| 0.65–1.00 | ease 120° → 137.5077° (it fits again) |

```
fit   = clamp(1 − |angle − g| / |120 − g|, 0, 1)
label = "GOLDEN ANGLE" if fit > 0.92 else "COLLAPSE" if fit < 0.25 else "DRIFT"
color = gold·(0.55 + 0.5·fit) + amber·(0.45·fit) + cyan·(0.7·(1 − fit))
```

The seeds turn cyan as the angle leaves gold, and warm back up when it returns. The readout is the only on-screen text in the whole video.

---

## 6. Other spirals in the cut

| Shot | Formula |
|------|---------|
| `c_nautilus_code` | logarithmic spiral r = 34 · e^(0.3 θ), θ grows from 6.5 to 11.5 rad so the shell fills the frame; chamber rings every 0.62 rad |
| `c_galaxy_code` | three arms 120° apart, each r = 26 · e^(0.4 θ), y squashed × 0.6 for tilt, plus a 1,400-star field |
| `c_storm_code` | four arms 90° apart, r = 55 · e^((0.30 + 0.04·e(t)) θ), rotating and tightening, y × 0.62 |
| `c_fib_tiling` | Fibonacci squares 1, 1, 2, 3, 5, 8 … 233 laid around a corner with a quarter arc in each (6 → 14 squares) |
| `c_fib_syllables` / `c_fib_climb` | Vogel seed count n(t) = 1 + e(t) · 180 (syllables) or · 560 (climb) |
| `c_voronoi` | Voronoi cells around 55 → 185 Vogel seeds, cell edges in white |
| `c_field_code` | 22 small 100-seed Vogel heads scattered and slowly turning |
| `c_water_code` | recursive branching (depth 8–9, each branch × 0.70–0.73 long, splits ≈ −0.38 / +0.45 rad) |
| `c_petal_math` | petal count climbs 5 → 39 around a 300-seed Vogel head |
| `c_grow_pulse` | 1,200-seed head breathing at scale 1 + 0.24 · sin(5πt), 34-arm highlight |

---

## 7. Picture-planning math

**Unique-motion headroom.** Bank more unique clips than the cut needs, so you never pad.

```
G_plan = ceil(1.5 × G_old)
G_old  ≈ 28 planned pockets  →  G_plan = 42
Shipped: 45 unique shots in the cut, plus 2 code shots left on the bench.
```

**Pocket length** between lyric anchors (sister-pack formula, used for the first desk pass):

```
Δ ≈ D / (N − 1)          D = song length (318.67 s), N = anchor count
```

**Render length for code plates.** Code shots render slightly long, then get trimmed or sped up a little to fit the pocket exactly:

```
render_seconds = max(6, ceil(pocket + 0.4))
example: pocket 9.514 s → render 10 s → setpts 0.9514
```

**Mix target.** About 55% code / 45% nature by screen time was the plan. The cut landed at 69% / 31% (219.0 s / 99.7 s) because code carries the long intro, bridge and outro.

---

## 8. Assembly guards

From [`code/assemble_v2.py`](code/assemble_v2.py). Any failure exits with `FATAL GUARD` and no master is written.

| Guard | Rule |
|-------|------|
| **Reuse** | every shot id appears once in the cutlist |
| **Near-still** | motion score ≥ 1.5 |
| **Stretch** | pocket / source ≤ 1.45 (no slow-motion padding) |
| **Forbidden filters** | regex on every filter chain: `still_pad · kenburns · zoompan · tpad=stop_mode=clone · loop=-1 · freeze=` |
| **Provisional label** | if any nature plate is not from the Real-ESRGAN bank, the master file name gets `_PROVISIONAL_lanczosHF` |

**Motion score:**

```
for (a, b) in [(12%, 50%), (50%, 88%), (12%, 88%)] of the clip:
    A, B = grayscale frames at 320×180
    mask = (A > 12) | (B > 12)            # ignore black background
    d    = mean(|A − B|) over mask         (whole frame if mask < 30 px)
score = mean of the three d
```

The masked mean matters for math plates on dark backgrounds. Without the mask, a tiny moving dot scores near zero and a big glowing field scores high. Two early code plates (nautilus and storm) failed this guard. See [LESSONS.md](LESSONS.md#picture).

---

## 9. The grade

Pure-black math plates punched holes in the cut next to sunlit nature plates. `finish()` grades every code frame toward the nature plates' shadow floor:

```
img  = img · lift + BG · 1.35                 BG = (0.090, 0.075, 0.055)  warm lifted floor
img += ambient(σ = 0.55 · min(W,H)) · (0.10, 0.08, 0.045)
img += blur(max(img − 0.38, 0), σ = 5) · 0.7  bloom
img *= vignette = clamp(1.18 − d / (0.95 · min(W,H)), 0.55, 1)
img += grain ±0.02 + dither ±1/255
img *= (1.08, 1.02, 0.90)                     warm tint
img  = img ^ 0.85                             lift shadows to nature midtones
```

Seeds are splatted at half resolution with three glow radii (σ = 1.2, 3.5, 10), upscaled with Lanczos, then sharp 3×3 cores are added at full 4K. Line overlays (angle arms) are drawn at 2× (7680×4320) and downsampled. That is real supersampling, not an upscale.

Palette: magma `(1, .45, .10)`, gold `(1, .84, .32)`, cyan `(.20, .92, .95)`, teal, amber, warm white.

---

## 10. Song clock and caption timing

```
BPM ≈ 103.36   →  beat = 60 / 103.36 ≈ 0.581 s   →  bar (4/4) ≈ 2.32 s
537 beats · 1,230 onsets over 318.64 s (≈ 232 onsets/min)
```

Cuts land on beats and on syllable drops (the hard cuts on "Shell. Storm. Pinecone. Galaxy." at 1:53).

**Captions:**

- 39 cues, at most 2 lines, at most 41 characters per line, no cues over instrumentals.
- Alignment: stable-ts (faster-whisper large-v3) per section, then MMS wav2vec2 CTC forced alignment as an independent check, both on a Demucs vocal stem at 16 kHz mono.
- Each cue start snaps to the acoustic onset: the largest 20 ms energy rise within ±0.3 s, measured in the 3 kHz+ band for fricative or stop starts (S, Th, Sh, T, P) and 80–1000 Hz otherwise. Breaths are excluded.
- Master vs song offset by cross-correlation over 8 windows of 30 s: 0.00 ms in every window.
