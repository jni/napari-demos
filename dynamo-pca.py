from pathlib import Path
from functools import cached_property

import napari
import pandas as pd
import numpy as np
import mrcfile


class DPCAA:
    def __init__(self, eigenvolumes_dir, eigentable_file):
        self.eigenvolumes_dir = Path(eigenvolumes_dir)
        self.eigentable_file = eigentable_file

    @cached_property
    def eigenvolumes(self):
        volume_files = list(self.eigenvolumes_dir.glob('*.mrc'))
        df = pd.DataFrame({'path' : volume_files}).sort_values(by='path')
        df['eigenvolume'] = df['path'].apply(lambda x: mrcfile.open(x).data)
        eigenvolumes = np.stack(df['eigenvolume'])
        return eigenvolumes

    @cached_property
    def eigentable(self):
        return np.loadtxt(self.eigentable_file, delimiter=',')

    def spectral_average_from_coefficients(self, coefficients, normalise=True):
        coefficients = coefficients.squeeze()[..., np.newaxis, np.newaxis, np.newaxis]
        spectral_average = (coefficients * self.eigenvolumes).sum(axis=-4)

        if normalise:
            spectral_average = self._normalise_volume(spectral_average)

        return spectral_average

    def spectral_average_from_idx(self, idx):
        """generate spectral average from particles at idx
        """
        coefficients = self._coefficients_from_idx(idx)
        return self.spectral_average_from_coefficients(coefficients)

    def _coefficients_from_idx(self, idx):
        """generate coefficients from a set of particles at idx
        """
        return self.eigentable[idx, :].sum(axis=0)

    def _generate_volume_series(self, eig, n_bins=10, qcut=True):
        eig_coefficients = self.eigentable[:, eig]

        if qcut:
            cut = pd.qcut(eig_coefficients, n_bins)
        else:
            cut = pd.cut(eig_coefficients, n_bins)

        volumes = [self.spectral_average_from_idx(cut == subset) for subset in cut.categories]
        return np.stack(volumes)

    def _generate_volume_series_vectorised(self, eig, n_bins=10, qcut=True):
        eig_coefficients = self.eigentable[:, eig]

        if qcut:
            cut = pd.qcut(eig_coefficients, n_bins)
        else:
            cut = pd.cut(eig_coefficients, n_bins)

        coefficients = np.stack(
            [self._coefficients_from_idx(cut == subset) for subset in cut.categories]
        )
        volumes = self.spectral_average_from_coefficients(coefficients)
        return volumes

    def _normalise_volume(self, volume):
        """independently normalise a stack of volumes to mean 0 standard deviation 1
        """
        volume_axes = (-1, -2, -3)
        volume_mean = np.expand_dims(volume.mean(axis=volume_axes), axis=volume_axes)
        volume_std = np.expand_dims(volume.std(axis=volume_axes), axis=volume_axes)
        return (volume - volume_mean) / volume_std


folder = Path('/Users/jni/data/dynamo-pca/dynamo_pca_analysis/WM4196')
eigenvolumes = folder / 'eigenvolumes'
eigentable = folder / 'eigentable.csv'

pca = DPCAA(eigenvolumes_dir=eigenvolumes, eigentable_file=eigentable)

viewer = napari.Viewer()

n_bins = 10

volumes = np.stack([
        pca._generate_volume_series(comp, n_bins=n_bins, qcut=True)
        for comp in range(50)
        ])

viewer.add_image(volumes)
viewer.dims.axis_labels = ['pc', 'pos', 'z', 'y', 'x']

napari.run()