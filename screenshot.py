import pyvista as pv

# Save a screenshot of HilbertBrain
mesh1 = pv.read('HilbertBrain.stl')
p1 = pv.Plotter(off_screen=True, window_size=(800, 800))
p1.add_mesh(mesh1, color='lightblue', smooth_shading=True)
p1.camera_position = 'iso'
p1.screenshot('HilbertBrain_screenshot.png')

# Save a screenshot of HilbertGyri
mesh2 = pv.read('HilbertGyri.stl')
p2 = pv.Plotter(off_screen=True, window_size=(800, 800))
p2.add_mesh(mesh2, color='lightcoral', smooth_shading=True)
p2.camera_position = 'iso'
p2.screenshot('HilbertGyri_screenshot.png')
