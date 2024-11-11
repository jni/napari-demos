import tifffile
import napari

image = tifffile.imread(
        '/Users/jni/data/flylight/'
        'R10D07-20130605_1_C3-f-20x-brain-GAL4-6882758.lsm'
        )
viewer, layers = napari.imshow(
        image,
        channel_axis=1,
        scale=[2, 0.5189161, 0.5189161],
        rendering='attenuated_mip',
        colormap=['gray', 'green', 'magenta'],
        name=['brain', 'R10D07-C3 (1)', 'R10D07-C3 (2)'],
        )
napari.run()
