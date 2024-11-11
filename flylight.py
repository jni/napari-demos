import tifffile
import napari

image = tifffile.imread(
        '/Users/jni/data/flylight/'
        'SS01491-20140729_31_B1-m-20x-brain-Split_GAL4-6945546.lsm'
        )
viewer, layers = napari.imshow(
        image,
        channel_axis=1,
        scale=[2, 0.5189161, 0.5189161],
        rendering='attenuated_mip',
        colormap=['gray', 'green', 'magenta'],
        )
napari.run()
