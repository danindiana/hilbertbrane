import os
import sys

# Make the repo-root modules (hilbert_core, exporters, hilbert_gen) importable
# from tests/ regardless of pytest version or invocation directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Exporter tests read/write meshes headlessly; never pop a window.
os.environ.setdefault("PYVISTA_OFF_SCREEN", "true")
