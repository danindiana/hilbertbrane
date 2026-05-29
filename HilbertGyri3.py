"""
HilbertBrain.py
A more biological-looking Hilbert-curve brain.
Author: you
"""
import numpy as np
import pyvista as pv
import inspect, math, noise   # pip install noise
from itertools import product

# ---------------------------------------------------------
# 1) Parameters you can play with
# ---------------------------------------------------------
ORDER          = 4                 # 8^4 = 4096 voxels
SPLINE_SAMPLES = 8000              # smoother centreline
RidgeRadius    = 1.5               # mm (cortical thickness)
SulcusScale    = 0.75              # how deep are sulci
Ellipsoid      = np.array([2.0, 1.3, 1.0])  # A-P, L-R, S-I
NOISE_OCTAVES  = 3
NOISE_AMP      = 0.45              # how wiggly the folding
SEED           = 42
np.random.seed(SEED)

# ---------------------------------------------------------
# 2) Classic 3-D Hilbert indexer
# ---------------------------------------------------------
def hilbert_3d_index(x, y, z, n):
    h = 0
    for i in range(n):
        xb = (x >> i) & 1; yb = (y >> i) & 1; zb = (z >> i) & 1
        prefix = (xb<<2)|(yb<<1)|zb
        prefix ^= (prefix>>1)
        h |= prefix << (3*i)
    return h

# ---------------------------------------------------------
# 3) Build raw Hilbert path in unit cube
# ---------------------------------------------------------
N = 2**ORDER
pts = []
for x,y,z in product(range(N), repeat=3):
    pts.append((hilbert_3d_index(x,y,z,ORDER), x,y,z))
pts.sort()
path = np.array([(x,y,z) for _,x,y,z in pts], dtype=float)
path /= (N-1)                       # map to [0,1]^3

# ---------------------------------------------------------
# 4) Map cube → ellipsoid (brain shape)
# ---------------------------------------------------------
path = (path - 0.5) * Ellipsoid     # centre at origin
path[:,2] += 0.15                   # drop occipital slightly

# ---------------------------------------------------------
# 5) Centreline spline
# ---------------------------------------------------------
centerline = pv.Spline(path, SPLINE_SAMPLES)
cl_pts = centerline.points.copy()

# ---------------------------------------------------------
# 6) Add low-freq noise to centreline → random folding
# ---------------------------------------------------------
t = np.linspace(0,1,len(cl_pts))
for i in range(3):
    for oct in range(NOISE_OCTAVES):
        freq = 4*(oct+1)
        offset = (NOISE_AMP/(oct+1)) * \
                 np.array([noise.pnoise1(tt*freq + i*57.3, octaves=2) for tt in t])
        cl_pts[:,i] += offset
centerline.points = cl_pts

# ---------------------------------------------------------
# 7) Arclength parameter
# ---------------------------------------------------------
seg = np.linalg.norm(np.diff(cl_pts, axis=0), axis=1)
s   = np.concatenate([[0], np.cumsum(seg)])
t   = s / s[-1]

# ---------------------------------------------------------
# 8) Pinch field + ventricle thinning
# ---------------------------------------------------------
def pinch_field(t, k1=9, k2=17, w1=1.0, w2=0.3, seed=42):
    rng = np.random.default_rng(seed)
    phi1,phi2 = rng.uniform(0,2*np.pi,2)
    base = w1*0.5*(1-np.cos(2*np.pi*k1*t+phi1)) + \
           w2*0.5*(1-np.cos(2*np.pi*k2*t+phi2))
    base -= base.min(); base /= base.max()
    return base

P = pinch_field(t)

# Ventricle mask: bottom 30 % of brain is thinner
zrel = (cl_pts[:,2] - cl_pts[:,2].min()) / (cl_pts[:,2].max()-cl_pts[:,2].min())
ventricle_mask = np.clip(1.2 - 1.5*zrel, 0.3, 1.0)

radius_abs = RidgeRadius * (1.0 - SulcusScale*P*ventricle_mask)
radius_abs = np.clip(radius_abs, RidgeRadius*0.25, RidgeRadius*1.15)

centerline.point_data["radius_profile"] = radius_abs

# ---------------------------------------------------------
# 9) Tube with varying radius (works old & new PyVista)
# ---------------------------------------------------------
def make_tube(cl):
    try:
        sig = inspect.signature(pv.core.filters.PolyDataFilters.tube)
        if "vary_radius" in sig.parameters:
            return cl.tube(radius=RidgeRadius,
                           scalars="radius_profile",
                           n_sides=32,
                           capping=True,
                           vary_radius="vary_radius_by_scalar",
                           radius_factor=1.0)
    except Exception:
        pass
    # legacy
    return cl.tube(radius=None,
                   scalars="radius_profile",
                   n_sides=32,
                   capping=True,
                   radius_factor=1.0)

tube = make_tube(centerline).triangulate()

# ---------------------------------------------------------
# 10) Grow & buckle – Taubin smooth + normal inflation
# ---------------------------------------------------------
def grow_buckle(mesh, outer_factor=1.25, n_iter=2):
    for _ in range(n_iter):
        mesh = mesh.smooth(n_iter=30, relaxation_factor=0.5,
                           feature_angle=120, edge_angle=90,
                           boundary_smoothing=False)
        normals = mesh.point_normals
        zrel = (mesh.points[:,2] - mesh.points[:,2].min()) / \
               (mesh.points[:,2].max()-mesh.points[:,2].min())
        mask = zrel > 0.35          # grow upper 2/3
        disp = 0.4*(outer_factor-1.0)*normals
        mesh.points[mask] += disp[mask]
    return mesh

tube = grow_buckle(tube)

# ---------------------------------------------------------
# 11) Export
# ---------------------------------------------------------
tube.save("HilbertBrain.stl")
print("Saved HilbertBrain.stl – happy printing!")