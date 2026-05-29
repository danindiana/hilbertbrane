"""
generate_logo.py — Hilbertbrane custom logo banner

Renders the actual 3D Hilbert space-filling curve (Order 3, 512 points) in
isometric projection as glowing neon lines on a dark background, paired with
the project title. Output: docs/logo.png at 1200×500 px.

Dependencies: numpy, matplotlib  (both already in requirements.txt)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.collections import LineCollection
from itertools import product

# ── palette ──────────────────────────────────────────────────────────────────
BG      = "#0d1117"
CYAN    = "#00bfff"
PINK    = "#ff2d78"
GOLD    = "#ffe600"
TEAL    = "#00ffe7"
MUTED   = "#8b949e"
DIM     = "#30363d"

W, H = 1200, 500          # banner dimensions in pixels
DPI  = 100                # 1 pt = 1 px at this DPI


# ── 1.  3-D Hilbert path (same Gray-code algorithm as HilbertGyri.py) ───────
def _hilbert_3d_index(x, y, z, n):
    h = 0
    for i in range(n):
        xb = (x >> i) & 1
        yb = (y >> i) & 1
        zb = (z >> i) & 1
        prefix = (xb << 2) | (yb << 1) | zb
        prefix ^= prefix >> 1          # Gray code
        h |= prefix << (3 * i)
    return h

def hilbert3d_path(order=3):
    N = 2 ** order
    pts = []
    for x, y, z in product(range(N), repeat=3):
        pts.append((_hilbert_3d_index(x, y, z, order), x, y, z))
    pts.sort()
    return np.array([(x, y, z) for _, x, y, z in pts], dtype=float)


# ── 2.  Isometric projection ─────────────────────────────────────────────────
def isometric(pts):
    """Rotate 45° around Y then tilt 30° forward → orthographic (x, y)."""
    cy, sy = np.cos(np.radians(45)), np.sin(np.radians(45))
    cx, sx = np.cos(np.radians(30)), np.sin(np.radians(30))
    x1 =  cy * pts[:, 0] + sy * pts[:, 2]
    y1 =  pts[:, 1]
    z1 = -sy * pts[:, 0] + cy * pts[:, 2]
    x2 = x1
    y2 = cx * y1 - sx * z1
    return x2, y2


# ── 3.  Colour gradient helper ────────────────────────────────────────────────
def _hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def gradient_colors(n, stops):
    """
    stops = [(t, '#rrggbb'), ...]  t in [0,1]
    Returns (n, 3) float RGB array.
    """
    rgb = [_hex_rgb(c) for _, c in stops]
    ts  = [t for t, _ in stops]
    out = np.zeros((n, 3))
    t_vals = np.linspace(0.0, 1.0, n)
    for i, t in enumerate(t_vals):
        # locate bracket
        j = 0
        while j < len(ts) - 2 and ts[j + 1] < t:
            j += 1
        t0, t1 = ts[j], ts[j + 1]
        frac = (t - t0) / (t1 - t0 + 1e-12)
        frac = np.clip(frac, 0.0, 1.0)
        out[i] = [rgb[j][k] + frac * (rgb[j + 1][k] - rgb[j][k]) for k in range(3)]
    return out


# ── 4.  Neon text helper ──────────────────────────────────────────────────────
def neon_text(ax, x, y, text, fontsize, color, ha="center", va="center",
              family="monospace", glow_radius=28):
    halo = color + "25"   # 15% alpha version
    mid  = color + "50"   # 31% alpha
    for lw, fc in [(glow_radius, halo), (glow_radius // 2, mid)]:
        ax.text(x, y, text, fontsize=fontsize, fontweight="bold",
                color=fc, ha=ha, va=va, fontfamily=family,
                path_effects=[pe.withStroke(linewidth=lw, foreground=fc)])
    ax.text(x, y, text, fontsize=fontsize, fontweight="bold",
            color=color, ha=ha, va=va, fontfamily=family,
            path_effects=[pe.withStroke(linewidth=3, foreground=color + "60")])


# ── 5.  Build everything ─────────────────────────────────────────────────────
def make_logo():
    # --- generate + project the Hilbert path ---
    path3d = hilbert3d_path(order=3)          # (512, 3)
    px, py = isometric(path3d)                # (512,), (512,)

    # --- scale into right 63% of canvas with padding ---
    pad    = 38
    left_x = W * 0.37 + pad
    right_x = W - pad
    cx_panel = (left_x + right_x) / 2
    cy_panel = H / 2

    rng_x = px.max() - px.min()
    rng_y = py.max() - py.min()
    avail_w = (right_x - left_x) * 0.92
    avail_h = (H - 2 * pad) * 0.90
    scale = min(avail_w / rng_x, avail_h / rng_y)

    px_s = (px - (px.min() + px.max()) / 2) * scale + cx_panel
    py_s = (py - (py.min() + py.max()) / 2) * scale + cy_panel

    # --- colour gradient along path ---
    stops = [(0.00, CYAN), (0.50, PINK), (1.00, GOLD)]
    n_seg = len(px_s) - 1
    seg_colors = gradient_colors(n_seg, stops)   # (n_seg, 3)

    # --- build LineCollection segments ---
    pts2d = np.column_stack([px_s, py_s]).reshape(-1, 1, 2)
    segs  = np.concatenate([pts2d[:-1], pts2d[1:]], axis=1)

    # ── figure ────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    # ── soft radial bloom behind the curve ───────────────────────────────
    theta = np.linspace(0, 2 * np.pi, 300)
    bloom_layers = [(300, 0.012, CYAN), (200, 0.018, PINK),
                    (130, 0.025, GOLD), (70,  0.03, CYAN)]
    for r, alpha, col in bloom_layers:
        bx = cx_panel + r * np.cos(theta)
        by = cy_panel + r * np.sin(theta)
        ax.fill(bx, by, color=col, alpha=alpha, zorder=0)

    # ── neon glow layers (wide → narrow) ─────────────────────────────────
    glow = [(28, 0.025), (16, 0.06), (7, 0.14), (2.8, 0.50), (0.8, 1.00)]
    for lw, alpha in glow:
        rgba = np.column_stack([seg_colors, np.full(n_seg, alpha)])
        lc = LineCollection(segs, colors=rgba, linewidths=lw,
                            capstyle="round", joinstyle="round", zorder=1)
        ax.add_collection(lc)

    # ── bright node dots at key bend points (every 64th point) ──────────
    step = 32
    dot_x = px_s[::step]
    dot_y = py_s[::step]
    dot_t = np.linspace(0, 1, len(dot_x))
    dot_c = gradient_colors(len(dot_x), stops)
    for dx, dy, dc in zip(dot_x, dot_y, dot_c):
        ax.plot(dx, dy, "o", color=dc, markersize=4.5, zorder=3,
                markeredgewidth=0)
        ax.plot(dx, dy, "o", color=list(dc) + [0.12], markersize=11, zorder=2,
                markeredgewidth=0)

    # ── thin vertical separator ───────────────────────────────────────────
    sep_x = W * 0.37
    ax.plot([sep_x, sep_x], [40, H - 40], color=DIM, lw=0.8, alpha=0.6, zorder=1)

    # ── left-panel title text ─────────────────────────────────────────────
    tx = sep_x / 2          # horizontal center of left panel

    neon_text(ax, tx, 318, "HILBERT",  fontsize=68, color=CYAN,
              glow_radius=30)
    neon_text(ax, tx, 228, "BRANE",    fontsize=68, color=PINK,
              glow_radius=30)

    # decorative rule
    rule_y = 186
    rule_x0, rule_x1 = tx - 148, tx + 148
    ax.plot([rule_x0, rule_x1], [rule_y, rule_y], color=TEAL,
            lw=0.9, alpha=0.55)

    # subtitles
    ax.text(tx, 161, "generative cortical mesh architecture",
            fontsize=11.5, color=TEAL, ha="center", va="center",
            fontfamily="monospace", alpha=0.9)
    ax.text(tx, 136, "3D Hilbert curves  →  watertight STL",
            fontsize=10.5, color=MUTED, ha="center", va="center",
            fontfamily="monospace")
    ax.text(tx, 100, "open source  ·  MIT license",
            fontsize=9, color=DIM, ha="center", va="center",
            fontfamily="monospace", alpha=0.8)

    # tiny corner accent lines
    for ex, ey, ddx, ddy in [
        (8, H - 8,  1,  -1),
        (8, 8,      1,   1),
    ]:
        ax.plot([ex, ex + 22 * ddx], [ey, ey],         color=TEAL, lw=1.2, alpha=0.4)
        ax.plot([ex, ex],            [ey, ey + 22 * ddy], color=TEAL, lw=1.2, alpha=0.4)

    # ── save ─────────────────────────────────────────────────────────────
    out = "docs/logo.png"
    fig.savefig(out, dpi=DPI, facecolor=BG, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out}  ({W}×{H} px)")


if __name__ == "__main__":
    make_logo()
