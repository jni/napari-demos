from typing import List, Tuple as Tup, Optional as Opt


import toolz as tz
from magicgui import magicgui
from magicgui.widgets import Container
import napari
import numpy as np
from skimage import io, measure
from skimage.transform import AffineTransform


@tz.curry
def next_layer_callback(viewer, event, *, image_layer0, pts_layer0, image_layer1, pts_layer1):
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
            if n1 > 3:  # we have enough points to estimate a transform
                mat = calculate_transform(pts0[:n1], pts1[:n1])
                image_layer1.affine = mat
    elif pts_layer1.selected:
        if n1 == n0:  # we just added enough points, go back to layer0
            pts_layer0.selected = True
            pts_layer1.selected = False
            pts_layer0.mode = 'add'
            viewer.layers.move(viewer.layers.index(image_layer0), -1)
            viewer.layers.move(viewer.layers.index(pts_layer0), -1)
        

@magicgui(call_button='Start', layout='vertical', viewer={'visible': False, 'label': ''})
def start_affinder(reference: napari.layers.Image, moving: napari.layers.Image, viewer : napari.Viewer):
    # make a points layer for each image
    points_layers = []
    for layer in [reference, moving]:
        data = (layer.data
                if not isinstance(layer.data, list)
                else layer.data[0]
                )
        new_layer = napari.layers.Points(
                ndim=data.ndim, name=layer.name + '_pts'
                )
        viewer.layers.append(new_layer)
        points_layers.append(new_layer)
    pts_layer0 = points_layers[0]
    pts_layer1 = points_layers[1]
    
    callback = next_layer_callback(
        image_layer0=reference,
        pts_layer0=pts_layer0,
        image_layer1=moving,
        pts_layer1=pts_layer1,
        )
    viewer.mouse_drag_callbacks.append(callback)
    close_affinder.callback.value = callback


@magicgui(
        call_button='Finish',
        callback={'visible': False, 'label': ''},
        viewer={'visible': False, 'label': ''}
        )
def close_affinder(viewer: napari.Viewer, callback=None):
    viewer.mouse_drag_callbacks.remove(callback)


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
    model.estimate(src, dst)
    return model.params


viewer = napari.Viewer()
viewer.window.add_dock_widget(start_affinder, area='right')
viewer.window.add_dock_widget(close_affinder, area='right')
napari.run()
