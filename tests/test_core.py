"""Property tests for the pure-math core (no PyVista needed)."""

import numpy as np
import pytest

import hilbert_core as hc


# ---------------------------------------------------------------------------
# The headline guard: this is what broke in the original repo.
# A real Hilbert curve is locality-preserving -- consecutive indices map to
# face-adjacent cells (Manhattan distance exactly 1) and every cell is visited
# once. A Gray-code interleave (the old bug) fails both.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("order", [2, 3, 4])
def test_hilbert_curve_is_locality_preserving(order):
    path = hc.build_hilbert_path(order)
    n = (1 << order) ** 3

    assert path.shape == (n, 3)

    # every consecutive pair is face-adjacent
    steps = np.abs(np.diff(path, axis=0)).sum(axis=1)
    assert np.all(steps == 1), f"order {order}: {(steps != 1).sum()} non-adjacent steps"

    # the curve is a bijection onto the grid (no repeats, no gaps)
    assert len({tuple(row) for row in path}) == n


@pytest.mark.parametrize("order", [2, 3])
def test_hilbert_point_stays_in_bounds(order):
    side = 1 << order
    for h in range(side ** 3):
        x, y, z = hc.hilbert_point(h, order)
        assert 0 <= x < side and 0 <= y < side and 0 <= z < side


def test_build_path_is_deterministic():
    assert np.array_equal(hc.build_hilbert_path(3), hc.build_hilbert_path(3))


# ---------------------------------------------------------------------------
# Field / geometry invariants
# ---------------------------------------------------------------------------
def test_pinch_field_is_bounded():
    t = np.linspace(0, 1, 1000)
    p = hc.pinch_field(t, seed=7)
    assert p.min() >= 0.0 - 1e-9
    assert p.max() <= 1.0 + 1e-9


def test_pinch_field_is_reproducible_per_seed():
    t = np.linspace(0, 1, 500)
    assert np.allclose(hc.pinch_field(t, seed=42), hc.pinch_field(t, seed=42))
    assert not np.allclose(hc.pinch_field(t, seed=1), hc.pinch_field(t, seed=2))


def test_normalize_path_maps_into_unit_cube():
    u = hc.normalize_path(hc.build_hilbert_path(3), 3)
    assert u.min() >= 0.0 and u.max() <= 1.0
    assert np.isclose(u.max(), 1.0)  # the far corner reaches 1


def test_arclength_is_monotonic_and_normalised():
    pts = hc.build_hilbert_path(3)
    t = hc.arclength_t(pts)
    assert t[0] == 0.0
    assert np.isclose(t[-1], 1.0)
    assert np.all(np.diff(t) >= 0)


def test_map_to_ellipsoid_is_centred_and_scaled():
    u = hc.normalize_path(hc.build_hilbert_path(3), 3)
    e = hc.map_to_ellipsoid(u, (2.0, 1.3, 1.0), occipital_drop=0.0)
    # centred on origin in X/Y, stretched to the requested half-extents
    assert abs(e[:, 0].mean()) < 0.2
    assert np.isclose(np.ptp(e[:, 0]), 2.0, atol=1e-6)
    assert np.isclose(np.ptp(e[:, 1]), 1.3, atol=1e-6)


def test_ventricle_mask_thins_the_bottom():
    # the mask scales the pinch field, so a HIGHER value means MORE thinning;
    # the ventricle proxy puts that thinning low in the volume.
    pts = hc.build_hilbert_path(3)
    m = hc.ventricle_mask(pts)
    z = pts[:, 2]
    lower = m[z < np.median(z)].mean()
    upper = m[z > np.median(z)].mean()
    assert lower > upper  # stronger pinch (more thinning) at the bottom
