import napari
from functools import partial
import itertools
from skimage import data
from app_model import Application
from app_model.types import Action


def rotate_angle(viewer: napari.Viewer, ax, inc):
    current_angles = viewer.camera.angles
    new_angles = list(current_angles)
    new_angles[ax] = (new_angles[ax] + inc)
    viewer.camera.angles = tuple(new_angles)


# Note: 15 is the number of degrees each "click" on the X-touch mini
# controller takes
directions = [('decrease', -5), ('increase', 5)]
axes = (0, 1, 2)

actions = [
        Action(id=f'main.{direction}_ax{ax}',
               title=f'{direction} rotation on axis {ax}',
               callback=partial(rotate_angle, ax=ax, inc=value))
        for (direction, value), ax in itertools.product(directions, axes)
        ]

viewer, layer = napari.imshow(
        data.cells3d(),
        channel_axis=1,
        name=['membrane', 'nuclei'],
        ndisplay=3,
        )

app = Application.get_or_create('napari')
app.register_actions(actions)

napari.run()