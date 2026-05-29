import numpy as np
import pyvista as pv
from itertools import product

ORDER = 3
N = 2**ORDER

def hilbert_3d_index(x, y, z, n):
    h = 0
    for i in range(n):
        xb = (x >> i) & 1; yb = (y >> i) & 1; zb = (z >> i) & 1
        prefix = (xb<<2)|(yb<<1)|zb
        prefix ^= (prefix>>1)
        h |= prefix << (3*i)
    return h

# Precompute path for Order 3
pts = []
for x,y,z in product(range(N), repeat=3):
    pts.append((hilbert_3d_index(x,y,z,ORDER), x,y,z))
pts.sort()
base_path = np.array([(x,y,z) for _,x,y,z in pts], dtype=float)
base_path /= (N-1) # map to [0,1]^3

p = pv.Plotter(window_size=(1200, 800))

# Default values
params = {
    'brain_size': 100.0,
    'radius': 2.0,
    'sulcus_depth': 0.7,
}

mesh_actor = None

def update_mesh():
    global mesh_actor
    
    # 1. Scale path
    # For a brain size of 100, the grid spacing is 100 / 7 = 14.2
    # So max radius without self intersection is ~7.1
    scaled_path = (base_path - 0.5) * params['brain_size']
    
    # 2. Spline
    centerline = pv.Spline(scaled_path, 1500)
    cl_pts = centerline.points
    
    # 3. Arclength parameter
    seg = np.linalg.norm(np.diff(cl_pts, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = s / (s[-1] + 1e-9)
    
    # 4. Pinch field
    w1, w2 = 1.0, 0.3
    k1, k2 = 9, 17
    phi1, phi2 = 0.5, 1.2
    base = w1*0.5*(1-np.cos(2*np.pi*k1*t+phi1)) + w2*0.5*(1-np.cos(2*np.pi*k2*t+phi2))
    base -= base.min(); base /= (base.max() + 1e-9)
    
    # 5. Radius profile
    radius_abs = params['radius'] * (1.0 - params['sulcus_depth'] * base)
    radius_abs = np.clip(radius_abs, params['radius']*0.1, params['radius']*1.5)
    centerline.point_data["radius_profile"] = radius_abs
    
    # 6. Tube
    try:
        tube = centerline.tube(scalars="radius_profile", n_sides=16, capping=True, vary_radius="vary_radius_by_scalar", radius_factor=1.0)
    except:
        tube = centerline.tube(radius=None, scalars="radius_profile", n_sides=16, capping=True, radius_factor=1.0)
        
    # Update plotter
    if mesh_actor is not None:
        p.remove_actor(mesh_actor)
    mesh_actor = p.add_mesh(tube, color='lightblue', smooth_shading=True)

# Callbacks
def set_size(val):
    params['brain_size'] = val
    update_mesh()

def set_radius(val):
    params['radius'] = val
    update_mesh()

def set_sulcus(val):
    params['sulcus_depth'] = val
    update_mesh()

update_mesh()

p.add_slider_widget(set_size, [20.0, 200.0], value=params['brain_size'], title="Overall Brain Size", pointa=(0.025, 0.1), pointb=(0.31, 0.1))
p.add_slider_widget(set_radius, [0.5, 15.0], value=params['radius'], title="Gyri Radius (Thickness)", pointa=(0.35, 0.1), pointb=(0.64, 0.1))
p.add_slider_widget(set_sulcus, [0.0, 0.95], value=params['sulcus_depth'], title="Sulcus Depth (Pinch)", pointa=(0.67, 0.1), pointb=(0.98, 0.1))

p.add_text("Interactive Tuner - Adjust sliders to prevent overlapping blobs!", font_size=12, position="upper_left")

p.show(title="Hilbertbrane Interactive Tuner")
