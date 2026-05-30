"""
neuro.py
========
Bio/neuro interoperability for hilbertbrane. The SWC neuron-morphology writer
already lives in exporters.py (a varying-radius centreline *is* SWC); this
module adds the surface- and volume-level neuro formats:

    gii      GIFTI surface (.surf.gii) + pinch-field overlay (.shape.gii)
             -> FreeView, Connectome Workbench, MNE, nilearn, pycortex
    nii      NIfTI volume (.nii.gz) of the Hilbert traversal, voxelised
             -> 3D Slicer, FSL, nilearn
    graphml  the Hilbert path as a graph (also gexf)
    gexf     -> NetworkX, igraph, Brain Connectivity Toolbox

Honesty, same as the rest of the project: this makes the geometry *speak* neuro
formats so it loads in neuro tooling for visualisation, teaching, and pipeline
testing. It is generative geometry, not a measured or anatomically validated
brain; the formats imply interoperability, not fidelity.

Optional dependencies, imported lazily with clear errors:
    nibabel    -- GIFTI + NIfTI   (pip install nibabel)
    networkx   -- graph export    (pip install networkx)
    scipy      -- fast overlay resampling / kNN edges (falls back if absent)
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

import numpy as np

import hilbert_core as hc

__all__ = [
    "write_neuro", "resolve", "SUPPORTED",
    "write_gifti_surface", "write_gifti_overlay", "surface_overlay_scalars",
    "hilbert_index_volume", "write_nifti",
    "path_to_graph", "write_graph",
]

SUPPORTED = ["gii", "nii", "graphml", "gexf"]


# ---------------------------------------------------------------------------
# path / format resolution (handles the double .nii.gz extension)
# ---------------------------------------------------------------------------
def resolve(path: str, fmt: Optional[str] = None) -> tuple[str, str]:
    low = path.lower()
    if fmt in (None, "auto"):
        if low.endswith(".nii.gz") or low.endswith(".nii"):
            fmt = "nii"
        elif low.endswith(".gii"):
            fmt = "gii"
        elif low.endswith(".graphml"):
            fmt = "graphml"
        elif low.endswith(".gexf"):
            fmt = "gexf"
        else:
            fmt = "gii"
    if fmt not in SUPPORTED:
        raise ValueError(f"unknown neuro format {fmt!r}; choose from {SUPPORTED}")
    return path, fmt


def _stem(path: str) -> str:
    """Strip any known neuro extension to get a base name."""
    low = path.lower()
    for suf in (".surf.gii", ".shape.gii", ".func.gii", ".gii",
                ".nii.gz", ".nii", ".graphml", ".gexf"):
        if low.endswith(suf):
            return path[: -len(suf)]
    return os.path.splitext(path)[0]


def _triangles(mesh) -> np.ndarray:
    tri = mesh.triangulate()
    try:
        return np.asarray(tri.regular_faces, dtype=np.int32)
    except AttributeError:
        return np.asarray(tri.faces).reshape(-1, 4)[:, 1:].astype(np.int32)


# ---------------------------------------------------------------------------
# GIFTI
# ---------------------------------------------------------------------------
def _gifti():
    try:
        import nibabel as nib
        from nibabel import gifti
        return nib, gifti
    except ImportError as exc:
        raise ImportError(
            "GIFTI export needs nibabel. Install with `pip install nibabel`."
        ) from exc


def _set_meta(obj, meta: dict) -> None:
    if not meta:
        return
    try:  # nibabel metadata API varies a little across versions
        for k, v in meta.items():
            obj.meta[str(k)] = str(v)
    except Exception:
        pass


def write_gifti_surface(mesh, path: str, meta: Optional[dict] = None) -> str:
    """Write vertices + triangles as a GIFTI surface (.surf.gii)."""
    nib, gifti = _gifti()
    pts = np.asarray(mesh.points, dtype=np.float32)
    tris = _triangles(mesh)
    coords = gifti.GiftiDataArray(pts, intent="NIFTI_INTENT_POINTSET",
                                  datatype="NIFTI_TYPE_FLOAT32")
    faces = gifti.GiftiDataArray(tris, intent="NIFTI_INTENT_TRIANGLE",
                                 datatype="NIFTI_TYPE_INT32")
    img = gifti.GiftiImage(darrays=[coords, faces])
    _set_meta(img, meta or {})
    nib.save(img, path)
    return path


def write_gifti_overlay(scalars: np.ndarray, path: str,
                        intent: str = "shape",
                        meta: Optional[dict] = None) -> str:
    """Write a per-vertex scalar overlay (.shape.gii / .func.gii)."""
    nib, gifti = _gifti()
    code = ("NIFTI_INTENT_SHAPE" if intent == "shape" else "NIFTI_INTENT_NONE")
    da = gifti.GiftiDataArray(np.asarray(scalars, dtype=np.float32),
                              intent=code, datatype="NIFTI_TYPE_FLOAT32")
    img = gifti.GiftiImage(darrays=[da])
    _set_meta(img, meta or {})
    nib.save(img, path)
    return path


def surface_overlay_scalars(mesh, centerline=None, pinch=None) -> tuple[np.ndarray, str]:
    """Per-vertex overlay scalars, analogous to sulcal depth / curvature.

    Preference: resample the centreline pinch field onto each mesh vertex by
    nearest point (works regardless of decimation). If the pinch field or scipy
    is unavailable, fall back to mesh mean curvature -- itself a sulcal-depth
    analogue.
    """
    if centerline is not None and pinch is not None:
        try:
            from scipy.spatial import cKDTree
            _, idx = cKDTree(np.asarray(centerline)).query(np.asarray(mesh.points))
            return np.asarray(pinch)[idx], "pinch"
        except ImportError:
            pass
    return np.asarray(mesh.curvature("mean")), "curvature"


# ---------------------------------------------------------------------------
# NIfTI: voxelise the Hilbert traversal into a volume
# ---------------------------------------------------------------------------
def hilbert_index_volume(order: int, upsample: int = 1) -> np.ndarray:
    """A (s, s, s) volume (s = 2**order) whose intensity is the normalised
    Hilbert traversal index of each cell.

    The curve is space-filling, so every voxel is visited -- "occupancy" alone
    would be uniformly 1 and useless. Encoding the *visit order* instead yields
    a dense scalar field that snakes through the cube, which is what's actually
    informative to look at in a volume viewer.
    """
    side = 1 << order
    pts = hc.build_hilbert_path(order).astype(int)
    vol = np.zeros((side, side, side), dtype=np.float32)
    n = len(pts)
    for idx, (x, y, z) in enumerate(pts):
        vol[x, y, z] = idx / (n - 1)
    if upsample > 1:
        vol = np.kron(vol, np.ones((upsample, upsample, upsample), dtype=np.float32))
    return vol


def write_nifti(volume: np.ndarray, path: str,
                voxel_size: float = 1.0,
                meta: Optional[dict] = None) -> str:
    """Write a 3-D array as a NIfTI image (.nii.gz) with a mm-scaled affine."""
    try:
        import nibabel as nib
    except ImportError as exc:
        raise ImportError(
            "NIfTI export needs nibabel. Install with `pip install nibabel`."
        ) from exc
    affine = np.diag([voxel_size, voxel_size, voxel_size, 1.0])
    img = nib.Nifti1Image(np.asarray(volume, dtype=np.float32), affine)
    try:
        img.header.set_xyzt_units("mm")
    except Exception:
        pass
    if meta:
        img.header["descrip"] = ("hilbertbrane " + ";".join(
            f"{k}={v}" for k, v in meta.items()))[:79].encode("utf-8", "ignore")
    nib.save(img, path)
    return path


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------
def path_to_graph(points: np.ndarray, knn: int = 0):
    """Build a NetworkX graph from the ordered Hilbert path.

    Nodes carry x/y/z; consecutive samples are joined by 'path' edges weighted
    by Euclidean length. With ``knn > 0`` each node also links to its k nearest
    neighbours in space ('spatial' edges) -- turning the chain into a graph
    where geodesic and path distance diverge, which is the interesting regime
    for graph-theoretic analysis.
    """
    try:
        import networkx as nx
    except ImportError as exc:
        raise ImportError(
            "graph export needs networkx. Install with `pip install networkx`."
        ) from exc

    pts = np.asarray(points, dtype=float)
    G = nx.Graph()
    for i, (x, y, z) in enumerate(pts):
        G.add_node(int(i), x=float(x), y=float(y), z=float(z))
    for i in range(len(pts) - 1):
        d = float(np.linalg.norm(pts[i + 1] - pts[i]))
        G.add_edge(i, i + 1, weight=d, length=d, kind="path")

    if knn > 0:
        try:
            from scipy.spatial import cKDTree
            dist, idx = cKDTree(pts).query(pts, k=knn + 1)
            for i in range(len(pts)):
                for j, dij in zip(idx[i, 1:], dist[i, 1:]):
                    j = int(j)
                    if not G.has_edge(i, j):
                        G.add_edge(i, j, weight=float(dij), length=float(dij),
                                   kind="spatial")
        except ImportError:
            pass
    return G


def write_graph(points: np.ndarray, path: str, fmt: str,
                knn: int = 0, meta: Optional[dict] = None):
    import networkx as nx
    G = path_to_graph(points, knn=knn)
    for k, v in (meta or {}).items():
        G.graph[str(k)] = str(v)
    if fmt == "graphml":
        nx.write_graphml(G, path)
    elif fmt == "gexf":
        nx.write_gexf(G, path)
    else:
        raise ValueError(f"unsupported graph format {fmt!r}")
    return path


# ---------------------------------------------------------------------------
# dispatch
# ---------------------------------------------------------------------------
def write_neuro(path: str, fmt: Optional[str] = None, *,
                mesh=None, centerline=None, pinch=None,
                order: Optional[int] = None,
                voxel_size: float = 1.0, upsample: int = 1,
                knn: int = 0, meta: Optional[dict] = None) -> list[str]:
    """Dispatch to the right neuro writer; returns the list of files written."""
    _, fmt = resolve(path, fmt)
    meta = dict(meta or {})
    meta.setdefault("created", datetime.now(timezone.utc).isoformat())
    stem = _stem(path)

    if fmt == "gii":
        if mesh is None:
            raise ValueError("GIFTI export needs a surface mesh.")
        surf = write_gifti_surface(mesh, stem + ".surf.gii", meta)
        scalars, name = surface_overlay_scalars(mesh, centerline, pinch)
        meta["overlay"] = name
        shape = write_gifti_overlay(scalars, stem + ".shape.gii", "shape", meta)
        return [surf, shape]

    if fmt == "nii":
        if order is None:
            raise ValueError("NIfTI export needs the Hilbert order.")
        vol = hilbert_index_volume(order, upsample=upsample)
        return [write_nifti(vol, stem + ".nii.gz", voxel_size, meta)]

    if fmt in ("graphml", "gexf"):
        if centerline is None:
            raise ValueError("graph export needs the Hilbert path points.")
        ext = ".graphml" if fmt == "graphml" else ".gexf"
        return [write_graph(centerline, stem + ext, fmt, knn=knn, meta=meta)]

    raise ValueError(f"unhandled neuro format {fmt!r}")
