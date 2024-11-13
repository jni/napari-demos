import numpy as np
import napari

image = np.random.random((3, 4, 5, 3, 4, 5, 8, 2, 10, 10))
viewer, layer = napari.imshow(image)

napari.run()
