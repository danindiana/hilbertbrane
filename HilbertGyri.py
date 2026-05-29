"""
HilbertGyri.py
Create a 3-D Hilbert curve, add a sulcal pinch field (varying radius), and export STL.
Compat: works with older PyVista/VTK that lack `vary_radius` in tube().
"""
import numpy as np
import pyvista as pv
import inspect
from itertools import product

# ---------- 1) 3-D Hilbert indexer (compact) ----------
def hilbert_3d_index(x, y, z, n):
    h = 0
    for i in range(n):
        xb = (x >> i) & 1
        yb = (y >> i) & 1
        zb = (z >> i) & 1
        prefix = (xb << 2) | (yb << 1) | zb
        prefix ^= (prefix >> 1)  # Gray
        h |= prefix << (3 * i)
    return h

# ---------- 2) Ordered point list along the 3-D Hilbert curve ----------
ORDER = 3                  # 8^3 = 512 voxels
N = 2**ORDER
pts = []
for x, y, z in product(range(N), repeat=3):
    pts.append((hilbert_3d_index(x, y, z, ORDER), x, y, z))
pts.sort()
path = np.array([(x, y, z) for _, x, y, z in pts], dtype=float)

# ---------- 3) Build a smooth centerline (spline) ----------
SPLINE_SAMPLES = 2000
centerline = pv.Spline(path, SPLINE_SAMPLES)
cl_pts = centerline.points

# ---------- 4) Normalized arclength parameter t ∈ [0,1] ----------
seg = np.linalg.norm(np.diff(cl_pts, axis=0), axis=1)
s = np.concatenate([[0.0], np.cumsum(seg)])
t = s / s[-1]

# ---------- 5) Pinch field P(t) in [0,1] ----------
def pinch_field(t, k1=7, k2=13, w1=1.0, w2=0.35, wobble=0.15, seed=42):
    rng = np.random.default_rng(seed)
    phi1 = rng.uniform(0, 2*np.pi); phi2 = rng.uniform(0, 2*np.pi)
    base = (
        w1 * (0.5 * (1 - np.cos(2*np.pi*k1*t + phi1))) +
        w2 * (0.5 * (1 - np.cos(2*np.pi*k2*t + phi2)))
    )
    wob = wobble * (0.5 * (1 - np.cos(2*np.pi*1.2*t + 0.7)))
    P = base + wob
    P -= P.min(); P /= (P.max() + 1e-12)
    return P

P = pinch_field(t)

# ---------- 6) Radius profile ----------
RidgeRadius = 2.0          # mean radius
SulcusScale = 0.55         # pinch strength (0..~0.8)
# Desired absolute radius per point:
radius_abs = RidgeRadius * (1.0 - SulcusScale * P)

# Attach as scalars
centerline.point_data["radius_profile"] = radius_abs

# ---------- 7) Make a tube with varying radius (handles both old/new PyVista) ----------
def make_tube(centerline):
    # Try the newer signature first (has vary_radius)
    try:
        sig = inspect.signature(pv.core.filters.PolyDataFilters.tube)
        if "vary_radius" in sig.parameters:
            return centerline.tube(
                radius=RidgeRadius,
                scalars="radius_profile",
                n_sides=28,
                capping=True,
                vary_radius="vary_radius_by_scalar",
                radius_factor=1.0,
            )
        else:
            raise TypeError  # fall through to legacy path
    except Exception:
        # Legacy behavior: when scalars are provided, VTK varies radius by scalar * radius_factor.
        # Many builds interpret scalar as ABSOLUTE if radius is None and radius_factor=1.
        try:
            return centerline.tube(
                radius=None,                 # let scalars drive absolute radius
                scalars="radius_profile",
                n_sides=28,
                capping=True,
                radius_factor=1.0
            )
        except Exception:
            # If your VTK interprets scalars RELATIVELY, normalize and use base radius
            rel = radius_abs / (RidgeRadius + 1e-12)
            centerline.point_data["radius_profile_rel"] = rel
            return centerline.tube(
                radius=RidgeRadius,          # base
                scalars="radius_profile_rel",
                n_sides=28,
                capping=True,
                radius_factor=1.0
            )

tube = make_tube(centerline)

# Ensure triangles for decimation
tube = tube.triangulate()

# ---------- 8) Optional differential-growth buckle ----------
mesh = tube.decimate(0.45)
mesh = mesh.compute_normals(cell_normals=False, auto_orient_normals=True)
vectors = mesh.point_normals
zvals = mesh.points[:, 2]
outer = zvals > zvals.mean()
growth_outer = 1.12
mesh.points[outer] += 0.25 * vectors[outer] * (growth_outer - 1.0)

# ---------- 9) Export ----------
mesh.save("HilbertGyri.stl")
print("Saved HilbertGyri.stl with sulcal pinch.")
