# Hilbertbrane 🧠

Hilbertbrane is a Python-based generative modeling project that constructs biologically plausible 3D brain surfaces (gyri and sulci) using Hilbert curves mapped to an ellipsoid bounding box. It applies Perlin noise and harmonic pinch fields to a PyVista volumetric tube generation pipeline to simulate cortical folding.

## 🚀 Features
- **Hilbert-Curve Brain Generation**: Utilizes mathematical space-filling curves to construct a continuous cortical surface.
- **Interactive Tuner (`interactive_tuner.py`)**: A PyVista GUI to visually tweak and balance variables (Overall Brain Size, Gyri Radius, Sulcus Depth) in real-time to avoid intersecting blobs.
- **Multi-Level Detail**:
  - `HilbertGyri.py`: Base generator.
  - `HilbertGyri2.py`: Detailed generator.
  - `HilbertGyri3.py`: Biological preset with Order=4 volumetric mapping (4096 nodes).
- **MNE-RSA Diagram Generator**: `brain_box.py` generates a dark-neon architectural component map using matplotlib.

## 🛠 Installation & Setup

1. **Clone the repository.**
2. **Create a virtual environment & install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## ⚙️ Usage
You can run the entire generation pipeline by running the included shell script:
```bash
./run.sh
```

**Generate specific meshes:**
```bash
python HilbertGyri3.py
```

**View the Output interactively:**
```bash
python view_stls.py
```

**Fine-tune Generation Parameters live:**
```bash
python interactive_tuner.py
```

## 📂 Documentation & Architecture
See the `docs/` folder for Graphviz-generated workflow and architecture diagrams detailing the step-by-step pipeline from mathematical curve index to watertight STL mesh.

- `docs/architecture.png`: Scripts & Dependencies
- `docs/workflow.png`: Mesh generation mathematical pipeline
