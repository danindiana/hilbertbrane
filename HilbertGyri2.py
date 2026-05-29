#!/usr/bin/env python3
"""
HilbertGyri.py
Generate a 3-D Hilbert centerline, apply a sulcal "pinch" radius field,
build a smooth organic tube, and export a watertight STL.

- Compatible with older PyVista/VTK (no 'vary_radius' kw in tube()).
- Includes smoothing + slight Z anisotropy for cortical-sheet vibes.
- Tunable presets at the top; defaults aim for "brainier" look.

Dependencies:
  pip install pyvista numpy
"""

import numpy as np
import pyvista as pv
import inspect
from itertools import product

# ==============================
# Quick knobs (good default set)
# ==============================
# Complexity / smoothness
ORDER = 4                  # 3=fast, 4=more complex "folds"
SPLINE_SAMPLES = 3500      # centerline sampling (higher = smoother)

# Tube geometry
RidgeRadius = 2.6          # overall thickness of gyri
NSIDES = 64                # polygon sides around the tube (higher = rounder)

# Pinch field (sulci/gyri modulation)
SulcusScale = 0.58         # 0..~0.8 (higher = deeper sulci)
K1, K2 = 4, 15             # harmonics: lower=broader lobes, higher=finer corrugations
W1, W2 = 1.00, 0.35        # harmonic weights
WOBBLE = 0.20              # low-freq irregularity
SEED = 42                  # change for different patterns

# Post-ops (organic finish)
DECIMATE_REDUCTION = 0.30  # keep more triangles (0.30–0.40 works well)
SMOOTH_ITERS = 90
SMOOTH_RELAX = 0.012
Z_FLATTEN = 0.50           # 1 keeps Z, <1 flattens toward a cortical sheet

# Optional tiny outward "growth" push on the outer side (keeps sulci narrow)
OUTER_GROWTH = 1.08        # multiplier idea; keep close to 1
GROWTH_STRENGTH = 0.18     # displacement scaling

# Preview window?
PREVIEW = False            # set True to see it in an interactive window

# Output filename
OUTFILE = "HilbertGyri.stl"


# ==============================
# Hilbert indexer (compact)
# ==============================
def hilbert_3d_index(x: int, y: int, z: int, n: int) -> int:
    """Return Hilbert index for 0<=x,y,z<2**n (compact bit-gray scheme)."""
    h = 0
    for i in range(n):
        xb = (x >> i) & 1
        yb = (y >> i) & 1
        zb = (z >> i) & 1
        prefix = (xb << 2) | (yb << 1) | zb
        prefix ^= (prefix >> 1)  # Gray code
        h |= prefix << (3 * i)
    return h


# ==============================
# Build ordered Hilbert path
# ==============================
def build_hilbert_path(order: int) -> np.ndarray:
    N = 2 ** order
    pts = []
    for x, y, z in product(range(N), repeat=3):
        pts.append((hilbert_3d_index(x, y, z, order), x, y, z))
    pts.sort()
    path = np.array([(x, y, z) for _, x, y, z in pts], dtype=float)
    return path


# ==============================
# Pinch field (0..1 over arclength)
# ==============================
def pinch_field(t: np.ndarray,
                k1=K1, k2=K2, w1=W1, w2=W2,
                wobble=WOBBLE, seed=SEED) -> np.ndarray:
    rng = np.random.default_rng(seed)
    phi1 = rng.uniform(0, 2 * np.pi)
    phi2 = rng.uniform(0, 2 * np.pi)

    base = (
        w1 * (0.5 * (1 - np.cos(2 * np.pi * k1 * t + phi1))) +
        w2 * (0.5 * (1 - np.cos(2 * np.pi * k2 * t + phi2)))
    )
    # very low-frequency wobble to break regularity
    wob = wobble * (0.5 * (1 - np.cos(2 * np.pi * 1.2 * t + 0.7)))
    P = base + wob
    P -= P.min()
    P /= (P.max() + 1e-12)
    return P


# ==============================
# Tube maker with compatibility
# ==============================
def make_varying_radius_tube(centerline: pv.PolyData,
                             radius_profile_abs: np.ndarray,
                             base_radius: float,
                             n_sides: int,
                             capping: bool = True) -> pv.PolyData:
    """
    Try modern signature first (vary_radius), fall back to legacy behaviors:
    - absolute scalars with radius=None
    - relative scalars with radius=base_radius
    """
    centerline = centerline.copy()
    centerline.point_data["radius_profile"] = radius_profile_abs

    try:
        sig = inspect.signature(pv.core.filters.PolyDataFilters.tube)
        if "vary_radius" in sig.parameters:
            return centerline.tube(
                radius=base_radius,
                scalars="radius_profile",
                n_sides=n_sides,
                capping=capping,
                vary_radius="vary_radius_by_scalar",
                radius_factor=1.0,
            )
        else:
            raise TypeError
    except Exception:
        # Attempt absolute-scalar path
        try:
            return centerline.tube(
                radius=None,  # let scalars be absolute radii
                scalars="radius_profile",
                n_sides=n_sides,
                capping=capping,
                radius_factor=1.0,
            )
        except Exception:
            # Fallback to relative-scalar path
            rel = radius_profile_abs / (base_radius + 1e-12)
            centerline.point_data["radius_profile_rel"] = rel
            return centerline.tube(
                radius=base_radius,
                scalars="radius_profile_rel",
                n_sides=n_sides,
                capping=capping,
                radius_factor=1.0,
            )


# ==============================
# Main
# ==============================
def main():
    # 1) Hilbert path → smooth centerline
    path = build_hilbert_path(ORDER)
    centerline = pv.Spline(path, SPLINE_SAMPLES)
    cl_pts = centerline.points

    # 2) Normalized arclength parameter t∈[0,1]
    seg = np.linalg.norm(np.diff(cl_pts, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    t = s / s[-1]

    # 3) Build pinch → absolute radius per point
    P = pinch_field(t)
    radius_abs = RidgeRadius * (1.0 - SulcusScale * P)

    # 4) Tube with varying radius (triangulate to enable decimation)
    tube = make_varying_radius_tube(centerline, radius_abs, RidgeRadius, NSIDES, True)
    tube = tube.triangulate()

    # 5) Organic finishing: light decimate, smooth, slight Z flatten, re-normals
    mesh = tube.decimate(DECIMATE_REDUCTION)
    mesh = mesh.compute_normals(cell_normals=False, auto_orient_normals=True)

    mesh = mesh.smooth(
        n_iter=SMOOTH_ITERS,
        relaxation_factor=SMOOTH_RELAX,
        feature_smoothing=False,
        boundary_smoothing=True,
    )

    if Z_FLATTEN != 1.0:
        mesh.scale([1.0, 1.0, Z_FLATTEN], inplace=True)

    mesh = mesh.compute_normals(cell_normals=False, auto_orient_normals=True)

    # 6) Tiny outward growth bias on "outer" side to keep sulci tighter
    if OUTER_GROWTH != 1.0 and GROWTH_STRENGTH > 0:
        zvals = mesh.points[:, 2]
        outer = zvals > zvals.mean()
        mesh.points[outer] += (
            GROWTH_STRENGTH * mesh.point_normals[outer] * (OUTER_GROWTH - 1.0)
        )
        mesh = mesh.compute_normals(cell_normals=False, auto_orient_normals=True)

    # 7) Preview (optional)
    if PREVIEW:
        pl = pv.Plotter(window_size=(1024, 768))
        pl.add_mesh(mesh, smooth_shading=True, specular=10.0, metallic=0.1)
        pl.add_axes()
        pl.show()

    # 8) Export STL
    mesh.save(OUTFILE)
    print(f"Saved {OUTFILE}  — ready for slicer / CAD / casting.")


if __name__ == "__main__":
    main()