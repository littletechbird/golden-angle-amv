# The Golden Angle — Craft Laws

**Status:** HARD public checklist. The rule is the star. Unique motion over volume.

If a choice fights this sheet, stop and re-read it.

---

## The rule is the star

- Every shot shows the golden angle at work, in math or in nature. If a shot doesn't carry the spiral, cut it.
- No characters, no faces, no mascots. Nothing to lip-sync.
- On-screen text: the bridge angle readout only.
- Nature plates carry the *same* spiral the code just drew. Pair them: code spiral, then the real thing.

## Motion (HARD, enforced in code)

- Unique forward motion only. Every shot is used **once**.
- No stills. No Ken Burns. No `zoompan`. No `tpad` clone frames. No `loop`. No `freeze`.
- No slow-motion padding: a source may be stretched at most 1.45× to fill its pocket.
- A plate that barely moves fails (motion score < 1.5). A tiny spiral in a big black frame counts as barely moving.
- The assembler checks all of this and exits with `FATAL GUARD`. The guard is part of the build, not a review step.

## Resolution

- Code plates: native 3840×2160. Never upscale a code plate. If it looks soft, fix the renderer.
- Nature plates: generate at the best affordable size, then Real-ESRGAN to 4K. Plain bicubic or Lanczos is provisional only, and the file name says so.
- Draw lines at 2× and downsample. Render seed glow at half resolution, then add sharp full-resolution cores.

## Look

- Palette: warm lifted black, magma, gold; cyan for the 34-arm family; warm gold for the 55.
- Code plates match the nature plates' shadow floor. Pure black next to a sunlit plate reads as a hole in the cut.
- Camera: slow orbit and push. Never whip-pan.
- 3D sunflower elevation stays at 45° or above, or the head goes edge-on and the spirals disappear.

## Audio

- The song is locked once the take is chosen. No recut, no loudness restyle unless asked.
- Native audio on generated clips is discarded.
- The picture follows the sung sheet, not a remembered lyric paste.

## Captions

- Captions follow what is sung on the take, checked against the lyrics embedded in the song file.
- Every cue starts on the acoustic onset of its first word. If the timing isn't right, ship no captions.
- No cues over instrumentals. At most 2 lines, 41 characters each.

## Process

- Run the phase-1 test triad (bridge, 3D sunflower, one nature macro) and get a human LOOK GO before any wave.
- **No timecode without LOOK:** before commenting on a timestamp, actually look at it (full playback or a frame grab). Inferring from the cut list doesn't count.
- Assembly is re-runnable. Swapping a plate means dropping it into its bank and re-running. Never hand-edit a master.
- Keep a twin of every plate and master off the render machine. A Done link goes out only after the twin's path and size are verified.

## Kill criteria (don't ship)

- Any repeated shot, freeze, still, or Ken Burns body
- A near-still code plate (a dot in the middle of a black frame)
- A code plate that was upscaled
- A master still labeled PROVISIONAL
- On-screen text beyond the angle readout
- Captions that drift off the vocal, or that come from an unverified lyric sheet
- Summary-only QA, or skimming counted as watching
