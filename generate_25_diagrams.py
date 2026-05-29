import os
import subprocess

diagrams = {
    "01_hilbert_theory": """digraph G { label="Hilbert Curve Fractal Theory"; node [shape=box]; 
        "1D Line" -> "2D Space Filling" -> "3D Volume Filling"; "Order 1" -> "Order 2" -> "Order N"; }""",
    "02_math_pipeline": """digraph G { label="Mathematical Pipeline"; 
        "Index i" -> "Bitwise Gray Code" -> "3D Coordinates (x,y,z)"; }""",
    "03_pyvista_mesh": """digraph G { label="PyVista Mesh Generation"; 
        "Centerline Points" -> "Spline Interpolation" -> "Varying Radius Tube" -> "Triangulation"; }""",
    "04_noise_modulation": """digraph G { label="Noise Modulation (Sulci/Gyri)"; 
        "Normalized Arclength t" -> "Low Frequency Harmonics" -> "Perlin Noise" -> "Radius Scaling"; }""",
    "05_mne_rsa_integration": """digraph G { label="MNE-RSA Brain Integration"; 
        "Evoked Data" -> "Searchlight" -> "RSA Computation" -> "Brain Mapping"; }""",
    "06_user_interaction": """digraph G { label="Interactive Tuner Flow"; 
        "User Adjusts Slider" -> "Callback Triggered" -> "Recompute Spline & Radii" -> "Update Actor"; }""",
    "07_file_structure": """digraph G { label="Directory Structure Map"; 
        "Root" -> "docs/"; "Root" -> "src/"; "Root" -> "output/"; "docs/" -> "diagrams"; }""",
    "08_decimation_process": """digraph G { label="Mesh Decimation & Smoothing"; 
        "Raw Tube (High Poly)" -> "Decimate (Reduction factor)" -> "Taubin Smoothing" -> "Recalculate Normals"; }""",
    "09_biological_growth": """digraph G { label="Differential Growth Buckle"; 
        "Mesh Surface" -> "Identify Outer Mask" -> "Displace Along Normals" -> "Simulate Cortical Expansion"; }""",
    "10_performance_metrics": """digraph G { label="Performance & Memory Mapping"; 
        "Order 4 (4096 nodes)" -> "Spline (8000 pts)" -> "Tube (300k Polys)" -> "GPU VRAM"; }""",
    "11_script_hierarchy": """digraph G { label="Script Dependency Hierarchy"; 
        "run.sh" -> "Python Generators"; "Python Generators" -> "numpy / pyvista / noise"; }""",
    "12_ellipsoid_mapping": """digraph G { label="Ellipsoid Bounding Box Mapping"; 
        "Unit Cube [0,1]^3" -> "Center at 0" -> "Scale by [A-P, L-R, S-I]" -> "Brain Shape"; }""",
    "13_color_materials": """digraph G { label="PBR Material Pipeline"; 
        "PolyData" -> "Apply Color (lightblue)" -> "Specular Highlight" -> "Metallic roughness"; }""",
    "14_offline_rendering": """digraph G { label="Offline Rendering (Screenshot)"; 
        "Xvfb / Offscreen Plotter" -> "Add Mesh" -> "Set Iso Camera" -> "Export PNG"; }""",
    "15_git_workflow": """digraph G { label="Git Version Control"; 
        "Working Directory" -> "Staging (add)" -> "Local Repo (commit)" -> "Remote Repo (push)"; }""",
    "16_data_flow_mne": """digraph G { label="MNE-RSA Data Flow"; 
        "MEG/EEG Epochs" -> "Source Estimate" -> "RDM Matrix" -> "Brain Plot"; }""",
    "17_ventricle_mask": """digraph G { label="Ventricle Thinning Mask"; 
        "Z-Axis Relative Height" -> "Threshold Mask" -> "Scale Radius Down (Thinning)"; }""",
    "18_tube_normals": """digraph G { label="Tube Surface Normals"; 
        "Centerline Tangent" -> "Orthogonal Vectors" -> "Extrude Circle" -> "Generate Faces"; }""",
    "19_parameter_space": """digraph G { label="Tuning Parameter Space"; 
        "Radius" -> "Self-Intersection Risk"; "Order" -> "Computation Time"; "Pinch" -> "Biological Realism"; }""",
    "20_deployment": """digraph G { label="Deployment Pipeline"; 
        "Install Requirements" -> "Generate STLs" -> "Quality Check (Tuner)" -> "3D Print / WebGL"; }""",
    "21_error_handling": """digraph G { label="Error Handling & Fallbacks"; 
        "Try vary_radius API" -> "Catch Exception" -> "Fallback to Legacy VTK Tube API"; }""",
    "22_stl_export": """digraph G { label="STL Export Pipeline"; 
        "Triangulate Faces" -> "Check Watertightness" -> "Write Binary STL Header" -> "Save File"; }""",
    "23_cli_interface": """digraph G { label="CLI Parameter Prompting"; 
        "Wait for Input" -> "Validate Float/Int" -> "Return Config Dict" -> "Run Generator"; }""",
    "24_hardware_accel": """digraph G { label="Hardware Acceleration"; 
        "VTK Pipeline" -> "OpenGL" -> "GPU Shaders" -> "Display Monitor"; }""",
    "25_future_work": """digraph G { label="Future Extensions"; 
        "Hilbert Curves" -> "L-Systems / Reaction-Diffusion" -> "Temporal Brain Evolution"; }""",
}

os.makedirs("docs/diagrams_25", exist_ok=True)

for name, dot_content in diagrams.items():
    dot_path = f"docs/diagrams_25/{name}.dot"
    with open(dot_path, "w") as f:
        f.write(dot_content)
    
    # Compile
    subprocess.run(["dot", "-Tpng", dot_path, "-o", f"docs/diagrams_25/{name}.png"])
    subprocess.run(["dot", "-Tsvg", dot_path, "-o", f"docs/diagrams_25/{name}.svg"])

print("Successfully generated 25 additional diagrams.")
