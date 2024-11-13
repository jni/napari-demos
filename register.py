import napari
import tifffile


em = tifffile.imread(
        '/Users/jni/data/demarco/worm_scanning-electron-microscopy.tif'
        )
fluo = tifffile.imread(
        '/Users/jni/data/demarco/worm_fluorescence-microscopy.tif'
)

viewer = napari.Viewer()

em_layer = viewer.add_image(em, opacity=0.7)
fluo_layer = viewer.add_image(fluo, opacity=0.7)

dw, widg = viewer.window.add_plugin_dock_widget('affinder')

napari.run()