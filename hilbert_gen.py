#!/usr/bin/env python3
"""
hilbert_gen.py
==============
One configurable generator that replaces HilbertGyri.py, HilbertGyri2.py,
HilbertGyri3.py and Hilbertbrane.py.

Pick a preset that reproduces an original script, then override any knob:

    python hilbert_gen.py --preset gyri   -o hilbert_gyri_o3.stl
    python hilbert_gen.py --preset gyri2  -o hilbert_gyri_o4.stl
    python hilbert_gen.py --preset gyri3  -o hilbert_brain.stl
    python hilbert_gen.py --preset gyri3 --sulcus 0.6 --noise-amp 0.6 -o custom.stl

With no arguments (or --interactive) on a terminal it falls back to prompts,
matching the old Hilbertbrane.py experience.

    python hilbert_gen.py --list-presets      # show what each preset does
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np

import exporters
import hilbert_core as hc
import morphoelastic
import neuro
import provenance


# ---------------------------------------------------------------------------
# Defaults + presets.  CLI flags default to None so we can resolve precedence:
#   explicit flag  >  preset value  >  BASE default
# ---------------------------------------------------------------------------
BASE = {
    "order": 3, "spline": 2000,
    "radius": 2.0, "sulcus": 0.55, "n_sides": 28,
    "k1": 7, "k2": 13, "w1": 1.0, "w2": 0.35, "wobble": 0.15, "seed": 42,
    "decimate": 0.45,
    "smooth_iters": 0, "smooth_relax": 0.012,
    "z_flatten": 1.0,
    "growth_mode": "simple", "growth_factor": 1.12, "growth_strength": 0.25,
    "buckle_iters": 2, "buckle_mask": 0.35,
    "ellipsoid": None, "occipital_drop": 0.15,
    "noise_amp": 0.0, "noise_octaves": 3,
    "ventricle": False,
    "radius_clip_lo": 0.0, "radius_clip_hi": 2.0,
    "output": "hilbert_brain.stl",
    "fmt": "auto",
    "fem": None, "cortical_thickness": 0.3, "fem_growth_rate": 1.4,
    "neuro": None, "neuro_knn": 0,
    "preview": False, "repair": False,
}

PRESETS = {
    # HilbertGyri.py  -- fast minimal base generator
    "gyri": {
        "order": 3, "spline": 2000, "radius": 2.0, "sulcus": 0.55, "n_sides": 28,
        "decimate": 0.45, "growth_mode": "simple",
        "growth_factor": 1.12, "growth_strength": 0.25,
        "output": "hilbert_gyri_o3.stl",
    },
    # HilbertGyri2.py -- dense, smoothed, Z-flattened cortical sheet
    "gyri2": {
        "order": 4, "spline": 3500, "radius": 2.6, "sulcus": 0.58, "n_sides": 64,
        "k1": 4, "k2": 15, "wobble": 0.20,
        "decimate": 0.30, "smooth_iters": 90, "smooth_relax": 0.012,
        "z_flatten": 0.50,
        "growth_mode": "simple", "growth_factor": 1.08, "growth_strength": 0.18,
        "output": "hilbert_gyri_o4.stl",
    },
    # HilbertGyri3.py -- ellipsoid + Perlin folding + ventricle + buckle
    "gyri3": {
        "order": 4, "spline": 8000, "radius": 1.5, "sulcus": 0.75, "n_sides": 32,
        "k1": 9, "k2": 17, "w2": 0.30, "wobble": 0.0,
        "ellipsoid": (2.0, 1.3, 1.0), "occipital_drop": 0.15,
        "noise_amp": 0.45, "noise_octaves": 3,
        "ventricle": True, "radius_clip_lo": 0.25, "radius_clip_hi": 1.15,
        "growth_mode": "buckle", "growth_factor": 1.25,
        "buckle_iters": 2, "buckle_mask": 0.35,
        "decimate": 0.0,
        "output": "hilbert_brain.stl",
    },
    # Hilbertbrane.py -- interactive base config
    "brane": {"output": "HilbertGyri.stl"},
}


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate a Hilbert-curve cortical mesh and export STL.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--preset", choices=sorted(PRESETS), default=None,
                   help="start from a named preset (reproduces an original script)")
    p.add_argument("--list-presets", action="store_true",
                   help="print the presets and exit")
    p.add_argument("--interactive", action="store_true",
                   help="prompt for the main parameters instead of using flags")

    g = p.add_argument_group("curve")
    g.add_argument("--order", type=int, help="Hilbert order (2-5); voxels = 8**order")
    g.add_argument("--spline", type=int, help="centreline spline samples")

    g = p.add_argument_group("tube geometry")
    g.add_argument("--radius", type=float, help="mean tube radius")
    g.add_argument("--sulcus", type=float, help="sulcus depth / pinch strength (0-0.95)")
    g.add_argument("--n-sides", type=int, dest="n_sides", help="polygon sides around tube")

    g = p.add_argument_group("pinch field")
    g.add_argument("--k1", type=int, help="primary harmonic")
    g.add_argument("--k2", type=int, help="secondary harmonic")
    g.add_argument("--w1", type=float, help="primary weight")
    g.add_argument("--w2", type=float, help="secondary weight")
    g.add_argument("--wobble", type=float, help="low-frequency wobble")
    g.add_argument("--seed", type=int, help="RNG / noise seed")

    g = p.add_argument_group("brain shaping")
    g.add_argument("--ellipsoid", type=str,
                   help="map cube to ellipsoid 'A,L,S' (e.g. 2.0,1.3,1.0); off if unset")
    g.add_argument("--occipital-drop", type=float, dest="occipital_drop",
                   help="Z nudge when using --ellipsoid")
    g.add_argument("--noise-amp", type=float, dest="noise_amp",
                   help="Perlin folding amplitude (0 disables; needs 'noise' pkg)")
    g.add_argument("--noise-octaves", type=int, dest="noise_octaves",
                   help="Perlin octaves")
    g.add_argument("--ventricle", dest="ventricle", action="store_true", default=None,
                   help="apply lower-volume ventricle thinning")
    g.add_argument("--no-ventricle", dest="ventricle", action="store_false",
                   help="disable ventricle thinning")
    g.add_argument("--radius-clip-lo", type=float, dest="radius_clip_lo",
                   help="min radius as fraction of --radius")
    g.add_argument("--radius-clip-hi", type=float, dest="radius_clip_hi",
                   help="max radius as fraction of --radius")

    g = p.add_argument_group("post-processing")
    g.add_argument("--decimate", type=float, help="decimation reduction (0 disables)")
    g.add_argument("--smooth-iters", type=int, dest="smooth_iters",
                   help="finishing smooth iterations (0 disables)")
    g.add_argument("--smooth-relax", type=float, dest="smooth_relax",
                   help="finishing smooth relaxation factor")
    g.add_argument("--z-flatten", type=float, dest="z_flatten",
                   help="Z scale; <1 flattens toward a cortical sheet")
    g.add_argument("--growth-mode", choices=["none", "simple", "buckle"],
                   dest="growth_mode", help="differential-growth strategy")
    g.add_argument("--growth-factor", type=float, dest="growth_factor")
    g.add_argument("--growth-strength", type=float, dest="growth_strength")
    g.add_argument("--buckle-iters", type=int, dest="buckle_iters")
    g.add_argument("--buckle-mask", type=float, dest="buckle_mask",
                   help="grow vertices with relative-Z above this threshold")

    g = p.add_argument_group("output")
    g.add_argument("-o", "--output", help="output filename")
    g.add_argument("-f", "--format", dest="fmt",
                   choices=["auto"] + exporters.SUPPORTED, default=None,
                   help="output format; 'auto' infers from the filename extension "
                        "(stl|ply|3mf|gltf|glb|swc)")
    g.add_argument("--preview", action="store_true", help="open an interactive window")

    g = p.add_argument_group("FEM / morphoelastic (tetrahedral volume + growth field)")
    g.add_argument("--fem", choices=["auto"] + morphoelastic.SUPPORTED, default=None,
                   help="instead of a surface, emit a tet volume mesh with a "
                        "cortical growth field (msh|inp|vtu|feb). Forces watertight "
                        "repair of the surface first.")
    g.add_argument("--cortical-thickness", type=float, dest="cortical_thickness",
                   help="depth of the fast-growing cortical shell (model units)")
    g.add_argument("--fem-growth-rate", type=float, dest="fem_growth_rate",
                   help="growth multiplier at the surface (1.0 = no growth)")

    g = p.add_argument_group("neuro interop (GIFTI / NIfTI / graph)")
    g.add_argument("--neuro", choices=["auto"] + neuro.SUPPORTED, default=None,
                   help="emit a neuro-format output instead of a plain surface: "
                        "gii (surface + pinch overlay), nii (Hilbert volume), "
                        "graphml or gexf (path graph)")
    g.add_argument("--neuro-knn", type=int, dest="neuro_knn",
                   help="for graph export, also add k nearest-neighbour spatial edges")

    g = p.add_argument_group("provenance")
    g.add_argument("--provenance", choices=["none", "embed", "sidecar", "both"],
                   default="both",
                   help="how to record the full config+seed+git for exact "
                        "regeneration: embed in the file, write a sidecar JSON, "
                        "both, or none")
    g.add_argument("--from-provenance", dest="from_provenance", metavar="JSON",
                   help="regenerate exactly from a provenance JSON (or an output "
                        "file whose sidecar exists); other generation flags ignored")
    g.add_argument("--repair", action="store_true",
                   help="attempt watertight repair via pymeshfix before saving")
    return p


def resolve_config(args: argparse.Namespace) -> dict:
    """explicit flag > preset value > BASE default."""
    cfg = dict(BASE)
    if args.preset:
        cfg.update(PRESETS[args.preset])
    for key in BASE:
        val = getattr(args, key, None)
        if val is not None:
            cfg[key] = val
    if isinstance(cfg["ellipsoid"], str):
        cfg["ellipsoid"] = tuple(float(x) for x in cfg["ellipsoid"].split(","))
    return cfg


# ---------------------------------------------------------------------------
# Interactive prompts (fallback for Hilbertbrane.py behaviour)
# ---------------------------------------------------------------------------
def _ask(prompt, cast, default, lo=None, hi=None):
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        try:
            val = cast(raw)
        except ValueError:
            print("  not a valid number, try again.")
            continue
        if lo is not None and not (lo <= val <= hi):
            print(f"  enter a value in [{lo}, {hi}].")
            continue
        return val


def prompt_config(cfg: dict) -> dict:
    print("=== Hilbert Brain Surface Generator ===\n")
    cfg["order"]   = _ask("Hilbert order", int, cfg["order"], 2, 5)
    cfg["spline"]  = _ask("Spline samples", int, cfg["spline"], 1000, 12000)
    cfg["radius"]  = _ask("Mean radius", float, cfg["radius"], 0.5, 15.0)
    cfg["sulcus"]  = _ask("Sulcus depth", float, cfg["sulcus"], 0.0, 0.95)
    cfg["k1"]      = _ask("Primary frequency k1", int, cfg["k1"])
    cfg["k2"]      = _ask("Secondary frequency k2", int, cfg["k2"])
    cfg["wobble"]  = _ask("Wobble", float, cfg["wobble"], 0.0, 0.5)
    cfg["seed"]    = _ask("Random seed", int, cfg["seed"])
    cfg["decimate"] = _ask("Decimation", float, cfg["decimate"], 0.0, 0.9)
    cfg["growth_factor"] = _ask("Growth factor", float, cfg["growth_factor"], 1.0, 2.0)
    out = input(f"Output filename [{cfg['output']}]: ").strip() or cfg["output"]
    cfg["output"] = out if out.lower().endswith(".stl") else out + ".stl"
    return cfg


# ---------------------------------------------------------------------------
# The pipeline
# ---------------------------------------------------------------------------
def _normals(mesh):
    """Compute point normals robustly.

    The varying-radius tube can contain degenerate triangles (where the radius
    pinches toward zero) that make VTK's normal generator fail outright with
    "Normals could not be computed". We escalate:
      1. auto-orient (assumes a closed surface)
      2. plain (no auto-orient -> fine on open meshes)
      3. a light remesh via smoothing, which clears the degenerate cells
    If everything fails we return the mesh untouched rather than crash.
    """
    for kwargs in ({"auto_orient_normals": True}, {"auto_orient_normals": False}):
        try:
            return mesh.compute_normals(cell_normals=False, **kwargs)
        except (RuntimeError, KeyError):
            continue
    try:
        rescued = mesh.smooth(n_iter=30, relaxation_factor=0.5,
                              feature_angle=120, edge_angle=90,
                              boundary_smoothing=False)
        return rescued.compute_normals(cell_normals=False, auto_orient_normals=False)
    except (RuntimeError, KeyError):
        return mesh


def generate(cfg: dict):
    import pyvista as pv  # lazy: keeps --list-presets / --help GL-free
    # 1) curve -> path
    path = hc.build_hilbert_path(cfg["order"])
    if cfg["ellipsoid"]:
        path = hc.map_to_ellipsoid(hc.normalize_path(path, cfg["order"]),
                                   cfg["ellipsoid"], cfg["occipital_drop"])

    # 2) centreline spline (+ optional Perlin folding)
    centerline = pv.Spline(path, cfg["spline"])
    if cfg["noise_amp"] > 0:
        centerline.points = hc.perlin_fold(
            centerline.points, cfg["noise_octaves"], cfg["noise_amp"], cfg["seed"])

    # 3) pinch field -> radius profile
    t = hc.arclength_t(centerline.points)
    P = hc.pinch_field(t, cfg["k1"], cfg["k2"], cfg["w1"], cfg["w2"],
                       cfg["wobble"], cfg["seed"])
    if cfg["ventricle"]:
        P = P * hc.ventricle_mask(centerline.points)
    radius_abs = cfg["radius"] * (1.0 - cfg["sulcus"] * P)
    radius_abs = np.clip(radius_abs,
                         cfg["radius"] * cfg["radius_clip_lo"],
                         cfg["radius"] * cfg["radius_clip_hi"])

    # 4) tube
    mesh = hc.make_varying_radius_tube(
        centerline, radius_abs, cfg["radius"], cfg["n_sides"]).triangulate()

    # 5) decimate (decimation also clears degenerate cells -> safe normals)
    if cfg["decimate"] > 0:
        mesh = mesh.decimate(cfg["decimate"])
        mesh = _normals(mesh)

    # 6) finishing smooth (gyri2)
    if cfg["smooth_iters"] > 0:
        mesh = mesh.smooth(n_iter=cfg["smooth_iters"],
                           relaxation_factor=cfg["smooth_relax"],
                           feature_smoothing=False, boundary_smoothing=True)
        mesh = _normals(mesh)

    # 7) Z flatten
    if cfg["z_flatten"] != 1.0:
        mesh.scale([1.0, 1.0, cfg["z_flatten"]], inplace=True)
        mesh = _normals(mesh)

    # 8) differential growth
    mesh = _apply_growth(mesh, cfg)

    if cfg["repair"]:
        mesh = hc.repair_mesh(mesh)
    # cl_points + radius_abs are the SWC morphology skeleton (pre-tube)
    return mesh, np.asarray(centerline.points), radius_abs


def _apply_growth(mesh, cfg):
    mode = cfg["growth_mode"]
    if mode == "none":
        return mesh

    if mode == "simple":
        mesh = _normals(mesh)          # safe even on an undecimated tube
        z = mesh.points[:, 2]
        outer = z > z.mean()
        mesh.points[outer] += (cfg["growth_strength"]
                               * mesh.point_normals[outer]
                               * (cfg["growth_factor"] - 1.0))
        return _normals(mesh)

    # buckle (gyri3): iterate Taubin-ish smooth + outer normal inflation
    for _ in range(cfg["buckle_iters"]):
        mesh = mesh.smooth(n_iter=30, relaxation_factor=0.5,
                           feature_angle=120, edge_angle=90,
                           boundary_smoothing=False)
        z = mesh.points[:, 2]
        zrel = (z - z.min()) / (z.max() - z.min() + 1e-12)
        mask = zrel > cfg["buckle_mask"]
        disp = 0.4 * (cfg["growth_factor"] - 1.0) * mesh.point_normals
        mesh.points[mask] += disp[mask]
    return mesh


# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_presets:
        for name, over in PRESETS.items():
            print(f"{name:6s} -> {over}")
        return 0

    if args.from_provenance:
        record_in = provenance.load(args.from_provenance)
        cfg = {**BASE, **provenance.config_from_record(record_in)}
        if args.output:
            cfg["output"] = args.output
        print(f"Regenerating from {args.from_provenance} "
              f"(git {record_in.get('git', '?')}, created {record_in.get('created', '?')})")
    else:
        cfg = resolve_config(args)

        use_prompts = sys.stdin.isatty() and (
            args.interactive or args.preset == "brane"
            or (args.preset is None and len(sys.argv) == 1))
        if use_prompts:
            cfg = prompt_config(cfg)

    out_path, fmt = exporters.resolve(cfg["output"], cfg["fmt"])
    if cfg["fem"]:
        target, _ = morphoelastic.resolve(cfg["output"], cfg["fem"])
        target_desc = f"{target} [fem]"
    elif cfg["neuro"]:
        _, nfmt = neuro.resolve(cfg["output"], cfg["neuro"])
        target_desc = f"{neuro._stem(cfg['output'])} [neuro:{nfmt}]"
    else:
        target_desc = f"{out_path} [{fmt}]"
    print(f"Generating order={cfg['order']} spline={cfg['spline']} "
          f"radius={cfg['radius']} sulcus={cfg['sulcus']} -> {target_desc}")
    t0 = time.time()
    try:
        mesh, cl_points, radius = generate(cfg)
    except ImportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if cfg["preview"]:
        import pyvista as pv
        pl = pv.Plotter(window_size=(1024, 768))
        pl.add_mesh(mesh, smooth_shading=True, specular=10.0, metallic=0.1)
        pl.add_axes()
        pl.show()

    # Full provenance: the resolved config + seed + git SHA fully determine the
    # output, so this is enough to regenerate it exactly.
    command = "python " + " ".join([os.path.basename(sys.argv[0])] + sys.argv[1:])
    record = provenance.build_record(cfg, command=command)
    mode = args.provenance
    meta_flat = provenance.flatten(record) if mode in ("embed", "both") else None

    written: list[str] = []
    try:
        if cfg["fem"]:
            fem_path, fem_fmt = morphoelastic.resolve(cfg["output"], cfg["fem"])
            fem_path, volume = morphoelastic.surface_to_fem(
                mesh, fem_path, fem_fmt,
                cortical_thickness=cfg["cortical_thickness"],
                growth_rate=cfg["fem_growth_rate"], meta=meta_flat)
            written = [fem_path]
            g = np.asarray(volume.cell_data["growth"])
            summary = (f"{volume.n_points} nodes, {volume.n_cells} tets "
                       f"-- growth field {g.min():.3f}..{g.max():.3f}")

        elif cfg["neuro"]:
            t = hc.arclength_t(cl_points)
            P = hc.pinch_field(t, cfg["k1"], cfg["k2"], cfg["w1"], cfg["w2"],
                               cfg["wobble"], cfg["seed"])
            if cfg["ventricle"]:
                P = P * hc.ventricle_mask(cl_points)
            written = neuro.write_neuro(
                cfg["output"], cfg["neuro"], mesh=mesh, centerline=cl_points,
                pinch=P, order=cfg["order"], knn=cfg["neuro_knn"], meta=meta_flat)
            summary = ""

        else:
            out_path = exporters.write(mesh, cl_points, radius, out_path, fmt, meta_flat)
            written = [out_path]
            if fmt == "ply" and mode in ("embed", "both"):
                provenance.embed_ply_comments(out_path, record)
            if fmt == "swc":
                summary = f"{len(cl_points)} samples, single unbranched path"
            else:
                open_edges = hc.open_edge_count(mesh)
                summary = ("watertight" if open_edges == 0
                           else f"{open_edges} open/non-manifold edges")
    except (ImportError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    sidecars = []
    if mode in ("sidecar", "both"):
        sidecars = [provenance.write_sidecar(w, record) for w in written]

    dt = time.time() - t0
    print(f"Saved {', '.join(written)} in {dt:.1f}s" + (f" -- {summary}" if summary else ""))
    if sidecars:
        print(f"  provenance: {', '.join(sidecars)}")
    if (not cfg["fem"] and not cfg["neuro"] and fmt not in ("swc",)
            and "open" in (summary or "") and not cfg["repair"]):
        print("  tip: re-run with --repair (needs `pip install pymeshfix`) "
              "for a print-ready watertight mesh.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
