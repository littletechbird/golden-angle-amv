# Dials — The Golden Angle

Twelve locked dials. Once a dial is set, it stays set. No hedge words "for flexibility".

| # | Dial | Locked value |
|--:|------|--------------|
| 1 | **Palette** | Warm lifted black + magma/gold; cyan accent for the 34-arm family; warm gold for the 55-arm family |
| 2 | **Camera** | Slow, hypnotic, cinematic. Orbit and push only. Never whip-pan. |
| 3 | **Cut grid** | On beats and syllable drops (Seed / Turn; Shell / Storm / Pinecone / Galaxy) |
| 4 | **Motion law** | HARD: no stills, no Ken Burns, no freeze/tpad; every motion used once |
| 5 | **Code resolution** | Native 3840×2160. Never upscale a code plate. |
| 6 | **Nature resolution** | Best affordable text-to-video (2K at 2560×1440 on the plan used), then Real-ESRGAN to 4K. Never bicubic. |
| 7 | **Bloom / grain** | Soft bloom + subtle film grain on code; nature keeps its photoreal grit |
| 8 | **Energy arc** | intro hush → V1 grow → chorus light-up → V2 hard cuts → bridge thesis → final zoom-out → single seed |
| 9 | **Text on screen** | Bridge angle readout only (`137.51°` / `DRIFT` / `COLLAPSE` / `GOLDEN ANGLE`). No other titles. |
| 10 | **Mix ratio** | Plan ~55% code / ~45% nature. Shipped 69% / 31% by screen time. |
| 11 | **Audio** | Original song untouched. The picture follows the sung sheet only. |
| 12 | **Headroom** | Bank `G_plan = ceil(1.5 × G_old)` unique real-motion clips before assembly |

---

## Render constants (code plates)

| Constant | Value | Where |
|----------|-------|-------|
| Frame | 3840 × 2160 | `W, H` |
| Frame rate | 24 fps (phase-1 tests were 30 fps) | `FPS` |
| Supersample | 2× for line overlays (drawn at 7680 × 4320) | `SS` |
| Golden angle | 137.5077640500378° | `GOLDEN` |
| Seeds per head | 1,000–1,500 (100 per head in the field shot) | each generator |
| Seed glow | three Gaussian radii σ = 1.2, 3.5, 10 at half-res + 3×3 4K cores | `splat()` |
| Background floor | RGB (0.090, 0.075, 0.055), never pure black | `BG` |
| Encode | libx264, yuv420p, CRF 14, preset veryfast, +faststart | `encode()` |
| Determinism | fixed RNG seed per shot (201–229) | each generator |

## Assembly constants

| Constant | Value |
|----------|-------|
| Segment encode | libx264 CRF 16, yuv420p, audio stripped |
| Master audio | the song, AAC 320 kbps |
| Max stretch | 1.45× |
| Min motion score | 1.5 |
| Review copy | 1080p, CRF 16 → 18 → 20 until under 100 MB |
| Teaser | 40 s from the final chorus (257.4 s), 1080p CRF 20 |
| Contact sheet | one 320×180 frame per shot at 45% of its length, 5 columns |

## Nature plate prompt grammar

Every nature prompt named: the subject, the spiral it carries, macro or aerial, a slow real motion (rotate, drift, uncurl, orbit), and a dark or golden-hour background so it sits next to the code plates. Examples from the bank:

- macro sunflower, florets in counter-rotating spirals, black void, slow rotation
- macro nautilus shell, golden spiral, black background
- hurricane from above, spiral cloud bands
- macro pinecone, Fibonacci spirals; pinecone top-down rotating in golden light
- spiral galaxy, deep space
- aerial river delta branching
- Romanesco broccoli fractal macro
- field of sunflowers, aerial, slow
- golden light bending through a glass prism on black
- sunlight refracting through clear water ripples
- chambered nautilus cross-section
