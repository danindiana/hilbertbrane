import os
import subprocess

# Color themes per category:
#   Math/Theory    (01,02,12,19): node=#AED6F1 border=#2980B9 cluster=#EBF5FB
#   Mesh/Process   (03,08,18,22): node=#A9DFBF border=#27AE60 cluster=#EAFAF1
#   Neuroscience   (04,05,09,16,17): node=#FAD7A0 border=#E67E22 cluster=#FDF2E9
#   UI/Interaction (06,23): node=#D2B4DE border=#8E44AD cluster=#F5EEF8
#   Infrastructure (07,11,14,15,20,21,24): node=#A2D9CE border=#17A589 cluster=#E8F8F5
#   Performance    (10): node=#F1948A border=#C0392B cluster=#FDEDEC
#   Materials      (13): node=#FAD390 border=#D35400 cluster=#FEF9E7
#   Future         (25): node=#FCF3CF border=#F39C12 cluster=#FDFEFE

_GRAPH_DEFAULTS = """\
    graph [
        fontname="Helvetica,Arial,sans-serif"
        bgcolor="#ffffff"
        splines=spline
        nodesep=0.6
        ranksep=0.8
        pad=0.4
        labelloc="t"
        labeljust="c"
        fontsize=14
    ]
    node [fontname="Helvetica,Arial,sans-serif" fontsize=11 style="filled,rounded" penwidth=1.5]
    edge [fontname="Helvetica,Arial,sans-serif" fontsize=9 color="#555555" penwidth=1.2]
"""

diagrams = {

# ─── 01 ─── Hilbert Curve Theory ─────────────────────────────────────────────
"01_hilbert_theory": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Hilbert Curve: Fractal Space-Filling Theory" rankdir="TB"]

    subgraph cluster_dim {
        label="Dimensionality Progression"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        d1 [label="1D Line Segment" shape=box fillcolor="#AED6F1" color="#2980B9"]
        d2 [label="2D Space-Filling Curve\\n(Order N fills unit square)" shape=box fillcolor="#AED6F1" color="#2980B9"]
        d3 [label="3D Hilbert Volume\\n(fills unit cube without self-intersection)" shape=box fillcolor="#AED6F1" color="#2980B9"]
        d1 -> d2 [label="extrude"]
        d2 -> d3 [label="extrude"]
    }

    subgraph cluster_orders {
        label="Fractal Orders"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        o1 [label="Order 1\\n8 voxels" shape=box fillcolor="#AED6F1" color="#2980B9"]
        o2 [label="Order 2\\n64 voxels" shape=box fillcolor="#AED6F1" color="#2980B9"]
        o3 [label="Order 3\\n512 voxels" shape=box fillcolor="#AED6F1" color="#2980B9"]
        o4 [label="Order 4\\n4096 voxels" shape=box fillcolor="#AED6F1" color="#2980B9"]
        o1 -> o2 -> o3 -> o4 [label="2× depth"]
    }

    subgraph cluster_props {
        label="Key Mathematical Properties"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        p1 [label="Space-Filling Property\\n(visits every voxel exactly once)" shape=ellipse fillcolor="#AED6F1" color="#2980B9"]
        p2 [label="Self-Similarity\\n(each sub-curve is a scaled copy)" shape=ellipse fillcolor="#AED6F1" color="#2980B9"]
        p3 [label="Locality Preservation\\n(nearby indices → nearby positions)" shape=ellipse fillcolor="#AED6F1" color="#2980B9"]
    }

    d3 -> p1 [label="implies"]
    d3 -> p2 [label="implies"]
    d3 -> p3 [label="implies"]
    o4 -> d3 [label="used in HilbertBrain.py" style=dashed]
}
""",

# ─── 02 ─── Mathematical Pipeline ────────────────────────────────────────────
"02_math_pipeline": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Mathematical Pipeline: Integer Index → 3D Coordinate" rankdir="LR"]

    subgraph cluster_input {
        label="Input"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"
        i1 [label="Integer Index i\\n(0 … N³-1)" shape=parallelogram fillcolor="#AED6F1" color="#2980B9"]
    }

    subgraph cluster_gray {
        label="Bitwise Gray Code Transform"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        g1 [label="Extract bit plane i\\n(x>>i)&1, (y>>i)&1, (z>>i)&1" fillcolor="#AED6F1" color="#2980B9"]
        g2 [label="Pack to prefix\\n(xb<<2)|(yb<<1)|zb" fillcolor="#AED6F1" color="#2980B9"]
        g3 [label="Apply Gray XOR\\nprefix ^= prefix >> 1" fillcolor="#AED6F1" color="#2980B9"]
        g4 [label="Accumulate\\nh |= prefix << (3*i)" fillcolor="#AED6F1" color="#2980B9"]
        g1 -> g2 -> g3 -> g4 [label="per bit"]
    }

    subgraph cluster_output {
        label="Output"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        o1 [label="Hilbert Index h" shape=cylinder fillcolor="#AED6F1" color="#2980B9"]
        o2 [label="Sort all points by h\\n→ continuous path order" fillcolor="#AED6F1" color="#2980B9"]
        o3 [label="(x, y, z) coordinate" shape=parallelogram fillcolor="#AED6F1" color="#2980B9"]
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
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        c1 [label="Hilbert Path\\n(N³ discrete integer points)" shape=cylinder fillcolor="#A9DFBF" color="#27AE60"]
        c2 [label="pv.Spline(path, N_SAMPLES)\\n→ smooth continuous centerline" fillcolor="#A9DFBF" color="#27AE60"]
        c3 [label="Arclength t ∈ [0,1]\\nnp.cumsum(segment lengths)" fillcolor="#A9DFBF" color="#27AE60"]
        c1 -> c2 [label="interpolate"]
        c2 -> c3 [label="normalize"]
    }

    subgraph cluster_rp {
        label="Radius Profile"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        r1 [label="Pinch Field P(t)\\n∈ [0, 1] per point" fillcolor="#A9DFBF" color="#27AE60"]
        r2 [label="radius_abs = R × (1 - SulcusScale × P)" fillcolor="#A9DFBF" color="#27AE60"]
        r3 [label="Attach as point_data\\n'radius_profile'" fillcolor="#A9DFBF" color="#27AE60"]
        r1 -> r2 -> r3
    }

    subgraph cluster_tube {
        label="Tube Extrusion"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        t1 [label="centerline.tube(\\n  scalars='radius_profile',\\n  n_sides=32, capping=True\\n)" fillcolor="#A9DFBF" color="#27AE60"]
        t2 [label="tube.triangulate()\\n(all-triangle faces)" fillcolor="#A9DFBF" color="#27AE60"]
        t3 [label="PolyData surface mesh\\n(watertight)" shape=cylinder fillcolor="#A9DFBF" color="#27AE60"]
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
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        h1 [label="Primary Harmonic\\nw1×(1-cos(2π·k1·t+φ1))/2\\n(k1=7..9, w1=1.0)" fillcolor="#FAD7A0" color="#E67E22"]
        h2 [label="Secondary Harmonic\\nw2×(1-cos(2π·k2·t+φ2))/2\\n(k2=13..17, w2=0.35)" fillcolor="#FAD7A0" color="#E67E22"]
        h3 [label="Low-freq Wobble\\nwobble×(1-cos(2π·1.2·t+0.7))/2" fillcolor="#FAD7A0" color="#E67E22"]
        hsum [label="Sum → P(t) raw" fillcolor="#FAD7A0" color="#E67E22"]
        h1 -> hsum
        h2 -> hsum
        h3 -> hsum
    }

    subgraph cluster_norm {
        label="Normalization"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        n1 [label="P -= P.min(); P /= P.max()" fillcolor="#FAD7A0" color="#E67E22"]
        n2 [label="P(t) normalized ∈ [0,1]" fillcolor="#FAD7A0" color="#E67E22"]
        n1 -> n2
    }

    subgraph cluster_perlin {
        label="Perlin Noise Overlay (HilbertGyri3)"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        pn1 [label="noise.pnoise1(t × freq)\\n→ per-point offset" fillcolor="#FAD7A0" color="#E67E22"]
        pn2 [label="Add to centerline XYZ\\n(organic folding)" shape=ellipse fillcolor="#FAD7A0" color="#E67E22"]
        pn1 -> pn2
    }

    subgraph cluster_out {
        label="Radius Output"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        ro1 [label="radius_abs = R×(1 - SulcusScale×P)" fillcolor="#FAD7A0" color="#E67E22"]
        ro2 [label="np.clip(radius_abs, R×0.25, R×1.15)" fillcolor="#FAD7A0" color="#E67E22"]
        ro3 [label="per-point radius array" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        ro1 -> ro2 -> ro3
    }

    phases [label="Random phases φ1, φ2\\nrng.uniform(0, 2π)" shape=note fillcolor="#FDEBD0" color="#E67E22"]
    hsum -> n1
    n2 -> ro1
    phases -> h1 [style=dashed]
    phases -> h2 [style=dashed]
}
""",

# ─── 05 ─── MNE-RSA Integration ───────────────────────────────────────────────
"05_mne_rsa_integration": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="MNE-RSA Neuroscience Integration Pipeline" rankdir="TB"]

    subgraph cluster_acq {
        label="Data Acquisition"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        a1 [label="MEG/EEG Recording" shape=parallelogram fillcolor="#FAD7A0" color="#E67E22"]
        a2 [label="mne.Epochs\\n(time-locked segments)" fillcolor="#FAD7A0" color="#E67E22"]
        a3 [label="Preprocessing\\n(filter, ICA, baseline)" fillcolor="#FAD7A0" color="#E67E22"]
        a1 -> a2 -> a3
    }

    subgraph cluster_src {
        label="Source Estimation"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        s1 [label="Forward Model\\n(BEM / sphere)" fillcolor="#FAD7A0" color="#E67E22"]
        s2 [label="Inverse Operator\\n(MNE / dSPM / sLORETA)" fillcolor="#FAD7A0" color="#E67E22"]
        s3 [label="SourceEstimate (STC)\\nvertices × time" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        s1 -> s2 -> s3
    }

    subgraph cluster_rsa {
        label="RSA Computation"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        r1 [label="RDM: pairwise dissimilarity\\n(1 - correlation)" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        r2 [label="Searchlight Analysis\\n(per-vertex sphere)" fillcolor="#FAD7A0" color="#E67E22"]
        r3 [label="Spearman / Pearson r\\nvs model RDM" fillcolor="#FAD7A0" color="#E67E22"]
        r4 [label="RSA Score Map\\n(vertex-level)" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        r1 -> r2 -> r3 -> r4
    }

    subgraph cluster_viz {
        label="Brain Visualization"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        v1 [label="brain_box.py\\nmne_rsa_dark_neon.png" shape=note fillcolor="#FAD7A0" color="#E67E22"]
        v2 [label="mne.viz /\\npyvista brain plot" fillcolor="#FAD7A0" color="#E67E22"]
        v3 [label="Surface Plot\\n(inflated / pial)" shape=ellipse fillcolor="#FAD7A0" color="#E67E22"]
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
        style="filled,rounded" fillcolor="#F5EEF8" color="#8E44AD" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        su1 [label="pv.Plotter()" fillcolor="#D2B4DE" color="#8E44AD"]
        su2 [label="add_slider_widget() × 3 sliders" fillcolor="#D2B4DE" color="#8E44AD"]
        su3 [label="initial update_mesh()" fillcolor="#D2B4DE" color="#8E44AD"]
        su1 -> su2 -> su3
    }

    subgraph cluster_sliders {
        label="Slider Events"
        style="filled,rounded" fillcolor="#F5EEF8" color="#8E44AD" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        sl1 [label="Brain Size slider\\n[20 .. 200]" shape=diamond fillcolor="#D2B4DE" color="#8E44AD"]
        sl2 [label="Gyri Radius slider\\n[0.5 .. 15]" shape=diamond fillcolor="#D2B4DE" color="#8E44AD"]
        sl3 [label="Sulcus Depth slider\\n[0 .. 0.95]" shape=diamond fillcolor="#D2B4DE" color="#8E44AD"]
        pd  [label="params dict update" fillcolor="#D2B4DE" color="#8E44AD"]
        sl1 -> pd
        sl2 -> pd
        sl3 -> pd
    }

    subgraph cluster_recompute {
        label="Mesh Recompute"
        style="filled,rounded" fillcolor="#F5EEF8" color="#8E44AD" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        m1 [label="update_mesh() callback" fillcolor="#D2B4DE" color="#8E44AD"]
        m2 [label="scale & spline\\nresample" fillcolor="#D2B4DE" color="#8E44AD"]
        m3 [label="pinch field P(t)" fillcolor="#D2B4DE" color="#8E44AD"]
        m4 [label="radius profile\\nper-point" fillcolor="#D2B4DE" color="#8E44AD"]
        m5 [label="centerline.tube()" fillcolor="#D2B4DE" color="#8E44AD"]
        m6 [label="p.remove_actor()\\np.add_mesh()" fillcolor="#D2B4DE" color="#8E44AD"]
        m1 -> m2 -> m3 -> m4 -> m5 -> m6
    }

    subgraph cluster_render {
        label="Render"
        style="filled,rounded" fillcolor="#F5EEF8" color="#8E44AD" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        rv [label="OpenGL Render" shape=ellipse fillcolor="#D2B4DE" color="#8E44AD"]
        disp [label="3D Viewport" shape=parallelogram fillcolor="#D2B4DE" color="#8E44AD"]
        rv -> disp
    }

    su3 -> m1
    pd -> m1
    m6 -> rv
    disp -> sl1 [label="user interacts" style=dashed color="#999999"]
}
""",

# ─── 07 ─── File Structure ────────────────────────────────────────────────────
"07_file_structure": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Project Directory Structure" rankdir="LR"]

    root [label="hilbertbrane/\\n(repo root)" shape=tab fillcolor="#A2D9CE" color="#17A589"]

    subgraph cluster_scripts {
        label="Generator Scripts"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        sc1 [label="Hilbertbrane.py\\n(CLI, interactive)" fillcolor="#A2D9CE" color="#17A589"]
        sc2 [label="HilbertGyri.py\\n(base generator)" fillcolor="#A2D9CE" color="#17A589"]
        sc3 [label="HilbertGyri2.py\\n(detailed)" fillcolor="#A2D9CE" color="#17A589"]
        sc4 [label="HilbertGyri3.py\\n(biological)" fillcolor="#A2D9CE" color="#17A589"]
        sc5 [label="interactive_tuner.py\\n(PyVista GUI)" fillcolor="#A2D9CE" color="#17A589"]
        sc6 [label="brain_box.py\\n(MNE-RSA diagram)" fillcolor="#A2D9CE" color="#17A589"]
        sc7 [label="run.sh\\n(batch runner)" shape=parallelogram fillcolor="#A2D9CE" color="#17A589"]
    }

    subgraph cluster_docs {
        label="docs/"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        d1 [label="architecture.dot/.png/.svg" fillcolor="#A2D9CE" color="#17A589"]
        d2 [label="diagrams_25/\\n25 × .dot + .png + .svg" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
    }

    subgraph cluster_output {
        label="Output Artifacts"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        o1 [label="HilbertBrain.stl\\n(~24 MB)" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
        o2 [label="HilbertGyri.stl\\n(~15 MB)" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
        o3 [label="*_screenshot.png" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
    }

    subgraph cluster_venv {
        label="venv/"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        v1 [label="pyvista · vtk · numpy\\nnoise · matplotlib" shape=ellipse fillcolor="#A2D9CE" color="#17A589"]
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
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        r1 [label="tube.triangulate()\\n(ensure all-triangle faces)" fillcolor="#A9DFBF" color="#27AE60"]
        r2 [label="~300k–600k cells\\n(pre-decimation)" shape=note fillcolor="#D5F5E3" color="#27AE60"]
    }

    subgraph cluster_dec {
        label="Decimation"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        d1 [label="mesh.decimate(0.30–0.45)\\n→ reduce cell count" fillcolor="#A9DFBF" color="#27AE60"]
        d2 [label="Decimated mesh\\n~100k–200k cells" shape=cylinder fillcolor="#A9DFBF" color="#27AE60"]
        d1 -> d2
    }

    subgraph cluster_nrm {
        label="Normal Computation"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        n1 [label="compute_normals(\\n  cell_normals=False,\\n  auto_orient=True\\n)" fillcolor="#A9DFBF" color="#27AE60"]
    }

    subgraph cluster_smooth {
        label="Smoothing"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        s1 [label="mesh.smooth(\\n  n_iter=30–90,\\n  relaxation_factor=0.5\\n)" fillcolor="#A9DFBF" color="#27AE60"]
        s2 [label="OR Taubin smooth\\n(HilbertGyri3 path)" style=dashed fillcolor="#D5F5E3" color="#27AE60"]
    }

    subgraph cluster_out {
        label="Output"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        o1 [label="Final mesh\\n(watertight, smooth)" shape=cylinder fillcolor="#A9DFBF" color="#27AE60"]
        o2 [label="mesh.save('*.stl')" shape=parallelogram fillcolor="#A9DFBF" color="#27AE60"]
        o1 -> o2
    }

    r1 -> d1 [label="feed"]
    d2 -> n1 [label="recompute"]
    n1 -> s1
    s1 -> o1
    s2 -> o1 [style=dashed]
}
""",

# ─── 09 ─── Biological Growth ─────────────────────────────────────────────────
"09_biological_growth": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Differential Cortical Growth Simulation" rankdir="TB"]

    subgraph cluster_state {
        label="Mesh State"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        ms1 [label="Post-smoothed PolyData" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        ms2 [label="mesh.point_normals\\n(per-vertex normal vectors)" fillcolor="#FAD7A0" color="#E67E22"]
        ms1 -> ms2
    }

    subgraph cluster_mask {
        label="Outer Surface Mask"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        mk1 [label="Z coords\\nmesh.points[:,2]" fillcolor="#FAD7A0" color="#E67E22"]
        mk2 [label="Z > Z.mean()\\n(upper ~65% of volume)" shape=diamond fillcolor="#FAD7A0" color="#E67E22"]
        mk3 [label="Outer surface mask\\n(boolean array)" fillcolor="#FAD7A0" color="#E67E22"]
        mki [label="Inner surface\\n(no displacement)" style=dashed fillcolor="#FDEBD0" color="#999999"]
        mk1 -> mk2
        mk2 -> mk3 [label="YES"]
        mk2 -> mki [label="NO" style=dashed color="#999999"]
    }

    subgraph cluster_disp {
        label="Normal Displacement"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        dp1 [label="growth_factor = 1.08–1.25" shape=tab fillcolor="#FAD7A0" color="#E67E22"]
        dp2 [label="disp = 0.25 × normals × (factor - 1.0)" fillcolor="#FAD7A0" color="#E67E22"]
        dp3 [label="mesh.points[mask] += disp[mask]" fillcolor="#FAD7A0" color="#E67E22"]
        dp4 [label="Outer expansion → buckling" shape=ellipse fillcolor="#FAD7A0" color="#E67E22"]
        dp1 -> dp2 -> dp3 -> dp4
    }

    bio [label="Biological analogy:\\ncortical white matter\\nexpansion drives folding" shape=note fillcolor="#FEF9E7" color="#E67E22"]

    ms2 -> mk1
    mk3 -> dp2
    dp4 -> bio [style=dashed]
}
""",

# ─── 10 ─── Performance Metrics ───────────────────────────────────────────────
"10_performance_metrics": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Performance and Memory Scaling by Hilbert Order" rankdir="TB"]

    subgraph cluster_o3 {
        label="Order 3"
        style="filled,rounded" fillcolor="#FDEDEC" color="#C0392B" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        p3a [label="512 voxels\\n(2³ × 2³ × 2³)" fillcolor="#F1948A" color="#C0392B"]
        p3b [label="~2000 spline pts" fillcolor="#F1948A" color="#C0392B"]
        p3c [label="~50k polys\\n(~5 MB RAM)" fillcolor="#F1948A" color="#C0392B"]
        p3d [label="< 5 seconds" fillcolor="#F1948A" color="#C0392B"]
        p3a -> p3b -> p3c -> p3d
    }

    subgraph cluster_o4 {
        label="Order 4  (default for HilbertBrain)"
        style="filled,rounded" fillcolor="#FDEDEC" color="#C0392B" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        p4a [label="4096 voxels\\n(4³ × 4³ × 4³)" fillcolor="#F1948A" color="#C0392B"]
        p4b [label="~8000 spline pts" fillcolor="#F1948A" color="#C0392B"]
        p4c [label="~300k polys\\n(~150 MB RAM)" fillcolor="#F1948A" color="#C0392B"]
        p4d [label="~30–60 seconds" fillcolor="#F1948A" color="#C0392B"]
        p4a -> p4b -> p4c -> p4d
    }

    subgraph cluster_o5 {
        label="Order 5"
        style="filled,rounded" fillcolor="#FDEDEC" color="#C0392B" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        p5a [label="32768 voxels\\n(5³ × 5³ × 5³)" fillcolor="#F1948A" color="#C0392B"]
        p5b [label="~50k+ spline pts" fillcolor="#F1948A" color="#C0392B"]
        p5c [label=">1M polys\\n(>1 GB RAM)" fillcolor="#F1948A" color="#C0392B"]
        p5d [label="several minutes" fillcolor="#F1948A" color="#C0392B"]
        p5a -> p5b -> p5c -> p5d
    }

    gpu [label="GPU VRAM\\n(VTK OpenGL buffer)" shape=cylinder fillcolor="#F1948A" color="#C0392B"]
    note1 [label="Decimation reduces\\npoly count 30–45%\\nbefore STL export" shape=note fillcolor="#FDFEFE" color="#C0392B"]

    p3d -> gpu
    p4d -> gpu
    p5d -> gpu
    gpu -> note1 [style=dashed]
}
""",

# ─── 11 ─── Script Hierarchy ──────────────────────────────────────────────────
"11_script_hierarchy": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Script Dependency Hierarchy" rankdir="TB"]

    subgraph cluster_entry {
        label="Entry Points"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        e1 [label="run.sh\\n(bash automation)" shape=parallelogram fillcolor="#A2D9CE" color="#17A589"]
        e2 [label="python3 -m venv\\npip install -r requirements.txt" fillcolor="#A2D9CE" color="#17A589"]
    }

    subgraph cluster_gen {
        label="Generator Scripts"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        g1 [label="Hilbertbrane.py\\n(CLI, interactive)" fillcolor="#A2D9CE" color="#17A589"]
        g2 [label="HilbertGyri.py\\n(base generator)" fillcolor="#A2D9CE" color="#17A589"]
        g3 [label="HilbertGyri2.py\\n(detailed, no Perlin)" fillcolor="#A2D9CE" color="#17A589"]
        g4 [label="HilbertGyri3.py\\n(biological + noise)" fillcolor="#A2D9CE" color="#17A589"]
        g5 [label="interactive_tuner.py\\n(PyVista GUI)" fillcolor="#A2D9CE" color="#17A589"]
    }

    subgraph cluster_deps {
        label="Python Dependencies"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        d1 [label="numpy\\n(arrays, linalg)" shape=ellipse fillcolor="#A2D9CE" color="#17A589"]
        d2 [label="pyvista + vtk\\n(mesh / rendering)" shape=ellipse fillcolor="#A2D9CE" color="#17A589"]
        d3 [label="noise\\n(pnoise1)" shape=ellipse fillcolor="#A2D9CE" color="#17A589"]
        d4 [label="matplotlib\\n(brain_box.py)" shape=ellipse fillcolor="#A2D9CE" color="#17A589"]
        d5 [label="inspect\\n(API compat)" shape=ellipse fillcolor="#A2D9CE" color="#17A589"]
    }

    subgraph cluster_out {
        label="Output Artifacts"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        o1 [label="HilbertGyri.stl" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
        o2 [label="HilbertBrain.stl" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
        o3 [label="mne_rsa_dark_neon.png" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
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
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        i1 [label="Grid [0, N-1]³\\n(integer Hilbert coords)" fillcolor="#AED6F1" color="#2980B9"]
        i2 [label="Normalize: path /= (N-1)\\n→ [0,1]³ unit cube" fillcolor="#AED6F1" color="#2980B9"]
        i1 -> i2
    }

    subgraph cluster_center {
        label="Centering Transform"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        c1 [label="Subtract 0.5:\\npath - 0.5\\n→ [-0.5, 0.5]³" fillcolor="#AED6F1" color="#2980B9"]
        c2 [label="Center at origin" shape=ellipse fillcolor="#AED6F1" color="#2980B9"]
        c1 -> c2
    }

    subgraph cluster_scale {
        label="Ellipsoid Scaling"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        s1 [label="Ellipsoid = [2.0, 1.3, 1.0]\\n(A-P, L-R, S-I)" shape=tab fillcolor="#AED6F1" color="#2980B9"]
        s2 [label="path × Ellipsoid\\n(axis-wise broadcast)" fillcolor="#AED6F1" color="#2980B9"]
        s3 [label="path[:,2] += 0.15\\n(occipital shift)" fillcolor="#AED6F1" color="#2980B9"]
        s1 -> s2 -> s3
    }

    subgraph cluster_axes {
        label="Brain Coordinate Space"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        ax [label="Brain-shaped ellipsoid\\nbounding volume" shape=ellipse fillcolor="#AED6F1" color="#2980B9"]
        nx [label="X: Anterior-Posterior\\n(-1.0 to +1.0)" shape=note fillcolor="#D6EAF8" color="#2980B9"]
        ny [label="Y: Left-Right\\n(-0.65 to +0.65)" shape=note fillcolor="#D6EAF8" color="#2980B9"]
        nz [label="Z: Superior-Inferior\\n(-0.5 to +0.5)" shape=note fillcolor="#D6EAF8" color="#2980B9"]
        s3 -> ax
        ax -> nx [style=dashed]
        ax -> ny [style=dashed]
        ax -> nz [style=dashed]
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
        style="filled,rounded" fillcolor="#FEF9E7" color="#D35400" fontsize=12
        fontname="Helvetica,Arial,sans-serif"
        ci [label="mesh (PolyData)\\ntriangulated surface" shape=cylinder fillcolor="#FAD390" color="#D35400"]
    }

    subgraph cluster_color {
        label="Color Assignment"
        style="filled,rounded" fillcolor="#FEF9E7" color="#D35400" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        cc1 [label="color='lightblue'\\n(or lightcoral)" fillcolor="#FAD390" color="#D35400"]
        cc2 [label="p.add_mesh(mesh,\\n  smooth_shading=True)" fillcolor="#FAD390" color="#D35400"]
        cc1 -> cc2
    }

    subgraph cluster_pbr {
        label="PBR Shading Parameters"
        style="filled,rounded" fillcolor="#FEF9E7" color="#D35400" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        pb1 [label="ambient = 0.0–0.2\\n(self-illumination)" fillcolor="#FAD390" color="#D35400"]
        pb2 [label="diffuse = 0.5–1.0\\n(Lambertian reflection)" fillcolor="#FAD390" color="#D35400"]
        pb3 [label="specular = 0–10\\n(highlight intensity)" fillcolor="#FAD390" color="#D35400"]
        pb4 [label="metallic = 0.0–0.1" fillcolor="#FAD390" color="#D35400"]
        pb5 [label="roughness = 0.5" fillcolor="#FAD390" color="#D35400"]
        pbs [label="PBR Shader\\n(VTK physically based)" fillcolor="#FAD390" color="#D35400"]
        pb1 -> pbs
        pb2 -> pbs
        pb3 -> pbs
        pb4 -> pbs
        pb5 -> pbs
    }

    subgraph cluster_light {
        label="Lighting"
        style="filled,rounded" fillcolor="#FEF9E7" color="#D35400" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        l1 [label="Key light\\n(main directional)" shape=ellipse fillcolor="#FAD390" color="#D35400"]
        l2 [label="Fill light" shape=ellipse fillcolor="#FAD390" color="#D35400"]
        l3 [label="Back light" shape=ellipse fillcolor="#FAD390" color="#D35400"]
        ogl [label="OpenGL render" fillcolor="#FAD390" color="#D35400"]
        l1 -> ogl
        l2 -> ogl
        l3 -> ogl
    }

    subgraph cluster_out {
        label="Output"
        style="filled,rounded" fillcolor="#FEF9E7" color="#D35400" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        out [label="Rendered framebuffer" fillcolor="#FAD390" color="#D35400"]
        disp [label="Display / screenshot" shape=parallelogram fillcolor="#FAD390" color="#D35400"]
        out -> disp
    }

    ci -> cc1
    cc2 -> pb1 [style=invis]
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
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        e1 [label="Xvfb (virtual framebuffer)\\nOR off_screen=True" fillcolor="#A2D9CE" color="#17A589"]
        e2 [label="pv.Plotter(\\n  off_screen=True,\\n  window_size=(800,800)\\n)" fillcolor="#A2D9CE" color="#17A589"]
        e1 -> e2
    }

    subgraph cluster_scene {
        label="Scene Assembly"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        s1 [label="pv.read('*.stl')" shape=parallelogram fillcolor="#A2D9CE" color="#17A589"]
        s2 [label="p.add_mesh(mesh,\\n  color='lightblue',\\n  smooth_shading=True)" fillcolor="#A2D9CE" color="#17A589"]
        s3 [label="p.camera_position='iso'" fillcolor="#A2D9CE" color="#17A589"]
        s1 -> s2 -> s3
    }

    subgraph cluster_cap {
        label="Capture and Export"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        c1 [label="p.screenshot(\\n  'output.png'\\n)" fillcolor="#A2D9CE" color="#17A589"]
        c2 [label="PNG file\\n(800 × 800 px)" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
        c1 -> c2
    }

    usage [label="Used in screenshot.py\\nfor automated CI/preview" shape=note fillcolor="#FDFEFE" color="#17A589"]

    e2 -> s1
    s3 -> c1
    c2 -> usage [style=dashed]
}
""",

# ─── 15 ─── Git Workflow ──────────────────────────────────────────────────────
"15_git_workflow": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Git Version Control Workflow" rankdir="LR"]

    subgraph cluster_local {
        label="Local Working Tree"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        wt1 [label="Edit files\\n(*.py, *.md, *.dot)" shape=parallelogram fillcolor="#A2D9CE" color="#17A589"]
        wt2 [label="git status\\n(see changes)" fillcolor="#A2D9CE" color="#17A589"]
        wt3 [label="git add <files>" fillcolor="#A2D9CE" color="#17A589"]
        wt4 [label="Staging Area\\n(index)" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
        wt1 -> wt2 -> wt3 -> wt4 [label="stage"]
    }

    subgraph cluster_repo {
        label="Local Repository"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        r1 [label="git commit -m '...'" fillcolor="#A2D9CE" color="#17A589"]
        r2 [label="Local commit\\n(SHA hash)" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
        r3 [label="git log\\n(history)" fillcolor="#A2D9CE" color="#17A589"]
        r1 -> r2 -> r3
    }

    subgraph cluster_remote {
        label="Remote Repository"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        rm1 [label="git push origin main" fillcolor="#A2D9CE" color="#17A589"]
        rm2 [label="GitHub remote\\n(origin)" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
        rm3 [label="Actions / CI\\n(optional)" fillcolor="#A2D9CE" color="#17A589"]
        rm1 -> rm2 -> rm3
    }

    pull [label="git pull\\n(sync from remote)" style=dashed fillcolor="#D0ECE7" color="#17A589"]

    wt4 -> r1 [label="commit"]
    r2 -> rm1 [label="push"]
    rm2 -> pull [label="pull" style=dashed color="#999999"]
    pull -> wt1 [style=dashed color="#999999"]
}
""",

# ─── 16 ─── Data Flow MNE ─────────────────────────────────────────────────────
"16_data_flow_mne": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="MNE-RSA Complete Data Flow" rankdir="TB"]

    subgraph cluster_raw {
        label="Raw Data"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        rw1 [label="MEG raw file\\n(.fif / .ds)" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        rw2 [label="EEG raw file\\n(.edf / .bdf)" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        rw3 [label="mne.read_epochs()\\nor events-based" fillcolor="#FAD7A0" color="#E67E22"]
        rw1 -> rw3
        rw2 -> rw3
    }

    subgraph cluster_prep {
        label="Preprocessing"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        pr1 [label="Band-pass filter\\n(1–40 Hz)" fillcolor="#FAD7A0" color="#E67E22"]
        pr2 [label="ICA artifact removal" fillcolor="#FAD7A0" color="#E67E22"]
        pr3 [label="Baseline correction" fillcolor="#FAD7A0" color="#E67E22"]
        pr4 [label="mne.Epochs object" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        pr1 -> pr2 -> pr3 -> pr4
    }

    subgraph cluster_src {
        label="Source Space"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        sr1 [label="Freesurfer cortical surface\\n(pial / inflated)" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        sr2 [label="Forward solution\\n(BEM / sphere model)" fillcolor="#FAD7A0" color="#E67E22"]
        sr3 [label="make_inverse_operator()" fillcolor="#FAD7A0" color="#E67E22"]
        sr4 [label="SourceEstimate (STC)\\nvertices × time" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        sr1 -> sr2 -> sr3 -> sr4
    }

    subgraph cluster_rsa {
        label="RSA"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        rs1 [label="Pairwise dissimilarity\\n(1 - correlation)" fillcolor="#FAD7A0" color="#E67E22"]
        rs2 [label="RDM: N×N matrix" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        rs3 [label="Compare to model RDM\\n(Spearman r)" fillcolor="#FAD7A0" color="#E67E22"]
        rs4 [label="RSA score per vertex" fillcolor="#FAD7A0" color="#E67E22"]
        rs1 -> rs2 -> rs3 -> rs4
    }

    subgraph cluster_out {
        label="Output"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        ov [label="mne.viz.plot_source_estimates()" fillcolor="#FAD7A0" color="#E67E22"]
        op [label="brain_map.png" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
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
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        vi [label="centerline points cl_pts\\n(N × 3 array)" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        vz [label="cl_pts[:,2]\\n(Z coordinates)" fillcolor="#FAD7A0" color="#E67E22"]
        vi -> vz
    }

    subgraph cluster_height {
        label="Relative Height Computation"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        h1 [label="z_min = cl_pts[:,2].min()" fillcolor="#FAD7A0" color="#E67E22"]
        h2 [label="z_max = cl_pts[:,2].max()" fillcolor="#FAD7A0" color="#E67E22"]
        h3 [label="zrel = (Z - z_min) / (z_max - z_min)\\nzrel ∈ [0, 1]" fillcolor="#FAD7A0" color="#E67E22"]
        h1 -> h3
        h2 -> h3
    }

    subgraph cluster_mask {
        label="Threshold Mask"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        m1 [label="ventricle_mask =\\nnp.clip(1.2 - 1.5×zrel, 0.3, 1.0)" fillcolor="#FAD7A0" color="#E67E22"]
        m2 [label="bottom 30%: mask≈0.3 (thin)\\ntop: mask≈1.0 (full)" shape=note fillcolor="#FDEBD0" color="#E67E22"]
        m1 -> m2 [style=dashed]
    }

    subgraph cluster_out {
        label="Radius Modulation"
        style="filled,rounded" fillcolor="#FDF2E9" color="#E67E22" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        ro1 [label="radius_abs = R × (1 - SulcusScale × P × mask)" fillcolor="#FAD7A0" color="#E67E22"]
        ro2 [label="np.clip(radius_abs, R×0.25, R×1.15)" fillcolor="#FAD7A0" color="#E67E22"]
        ro3 [label="per-point radius\\n(thinner near ventricles)" shape=cylinder fillcolor="#FAD7A0" color="#E67E22"]
        ro1 -> ro2 -> ro3
    }

    bio [label="Ventricles occupy lower\\n~30% of brain volume\\n→ thinner periventricular cortex" shape=note fillcolor="#FEF9E7" color="#E67E22"]

    vz -> h1
    vz -> h2
    h3 -> m1
    m1 -> ro1
    ro3 -> bio [style=dashed]
}
""",

# ─── 18 ─── Tube Normals ──────────────────────────────────────────────────────
"18_tube_normals": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Tube Surface: Centerline to Geometry" rankdir="LR"]

    subgraph cluster_tan {
        label="Centerline Tangent"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        t1 [label="Centerline point P(t)" fillcolor="#A9DFBF" color="#27AE60"]
        t2 [label="Finite difference\\ndP/dt ≈ P(t+1) - P(t)" fillcolor="#A9DFBF" color="#27AE60"]
        t3 [label="Normalize tangent T" fillcolor="#A9DFBF" color="#27AE60"]
        t1 -> t2 -> t3
    }

    subgraph cluster_frame {
        label="Frenet-Serret Frame"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        f1 [label="Arbitrary up-vector" shape=note fillcolor="#D5F5E3" color="#27AE60"]
        f2 [label="N = up × T\\n(surface normal)" fillcolor="#A9DFBF" color="#27AE60"]
        f3 [label="B = T × N\\n(binormal)" fillcolor="#A9DFBF" color="#27AE60"]
        vtk [label="VTK computes Frenet\\nframe automatically\\nvia vtkTubeFilter" shape=note fillcolor="#D5F5E3" color="#27AE60"]
        f1 -> f2 -> f3
        f3 -> vtk [style=dashed]
    }

    subgraph cluster_circle {
        label="Cross-Section Circle"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        cc1 [label="n_sides = 28–64\\n(polygon facets)" shape=tab fillcolor="#A9DFBF" color="#27AE60"]
        cc2 [label="cos(θ)×N + sin(θ)×B\\n(unit circle in local frame)" fillcolor="#A9DFBF" color="#27AE60"]
        cc3 [label="Scale by radius_profile[i]" fillcolor="#A9DFBF" color="#27AE60"]
        cc4 [label="Circle vertices\\n(n_sides points)" fillcolor="#A9DFBF" color="#27AE60"]
        cc1 -> cc2 -> cc3 -> cc4
    }

    subgraph cluster_faces {
        label="Face Generation"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        fc1 [label="Connect consecutive\\ncircles → quad strips" fillcolor="#A9DFBF" color="#27AE60"]
        fc2 [label="Triangulate quads\\n→ 2 triangles each" fillcolor="#A9DFBF" color="#27AE60"]
        fc3 [label="Cap end disks\\n(capping=True)" fillcolor="#A9DFBF" color="#27AE60"]
        fc4 [label="PolyData surface\\n(watertight tube)" shape=cylinder fillcolor="#A9DFBF" color="#27AE60"]
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
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        g1 [label="order (2–5)" shape=tab fillcolor="#AED6F1" color="#2980B9"]
        g1e [label="Computation time\\nO(8^order)" fillcolor="#F1948A" color="#C0392B"]
        g2 [label="ridge_radius (0.5–5.0 mm)" shape=tab fillcolor="#AED6F1" color="#2980B9"]
        g2e [label="Self-intersection risk\\nif > cell_spacing/2" shape=diamond fillcolor="#F1948A" color="#C0392B"]
        g3 [label="spline_samples (1000–8000)" shape=tab fillcolor="#AED6F1" color="#2980B9"]
        g3e [label="Smoothness vs\\nMemory / speed" fillcolor="#AED6F1" color="#2980B9"]
        g1 -> g1e
        g2 -> g2e
        g3 -> g3e
    }

    subgraph cluster_sulcal {
        label="Sulcal Field Parameters"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        s1 [label="SulcusScale (0–0.8)" shape=tab fillcolor="#AED6F1" color="#2980B9"]
        s1e [label="Sulcus depth\\n→ biological realism" fillcolor="#AED6F1" color="#2980B9"]
        s2 [label="k1, k2 (frequencies 4–17)" shape=tab fillcolor="#AED6F1" color="#2980B9"]
        s2e [label="Gyri count\\nper lobe" fillcolor="#AED6F1" color="#2980B9"]
        s3 [label="w1, w2 (harmonic weights)" shape=tab fillcolor="#AED6F1" color="#2980B9"]
        s3e [label="Primary vs secondary\\ngyrification" fillcolor="#AED6F1" color="#2980B9"]
        s1 -> s1e
        s2 -> s2e
        s3 -> s3e
    }

    subgraph cluster_noise {
        label="Noise Parameters"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        n1 [label="wobble (0–0.5)" shape=tab fillcolor="#AED6F1" color="#2980B9"]
        n1e [label="Low-freq asymmetry\\n→ naturalism" fillcolor="#AED6F1" color="#2980B9"]
        n2 [label="NOISE_AMP (0–0.45)" shape=tab fillcolor="#AED6F1" color="#2980B9"]
        n2e [label="Perlin centerline\\nrandom folding" fillcolor="#AED6F1" color="#2980B9"]
        n1 -> n1e
        n2 -> n2e
    }

    subgraph cluster_post {
        label="Post-Processing"
        style="filled,rounded" fillcolor="#EBF5FB" color="#2980B9" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        p1 [label="decimation (0.1–0.9)" shape=tab fillcolor="#AED6F1" color="#2980B9"]
        p1e [label="File size\\n→ printability" fillcolor="#AED6F1" color="#2980B9"]
        p2 [label="growth_factor (1.0–2.0)" shape=tab fillcolor="#AED6F1" color="#2980B9"]
        p2e [label="Outer expansion\\n→ sulcal depth" fillcolor="#AED6F1" color="#2980B9"]
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
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        i1 [label="git clone\\nhttps://github.com/.../hilbertbrane" shape=parallelogram fillcolor="#A2D9CE" color="#17A589"]
        i2 [label="python3 -m venv venv\\nsource venv/bin/activate" fillcolor="#A2D9CE" color="#17A589"]
        i3 [label="pip install -r requirements.txt\\n(pyvista, vtk, numpy, noise, matplotlib)" fillcolor="#A2D9CE" color="#17A589"]
        i1 -> i2 -> i3
    }

    subgraph cluster_gen {
        label="Generation"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        g1 [label="./run.sh\\n(batch runner)" shape=parallelogram fillcolor="#A2D9CE" color="#17A589"]
        g2 [label="HilbertGyri3.py\\n→ HilbertBrain.stl" fillcolor="#A2D9CE" color="#17A589"]
        g3 [label="brain_box.py\\n→ mne_rsa_dark_neon.png" fillcolor="#A2D9CE" color="#17A589"]
        g1 -> g2 -> g3
    }

    subgraph cluster_tune {
        label="Interactive Refinement"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        t1 [label="python interactive_tuner.py" fillcolor="#A2D9CE" color="#17A589"]
        t2 [label="Adjust sliders\\n(size / radius / sulcus)" shape=diamond fillcolor="#A2D9CE" color="#17A589"]
        t3 [label="Mesh OK?" shape=diamond fillcolor="#A2D9CE" color="#17A589"]
        t1 -> t2 -> t3
        t3 -> t2 [label="NO – adjust" style=dashed color="#999999"]
    }

    subgraph cluster_export {
        label="Export and Delivery"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        e1 [label="mesh.save('*.stl')" shape=parallelogram fillcolor="#A2D9CE" color="#17A589"]
        e2 [label="3D Printer Slicer\\n(Cura / PrusaSlicer)" fillcolor="#A2D9CE" color="#17A589"]
        e3 [label="WebGL Viewer\\n(Three.js / Babylon.js)" fillcolor="#A2D9CE" color="#17A589"]
        e4 [label="Physics Sim\\n(Blender / FEA)" fillcolor="#A2D9CE" color="#17A589"]
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
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        ad1 [label="inspect.signature(\\n  PolyDataFilters.tube\\n)" fillcolor="#A2D9CE" color="#17A589"]
        ad2 [label="'vary_radius' in\\nsig.parameters?" shape=diamond fillcolor="#A2D9CE" color="#17A589"]
        ad1 -> ad2
    }

    subgraph cluster_modern {
        label="Modern PyVista Path (YES)"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        mp1 [label="centerline.tube(\\n  vary_radius=\\n  'vary_radius_by_scalar'\\n)" fillcolor="#A2D9CE" color="#17A589"]
        mp2 [label="Success: modern API" shape=ellipse fillcolor="#A2D9CE" color="#17A589"]
        mp1 -> mp2
    }

    subgraph cluster_legacy {
        label="Legacy Fallback Path (NO)"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        lp1 [label="Try: radius=None,\\nscalars='radius_profile'" fillcolor="#A2D9CE" color="#17A589"]
        lp2 [label="VTK interprets scalars\\nas absolute radii?" shape=diamond fillcolor="#A2D9CE" color="#17A589"]
        lp3 [label="Success: absolute mode" shape=ellipse fillcolor="#A2D9CE" color="#17A589"]
        lp4 [label="Normalize scalars:\\nrel = radius_abs / base" fillcolor="#A2D9CE" color="#17A589"]
        lp5 [label="centerline.tube(\\n  radius=base,\\n  scalars='rel'\\n)" fillcolor="#A2D9CE" color="#17A589"]
        lp6 [label="Success: relative mode" shape=ellipse fillcolor="#A2D9CE" color="#17A589"]
        lp1 -> lp2
        lp2 -> lp3 [label="YES"]
        lp2 -> lp4 [label="NO"]
        lp4 -> lp5 -> lp6
    }

    compat [label="Supports PyVista 0.38+\\nand legacy VTK" shape=note fillcolor="#FDFEFE" color="#17A589"]

    ad2 -> mp1 [label="YES"]
    ad2 -> lp1 [label="NO"]
    lp6 -> compat [style=dashed]
    mp2 -> compat [style=dashed]
}
""",

# ─── 22 ─── STL Export ────────────────────────────────────────────────────────
"22_stl_export": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="STL Export Pipeline" rankdir="TB"]

    subgraph cluster_check {
        label="Pre-Export Checks"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        c1 [label="mesh.triangulate()\\n(ensure all-triangle faces)" fillcolor="#A9DFBF" color="#27AE60"]
        c2 [label="Is watertight?\\n(no open edges)" shape=diamond fillcolor="#A9DFBF" color="#27AE60"]
        c3 [label="Proceed to export" fillcolor="#A9DFBF" color="#27AE60"]
        c4 [label="mesh.fill_holes()\\nor re-triangulate" style=dashed fillcolor="#D5F5E3" color="#27AE60"]
        c1 -> c2
        c2 -> c3 [label="YES"]
        c2 -> c4 [label="NO"]
        c4 -> c2 [label="retry" style=dashed]
    }

    subgraph cluster_fmt {
        label="STL Binary Format"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        f1 [label="80-byte ASCII header" fillcolor="#A9DFBF" color="#27AE60"]
        f2 [label="uint32: triangle count" fillcolor="#A9DFBF" color="#27AE60"]
        f3 [label="Per-face loop:\\n  float32×3: normal\\n  float32×9: 3 vertices\\n  uint16: attrib byte" fillcolor="#A9DFBF" color="#27AE60"]
        f4 [label="Binary STL file" shape=cylinder fillcolor="#A9DFBF" color="#27AE60"]
        f1 -> f2 -> f3 -> f4
    }

    subgraph cluster_pv {
        label="PyVista Export"
        style="filled,rounded" fillcolor="#EAFAF1" color="#27AE60" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        pv1 [label="mesh.save('*.stl')" shape=parallelogram fillcolor="#A9DFBF" color="#27AE60"]
        pv2 [label="VTK STL writer\\n(binary by default)" fillcolor="#A9DFBF" color="#27AE60"]
        pv3 [label="File written" shape=cylinder fillcolor="#A9DFBF" color="#27AE60"]
        pv1 -> pv2 -> pv3
    }

    sizes [label="HilbertBrain.stl: ~24 MB\\nHilbertGyri.stl: ~15 MB\\nhil.stl: ~1.2 MB" shape=note fillcolor="#FDFEFE" color="#27AE60"]

    c3 -> pv1 [label="validate"]
    pv3 -> sizes [style=dashed]
    f4 -> pv3 [style=invis]
}
""",

# ─── 23 ─── CLI Interface ─────────────────────────────────────────────────────
"23_cli_interface": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="CLI Parameter Prompting Interface" rankdir="TB"]

    banner [label="=== Hilbert Brain Surface Generator ===" shape=note fillcolor="#D2B4DE" color="#8E44AD"]

    subgraph cluster_hilbert {
        label="Hilbert Parameters"
        style="filled,rounded" fillcolor="#F5EEF8" color="#8E44AD" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        h1 [label="Prompt: order\\n(2–5, default 3)" shape=parallelogram fillcolor="#D2B4DE" color="#8E44AD"]
        h2 [label="input().strip() or '3'" fillcolor="#D2B4DE" color="#8E44AD"]
        h3 [label="Valid int 2 ≤ order ≤ 5?" shape=diamond fillcolor="#D2B4DE" color="#8E44AD"]
        h4 [label="Prompt: spline_samples\\n(1000–8000)" shape=parallelogram fillcolor="#D2B4DE" color="#8E44AD"]
        h1 -> h2 -> h3
        h3 -> h4 [label="YES"]
        h3 -> h1 [label="NO – retry" style=dashed color="#999999"]
    }

    subgraph cluster_geom {
        label="Geometry Parameters"
        style="filled,rounded" fillcolor="#F5EEF8" color="#8E44AD" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        gp1 [label="Prompt: ridge_radius\\n(0.5–5.0)" shape=parallelogram fillcolor="#D2B4DE" color="#8E44AD"]
        gp2 [label="Prompt: sulcus_scale\\n(0.0–0.8)" shape=parallelogram fillcolor="#D2B4DE" color="#8E44AD"]
        gp3 [label="Prompt: growth_factor\\n(1.0–2.0)" shape=parallelogram fillcolor="#D2B4DE" color="#8E44AD"]
        gp1 -> gp2 -> gp3
    }

    subgraph cluster_pinch {
        label="Pinch Field Parameters"
        style="filled,rounded" fillcolor="#F5EEF8" color="#8E44AD" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        pp [label="k1, k2, w1, w2\\nwobble, seed" shape=tab fillcolor="#D2B4DE" color="#8E44AD"]
    }

    subgraph cluster_out {
        label="Output Parameters"
        style="filled,rounded" fillcolor="#F5EEF8" color="#8E44AD" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        op1 [label="output_filename (*.stl)" shape=parallelogram fillcolor="#D2B4DE" color="#8E44AD"]
        op2 [label="decimation (0.1–0.9)" shape=parallelogram fillcolor="#D2B4DE" color="#8E44AD"]
    }

    result [label="Return config dict\\n→ generator call" shape=cylinder fillcolor="#D2B4DE" color="#8E44AD"]

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
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        ap1 [label="PyVista\\n(Python API)" fillcolor="#A2D9CE" color="#17A589"]
        ap2 [label="VTK Pipeline\\n(C++ render engine)" fillcolor="#A2D9CE" color="#17A589"]
        ap3 [label="vtkPolyDataMapper\\nvtkActor · vtkRenderer" fillcolor="#A2D9CE" color="#17A589"]
        ap1 -> ap2 -> ap3
    }

    subgraph cluster_driver {
        label="Graphics Driver Layer"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        dr1 [label="OpenGL 3.3+\\n(cross-platform)" fillcolor="#A2D9CE" color="#17A589"]
        dr2 [label="GPU Shaders\\n(GLSL vertex + fragment)" fillcolor="#A2D9CE" color="#17A589"]
        dr3 [label="Z-buffer\\nDepth testing" fillcolor="#A2D9CE" color="#17A589"]
        dr4 [label="EGL (headless)\\nfor off_screen=True" style=dashed fillcolor="#D0ECE7" color="#17A589"]
        dr1 -> dr2 -> dr3
        dr1 -> dr4 [style=dashed]
    }

    subgraph cluster_gpu {
        label="GPU Hardware"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        gp1 [label="Geometry stage\\n(vertex transform)" fillcolor="#A2D9CE" color="#17A589"]
        gp2 [label="Rasterization\\n(triangle → fragments)" fillcolor="#A2D9CE" color="#17A589"]
        gp3 [label="Fragment shading\\n(PBR materials)" fillcolor="#A2D9CE" color="#17A589"]
        gp4 [label="Framebuffer\\n(RGBA + depth)" shape=cylinder fillcolor="#A2D9CE" color="#17A589"]
        gp1 -> gp2 -> gp3 -> gp4
    }

    subgraph cluster_cuda {
        label="Optional CUDA"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        cu1 [label="CUDA (optional)\\nlarge mesh compute" style=dashed fillcolor="#D0ECE7" color="#17A589"]
        cu2 [label="cuVTK acceleration" style=dashed fillcolor="#D0ECE7" color="#17A589"]
        cu1 -> cu2 [style=dashed]
    }

    subgraph cluster_out {
        label="Output"
        style="filled,rounded" fillcolor="#E8F8F5" color="#17A589" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        ot1 [label="p.show()\\n(display)" shape=parallelogram fillcolor="#A2D9CE" color="#17A589"]
        ot2 [label="p.screenshot()\\n(PNG export)" shape=parallelogram fillcolor="#A2D9CE" color="#17A589"]
    }

    ap3 -> dr1
    dr3 -> gp1
    gp4 -> ot1
    gp4 -> ot2
    cu2 -> gp1 [style=dashed color="#999999"]
}
""",

# ─── 25 ─── Future Work ───────────────────────────────────────────────────────
"25_future_work": """\
digraph G {
""" + _GRAPH_DEFAULTS + """\
    graph [label="Future Extensions and Research Directions" rankdir="TB"]

    current [label="HilbertBrane v1\\n(current codebase)" shape=tab fillcolor="#FCF3CF" color="#F39C12"]

    subgraph cluster_alt {
        label="Alternative Geometry"
        style="filled,rounded" fillcolor="#FDFEFE" color="#F39C12" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        a1 [label="L-Systems\\n(Lindenmayer branching)" fillcolor="#FCF3CF" color="#F39C12"]
        a2 [label="Reaction-Diffusion\\n(Turing patterns)" fillcolor="#FCF3CF" color="#F39C12"]
        a3 [label="Fractal IFS\\n(iterated function systems)" fillcolor="#FCF3CF" color="#F39C12"]
        alt [label="Alternative folding\\ngeometries" shape=ellipse fillcolor="#FCF3CF" color="#F39C12"]
        a1 -> alt
        a2 -> alt
        a3 -> alt
    }

    subgraph cluster_time {
        label="Temporal Evolution"
        style="filled,rounded" fillcolor="#FDFEFE" color="#F39C12" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        t1 [label="Time-series mesh\\n(animated growth)" fillcolor="#FCF3CF" color="#F39C12"]
        t2 [label="Developmental stages\\n(fetal → adult)" fillcolor="#FCF3CF" color="#F39C12"]
        t3 [label="VTK animation export\\n(.vtk sequence)" shape=cylinder fillcolor="#FCF3CF" color="#F39C12"]
        t1 -> t2 -> t3
    }

    subgraph cluster_atlas {
        label="Multi-Subject Atlas"
        style="filled,rounded" fillcolor="#FDFEFE" color="#F39C12" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        at1 [label="Freesurfer subject DB" shape=cylinder fillcolor="#FCF3CF" color="#F39C12"]
        at2 [label="Statistical shape model\\n(PCA on vertices)" fillcolor="#FCF3CF" color="#F39C12"]
        at3 [label="Average cortical\\nfolding atlas" fillcolor="#FCF3CF" color="#F39C12"]
        at1 -> at2 -> at3
    }

    subgraph cluster_web {
        label="WebGL Integration"
        style="filled,rounded" fillcolor="#FDFEFE" color="#F39C12" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        w1 [label="STL → glTF/OBJ\\n(format conversion)" fillcolor="#FCF3CF" color="#F39C12"]
        w2 [label="Three.js / Babylon.js\\ninteractive viewer" fillcolor="#FCF3CF" color="#F39C12"]
        w3 [label="Browser-hosted\\nbrain explorer" shape=ellipse fillcolor="#FCF3CF" color="#F39C12"]
        w1 -> w2 -> w3
    }

    subgraph cluster_neuro {
        label="Advanced Neuroscience"
        style="filled,rounded" fillcolor="#FDFEFE" color="#F39C12" fontsize=12
        fontname="Helvetica,Arial,sans-serif"

        n1 [label="MEG source imaging\\n(beamformer)" fillcolor="#FCF3CF" color="#F39C12"]
        n2 [label="RSA on\\nHilbert topology" fillcolor="#FCF3CF" color="#F39C12"]
        n3 [label="Cortical connectivity\\nmap" shape=ellipse fillcolor="#FCF3CF" color="#F39C12"]
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
