import os
import subprocess

# Dark / Neon color themes per category:
#   Math/Theory    (01,02,12,19): node=#001a2e  neon=#00bfff  cluster=#000d1a
#   Mesh/Process   (03,08,18,22): node=#001a0d  neon=#00ff88  cluster=#000d07
#   Neuroscience   (04,05,09,16,17): node=#2e0014  neon=#ff2d78  cluster=#1a000c
#   UI/Interaction (06,23): node=#1a0033  neon=#bf00ff  cluster=#0d001a
#   Infrastructure (07,11,14,15,20,21,24): node=#001a1a  neon=#00ffe7  cluster=#000d0d
#   Performance    (10): node=#2e0900  neon=#ff6600  cluster=#1a0500
#   Materials      (13): node=#2e1a00  neon=#ffaa00  cluster=#1a0f00
#   Future         (25): node=#2e2a00  neon=#ffe600  cluster=#1a1800

_GRAPH_DEFAULTS = """\
    graph [
        fontname="Helvetica,Arial,sans-serif"
        bgcolor="#0d1117"
        fontcolor="white"
        splines=spline
        nodesep=0.6
        ranksep=0.8
        pad=0.4
        labelloc="t"
        labeljust="c"
        fontsize=14
    ]
    node [fontname="Helvetica,Arial,sans-serif" fontsize=11 style="filled,rounded" penwidth=1.8 fontcolor="white"]
    edge [fontname="Helvetica,Arial,sans-serif" fontsize=9 color="#444466" penwidth=1.2 fontcolor="#aaaacc"]
"""

diagrams = {

# ─── 01 ─── Hilbert Curve Theory ─────────────────────────────────────────────
"01_hilbert_theory": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Hilbert Curve: Fractal Space-Filling Theory" rankdir="TB"]

    subgraph cluster_dim {
        label="Dimensionality Progression"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        d1 [label="1D Line Segment" shape=box fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        d2 [label="2D Space-Filling Curve\\n(Order N fills unit square)" shape=box fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        d3 [label="3D Hilbert Volume\\n(fills unit cube without self-intersection)" shape=box fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        d1 -> d2 [label="extrude"]
        d2 -> d3 [label="extrude"]
    }

    subgraph cluster_orders {
        label="Fractal Orders"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        o1 [label="Order 1\\n8 voxels" shape=box fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        o2 [label="Order 2\\n64 voxels" shape=box fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        o3 [label="Order 3\\n512 voxels" shape=box fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        o4 [label="Order 4\\n4096 voxels" shape=box fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        o1 -> o2 -> o3 -> o4 [label="2× depth"]
    }

    subgraph cluster_props {
        label="Key Mathematical Properties"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        p1 [label="Space-Filling Property\\n(visits every voxel exactly once)" shape=ellipse fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        p2 [label="Self-Similarity\\n(each sub-curve is a scaled copy)" shape=ellipse fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        p3 [label="Locality Preservation\\n(nearby indices → nearby positions)" shape=ellipse fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
    }

    d3 -> p1 [label="implies"]
    d3 -> p2 [label="implies"]
    d3 -> p3 [label="implies"]
    o4 -> d3 [label="used in HilbertBrain.py" style=dashed color="#334455" fontcolor="#778899"]
}
""",

# ─── 02 ─── Mathematical Pipeline ────────────────────────────────────────────
"02_math_pipeline": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Mathematical Pipeline: Integer Index → 3D Coordinate" rankdir="LR"]

    subgraph cluster_input {
        label="Input"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"
        i1 [label="Integer Index i\\n(0 … N³-1)" shape=parallelogram fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
    }

    subgraph cluster_gray {
        label="Bitwise Gray Code Transform"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        g1 [label="Extract bit plane i\\n(x>>i)&1, (y>>i)&1, (z>>i)&1" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        g2 [label="Pack to prefix\\n(xb<<2)|(yb<<1)|zb" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        g3 [label="Apply Gray XOR\\nprefix ^= prefix >> 1" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        g4 [label="Accumulate\\nh |= prefix << (3*i)" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        g1 -> g2 -> g3 -> g4 [label="per bit"]
    }

    subgraph cluster_output {
        label="Output"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        o1 [label="Hilbert Index h" shape=cylinder fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        o2 [label="Sort all points by h\\n→ continuous path order" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        o3 [label="(x, y, z) coordinate" shape=parallelogram fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        o1 -> o2 -> o3
    }

    i1 -> g1 [label="feed"]
    g4 -> o1 [label="concat bits"]
}
""",

# ─── 03 ─── PyVista Mesh Generation ──────────────────────────────────────────
"03_pyvista_mesh": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="PyVista Mesh Generation Pipeline" rankdir="TB"]

    subgraph cluster_cl {
        label="Centerline Construction"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        c1 [label="Hilbert Path\\n(N³ discrete integer points)" shape=cylinder fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        c2 [label="pv.Spline(path, N_SAMPLES)\\n→ smooth continuous centerline" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        c3 [label="Arclength t ∈ [0,1]\\nnp.cumsum(segment lengths)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        c1 -> c2 [label="interpolate"]
        c2 -> c3 [label="normalize"]
    }

    subgraph cluster_rp {
        label="Radius Profile"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        r1 [label="Pinch Field P(t)\\n∈ [0, 1] per point" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        r2 [label="radius_abs = R × (1 - SulcusScale × P)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        r3 [label="Attach as point_data\\n'radius_profile'" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        r1 -> r2 -> r3
    }

    subgraph cluster_tube {
        label="Tube Extrusion"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        t1 [label="centerline.tube(\\n  scalars='radius_profile',\\n  n_sides=32, capping=True\\n)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        t2 [label="tube.triangulate()\\n(all-triangle faces)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        t3 [label="PolyData surface mesh\\n(watertight)" shape=cylinder fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        t1 -> t2 -> t3
    }

    c3 -> r1 [label="feeds t"]
    r3 -> t1 [label="drives radius"]
    t3 -> t2 [style=invis]
}
""",

# ─── 04 ─── Noise Modulation ──────────────────────────────────────────────────
"04_noise_modulation": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Sulcal Pinch Field: Harmonic + Perlin Modulation" rankdir="TB"]

    subgraph cluster_harm {
        label="Harmonic Components"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        h1 [label="Primary Harmonic\\nw1×(1-cos(2π·k1·t+φ1))/2\\n(k1=7..9, w1=1.0)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        h2 [label="Secondary Harmonic\\nw2×(1-cos(2π·k2·t+φ2))/2\\n(k2=13..17, w2=0.35)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        h3 [label="Low-freq Wobble\\nwobble×(1-cos(2π·1.2·t+0.7))/2" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        hsum [label="Sum → P(t) raw" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        h1 -> hsum
        h2 -> hsum
        h3 -> hsum
    }

    subgraph cluster_norm {
        label="Normalization"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        n1 [label="P -= P.min(); P /= P.max()" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        n2 [label="P(t) normalized ∈ [0,1]" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        n1 -> n2
    }

    subgraph cluster_perlin {
        label="Perlin Noise Overlay (HilbertGyri3)"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        pn1 [label="noise.pnoise1(t × freq)\\n→ per-point offset" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        pn2 [label="Add to centerline XYZ\\n(organic folding)" shape=ellipse fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        pn1 -> pn2
    }

    subgraph cluster_out {
        label="Radius Output"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        ro1 [label="radius_abs = R×(1 - SulcusScale×P)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        ro2 [label="np.clip(radius_abs, R×0.25, R×1.15)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        ro3 [label="per-point radius array" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        ro1 -> ro2 -> ro3
    }

    phases [label="Random phases φ1, φ2\\nrng.uniform(0, 2π)" shape=note fillcolor="#1a1a2e" color="#ff2d78" fontcolor="#cccccc"]
    hsum -> n1
    n2 -> ro1
    phases -> h1 [style=dashed color="#553344"]
    phases -> h2 [style=dashed color="#553344"]
}
""",

# ─── 05 ─── MNE-RSA Integration ───────────────────────────────────────────────
"05_mne_rsa_integration": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="MNE-RSA Neuroscience Integration Pipeline" rankdir="TB"]

    subgraph cluster_acq {
        label="Data Acquisition"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        a1 [label="MEG/EEG Recording" shape=parallelogram fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        a2 [label="mne.Epochs\\n(time-locked segments)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        a3 [label="Preprocessing\\n(filter, ICA, baseline)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        a1 -> a2 -> a3
    }

    subgraph cluster_src {
        label="Source Estimation"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        s1 [label="Forward Model\\n(BEM / sphere)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        s2 [label="Inverse Operator\\n(MNE / dSPM / sLORETA)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        s3 [label="SourceEstimate (STC)\\nvertices × time" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        s1 -> s2 -> s3
    }

    subgraph cluster_rsa {
        label="RSA Computation"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        r1 [label="RDM: pairwise dissimilarity\\n(1 - correlation)" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        r2 [label="Searchlight Analysis\\n(per-vertex sphere)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        r3 [label="Spearman / Pearson r\\nvs model RDM" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        r4 [label="RSA Score Map\\n(vertex-level)" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        r1 -> r2 -> r3 -> r4
    }

    subgraph cluster_viz {
        label="Brain Visualization"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        v1 [label="brain_box.py\\nmne_rsa_dark_neon.png" shape=note fillcolor="#1a1a2e" color="#ff2d78" fontcolor="#cccccc"]
        v2 [label="mne.viz /\\npyvista brain plot" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        v3 [label="Surface Plot\\n(inflated / pial)" shape=ellipse fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        v1 -> v2 -> v3
    }

    a3 -> s1 [label="epochs→source"]
    s3 -> r1 [label="stc→RDM"]
    r4 -> v1 [label="scores→map"]
}
""",

# ─── 06 ─── User Interaction ──────────────────────────────────────────────────
"06_user_interaction": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Interactive Tuner: PyVista GUI Event Flow" rankdir="TB"]

    subgraph cluster_setup {
        label="GUI Setup"
        style="filled,rounded" fillcolor="#0d001a" color="#bf00ff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#bf00ff"

        su1 [label="pv.Plotter()" fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        su2 [label="add_slider_widget() × 3 sliders" fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        su3 [label="initial update_mesh()" fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        su1 -> su2 -> su3
    }

    subgraph cluster_sliders {
        label="Slider Events"
        style="filled,rounded" fillcolor="#0d001a" color="#bf00ff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#bf00ff"

        sl1 [label="Brain Size slider\\n[20 .. 200]" shape=diamond fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        sl2 [label="Gyri Radius slider\\n[0.5 .. 15]" shape=diamond fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        sl3 [label="Sulcus Depth slider\\n[0 .. 0.95]" shape=diamond fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        pd  [label="params dict update" fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        sl1 -> pd
        sl2 -> pd
        sl3 -> pd
    }

    subgraph cluster_recompute {
        label="Mesh Recompute"
        style="filled,rounded" fillcolor="#0d001a" color="#bf00ff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#bf00ff"

        m1 [label="update_mesh() callback" fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        m2 [label="scale & spline\\nresample" fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        m3 [label="pinch field P(t)" fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        m4 [label="radius profile\\nper-point" fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        m5 [label="centerline.tube()" fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        m6 [label="p.remove_actor()\\np.add_mesh()" fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        m1 -> m2 -> m3 -> m4 -> m5 -> m6
    }

    subgraph cluster_render {
        label="Render"
        style="filled,rounded" fillcolor="#0d001a" color="#bf00ff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#bf00ff"

        rv [label="OpenGL Render" shape=ellipse fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        disp [label="3D Viewport" shape=parallelogram fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        rv -> disp
    }

    su3 -> m1
    pd -> m1
    m6 -> rv
    disp -> sl1 [label="user interacts" style=dashed color="#553366" fontcolor="#888899"]
}
""",

# ─── 07 ─── File Structure ────────────────────────────────────────────────────
"07_file_structure": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Project Directory Structure" rankdir="LR"]

    root [label="hilbertbrane/\\n(repo root)" shape=tab fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]

    subgraph cluster_scripts {
        label="Generator Scripts"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        sc1 [label="Hilbertbrane.py\\n(CLI, interactive)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        sc2 [label="HilbertGyri.py\\n(base generator)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        sc3 [label="HilbertGyri2.py\\n(detailed)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        sc4 [label="HilbertGyri3.py\\n(biological)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        sc5 [label="interactive_tuner.py\\n(PyVista GUI)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        sc6 [label="brain_box.py\\n(MNE-RSA diagram)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        sc7 [label="run.sh\\n(batch runner)" shape=parallelogram fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
    }

    subgraph cluster_docs {
        label="docs/"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        d1 [label="architecture.dot/.png/.svg" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        d2 [label="diagrams_25/\\n25 × .dot + .png + .svg" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
    }

    subgraph cluster_output {
        label="Output Artifacts"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        o1 [label="HilbertBrain.stl\\n(~24 MB)" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        o2 [label="HilbertGyri.stl\\n(~15 MB)" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        o3 [label="*_screenshot.png" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
    }

    subgraph cluster_venv {
        label="venv/"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        v1 [label="pyvista · vtk · numpy\\nnoise · matplotlib" shape=ellipse fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
    }

    root -> sc1 [label="contains"]
    root -> sc2
    root -> sc3
    root -> sc4
    root -> sc5
    root -> sc6
    root -> sc7
    root -> d1
    root -> d2
    root -> o1
    root -> o2
    root -> o3
    root -> v1
}
""",

# ─── 08 ─── Decimation Process ────────────────────────────────────────────────
"08_decimation_process": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Mesh Decimation and Smoothing Pipeline" rankdir="TB"]

    subgraph cluster_raw {
        label="Raw Tube Input"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        r1 [label="tube.triangulate()\\n(ensure all-triangle faces)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        r2 [label="~300k–600k cells\\n(pre-decimation)" shape=note fillcolor="#1a1a2e" color="#00ff88" fontcolor="#cccccc"]
    }

    subgraph cluster_dec {
        label="Decimation"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        d1 [label="mesh.decimate(0.30–0.45)\\n→ reduce cell count" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        d2 [label="Decimated mesh\\n~100k–200k cells" shape=cylinder fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        d1 -> d2
    }

    subgraph cluster_nrm {
        label="Normal Computation"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        n1 [label="compute_normals(\\n  cell_normals=False,\\n  auto_orient=True\\n)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
    }

    subgraph cluster_smooth {
        label="Smoothing"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        s1 [label="mesh.smooth(\\n  n_iter=30–90,\\n  relaxation_factor=0.5\\n)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        s2 [label="OR Taubin smooth\\n(HilbertGyri3 path)" style=dashed fillcolor="#0d1a10" color="#335533" fontcolor="#557755"]
    }

    subgraph cluster_out {
        label="Output"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        o1 [label="Final mesh\\n(watertight, smooth)" shape=cylinder fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        o2 [label="mesh.save('*.stl')" shape=parallelogram fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        o1 -> o2
    }

    r1 -> d1 [label="feed"]
    d2 -> n1 [label="recompute"]
    n1 -> s1
    s1 -> o1
    s2 -> o1 [style=dashed color="#335533"]
}
""",

# ─── 09 ─── Biological Growth ─────────────────────────────────────────────────
"09_biological_growth": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Differential Cortical Growth Simulation" rankdir="TB"]

    subgraph cluster_state {
        label="Mesh State"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        ms1 [label="Post-smoothed PolyData" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        ms2 [label="mesh.point_normals\\n(per-vertex normal vectors)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        ms1 -> ms2
    }

    subgraph cluster_mask {
        label="Outer Surface Mask"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        mk1 [label="Z coords\\nmesh.points[:,2]" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        mk2 [label="Z > Z.mean()\\n(upper ~65% of volume)" shape=diamond fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        mk3 [label="Outer surface mask\\n(boolean array)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        mki [label="Inner surface\\n(no displacement)" style=dashed fillcolor="#1a0010" color="#553344" fontcolor="#887788"]
        mk1 -> mk2
        mk2 -> mk3 [label="YES"]
        mk2 -> mki [label="NO" style=dashed color="#553344"]
    }

    subgraph cluster_disp {
        label="Normal Displacement"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        dp1 [label="growth_factor = 1.08–1.25" shape=tab fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        dp2 [label="disp = 0.25 × normals × (factor - 1.0)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        dp3 [label="mesh.points[mask] += disp[mask]" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        dp4 [label="Outer expansion → buckling" shape=ellipse fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        dp1 -> dp2 -> dp3 -> dp4
    }

    bio [label="Biological analogy:\\ncortical white matter\\nexpansion drives folding" shape=note fillcolor="#1a1a2e" color="#ff2d78" fontcolor="#cccccc"]

    ms2 -> mk1
    mk3 -> dp2
    dp4 -> bio [style=dashed color="#553344"]
}
""",

# ─── 10 ─── Performance Metrics ───────────────────────────────────────────────
"10_performance_metrics": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Performance and Memory Scaling by Hilbert Order" rankdir="TB"]

    subgraph cluster_o3 {
        label="Order 3"
        style="filled,rounded" fillcolor="#1a0500" color="#ff6600" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff6600"

        p3a [label="512 voxels\\n(2³ × 2³ × 2³)" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p3b [label="~2000 spline pts" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p3c [label="~50k polys\\n(~5 MB RAM)" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p3d [label="< 5 seconds" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p3a -> p3b -> p3c -> p3d
    }

    subgraph cluster_o4 {
        label="Order 4  (default for HilbertBrain)"
        style="filled,rounded" fillcolor="#1a0500" color="#ff6600" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff6600"

        p4a [label="4096 voxels\\n(4³ × 4³ × 4³)" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p4b [label="~8000 spline pts" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p4c [label="~300k polys\\n(~150 MB RAM)" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p4d [label="~30–60 seconds" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p4a -> p4b -> p4c -> p4d
    }

    subgraph cluster_o5 {
        label="Order 5"
        style="filled,rounded" fillcolor="#1a0500" color="#ff6600" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff6600"

        p5a [label="32768 voxels\\n(5³ × 5³ × 5³)" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p5b [label="~50k+ spline pts" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p5c [label=">1M polys\\n(>1 GB RAM)" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p5d [label="several minutes" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        p5a -> p5b -> p5c -> p5d
    }

    gpu [label="GPU VRAM\\n(VTK OpenGL buffer)" shape=cylinder fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
    note1 [label="Decimation reduces\\npoly count 30–45%\\nbefore STL export" shape=note fillcolor="#1a1a2e" color="#ff6600" fontcolor="#cccccc"]

    p3d -> gpu
    p4d -> gpu
    p5d -> gpu
    gpu -> note1 [style=dashed color="#553300"]
}
""",

# ─── 11 ─── Script Hierarchy ──────────────────────────────────────────────────
"11_script_hierarchy": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Script Dependency Hierarchy" rankdir="TB"]

    subgraph cluster_entry {
        label="Entry Points"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        e1 [label="run.sh\\n(bash automation)" shape=parallelogram fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        e2 [label="python3 -m venv\\npip install -r requirements.txt" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
    }

    subgraph cluster_gen {
        label="Generator Scripts"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        g1 [label="Hilbertbrane.py\\n(CLI, interactive)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        g2 [label="HilbertGyri.py\\n(base generator)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        g3 [label="HilbertGyri2.py\\n(detailed, no Perlin)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        g4 [label="HilbertGyri3.py\\n(biological + noise)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        g5 [label="interactive_tuner.py\\n(PyVista GUI)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
    }

    subgraph cluster_deps {
        label="Python Dependencies"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        d1 [label="numpy\\n(arrays, linalg)" shape=ellipse fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        d2 [label="pyvista + vtk\\n(mesh / rendering)" shape=ellipse fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        d3 [label="noise\\n(pnoise1)" shape=ellipse fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        d4 [label="matplotlib\\n(brain_box.py)" shape=ellipse fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        d5 [label="inspect\\n(API compat)" shape=ellipse fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
    }

    subgraph cluster_out {
        label="Output Artifacts"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        o1 [label="HilbertGyri.stl" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        o2 [label="HilbertBrain.stl" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        o3 [label="mne_rsa_dark_neon.png" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
    }

    e1 -> g1 [label="triggers"]
    e1 -> g2 [label="triggers"]
    e1 -> g3 [label="triggers"]
    e1 -> g4 [label="triggers"]
    g2 -> d1 [label="imports"]
    g2 -> d2
    g4 -> d3
    g5 -> d2
    g5 -> d5
    g2 -> o1 [label="exports"]
    g3 -> o1
    g4 -> o2 [label="exports"]
    g1 -> o1
}
""",

# ─── 12 ─── Ellipsoid Mapping ─────────────────────────────────────────────────
"12_ellipsoid_mapping": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Unit Cube to Brain Ellipsoid Coordinate Transform" rankdir="LR"]

    subgraph cluster_in {
        label="Input Space"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        i1 [label="Grid [0, N-1]³\\n(integer Hilbert coords)" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        i2 [label="Normalize: path /= (N-1)\\n→ [0,1]³ unit cube" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        i1 -> i2
    }

    subgraph cluster_center {
        label="Centering Transform"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        c1 [label="Subtract 0.5:\\npath - 0.5\\n→ [-0.5, 0.5]³" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        c2 [label="Center at origin" shape=ellipse fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        c1 -> c2
    }

    subgraph cluster_scale {
        label="Ellipsoid Scaling"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        s1 [label="Ellipsoid = [2.0, 1.3, 1.0]\\n(A-P, L-R, S-I)" shape=tab fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        s2 [label="path × Ellipsoid\\n(axis-wise broadcast)" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        s3 [label="path[:,2] += 0.15\\n(occipital shift)" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        s1 -> s2 -> s3
    }

    subgraph cluster_axes {
        label="Brain Coordinate Space"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        ax [label="Brain-shaped ellipsoid\\nbounding volume" shape=ellipse fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        nx [label="X: Anterior-Posterior\\n(-1.0 to +1.0)" shape=note fillcolor="#1a1a2e" color="#00bfff" fontcolor="#cccccc"]
        ny [label="Y: Left-Right\\n(-0.65 to +0.65)" shape=note fillcolor="#1a1a2e" color="#00bfff" fontcolor="#cccccc"]
        nz [label="Z: Superior-Inferior\\n(-0.5 to +0.5)" shape=note fillcolor="#1a1a2e" color="#00bfff" fontcolor="#cccccc"]
        s3 -> ax
        ax -> nx [style=dashed color="#334455"]
        ax -> ny [style=dashed color="#334455"]
        ax -> nz [style=dashed color="#334455"]
    }

    i2 -> c1
    c2 -> s1
}
""",

# ─── 13 ─── Color & Materials ─────────────────────────────────────────────────
"13_color_materials": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="PBR Material and Lighting Pipeline" rankdir="TB"]

    subgraph cluster_in {
        label="PolyData Input"
        style="filled,rounded" fillcolor="#1a0f00" color="#ffaa00" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ffaa00"
        ci [label="mesh (PolyData)\\ntriangulated surface" shape=cylinder fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
    }

    subgraph cluster_color {
        label="Color Assignment"
        style="filled,rounded" fillcolor="#1a0f00" color="#ffaa00" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ffaa00"

        cc1 [label="color='lightblue'\\n(or lightcoral)" fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        cc2 [label="p.add_mesh(mesh,\\n  smooth_shading=True)" fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        cc1 -> cc2
    }

    subgraph cluster_pbr {
        label="PBR Shading Parameters"
        style="filled,rounded" fillcolor="#1a0f00" color="#ffaa00" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ffaa00"

        pb1 [label="ambient = 0.0–0.2\\n(self-illumination)" fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        pb2 [label="diffuse = 0.5–1.0\\n(Lambertian reflection)" fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        pb3 [label="specular = 0–10\\n(highlight intensity)" fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        pb4 [label="metallic = 0.0–0.1" fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        pb5 [label="roughness = 0.5" fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        pbs [label="PBR Shader\\n(VTK physically based)" fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        pb1 -> pbs
        pb2 -> pbs
        pb3 -> pbs
        pb4 -> pbs
        pb5 -> pbs
    }

    subgraph cluster_light {
        label="Lighting"
        style="filled,rounded" fillcolor="#1a0f00" color="#ffaa00" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ffaa00"

        l1 [label="Key light\\n(main directional)" shape=ellipse fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        l2 [label="Fill light" shape=ellipse fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        l3 [label="Back light" shape=ellipse fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        ogl [label="OpenGL render" fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        l1 -> ogl
        l2 -> ogl
        l3 -> ogl
    }

    subgraph cluster_out {
        label="Output"
        style="filled,rounded" fillcolor="#1a0f00" color="#ffaa00" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ffaa00"

        out [label="Rendered framebuffer" fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        disp [label="Display / screenshot" shape=parallelogram fillcolor="#2e1a00" color="#ffaa00" fontcolor="#ffaa00"]
        out -> disp
    }

    ci -> cc1
    pbs -> ogl [label="GPU pipeline"]
    ogl -> out
}
""",

# ─── 14 ─── Offline Rendering ─────────────────────────────────────────────────
"14_offline_rendering": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Headless / Offline Screenshot Pipeline" rankdir="TB"]

    subgraph cluster_env {
        label="Environment Setup"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        e1 [label="Xvfb (virtual framebuffer)\\nOR off_screen=True" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        e2 [label="pv.Plotter(\\n  off_screen=True,\\n  window_size=(800,800)\\n)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        e1 -> e2
    }

    subgraph cluster_scene {
        label="Scene Assembly"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        s1 [label="pv.read('*.stl')" shape=parallelogram fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        s2 [label="p.add_mesh(mesh,\\n  color='lightblue',\\n  smooth_shading=True)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        s3 [label="p.camera_position='iso'" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        s1 -> s2 -> s3
    }

    subgraph cluster_cap {
        label="Capture and Export"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        c1 [label="p.screenshot(\\n  'output.png'\\n)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        c2 [label="PNG file\\n(800 × 800 px)" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        c1 -> c2
    }

    usage [label="Used in screenshot.py\\nfor automated CI/preview" shape=note fillcolor="#1a1a2e" color="#00ffe7" fontcolor="#cccccc"]

    e2 -> s1
    s3 -> c1
    c2 -> usage [style=dashed color="#335555"]
}
""",

# ─── 15 ─── Git Workflow ──────────────────────────────────────────────────────
"15_git_workflow": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Git Version Control Workflow" rankdir="LR"]

    subgraph cluster_local {
        label="Local Working Tree"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        wt1 [label="Edit files\\n(*.py, *.md, *.dot)" shape=parallelogram fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        wt2 [label="git status\\n(see changes)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        wt3 [label="git add <files>" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        wt4 [label="Staging Area\\n(index)" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        wt1 -> wt2 -> wt3 -> wt4 [label="stage"]
    }

    subgraph cluster_repo {
        label="Local Repository"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        r1 [label="git commit -m '...'" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        r2 [label="Local commit\\n(SHA hash)" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        r3 [label="git log\\n(history)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        r1 -> r2 -> r3
    }

    subgraph cluster_remote {
        label="Remote Repository"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        rm1 [label="git push origin main" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        rm2 [label="GitHub remote\\n(origin)" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        rm3 [label="Actions / CI\\n(optional)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        rm1 -> rm2 -> rm3
    }

    pull [label="git pull\\n(sync from remote)" style=dashed fillcolor="#0d1a1a" color="#335555" fontcolor="#557777"]

    wt4 -> r1 [label="commit"]
    r2 -> rm1 [label="push"]
    rm2 -> pull [label="pull" style=dashed color="#335555"]
    pull -> wt1 [style=dashed color="#335555"]
}
""",

# ─── 16 ─── Data Flow MNE ─────────────────────────────────────────────────────
"16_data_flow_mne": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="MNE-RSA Complete Data Flow" rankdir="TB"]

    subgraph cluster_raw {
        label="Raw Data"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        rw1 [label="MEG raw file\\n(.fif / .ds)" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        rw2 [label="EEG raw file\\n(.edf / .bdf)" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        rw3 [label="mne.read_epochs()\\nor events-based" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        rw1 -> rw3
        rw2 -> rw3
    }

    subgraph cluster_prep {
        label="Preprocessing"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        pr1 [label="Band-pass filter\\n(1–40 Hz)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        pr2 [label="ICA artifact removal" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        pr3 [label="Baseline correction" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        pr4 [label="mne.Epochs object" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        pr1 -> pr2 -> pr3 -> pr4
    }

    subgraph cluster_src {
        label="Source Space"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        sr1 [label="Freesurfer cortical surface\\n(pial / inflated)" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        sr2 [label="Forward solution\\n(BEM / sphere model)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        sr3 [label="make_inverse_operator()" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        sr4 [label="SourceEstimate (STC)\\nvertices × time" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        sr1 -> sr2 -> sr3 -> sr4
    }

    subgraph cluster_rsa {
        label="RSA"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        rs1 [label="Pairwise dissimilarity\\n(1 - correlation)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        rs2 [label="RDM: N×N matrix" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        rs3 [label="Compare to model RDM\\n(Spearman r)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        rs4 [label="RSA score per vertex" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        rs1 -> rs2 -> rs3 -> rs4
    }

    subgraph cluster_out {
        label="Output"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        ov [label="mne.viz.plot_source_estimates()" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        op [label="brain_map.png" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        ov -> op
    }

    rw3 -> pr1
    pr4 -> sr2
    sr4 -> rs1
    rs4 -> ov
}
""",

# ─── 17 ─── Ventricle Mask ────────────────────────────────────────────────────
"17_ventricle_mask": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Ventricle Thinning: Z-Axis Threshold Mask" rankdir="TB"]

    subgraph cluster_in {
        label="Input"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        vi [label="centerline points cl_pts\\n(N × 3 array)" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        vz [label="cl_pts[:,2]\\n(Z coordinates)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        vi -> vz
    }

    subgraph cluster_height {
        label="Relative Height Computation"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        h1 [label="z_min = cl_pts[:,2].min()" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        h2 [label="z_max = cl_pts[:,2].max()" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        h3 [label="zrel = (Z - z_min) / (z_max - z_min)\\nzrel ∈ [0, 1]" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        h1 -> h3
        h2 -> h3
    }

    subgraph cluster_mask {
        label="Threshold Mask"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        m1 [label="ventricle_mask =\\nnp.clip(1.2 - 1.5×zrel, 0.3, 1.0)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        m2 [label="bottom 30%: mask≈0.3 (thin)\\ntop: mask≈1.0 (full)" shape=note fillcolor="#1a1a2e" color="#ff2d78" fontcolor="#cccccc"]
        m1 -> m2 [style=dashed color="#553344"]
    }

    subgraph cluster_out {
        label="Radius Modulation"
        style="filled,rounded" fillcolor="#1a000c" color="#ff2d78" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ff2d78"

        ro1 [label="radius_abs = R × (1 - SulcusScale × P × mask)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        ro2 [label="np.clip(radius_abs, R×0.25, R×1.15)" fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        ro3 [label="per-point radius\\n(thinner near ventricles)" shape=cylinder fillcolor="#2e0014" color="#ff2d78" fontcolor="#ff2d78"]
        ro1 -> ro2 -> ro3
    }

    bio [label="Ventricles occupy lower\\n~30% of brain volume\\n→ thinner periventricular cortex" shape=note fillcolor="#1a1a2e" color="#ff2d78" fontcolor="#cccccc"]

    vz -> h1
    vz -> h2
    h3 -> m1
    m1 -> ro1
    ro3 -> bio [style=dashed color="#553344"]
}
""",

# ─── 18 ─── Tube Normals ──────────────────────────────────────────────────────
"18_tube_normals": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Tube Surface: Centerline to Geometry" rankdir="LR"]

    subgraph cluster_tan {
        label="Centerline Tangent"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        t1 [label="Centerline point P(t)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        t2 [label="Finite difference\\ndP/dt ≈ P(t+1) - P(t)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        t3 [label="Normalize tangent T" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        t1 -> t2 -> t3
    }

    subgraph cluster_frame {
        label="Frenet-Serret Frame"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        f1 [label="Arbitrary up-vector" shape=note fillcolor="#1a1a2e" color="#00ff88" fontcolor="#cccccc"]
        f2 [label="N = up × T\\n(surface normal)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        f3 [label="B = T × N\\n(binormal)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        vtk [label="VTK computes Frenet\\nframe automatically\\nvia vtkTubeFilter" shape=note fillcolor="#1a1a2e" color="#00ff88" fontcolor="#cccccc"]
        f1 -> f2 -> f3
        f3 -> vtk [style=dashed color="#335533"]
    }

    subgraph cluster_circle {
        label="Cross-Section Circle"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        cc1 [label="n_sides = 28–64\\n(polygon facets)" shape=tab fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        cc2 [label="cos(θ)×N + sin(θ)×B\\n(unit circle in local frame)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        cc3 [label="Scale by radius_profile[i]" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        cc4 [label="Circle vertices\\n(n_sides points)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        cc1 -> cc2 -> cc3 -> cc4
    }

    subgraph cluster_faces {
        label="Face Generation"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        fc1 [label="Connect consecutive\\ncircles → quad strips" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        fc2 [label="Triangulate quads\\n→ 2 triangles each" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        fc3 [label="Cap end disks\\n(capping=True)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        fc4 [label="PolyData surface\\n(watertight tube)" shape=cylinder fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        fc1 -> fc2 -> fc3 -> fc4
    }

    t3 -> f2 [label="per spline pt"]
    f3 -> cc2
    cc4 -> fc1 [label="extruded"]
}
""",

# ─── 19 ─── Parameter Space ───────────────────────────────────────────────────
"19_parameter_space": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Parameter Interaction and Trade-off Space" rankdir="LR"]

    subgraph cluster_geom {
        label="Geometric Parameters"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        g1 [label="order (2–5)" shape=tab fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        g1e [label="Computation time\\nO(8^order)" fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        g2 [label="ridge_radius (0.5–5.0 mm)" shape=tab fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        g2e [label="Self-intersection risk\\nif > cell_spacing/2" shape=diamond fillcolor="#2e0900" color="#ff6600" fontcolor="#ff6600"]
        g3 [label="spline_samples (1000–8000)" shape=tab fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        g3e [label="Smoothness vs\\nMemory / speed" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        g1 -> g1e
        g2 -> g2e
        g3 -> g3e
    }

    subgraph cluster_sulcal {
        label="Sulcal Field Parameters"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        s1 [label="SulcusScale (0–0.8)" shape=tab fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        s1e [label="Sulcus depth\\n→ biological realism" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        s2 [label="k1, k2 (frequencies 4–17)" shape=tab fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        s2e [label="Gyri count\\nper lobe" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        s3 [label="w1, w2 (harmonic weights)" shape=tab fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        s3e [label="Primary vs secondary\\ngyrification" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        s1 -> s1e
        s2 -> s2e
        s3 -> s3e
    }

    subgraph cluster_noise {
        label="Noise Parameters"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        n1 [label="wobble (0–0.5)" shape=tab fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        n1e [label="Low-freq asymmetry\\n→ naturalism" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        n2 [label="NOISE_AMP (0–0.45)" shape=tab fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        n2e [label="Perlin centerline\\nrandom folding" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        n1 -> n1e
        n2 -> n2e
    }

    subgraph cluster_post {
        label="Post-Processing"
        style="filled,rounded" fillcolor="#000d1a" color="#00bfff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00bfff"

        p1 [label="decimation (0.1–0.9)" shape=tab fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        p1e [label="File size\\n→ printability" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        p2 [label="growth_factor (1.0–2.0)" shape=tab fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        p2e [label="Outer expansion\\n→ sulcal depth" fillcolor="#001a2e" color="#00bfff" fontcolor="#00bfff"]
        p1 -> p1e
        p2 -> p2e
    }
}
""",

# ─── 20 ─── Deployment ────────────────────────────────────────────────────────
"20_deployment": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="User Deployment Workflow" rankdir="TB"]

    subgraph cluster_install {
        label="Installation"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        i1 [label="git clone\\nhttps://github.com/.../hilbertbrane" shape=parallelogram fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        i2 [label="python3 -m venv venv\\nsource venv/bin/activate" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        i3 [label="pip install -r requirements.txt\\n(pyvista, vtk, numpy, noise, matplotlib)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        i1 -> i2 -> i3
    }

    subgraph cluster_gen {
        label="Generation"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        g1 [label="./run.sh\\n(batch runner)" shape=parallelogram fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        g2 [label="HilbertGyri3.py\\n→ HilbertBrain.stl" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        g3 [label="brain_box.py\\n→ mne_rsa_dark_neon.png" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        g1 -> g2 -> g3
    }

    subgraph cluster_tune {
        label="Interactive Refinement"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        t1 [label="python interactive_tuner.py" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        t2 [label="Adjust sliders\\n(size / radius / sulcus)" shape=diamond fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        t3 [label="Mesh OK?" shape=diamond fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        t1 -> t2 -> t3
        t3 -> t2 [label="NO – adjust" style=dashed color="#335555" fontcolor="#557777"]
    }

    subgraph cluster_export {
        label="Export and Delivery"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        e1 [label="mesh.save('*.stl')" shape=parallelogram fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        e2 [label="3D Printer Slicer\\n(Cura / PrusaSlicer)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        e3 [label="WebGL Viewer\\n(Three.js / Babylon.js)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        e4 [label="Physics Sim\\n(Blender / FEA)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        e1 -> e2
        e1 -> e3
        e1 -> e4
    }

    i3 -> g1
    g3 -> t1
    t3 -> e1 [label="YES – export"]
}
""",

# ─── 21 ─── Error Handling ────────────────────────────────────────────────────
"21_error_handling": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="vary_radius API Compatibility and Error Fallbacks" rankdir="TB"]

    subgraph cluster_detect {
        label="API Detection"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        ad1 [label="inspect.signature(\\n  PolyDataFilters.tube\\n)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        ad2 [label="'vary_radius' in\\nsig.parameters?" shape=diamond fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        ad1 -> ad2
    }

    subgraph cluster_modern {
        label="Modern PyVista Path (YES)"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        mp1 [label="centerline.tube(\\n  vary_radius=\\n  'vary_radius_by_scalar'\\n)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        mp2 [label="Success: modern API" shape=ellipse fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        mp1 -> mp2
    }

    subgraph cluster_legacy {
        label="Legacy Fallback Path (NO)"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        lp1 [label="Try: radius=None,\\nscalars='radius_profile'" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        lp2 [label="VTK interprets scalars\\nas absolute radii?" shape=diamond fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        lp3 [label="Success: absolute mode" shape=ellipse fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        lp4 [label="Normalize scalars:\\nrel = radius_abs / base" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        lp5 [label="centerline.tube(\\n  radius=base,\\n  scalars='rel'\\n)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        lp6 [label="Success: relative mode" shape=ellipse fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        lp1 -> lp2
        lp2 -> lp3 [label="YES"]
        lp2 -> lp4 [label="NO"]
        lp4 -> lp5 -> lp6
    }

    compat [label="Supports PyVista 0.38+\\nand legacy VTK" shape=note fillcolor="#1a1a2e" color="#00ffe7" fontcolor="#cccccc"]

    ad2 -> mp1 [label="YES"]
    ad2 -> lp1 [label="NO"]
    lp6 -> compat [style=dashed color="#335555"]
    mp2 -> compat [style=dashed color="#335555"]
}
""",

# ─── 22 ─── STL Export ────────────────────────────────────────────────────────
"22_stl_export": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="STL Export Pipeline" rankdir="TB"]

    subgraph cluster_check {
        label="Pre-Export Checks"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        c1 [label="mesh.triangulate()\\n(ensure all-triangle faces)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        c2 [label="Is watertight?\\n(no open edges)" shape=diamond fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        c3 [label="Proceed to export" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        c4 [label="mesh.fill_holes()\\nor re-triangulate" style=dashed fillcolor="#0d1a10" color="#335533" fontcolor="#557755"]
        c1 -> c2
        c2 -> c3 [label="YES"]
        c2 -> c4 [label="NO"]
        c4 -> c2 [label="retry" style=dashed color="#335533"]
    }

    subgraph cluster_fmt {
        label="STL Binary Format"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        f1 [label="80-byte ASCII header" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        f2 [label="uint32: triangle count" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        f3 [label="Per-face loop:\\n  float32×3: normal\\n  float32×9: 3 vertices\\n  uint16: attrib byte" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        f4 [label="Binary STL file" shape=cylinder fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        f1 -> f2 -> f3 -> f4
    }

    subgraph cluster_pv {
        label="PyVista Export"
        style="filled,rounded" fillcolor="#000d07" color="#00ff88" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ff88"

        pv1 [label="mesh.save('*.stl')" shape=parallelogram fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        pv2 [label="VTK STL writer\\n(binary by default)" fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        pv3 [label="File written" shape=cylinder fillcolor="#001a0d" color="#00ff88" fontcolor="#00ff88"]
        pv1 -> pv2 -> pv3
    }

    sizes [label="HilbertBrain.stl: ~24 MB\\nHilbertGyri.stl: ~15 MB\\nhil.stl: ~1.2 MB" shape=note fillcolor="#1a1a2e" color="#00ff88" fontcolor="#cccccc"]

    c3 -> pv1 [label="validate"]
    pv3 -> sizes [style=dashed color="#335533"]
}
""",

# ─── 23 ─── CLI Interface ─────────────────────────────────────────────────────
"23_cli_interface": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="CLI Parameter Prompting Interface" rankdir="TB"]

    banner [label="=== Hilbert Brain Surface Generator ===" shape=note fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]

    subgraph cluster_hilbert {
        label="Hilbert Parameters"
        style="filled,rounded" fillcolor="#0d001a" color="#bf00ff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#bf00ff"

        h1 [label="Prompt: order\\n(2–5, default 3)" shape=parallelogram fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        h2 [label="input().strip() or '3'" fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        h3 [label="Valid int 2 ≤ order ≤ 5?" shape=diamond fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        h4 [label="Prompt: spline_samples\\n(1000–8000)" shape=parallelogram fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        h1 -> h2 -> h3
        h3 -> h4 [label="YES"]
        h3 -> h1 [label="NO – retry" style=dashed color="#553366" fontcolor="#887799"]
    }

    subgraph cluster_geom {
        label="Geometry Parameters"
        style="filled,rounded" fillcolor="#0d001a" color="#bf00ff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#bf00ff"

        gp1 [label="Prompt: ridge_radius\\n(0.5–5.0)" shape=parallelogram fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        gp2 [label="Prompt: sulcus_scale\\n(0.0–0.8)" shape=parallelogram fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        gp3 [label="Prompt: growth_factor\\n(1.0–2.0)" shape=parallelogram fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        gp1 -> gp2 -> gp3
    }

    subgraph cluster_pinch {
        label="Pinch Field Parameters"
        style="filled,rounded" fillcolor="#0d001a" color="#bf00ff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#bf00ff"

        pp [label="k1, k2, w1, w2\\nwobble, seed" shape=tab fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
    }

    subgraph cluster_out {
        label="Output Parameters"
        style="filled,rounded" fillcolor="#0d001a" color="#bf00ff" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#bf00ff"

        op1 [label="output_filename (*.stl)" shape=parallelogram fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
        op2 [label="decimation (0.1–0.9)" shape=parallelogram fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]
    }

    result [label="Return config dict\\n→ generator call" shape=cylinder fillcolor="#1a0033" color="#bf00ff" fontcolor="#bf00ff"]

    banner -> h1
    h4 -> gp1
    gp3 -> pp
    pp -> op1
    op2 -> result
    op1 -> op2
}
""",

# ─── 24 ─── Hardware Acceleration ────────────────────────────────────────────
"24_hardware_accel": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Hardware Acceleration Stack" rankdir="LR"]

    subgraph cluster_app {
        label="Application Layer"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        ap1 [label="PyVista\\n(Python API)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        ap2 [label="VTK Pipeline\\n(C++ render engine)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        ap3 [label="vtkPolyDataMapper\\nvtkActor · vtkRenderer" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        ap1 -> ap2 -> ap3
    }

    subgraph cluster_driver {
        label="Graphics Driver Layer"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        dr1 [label="OpenGL 3.3+\\n(cross-platform)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        dr2 [label="GPU Shaders\\n(GLSL vertex + fragment)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        dr3 [label="Z-buffer\\nDepth testing" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        dr4 [label="EGL (headless)\\nfor off_screen=True" style=dashed fillcolor="#0d1a1a" color="#335555" fontcolor="#557777"]
        dr1 -> dr2 -> dr3
        dr1 -> dr4 [style=dashed color="#335555"]
    }

    subgraph cluster_gpu {
        label="GPU Hardware"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        gp1 [label="Geometry stage\\n(vertex transform)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        gp2 [label="Rasterization\\n(triangle → fragments)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        gp3 [label="Fragment shading\\n(PBR materials)" fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        gp4 [label="Framebuffer\\n(RGBA + depth)" shape=cylinder fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        gp1 -> gp2 -> gp3 -> gp4
    }

    subgraph cluster_cuda {
        label="Optional CUDA"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        cu1 [label="CUDA (optional)\\nlarge mesh compute" style=dashed fillcolor="#0d1a1a" color="#335555" fontcolor="#557777"]
        cu2 [label="cuVTK acceleration" style=dashed fillcolor="#0d1a1a" color="#335555" fontcolor="#557777"]
        cu1 -> cu2 [style=dashed color="#335555"]
    }

    subgraph cluster_out {
        label="Output"
        style="filled,rounded" fillcolor="#000d0d" color="#00ffe7" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#00ffe7"

        ot1 [label="p.show()\\n(display)" shape=parallelogram fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
        ot2 [label="p.screenshot()\\n(PNG export)" shape=parallelogram fillcolor="#001a1a" color="#00ffe7" fontcolor="#00ffe7"]
    }

    ap3 -> dr1
    dr3 -> gp1
    gp4 -> ot1
    gp4 -> ot2
    cu2 -> gp1 [style=dashed color="#335555"]
}
""",

# ─── 25 ─── Future Work ───────────────────────────────────────────────────────
"25_future_work": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Future Extensions and Research Directions" rankdir="TB"]

    current [label="HilbertBrane v1\\n(current codebase)" shape=tab fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]

    subgraph cluster_alt {
        label="Alternative Geometry"
        style="filled,rounded" fillcolor="#1a1800" color="#ffe600" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ffe600"

        a1 [label="L-Systems\\n(Lindenmayer branching)" fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        a2 [label="Reaction-Diffusion\\n(Turing patterns)" fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        a3 [label="Fractal IFS\\n(iterated function systems)" fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        alt [label="Alternative folding\\ngeometries" shape=ellipse fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        a1 -> alt
        a2 -> alt
        a3 -> alt
    }

    subgraph cluster_time {
        label="Temporal Evolution"
        style="filled,rounded" fillcolor="#1a1800" color="#ffe600" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ffe600"

        t1 [label="Time-series mesh\\n(animated growth)" fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        t2 [label="Developmental stages\\n(fetal → adult)" fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        t3 [label="VTK animation export\\n(.vtk sequence)" shape=cylinder fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        t1 -> t2 -> t3
    }

    subgraph cluster_atlas {
        label="Multi-Subject Atlas"
        style="filled,rounded" fillcolor="#1a1800" color="#ffe600" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ffe600"

        at1 [label="Freesurfer subject DB" shape=cylinder fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        at2 [label="Statistical shape model\\n(PCA on vertices)" fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        at3 [label="Average cortical\\nfolding atlas" fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        at1 -> at2 -> at3
    }

    subgraph cluster_web {
        label="WebGL Integration"
        style="filled,rounded" fillcolor="#1a1800" color="#ffe600" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ffe600"

        w1 [label="STL → glTF/OBJ\\n(format conversion)" fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        w2 [label="Three.js / Babylon.js\\ninteractive viewer" fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        w3 [label="Browser-hosted\\nbrain explorer" shape=ellipse fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        w1 -> w2 -> w3
    }

    subgraph cluster_neuro {
        label="Advanced Neuroscience"
        style="filled,rounded" fillcolor="#1a1800" color="#ffe600" fontsize=12
        fontname="Helvetica,Arial,sans-serif" fontcolor="#ffe600"

        n1 [label="MEG source imaging\\n(beamformer)" fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        n2 [label="RSA on\\nHilbert topology" fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        n3 [label="Cortical connectivity\\nmap" shape=ellipse fillcolor="#2e2a00" color="#ffe600" fontcolor="#ffe600"]
        n1 -> n2 -> n3
    }

    current -> a1 [label="extend to"]
    current -> t1 [label="extend to"]
    current -> at1 [label="extend to"]
    current -> w1 [label="extend to"]
    current -> n1 [label="extend to"]
}
""",

}  # end diagrams dict


# ─── Generation ───────────────────────────────────────────────────────────────

os.makedirs("docs/diagrams_25", exist_ok=True)

for name, dot_content in diagrams.items():
    dot_path = f"docs/diagrams_25/{name}.dot"
    with open(dot_path, "w") as f:
        f.write(dot_content)

    subprocess.run(
        ["dot", "-Tpng", "-Gdpi=150", dot_path, "-o", f"docs/diagrams_25/{name}.png"],
        check=True,
    )
    subprocess.run(
        ["dot", "-Tsvg", dot_path, "-o", f"docs/diagrams_25/{name}.svg"],
        check=True,
    )
    print(f"  {name}.png + .svg")

print(f"\nGenerated {len(diagrams)} diagrams in docs/diagrams_25/")
