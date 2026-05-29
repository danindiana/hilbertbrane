# Hilbertbrane: A Generative Biological Mesh Architecture 🧠

Welcome to **Hilbertbrane**, an advanced computational modeling suite that procedurally generates biologically plausible 3D brain surfaces (gyri and sulci) using discrete mathematical fractals.

This repository takes the continuous, space-filling properties of the **3D Hilbert Curve** and wraps them through a volumetric mapping pipeline to synthesize cortical folding patterns that parallel biological neurogenesis.

---

## 🔬 Theoretical Background
The human cortex maximizes surface area within the constrained volume of the skull through complex folding (gyrification). Hilbert curves—a continuous fractal space-filling curve first described by David Hilbert in 1891—exhibit similar mathematical properties: they maximize path density within a bounded Euclidean space without self-intersection.

By generating a 3D Hilbert curve and subjecting it to harmonic frequency modulation and Perlin noise, **Hilbertbrane** simulates the mechanical buckling and tension of cortical white matter, extruding it into a 3D watertight STL mesh ready for visualization, physics simulation, or 3D printing.

---

## 🚀 Core Features & Generators

### 1. The Generators (`HilbertGyri*.py`)
- **`HilbertGyri.py`**: The base generator. Sets up the foundational bitwise Gray code indexing to generate the raw spatial coordinate path.
- **`HilbertGyri2.py`**: The detailed generator. Bumps the fractal recursion depth to create a dense, highly folded structure, mapping the coordinates to an unconstrained grid.
- **`HilbertGyri3.py`**: The biological preset. Normalizes the unit cube and maps it across an ellipsoid bounding box `[A-P: 2.0, L-R: 1.3, S-I: 1.0]` with a Z-axis ventricle mask for realistic brain topology.

### 2. Live Parameter Tuning (`interactive_tuner.py`)
Because calculating spatial non-intersection in volumetric meshes is non-trivial, blindly entering variables often results in merged geometric blobs. The `interactive_tuner.py` script opens a live **PyVista OpenGL GUI** allowing users to physically scrub through:
- **Overall Brain Scale**: The bounding volume mapping.
- **Gyri Radius**: The thickness of the extruded spline tube.
- **Sulcus Depth**: The amplitude of the harmonic pinch field simulating sulci.

### 3. MNE-RSA Architecture Diagram (`brain_box.py`)
A supplementary utility for visualizing complex systems architectures. Generates a dark-neon, cyber-aesthetic node map describing MNE-Python integration for Representational Similarity Analysis (RSA) of MEG/EEG data.

---

## 🛠 Installation & Quickstart

**1. Clone the repository and navigate to the directory:**
```bash
git clone https://github.com/danindiana/hilbertbrane.git
cd hilbertbrane
```

**2. Initialize the Python Environment:**
This project relies heavily on `pyvista` and `vtk` which require strict dependency management.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Execute the full pipeline:**
The included shell script will execute all generators and architecture renderers sequentially.
```bash
chmod +x run.sh
./run.sh
```

---

## 📂 Documentation & 25 Component Diagrams

The `docs/` folder contains comprehensive Graphviz-generated flowcharts detailing every sub-process in the mathematical and programmatic pipeline. We have generated **25 distinct diagrams** to cover the architecture.

Inside `docs/diagrams_25/`, you will find both `.png` (raster) and `.svg` (vector) diagrams of the following sub-systems:

1. **`01_hilbert_theory`**: 1D to 3D fractal recursion models.
2. **`02_math_pipeline`**: Bitwise Gray Code to XYZ coordinate mapping.
3. **`03_pyvista_mesh`**: Spline interpolation and Triangulation pipeline.
4. **`04_noise_modulation`**: Arclength parameters tied to Perlin noise.
5. **`05_mne_rsa_integration`**: Searchlight to Brain mapping.
6. **`06_user_interaction`**: Interactive Tuner callback flows.
7. **`07_file_structure`**: Root vs Docs directory structure mapping.
8. **`08_decimation_process`**: Taubin smoothing and Poly reduction.
9. **`09_biological_growth`**: Differential growth and buckling logic.
10. **`10_performance_metrics`**: Spline generation to VRAM mapping.
11. **`11_script_hierarchy`**: Shell to Python to VTK dependency execution.
12. **`12_ellipsoid_mapping`**: Unit cube to A-P/L-R/S-I shape mapping.
13. **`13_color_materials`**: PBR material lighting pipeline.
14. **`14_offline_rendering`**: Headless Xvfb screenshot generation.
15. **`15_git_workflow`**: Version control staging map.
16. **`16_data_flow_mne`**: Epoch to RDM visualization flow.
17. **`17_ventricle_mask`**: Z-axis height thresholding logic.
18. **`18_tube_normals`**: Centerline tangent extrusion math.
19. **`19_parameter_space`**: Radius vs Intersection vs Realism tuning map.
20. **`20_deployment`**: Local setup to WebGL/Print map.
21. **`21_error_handling`**: `vary_radius` API to Legacy VTK fallback logic.
22. **`22_stl_export`**: PolyData watertight mesh export checks.
23. **`23_cli_interface`**: Synchronous interactive parameter prompts.
24. **`24_hardware_accel`**: GPU OpenGL acceleration stack.
25. **`25_future_work`**: Extension into Reaction-Diffusion mapping.

---

## 🎨 Visualization
To render your generated `.stl` files in a high-fidelity 3D environment locally, simply run:
```bash
python view_stls.py
```
This will open a linked-view Plotter instance rendering your structural mesh outputs using Physically Based Rendering (PBR) shading.
