# Planning — The Golden Angle

How the cut was planned, gated, and versioned. Copy this structure for any no-cast or math-led music video.

---

## The craft pack (one page, written before any generation)

| Block | Content |
|-------|---------|
| Song facts | 5:18.67 · ≈103 BPM · audio locked as-is |
| Look lock | MIX of code math renders + photoreal nature · final 4K · no lip sync |
| Thesis | One rule, the golden angle, writes nature's order |
| North star | No cast. Subject = phyllotaxis: seed → sunflower → shell / storm / pinecone / galaxy → field |
| Dials | 12, see [`DIALS.md`](DIALS.md) |
| Unique-motion bank | `G_plan = ceil(1.5 × G_old)` = 42 |
| Shot list by lyric | which section gets which picture, and whether it is CODE or NATURE |
| 4K plan | code native 4K; nature masters kept, then Real-ESRGAN; master muxes the original song |
| Anti-jobs | no stills / Ken Burns, no distinctive recycling, no captions from an unrecovered paste, no single copy of anything on one machine |
| Next unlocks | phase-1 LOOK → lyric ear-check → nature wave inside remaining credits |

## Shot list by lyric (as planned)

| When | Picture | Source |
|------|---------|--------|
| Intro 0:00–0:40 | One glowing seed → second at 137.5° | CODE |
| V1 Seed / Turn | One seed per syllable (Fibonacci climb) | CODE |
| V1 gaps / light | Voronoi seed cells filling gaps | CODE |
| Chorus 1 34 / 55 | Sunflower → dot spiral; 34 cyan / 55 gold light | CODE + NATURE |
| Break | Slow orbit of the Vogel head with depth of field | CODE |
| V2 Shell | Nautilus on a shared golden spiral | NATURE |
| V2 Storm | Hurricane from above, same spiral | NATURE |
| V2 Pinecone | Macro pinecone spirals | NATURE |
| V2 Galaxy | Spiral galaxy | NATURE (or CODE if credits ran short) |
| Water / light | River branching + light refraction | NATURE |
| Bridge | Angle arm 137.5° → off-angle spokes → return | CODE (phase-1 test locked) |
| Final chorus | Zoom out: sunflower → pinecone → galaxy → flower field | CODE + NATURE |
| Outro | Back to one seed, fade to black | CODE |
| Flex bank | Fibonacci tiling, Romanesco fractal, 3D Vogel variants | CODE |

The shipped version is in [`SHOTLIST.md`](SHOTLIST.md). Verse 2 grew into code/nature pairs (code spiral, then the real thing) because the pairs argue the thesis better than nature alone.

## Bank sizing

| Bank | Planned | Built | Cut |
|------|--------:|------:|----:|
| Code (math) | 30 | 30 (v1) → 28 (v2) | 28 |
| Nature | 12 at first, grown to 17 | 17 | 17 |
| **Total unique** | **42 (G_plan)** | **47** | **45** |

Code shots left on the bench: `c_romanesco_code` and `c_seed_pair_orbit`. The real Romanesco plate beat the code version.

## Gates

```
Gate 0  Thesis + lyrics locked           → song generation
Gate 1  Song take chosen                 → audio locked forever
Gate 2  Sung lyric map                   → craft pack
Gate 3  Phase-1 test triad LOOK GO       → nature wave + code bank
Gate 4  Guard PASS + ESRGAN complete     → non-provisional master
Gate 5  Full-playback LOOK               → captions, thumbnail
Gate 6  Captions timed to the onset      → captions ship (else none)
Gate 7  Human GO                         → public upload / post
```

No gate is passed by a summary. Each one is passed by looking at the real file.

## v1 → v2

| | v1 | v2 (shipped) |
|-|----|--------------|
| Code plates | 4K renders + 1080p previews | Native 4K with 2× supersampled overlays and fatter seed cores |
| Code grade | Deep black, magma/gold | Warm lifted floor, ambient fill, bloom, grain, warm tint, gamma 0.85 to match nature shadows |
| Nature plates | Lanczos 2K → 4K (provisional) | Real-ESRGAN 4K, all 17 |
| Nautilus / storm | Tiny spirals (near-still) | Full-frame growing spirals |
| Master | Provisional | Non-provisional; guard PASS |
| Extras | — | 1080p review, 40 s teaser, contact sheet, captions, thumbnail |

The re-runnable design is what made v2 cheap. The cutlist stayed fixed, plates were swapped into their banks, and one command rebuilt the master.

## Distribution of work

- **Box (cloud Linux):** code renders, assembly, captions, review copies.
- **Local GPU desk:** Real-ESRGAN upscales and spare code-render workers.
- **Cloud drive:** the twin of every plate and master. Nothing lives as a single copy on one machine. A Done link goes out only after the drive copy's path and size are verified.
