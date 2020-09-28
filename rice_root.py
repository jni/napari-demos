import os
from glob import glob
import imageio as iio
import dask
import dask.array as da
import numpy as np
import napari


FILES = sorted(
    glob('/Users/jni/Dropbox/data/rice_root_daily_growth/*/*.cb')
)
FILES_ARRAY = np.array(list(FILES)).reshape((21, -1))
IMAGE0 = iio.imread(FILES_ARRAY[0, 0])
IMAGE0_SHAPE = IMAGE0.shape
IMAGE0_DTYPE = IMAGE0.dtype


def load_block(block_id):
    image = np.asarray(iio.imread(FILES_ARRAY[block_id[:2]]))
    return image[np.newaxis, np.newaxis]


def load_images():
    nvols, nz = FILES_ARRAY.shape
    ny, nx = IMAGE0_SHAPE
    stacked = da.map_blocks(
        load_block,
        chunks=((1,) * nvols, (1,) * nz, (ny,), (nx,)),
        dtype=IMAGE0_DTYPE,
    )
    return stacked


if __name__ == '__main__':
    vol = load_images()
    with napari.gui_qt():
        viewer = napari.view_image(vol)
