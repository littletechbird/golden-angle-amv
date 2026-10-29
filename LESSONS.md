# Lessons — The Golden Angle

What broke, what fixed it, and what to carry into the next cut. Grouped by area. Each lesson is one line of rule with the reason under it.

**Contents:** [Planning](#planning) · [Picture](#picture) · [Audio and captions](#audio-and-captions) · [Pipeline and ops](#pipeline-and-ops) · [Thoughts](#thoughts)

---

## Planning

**1. Three tests before any wave.**
The bridge sweep, the 3D sunflower and one nature macro together proved the thesis read with no narration, the chorus light-up worked, and the nature lane matched the code lane. After that GO, 17 of 17 nature plates were keepers.

**2. A no-cast video needs a rule lock instead of an identity lock.**
With no faces to keep consistent, the continuity question becomes "does this shot carry the same spiral?" Ask it of every plate.

**3. Write lyrics the picture can take literally.**
"Seed. Turn." · "Thirty-four one way, fifty-five the other" · "One thirty-seven point five." Each line hands the editor a shot. Math lyrics plus math picture is the whole concept.

**4. Pair code and nature in verse 2.**
Code shell → real shell, code storm → real hurricane, code top-down → real pinecone, code galaxy → real galaxy. The pair turns "nobody drew it and it's everywhere" from a claim into a demonstration.

**5. Bank more than you need.**
`G_plan = ceil(1.5 × 28) = 42`; 47 were built; 45 made the cut. Headroom meant no pocket ever needed a pad.

## Picture

**6. Never upscale code. Render it at the delivery resolution.**
Math is free to render at 4K. An upscaled code plate is softer for no reason.

**7. Real-ESRGAN, not bicubic, for generated footage.**
The 2K nature plates held up at 4K only after ESRGAN. The Lanczos version stayed labeled PROVISIONAL until the last ESRGAN plate landed.

**8. Keep the 3D sunflower's camera at 45° or above.**
In the phase-1 test the late orbit went nearly edge-on, and the disc collapsed into a thin vertical column. The shipped orbit holds 52° ± 10°.

**9. A small moving thing in a big black frame is a still.**
The first code nautilus maxed out around a 46 px radius and the first storm around 97 px arms. Both read as a dot. The motion guard rejected them (they are kept as `_nearstill` rejects), and they were rebuilt as full-frame growing spirals. Rule: the subject of a code plate fills the frame at some point in the shot.

**10. Mask the background when you score motion.**
On dark math plates, an unmasked frame difference is dominated by black. Scoring only pixels brighter than 12/255 makes the near-still test honest.

**11. Grade code to nature, not nature to code.**
Pure-black code plates punched holes in the cut next to sunlit nature. Lifting the floor to a warm (0.090, 0.075, 0.055), adding an ambient fill and gamma 0.85 made the cuts feel like one film. Nature keeps its own grit.

**12. Seed rendering: half-res glow + full-res cores.**
Three Gaussian glow radii at half resolution, upscaled, plus sharp 3×3 cores at 4K, gives soft bloom with crisp seeds at a fraction of the cost of full 4K blurs. v2 answered the phase-1 nit ("point splats, not shaded discs") with fatter cores; true shaded discs are still on the wish list.

**13. One piece of on-screen text, earned.**
The bridge readout (`137.51°` → `DRIFT` → `120.00° COLLAPSE` → `GOLDEN ANGLE`) is the only text in five minutes, so it lands.

## Audio and captions

**14. Don't run voice-activity detection on a sung mix.**
VAD treated the vocal as non-speech and wiped it. Transcribe without VAD, or better, on the isolated vocal stem.

**15. The song file already knows the lyrics.**
Suno writes the lyrics into the audio file's tag. Read that first. Speech recognition guessed "light bends to grow the loss" for "light bends too, the rule holds, holds", and "eternal plan" for "by a turn, no plan".

**16. Captions need two aligners and an onset snap.**
stable-ts on the vocal stem, MMS forced alignment as an independent check, then snap each start to the largest 20 ms energy rise within ±0.3 s (high band for S / Th / Sh / T / P). Breaths before a line don't count as the start.

**17. Prove the master's audio is the song.**
Cross-correlate master audio against the song in 8 windows of 30 s. The result was 0.00 ms offset in every window.

**18. Check the master's length against the song's.**
The cutlist adds up to 318.67 s, the song's length. The concatenated picture came out at 316.58 s, about one frame short per segment across 45 segments, and the `-shortest` mux then ended the audio there too. Only the soft outro fade was lost, and nothing sung. Next time: probe the concat length before muxing, carry the rounding error into the next segment's pocket, and fill any gap with real motion, never a freeze.

**19. The first structure map can mislabel sections.**
The ASR-based map called the second chorus a "turn tag". Shots planned against that map straddle a few section lines. Re-map after forced alignment, before cutting.

## Pipeline and ops

**20. Re-runnable assembly beats hand edits.**
Fixed cutlist + source priority (ESRGAN > Lanczos > raw; v2 > v1) + resume on existing segments. Upgrading the whole film from v1 to v2 was one command.

**21. Guards in the build, not in review.**
Reuse, near-still, stretch and forbidden filters exit the build. Nobody has to remember the rules at 2 AM.

**22. Lock files let two machines share one render queue.**
An exclusive `mkdir` lock per shot, a 45-minute stale takeover, and skip-if-done let the cloud box and a local GPU desk render the same bank without collisions.

**23. Pipe frames straight into ffmpeg.**
Raw RGB frames into `ffmpeg -f rawvideo` means a 4K code shot never touches disk as images.

**24. Deterministic shots.**
Each code shot has its own fixed RNG seed (201–229). A re-render is bit-for-bit the same picture, so a fix to one shot can't silently change another.

**25. Twin everything, then link.**
Every plate and master was copied to a cloud drive, and the copy's path and size were verified before anyone got a link.

## Thoughts

- This is the first pack in the series where the code *is* the footage. Half the film can be re-rendered from one 575-line Python file, at any resolution and any length.
- The thesis and the method turned out to be the same idea. One simple rule (unique motion, used once, never padded) and the whole cut follows.
- Nature generators are good at spirals because the real world is full of them. Prompting the spiral by name (Fibonacci florets, golden spiral, logarithmic chambers) was more reliable than describing the object alone.
- A math video can still be emotional. The bridge, where the angle breaks and the seeds go cyan and fall into three cold spokes, is the moment people remember, because it shows what would happen without the rule.
- Next time: shaded seed discs instead of point splats, a code Romanesco that beats the real one, and the master length checked against the song before upload.
