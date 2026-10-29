#!/usr/bin/env python3
"""Native 4K 3D Vogel sunflower: orbit camera, DOF via CoC blur, 34/55 highlight."""
from __future__ import annotations
import math, subprocess
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image

OUT_DIR = Path(__file__).resolve().parent.parent/'tests'
FRAMES = Path(__file__).resolve().parent.parent/('renders/vogel_frames')
OUT_DIR.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)

W, H = 3840, 2160
FPS = 30
DUR = 8.0
N = int(DUR * FPS)
N_SEEDS = 1800
GOLDEN = 137.5077640500378

MAGMA = np.array([1.0, 0.40, 0.06], dtype=np.float32)
GOLD = np.array([1.0, 0.80, 0.25], dtype=np.float32)
CYAN = np.array([0.15, 0.95, 1.0], dtype=np.float32)
WHITE = np.array([1.0, 0.97, 0.90], dtype=np.float32)


def vogel_3d(n_seeds: int):
    n = np.arange(n_seeds, dtype=np.float64)
    th = np.deg2rad(GOLDEN) * n
    r = 0.042 * np.sqrt(n)
    x = r * np.cos(th)
    y = r * np.sin(th)
    z = 0.10 * (1.0 - (r / (0.042 * math.sqrt(n_seeds))) ** 2)
    return x, y, z, n


def project(x, y, z, cam_az, cam_el, cam_dist, fov_deg=38.0):
    ca, sa = math.cos(cam_az), math.sin(cam_az)
    ce, se = math.cos(cam_el), math.sin(cam_el)
    cx = cam_dist * ce * sa
    cy = cam_dist * se
    cz = cam_dist * ce * ca
    forward = np.array([-cx, -cy, -cz], dtype=np.float64)
    forward /= np.linalg.norm(forward)
    up = np.array([0.0, 1.0, 0.0])
    right = np.cross(forward, up)
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    pts = np.stack([x - cx, y - cy, z - cz], axis=1)
    xc = pts @ right
    yc = pts @ up
    zc = pts @ forward
    f = 0.5 * H / math.tan(math.radians(fov_deg) / 2)
    px = W * 0.5 + f * (xc / np.maximum(zc, 1e-3))
    py = H * 0.5 - f * (yc / np.maximum(zc, 1e-3))
    return px, py, zc


def render_frame(t, X, Y, Z, n, m34, m55, rng):
    # more top-down than smoke so 34/55 read as arms
    az = t * 2 * math.pi * 0.28
    el = math.radians(52 + 6 * math.sin(t * 2 * math.pi))
    dist = 2.35 - 0.12 * math.sin(t * math.pi)
    px, py, zc = project(X, Y, Z, az, el, dist)

    h34 = 0.0 if t < 0.30 else min(1.0, (t - 0.30) / 0.25)
    h55 = 0.0 if t < 0.60 else min(1.0, (t - 0.60) / 0.25)

    sw, sh = W // 2, H // 2
    focus = np.median(zc)
    # brightness
    bri = (0.50 + 0.85 * (1.0 - n / N_SEEDS) ** 0.55) * np.clip(1.35 - (zc - focus) * 0.4, 0.3, 1.5)

    # colors per seed
    col = np.broadcast_to((GOLD * 0.7 + MAGMA * 0.4), (N_SEEDS, 3)).copy()
    if h34 > 0:
        col[m34] = col[m34] * (1 - h34) + CYAN * h34
    if h55 > 0:
        warm = GOLD * 0.35 + np.array([1.0, 0.55, 0.08]) * 0.65
        col[m55] = col[m55] * (1 - 0.9 * h55) + warm * (0.9 * h55)

    glow = np.zeros((sh, sw, 3), dtype=np.float32)
    ix = np.clip((px * 0.5).astype(np.int32), 0, sw - 1)
    iy = np.clip((py * 0.5).astype(np.int32), 0, sh - 1)
    w = bri.astype(np.float32)
    for c in range(3):
        np.add.at(glow[:, :, c], (iy, ix), w * col[:, c].astype(np.float32))
        # slight neighborhood for seed body
        np.add.at(glow[:, :, c], (np.clip(iy + 1, 0, sh - 1), ix), w * col[:, c] * 0.35)
        np.add.at(glow[:, :, c], (iy, np.clip(ix + 1, 0, sw - 1)), w * col[:, c] * 0.35)

    # DOF: stronger blur on a duplicate of far seeds approx via global multi-scale
    g1 = gaussian_filter(glow, (0.7, 0.7, 0))
    g2 = gaussian_filter(glow, (2.4, 2.4, 0))
    g3 = gaussian_filter(glow, (8.0, 8.0, 0))
    g4 = gaussian_filter(glow, (20.0, 20.0, 0))
    # Mix more blur when camera is lower (already el high); keep crisp cores via g1
    glow = g1 * 1.9 + g2 * 1.3 + g3 * 0.75 + g4 * 0.4

    img = np.asarray(
        Image.fromarray(np.clip(glow * 255, 0, 255).astype(np.uint8), 'RGB').resize((W, H), Image.Resampling.LANCZOS)
    ).astype(np.float32) / 255.0

    # crisp cores near focus
    near = np.abs(zc - focus) < 0.10
    ix2 = np.clip(px[near].astype(np.int32), 0, W - 1)
    iy2 = np.clip(py[near].astype(np.int32), 0, H - 1)
    for c in range(3):
        np.add.at(img[:, :, c], (iy2, ix2), 0.65 * WHITE[c])

    yy, xx = np.ogrid[:H, :W]
    d2 = (xx - W / 2) ** 2 + (yy - H / 2) ** 2
    vig = np.clip(1.18 - np.sqrt(d2) / (min(W, H) * 0.78), 0.2, 1.0)
    img *= vig[:, :, None]
    img += (rng.random((H, W, 1), dtype=np.float32) - 0.5) * 0.032
    return np.clip(np.power(np.clip(img, 0, 1), 0.90), 0, 1)


def main():
    rng = np.random.default_rng(55)
    X, Y, Z, n = vogel_3d(N_SEEDS)
    ni = n.astype(int)
    m34 = (ni % 34) < 2
    m55 = (ni % 55) < 2
    print(f'rendering {N} frames @ {W}x{H}')
    for i in range(N):
        t = i / max(1, N - 1)
        frame = render_frame(t, X, Y, Z, n, m34, m55, rng)
        Image.fromarray((frame * 255).astype(np.uint8), 'RGB').save(FRAMES / f'f_{i:04d}.png', compress_level=1)
        if i % 10 == 0:
            print(f'  {i}/{N}', flush=True)
    out4k = OUT_DIR / 'test_vogel_sunflower_4k.mp4'
    preview = OUT_DIR / 'test_vogel_sunflower_1080p.mp4'
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
    subprocess.check_call([
        'ffmpeg', '-y', '-i', str(out4k),
        '-vf', r"select=eq(n\,45)+eq(n\,130)+eq(n\,210)",
        '-vsync', 'vfr', str((Path(__file__).resolve().parent.parent/'frames') / 'vogel_%02d.png'),
    ])
    print('OK', out4k.stat().st_size, preview.stat().st_size)


if __name__ == '__main__':
    main()
