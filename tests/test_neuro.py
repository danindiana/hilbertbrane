"""Tests for neuro interop (GIFTI / NIfTI / graph).

GIFTI + NIfTI need nibabel; graph export needs networkx. Each test skips
cleanly when its dependency is absent.
"""

import numpy as np
import pytest

pv = pytest.importorskip("pyvista")

import hilbert_core as hc
import neuro


@pytest.fixture(scope="module")
def mesh():
    return pv.Sphere(theta_resolution=16, phi_resolution=16).triangulate()


@pytest.fixture(scope="module")
def skeleton():
    pts = hc.build_hilbert_path(3)
    pinch = hc.pinch_field(hc.arclength_t(pts))
    return pts, pinch


# ---------------------------------------------------------------------------
# resolve / stem
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("path,expect", [
    ("b.gii", "gii"), ("b.surf.gii", "gii"), ("b.nii.gz", "nii"),
    ("b.nii", "nii"), ("b.graphml", "graphml"), ("b.gexf", "gexf"),
    ("b.stl", "gii"),  # unknown -> default gii
])
def test_resolve_infers_neuro_format(path, expect):
    assert neuro.resolve(path, None)[1] == expect


def test_resolve_unknown_raises():
    with pytest.raises(ValueError):
        neuro.resolve("b.gii", "xyz")


@pytest.mark.parametrize("path,stem", [
    ("brain.surf.gii", "brain"), ("brain.nii.gz", "brain"),
    ("brain.graphml", "brain"), ("path/to/brain.gexf", "path/to/brain"),
])
def test_stem_strips_known_extensions(path, stem):
    assert neuro._stem(path) == stem


# ---------------------------------------------------------------------------
# GIFTI
# ---------------------------------------------------------------------------
def test_gifti_surface_and_overlay_roundtrip(mesh, skeleton, tmp_path):
    nib = pytest.importorskip("nibabel")
    pts, pinch = skeleton
    written = neuro.write_neuro(str(tmp_path / "b.gii"), "gii",
                                mesh=mesh, centerline=pts, pinch=pinch)
    assert len(written) == 2

    surf = nib.load(str(tmp_path / "b.surf.gii"))
    coords = surf.agg_data("NIFTI_INTENT_POINTSET")
    tris = surf.agg_data("NIFTI_INTENT_TRIANGLE")
    assert coords.shape == (mesh.n_points, 3)
    assert tris.shape[0] == mesh.n_cells
    assert int(tris.max()) < mesh.n_points

    overlay = nib.load(str(tmp_path / "b.shape.gii")).agg_data()
    assert overlay.shape[0] == mesh.n_points  # one scalar per vertex


def test_overlay_prefers_pinch_then_falls_back_to_curvature(mesh, skeleton):
    pts, pinch = skeleton
    vals, name = neuro.surface_overlay_scalars(mesh, pts, pinch)
    assert name == "pinch"
    assert len(vals) == mesh.n_points

    vals2, name2 = neuro.surface_overlay_scalars(mesh, None, None)
    assert name2 == "curvature"
    assert len(vals2) == mesh.n_points


def test_gifti_requires_mesh(tmp_path):
    pytest.importorskip("nibabel")
    with pytest.raises(ValueError):
        neuro.write_neuro(str(tmp_path / "b.gii"), "gii", mesh=None)


# ---------------------------------------------------------------------------
# NIfTI
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("order", [2, 3, 4])
def test_hilbert_index_volume_is_dense_gradient(order):
    vol = neuro.hilbert_index_volume(order)
    side = 1 << order
    assert vol.shape == (side, side, side)
    # space-filling: every voxel is assigned a (distinct-ish) traversal value
    assert np.isclose(vol.min(), 0.0)
    assert np.isclose(vol.max(), 1.0)
    assert len(np.unique(vol)) == side ** 3  # bijective traversal index


def test_hilbert_index_volume_upsamples():
    vol = neuro.hilbert_index_volume(2, upsample=2)
    assert vol.shape == (8, 8, 8)  # (2**2) * 2


def test_nifti_roundtrip(tmp_path):
    nib = pytest.importorskip("nibabel")
    out = neuro.write_neuro(str(tmp_path / "b.nii.gz"), "nii", order=3,
                            voxel_size=2.0)[0]
    img = nib.load(out)
    assert img.shape == (8, 8, 8)
    assert np.allclose(np.diag(img.affine)[:3], 2.0)


def test_nifti_requires_order(tmp_path):
    pytest.importorskip("nibabel")
    with pytest.raises(ValueError):
        neuro.write_neuro(str(tmp_path / "b.nii.gz"), "nii", order=None)


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------
def test_path_graph_is_a_chain(skeleton):
    nx = pytest.importorskip("networkx")
    pts, _ = skeleton
    G = neuro.path_to_graph(pts)
    assert G.number_of_nodes() == len(pts)
    assert G.number_of_edges() == len(pts) - 1          # unbranched chain
    assert all(k in G.nodes[0] for k in ("x", "y", "z"))
    assert {d["kind"] for _, _, d in G.edges(data=True)} == {"path"}


def test_knn_adds_spatial_edges(skeleton):
    pytest.importorskip("networkx")
    pytest.importorskip("scipy")
    pts, _ = skeleton
    chain = neuro.path_to_graph(pts).number_of_edges()
    G = neuro.path_to_graph(pts, knn=4)
    assert G.number_of_edges() > chain
    assert "spatial" in {d["kind"] for _, _, d in G.edges(data=True)}


@pytest.mark.parametrize("fmt,reader", [
    ("graphml", "read_graphml"), ("gexf", "read_gexf"),
])
def test_graph_roundtrip(skeleton, tmp_path, fmt, reader):
    nx = pytest.importorskip("networkx")
    pts, _ = skeleton
    out = neuro.write_neuro(str(tmp_path / f"b.{fmt}"), fmt, centerline=pts)[0]
    G = getattr(nx, reader)(out)
    assert G.number_of_nodes() == len(pts)


def test_graph_requires_centerline(tmp_path):
    pytest.importorskip("networkx")
    with pytest.raises(ValueError):
        neuro.write_neuro(str(tmp_path / "b.graphml"), "graphml", centerline=None)
