#!/usr/bin/env bash
#
# run.sh -- build the venv (if needed) and generate every Hilbertbrane mesh
# using the single unified generator. Each preset writes a DISTINCT file, so
# nothing overwrites anything (the old script had Gyri and Gyri2 colliding on
# HilbertGyri.stl).
#
# Usage:
#   ./run.sh                 # generate all preset meshes
#   ./run.sh --preview       # ... and open each in a window
#   ./run.sh --repair        # ... and watertight-repair before saving
#   ./run.sh gyri3           # generate only the named preset(s)
#
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
VENV="${VENV:-venv}"

# ---- venv ------------------------------------------------------------------
if [ ! -d "$VENV" ]; then
    echo ">> creating virtual environment in $VENV"
    "$PYTHON" -m venv "$VENV"
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
    pip install --upgrade pip
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    else
        pip install pyvista numpy noise matplotlib
    fi
else
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
fi

# ---- collect flags vs. preset names ----------------------------------------
EXTRA_FLAGS=()
PRESETS=()
for arg in "$@"; do
    case "$arg" in
        -*) EXTRA_FLAGS+=("$arg") ;;   # pass-through flags (--preview, --repair, ...)
        *)  PRESETS+=("$arg") ;;       # explicit preset names
    esac
done
if [ "${#PRESETS[@]}" -eq 0 ]; then
    PRESETS=(gyri gyri2 gyri3)
fi

# ---- generate --------------------------------------------------------------
for preset in "${PRESETS[@]}"; do
    echo ">> generating preset: $preset"
    "$PYTHON" hilbert_gen.py --preset "$preset" "${EXTRA_FLAGS[@]}"
done

# ---- MNE-RSA architecture diagram (unchanged) ------------------------------
if [ -f brain_box.py ]; then
    echo ">> generating MNE-RSA architecture diagram"
    "$PYTHON" brain_box.py
fi

echo ">> done. STL files:"
ls -1 ./*.stl 2>/dev/null || echo "  (none found)"
