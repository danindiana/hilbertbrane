from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch
import numpy as np

# Create figure with dark background
fig, ax = plt.subplots(1, 1, figsize=(20, 24))
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')
ax.set_xlim(0, 20)
ax.set_ylim(0, 24)
ax.axis('off')

# Neon color palette
neon_colors = {
    'pink': '#ff00ff',
    'cyan': '#00ffff',
    'green': '#39ff14',
    'yellow': '#ffff00',
    'orange': '#ff6600',
    'purple': '#bf00ff',
    'blue': '#0080ff',
    'red': '#ff0040',
    'white': '#ffffff'
}

def draw_neon_box(ax, x, y, width, height, color, text, fontsize=9, alpha=0.15):
    """Draw a neon-styled box with glow effect"""
    # Glow effect (outer)
    for i in range(3, 0, -1):
        glow = FancyBboxPatch((x - i*0.05, y - i*0.05), width + i*0.1, height + i*0.1,
                              boxstyle="round,pad=0.02", 
                              facecolor=color, alpha=0.1/i, edgecolor='none')
        ax.add_patch(glow)
    
    # Main box
    box = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02",
                         facecolor='#161b22', edgecolor=color, linewidth=2.5, alpha=0.9)
    ax.add_patch(box)
    
    # Text
    ax.text(x + width/2, y + height/2, text, ha='center', va='center',
            fontsize=fontsize, color=color, fontweight='bold',
            fontfamily='monospace')
    return box

def draw_neon_cylinder(ax, x, y, width, height, color, text, fontsize=10):
    """Draw a neon cylinder for data nodes"""
    # Top ellipse
    ellipse = mpatches.Ellipse((x + width/2, y + height), width, height*0.3, 
                               facecolor='#0a0a1a', edgecolor=color, linewidth=3)
    ax.add_patch(ellipse)
    
    # Body
    rect = Rectangle((x, y), width, height, facecolor='#0a0a1a', 
                     edgecolor=color, linewidth=2)
    ax.add_patch(rect)
    
    # Bottom ellipse
    ellipse2 = mpatches.Ellipse((x + width/2, y), width, height*0.3, 
                                facecolor='#0a0a1a', edgecolor=color, linewidth=2)
    ax.add_patch(ellipse2)
    
    # Text
    ax.text(x + width/2, y + height/2, text, ha='center', va='center',
            fontsize=fontsize, color=color, fontweight='bold',
            fontfamily='monospace')

def draw_cluster_label(ax, x, y, text, color):
    """Draw cluster label with neon effect"""
    ax.text(x, y, text, ha='center', va='center', fontsize=14, 
            color=color, fontweight='bold', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#161b22', 
                     edgecolor=color, linewidth=2, alpha=0.9))

def draw_arrow(ax, start, end, color, label='', style='solid', lw=2):
    """Draw neon arrow"""
    arrow = FancyArrowPatch(start, end, arrowstyle='->', mutation_scale=20,
                           color=color, linewidth=lw, linestyle=style,
                           connectionstyle="arc3,rad=0.1")
    ax.add_patch(arrow)
    if label:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.text(mid_x, mid_y + 0.2, label, ha='center', va='bottom',
                fontsize=8, color=color, fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#0d1117', 
                         edgecolor='none', alpha=0.8))

# ==================== TITLE ====================
ax.text(10, 23.5, '◈ MNE-RSA ARCHITECTURE ◈', ha='center', va='center',
        fontsize=24, color=neon_colors['cyan'], fontweight='bold',
        fontfamily='monospace',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#161b22', 
                 edgecolor=neon_colors['cyan'], linewidth=3))

# ==================== CORE MODULES CLUSTER ====================
# Cluster background
core_bg = FancyBboxPatch((1, 17), 8, 5.5, boxstyle="round,pad=0.1",
                         facecolor='#1a0a1a', edgecolor=neon_colors['pink'], 
                         linewidth=3, alpha=0.3, linestyle='-')
ax.add_patch(core_bg)
draw_cluster_label(ax, 5, 22, '◈ CORE RSA MODULES ◈', neon_colors['pink'])

# Core nodes
draw_neon_box(ax, 1.5, 20, 2.5, 1.2, neon_colors['pink'], 'rdm.py\n<RDM>', 10)
draw_neon_box(ax, 4.5, 20, 2.5, 1.2, neon_colors['pink'], 'folds.py\n<FOLDS>', 10)
draw_neon_box(ax, 1.5, 18, 2.5, 1.2, neon_colors['pink'], 'searchlight.py\n<SEARCH>', 9)
draw_neon_box(ax, 4.5, 18, 2.5, 1.2, neon_colors['pink'], 'rsa.py\n<RSA>', 10)

# ==================== MNE INTEGRATION CLUSTER ====================
mne_bg = FancyBboxPatch((11, 17), 8, 5.5, boxstyle="round,pad=0.1",
                        facecolor='#0a1a0a', edgecolor=neon_colors['green'], 
                        linewidth=3, alpha=0.3)
ax.add_patch(mne_bg)
draw_cluster_label(ax, 15, 22, '◈ MNE-PYTHON INTEGRATION ◈', neon_colors['green'])

# MNE nodes
draw_neon_box(ax, 11.5, 20, 3, 1.2, neon_colors['green'], 
              'sensor_level.py\n<SENSOR RSA>', 9)
draw_neon_box(ax, 11.5, 18, 3, 1.2, neon_colors['green'], 
              'source_level.py\n<SOURCE RSA>', 9)

# ==================== VISUALIZATION NODE ====================
draw_neon_box(ax, 15.5, 14, 3.5, 1.5, neon_colors['yellow'], 
              'viz.py\n<VISUALIZATION>', 11)

# ==================== EXTERNAL DEPENDENCIES CLUSTER ====================
ext_bg = FancyBboxPatch((1, 8), 18, 7, boxstyle="round,pad=0.1",
                        facecolor='#1a0f0a', edgecolor=neon_colors['orange'], 
                        linewidth=3, alpha=0.3)
ax.add_patch(ext_bg)
draw_cluster_label(ax, 10, 14.5, '◈ EXTERNAL DEPENDENCIES ◈', neon_colors['orange'])

# External nodes - row 1
draw_neon_box(ax, 1.5, 12, 2, 1, neon_colors['orange'], 'NumPy', 9)
draw_neon_box(ax, 4, 12, 2, 1, neon_colors['orange'], 'SciPy', 9)
draw_neon_box(ax, 6.5, 12, 2.5, 1, neon_colors['orange'], 'scikit-learn', 9)
draw_neon_box(ax, 9.5, 12, 2.5, 1, neon_colors['orange'], 'MNE-Python', 9)

# External nodes - row 2
draw_neon_box(ax, 1.5, 10, 2, 1, neon_colors['orange'], 'joblib', 9)
draw_neon_box(ax, 4, 10, 2.5, 1, neon_colors['orange'], 'Matplotlib', 9)
draw_neon_box(ax, 7, 10, 2, 1, neon_colors['orange'], 'Nibabel', 9)
draw_neon_box(ax, 9.5, 10, 2, 1, neon_colors['orange'], 'tqdm', 9)

# ==================== DATA FLOW NODES ====================
draw_neon_cylinder(ax, 2, 4, 3, 1.5, neon_colors['cyan'], '◉ INPUT DATA ◉', 11)
draw_neon_cylinder(ax, 15, 4, 3, 1.5, neon_colors['cyan'], '◉ RSA RESULTS ◉', 11)

# ==================== FEATURES CLUSTER ====================
feat_bg = FancyBboxPatch((6, 0.5), 8, 3, boxstyle="round,pad=0.1",
                         facecolor='#0f0a1a', edgecolor=neon_colors['purple'], 
                         linewidth=2, alpha=0.3, linestyle='--')
ax.add_patch(feat_bg)
draw_cluster_label(ax, 10, 3.2, '◈ KEY FEATURES ◈', neon_colors['purple'])

# Feature notes
features = [
    '⚡ Cross-validated RDMs',
    '⚡ Searchlight analysis', 
    '⚡ Multiple RSA metrics',
    '⚡ Surface & volume support',
    '⚡ Interactive viz'
]
for i, feat in enumerate(features):
    x_pos = 6.5 + (i % 3) * 2.5
    y_pos = 2.2 if i < 3 else 1.2
    ax.text(x_pos, y_pos, feat, ha='left', va='center', fontsize=8,
            color=neon_colors['purple'], fontfamily='monospace')

# ==================== CONNECTIONS ====================
# Core internal connections
draw_arrow(ax, (5.75, 20.6), (2.75, 20.6), neon_colors['pink'], 'uses')
draw_arrow(ax, (5.75, 20.3), (2.75, 18.9), neon_colors['pink'], 'uses')
draw_arrow(ax, (5.75, 20), (2.75, 18.3), neon_colors['pink'], 'uses')
draw_arrow(ax, (4.5, 20.3), (2.75, 20.3), neon_colors['pink'], 'feeds')
draw_arrow(ax, (4.5, 18.3), (2.75, 18.9), neon_colors['pink'], 'feeds')

# MNE to Core connections
draw_arrow(ax, (13, 20.6), (7, 20.6), neon_colors['green'], 'calls')
draw_arrow(ax, (13, 20.3), (7, 20.3), neon_colors['green'], 'calls')
draw_arrow(ax, (13, 20), (7, 18.9), neon_colors['green'], 'calls')
draw_arrow(ax, (13, 19.7), (7, 18.3), neon_colors['green'], 'calls')

draw_arrow(ax, (13, 18.6), (7, 20.6), neon_colors['green'], 'calls')
draw_arrow(ax, (13, 18.3), (7, 20.3), neon_colors['green'], 'calls')
draw_arrow(ax, (13, 18), (7, 18.9), neon_colors['green'], 'calls')
draw_arrow(ax, (13, 17.7), (7, 18.3), neon_colors['green'], 'calls')

# Visualization connections
draw_arrow(ax, (15.5, 14.75), (2.75, 21.2), neon_colors['yellow'], 'viz', lw=1.5)
draw_arrow(ax, (15.5, 14.5), (13, 21.2), neon_colors['yellow'], 'viz', lw=1.5)
draw_arrow(ax, (15.5, 14.25), (13, 19.2), neon_colors['yellow'], 'viz', lw=1.5)

# External dependencies (dashed)
# rdm dependencies
draw_arrow(ax, (2.75, 20), (2.5, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (2.75, 20), (5, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (2.75, 20), (2.5, 11), neon_colors['orange'], '', 'dashed', 1)

# folds dependencies
draw_arrow(ax, (5.75, 20), (2.5, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (5.75, 20), (7.25, 13), neon_colors['orange'], '', 'dashed', 1)

# searchlight dependencies
draw_arrow(ax, (2.75, 18), (2.5, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (2.75, 18), (5, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (2.75, 18), (7.25, 13), neon_colors['orange'], '', 'dashed', 1)

# rsa dependencies
draw_arrow(ax, (5.75, 18), (2.5, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (5.75, 18), (5, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (5.75, 18), (2.5, 11), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (5.75, 18), (10.5, 11), neon_colors['orange'], '', 'dashed', 1)

# sensor dependencies
draw_arrow(ax, (13, 20.6), (10.75, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (13, 20.6), (2.5, 13), neon_colors['orange'], '', 'dashed', 1)

# source dependencies
draw_arrow(ax, (13, 18.6), (10.75, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (13, 18.6), (2.5, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (13, 18.6), (8, 11), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (13, 18.6), (7.25, 13), neon_colors['orange'], '', 'dashed', 1)

# viz dependencies
draw_arrow(ax, (17.25, 14), (5.25, 11), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (17.25, 14), (10.75, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (17.25, 14), (2.5, 13), neon_colors['orange'], '', 'dashed', 1)
draw_arrow(ax, (17.25, 14), (5, 13), neon_colors['orange'], '', 'dashed', 1)

# Data flow connections
draw_arrow(ax, (3.5, 5.5), (13, 20.6), neon_colors['cyan'], 'Evoked', lw=2)
draw_arrow(ax, (3.5, 5.2), (13, 18.6), neon_colors['cyan'], 'STC/NIfTI', lw=2)

draw_arrow(ax, (13, 20), (15, 5.5), neon_colors['cyan'], '', lw=2)
draw_arrow(ax, (13, 18), (15, 5.2), neon_colors['cyan'], '', lw=2)

draw_arrow(ax, (16.5, 4), (17.25, 14), neon_colors['cyan'], '', lw=2)

# Add glow effect to title
for i in range(5):
    circle = Circle((10, 23.5), 4 + i*0.3, fill=False, 
                    edgecolor=neon_colors['cyan'], alpha=0.1/(i+1), linewidth=1)
    ax.add_patch(circle)

plt.tight_layout()

out_dir = Path(__file__).resolve().parent / "output"
out_dir.mkdir(parents=True, exist_ok=True)

plt.tight_layout()
plt.savefig(out_dir / "mne_rsa_dark_neon.png", dpi=150,
            facecolor="#0d1117", edgecolor="none", bbox_inches="tight")
plt.savefig(out_dir / "mne_rsa_dark_neon.svg",
            facecolor="#0d1117", edgecolor="none", bbox_inches="tight")

print("✨ Dark neon diagram generated successfully!")

