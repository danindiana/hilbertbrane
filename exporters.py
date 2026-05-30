"""
exporters.py
============
One in-memory result, many file formats. Everything goes through a single
entry point:

    write(mesh, centerline, radius, path, fmt=None, meta=None)

  * mesh        -- final PyVista surface (PolyData), used by stl/ply/3mf/gltf/glb
  * centerline  -- ordered (N, 3) array of curve points, used by swc
  * radius      -- per-centerline-point radius array, used by swc
  * path        -- output filename
  * fmt         -- explicit format; if None/"auto" it is inferred from the extension
  * meta        -- optional dict of provenance metadata embedded where supported

Format support and dependencies:

    stl   PyVista (always available)            triangle soup, no units
    ply   PyVista (always available)            keeps per-vertex scalars
    3mf   pure stdlib (zip + XML)               units=mm, manifold-by-spec, metadata
    gltf  trimesh (optional)                    web/3D ecosystem, PBR-ready
    glb   trimesh (optional)                    binary glTF
    swc   pure stdlib                            neuron-morphology skeleton

Only the format actually requested is imported, so missing optional packages
never break unrelated exports.
"""

from __future__ import annotations

import os
import zipfile
from datetime import datetime, timezone
from typing import Optional, Sequence

import numpy as np

__all__ = ["write", "resolve", "SUPPORTED", "EXT_TO_FMT"]

EXT_TO_FMT = {
    ".stl": "stl", ".ply": "ply", ".3mf": "3mf",
    ".gltf": "gltf", ".glb": "glb", ".swc": "swc",
}
FMT_TO_EXT = {v: k for k, v in EXT_TO_FMT.items()}
SUPPORTED = sorted(FMT_TO_EXT)


# ---------------------------------------------------------------------------
# Path / format reconciliation
# ---------------------------------------------------------------------------
def resolve(path: str, fmt: Optional[str] = None) -> tuple[str, str]:
    """Return ``(final_path, fmt)``.

    Rules: an explicit ``fmt`` wins and the extension is corrected to match;
    otherwise the extension decides, defaulting to STL when unknown.
    """
    stem, ext = os.path.splitext(path)
    ext = ext.lower()
    if fmt in (None, "auto"):
        fmt = EXT_TO_FMT.get(ext, "stl")
    if fmt not in FMT_TO_EXT:
        raise ValueError(f"unknown format {fmt!r}; choose from {SUPPORTED}")
    want_ext = FMT_TO_EXT[fmt]
    if ext != want_ext:
        path = stem + want_ext
    return path, fmt


# ---------------------------------------------------------------------------
# Public dispatch
# ---------------------------------------------------------------------------
def write(mesh,
          centerline: Optional[np.ndarray],
          radius: Optional[np.ndarray],
          path: str,
          fmt: Optional[str] = None,
          meta: Optional[dict] = None) -> str:
    """Write the result in the requested format; returns the final path."""
    path, fmt = resolve(path, fmt)
    meta = meta or {}

    if fmt == "stl":
        _write_pyvista(mesh, path)
    elif fmt == "ply":
        _write_pyvista(mesh, path)
    elif fmt == "3mf":
        _write_3mf(mesh, path, meta)
    elif fmt in ("gltf", "glb"):
        _write_gltf(mesh, path, meta)
    elif fmt == "swc":
        _write_swc(centerline, radius, path, meta)
    else:  # pragma: no cover - resolve() already validated
        raise ValueError(f"unhandled format {fmt!r}")
    return path


# ---------------------------------------------------------------------------
# Backend helpers
# ---------------------------------------------------------------------------
def _triangles(mesh) -> np.ndarray:
    """Return an (n, 3) int array of triangle vertex indices."""
    tri = mesh.triangulate()
    try:
        return np.asarray(tri.regular_faces, dtype=np.int64)
    except AttributeError:  # very old PyVista
        faces = np.asarray(tri.faces).reshape(-1, 4)
        return faces[:, 1:].astype(np.int64)


def _write_pyvista(mesh, path: str) -> None:
    # PyVista picks the writer from the extension; PLY carries any point_data
    # scalars (e.g. radius_profile / curvature) as per-vertex attributes.
    mesh.save(path)


def _write_gltf(mesh, path: str, meta: dict) -> None:
    try:
        import trimesh
    except ImportError as exc:
        raise ImportError(
            "glTF/GLB export needs trimesh. Install with `pip install trimesh` "
            "(or export to .glb only after installing it)."
        ) from exc

    tm = trimesh.Trimesh(vertices=np.asarray(mesh.points),
                         faces=_triangles(mesh),
                         process=False)
    if meta:
        tm.metadata.update({str(k): str(v) for k, v in meta.items()})

    if path.lower().endswith(".glb"):
        tm.export(path)  # single self-contained binary
        return

    # .gltf: embed buffers as data URIs so the result is one portable file
    # instead of the default .gltf + sidecar .bin split.
    from trimesh.exchange.gltf import export_gltf
    files = export_gltf(tm.scene(), embed_buffers=True)
    data = next(v for k, v in files.items() if k.lower().endswith(".gltf"))
    mode = "wb" if isinstance(data, (bytes, bytearray)) else "w"
    with open(path, mode) as fh:
        fh.write(data)


def _write_swc(centerline: Optional[np.ndarray],
               radius: Optional[np.ndarray],
               path: str,
               meta: dict) -> None:
    """Write the varying-radius centreline as an SWC neuron-morphology file.

    SWC columns: id type x y z radius parent. A Hilbert centreline is a single
    unbranched path, so parent is simply the previous sample (root parent = -1).
    Type 0 = undefined (this is generative geometry, not a measured neuron).
    """
    if centerline is None or radius is None:
        raise ValueError("SWC export needs both `centerline` and `radius`.")
    pts = np.asarray(centerline, dtype=float)
    rad = np.asarray(radius, dtype=float)
    if len(pts) != len(rad):
        raise ValueError(
            f"centerline ({len(pts)}) and radius ({len(rad)}) length mismatch.")

    lines = [
        "# SWC generated by hilbertbrane -- generative geometry, NOT a measured neuron.",
        f"# created {datetime.now(timezone.utc).isoformat()}",
    ]
    lines += [f"# {k}: {v}" for k, v in meta.items()]
    lines.append("# id type x y z radius parent")
    for i, ((x, y, z), r) in enumerate(zip(pts, rad), start=1):
        parent = -1 if i == 1 else i - 1
        lines.append(f"{i} 0 {x:.6f} {y:.6f} {z:.6f} {r:.6f} {parent}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# 3MF (OPC zip + 3D model XML) -- hand-written so it needs no extra packages
# ---------------------------------------------------------------------------
_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" '
    'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="model" '
    'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
    "</Types>"
)
_RELS = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
    'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
    "</Relationships>"
)
_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"


def _xml_escape(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _build_3mf_model(vertices: np.ndarray, triangles: np.ndarray,
                     meta: dict) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<model unit="millimeter" xml:lang="en-US" xmlns="{_NS}">']
    out.append('<metadata name="Application">hilbertbrane</metadata>')
    for k, v in meta.items():
        out.append(f'<metadata name="{_xml_escape(k)}">{_xml_escape(v)}</metadata>')
    out.append('<resources><object id="1" type="model"><mesh><vertices>')
    out += [f'<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>'
            for x, y, z in vertices]
    out.append("</vertices><triangles>")
    out += [f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in triangles]
    out.append("</triangles></mesh></object></resources>")
    out.append('<build><item objectid="1"/></build></model>')
    return "".join(out)


def _write_3mf(mesh, path: str, meta: dict) -> None:
    vertices = np.asarray(mesh.points, dtype=float)
    triangles = _triangles(mesh)
    model_xml = _build_3mf_model(vertices, triangles, meta)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _CONTENT_TYPES)
        zf.writestr("_rels/.rels", _RELS)
        zf.writestr("3D/3dmodel.model", model_xml)
