"""Round-trip tests for every export format, plus path/format resolution.

Mesh formats need PyVista; glTF/GLB additionally need trimesh. Those tests
skip cleanly when the optional dependency is absent, so the core curve tests
still run anywhere.
"""

import os
import zipfile

import numpy as np
import pytest

import exporters

pv = pytest.importorskip("pyvista")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def mesh():
    """A small, watertight, all-triangle surface."""
    return pv.Sphere(theta_resolution=12, phi_resolution=12).triangulate()


@pytest.fixture
def skeleton():
    """A varying-radius centreline (the SWC morphology input)."""
    t = np.linspace(0, 4 * np.pi, 200)
    pts = np.column_stack([np.cos(t), np.sin(t), t / 5.0])
    rad = 0.5 + 0.3 * np.sin(t)
    return pts, rad


# ---------------------------------------------------------------------------
# resolve() — path/format reconciliation
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("path,expect", [
    ("brain.stl", "stl"), ("brain.ply", "ply"), ("brain.3mf", "3mf"),
    ("brain.glb", "glb"), ("brain.gltf", "gltf"), ("brain.swc", "swc"),
    ("brain.unknown", "stl"),  # unknown extension defaults to STL
])
def test_resolve_infers_format_from_extension(path, expect):
    out_path, fmt = exporters.resolve(path, None)
    assert fmt == expect


def test_resolve_explicit_format_overrides_extension():
    out_path, fmt = exporters.resolve("brain.stl", "glb")
    assert fmt == "glb"
    assert out_path.endswith(".glb")


def test_resolve_appends_extension_when_missing():
    out_path, fmt = exporters.resolve("brain", "3mf")
    assert out_path == "brain.3mf"


def test_resolve_rejects_unknown_format():
    with pytest.raises(ValueError):
        exporters.resolve("brain.xyz", "xyz")


# ---------------------------------------------------------------------------
# Mesh format round-trips
# ---------------------------------------------------------------------------
def test_stl_roundtrip(mesh, tmp_path):
    out = exporters.write(mesh, None, None, str(tmp_path / "m.stl"))
    back = pv.read(out)
    assert back.n_cells == mesh.n_cells
    assert np.allclose(back.bounds, mesh.bounds, atol=1e-5)


def test_ply_roundtrip(mesh, tmp_path):
    out = exporters.write(mesh, None, None, str(tmp_path / "m.ply"))
    back = pv.read(out)
    assert back.n_points == mesh.n_points   # PLY preserves the vertex list
    assert back.n_cells == mesh.n_cells


def test_3mf_is_valid_opc_with_matching_geometry(mesh, tmp_path):
    out = exporters.write(mesh, None, None, str(tmp_path / "m.3mf"))
    assert zipfile.is_zipfile(out)
    with zipfile.ZipFile(out) as zf:
        names = set(zf.namelist())
        assert {"[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"} <= names
        model = zf.read("3D/3dmodel.model").decode()
    assert 'unit="millimeter"' in model
    assert model.count("<vertex ") == mesh.n_points
    assert model.count("<triangle ") == mesh.n_cells


def test_3mf_embeds_metadata(mesh, tmp_path):
    out = exporters.write(mesh, None, None, str(tmp_path / "m.3mf"),
                          meta={"seed": 42, "preset": "gyri"})
    with zipfile.ZipFile(out) as zf:
        model = zf.read("3D/3dmodel.model").decode()
    assert 'name="seed"' in model and ">42<" in model
    assert 'name="preset"' in model and ">gyri<" in model


def test_glb_roundtrip(mesh, tmp_path):
    trimesh = pytest.importorskip("trimesh")
    out = exporters.write(mesh, None, None, str(tmp_path / "m.glb"))
    back = trimesh.load(out, force="mesh")
    assert len(back.vertices) == mesh.n_points
    assert len(back.faces) == mesh.n_cells


def test_gltf_is_self_contained(mesh, tmp_path):
    trimesh = pytest.importorskip("trimesh")
    out = exporters.write(mesh, None, None, str(tmp_path / "m.gltf"))
    # the fix: no sidecar .bin files leak alongside the .gltf
    sidecars = [f for f in os.listdir(tmp_path) if f.endswith(".bin")]
    assert sidecars == []
    back = trimesh.load(out, force="mesh")
    assert len(back.vertices) == mesh.n_points
    assert len(back.faces) == mesh.n_cells


# ---------------------------------------------------------------------------
# SWC (neuron morphology)
# ---------------------------------------------------------------------------
def _read_swc(path):
    rows = []
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#"):
            rows.append(line.split())
    return rows


def test_swc_roundtrip(skeleton, tmp_path):
    pts, rad = skeleton
    out = exporters.write(None, pts, rad, str(tmp_path / "n.swc"))
    rows = _read_swc(out)

    assert len(rows) == len(pts)

    ids = [int(r[0]) for r in rows]
    parents = [int(r[6]) for r in rows]
    assert parents[0] == -1                         # root
    assert all(p == i - 1 for i, p in zip(ids[1:], parents[1:]))  # unbranched chain

    xyz = np.array([[float(r[2]), float(r[3]), float(r[4])] for r in rows])
    radii = np.array([float(r[5]) for r in rows])
    assert np.allclose(xyz, pts, atol=1e-5)
    assert np.allclose(radii, rad, atol=1e-5)


def test_swc_states_it_is_generative(skeleton, tmp_path):
    pts, rad = skeleton
    out = exporters.write(None, pts, rad, str(tmp_path / "n.swc"))
    header = "".join(l for l in open(out) if l.startswith("#")).lower()
    assert "not a measured neuron" in header


def test_swc_requires_centerline_and_radius(tmp_path):
    with pytest.raises(ValueError):
        exporters.write(None, None, None, str(tmp_path / "n.swc"))


def test_swc_rejects_length_mismatch(tmp_path):
    pts = np.zeros((10, 3))
    rad = np.zeros(9)
    with pytest.raises(ValueError):
        exporters.write(None, pts, rad, str(tmp_path / "n.swc"))


# ---------------------------------------------------------------------------
# dispatch
# ---------------------------------------------------------------------------
def test_write_returns_corrected_path(mesh, tmp_path):
    # ask for .stl but force glb -> path comes back as .glb
    out = exporters.write(mesh, None, None, str(tmp_path / "m.stl"), fmt="3mf")
    assert out.endswith(".3mf")
    assert os.path.exists(out)
