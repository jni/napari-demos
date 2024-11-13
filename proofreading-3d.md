---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

### interactive segmentation of 3D cells

Semi-automated methods in Python.

```{code-cell} ipython3
import napari
import numpy as np
from skimage import data

cells = data.cells3d()

viewer, (membrane_layer, nuclei_layer) = napari.imshow(
        cells,
        channel_axis=1,
        name=['membrane', 'nuclei'],
        )
```

```{code-cell} ipython3
# grab individual channels and convert to float in [0, 1]

membranes = cells[:, 0, :, :] / np.max(cells)
nuclei = cells[:, 1, :, :] / np.max(cells)
```

```{code-cell} ipython3
from skimage import filters


edges = filters.farid(nuclei)

edges_layer = viewer.add_image(
        edges,
        blending='additive',
        colormap='yellow',
        )
```

```{code-cell} ipython3
from scipy import ndimage as ndi

denoised = ndi.median_filter(nuclei, size=3)
```

```{code-cell} ipython3
li_thresholded = denoised > filters.threshold_li(denoised)

threshold_layer = viewer.add_image(
        li_thresholded,
        opacity=0.3,
        )
```

```{code-cell} ipython3
from skimage import morphology

width = 20

holes_removed = morphology.remove_small_holes(
        li_thresholded, width ** 3
        )

speckle_removed = morphology.remove_small_objects(
        holes_removed, width ** 3
        )

viewer.layers[-1].visible = False

viewer.add_image(
        speckle_removed,
        name='cleaned',
        opacity=0.3,
        );
```

```{code-cell} ipython3
from skimage import measure

labels = measure.label(speckle_removed)

viewer.layers[-1].visible = False
viewer.add_labels(
        labels,
        opacity=0.5,
        blending='translucent_no_depth'
        )
```

```{code-cell} ipython3
# Sean's solution
from scipy import ndimage as ndi
from skimage.feature import peak_local_max

spacing = [0.29, 0.26, 0.26]
distances = ndi.distance_transform_edt(
    speckle_removed, sampling=spacing
)
dt_smoothed = filters.gaussian(distances, sigma=5)
peaks = peak_local_max(dt_smoothed, min_distance=5)

pts_layer = viewer.add_points(
        peaks,
        name="sean's points",
        size=4,
        n_dimensional=True,  # points have 3D "extent"
        )
```

```{code-cell} ipython3
points_data = pts_layer.data
points_data
```

```{code-cell} ipython3
from skimage import segmentation, util

markers = util.label_points(points_data, nuclei.shape)
markers_big = morphology.dilation(markers, morphology.ball(5))

segmented = segmentation.watershed(
        edges, markers_big, mask=speckle_removed,
        )

seg_layer = viewer.add_labels(
        segmented, blending='translucent_no_depth',
        )

viewer.layers['labels'].visible = False
```
