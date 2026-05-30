"""Tests for the provenance layer: records, flattening, sidecars, PLY embedding,
and -- the headline guarantee -- exact regeneration from a sidecar.
"""

import json
import os

import numpy as np
import pytest

import provenance as prov


SAMPLE_CFG = {
    "order": 3, "spline": 1500, "seed": 42, "k1": 7, "wobble": 0.15,
    "ellipsoid": (2.0, 1.3, 1.0), "ventricle": True, "output": "b.stl",
    "preview": True,
}


# ---------------------------------------------------------------------------
# record / flatten
# ---------------------------------------------------------------------------
def test_build_record_has_full_config_and_metadata():
    rec = prov.build_record(SAMPLE_CFG, command="hilbert_gen.py --preset gyri")
    assert rec["tool"] == prov.TOOL
    assert rec["version"] == prov.VERSION
    assert "git" in rec and "created" in rec
    assert rec["command"].startswith("hilbert_gen.py")
    # the entire config is captured, with tuples made JSON-safe
    assert rec["config"]["seed"] == 42
    assert rec["config"]["ellipsoid"] == [2.0, 1.3, 1.0]


def test_flatten_includes_full_record_json():
    rec = prov.build_record(SAMPLE_CFG)
    flat = prov.flatten(rec)
    assert set(flat) >= {"tool", "version", "git", "created", "provenance_json"}
    # the one field round-trips to the whole record
    reconstructed = json.loads(flat["provenance_json"])
    assert reconstructed["config"]["order"] == 3


def test_record_is_json_serialisable():
    rec = prov.build_record(SAMPLE_CFG)
    json.loads(prov.to_json(rec))            # must not raise


def test_config_from_record_disables_preview():
    rec = prov.build_record(SAMPLE_CFG)
    cfg = prov.config_from_record(rec)
    assert cfg["preview"] is False           # never pop a window on regen
    assert cfg["seed"] == 42


# ---------------------------------------------------------------------------
# sidecar
# ---------------------------------------------------------------------------
def test_sidecar_roundtrip(tmp_path):
    rec = prov.build_record(SAMPLE_CFG)
    out = str(tmp_path / "brain.stl")
    side = prov.write_sidecar(out, rec)
    assert side == out + prov.SIDECAR_SUFFIX
    assert os.path.exists(side)
    # load by sidecar path, and by the output path (which finds the sidecar)
    assert prov.load(side)["config"]["seed"] == 42
    assert prov.load(out)["config"]["seed"] == 42


# ---------------------------------------------------------------------------
# PLY embedding
# ---------------------------------------------------------------------------
def test_embed_ply_comments_preserves_mesh(tmp_path):
    pv = pytest.importorskip("pyvista")
    mesh = pv.Sphere(theta_resolution=12, phi_resolution=12).triangulate()
    path = str(tmp_path / "m.ply")
    mesh.save(path)
    n_before = pv.read(path).n_points

    prov.embed_ply_comments(path, prov.build_record(SAMPLE_CFG))

    header = open(path, "rb").read(4000).decode("latin1")
    assert "comment provenance" in header
    assert "comment git" in header
    # binary data intact -> still readable, same vertex count
    assert pv.read(path).n_points == n_before


# ---------------------------------------------------------------------------
# end-to-end: regenerate exactly from a sidecar
# ---------------------------------------------------------------------------
def test_regeneration_is_bit_identical(tmp_path):
    pv = pytest.importorskip("pyvista")
    import hilbert_gen

    orig = str(tmp_path / "orig.ply")
    assert hilbert_gen.main(
        ["--preset", "gyri", "--order", "2", "--spline", "400",
         "--decimate", "0.3", "-o", orig]) == 0
    side = orig + prov.SIDECAR_SUFFIX
    assert os.path.exists(side)

    regen = str(tmp_path / "regen.ply")
    assert hilbert_gen.main(["--from-provenance", side, "-o", regen]) == 0

    a, b = pv.read(orig), pv.read(regen)
    assert a.n_points == b.n_points
    assert np.array_equal(a.points, b.points)   # exact reproduction


def test_provenance_none_writes_no_sidecar(tmp_path):
    pytest.importorskip("pyvista")
    import hilbert_gen
    out = str(tmp_path / "n.ply")
    assert hilbert_gen.main(
        ["--preset", "gyri", "--order", "2", "--spline", "400",
         "--provenance", "none", "-o", out]) == 0
    assert not os.path.exists(out + prov.SIDECAR_SUFFIX)
