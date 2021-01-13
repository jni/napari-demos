from typing import List, Tuple as Tup, Optional as Opt


import toolz as tz
from magicgui import magicgui
from magicgui.widgets import Container
import napari
import numpy as np
from skimage import io, measure
from skimage.transform import AffineTransform


@tz.curry
def next_layer_callback(value, *args, viewer, event, image_layer0, pts_layer0, image_layer1, pts_layer1):
    pts0, pts1 = pts_layer0.data, pts_layer1.data
    n0, n1 = len(pts0), len(pts1)
    if pts_layer0.selected:
        if n0 < 3:
            return
        if n0 > n1:
            pts_layer0.selected = False
            pts_layer1.selected = True
            pts_layer1.mode == 'add'
            viewer.layers.move(viewer.layers.index(image_layer1), -1)
            viewer.layers.move(viewer.layers.index(pts_layer1), -1)
    elif pts_layer1.selected:
        if n1 == n0:  # we just added enough points, estimate transform, go back to layer0
            if n0 > 2:
                mat = calculate_transform(pts0, pts1)
                print(mat)
                image_layer1.affine = mat
                print(image_layer1.affine.affine_matrix)
            pts_layer0.selected = True
            pts_layer1.selected = False
            pts_layer0.mode = 'add'
            viewer.layers.move(viewer.layers.index(image_layer0), -1)
            viewer.layers.move(viewer.layers.index(pts_layer0), -1)
        

@magicgui(call_button='Start', layout='vertical', viewer={'visible': False, 'label': ' '})
def start_affinder(reference: napari.layers.Image, moving: napari.layers.Image, viewer : napari.Viewer):
    # make a points layer for each image
    points_layers = []
    # Use C0 and C1 from matplotlib color cycle
    for layer, color in [(reference, (0.122, 0.467, 0.706, 1.0)), (moving, (1.0, 0.498, 0.055, 1.0))]:
        new_layer = napari.layers.Points(
                ndim=layer.ndim, name=layer.name + '_pts'
                )
        new_layer.current_face_color = color
        viewer.layers.append(new_layer)
        points_layers.append(new_layer)
    pts_layer0 = points_layers[0]
    pts_layer1 = points_layers[1]
    
    # make a callback for points added
    callback = next_layer_callback(
        viewer=viewer,
        event=None,
        image_layer0=reference,
        pts_layer0=pts_layer0,
        image_layer1=moving,
        pts_layer1=pts_layer1,
        )
    pts_layer0.events.data.connect(callback)
    pts_layer1.events.data.connect(callback)
    close_affinder.layers.value = [pts_layer0, pts_layer1]
    close_affinder.callback.value = callback

    # get the layer order started
    for layer in [moving, pts_layer1, reference, pts_layer0]:
        viewer.layers.move(viewer.layers.index(layer), -1)
    
    viewer.layers.unselect_all()
    pts_layer0.selected = True
    pts_layer0.mode = 'add'


@magicgui(
        call_button='Finish',
        callback={'visible': False, 'label': ' '},
        layers={'visible': False, 'label': ' '}
        )
def close_affinder(layers, callback=None):
    for layer in layers:
        layer.events.data.disconnect(callback)


# affinder = Container(widgets=[start_affinder, close_affinder], layout='vertical')

def calculate_transform(src, dst, model=AffineTransform()):
    """Calculate transformation matrix from matched coordinate pairs.

    Parameters
    ----------
    src : ndarray
        Matched row, column coordinates from source image.
    dst : ndarray
        Matched row, column coordinates from destination image.
    model : scikit-image transformation class, optional.
        By default, model=AffineTransform()
    Returns
    -------
    ndarray
        Transformation matrix.
    """
    print(src)
    print(dst)
    model.estimate(dst, src)  # we want the inverse
    return model.params


viewer = napari.Viewer()
viewer.window.add_dock_widget(start_affinder, area='right')
viewer.window.add_dock_widget(close_affinder, area='right')
napari.run()