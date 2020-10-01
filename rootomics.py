"""Functions and script to load data from Shota Teramoto et al, 2020.

https://plantmethods.biomedcentral.com/articles/10.1186/s13007-020-00612-6

Data available at:
    https://rootomics.dna.affrc.go.jp/en/results

Or by request to the author, Shota Teramoto.
"""
import os
import sys
from glob import glob
import imageio as iio
import dask
import dask.array as da
import numpy as np
import napari


def load_block(files_array, block_id):
    image = np.asarray(iio.imread(files_array[block_id[:2]]))
    return image[np.newaxis, np.newaxis]


def load_images(folder):
    """Load images from root (heh) folder.

    The root folder must contain one or more subfolders, one per timepoint.
    Each subfolder contains a 3D image stack, with each slice in the stack
    present as a separate .cb (tiff) file.

    Parameters
    ----------
    folder : str
        The root folder containing the data.

    Returns
    -------
    stacked : dask.array.Array
        The 4D stacked dataset as a dask array.
    """
    files = sorted(glob(os.path.join(folder, '*/*.cb')))
    n_folders = len(set(os.path.dirname(fn) for fn in files))
    files_array = np.array(list(files)).reshape((n_folders, -1))
    image0 = iio.imread(files_array[0, 0])
    nvols, nz = files_array.shape
    ny, nx = image0.shape
    stacked = da.map_blocks(
        load_block,
        files_array,
        chunks=((1,) * nvols, (1,) * nz, (ny,), (nx,)),
        dtype=image0.dtype,
    )
    return stacked


if __name__ == '__main__':
    vol = load_images(sys.argv[1])
    with napari.gui_qt():
        viewer = napari.view_image(vol)
