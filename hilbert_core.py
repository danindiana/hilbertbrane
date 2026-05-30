"""
hilbert_core.py
================
Shared building blocks for the Hilbertbrane generators.

Everything that used to be copy-pasted across HilbertGyri*.py, Hilbertbrane.py
and interactive_tuner.py now lives here exactly once:

    * a *correct* (locality-preserving) 3-D Hilbert curve   -> hilbert_point / build_hilbert_path
    * cube -> [0,1]^3 normalisation and cube -> ellipsoid mapping
    * arclength parameterisation
    * the sulcal pinch field
    * the ventricle thinning mask
    * optional Perlin folding of the centreline
    * a PyVista/VTK-version-agnostic varying-radius tube builder
    * a watertightness check (+ optional pymeshfix repair)

Pure-math helpers (the curve, the fields) have NO PyVista dependency, so they
can be imported and unit-tested without a GL stack. PyVista is imported lazily
inside the functions that actually need it.
"""

from __future__ import annotations

import inspect
from typing import Optional, Sequence

import numpy as np

__all__ = [
    "hilbert_point",
    "build_hilbert_path",
    "normalize_path",
    "map_to_ellipsoid",
    "arclength_t",
    "pinch_field",
    "ventricle_mask",
    "perlin_fold",
    "make_varying_radius_tube",
    "open_edge_count",
    "is_watertight",
    "repair_mesh",
]


# ---------------------------------------------------------------------------
# 1) A correct 3-D Hilbert curve (Skilling 2004)
# ---------------------------------------------------------------------------
def hilbert_point(h: int, order: int, dim: int = 3) -> tuple[int, ...]:
    """Map a Hilbert index ``h`` to integer coordinates in ``[0, 2**order)``.

    Unlike a plain Gray-code bit-interleave, this preserves locality: indices
    that differ by 1 map to face-adjacent cells (Manhattan distance 1).
    """
    X = [0] * dim
    for b in range(order * dim):
        if (h >> b) & 1:
            X[dim - 1 - (b % dim)] |= 1 << (b // dim)

    # Gray decode (Skilling's transpose -> axes)
    t = X[dim - 1] >> 1
    for i in range(dim - 1, 0, -1):
        X[i] ^= X[i - 1]
    X[0] ^= t

    # Undo excess work
    Q = 2
    while Q != (1 << order):
        P = Q - 1
        for i in range(dim - 1, -1, -1):
            if X[i] & Q:
                X[0] ^= P
            else:
                swap = (X[0] ^ X[i]) & P
                X[0] ^= swap
                X[i] ^= swap
        Q <<= 1

    return tuple(X)


def build_hilbert_path(order: int, dim: int = 3) -> np.ndarray:
    """Return the ordered ``(2**order)**dim x dim`` array of curve vertices."""
    n_points = (1 << order) ** dim
    return np.array([hilbert_point(h, order, dim) for h in range(n_points)],
                    dtype=float)


# ---------------------------------------------------------------------------
# 2) Geometry helpers (still pure numpy)
# ---------------------------------------------------------------------------
def normalize_path(path: np.ndarray, order: int) -> np.ndarray:
    """Scale integer cube coordinates into the unit cube ``[0, 1]^dim``."""
    span = (1 << order) - 1
    return path / span if span else path.copy()


def map_to_ellipsoid(path_unit: np.ndarray,
                     ellipsoid: Sequence[float],
                     occipital_drop: float = 0.15) -> np.ndarray:
    """Centre a unit-cube path on the origin and stretch it to a brain-ish ellipsoid.

    ``ellipsoid`` is (A-P, L-R, S-I). ``occipital_drop`` nudges Z to break symmetry.
    """
    out = (path_unit - 0.5) * np.asarray(ellipsoid, dtype=float)
    if path_unit.shape[1] >= 3:
        out[:, 2] += occipital_drop
    return out


def arclength_t(points: np.ndarray) -> np.ndarray:
    """Normalised cumulative arclength ``t in [0, 1]`` for an ordered point set."""
    seg = np.linalg.norm(np.diff(points, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    return s / (s[-1] + 1e-12)


# ---------------------------------------------------------------------------
# 3) Sulcal / cortical fields
# ---------------------------------------------------------------------------
def pinch_field(t: np.ndarray,
                k1: int = 7, k2: int = 13,
                w1: float = 1.0, w2: float = 0.35,
                wobble: float = 0.15,
                seed: int = 42) -> np.ndarray:
    """Two-harmonic + low-frequency wobble pinch field, normalised to ``[0, 1]``."""
    rng = np.random.default_rng(seed)
    phi1, phi2 = rng.uniform(0, 2 * np.pi, size=2)

    base = (w1 * 0.5 * (1 - np.cos(2 * np.pi * k1 * t + phi1))
            + w2 * 0.5 * (1 - np.cos(2 * np.pi * k2 * t + phi2)))
    if wobble:
        base += wobble * 0.5 * (1 - np.cos(2 * np.pi * 1.2 * t + 0.7))

    base -= base.min()
    base /= (base.max() + 1e-12)
    return base


def ventricle_mask(cl_pts: np.ndarray,
                   floor: float = 0.3, ceil: float = 1.0) -> np.ndarray:
    """Thin the lower portion of the volume (crude ventricle proxy)."""
    z = cl_pts[:, 2]
    zrel = (z - z.min()) / (z.max() - z.min() + 1e-12)
    return np.clip(1.2 - 1.5 * zrel, floor, ceil)


def perlin_fold(cl_pts: np.ndarray,
                octaves: int = 3,
                amplitude: float = 0.45,
                seed: int = 42) -> np.ndarray:
    """Add reproducible low-frequency Perlin noise to a centreline.

    Returns a *new* array; the input is not mutated. Requires the ``noise``
    package (``pip install noise``); raises a clear error if it is missing.
    """
    try:
        import noise  # noqa: WPS433 (lazy import is intentional)
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "Perlin folding needs the 'noise' package. "
            "Install it with `pip install noise` (or drop the --noise-amp flag)."
        ) from exc

    out = cl_pts.copy()
    t = np.linspace(0.0, 1.0, len(out))
    for axis in range(3):
        # 'base' makes the permutation table depend on seed -> reproducible
        base = int(seed) + axis * 101
        for octv in range(octaves):
            freq = 4 * (octv + 1)
            offset = (amplitude / (octv + 1)) * np.array(
                [noise.pnoise1(tt * freq + axis * 57.3, octaves=2, base=base)
                 for tt in t]
            )
            out[:, axis] += offset
    return out


# ---------------------------------------------------------------------------
# 4) PyVista tube builder (VTK-version agnostic, detected once)
# ---------------------------------------------------------------------------
def _tube_supports_vary_radius() -> bool:
    """True if this PyVista build exposes the modern ``vary_radius`` kwarg."""
    import pyvista as pv  # lazy
    try:
        sig = inspect.signature(pv.core.filters.PolyDataFilters.tube)
        return "vary_radius" in sig.parameters
    except (AttributeError, ValueError, TypeError):
        return False


def make_varying_radius_tube(centerline,
                             radius_profile_abs: np.ndarray,
                             base_radius: float,
                             n_sides: int = 32,
                             capping: bool = True):
    """Extrude a centreline into a varying-radius tube across PyVista versions.

    Strategy (chosen explicitly rather than via blanket except):
      1. modern signature: pass ``vary_radius='vary_radius_by_scalar'``
      2. legacy absolute:  ``radius=None`` lets the scalar drive absolute radius
      3. legacy relative:  scalars normalised against ``base_radius``
    """
    cl = centerline.copy()
    cl.point_data["radius_profile"] = radius_profile_abs

    if _tube_supports_vary_radius():
        return cl.tube(
            radius=base_radius,
            scalars="radius_profile",
            n_sides=n_sides,
            capping=capping,
            vary_radius="vary_radius_by_scalar",
            radius_factor=1.0,
        )

    # Legacy path 1: absolute scalar radius
    try:
        return cl.tube(
            radius=None,
            scalars="radius_profile",
            n_sides=n_sides,
            capping=capping,
            radius_factor=1.0,
        )
    except (TypeError, ValueError):
        # Legacy path 2: relative scalar radius
        cl.point_data["radius_profile_rel"] = radius_profile_abs / (base_radius + 1e-12)
        return cl.tube(
            radius=base_radius,
            scalars="radius_profile_rel",
            n_sides=n_sides,
            capping=capping,
            radius_factor=1.0,
        )


# ---------------------------------------------------------------------------
# 5) Watertightness
# ---------------------------------------------------------------------------
def open_edge_count(mesh) -> int:
    """Number of boundary + non-manifold edges (0 means closed & manifold)."""
    edges = mesh.extract_feature_edges(
        boundary_edges=True,
        non_manifold_edges=True,
        feature_edges=False,
        manifold_edges=False,
    )
    return int(edges.n_cells)


def is_watertight(mesh) -> bool:
    return open_edge_count(mesh) == 0


def repair_mesh(mesh):
    """Best-effort watertight repair via pymeshfix; returns mesh unchanged if absent."""
    try:
        import pymeshfix  # lazy
    except ImportError:
        return mesh
    fixed = pymeshfix.MeshFix(mesh.triangulate())
    fixed.repair()
    return fixed.mesh
