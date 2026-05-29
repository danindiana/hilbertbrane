#!/usr/bin/env bash
# Quick script to run all generation tools in the hilbertbrane directory

# Setup venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install pyvista noise numpy matplotlib
else
    source venv/bin/activate
fi

echo "Generating HilbertGyri.stl..."
python HilbertGyri.py

echo "Generating HilbertGyri2..."
python HilbertGyri2.py

echo "Generating HilbertGyri3..."
python HilbertGyri3.py

echo "Generating MNE-RSA architecture diagram..."
python brain_box.py

echo "All generation tasks complete!"
