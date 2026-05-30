"""Tests for the FEM / morphoelastic scaffolding.

Tetrahedralisation needs tetgen; the mesh formats need meshio. Each test skips
cleanly when its optional dependency is missing, so the rest of the suite is
unaffected.
"""

import xml.etree.ElementTree as ET

import numpy as np
import pytest

pv = pytest.importorskip("pyvista")

import morphoelastic as me


@pytest.fixture(scope="module")
def closed_surface():
    """A watertight surface tetgen can mesh directly."""
    return pv.Sphere(theta_resolution=16, phi_resolution=16).triangulate()


@pytest.fixture(scope="module")
def volume(closed_surface):
    tetgen = pytest.importorskip("tetgen")  # noqa: F841
    return me.tetrahedralize(closed_surface)


# ---------------------------------------------------------------------------
# resolve()
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("path,expect", [
    ("v.msh", "msh"), ("v.inp", "inp"), ("v.vtu", "vtu"), ("v.feb", "feb"),
    ("v.stl", "vtu"),  # non-FEM extension -> default vtu
])
def test_resolve_infers_fem_format(path, expect):
    _, fmt = me.resolve(path, None)
    assert fmt == expect


def test_resolve_override_and_unknown():
    assert me.resolve("v.vtu", "feb")[0].endswith(".feb")
    with pytest.raises(ValueError):
        me.resolve("v.x", "x")


# ---------------------------------------------------------------------------
# tetrahedralisation
# ---------------------------------------------------------------------------
def test_tetrahedralize_produces_tets(volume):
    assert volume.n_cells > 0
    assert me.VTK_TETRA in volume.cells_dict


# ---------------------------------------------------------------------------
# growth field (the physically meaningful part)
# ---------------------------------------------------------------------------
def test_growth_field_ramps_from_core_to_surface(volume, closed_surface):
    rate = 1.5
    vol = me.cortical_growth_field(volume, closed_surface,
                                   cortical_thickness=0.2, growth_rate=rate)
    g = np.asarray(vol.point_data["growth"])
    depth = np.asarray(vol.point_data["depth"])

    # bounded between no-growth and the target rate
    assert g.min() >= 1.0 - 1e-6
    assert g.max() <= rate + 1e-6

    # surface (shallow) grows more than the core (deep). Most tet nodes lie on
    # the surface (depth 0), so split by rank rather than percentile value.
    order = np.argsort(depth)
    k = max(1, len(depth) // 10)
    shallow = g[order[:k]].mean()
    deep = g[order[-k:]].mean()
    assert shallow > deep

    # per-element field is attached too
    assert "growth" in vol.cell_data
    assert len(vol.cell_data["growth"]) == vol.n_cells


# ---------------------------------------------------------------------------
# exporters: meshio formats round-trip with the field intact
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("fmt", ["vtu", "msh"])
def test_meshio_volume_roundtrip(volume, closed_surface, fmt, tmp_path):
    meshio = pytest.importorskip("meshio")
    vol = me.cortical_growth_field(volume, closed_surface,
                                   cortical_thickness=0.2, growth_rate=1.5)
    out = me.write_volume(vol, str(tmp_path / "v"), fmt=fmt)
    m = meshio.read(out)
    ntet = sum(len(c.data) for c in m.cells if c.type == "tetra")
    assert ntet == vol.n_cells
    assert len(m.points) == vol.n_points
    assert "growth" in (m.point_data or {})


def test_abaqus_inp_writes_geometry(volume, tmp_path):
    meshio = pytest.importorskip("meshio")
    out = me.write_volume(volume, str(tmp_path / "v"), fmt="inp")
    m = meshio.read(out)
    ntet = sum(len(c.data) for c in m.cells if c.type == "tetra")
    assert ntet == volume.n_cells  # geometry preserved (meshio .inp drops point_data)


# ---------------------------------------------------------------------------
# FEBio .feb: well-formed XML with geometry + growth field
# ---------------------------------------------------------------------------
def test_feb_is_wellformed_with_growth(volume, closed_surface, tmp_path):
    vol = me.cortical_growth_field(volume, closed_surface,
                                   cortical_thickness=0.2, growth_rate=1.5)
    out = me.write_volume(vol, str(tmp_path / "v.feb"))
    root = ET.parse(out).getroot()  # raises if malformed

    assert root.tag.endswith("febio_spec")
    assert len(root.findall(".//{*}Nodes/{*}node")) == vol.n_points
    elems = root.findall(".//{*}Elements/{*}elem")
    assert len(elems) == vol.n_cells
    growth = root.findall(".//{*}MeshData/{*}ElementData/{*}e")
    assert len(growth) == vol.n_cells

    # FEBio is 1-based; no zero node id should appear in connectivity
    first = [int(x) for x in elems[0].text.split(",")]
    assert min(first) >= 1


def test_feb_marks_itself_a_scaffold(volume, tmp_path):
    out = me.write_volume(volume, str(tmp_path / "v.feb"))
    text = open(out).read().lower()
    assert "scaffold" in text and "stub" in text


# ---------------------------------------------------------------------------
# end-to-end convenience
# ---------------------------------------------------------------------------
def test_surface_to_fem_one_call(closed_surface, tmp_path):
    pytest.importorskip("tetgen")
    pytest.importorskip("meshio")
    out, vol = me.surface_to_fem(closed_surface, str(tmp_path / "brain.vtu"),
                                 cortical_thickness=0.2, growth_rate=1.4)
    assert out.endswith(".vtu")
    assert vol.n_cells > 0
    assert "growth" in vol.cell_data
