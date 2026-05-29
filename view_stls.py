import pyvista as pv
import sys

# Write log to file to catch any issues
with open("viewer_log.txt", "w") as f:
    f.write("Starting viewer...\n")

    p = pv.Plotter(shape=(1, 2), window_size=(1600, 800))

    f.write("Loading HilbertBrain.stl...\n")
    p.subplot(0, 0)
    try:
        mesh1 = pv.read('HilbertBrain.stl')
        f.write(f"HilbertBrain.stl loaded. Points: {mesh1.n_points}, Cells: {mesh1.n_cells}\n")
        p.add_mesh(mesh1, color='lightblue', smooth_shading=True)
        p.add_text("HilbertBrain.stl", font_size=12)
        f.write("HilbertBrain.stl added to plotter.\n")
    except Exception as e:
        f.write(f"Error loading HilbertBrain.stl: {e}\n")
        p.add_text(f"Error: {e}")

    f.write("Loading HilbertGyri.stl...\n")
    p.subplot(0, 1)
    try:
        mesh2 = pv.read('HilbertGyri.stl')
        f.write(f"HilbertGyri.stl loaded. Points: {mesh2.n_points}, Cells: {mesh2.n_cells}\n")
        p.add_mesh(mesh2, color='lightcoral', smooth_shading=True)
        p.add_text("HilbertGyri.stl", font_size=12)
        f.write("HilbertGyri.stl added to plotter.\n")
    except Exception as e:
        f.write(f"Error loading HilbertGyri.stl: {e}\n")
        p.add_text(f"Error: {e}")

    p.link_views()
    f.write("Showing plotter...\n")

p.show(title="Hilbertbrane 3D Viewer")
