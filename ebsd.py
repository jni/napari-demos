import sys
import napari
import dask.array as da
import numpy as np
import h5py
from pathlib import Path

# modify fn for your local storage or use sys.argv
fn = Path(
        '~/Dropbox/data/kikuchi/CP-Ti-abnormal-grains-spec-1-site-5.h5oina'
        ).expanduser()
path = sys.argv[1] if len(sys.argv) > 1 else fn

f = h5py.File(path)

ebsd = f['1/EBSD']
pat = ebsd['Data/Processed Patterns']  # array, (npatterns, dy, dx)
nx = ebsd['Header/X Cells'][0]  # patterns are along 2D scan
ny = ebsd['Header/Y Cells'][0]

pat2d = da.from_array(pat, chunks=pat.chunks).reshape(
        (ny, nx) + pat.shape[-2:]
        )

viewer, layer = napari.imshow(pat2d)
viewer.dims.axis_labels = ['y', 'x', 'dy', 'dx']

napari.run()
