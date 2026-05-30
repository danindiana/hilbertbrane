"""
generate_spin.py — 360° neon Hilbert cube spin GIF

Renders 72 frames (5° Y-axis rotation steps) of the 3D Hilbert curve with
the same neon-glow style as generate_logo.py, then assembles with ImageMagick.
Output: docs/spin.gif

Run from repo root:  python generate_spin.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from itertools import product
import subprocess
import os
import sys

# ── palette ──────────────────────────────────────────────────────────────────
BG   = "#0d1117"
CYAN = "#00bfff"
PINK = "#ff2d78"
GOLD = "#ffe600"
TEAL = "#00ffe7"

# ── config ───────────────────────────────────────────────────────────────────
SIZE     = 600      # square canvas (px)
DPI      = 100
N_FRAMES = 72       # 5° per step → full 360°
DELAY_CS = 4        # centiseconds per frame (4 = 25 fps → ~2.9 s loop)
TILT_DEG = 28       # fixed downward tilt during rotation
ORDER    = 3        # Hilbert order (512 points; fast to render)
MARGIN   = 55       # px clearance on each side


# ── 1.  Hilbert path (same Gray-code as HilbertGyri.py) ─────────────────────
def _h3d(x, y, z, n):
    h = 0
    for i in range(n):
        xb = (x >> i) & 1
        yb = (y >> i) & 1
        zb = (z >> i) & 1
        p  = (xb << 2) | (yb << 1) | zb
        p ^= p >> 1
        h |= p << (3 * i)
    return h

def hilbert3d(order=3):
    N   = 2 ** order
    pts = []
    for x, y, z in product(range(N), repeat=3):
        pts.append((_h3d(x, y, z, order), x, y, z))
    pts.sort()
    return np.array([(x, y, z) for _, x, y, z in pts], dtype=float)


# ── 2.  Colour gradient ───────────────────────────────────────────────────────
def _hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def grad_colors(n, stops):
    rgb  = [_hex_rgb(c) for _, c in stops]
    ts   = [t           for t, _ in stops]
    out  = np.zeros((n, 3))
    tv   = np.linspace(0.0, 1.0, n)
    for i, t in enumerate(tv):
        j = 0
        while j < len(ts) - 2 and ts[j + 1] < t:
            j += 1
        t0, t1 = ts[j], ts[j + 1]
        f = np.clip((t - t0) / (t1 - t0 + 1e-12), 0.0, 1.0)
        out[i] = [rgb[j][k] + f * (rgb[j+1][k] - rgb[j][k]) for k in range(3)]
    return out


# ── 3.  Rotation + projection ─────────────────────────────────────────────────
def rotate_y(pts, deg):
    r  = np.radians(deg)
    cy, sy = np.cos(r), np.sin(r)
    x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
    return np.column_stack([cy*x + sy*z, y, -sy*x + cy*z])

def project(pts, tilt_deg=TILT_DEG):
    r  = np.radians(tilt_deg)
    cx, sx = np.cos(r), np.sin(r)
    x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
    return x, cx*y - sx*z


# ── 4.  Render one frame ──────────────────────────────────────────────────────
def render_frame(path3d, angle_deg, colors_rgb, scale, cx, cy, label_alpha=0.22):
    fig = plt.figure(figsize=(SIZE / DPI, SIZE / DPI), dpi=DPI)
    fig.patch.set_facecolor(BG)
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.set_xlim(0, SIZE)
    ax.set_ylim(0, SIZE)
    ax.axis("off")

    # rotate + project + scale
    rot  = rotate_y(path3d, angle_deg)
    px, py = project(rot)
    px_s = (px - px.mean()) * scale + cx
    py_s = (py - py.mean()) * scale + cy

    # LineCollection segments
    pts2d = np.column_stack([px_s, py_s]).reshape(-1, 1, 2)
    segs  = np.concatenate([pts2d[:-1], pts2d[1:]], axis=1)
    n_seg = len(segs)

    # soft radial bloom (background glow behind the curve)
    theta = np.linspace(0, 2 * np.pi, 300)
    for r, a, col in [
        (230, 0.010, CYAN),
        (160, 0.016, PINK),
        (100, 0.022, GOLD),
        (55,  0.028, CYAN),
    ]:
        ax.fill(cx + r * np.cos(theta), cy + r * np.sin(theta),
                color=col, alpha=a, zorder=0)

    # neon glow layers (outermost halo → bright core)
    for lw, alpha in [
        (30,  0.022),
        (17,  0.055),
        (7,   0.140),
        (2.8, 0.500),
        (0.8, 1.000),
    ]:
        rgba = np.column_stack([colors_rgb, np.full(n_seg, alpha)])
        lc   = LineCollection(segs, colors=rgba, linewidths=lw,
                              capstyle="round", joinstyle="round", zorder=1)
        ax.add_collection(lc)

    # bright vertex dots at every 32nd path point
    step  = 32
    dcols = grad_colors(len(px_s[::step]), [(0.0, CYAN), (0.5, PINK), (1.0, GOLD)])
    for dx, dy, dc in zip(px_s[::step], py_s[::step], dcols):
        # halo
        ax.plot(dx, dy, "o", color=list(dc) + [0.13],
                markersize=10, zorder=2, markeredgewidth=0)
        # bright core
        ax.plot(dx, dy, "o", color=dc,
                markersize=4.5, zorder=3, markeredgewidth=0)

    # subtle watermark at bottom
    ax.text(SIZE / 2, 22, "HILBERTBRANE",
            fontsize=9, color=TEAL, ha="center", va="center",
            fontfamily="monospace", alpha=label_alpha)

    return fig


# ── 5.  Main ──────────────────────────────────────────────────────────────────
def main():
    print(f"Building {ORDER}rd-order Hilbert path …")
    path3d  = hilbert3d(ORDER)          # (512, 3)
    path3d -= path3d.mean(axis=0)       # centre at origin

    # compute a scale that keeps the curve inside the canvas for ALL angles
    print("Computing safe scale across all rotation angles …")
    max_ext = 0.0
    for a in range(0, 360, 5):
        rot  = rotate_y(path3d, a)
        px, py = project(rot)
        ext  = max(px.max() - px.min(), py.max() - py.min())
        if ext > max_ext:
            max_ext = ext
    scale = (SIZE - 2 * MARGIN) / max_ext
    cx, cy = SIZE / 2.0, SIZE / 2.0
    print(f"  max_extent={max_ext:.2f}, scale={scale:.3f}")

    # pre-compute colour gradient (constant along the path — doesn't rotate)
    stops      = [(0.0, CYAN), (0.5, PINK), (1.0, GOLD)]
    colors_rgb = grad_colors(len(path3d) - 1, stops)

    # render frames
    print(f"Rendering {N_FRAMES} frames at {SIZE}×{SIZE} px …")
    frame_paths = []
    for i in range(N_FRAMES):
        angle  = 360.0 * i / N_FRAMES
        fig    = render_frame(path3d, angle, colors_rgb, scale, cx, cy)
        fpath  = f"/tmp/hilbert_spin_{i:04d}.png"
        fig.savefig(fpath, dpi=DPI, facecolor=BG, bbox_inches=None)
        plt.close(fig)
        frame_paths.append(fpath)
        if (i + 1) % 12 == 0 or i == 0:
            pct = (i + 1) / N_FRAMES * 100
            print(f"  [{pct:5.1f}%]  frame {i+1}/{N_FRAMES}  (angle={angle:.0f}°)")

    # assemble GIF
    print("Assembling GIF with ImageMagick …")
    out = "docs/spin.gif"
    subprocess.run(
        ["convert",
         "-delay", str(DELAY_CS),
         "-loop",  "0"]
        + frame_paths
        + ["-layers", "Optimize",
           "-dither", "None",
           "-colors", "160",
           out],
        check=True,
    )
    size_kb = os.path.getsize(out) / 1024
    print(f"Saved {out}  ({size_kb:.0f} KB)")

    # clean up temp frames
    for f in frame_paths:
        os.remove(f)

    print(f"\nDone!  Embed in README with:")
    print(f'  <img src="docs/spin.gif" alt="Hilbertbrane 360° spin" width="500">')


if __name__ == "__main__":
    main()
