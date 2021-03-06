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

""" PyQuante Driver """

import importlib
from enum import Enum
import logging
from qiskit.aqua.utils.validation import validate
from qiskit.chemistry.drivers import BaseDriver, UnitsType, HFMethodType
from qiskit.chemistry import QiskitChemistryError
from qiskit.chemistry.drivers.pyquanted.integrals import compute_integrals

logger = logging.getLogger(__name__)


class BasisType(Enum):
    """ Basis Type """
    BSTO3G = 'sto3g'
    B631G = '6-31g'
    B631GSS = '6-31g**'


class PyQuanteDriver(BaseDriver):
    """Python implementation of a PyQuante driver."""

    KEY_UNITS = 'units'
    KEY_BASIS = 'basis'

    _INPUT_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "id": "pyquante_schema",
        "type": "object",
        "properties": {
            "atoms": {
                "type": "string",
                "default": "H 0.0 0.0 0.0; H 0.0 0.0 0.735"
            },
            KEY_UNITS: {
                "type": "string",
                "default": UnitsType.ANGSTROM.value,
                "enum": [
                    UnitsType.ANGSTROM.value,
                    UnitsType.BOHR.value,
                ]
            },
            "charge": {
                "type": "integer",
                "default": 0
            },
            "multiplicity": {
                "type": "integer",
                "default": 1
            },
            KEY_BASIS: {
                "type": "string",
                "default": BasisType.BSTO3G.value,
                "enum": [
                    BasisType.BSTO3G.value,
                    BasisType.B631G.value,
                    BasisType.B631GSS.value,
                ]
            },
            "hf_method": {
                "type": "string",
                "default": HFMethodType.RHF.value,
                "enum": [
                    HFMethodType.RHF.value,
                    HFMethodType.ROHF.value,
                    HFMethodType.UHF.value
                ]
            },
            "tol": {
                "type": "number",
                "default": 1e-08
            },
            "maxiters": {
                "type": "integer",
                "default": 100,
                "minimum": 1
            }
        }
    }

    def __init__(self,
                 atoms,
                 units=UnitsType.ANGSTROM,
                 charge=0,
                 multiplicity=1,
                 basis=BasisType.BSTO3G,
                 hf_method=HFMethodType.RHF,
                 tol=1e-8,
                 maxiters=100):
        """
        Initializer
        Args:
            atoms (str or list): atoms list or string separated by semicolons or line breaks
            units (UnitsType): angstrom or bohr
            charge (int): charge
            multiplicity (int): spin multiplicity
            basis (BasisType): sto3g or 6-31g or 6-31g**
            hf_method (HFMethodType): Hartree-Fock Method type
            tol (float): Convergence tolerance see pyquante2.scf hamiltonians and iterators
            maxiters (int): Convergence max iterations see pyquante2.scf hamiltonians and iterators
        Raises:
            QiskitChemistryError: Invalid Input
        """
        self._check_valid()
        if not isinstance(atoms, list) and not isinstance(atoms, str):
            raise QiskitChemistryError("Invalid atom input for PYQUANTE Driver '{}'".format(atoms))

        if isinstance(atoms, list):
            atoms = ';'.join(atoms)
        else:
            atoms = atoms.replace('\n', ';')

        units = units.value
        basis = basis.value
        hf_method = hf_method.value
        validate(locals(), self._INPUT_SCHEMA)
        super().__init__()
        self._atoms = atoms
        self._units = units
        self._charge = charge
        self._multiplicity = multiplicity
        self._basis = basis
        self._hf_method = hf_method
        self._tol = tol
        self._maxiters = maxiters

    @staticmethod
    def _check_valid():
        err_msg = 'PyQuante2 is not installed. See https://github.com/rpmuller/pyquante2'
        try:
            spec = importlib.util.find_spec('pyquante2')
            if spec is not None:
                return
        except Exception as ex:  # pylint: disable=broad-except
            logger.debug('PyQuante2 check error %s', str(ex))
            raise QiskitChemistryError(err_msg) from ex

        raise QiskitChemistryError(err_msg)

    def run(self):
        q_mol = compute_integrals(atoms=self._atoms,
                                  units=self._units,
                                  charge=self._charge,
                                  multiplicity=self._multiplicity,
                                  basis=self._basis,
                                  hf_method=self._hf_method,
                                  tol=self._tol,
                                  maxiters=self._maxiters)

        q_mol.origin_driver_name = 'PYQUANTE'
        cfg = ['atoms={}'.format(self._atoms),
               'units={}'.format(self._units),
               'charge={}'.format(self._charge),
               'multiplicity={}'.format(self._multiplicity),
               'basis={}'.format(self._basis),
               'hf_method={}'.format(self._hf_method),
               'tol={}'.format(self._tol),
               'maxiters={}'.format(self._maxiters),
               '']
        q_mol.origin_driver_config = '\n'.join(cfg)

        return q_mol
