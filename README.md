<p align="center">
  <img src="docs/logo.png" alt="Hilbertbrane Logo" width="820">
</p>

# Hilbertbrane: A Generative Biological Mesh Architecture 🧠

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="https://docs.pyvista.org/"><img src="https://img.shields.io/badge/Rendered_with-PyVista-green.svg" alt="PyVista"></a>
  <a href="https://github.com/danindiana/hilbertbrane/stargazers"><img src="https://img.shields.io/github/stars/danindiana/hilbertbrane?style=social" alt="Stars"></a>
</p>

Hilbertbrane maps the continuous, space-filling properties of the **3D Hilbert Curve** through a volumetric pipeline to synthesize cortical folding patterns that parallel biological neurogenesis — producing watertight STL meshes ready for 3D printing, physics simulation, or WebGL visualization.

<p align="center">
  <img src="docs/animations/spin_zoomout_sm.gif" alt="3D Hilbert curve spin-out" width="600">
</p>

<p align="center">
  <img src="docs/demo.gif" alt="Hilbertbrane diagram preview" width="800">
</p>

<p align="center">
  <a href="http://calisota.ai/hilbertbrane/"><strong>Browse all 25 diagrams →</strong></a>
</p>

---

## 🔬 Theoretical Background

The human cortex maximizes surface area within the constrained volume of the skull through complex folding (gyrification). Hilbert curves — a continuous fractal space-filling curve first described by David Hilbert in 1891 — exhibit a mathematically analogous property: they maximize path density within a bounded Euclidean space without self-intersection.

<p align="center">
  <img src="docs/diagrams_25/01_hilbert_theory.png" alt="Hilbert Curve Theory" width="600">
</p>

By generating a 3D Hilbert curve and subjecting it to harmonic frequency modulation and Perlin noise, **Hilbertbrane** simulates the mechanical buckling and tension of cortical white matter — extruding it into a 3D watertight mesh.

---

## ⚙️ How It Works

### Step 1 — Integer Index to 3D Coordinate

Each point on the Hilbert path is decoded from an integer index via a compact bitwise Gray code transform. Every voxel in the N³ grid is visited exactly once.

<p align="center">
  <img src="docs/diagrams_25/02_math_pipeline.png" alt="Mathematical Pipeline" width="680">
</p>

### Step 2 — Sulcal Pinch Field

A superposition of two harmonics (plus a low-frequency wobble term) creates the arclength-varying pinch field P(t) that drives sulcus/gyrus alternation along the spline:

```
P(t) = w1 × (1 - cos(2π·k1·t + φ1)) / 2
     + w2 × (1 - cos(2π·k2·t + φ2)) / 2
     + wobble term
```

The per-point tube radius is then `R × (1 − SulcusScale × P(t))`, clipped to a safe range.

<p align="center">
  <img src="docs/diagrams_25/04_noise_modulation.png" alt="Sulcal Pinch Field" width="620">
</p>

### Step 3 — PyVista Mesh Generation

The decoded path is smoothed into a continuous spline, which is then extruded into a varying-radius tube, triangulated, decimated, and Taubin-smoothed into a production-ready mesh.

<p align="center">
  <img src="docs/diagrams_25/03_pyvista_mesh.png" alt="PyVista Mesh Pipeline" width="560">
</p>

### Step 4 — Differential Cortical Growth

The outer surface (Z > mean Z) is identified and displaced along its vertex normals by a growth factor (1.08–1.25), simulating the biomechanical expansion that causes cortical buckling during development.

<p align="center">
  <img src="docs/diagrams_25/09_biological_growth.png" alt="Biological Growth Simulation" width="560">
</p>

---

## 🚀 Core Features & Generators

### Generator Scripts (`HilbertGyri*.py`)

| Script | Order | Spline pts | Key feature |
|--------|-------|-----------|-------------|
| `HilbertGyri.py` | 3 | 2 000 | Base generator — fast, minimal |
| `HilbertGyri2.py` | 4 | 3 500 | Dense, highly-folded, no Perlin noise |
| `HilbertGyri3.py` | 4 | 8 000 | Ellipsoid bounding box `[A-P: 2.0, L-R: 1.3, S-I: 1.0]` + ventricle mask + Perlin noise |
| `Hilbertbrane.py` | configurable | configurable | Interactive CLI — prompts for all parameters |

### Live Parameter Tuning (`interactive_tuner.py`)

Because volumetric self-intersection is non-trivial to predict analytically, the interactive tuner opens a **PyVista OpenGL GUI** with three real-time sliders:

- **Brain Scale** `[20 – 200]` — overall bounding volume
- **Gyri Radius** `[0.5 – 15]` — tube extrusion thickness
- **Sulcus Depth** `[0 – 0.95]` — harmonic pinch amplitude

<p align="center">
  <img src="docs/diagrams_25/06_user_interaction.png" alt="Interactive Tuner Flow" width="500">
</p>

### MNE-RSA Architecture (`brain_box.py`)

Generates a dark-neon node map describing MNE-Python integration for Representational Similarity Analysis (RSA) of MEG/EEG data. See the [full MNE-RSA data flow](#).

---

## 🛠 Installation & Quickstart

```bash
# 1. Clone
git clone https://github.com/danindiana/hilbertbrane.git
cd hilbertbrane

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run the full pipeline
chmod +x run.sh
./run.sh
```

Or run a single generator interactively:

```bash
python Hilbertbrane.py
```

---

## 🎨 Visualization

View generated `.stl` files in a high-fidelity PBR 3D environment:

```bash
python view_stls.py
```

Render a headless screenshot (no display required):

```bash
python screenshot.py
```

---

## 📊 Performance Scaling

| Order | Voxels | ~Poly count | ~RAM | ~Time |
|-------|--------|-------------|------|-------|
| 3 | 512 | 50k | 5 MB | < 5 s |
| 4 | 4 096 | 300k | 150 MB | 30–60 s |
| 5 | 32 768 | > 1M | > 1 GB | minutes |

Decimation (0.30–0.45 reduction factor) brings the final STL to a printable size before export.

---

## 📂 25 Component Diagrams

All diagrams live in `docs/diagrams_25/` as `.png`, `.svg`, and `.dot` source files. A selection is shown inline above; the complete set covers:

| # | Diagram | Category |
|---|---------|----------|
| 01 | Hilbert Curve Fractal Theory | Math/Theory |
| 02 | Mathematical Pipeline (Gray Code) | Math/Theory |
| 03 | PyVista Mesh Generation | Mesh/Processing |
| 04 | Sulcal Pinch Field (Harmonic + Perlin) | Neuroscience |
| 05 | MNE-RSA Integration Pipeline | Neuroscience |
| 06 | Interactive Tuner GUI Flow | UI/Interaction |
| 07 | Project Directory Structure | Infrastructure |
| 08 | Mesh Decimation & Smoothing | Mesh/Processing |
| 09 | Differential Cortical Growth | Neuroscience |
| 10 | Performance & Memory Scaling | Performance |
| 11 | Script Dependency Hierarchy | Infrastructure |
| 12 | Ellipsoid Bounding Box Mapping | Math/Theory |
| 13 | PBR Material & Lighting Pipeline | Materials |
| 14 | Headless/Offline Screenshot Pipeline | Infrastructure |
| 15 | Git Version Control Workflow | Infrastructure |
| 16 | MNE-RSA Complete Data Flow | Neuroscience |
| 17 | Ventricle Thinning Mask | Neuroscience |
| 18 | Tube Surface Normals & Geometry | Mesh/Processing |
| 19 | Parameter Interaction & Trade-offs | Math/Theory |
| 20 | User Deployment Workflow | Infrastructure |
| 21 | vary_radius API Fallback Logic | Infrastructure |
| 22 | STL Export Pipeline | Mesh/Processing |
| 23 | CLI Parameter Prompting Interface | UI/Interaction |
| 24 | Hardware Acceleration Stack | Infrastructure |
| 25 | Future Extensions & Research Directions | Future |

Regenerate all diagrams at any time:

```bash
python generate_25_diagrams.py
```

View the full interactive gallery at **[calisota.ai/hilbertbrane](http://calisota.ai/hilbertbrane/)** — each card links to the full-size PNG and vector SVG source.

### Future Directions

<p align="center">
  <img src="docs/diagrams_25/25_future_work.png" alt="Future Extensions" width="700">
</p>

Planned extensions include L-systems, reaction-diffusion Turing patterns, temporal developmental animations, multi-subject cortical atlases, and a browser-hosted WebGL viewer.

---

## 🖼 Infographics

### Project Overview

<p align="center">
  <img src="docs/infographics/hilbertbrane_overview.png" alt="Hilbertbrane Generative Biological Mesh Architecture overview" width="900">
</p>

### MNE-RSA Architecture

<p align="center">
  <img src="docs/infographics/mne_rsa_architecture.png" alt="MNE-RSA Architecture diagram" width="900">
</p>

Source files live in [`docs/infographics/`](docs/infographics/).

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
