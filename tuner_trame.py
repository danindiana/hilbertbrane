#!/usr/bin/env python3
"""
tuner_trame.py
==============
Browser-served replacement for interactive_tuner.py.

The old tuner called ``pv.Plotter().show()`` and needed a local OpenGL display,
so it couldn't run over SSH or be shared. This serves the *same* PyVista
rendering through trame: the scene renders off-screen on the server and streams
to a browser tab. Run it on a headless box, forward the port, tune from your
laptop. It also drops the duplicated (and incorrect) Hilbert code in favour of
hilbert_core, so the curve here is the real locality-preserving one.

    python tuner_trame.py                 # serve on http://localhost:8080
    python tuner_trame.py --port 9000 --no-browser
    # over SSH:  ssh -L 8080:localhost:8080 user@host  then open localhost:8080

Live view shows the bare varying-radius tube for responsiveness; the Export
button runs through exporters.write so you get the same files as hilbert_gen.
"""

from __future__ import annotations

import argparse
from functools import lru_cache

import numpy as np
import pyvista as pv

import exporters
import hilbert_core as hc

pv.OFF_SCREEN = True

DEFAULTS = dict(
    order=3, spline=1500, brain_size=100.0, radius=2.0, sulcus=0.7,
    k1=9, k2=17, wobble=0.15, seed=42, n_sides=16,
)

# slider metadata: (label, min, max, step, integer?)
CONTROLS = {
    "order":      ("Hilbert order", 2, 5, 1, True),
    "spline":     ("Spline samples", 500, 6000, 100, True),
    "brain_size": ("Overall size", 20.0, 200.0, 1.0, False),
    "radius":     ("Gyri radius", 0.5, 15.0, 0.1, False),
    "sulcus":     ("Sulcus depth", 0.0, 0.95, 0.01, False),
    "k1":         ("Frequency k1", 1, 24, 1, True),
    "k2":         ("Frequency k2", 1, 24, 1, True),
    "wobble":     ("Wobble", 0.0, 0.5, 0.01, False),
    "n_sides":    ("Tube facets", 6, 64, 1, True),
    "seed":       ("Seed", 0, 999, 1, True),
}


# ---------------------------------------------------------------------------
# Pure geometry (testable without trame): build the live tube from params.
# ---------------------------------------------------------------------------
@lru_cache(maxsize=8)
def _cached_unit_path(order: int) -> np.ndarray:
    return hc.normalize_path(hc.build_hilbert_path(order), order)


def build_mesh(order, spline, brain_size, radius, sulcus,
               k1, k2, wobble, seed, n_sides):
    """Return (mesh, centerline_points, radius_profile) for the given params."""
    scaled = (_cached_unit_path(int(order)) - 0.5) * float(brain_size)
    cl = pv.Spline(scaled, int(spline))
    t = hc.arclength_t(cl.points)
    P = hc.pinch_field(t, int(k1), int(k2), wobble=float(wobble), seed=int(seed))
    r = float(radius) * (1.0 - float(sulcus) * P)
    r = np.clip(r, float(radius) * 0.1, float(radius) * 1.5)
    mesh = hc.make_varying_radius_tube(cl, r, float(radius), int(n_sides))
    return mesh, np.asarray(cl.points), r


# ---------------------------------------------------------------------------
# trame application
# ---------------------------------------------------------------------------
def build_app(server=None):
    """Construct the trame app. Returns a dict of handles (also usable in tests)."""
    from trame.app import get_server
    from trame.ui.vuetify3 import SinglePageWithDrawerLayout
    from trame.widgets import vuetify3
    from pyvista.trame.ui import plotter_ui

    server = server or get_server()
    server.client_type = "vue3"
    state, ctrl = server.state, server.controller

    plotter = pv.Plotter(off_screen=True)
    plotter.background_color = "white"

    state.update(DEFAULTS)
    state.export_name = "tuner_out.stl"
    state.status = "ready"

    holder = {"actor": None, "first": True}

    def rebuild():
        mesh, _, _ = build_mesh(
            state.order, state.spline, state.brain_size, state.radius,
            state.sulcus, state.k1, state.k2, state.wobble, state.seed,
            state.n_sides)
        if holder["actor"] is not None:
            plotter.remove_actor(holder["actor"])
        holder["actor"] = plotter.add_mesh(
            mesh, color="lightblue", smooth_shading=True, specular=0.3)
        if holder["first"]:
            plotter.reset_camera()
            holder["first"] = False
        return mesh

    @state.change(*CONTROLS.keys())
    def _on_change(**_):
        rebuild()
        ctrl.view_update()

    def export():
        mesh, clp, r = build_mesh(
            state.order, state.spline, state.brain_size, state.radius,
            state.sulcus, state.k1, state.k2, state.wobble, state.seed,
            state.n_sides)
        try:
            path, fmt = exporters.resolve(state.export_name, None)
            out = exporters.write(mesh, clp, r, path, fmt,
                                  meta={"source": "tuner_trame"})
            edges = hc.open_edge_count(mesh)
            state.status = f"saved {out}" + (
                f" ({edges} open edges)" if edges else " (watertight)")
        except Exception as exc:  # surface the message in the UI, don't crash
            state.status = f"export failed: {exc}"

    ctrl.export = export
    ctrl.reset = lambda: state.update(DEFAULTS)

    # initial render
    rebuild()

    with SinglePageWithDrawerLayout(server) as layout:
        layout.title.set_text("Hilbertbrane Tuner")

        with layout.drawer:
            for key, (label, lo, hi, step, _is_int) in CONTROLS.items():
                vuetify3.VSlider(
                    v_model=(key,), min=lo, max=hi, step=step,
                    label=label, thumb_label=True, hide_details=True,
                    density="compact", classes="mt-3 mx-2")
            vuetify3.VDivider(classes="my-3")
            vuetify3.VTextField(
                v_model=("export_name",), label="Export filename",
                hint="stl | ply | 3mf | glb | gltf | swc", density="compact",
                classes="mx-2")
            vuetify3.VBtn("Export", click=ctrl.export,
                          block=True, classes="mx-2 mt-2")
            vuetify3.VBtn("Reset", click=ctrl.reset,
                          block=True, variant="tonal", classes="mx-2 mt-2")
            vuetify3.VAlert(
                text=("status",), density="compact", variant="tonal",
                classes="ma-2")

        with layout.content:
            with vuetify3.VContainer(fluid=True, classes="pa-0 fill-height"):
                view = plotter_ui(plotter)
                ctrl.view_update = view.update

    return {"server": server, "state": state, "ctrl": ctrl,
            "plotter": plotter, "rebuild": rebuild, "export": export}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Browser tuner for hilbertbrane.")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--no-browser", action="store_true",
                        help="don't auto-open a browser (useful over SSH)")
    args = parser.parse_args(argv)

    app = build_app()
    app["server"].start(host=args.host, port=args.port,
                        open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
