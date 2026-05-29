"""
HilbertGyri.py
Create a 3-D Hilbert curve, add a sulcal pinch field (varying radius), and export STL.
Compat: works with older PyVista/VTK that lack `vary_radius` in tube().
"""
import numpy as np
import pyvista as pv
import inspect
from itertools import product

def get_user_parameters():
    """Prompt user for all configurable parameters."""
    print("=== Hilbert Brain Surface Generator ===")
    print("Configure your 3D Hilbert curve brain surface parameters:\n")

    # Hilbert curve parameters
    while True:
        try:
            order = int(input("Hilbert curve order (2-5, default 3): ").strip() or "3")
            if 2 <= order <= 5:
                break
            print("Please enter a value between 2 and 5.")
        except ValueError:
            print("Please enter a valid integer.")

    while True:
        try:
            spline_samples = int(input("Spline resolution (1000-5000, default 2000): ").strip() or "2000")
            if 1000 <= spline_samples <= 5000:
                break
            print("Please enter a value between 1000 and 5000.")
        except ValueError:
            print("Please enter a valid integer.")

    # Geometry parameters
    while True:
        try:
            ridge_radius = float(input("Mean radius (0.5-5.0, default 2.0): ").strip() or "2.0")
            if 0.5 <= ridge_radius <= 5.0:
                break
            print("Please enter a value between 0.5 and 5.0.")
        except ValueError:
            print("Please enter a valid number.")

    while True:
        try:
            sulcus_scale = float(input("Sulcus depth (0.0-0.8, default 0.55): ").strip() or "0.55")
            if 0.0 <= sulcus_scale <= 0.8:
                break
            print("Please enter a value between 0.0 and 0.8.")
        except ValueError:
            print("Please enter a valid number.")

    # Pinch field parameters
    print("\nPinch field parameters (advanced):")
    while True:
        try:
            k1 = int(input("Primary frequency k1 (default 7): ").strip() or "7")
            break
        except ValueError:
            print("Please enter a valid integer.")

    while True:
        try:
            k2 = int(input("Secondary frequency k2 (default 13): ").strip() or "13")
            break
        except ValueError:
            print("Please enter a valid integer.")

    while True:
        try:
            w1 = float(input("Primary weight w1 (0.0-2.0, default 1.0): ").strip() or "1.0")
            if 0.0 <= w1 <= 2.0:
                break
            print("Please enter a value between 0.0 and 2.0.")
        except ValueError:
            print("Please enter a valid number.")

    while True:
        try:
            w2 = float(input("Secondary weight w2 (0.0-1.0, default 0.35): ").strip() or "0.35")
            if 0.0 <= w2 <= 1.0:
                break
            print("Please enter a value between 0.0 and 1.0.")
        except ValueError:
            print("Please enter a valid number.")

    while True:
        try:
            wobble = float(input("Wobble amount (0.0-0.5, default 0.15): ").strip() or "0.15")
            if 0.0 <= wobble <= 0.5:
                break
            print("Please enter a value between 0.0 and 0.5.")
        except ValueError:
            print("Please enter a valid number.")

    while True:
        try:
            seed = int(input("Random seed (default 42): ").strip() or "42")
            break
        except ValueError:
            print("Please enter a valid integer.")

    # Output parameters
    output_filename = input("Output filename (default 'HilbertGyri.stl'): ").strip() or "HilbertGyri.stl"
    if not output_filename.endswith('.stl'):
        output_filename += '.stl'

    while True:
        try:
            decimation = float(input("Mesh decimation (0.1-0.9, default 0.45): ").strip() or "0.45")
            if 0.1 <= decimation <= 0.9:
                break
            print("Please enter a value between 0.1 and 0.9.")
        except ValueError:
            print("Please enter a valid number.")

    while True:
        try:
            growth_factor = float(input("Growth factor (1.0-2.0, default 1.12): ").strip() or "1.12")
            if 1.0 <= growth_factor <= 2.0:
                break
            print("Please enter a value between 1.0 and 2.0.")
        except ValueError:
            print("Please enter a valid number.")

    return {
        'order': order,
        'spline_samples': spline_samples,
        'ridge_radius': ridge_radius,
        'sulcus_scale': sulcus_scale,
        'k1': k1,
        'k2': k2,
        'w1': w1,
        'w2': w2,
        'wobble': wobble,
        'seed': seed,
        'output_filename': output_filename,
        'decimation': decimation,
        'growth_factor': growth_factor
    }

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

# Get user parameters
params = get_user_parameters()

# ---------- 2) Ordered point list along the 3-D Hilbert curve ----------
ORDER = params['order']                  # 8^3 = 512 voxels
N = 2**ORDER
pts = []
for x, y, z in product(range(N), repeat=3):
    pts.append((hilbert_3d_index(x, y, z, ORDER), x, y, z))
pts.sort()
path = np.array([(x, y, z) for _, x, y, z in pts], dtype=float)

# ---------- 3) Build a smooth centerline (spline) ----------
SPLINE_SAMPLES = params['spline_samples']
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

P = pinch_field(t, params['k1'], params['k2'], params['w1'], params['w2'], params['wobble'], params['seed'])

# ---------- 6) Radius profile ----------
RidgeRadius = params['ridge_radius']          # mean radius
SulcusScale = params['sulcus_scale']         # pinch strength (0..~0.8)
# Desired absolute radius per point:
radius_abs = RidgeRadius * (1.0 - SulcusScale * P)

# Attach as scalars
centerline.point_data["radius_profile"] = radius_abs

# ---------- 7) Make a tube with varying radius (handles both old/new PyVista) ----------
def make_tube(centerline, ridge_radius):
    # Try the newer signature first (has vary_radius)
    try:
        sig = inspect.signature(pv.core.filters.PolyDataFilters.tube)
        if "vary_radius" in sig.parameters:
            return centerline.tube(
                radius=ridge_radius,
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
            rel = radius_abs / (ridge_radius + 1e-12)
            centerline.point_data["radius_profile_rel"] = rel
            return centerline.tube(
                radius=ridge_radius,          # base
                scalars="radius_profile_rel",
                n_sides=28,
                capping=True,
                radius_factor=1.0
            )

tube = make_tube(centerline, params['ridge_radius'])

# Ensure triangles for decimation
tube = tube.triangulate()

# ---------- 8) Optional differential-growth buckle ----------
mesh = tube.decimate(params['decimation'])
mesh = mesh.compute_normals(cell_normals=False, auto_orient_normals=True)
vectors = mesh.point_normals
zvals = mesh.points[:, 2]
outer = zvals > zvals.mean()
growth_outer = params['growth_factor']
mesh.points[outer] += 0.25 * vectors[outer] * (growth_outer - 1.0)

# ---------- 9) Export ----------
mesh.save(params['output_filename'])
print(f"Saved {params['output_filename']} with sulcal pinch.")
print(f"Parameters used: Order={params['order']}, Radius={params['ridge_radius']}, Sulcus={params['sulcus_scale']}")
print(f"Mesh has {mesh.n_points} points and {mesh.n_cells} cells.")
