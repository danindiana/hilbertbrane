# Hilbertbrane: Future Directions Roadmap

This document expands the five research tracks outlined in
[`docs/diagrams_25/25_future_work.dot`](../diagrams_25/25_future_work.dot) into
concrete milestones, technical dependencies, and relevant prior art. Tracks are
independent and can be pursued in any order; cross-track dependencies are noted
where they exist.

---

## Track 1 — Alternative Geometry Engines

**Goal:** Replace or augment the 3D Hilbert curve with other space-filling or
growth-process centerline generators, keeping the downstream tube-extrusion and
smoothing pipeline unchanged.

### 1.1 L-Systems (Lindenmayer)

Lindenmayer systems encode recursive branching grammars as string rewriting rules.
Applied here, the rewriting produces a 3D point sequence that substitutes for the
Hilbert path as the tube centerline.

**Example axiom for cortical branching:**
```
Axiom:  F
Rules:  F → F[+F][-F][^F][&F]
Angle:  22.5°
Depth:  5
```

Each `F` becomes a straight segment; `[+F]` branches right, `[-F]` left, `[^F]`
up, `[&F]` down. At recursion depth 5 the path visits 2⁵ = 32 branching points,
producing a dendritic 3D tree whose convex hull can be scaled to the
`[A-P: 2.0, L-R: 1.3, S-I: 1.0]` ellipsoid in `HilbertGyri3.py`.

**Implementation path:**
1. Write `lsystem.py` — string rewriter + turtle-geometry interpreter → `(N, 3)` numpy array
2. Feed the path array into the existing spline/tube pipeline unchanged
3. The sulcal pinch field `P(t)` still applies along arclength `t ∈ [0,1]`

**Prior art:** Prusinkiewicz & Lindenmayer, *The Algorithmic Beauty of Plants* (1990);
Shap (2001) 3D L-system visualization toolkits.

**Estimated effort:** 2–3 days. No new dependencies if turtle geometry is hand-coded.

---

### 1.2 Reaction-Diffusion (Gray-Scott Model)

The Gray-Scott reaction-diffusion system produces Turing instability patterns on
surfaces — spots, stripes, and labyrinths — that closely resemble the spontaneous
sulcal patterning seen in cortical development (Tallinen et al., 2016, *Nature Physics*).

**Mechanism:** Two coupled PDEs for concentrations U and V evolve on the mesh surface:
```
∂U/∂t = Du∇²U − UV² + f(1−U)
∂V/∂t = Dv∇²V + UV² − (f+k)V
```
where `f` (feed rate) and `k` (kill rate) control pattern type. For `f=0.037,
k=0.060`, the system produces labyrinthine stripes closely analogous to sulci.

**Application to Hilbertbrane:** Run the Gray-Scott system on the pre-tube PolyData
surface mesh for `N_steps` iterations. Use the resulting `V` concentration field
as a per-point replacement for the harmonic pinch field `P(t)`, directly modulating
tube radius. This generates aperiodic, biologically plausible folding patterns
without explicit harmonic frequency parameters.

**Prior art:** Pearson (1993), *Science*; Witkin & Kass (1991), *Computer Graphics*;
Tallinen et al. (2016), *Nature Physics* — cortical folding as mechanical instability.

**Implementation path:**
1. Write `reaction_diffusion.py` — Gray-Scott solver on a PyVista mesh surface
   using finite-difference Laplacian (6-neighbor averaging on triangulated mesh)
2. Return per-vertex V concentration as a numpy array matching `radius_profile` shape
3. Swap into `HilbertGyri3.py` in place of `pinch_field(t)`

**Estimated effort:** 3–5 days. Requires careful timestep control (explicit Euler
is stable for `dt ≤ 1/(4*max(Du,Dv)/(dx²))`).

---

### 1.3 Plugin API

Define a `CenterlineGenerator` abstract base class so geometry engines are
hot-swappable without modifying the tube-extrusion pipeline:

```python
from abc import ABC, abstractmethod
import numpy as np

class CenterlineGenerator(ABC):
    @abstractmethod
    def generate(self, **kwargs) -> np.ndarray:
        """Return (N, 3) float64 array of centerline points."""
        ...

class HilbertGenerator(CenterlineGenerator): ...
class LSystemGenerator(CenterlineGenerator): ...
class GrayScottGenerator(CenterlineGenerator): ...
```

---

## Track 2 — Temporal Evolution and Animation

**Goal:** Animate cortical growth — show how folding complexity increases from a
smooth sphere (Order 2, low sulcus depth) to a richly gyrified surface (Order 4,
high sulcus depth) — and export the animation for web and print use.

### 2.1 Parameterized Growth Timeline

Define a growth timeline as a curve through parameter space:

```python
TIMELINE = [
    # (t, order, ridge_radius, sulcus_scale, growth_factor)
    (0.00,  2, 3.5, 0.05, 1.00),   # fetal: smooth, lissencephalic
    (0.25,  3, 3.0, 0.20, 1.05),   # early gyrification
    (0.60,  3, 2.5, 0.45, 1.12),   # primary sulci established
    (0.85,  4, 2.2, 0.60, 1.18),   # secondary sulci
    (1.00,  4, 2.0, 0.72, 1.22),   # adult complexity
]
```

At each keyframe, generate the full mesh and save to a `.vtk` or `.stl` file.
Intermediate frames are interpolated by blending adjacent keyframe meshes in
vertex-space (requires consistent topology — same order must be used throughout,
or mesh registration must be applied).

### 2.2 Export Formats

| Format | Tool | Use case |
|--------|------|----------|
| VTK time series (`.pvd` + `.vtu`) | PyVista | ParaView visualization |
| glTF animation (`.glb`) | `pygltflib` or `trimesh` | Browser / Three.js |
| PNG frame sequence → WebM | `ffmpeg` | README / social media |
| PNG frame sequence → GIF | `convert` (ImageMagick) | README embedding |

### 2.3 Connection to Existing Infrastructure

`generate_logo.py` already uses matplotlib to render the Hilbert curve path with
neon glow. The same rendering infrastructure can produce animation frames:
render a 2D projection of the mesh at each growth stage → assemble with
`convert -delay 40 -loop 0 frame_*.png animation.gif`.

**Estimated effort:** 4–6 days for VTK series + GIF. Add 2–3 days for glTF.

---

## Track 3 — Multi-Subject Cortical Atlas

**Goal:** Given a collection of real or synthetic cortical surface meshes, compute a
mean shape and statistical shape model capturing inter-subject variability.

### 3.1 Alignment

All surfaces must be brought to a common spatial frame before averaging.
Two approaches:

- **Iterative Closest Point (ICP):** rigid registration; fast but loses local shape
  information. Suitable for aligning ellipsoid bounding boxes.
- **Spherical registration (FreeSurfer-style):** inflate each surface to a sphere,
  register spheres via spherical harmonics or gradient descent on vertex
  correspondence. More accurate but requires FreeSurfer or a custom sphere mapper.

For synthetic Hilbertbrane surfaces (all generated with the same ellipsoid
`[2.0, 1.3, 1.0]`), ICP on the convex hull is sufficient.

### 3.2 PCA Shape Model

After alignment, stack all N vertex coordinate arrays into a matrix
`X` of shape `(N_subjects, N_vertices * 3)`. PCA decomposes this into:

```
X_centered = X − mean(X)
U, S, Vt = svd(X_centered)
modes = Vt[:K]           # K principal shape modes
```

Each mode is a 3D displacement field that can be added to the mean shape with a
scalar weight `α`:

```
deformed = mean_shape + α * mode_i.reshape(N_vertices, 3)
```

This enables interpolation across the human (or synthetic) shape space.

### 3.3 Gyrification Index Integration

Gyrification Index (GI) = pial surface area / convex hull area. For real human
brains: GI ≈ 2.6 ± 0.3 (Zilles et al., 1988). For Hilbertbrane Order 4: GI ≈ 1.8–2.2
(estimated; depends on `sulcus_scale`). GI can be used as a quality label in the
PCA shape space plot.

**Deliverable:** `atlas.py` + `notebooks/shape_space.ipynb`

---

## Track 4 — WebGL Browser Viewer

**Goal:** Serve an interactive 3D viewer of the generated mesh at the GitHub Pages
URL (currently `http://calisota.ai/hilbertbrane/`) with no local installation.

### 4.1 STL → glTF Conversion

```python
import trimesh
mesh = trimesh.load('HilbertBrain.stl')
mesh.export('docs/viewer/brain.glb')
```

glTF 2.0 binary (`.glb`) is natively supported by Three.js, Babylon.js, and
modern browsers. File size for Order 4 after decimation: ~8–15 MB.

### 4.2 Three.js Scene

```
docs/viewer/
├── index.html         ← Three.js scene
├── brain.glb          ← converted mesh
└── OrbitControls.js   ← camera interaction (CDN link preferred)
```

The scene should include:
- PBR material with `metalness=0.1`, `roughness=0.5`, `color=#4a9eff`
- Directional key light + ambient fill
- OrbitControls for pan/zoom/rotate
- GUI panel (dat.GUI or lil-gui) to adjust color, metalness, roughness live
- Link back to the GitHub repo

### 4.3 CI Integration (optional)

A GitHub Actions workflow can auto-regenerate `brain.glb` whenever a new STL is
pushed to `master`, keeping the viewer always up to date.

---

## Track 5 — Advanced Neuroscience Integration

### 5.1 Gyrification Index Pipeline

```python
# gyrification_index.py
import pyvista as pv
from scipy.spatial import ConvexHull

def gyrification_index(stl_path):
    mesh = pv.read(stl_path)
    surface_area = mesh.area
    pts = mesh.points
    hull = ConvexHull(pts)
    convex_area = hull.area
    return surface_area / convex_area
```

Target human range: 2.3–3.0. Target Hilbertbrane range (to be calibrated): 1.6–2.4.
Print GI after every STL export in the generators.

### 5.2 RSA on Hilbert Topology

The Hilbert path imposes a spatial ordering on all N³ voxels. This ordering can be
treated as a dissimilarity matrix: two voxels are "near" if their Hilbert indices
are close, "far" if distant. Comparing this matrix to MEG/EEG Representational
Dissimilarity Matrices (RDMs) via Spearman correlation tests whether cortical
spatial proximity (as captured by Hilbert topology) predicts neural representational
similarity.

Predicted outcome: moderate positive correlation (r ≈ 0.2–0.4) in visual and
somatosensory cortex where spatial organization is known to be preserved.

### 5.3 Cortical Parcellation Mapping

Map standard anatomical labels (Brodmann areas, Desikan-Killiany parcellation) from
a template brain (e.g., MNI152) onto the Hilbertbrane synthetic mesh via barycentric
interpolation after ICP alignment. This allows region-specific analysis of the
generated folding patterns.

**Library:** `nibabel` (for `.nii.gz` atlas files), `nilearn` (for plotting), already
partially covered in `brain_box.py`.

---

## Cross-Track Dependencies

```
Track 1 (Alt. Geometry)
    └── feeds Track 2 (Animation: animate growth of L-system or RD surface)
    └── feeds Track 3 (Atlas: include L-system and RD meshes in shape space)

Track 3 (Atlas)
    └── feeds Track 5 (GI per subject → label shape space)
    └── feeds Track 5 (parcellation alignment)

Track 4 (WebGL)
    └── can visualize Track 3 mean shape and modes interactively
```

---

## Contributing

See [`CONTRIBUTING.md`](../../CONTRIBUTING.md) for pull request guidelines.
Discussions on any of these tracks are welcome as GitHub Issues.
