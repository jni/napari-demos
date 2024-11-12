import napari
import dask.array as da
import numpy as np
import h5py

f = h5py.File(
        '/Users/jni/data/kikuchi/jie/'
        'CP_Ti_abnormal_grains Specimen 1 Site 5 Map Data 4.h5oina'
        )

ebsd = f['1']['EBSD']['Data']
pat = ebsd['Processed Patterns']  # array, (npatterns, dy, dx)
nx = len(np.unique(ebsd['X']))  # patterns are along 2D scan
ny = len(np.unique(ebsd['Y']))

pat2d = da.from_array(pat, chunks=pat.chunks).reshape(
        (ny, nx) + pat.shape[-2:]
        )

viewer, layer = napari.imshow(pat2d)
viewer.dims.axis_labels = ['y', 'x', 'dy', 'dx']

napari.run()
