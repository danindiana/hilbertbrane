# Visual Consistency Testing in Hilbertbrane — An Open Problem

## Status: Open Engineering Challenge

Hilbertbrane is a **generative** system: its outputs (STL meshes, PNG screenshots,
Graphviz diagrams) are produced by stochastic and numerically sensitive pipelines.
This makes automated quality assurance substantially harder than for deterministic
software. This document maps the problem space, identifies what is tractable today,
and characterizes what remains unsolved.

---

## 1. The Problem

Generative mesh quality is multi-dimensional. A single "pass/fail" criterion does
not capture whether a Hilbertbrane output is correct. Four independent quality
axes exist:

| Axis | Definition | Why it matters |
|------|-----------|----------------|
| **Geometric validity** | No open edges, no degenerate faces, finite bounding box | Required for 3D printing and physics simulation |
| **Parametric reproducibility** | Same config + seed → same STL, across runs and platforms | Enables regression testing and reproducible publications |
| **Biological plausibility** | Folding frequency, sulcal depth, gyrification index within human ranges | Scientific credibility of the model |
| **Render consistency** | Same mesh → same screenshot pixels, across GPU drivers and OS versions | Reproducible documentation and CI artifacts |

The repo currently has **zero automated tests**. All four axes are validated
manually by visual inspection.

---

## 2. What We Can Test Today

The following tests are **implementable now** with existing dependencies
(`pyvista`, `PIL/Pillow`, `hashlib`, `os`).

### 2.1 Mesh Geometric Validity

```python
# tests/test_mesh_quality.py
import pyvista as pv
import pytest, subprocess, os

@pytest.fixture(scope="module")
def brain_mesh():
    # Generate a small test mesh (Order 3, fast)
    subprocess.run(["python", "HilbertGyri.py"], check=True, timeout=120)
    return pv.read("HilbertGyri.stl")

def test_watertight(brain_mesh):
    assert brain_mesh.n_open_edges == 0, \
        f"Mesh has {brain_mesh.n_open_edges} open edges — not watertight"

def test_bounding_box_reasonable(brain_mesh):
    bounds = brain_mesh.bounds   # (xmin, xmax, ymin, ymax, zmin, zmax)
    extent_x = bounds[1] - bounds[0]
    assert 5.0 < extent_x < 200.0, f"X-extent {extent_x} is outside expected range"

def test_poly_count_in_range(brain_mesh):
    n = brain_mesh.n_cells
    # Order 3 after decimation: expect 10k–200k
    assert 10_000 < n < 200_000, f"Cell count {n} is outside expected range"

def test_no_nan_vertices(brain_mesh):
    import numpy as np
    assert not np.any(np.isnan(brain_mesh.points)), "NaN vertices detected"

def test_stl_exists_and_nonzero():
    size = os.path.getsize("HilbertGyri.stl")
    assert size > 100_000, f"STL too small ({size} bytes) — likely empty"
```

### 2.2 Parametric Hash (Fixed-Seed Regression)

Binary STL output is deterministic when all random seeds are fixed. A SHA-256 hash
of the STL file provides a tight regression anchor:

```python
import hashlib, subprocess

def stl_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

# Generate baseline once:
# BASELINE = stl_sha256("HilbertGyri.stl")   → store in tests/baselines.json

def test_parametric_hash_stable():
    import json, pathlib
    baseline = json.loads(
        pathlib.Path("tests/baselines.json").read_text()
    )["HilbertGyri.stl"]
    current = stl_sha256("HilbertGyri.stl")
    assert current == baseline, \
        "STL hash changed — pipeline output is no longer reproducible. " \
        "If this is intentional, update tests/baselines.json."
```

**Caveat:** Hash tests are only reliable on the same platform + library versions
(see Section 3.4).

### 2.3 Gyrification Index

The Gyrification Index (GI) measures folding complexity as the ratio of total
surface area to convex hull area. Human adult cortex: GI ≈ 2.3–3.0 (Zilles et al.,
1988). A Hilbertbrane mesh with `order=4, sulcus_scale=0.6` should fall in roughly
the same range.

```python
from scipy.spatial import ConvexHull
import pyvista as pv, numpy as np

def gyrification_index(mesh: pv.PolyData) -> float:
    hull = ConvexHull(mesh.points)
    return mesh.area / hull.area

def test_gyrification_index_plausible(brain_mesh):
    gi = gyrification_index(brain_mesh)
    assert 1.2 < gi < 4.0, \
        f"GI={gi:.2f} — outside plausible biological range (1.2–4.0)"
```

### 2.4 Diagram PNG Sanity Checks

```python
# tests/test_diagram_output.py
import os
from PIL import Image
import numpy as np
import glob

DIAGRAM_DIR = "docs/diagrams_25"

@pytest.mark.parametrize("path", glob.glob(f"{DIAGRAM_DIR}/*.png"))
def test_diagram_not_empty(path):
    size = os.path.getsize(path)
    assert size > 50_000, f"{path}: PNG too small ({size} bytes) — likely blank"

@pytest.mark.parametrize("path", glob.glob(f"{DIAGRAM_DIR}/*.png"))
def test_diagram_not_all_black(path):
    img = np.array(Image.open(path).convert("RGB"), dtype=float)
    mean_brightness = img.mean()
    # Dark-theme diagrams are dark but not fully black
    assert mean_brightness > 8.0, \
        f"{path}: mean pixel value {mean_brightness:.1f} — image appears blank"

@pytest.mark.parametrize("path", glob.glob(f"{DIAGRAM_DIR}/*.png"))
def test_diagram_has_expected_size(path):
    img = Image.open(path)
    w, h = img.size
    assert w > 400 and h > 200, \
        f"{path}: image too small ({w}×{h}) — render may have failed"
```

### 2.5 Proposed Test Suite Structure

```
tests/
├── baselines.json              ← SHA-256 hashes for fixed-seed STL outputs
├── conftest.py                 ← shared fixtures (generate mesh once per session)
├── test_mesh_quality.py        ← watertightness, bounds, poly count, GI
├── test_parametric_hash.py     ← regression: same params → same STL
└── test_diagram_output.py      ← PNG size, brightness, resolution
```

Run with: `pytest tests/ -v --timeout=300`

---

## 3. What Remains Unsolved

### 3.1 Cross-Version Pixel Determinism

**Problem:** PyVista/VTK renders to an OpenGL framebuffer. The exact pixel values
depend on the GPU driver, anti-aliasing mode, Mesa/NVIDIA software version, and
screen DPI. The same mesh can produce screenshots that differ by 1–10 pixel values
on different machines, making tight pixel-diff comparisons unreliable.

**Current state:** No known general solution for GPU-rendered generative art.
Screenshot tests require a large tolerance (SSIM > 0.90) that misses real
regressions, or a tight tolerance (pixel diff < 5) that produces constant false
positives in CI.

**Possible mitigations:**
- Use `off_screen=True` with a software Mesa rasterizer (deterministic, but slow)
- Store screenshots as perceptual hashes (pHash) rather than pixel arrays; compare
  pHash Hamming distance < threshold
- Pin exact OS + GPU + driver version in a Docker container for CI

**Open question:** Is perceptual hashing (pHash/dHash) a sufficient proxy for
"visually correct" for scientific visualization outputs?

---

### 3.2 Biological Plausibility Scoring

**Problem:** No single metric captures "this looks like a real brain cortex."
The gyrification index (Section 2.3) is necessary but not sufficient:
- A smooth sphere with no folds can have GI = 1.0 (wrong)
- A random noise surface can have GI = 2.5 (coincidentally correct GI, wrong morphology)

**Candidate additional metrics from the neuroimaging literature:**

| Metric | Definition | Human range | Status |
|--------|-----------|-------------|--------|
| Gyrification Index (GI) | pial area / convex hull area | 2.3–3.0 | Implementable (Section 2.3) |
| Sulcal depth distribution | Mean and std of sulcus depth along geodesics | mean ≈ 10 mm | Requires surface geodesics |
| Fractal dimension of sulcal pattern | Box-counting dimension of sulcal outline | 1.5–1.7 | Implementable with skimage |
| Mean curvature distribution | Distribution of principal curvatures | peaks at ±0.1/mm | Implementable via PyVista |
| Power spectrum of folding | Spatial frequency content of curvature map | peak at 10–20 mm | Requires FFT on surface |

**Open question:** Which combination of metrics provides a necessary and sufficient
test for "biologically plausible cortical folding"? This is an active research
question in computational neuroanatomy.

---

### 3.3 Self-Intersection Detection at Scale

**Problem:** When `ridge_radius > cell_spacing / 2`, the extruded tube faces
intersect themselves. This produces meshes that are formally "closed" (no open
edges) but have internal voids and incorrect geometry for physics simulation.

`mesh.is_all_triangles` and `mesh.n_open_edges == 0` do **not** catch internal
self-intersections.

**Correct test:** cast a ray from every face center along its normal; if the ray
hits another face of the same mesh within distance `2 * ridge_radius`, a
self-intersection exists.

**Complexity:** O(N × M) where N = number of test rays, M = total face count.
For a 300k-face mesh, this is ~10¹¹ operations — prohibitively slow without
acceleration.

**Possible solutions:**
- BVH (Bounding Volume Hierarchy) ray-casting — PyVista supports this via VTK's
  `vtkOBBTree`, but the API is not exposed at the Python level
- Sample a random 1% of faces and run ray-casting on the sample (probabilistic test)
- Use `trimesh.is_watertight` + `trimesh.is_volume` as a proxy (catches most but
  not all self-intersections)

**Open question:** What is the minimum sampling rate for a probabilistic
self-intersection test to have 95% power at detecting the intersection density
typical of `ridge_radius = 0.8 * cell_spacing`?

---

### 3.4 Cross-Platform STL Reproducibility

**Problem:** The spline interpolation in `pv.Spline(path, N_SAMPLES)` calls VTK's
`vtkParametricSpline`. VTK's floating-point arithmetic is **not** guaranteed
bitwise-identical across:
- x86 vs ARM (different FPU rounding)
- Different numpy builds (OpenBLAS vs MKL)
- Different VTK versions (9.2 vs 9.3 changed spline solver internals)

A parametric hash test (Section 2.2) that passes on the developer's machine
may fail in CI on a different architecture.

**Possible mitigations:**
- Use a tolerance-based comparison: assert that vertex coordinates match to within
  `1e-4` mm rather than exact binary equality
- Pin exact VTK version in `requirements.txt` (`vtk==9.6.2`)
- Use a platform-independent checksum of mesh topology (connectivity graph hash)
  rather than vertex coordinates

**Open question:** What tolerance on vertex coordinates is perceptually invisible
in rendered outputs, and therefore "safe" for regression testing?

---

### 3.5 Perceptual Visual Consistency of Graphviz Diagrams

**Problem:** The 25 Graphviz diagrams are generated from `.dot` source files using
`dot -Tpng`. The same `.dot` file can produce different edge routing on different
Graphviz versions (2.42 vs 2.43 changed the orthogonal spline router). Text
anti-aliasing also differs by platform (Cairo backend on Linux vs quartz on macOS).

**The core tension:**

| Test corpus | Pros | Cons |
|------------|------|------|
| DOT source files | Version-controlled, platform-independent, fully verifiable | Does not test the rendered PNG (what users actually see) |
| PNG files | Tests actual visual output | Platform-dependent; brittle across Graphviz/Cairo versions |

**Current approach:** The `.dot` files are committed to git alongside the `.png`
files. A change to `.dot` structure (new node, edge, cluster) is visible in `git diff`.
PNG changes are binary blobs.

**Proposed test:** Parse the `.dot` files with `pydot` or regex, verify that each
diagram has ≥ 6 nodes, ≥ 3 edges, and a `label` attribute matching the expected
diagram name. This tests structural completeness without pixel comparison.

```python
def test_dot_structural_completeness():
    import pydot, glob
    for dot_path in glob.glob("docs/diagrams_25/*.dot"):
        graphs = pydot.graph_from_dot_file(dot_path)
        g = graphs[0]
        n_nodes = len(g.get_nodes())
        n_edges = len(g.get_edges())
        assert n_nodes >= 6, f"{dot_path}: only {n_nodes} nodes"
        assert n_edges >= 3, f"{dot_path}: only {n_edges} edges"
```

**Open question:** Is DOT structural testing sufficient as a proxy for
"visually meaningful diagram," or do we need rendered PNG comparison?

---

## 4. Recommended First Steps

If you want to add testing to this project, prioritize in this order:

1. **[Easy, high value]** Add `tests/test_diagram_output.py` — PNG file size + mean brightness. No new dependencies. Catches blank renders and failed `dot` compilation.
2. **[Medium, high value]** Add `tests/test_mesh_quality.py` — watertightness + bounding box. Requires `pyvista` (already installed). Catches the most common pipeline failures.
3. **[Medium, medium value]** Add gyrification index test. Requires `scipy` (`ConvexHull`). Provides biological plausibility anchor.
4. **[Hard, medium value]** Parametric hash baseline. Run once, commit `baselines.json`, maintain carefully.
5. **[Research, open]** Cross-platform pixel determinism — no clear solution yet.

---

## References

- Zilles et al. (1988). *The human pattern of gyrification in the cerebral cortex.*
  Anatomy and Embryology.
- Tallinen et al. (2016). *On the growth and form of cortical convolutions.*
  Nature Physics.
- Pearson (1993). *Complex patterns in a simple system.* Science.
- Prusinkiewicz & Lindenmayer (1990). *The Algorithmic Beauty of Plants.* Springer.
- Wang et al. (2004). *Image quality assessment: from error visibility to structural
  similarity.* IEEE TIP. (SSIM metric)
