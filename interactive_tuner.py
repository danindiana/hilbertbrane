import numpy as np
import pyvista as pv
import hilbert_core as hc

# Precompute Order-3 Hilbert path once, normalised to [0,1]^3
_raw = hc.build_hilbert_path(order=3)
base_path = hc.normalize_path(_raw, order=3)

p = pv.Plotter(window_size=(1200, 800))

params = {
    'brain_size':  100.0,
    'radius':        2.0,
    'sulcus_depth':  0.7,
}

mesh_actor = None


def update_mesh():
    global mesh_actor

    # Scale path: brain_size=100 → grid spacing ≈ 14.2, safe radius ≈ 7.1
    scaled_path = (base_path - 0.5) * params['brain_size']

    centerline = pv.Spline(scaled_path, 1500)
    t = hc.arclength_t(centerline.points)

    P = hc.pinch_field(t, k1=9, k2=17, w1=1.0, w2=0.3, wobble=0.0, seed=42)

    radius_abs = params['radius'] * (1.0 - params['sulcus_depth'] * P)
    radius_abs = np.clip(radius_abs,
                         params['radius'] * 0.10,
                         params['radius'] * 1.50)

    tube = hc.make_varying_radius_tube(centerline, radius_abs,
                                       params['radius'], n_sides=16)

    if mesh_actor is not None:
        p.remove_actor(mesh_actor)
    mesh_actor = p.add_mesh(tube, color='lightblue', smooth_shading=True)


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

p.add_slider_widget(set_size,   [20.0, 200.0], value=params['brain_size'],
                    title="Overall Brain Size",
                    pointa=(0.025, 0.1), pointb=(0.31, 0.1))
p.add_slider_widget(set_radius, [0.5, 15.0],   value=params['radius'],
                    title="Gyri Radius (Thickness)",
                    pointa=(0.35, 0.1), pointb=(0.64, 0.1))
p.add_slider_widget(set_sulcus, [0.0, 0.95],   value=params['sulcus_depth'],
                    title="Sulcus Depth (Pinch)",
                    pointa=(0.67, 0.1), pointb=(0.98, 0.1))

p.add_text("Interactive Tuner — adjust sliders to prevent overlapping blobs!",
           font_size=12, position="upper_left")
p.show(title="Hilbertbrane Interactive Tuner")
