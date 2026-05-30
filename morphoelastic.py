"""
morphoelastic.py
================
Scaffolding for the "model the buckling instead of faking it" direction.

The differential-growth step in hilbert_gen.py *fakes* cortical folding by
displacing outer vertices along their normals. The real phenomenon is
growth-induced mechanical instability of a thin fast-growing cortex over a
slower-growing core (Tallinen, Chung, Biggins & Mahadevan, 2014). Actually
*producing* a fold requires a nonlinear finite-element solver. This module does
the honest, solver-agnostic part:

    surface mesh  ->  (repair to watertight)  ->  tetrahedral volume mesh
                  ->  cortical growth field g(x)  ->  FEM file

so the geometry + the field that *drives* the instability are usable by a real
solver (FEBio, FEniCS/dolfinx, Abaqus) or any continuum-mechanics tooling.

What this is NOT: a solver, a validated constitutive model, or a guarantee of
biological fidelity. The growth field is a depth-based cortex/core proxy, and
the FEBio writer emits geometry + field + stub material/BC/solver blocks you
must complete before a run means anything. Comments in the output say so.

Dependencies (all optional, imported lazily, with clear errors if missing):
    tetgen     -- tetrahedralisation (pip install tetgen)
    pymeshfix  -- watertight repair  (pip install pymeshfix)
    meshio     -- .msh/.inp/.vtu I/O (pip install meshio)
.feb is hand-written and needs none of the above beyond the volume mesh.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

import numpy as np

import hilbert_core as hc

__all__ = [
    "tetrahedralize",
    "cortical_growth_field",
    "write_volume",
    "resolve",
    "SUPPORTED",
    "VTK_TETRA",
]

VTK_TETRA = 10  # vtkCellType for a linear tetrahedron

EXT_TO_FMT = {".msh": "msh", ".inp": "inp", ".vtu": "vtu", ".feb": "feb"}
FMT_TO_EXT = {v: k for k, v in EXT_TO_FMT.items()}
SUPPORTED = sorted(FMT_TO_EXT)

# meshio handles these three; .feb is ours.
_MESHIO_FORMAT = {"msh": "gmsh", "inp": "abaqus", "vtu": "vtu"}


# ---------------------------------------------------------------------------
# 1) Surface -> watertight tetrahedral volume
# ---------------------------------------------------------------------------
def tetrahedralize(surface,
                   ensure_watertight: bool = True,
                   switches: Optional[str] = None,
                   order: int = 1):
    """Tetrahedralise a closed surface into a PyVista ``UnstructuredGrid``.

    TetGen requires a watertight, manifold input. Our generated surfaces are
    typically NOT closed, so by default we repair them first (pymeshfix) and
    refuse to proceed if repair fails -- a tet mesh of a leaky surface is
    meaningless. This is the same watertightness requirement that matters for
    printing, surfacing here because volume meshing is unforgiving about it.
    """
    try:
        import tetgen
    except ImportError as exc:
        raise ImportError(
            "tetrahedralisation needs tetgen. Install with `pip install tetgen`."
        ) from exc

    surf = surface.triangulate()
    if ensure_watertight and not hc.is_watertight(surf):
        surf = hc.repair_mesh(surf).triangulate()
        if not hc.is_watertight(surf):
            raise ValueError(
                "surface is not watertight even after repair; cannot tetrahedralise. "
                "Generate with --repair, or pre-clean the mesh, before meshing a volume."
            )

    tet = tetgen.TetGen(surf)
    if switches:
        tet.tetrahedralize(switches=switches)
    else:
        # quality switches: bounded radius-edge ratio + min dihedral angle
        tet.tetrahedralize(order=order, mindihedral=20.0, minratio=1.5)
    grid = tet.grid
    if grid is None or grid.n_cells == 0:
        raise RuntimeError("tetrahedralisation produced no cells.")
    return grid


def _extract_tets(volume) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(points, tets)`` with tets as an (n, 4) int array."""
    points = np.asarray(volume.points, dtype=float)
    cells = volume.cells_dict
    if VTK_TETRA not in cells:
        raise ValueError("volume mesh contains no linear tetrahedra.")
    return points, np.asarray(cells[VTK_TETRA], dtype=np.int64)


# ---------------------------------------------------------------------------
# 2) Cortical growth field (the thing that drives buckling)
# ---------------------------------------------------------------------------
def cortical_growth_field(volume,
                          surface,
                          cortical_thickness: float,
                          growth_rate: float = 1.4):
    """Attach a depth-based growth multiplier to ``volume`` (returns it).

    In the Tallinen-Mahadevan picture, folds emerge because a thin outer cortex
    expands tangentially relative to a non-growing core. We approximate the
    *driver* of that instability: nodes within ``cortical_thickness`` of the
    surface get a growth multiplier ramping from 1.0 (core / inner edge of
    cortex) up to ``growth_rate`` (at the surface); the core stays at 1.0.

    Writes point_data 'depth' (distance below the surface) and 'growth', and
    cell_data 'growth' (per-tet mean) -- the form most FEM tools expect.

    Note: this is an isotropic scalar proxy. A faithful model uses an
    anisotropic (tangential) growth tensor; that belongs in the solver setup.
    """
    surf = surface.triangulate()
    # signed implicit distance: negative inside the closed surface
    sampled = volume.compute_implicit_distance(surf)
    signed = np.asarray(sampled.point_data["implicit_distance"])
    depth = np.clip(-signed, 0.0, None)  # how far *below* the surface

    # ramp: 1.0 at depth >= thickness, growth_rate at depth == 0
    if cortical_thickness <= 0:
        frac = np.zeros_like(depth)
    else:
        frac = np.clip(1.0 - depth / cortical_thickness, 0.0, 1.0)
    g_node = 1.0 + (growth_rate - 1.0) * frac

    volume = volume.copy()
    volume.point_data["depth"] = depth
    volume.point_data["growth"] = g_node

    _, tets = _extract_tets(volume)
    volume.cell_data["growth"] = g_node[tets].mean(axis=1)
    return volume


# ---------------------------------------------------------------------------
# 3) Export
# ---------------------------------------------------------------------------
def resolve(path: str, fmt: Optional[str] = None) -> tuple[str, str]:
    """Reconcile filename + explicit format, defaulting unknown extensions to .vtu."""
    stem, ext = os.path.splitext(path)
    ext = ext.lower()
    if fmt in (None, "auto"):
        fmt = EXT_TO_FMT.get(ext, "vtu")
    if fmt not in FMT_TO_EXT:
        raise ValueError(f"unknown FEM format {fmt!r}; choose from {SUPPORTED}")
    want = FMT_TO_EXT[fmt]
    if ext != want:
        path = stem + want
    return path, fmt


def write_volume(volume,
                 path: str,
                 fmt: Optional[str] = None,
                 meta: Optional[dict] = None) -> str:
    """Write a tetrahedral volume mesh in the requested FEM format."""
    path, fmt = resolve(path, fmt)
    meta = meta or {}
    if fmt == "feb":
        _write_feb(volume, path, meta)
    else:
        _write_meshio(volume, path, fmt, meta)
    return path


def _write_meshio(volume, path: str, fmt: str, meta: dict) -> None:
    try:
        import meshio
    except ImportError as exc:
        raise ImportError(
            f"{fmt} export needs meshio. Install with `pip install meshio`."
        ) from exc

    points, tets = _extract_tets(volume)
    point_data, cell_data = {}, {}
    if "growth" in volume.point_data:
        point_data["growth"] = np.asarray(volume.point_data["growth"])
        point_data["depth"] = np.asarray(volume.point_data["depth"])
    if "growth" in volume.cell_data:
        cell_data["growth"] = [np.asarray(volume.cell_data["growth"])]

    mesh = meshio.Mesh(points=points, cells=[("tetra", tets)],
                       point_data=point_data or None,
                       cell_data=cell_data or None)
    mesh.write(path, file_format=_MESHIO_FORMAT[fmt])


# ---------------------------------------------------------------------------
# FEBio .feb writer (hand-written; geometry + growth field + clearly-marked stubs)
# ---------------------------------------------------------------------------
def _write_feb(volume, path: str, meta: dict) -> None:
    points, tets = _extract_tets(volume)
    g_elem = (np.asarray(volume.cell_data["growth"])
              if "growth" in volume.cell_data else np.ones(len(tets)))

    out = ['<?xml version="1.0" encoding="ISO-8859-1"?>',
           '<febio_spec version="4.0">']
    out.append("<!-- Generated by hilbertbrane/morphoelastic.py. -->")
    out.append("<!-- SCAFFOLD: geometry + cortical growth field are real; the")
    out.append("     material, boundary conditions, growth law and solver Control")
    out.append("     blocks below are stubs. Complete them for a meaningful run. -->")
    for k, v in meta.items():
        out.append(f"<!-- {k}: {v} -->")

    out.append('<Module type="solid"/>')

    # --- stub material: neo-Hookean (replace with a growth/morphoelastic model)
    out.append("<Material>")
    out.append('  <material id="1" name="tissue" type="neo-Hookean">')
    out.append("    <E>1.0</E>")
    out.append("    <v>0.45</v>")
    out.append("  </material>")
    out.append("</Material>")

    # --- geometry
    out.append("<Mesh>")
    out.append('  <Nodes name="all">')
    out += [f'    <node id="{i+1}">{x:.6f},{y:.6f},{z:.6f}</node>'
            for i, (x, y, z) in enumerate(points)]
    out.append("  </Nodes>")
    out.append('  <Elements type="tet4" name="brain">')
    out += [f'    <elem id="{i+1}">{a+1},{b+1},{c+1},{d+1}</elem>'
            for i, (a, b, c, d) in enumerate(tets)]
    out.append("  </Elements>")
    out.append("</Mesh>")

    out.append("<MeshDomains>")
    out.append('  <SolidDomain name="brain" mat="tissue"/>')
    out.append("</MeshDomains>")

    # --- the physically meaningful part: per-element growth multiplier
    out.append("<MeshData>")
    out.append('  <ElementData name="growth" elem_set="brain" datatype="scalar">')
    out += [f'    <e lid="{i+1}">{g:.6f}</e>' for i, g in enumerate(g_elem)]
    out.append("  </ElementData>")
    out.append("</MeshData>")

    # --- stub boundary conditions + step (must be completed)
    out.append("<!-- TODO: add <Boundary> fixing/anchoring the core, and a")
    out.append("     <Step> applying volumetric/tangential growth from the")
    out.append("     'growth' field, then a <Control> block (time stepper, solver). -->")
    out.append('<Step>')
    out.append('  <step name="grow"><Control>')
    out.append("    <time_steps>10</time_steps>")
    out.append("    <step_size>0.1</step_size>")
    out.append("  </Control></step>")
    out.append("</Step>")

    out.append("</febio_spec>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


# ---------------------------------------------------------------------------
# convenience: one call from a surface to a FEM file
# ---------------------------------------------------------------------------
def surface_to_fem(surface,
                   path: str,
                   fmt: Optional[str] = None,
                   cortical_thickness: float = 0.3,
                   growth_rate: float = 1.4,
                   meta: Optional[dict] = None,
                   tet_switches: Optional[str] = None) -> tuple[str, "object"]:
    """surface -> watertight tet volume + growth field -> FEM file. Returns (path, volume)."""
    volume = tetrahedralize(surface, switches=tet_switches)
    volume = cortical_growth_field(volume, surface,
                                   cortical_thickness=cortical_thickness,
                                   growth_rate=growth_rate)
    meta = dict(meta or {})
    meta.setdefault("created", datetime.now(timezone.utc).isoformat())
    meta.setdefault("n_tets", volume.n_cells)
    out = write_volume(volume, path, fmt, meta)
    return out, volume
