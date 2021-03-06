# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2018, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

""" HDF5 Driver """

import os
import logging
from qiskit.chemistry.drivers import BaseDriver
from qiskit.chemistry import QMolecule

logger = logging.getLogger(__name__)


class HDF5Driver(BaseDriver):
    """Python implementation of a hdf5 driver."""

    KEY_HDF5_INPUT = 'hdf5_input'

    def __init__(self, hdf5_input=None):
        """
        Initializer
        Args:
            hdf5_input (str): path to hdf5 file
        """
        if hdf5_input is None:
            hdf5_input = "molecule.hdf5"

        super().__init__()
        self._hdf5_input = hdf5_input
        self._work_path = None

    @property
    def work_path(self):
        """ returns work path """
        return self._work_path

    @work_path.setter
    def work_path(self, new_work_path):
        """ sets work path """
        self._work_path = new_work_path

    def run(self):
        hdf5_file = self._hdf5_input
        if self.work_path is not None and not os.path.isabs(hdf5_file):
            hdf5_file = os.path.abspath(os.path.join(self.work_path, hdf5_file))

        if not os.path.isfile(hdf5_file):
            raise LookupError('HDF5 file not found: {}'.format(hdf5_file))

        molecule = QMolecule(hdf5_file)
        molecule.load()
        return molecule
