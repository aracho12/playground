"""
Tools Package for Computational Chemistry

This package contains utilities for processing DFT calculations and related data.

Modules:
    formation_energy: Calculate formation energies from raw DFT energies
"""

from .formation_energy import FormationEnergyCalculator, calculate_formation_energy

__all__ = ['FormationEnergyCalculator', 'calculate_formation_energy']
__version__ = '1.0.0'
