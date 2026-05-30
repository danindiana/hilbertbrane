"""
generate_animations.py — High-res & stylistic GIF variants of the neon Hilbert spin

Produces four GIFs into docs/animations/:
  spin_hd.gif      800×800, 72 frames,  5°/frame, 4cs  — high-res showcase
  spin_zoomout.gif 700×700, 108 frames, 3.33°/frame, 4cs — zoom-out reveal
  spin_slow.gif    600×600, 120 frames, 3°/frame,  5cs  — smooth slow spin
  spin_glacial.gif 600×600, 90 frames,  4°/frame,  9cs  — very slow, contemplative

Run from repo root:  python generate_animations.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from itertools import product
import subprocess, os, sys

# ── palette ──────────────────────────────────────────────────────────────────
BG   = "#0d1117"
CYAN = "#00bfff"
PINK = "#ff2d78"
GOLD = "#ffe600"
TEAL = "#00ffe7"

OUT_DIR  = "docs/animations"
TMP_PFX  = "/tmp/hbanim"
ORDER    = 3
TILT_DEG = 28


# ── shared helpers ────────────────────────────────────────────────────────────
def _h3d(x, y, z, n):
    h = 0
    for i in range(n):
        xb = (x >> i) & 1; yb = (y >> i) & 1; zb = (z >> i) & 1
        p  = (xb << 2) | (yb << 1) | zb
        p ^= p >> 1
        h |= p << (3 * i)
    return h

def hilbert3d(order=3):
    N = 2 ** order
    pts = []
    for x, y, z in product(range(N), repeat=3):
        pts.append((_h3d(x, y, z, order), x, y, z))
    pts.sort()
    return np.array([(x, y, z) for _, x, y, z in pts], dtype=float)

def _hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def grad_colors(n, stops):
    rgb = [_hex_rgb(c) for _, c in stops]
    ts  = [t           for t, _ in stops]
    out = np.zeros((n, 3))
    for i, t in enumerate(np.linspace(0, 1, n)):
        j = 0
        while j < len(ts) - 2 and ts[j+1] < t:
            j += 1
        f = np.clip((t - ts[j]) / (ts[j+1] - ts[j] + 1e-12), 0, 1)
        out[i] = [rgb[j][k] + f*(rgb[j+1][k]-rgb[j][k]) for k in range(3)]
    return out

def rotate_y(pts, deg):
    r = np.radians(deg); cy, sy = np.cos(r), np.sin(r)
    x, y, z = pts[:,0], pts[:,1], pts[:,2]
    return np.column_stack([cy*x+sy*z, y, -sy*x+cy*z])

def project(pts, tilt=TILT_DEG):
    r = np.radians(tilt); cx, sx = np.cos(r), np.sin(r)
    x, y, z = pts[:,0], pts[:,1], pts[:,2]
    return x, cx*y - sx*z

def safe_scale(path3d, size, margin, n_frames):
    """Compute a scale that keeps the curve in-frame for every rotation angle."""
    max_ext = 0.0
    for a in range(0, 360, max(1, 360 // n_frames)):
        rot = rotate_y(path3d, a)
        px, py = project(rot)
        ext = max(px.max()-px.min(), py.max()-py.min())
        if ext > max_ext:
            max_ext = ext
    return (size - 2*margin) / max_ext


# ── smoothstep zoom helper ────────────────────────────────────────────────────
def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2*x)

def zoomout_scale_fn(frame_i, base_scale, n_zoom=36, zoom_start=2.5):
    """Scale starts at zoom_start×base and eases to 1× over n_zoom frames."""
    if frame_i >= n_zoom:
        return base_scale
    frac = smoothstep(frame_i / (n_zoom - 1))
    factor = zoom_start + frac * (1.0 - zoom_start)
    return base_scale * factor


# ── single-frame renderer ─────────────────────────────────────────────────────
def render_frame(path3d, angle_deg, colors_rgb, draw_scale,
                 size=600, dpi=100):
    fig = plt.figure(figsize=(size/dpi, size/dpi), dpi=dpi)
    fig.patch.set_facecolor(BG)
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG); ax.set_xlim(0, size); ax.set_ylim(0, size); ax.axis("off")

    cx, cy = size / 2.0, size / 2.0

    # rotate, project, scale
    rot  = rotate_y(path3d, angle_deg)
    px, py = project(rot)
    px_s = (px - px.mean()) * draw_scale + cx
    py_s = (py - py.mean()) * draw_scale + cy

    # segments
    pts2d = np.column_stack([px_s, py_s]).reshape(-1, 1, 2)
    segs  = np.concatenate([pts2d[:-1], pts2d[1:]], axis=1)
    n_seg = len(segs)

    # scale glow radii with canvas size
    sf = size / 600.0

    # soft radial bloom
    theta = np.linspace(0, 2*np.pi, 300)
    for r, a, col in [
        (int(230*sf), 0.010, CYAN),
        (int(155*sf), 0.016, PINK),
        (int(100*sf), 0.022, GOLD),
        (int(55*sf),  0.028, CYAN),
    ]:
        ax.fill(cx + r*np.cos(theta), cy + r*np.sin(theta),
                color=col, alpha=a, zorder=0)

    # neon glow layers
    for lw, alpha in [
        (30*sf, 0.022), (17*sf, 0.055), (7*sf, 0.140),
        (2.8*sf, 0.500), (0.8*sf, 1.000),
    ]:
        rgba = np.column_stack([colors_rgb, np.full(n_seg, alpha)])
        lc   = LineCollection(segs, colors=rgba, linewidths=lw,
                              capstyle="round", joinstyle="round", zorder=1)
        ax.add_collection(lc)

    # vertex dots
    step  = 32
    dcols = grad_colors(len(px_s[::step]), [(0,CYAN),(0.5,PINK),(1,GOLD)])
    for dx, dy, dc in zip(px_s[::step], py_s[::step], dcols):
        ax.plot(dx, dy, "o", color=list(dc)+[0.13],
                markersize=10*sf, zorder=2, markeredgewidth=0)
        ax.plot(dx, dy, "o", color=dc,
                markersize=4.5*sf, zorder=3, markeredgewidth=0)

    # watermark
    ax.text(size/2, 22*sf, "HILBERTBRANE",
            fontsize=9*sf, color=TEAL, ha="center", va="center",
            fontfamily="monospace", alpha=0.22)

    return fig


# ── variant renderer ──────────────────────────────────────────────────────────
def render_variant(name, path3d, colors_rgb,
                   size=600, n_frames=72, delay_cs=4, n_colors=128,
                   margin=55, scale_fn=None):
    """Render one GIF variant to docs/animations/{name}.gif"""
    print(f"\n{'='*60}")
    print(f"  {name}  |  {size}px  |  {n_frames} frames  |  {delay_cs}cs/frame")

    base_scale = safe_scale(path3d, size, margin, n_frames)
    print(f"  base_scale={base_scale:.3f}")

    frame_paths = []
    for i in range(n_frames):
        angle = 360.0 * i / n_frames

        # apply optional per-frame scale override
        if scale_fn is not None:
            draw_scale = scale_fn(i, base_scale)
        else:
            draw_scale = base_scale

        fig   = render_frame(path3d, angle, colors_rgb, draw_scale, size=size)
        fpath = f"{TMP_PFX}_{name}_{i:04d}.png"
        fig.savefig(fpath, dpi=100, facecolor=BG, bbox_inches=None)
        plt.close(fig)
        frame_paths.append(fpath)

        if (i+1) % max(1, n_frames//6) == 0 or i == 0:
            pct = (i+1)/n_frames*100
            print(f"  [{pct:5.1f}%]  frame {i+1}/{n_frames}  (angle={angle:.1f}°)")

    out = f"{OUT_DIR}/{name}.gif"
    print(f"  Assembling → {out} …")
    subprocess.run(
        ["convert", "-delay", str(delay_cs), "-loop", "0"]
        + frame_paths
        + ["-layers", "Optimize", "-dither", "None", "-colors", str(n_colors), out],
        check=True,
    )
    for f in frame_paths:
        os.remove(f)

    kb = os.path.getsize(out) / 1024
    print(f"  Done: {out}  ({kb:.0f} KB)")
    return out


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Building Hilbert path …")
    path3d  = hilbert3d(ORDER)
    path3d -= path3d.mean(axis=0)

    stops      = [(0.0, CYAN), (0.5, PINK), (1.0, GOLD)]
    colors_rgb = grad_colors(len(path3d) - 1, stops)

    # ── variant 1: high-res ────────────────────────────────────────────────
    render_variant("spin_hd", path3d, colors_rgb,
                   size=800, n_frames=72, delay_cs=4, n_colors=160)

    # ── variant 2: spin-out (zoom-out reveal) ─────────────────────────────
    render_variant("spin_zoomout", path3d, colors_rgb,
                   size=700, n_frames=108, delay_cs=4, n_colors=160,
                   scale_fn=lambda i, bs: zoomout_scale_fn(i, bs, n_zoom=36, zoom_start=2.5))

    # ── variant 3: slow smooth rotation ───────────────────────────────────
    render_variant("spin_slow", path3d, colors_rgb,
                   size=600, n_frames=120, delay_cs=5, n_colors=128)

    # ── variant 4: glacial (very slow) ────────────────────────────────────
    render_variant("spin_glacial", path3d, colors_rgb,
                   size=600, n_frames=90, delay_cs=9, n_colors=128)

    print("\n" + "="*60)
    print("All variants complete:")
    for name in ("spin_hd", "spin_zoomout", "spin_slow", "spin_glacial"):
        path = f"{OUT_DIR}/{name}.gif"
        kb   = os.path.getsize(path) / 1024
        print(f"  {path:<42}  {kb:>6.0f} KB")


if __name__ == "__main__":
    main()
