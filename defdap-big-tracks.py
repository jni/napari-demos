import napari
import pandas as pd
from napari_defdap._tracks import tracks_from_seg

viewer = napari.Viewer()
shear_layer, grains_layer, phase_layer = viewer.open(
        '/Users/jni/data/jie-tracking-grains/Jie_steel_data_8_steps/'
        'time-series-8steps.defdap.yml',
        plugin='napari-defdap'
        )

seg = grains_layer.data

tracks = tracks_from_seg(seg, time_axis=0)
tracks_data = pd.DataFrame(
    tracks,
    columns=['track_id', 't', 'y', 'x'],
)

pts_layer = viewer.add_points(tracks[:, 1:], size=3, scale=grains_layer.scale)
trk_layer = viewer.add_tracks(
        tracks, scale=grains_layer.scale, features=tracks_data
        )

if __name__ == '__main__':
    napari.run()
