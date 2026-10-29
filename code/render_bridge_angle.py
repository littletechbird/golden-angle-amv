#!/usr/bin/env python3
"""Native 4K bridge: golden-angle arm sweep → off-angle collapse → back to 137.5°."""
from __future__ import annotations
import math, subprocess
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = Path(__file__).resolve().parent.parent/'tests'
FRAMES = Path(__file__).resolve().parent.parent/('renders/bridge_frames')
OUT_DIR.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)

W, H = 3840, 2160
FPS = 30
DUR = 8.0
N = int(DUR * FPS)
CX, CY = W / 2.0, H / 2.0
GOLDEN = 137.5077640500378
N_SEEDS = 1200
# Fill ~78% of short side
SCALE = (min(W, H) * 0.39) / math.sqrt(N_SEEDS)

MAGMA = np.array([1.0, 0.38, 0.05], dtype=np.float32)
GOLD = np.array([1.0, 0.78, 0.22], dtype=np.float32)
CYAN = np.array([0.20, 0.92, 1.0], dtype=np.float32)
WHITE = np.array([1.0, 0.98, 0.92], dtype=np.float32)


def ease_in_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def angle_at(t: float) -> float:
    if t < 0.25:
        return GOLDEN
    if t < 0.50:
        u = ease_in_out((t - 0.25) / 0.25)
        return GOLDEN + (120.0 - GOLDEN) * u
    if t < 0.68:
        return 120.0
    u = ease_in_out((t - 0.68) / 0.32)
    return 120.0 + (GOLDEN - 120.0) * u


def vogel(n_seeds: int, angle_deg: float):
    n = np.arange(n_seeds, dtype=np.float32)
    th = np.deg2rad(angle_deg) * n
    r = SCALE * np.sqrt(n)
    return r * np.cos(th), r * np.sin(th), n, th


def splat_discs(img, xs, ys, radii, colors, strengths):
    """Additive soft discs."""
    h, w = img.shape[:2]
    for x, y, rad, col, s in zip(xs, ys, radii, colors, strengths):
        xi, yi = int(round(x)), int(round(y))
        r = max(1, int(math.ceil(rad)))
        x0, x1 = max(0, xi - r - 1), min(w, xi + r + 2)
        y0, y1 = max(0, yi - r - 1), min(h, yi + r + 2)
        if x0 >= x1 or y0 >= y1:
            continue
        yy, xx = np.ogrid[y0:y1, x0:x1]
        d2 = (xx - x) ** 2 + (yy - y) ** 2
        fall = np.exp(-d2 / (2 * (rad * 0.55) ** 2))
        img[y0:y1, x0:x1] += (fall * s)[:, :, None] * col


def render_frame(t: float, rng) -> np.ndarray:
    ang = angle_at(t)
    xs, ys, ns, ths = vogel(N_SEEDS, ang)
    rot = t * 0.55  # slow whole-field spin
    ca, sa = math.cos(rot), math.sin(rot)
    xr = xs * ca - ys * sa
    yr = xs * sa + ys * ca
    zoom = 1.05 + 0.08 * math.sin(t * math.pi)
    px = CX + xr * zoom
    py = CY + yr * zoom

    # fitness: 1 at golden, 0 at 120
    fit = 1.0 - abs(ang - GOLDEN) / abs(120.0 - GOLDEN)
    fit = max(0.0, min(1.0, fit))

    # work at half-res for glow then upsample
    sw, sh = W // 2, H // 2
    glow = np.zeros((sh, sw, 3), dtype=np.float32)
    scx, scy = sw / 2.0, sh / 2.0
    spx = scx + (px - CX) * 0.5
    spy = scy + (py - CY) * 0.5

    # color mix: golden magma when fit high; cyan/cold spokes when collapsed
    base_col = GOLD * (0.55 + 0.45 * fit) + MAGMA * (0.35 * fit) + CYAN * (0.55 * (1 - fit))
    # radii grow with index a bit
    rads = 1.2 + 2.8 * (ns / N_SEEDS) ** 0.6
    strengths = 0.55 + 0.9 * (1.0 - ns / N_SEEDS) ** 0.5
    # batch splat via scatter (faster): paint points then blur heavily
    ix = np.clip(spx.astype(np.int32), 0, sw - 1)
    iy = np.clip(spy.astype(np.int32), 0, sh - 1)
    # weight by strength
    for c in range(3):
        np.add.at(glow[:, :, c], (iy, ix), strengths * base_col[c])

    # multi-scale bloom
    g1 = gaussian_filter(glow, sigma=(0.8, 0.8, 0))
    g2 = gaussian_filter(glow, sigma=(2.5, 2.5, 0))
    g3 = gaussian_filter(glow, sigma=(8.0, 8.0, 0))
    g4 = gaussian_filter(glow, sigma=(22.0, 22.0, 0))
    glow = g1 * 1.8 + g2 * 1.4 + g3 * 0.9 + g4 * 0.45

    # upsample
    g8 = np.clip(glow * 255.0, 0, 255).astype(np.uint8)
    img = np.asarray(Image.fromarray(g8, 'RGB').resize((W, H), Image.Resampling.LANCZOS)).astype(np.float32) / 255.0

    # crisp cores
    ix2 = np.clip(px.astype(np.int32), 0, W - 1)
    iy2 = np.clip(py.astype(np.int32), 0, H - 1)
    core_col = WHITE * (0.4 + 0.6 * fit) + GOLD * 0.5
    for c in range(3):
        np.add.at(img[:, :, c], (iy2, ix2), (0.55 + 0.45 * (1 - ns / N_SEEDS)) * core_col[c])
    # 3x3 for nearer seeds
    near = ns < N_SEEDS * 0.35
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            xx = np.clip(ix2[near] + dx, 0, W - 1)
            yy = np.clip(iy2[near] + dy, 0, H - 1)
            for c in range(3):
                np.add.at(img[:, :, c], (yy, xx), 0.18 * core_col[c])

    # protractor arm + angle readout via PIL overlay
    pil = Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8), 'RGB')
    # draw on separate layer for glow arm
    arm_layer = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(arm_layer)
    # arm points along geometric displayed angle (from +x, screen y down)
    show = math.radians(-90)  # start upward, then offset by ang visualization
    # visualize the STEP angle as a wedge from a reference ray
    ref = -math.pi / 2
    a1 = ref
    a2 = ref + math.radians(ang)
    arm_len = min(W, H) * 0.42 * zoom
    # thick glowing arm for current angle
    for width, col in ((14, (20, 180, 220)), (6, (180, 240, 255)), (2, (255, 255, 255))):
        x2 = CX + math.cos(a2) * arm_len
        y2 = CY + math.sin(a2) * arm_len
        draw.line([(CX, CY), (x2, y2)], fill=col, width=width)
    # reference arm (faint)
    for width, col in ((8, (120, 60, 20)), (3, (255, 180, 60))):
        x2 = CX + math.cos(a1) * arm_len
        y2 = CY + math.sin(a1) * arm_len
        draw.line([(CX, CY), (x2, y2)], fill=col, width=width)
    # arc between
    bbox = [CX - arm_len * 0.28, CY - arm_len * 0.28, CX + arm_len * 0.28, CY + arm_len * 0.28]
    # PIL arc angles: 0 is +x, degrees clockwise... use approximate polyline
    pts = []
    for u in np.linspace(0, 1, 60):
        a = a1 + (a2 - a1) * u
        pts.append((CX + math.cos(a) * arm_len * 0.28, CY + math.sin(a) * arm_len * 0.28))
    if len(pts) > 1:
        draw.line(pts, fill=(255, 200, 80) if fit > 0.7 else (80, 200, 230), width=4)

    # label
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 72)
        font_s = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 48)
    except Exception:
        font = ImageFont.load_default()
        font_s = font
    label = f'{ang:.2f}°'
    status = 'GOLDEN ANGLE' if fit > 0.92 else ('COLLAPSE' if fit < 0.25 else 'DRIFT')
    # text with shadow
    tx, ty = int(W * 0.06), int(H * 0.08)
    for ox, oy in ((2, 2), (0, 0)):
        col = (0, 0, 0) if (ox, oy) != (0, 0) else ((255, 210, 80) if fit > 0.7 else (120, 230, 255))
        draw.text((tx + ox, ty + oy), label, font=font, fill=col)
        draw.text((tx + ox, ty + 90 + oy), status, font=font_s, fill=col)

    arm = np.asarray(arm_layer).astype(np.float32) / 255.0
    arm = gaussian_filter(arm, sigma=(1.2, 1.2, 0))
    img = img + arm * 1.15

    # center nucleus
    yy, xx = np.ogrid[:H, :W]
    d2 = (xx - CX) ** 2 + (yy - CY) ** 2
    nucleus = np.exp(-d2 / (2 * (18 ** 2)))
    img += nucleus[:, :, None] * (GOLD * 0.8 + WHITE * 0.4)

    # vignette + grain
    vig = np.clip(1.25 - np.sqrt(d2) / (min(W, H) * 0.78), 0.2, 1.0)
    img *= vig[:, :, None]
    grain = rng.random((H, W, 1), dtype=np.float32)
    img += (grain - 0.5) * 0.04

    img = np.clip(img, 0, 1)
    # gentle tone curve
    img = np.power(img, 0.88)
    return img


def main():
    rng = np.random.default_rng(1375)
    print(f'rendering {N} frames @ {W}x{H}, SCALE={SCALE:.3f}')
    for i in range(N):
        t = i / max(1, N - 1)
        frame = render_frame(t, rng)
        Image.fromarray((frame * 255).astype(np.uint8), 'RGB').save(FRAMES / f'f_{i:04d}.png', compress_level=1)
        if i % 10 == 0:
            print(f'  {i}/{N} angle={angle_at(t):.2f} fit={(1-abs(angle_at(t)-GOLDEN)/abs(120-GOLDEN)):.2f}')
    out4k = OUT_DIR / 'test_bridge_angle_4k.mp4'
    preview = OUT_DIR / 'test_bridge_angle_1080p.mp4'
    subprocess.check_call([
        'ffmpeg', '-y', '-framerate', str(FPS), '-i', str(FRAMES / 'f_%04d.png'),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '15', '-preset', 'medium',
        '-movflags', '+faststart', str(out4k),
    ])
    subprocess.check_call([
        'ffmpeg', '-y', '-i', str(out4k),
        '-vf', 'scale=1920:1080:flags=lanczos',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'fast',
        '-movflags', '+faststart', str(preview),
    ])
    # LOOK frames
    subprocess.check_call([
        'ffmpeg', '-y', '-i', str(out4k),
        '-vf', r"select=eq(n\,30)+eq(n\,90)+eq(n\,150)+eq(n\,210)",
        '-vsync', 'vfr', str((Path(__file__).resolve().parent.parent/'frames') / 'bridge_%02d.png'),
    ])
    print('OK', out4k, out4k.stat().st_size, preview.stat().st_size)


if __name__ == '__main__':
    main()
