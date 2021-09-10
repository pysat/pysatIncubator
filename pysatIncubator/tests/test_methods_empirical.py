# -*- coding: utf-8 -*-
"""Test some of the pyglow method functions."""

import datetime as dt
import numpy as np
import os

import pytest

import pysat
from pysatIncubator.methods import empirical as mm_emp


class TestBasics():
    """Main unit tests for pyglow methods to add empirical models.

    Note
    ----
    Currently skipped in CI environments due to issues with installing pyglow
    on github actions.
    """

    def setup(self):
        """Create a clean testing setup before each method."""

        if (os.environ.get('CI') == 'true'):
            pytest.skip('pyglow tests skipped on CI')
        self.testInst = pysat.Instrument(platform='pysat', name='testing',
                                         num_samples=100, clean_level='clean')
        return

    def teardown(self):
        """Clean up test environment after each method."""

        del self
        return

    def test_add_iri_thermal_plasma(self):
        """Test adding thermal plasma data to test inst."""

        self.testInst.custom_attach(mm_emp.add_iri_thermal_plasma,
                                    kwargs={'glat_label': 'latitude',
                                            'glong_label': 'longitude',
                                            'alt_label': 'altitude'})
        self.testInst.load(date=dt.datetime(2009, 1, 1))
        targets = ['e_temp', 'frac_dens_h', 'frac_dens_he', 'frac_dens_o',
                   'ion_dens', 'ion_temp']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index
        return

    def test_add_igrf(self):
        """Test adding igrf model to test inst."""

        self.testInst.custom_attach(mm_emp.add_igrf,
                                    kwargs={'glat_label': 'latitude',
                                            'glong_label': 'longitude',
                                            'alt_label': 'altitude'})
        self.testInst.load(date=dt.datetime(2009, 1, 1))
        targets = ['B', 'B_east', 'B_north', 'B_up', 'B_ecef_x', 'B_ecef_y',
                   'B_ecef_z']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index
        return

    def test_add_msis(self):
        """Test adding msis model to test inst."""

        self.testInst.custom_attach(mm_emp.add_msis,
                                    kwargs={'glat_label': 'latitude',
                                            'glong_label': 'longitude',
                                            'alt_label': 'altitude'})
        self.testInst.load(date=dt.datetime(2009, 1, 1))
        targets = ['Nn', 'Nn_H', 'Nn_He', 'Nn_N', 'Nn_N2', 'Nn_O', 'Nn_O2',
                   'Nn_Ar', 'Tn_msis']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index
        return
