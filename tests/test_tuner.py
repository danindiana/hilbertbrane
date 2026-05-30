"""Tests for the browser tuner.

Geometry tests need PyVista; the app-construction test additionally needs
trame. Both skip cleanly when the dependency is absent. The trame server is
never *started* here -- we build the app and drive its callbacks directly, so
no browser or event loop is required.
"""

import os

import numpy as np
import pytest

pv = pytest.importorskip("pyvista")

import tuner_trame as tt


# ---------------------------------------------------------------------------
# config sanity
# ---------------------------------------------------------------------------
def test_every_control_has_a_default():
    assert set(tt.CONTROLS).issubset(tt.DEFAULTS)


# ---------------------------------------------------------------------------
# pure geometry
# ---------------------------------------------------------------------------
def test_build_mesh_produces_geometry():
    mesh, cl, r = tt.build_mesh(**tt.DEFAULTS)
    assert mesh.n_points > 0
    assert len(cl) == tt.DEFAULTS["spline"]
    assert len(r) == tt.DEFAULTS["spline"]


def test_build_mesh_respects_radius_clip():
    params = dict(tt.DEFAULTS, radius=2.0, sulcus=0.95)
    _, _, r = tt.build_mesh(**params)
    assert r.min() >= 2.0 * 0.1 - 1e-9
    assert r.max() <= 2.0 * 1.5 + 1e-9


def test_unit_path_is_cached_and_order_dependent():
    a = tt._cached_unit_path(3)
    assert a is tt._cached_unit_path(3)          # cache hit
    assert tt._cached_unit_path(4).shape[0] == (2 ** 4) ** 3


def test_tuner_uses_correct_hilbert_curve():
    # the cached path is the locality-preserving curve from hilbert_core
    import hilbert_core as hc
    path = hc.build_hilbert_path(3)
    steps = np.abs(np.diff(path, axis=0)).sum(axis=1)
    assert np.all(steps == 1)


# ---------------------------------------------------------------------------
# trame app (constructed, not served)
# ---------------------------------------------------------------------------
@pytest.fixture
def app():
    pytest.importorskip("trame")
    from trame.app import get_server
    return tt.build_app(get_server("pytest-tuner"))


def test_app_builds_with_defaults(app):
    assert app["state"].order == tt.DEFAULTS["order"]
    assert callable(app["ctrl"].view_update)
    assert app["plotter"] is not None


def test_rebuild_swaps_in_a_single_actor(app):
    app["state"].sulcus = 0.3
    app["rebuild"]()
    assert len(app["plotter"].actors) == 1   # old actor removed, one remains
    app["state"].sulcus = 0.6
    app["rebuild"]()
    assert len(app["plotter"].actors) == 1


def test_export_writes_a_file_via_exporters(app, tmp_path):
    out = str(tmp_path / "tuner.ply")
    app["state"].export_name = out
    app["export"]()
    assert os.path.exists(out)
    assert "saved" in app["state"].status
