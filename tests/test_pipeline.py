"""End-to-end smoke test: run the real pipeline at small scale and export
each format. Catches integration breakage that unit tests on fixtures miss.
"""

import os

import pytest

pytest.importorskip("pyvista")

import exporters
import hilbert_gen


def _tiny_cfg(**overrides):
    cfg = dict(hilbert_gen.BASE)
    cfg.update(order=2, spline=400, decimate=0.3, n_sides=12)
    cfg.update(overrides)
    return cfg


def test_generate_returns_mesh_centerline_radius():
    mesh, cl, radius = hilbert_gen.generate(_tiny_cfg())
    assert mesh.n_points > 0 and mesh.n_cells > 0
    assert len(cl) == len(radius) == 400


@pytest.mark.parametrize("fmt", ["stl", "ply", "3mf", "swc"])
def test_pipeline_exports_each_core_format(fmt, tmp_path):
    mesh, cl, radius = hilbert_gen.generate(_tiny_cfg())
    out = exporters.write(mesh, cl, radius, str(tmp_path / "out"), fmt=fmt)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 0
    assert out.endswith("." + fmt)


@pytest.mark.parametrize("fmt", ["glb", "gltf"])
def test_pipeline_exports_gltf_formats(fmt, tmp_path):
    pytest.importorskip("trimesh")
    mesh, cl, radius = hilbert_gen.generate(_tiny_cfg())
    out = exporters.write(mesh, cl, radius, str(tmp_path / "out"), fmt=fmt)
    assert os.path.getsize(out) > 0


def test_buckle_mode_pipeline_runs(tmp_path):
    # exercises the ellipsoid + ventricle + buckle path (the gyri3 branch)
    cfg = _tiny_cfg(spline=600, decimate=0.0, growth_mode="buckle",
                    ellipsoid=(2.0, 1.3, 1.0), ventricle=True, noise_amp=0.0)
    mesh, cl, radius = hilbert_gen.generate(cfg)
    assert mesh.n_points > 0
