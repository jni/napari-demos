import napari

viewer = napari.Viewer()
layer = viewer.open_sample('napari', 'eagle')
dw, widg = viewer.window.add_plugin_dock_widget('napari-segment-everything')
widg.process()

napari.run()
