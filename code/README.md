# Code — The Golden Angle

The source that drew every math shot in the video, plus the guarded assembler. Pure Python + NumPy + SciPy + Pillow, encoded by ffmpeg. No GPU needed for the code plates.

| File | What |
|------|------|
| [`render_code_v2.py`](render_code_v2.py) | All 28 shipped code shots (`c_*`) at native 3840×2160, 24 fps. One generator per shot. |
| [`assemble_v2.py`](assemble_v2.py) | Guarded assembly: unique / moving / no pads / stretch ≤ 1.45×, then concat + mux + review + teaser + contact sheet |
| [`cutlist.json`](cutlist.json) | The 45-shot cut: id, start, end, duration (seconds) |
| [`render_bridge_angle.py`](render_bridge_angle.py) | Phase-1 test: the 8 s bridge angle sweep (30 fps) |
| [`render_vogel_sunflower.py`](render_vogel_sunflower.py) | Phase-1 test: the 8 s 3D Vogel sunflower orbit (30 fps) |
| [`requirements.txt`](requirements.txt) | Python packages |

## Run

```bash
pip install -r code/requirements.txt      # plus ffmpeg + ffprobe on PATH

# render one shot (writes bank/code_v2/<id>.mp4 next to the repo root)
python3 code/render_code_v2.py c_bridge

# render every code shot in the cutlist
python3 code/render_code_v2.py

# phase-1 tests (write to tests/)
python3 code/render_bridge_angle.py
python3 code/render_vogel_sunflower.py
```

Environment overrides: `GA_ROOT` (project root; default = repo root), `GA_CODE_OUT` (code plate folder), `GA_AUDIO` (song file for assembly).

## Assemble

`assemble_v2.py` expects plates the repo does not ship:

```
bank/code_v2/c_*.mp4        from render_code_v2.py
bank/hf_esrgan/h_*.mp4      your nature plates, upscaled to 4K (preferred)
bank/hf_4k/h_*.mp4          Lanczos fallback (master is labeled PROVISIONAL)
bank/hf/h_*.mp4             raw nature plates
golden-angle-v1.mp3         the song (or set GA_AUDIO)
```

Nature plates and the song are not in this repo. Generate your own nature plates with the prompt grammar in [`../DIALS.md`](../DIALS.md#nature-plate-prompt-grammar), or point the cutlist at your own footage.

## Notes

- A 4K shot is rendered by piping raw RGB frames into `ffmpeg -f rawvideo`. No frames are written to disk.
- Rendering is CPU-heavy: 4K frames with Gaussian glow at 24 fps. Run several workers in parallel; each shot takes an exclusive `mkdir` lock under `bank/code_v2/_locks/`, and a lock older than 45 minutes is treated as stale.
- Each shot has a fixed RNG seed, so re-renders are identical.
- Fonts: the bridge readout uses DejaVu Sans and falls back to Pillow's default font.
