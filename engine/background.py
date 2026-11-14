"""The drifting background glows, composited by ffmpeg behind each scene (not drawn by ManimGX).

Scenes render on a transparent background (premultiplied RGBA). render.py pipes those frames into
ffmpeg, which lays them over: a flat BG colour, then two soft glow images that drift with time.
The glows are RGBA PNGs with a Gaussian falloff that reaches zero at the rim (no hard circular edge)
and a little alpha dither so the 8-bit gradient does not band into rings. Drawing them in ffmpeg
instead of as ManimGX fills is also much faster on a CPU. The slow drift also means no two frames
are identical, so the output is a true constant 30 fps.

Drift (scene-local time t, scene units):
  glow 1 centre: (-3.5 + 0.8 sin 0.21t,  1.2 + 0.5 cos 0.17t), radius 5.5, colour #1c2a4a
  glow 2 centre: ( 3.8 + 0.7 cos 0.19t, -0.8 + 0.5 sin 0.23t), radius 4.0, colour #2a1c4a
"""
import math
import numpy as np

import project
from style import BG, WIDTH, HEIGHT, FPS

PX = HEIGHT / 8.0  # pixels per scene unit (180 at 1440p)

GLOWS = [  # (name, colour, radius in units, peak opacity, seed, x(t), y(t))
    ("glow1", "#1c2a4a", 5.5, 0.30, 11, "-3.5+0.8*sin(0.21*t)", "1.2+0.5*cos(0.17*t)"),
    ("glow2", "#2a1c4a", 4.0, 0.22, 12, "3.8+0.7*cos(0.19*t)", "-0.8+0.5*sin(0.23*t)"),
]


def _glow_rgba(color, radius_units, peak, seed):
    n = int(round(2 * radius_units * PX))
    c = color.lstrip("#")
    rgb = [int(c[i:i + 2], 16) for i in (0, 2, 4)]
    yy, xx = np.mgrid[0:n, 0:n]
    r = np.hypot(xx - (n - 1) / 2, yy - (n - 1) / 2) / ((n - 1) / 2)   # 0 centre .. 1 rim
    a = np.exp(-(r / 0.5) ** 2) * np.clip(1 - r, 0, 1) ** 1.5 * peak * 255
    rng = np.random.default_rng(seed)
    a = a + (rng.random((n, n)) + rng.random((n, n)) - 1.0) * 6.0 * np.clip(a / 6.0, 0, 1)
    img = np.zeros((n, n, 4), np.uint8)
    img[..., :3] = rgb
    img[..., 3] = np.clip(np.round(a), 0, 255).astype(np.uint8)
    return img


def glow_paths():
    """The glow PNGs, drawn once into the cache folder (~/.cache/video-gen or $VG_CACHE)."""
    from PIL import Image
    paths = []
    for name, col, rad, peak, seed, _, _ in GLOWS:
        p = project.cache_dir() / f"{name}_{HEIGHT}p_{col.lstrip('#')}_{rad}_{peak}_{seed}.png"
        if not p.exists():
            tmp = p.with_suffix(".tmp.png")
            Image.fromarray(_glow_rgba(col, rad, peak, seed), "RGBA").save(tmp)
            tmp.replace(p)
        paths.append(p)
    return paths


def ffmpeg_filter():
    """filter_complex: input 0 = scene RGBA (premultiplied), 1 = BG colour, 2.. = glow PNGs."""
    parts, prev = [], "[1:v]"
    for k, (_, _, _, _, _, fx, fy) in enumerate(GLOWS):
        x = f"{WIDTH / 2}+{PX}*({fx})-overlay_w/2"
        y = f"{HEIGHT / 2}-{PX}*({fy})-overlay_h/2"
        parts.append(f"{prev}[{k + 2}:v]overlay=x='{x}':y='{y}':eval=frame[g{k}]")
        prev = f"[g{k}]"
    parts.append(f"{prev}[0:v]overlay=alpha=premultiplied:eof_action=endall,format=yuv420p")
    return ";".join(parts)


def ffmpeg_inputs():
    args = ["-f", "lavfi", "-i", f"color=c=0x{BG.lstrip('#')}:s={WIDTH}x{HEIGHT}:r={FPS}"]
    for p in glow_paths():
        args += ["-loop", "1", "-framerate", str(FPS), "-i", str(p)]
    return args


def composite_still(rgba_premult, t):
    """Same composite in numpy, for stills: premultiplied RGBA frame at scene time t -> RGB uint8."""
    from PIL import Image
    c = BG.lstrip("#")
    out = np.zeros((HEIGHT, WIDTH, 3), np.float32)
    out[:] = [int(c[i:i + 2], 16) for i in (0, 2, 4)]
    env = {"sin": math.sin, "cos": math.cos, "t": t}
    for p, g_def in zip(glow_paths(), GLOWS):
        fx, fy = g_def[-2], g_def[-1]
        g = np.asarray(Image.open(p).convert("RGBA")).astype(np.float32)
        h, w = g.shape[:2]
        x0 = int(WIDTH / 2 + PX * eval(fx, {"__builtins__": {}}, env) - w / 2)   # constant expressions above
        y0 = int(HEIGHT / 2 - PX * eval(fy, {"__builtins__": {}}, env) - h / 2)
        X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(WIDTH, x0 + w), min(HEIGHT, y0 + h)
        if X1 <= X0 or Y1 <= Y0:
            continue
        gs = g[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
        a = gs[..., 3:4] / 255.0
        out[Y0:Y1, X0:X1] = gs[..., :3] * a + out[Y0:Y1, X0:X1] * (1 - a)
    fr = rgba_premult.astype(np.float32)
    a = fr[..., 3:4] / 255.0
    out = fr[..., :3] + out * (1 - a)
    return np.clip(np.round(out), 0, 255).astype(np.uint8)
