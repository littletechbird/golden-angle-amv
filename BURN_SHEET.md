# Burn Sheet — The Golden Angle

Honest high-level crumbs. **Honesty over theater.** Where the meter was not re-read, we say so. Where costs lack receipts, we label them **ESTIMATE**.

---

## Wall clock (high level)

| Marker | Note |
|--------|------|
| Song take | Generated the evening of Oct 26, 2026 (PT) |
| Phase-1 test triad + LOOK | Same night |
| Nature wave + code bank v1 | Oct 26–27 |
| v2 (supersampled code, nature grade, ESRGAN 17/17, guarded master) | Morning of Oct 27 |
| Captions (39 cues, forced-aligned) | Evening of Oct 27 |
| Thumbnail + YouTube upload | After captions |

Song to 4K master took roughly **one day**. Code plates cost compute, not credits, and the guarded, re-runnable assembly made the v2 rebuild a single command.

---

## Spend by lane

| Lane | What | Crumb | Confidence |
|------|------|-------|------------|
| Nature plates | 17 × ~6 s text-to-video at 2560×1440 | Phase-1 test: **12 credits** for one 6.58 s clip. 17 plates at that rate ≈ **~200 credits** | **MED** (one metered test; wave not re-metered per clip) |
| Nature rejects | none | 17 generated, 17 used | **HIGH** |
| Code plates | 28 shipped + 2 benched + 2 near-still rejects re-rendered | Compute only, no API cost | **HIGH** |
| Upscale | Real-ESRGAN, 17 plates to 4K | Local GPU, no API cost | **HIGH** |
| Song | Suno custom | Subscription, **not receipted** as dollars here | **LOW** |
| Captions | Demucs, stable-ts, MMS | Local compute, no API cost | **HIGH** |
| Orchestration | Grok Bot / agent usage | Significant, **not metered for this cut alone** | **LOW** |

---

## Why this cut was cheap

- About **69% of screen time is code**. Code costs CPU time, not credits.
- The phase-1 test triad caught the look problems before the wave, so **zero nature rejects**.
- A tight prompt grammar (subject + spiral + macro/aerial + slow real motion + dark background) meant one take per plate.
- ESRGAN on a local GPU instead of a paid upscaler.

## Diminishing returns

- Re-generating a nature plate rarely beats fixing the code plate next to it.
- 4K-native generation needed a higher plan tier. The path taken was 2K generation plus Real-ESRGAN on a local GPU.
- Most of the polish budget went into the grade and the guards, not into more generations.

---

## What this sheet deliberately omits

- Vendor request IDs and job IDs
- Private local paths, machine names, and cloud folder IDs
- API keys and account emails
- Exact credit-wallet balances
