# Process — The Golden Angle

Public pipeline for a 5-minute 4K math music video with no cast. Sister lessons from Fairy Tale / Equals / AMV Queen / You / Tesla Flywheel / Birth of Bird still apply. The Golden Angle adds **code as camera**, a **mixed code + nature bank**, and an **assembler that refuses to cheat**.

---

## Pipeline (locked order)

```
Thesis (one rule, no cast)
  → Suno custom, lyrics-first  (audio then locked; never recut)
  → Sung lyric map             (vocal stem + forced alignment, not a remembered paste)
  → Craft pack: 12 dials + shot list by lyric + G_plan
  → Phase-1 test triad         (bridge code · 3D Vogel code · one nature macro)
  → LOOK gate                  (human watches the three tests; GO before any wave)
  → Nature wave                (2K text-to-video, 17 plates)
  → Code bank                  (28 math plates, native 4K, re-runnable)
  → Real-ESRGAN                (nature 2K → 4K on a local GPU)
  → Guarded assembly           (unique · moving · no pads · no stretch > 1.45×)
  → LOOK gate                  (full playback + contact sheet)
  → Captions                   (39 cues, onset-snapped)
  → Thumbnail                  (type + one real sunflower)
  → YouTube 4K → Shorts → X
```

---

## 1. Thesis and song

- Write the thesis first: *one rule writes nature's order; the angle that never lines up is why it all fits.*
- Write lyrics that carry the math so the picture can be literal: "Seed. Turn." · "Thirty-four one way, fifty-five the other" · "One thirty-seven point five".
- Suno custom with full lyrics. Once the take is chosen, the audio is locked. The picture follows the song, never the reverse.

## 2. Sung lyric map

1. Separate the vocal (Demucs two-stem).
2. Read the lyrics the generator embedded in the file's tag. That is the text truth.
3. Force-align the known words to the vocal stem (stable-ts, then MMS as an independent check).
4. Mark the structure and the energy builds.

Don't transcribe the full mix with voice-activity detection turned on: in this song it deleted the vocals. See [`LYRIC_MAP.md`](LYRIC_MAP.md) for the drift table.

## 3. Craft pack

One page: thesis, 12 dials ([`DIALS.md`](DIALS.md)), shot list by lyric, the 4K plan, anti-jobs, and the unique-motion bank math:

```
G_old ≈ 28 planned pockets  →  G_plan = ceil(1.5 × 28) = 42 unique motions before assembly
```

## 4. Phase-1 test triad (before spending)

Three 8-second tests that between them prove the whole look:

| Test | Proves | Verdict |
|------|--------|---------|
| (a) Bridge angle sweep, code, native 4K | The thesis reads with no narration | PASS: 137.51° dense packing, drift to spokes, clean 3-spoke collapse at 120°, return |
| (b) 3D Vogel sunflower, code, native 4K | Chorus 34/55 light-up | PASS with nit: late orbit went edge-on; lock elevation ≥ 45° |
| (c) Nature macro sunflower, 2K text-to-video | The nature lane matches the code lane | PASS: real counter-rotating spirals, black void, real motion |

Only after a human LOOK GO on all three does any wave start.

## 5. Nature wave

- 17 prompts, one per nature pocket, written to the grammar in [`DIALS.md`](DIALS.md#nature-plate-prompt-grammar).
- Generated at the best resolution the plan allowed (2560×1440). 4K-native models needed a higher tier.
- 17 generated, 17 used. A tight prompt grammar plus the phase-1 test meant zero nature rejects.
- Native clip audio is never used. The song owns the soundtrack.

## 6. Code bank

- [`code/render_code_v2.py`](code/render_code_v2.py) renders all 28 code shots straight to 4K H.264 by piping raw frames into ffmpeg. No intermediate frames on disk.
- Each shot renders slightly longer than its pocket (`max(6, ceil(pocket + 0.4))` s) so assembly trims, never pads.
- Workers can run in parallel on several machines: each shot takes an exclusive `mkdir` lock, a lock older than 45 minutes counts as stale and can be taken over, and finished shots are skipped on re-run.
- v1 → v2: v2 added 2× supersampled line overlays, fatter seeds, and the nature-matched grade. See [`PLANNING.md`](PLANNING.md#v1--v2).

## 7. Real-ESRGAN

- Every nature plate goes 2K → 3840×2160 with Real-ESRGAN on a local GPU.
- Until every plate has an ESRGAN version, the assembler falls back to Lanczos and writes the master as `…_PROVISIONAL_lanczosHF.mp4`, so nobody mistakes it for the final.
- Drop finished plates into `bank/hf_esrgan/` and re-run assembly. The cutlist never changes.

## 8. Guarded assembly

[`code/assemble_v2.py`](code/assemble_v2.py):

1. For each cutlist entry: find the best source (ESRGAN > Lanczos > raw for nature; v2 > v1 for code).
2. **Guard:** no reuse; motion score ≥ 1.5; stretch ≤ 1.45×; no forbidden filter in the chain. Any failure is `FATAL GUARD`.
3. Cut each segment to the exact pocket length (scale, `setpts`, `fps`, `trim`) and encode.
4. Concat with stream copy, mux the untouched song (AAC 320k).
5. Write a 1080p review copy, a 40 s teaser from the final chorus, a contact sheet, a source map, and a guard report.

## 9. LOOK gate

- Watch the full 1080p review end to end. A summary is not a watch.
- Read the contact sheet: every shot visible, no black holes, no repeats.
- Two code plates (nautilus, storm) moved too little to read. The guard caught them, they were rebuilt full-frame, and the cut was re-assembled.

## 10. Captions

39 cues, at most 2 lines and 41 characters per line, no cues over instrumentals, each start snapped to the vocal onset. Captions ship only if the timing is right. Method: [`FORMULAS.md`](FORMULAS.md#10-song-clock-and-caption-timing).

## 11. Thumbnail

One real macro sunflower placed right, fading to black on the left. Gold serif type: **GOLDEN / ANGLE**, a thin rule, *137.5°*, A MUSIC VIDEO. See [`assets/thumbnail.jpg`](assets/thumbnail.jpg).

## 12. Ship

- YouTube long-form in 4K: **The Golden Angle | 4K**.
- Shorts: vertical cuts from the 4K master.
- X post when it goes live (link added to [`LINKS.md`](LINKS.md)).
