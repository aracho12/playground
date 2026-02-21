"""
VASP ZPE and thermochemistry from OUTCAR vibrational frequencies.
Extracts frequencies from OUTCAR (grep THz lines), converts to eV,
and uses ASE HarmonicThermo / IdealGasThermo like qe_zpe_entropy.py.
"""
from ase import units
import numpy as np
import os
import sys
from datetime import datetime

from ase.io import read
from ase.thermochemistry import HarmonicThermo, IdealGasThermo

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

# Optional: gas phase needs catmap for molecule()
try:
    import catmap
    HAS_CATMAP = True
except ImportError:
    HAS_CATMAP = False

ideal_gas_params = {
    # 'name': [symmetrynumber, geometry, spin]
    'H2_g': [2, 'linear', 0],
    'N2_g': [2, 'linear', 0],
    'O2_g': [2, 'linear', 1.0],
    'H2O_g': [2, 'nonlinear', 0],
    'CO_g': [1, 'linear', 0],
    'CH4_g': [12, 'nonlinear', 0],
    'NH3_g': [3, 'nonlinear', 0],
    'CH3OH_g': [1, 'nonlinear', 0],
    'CH3CH2OH_g': [1, 'nonlinear', 0],
    'CO2_g': [2, 'linear', 0],
    'CH2O_g': [2, 'nonlinear', 0],
    'HCOOH_g': [1, 'nonlinear', 0],
    'HCOO_g': [1, 'nonlinear', 0],
    'CH2CH2_g': [4, 'nonlinear', 0],
    'CH3CHCH2_g': [1, 'nonlinear', 0],
    'CH3CH2CHCH2_g': [1, 'nonlinear', 0],
    'CH3CHCHCH3_g': [2, 'nonlinear', 0],
    'CH3CH3CCH2_g': [2, 'nonlinear', 0],
    'pe_g': [2, 'linear', 0],
    'C2H2_g': [2, 'linear', 0],
    'C2H4_g': [4, 'nonlinear', 0],
    'C2H6_g': [6, 'nonlinear', 0],
    'C3H6_g': [1, 'nonlinear', 0],
    'CH3COOH_g': [1, 'nonlinear', 0],
    'CH3CHO_g': [1, 'nonlinear', 0],
    'C5H4O2_g': [1, 'nonlinear', 0],
    'C5H6O2_g': [1, 'nonlinear', 0],
    'C5H6O_g': [1, 'nonlinear', 0],
    'HCl_g': [1, 'linear', 0],
    'Cl2_g': [2, 'linear', 0],
    'HCOOCH3_g': [1, 'nonlinear', 0],
    'C3H8_g': [2, 'nonlinear', 0],
    'butadiene_g': [2, 'nonlinear', 0],
    'glyoxal_g': [2, 'nonlinear', 0],
    'OCHCHO_g': [2, 'nonlinear', 0],
    'CH3CH2COOH_g': [1, 'nonlinear', 0],
    'CH3COOCH3_g': [1, 'nonlinear', 0],
}


def extract_frequencies_from_outcar(file_path='OUTCAR'):
    """
    Extract vibrational frequencies from VASP OUTCAR (lines containing THz).
    Returns list of vibrational energies in eV.
    Real modes: positive eV. Imaginary modes (f/i=): negative eV.
    ASE thermochemistry uses only positive energies; imaginary are excluded.
    """
    energies_eV = []
    with open(file_path, 'r') as f:
        for line in f:
            if 'THz' not in line or 'meV' not in line:
                continue
            # f/i= means imaginary frequency
            is_imaginary = 'f/i' in line
            tokens = line.split()
            idx = tokens.index('meV')
            meV_val = float(tokens[idx - 1])
            eV_val = meV_val / 1000.0
            if is_imaginary:
                eV_val = -abs(eV_val)
            energies_eV.append(eV_val)
    return energies_eV


def vib_energies_for_thermo(vib_energies):
    """Use only real (positive) frequencies for ASE thermochemistry."""
    return [e for e in vib_energies if e > 0]


class DualOutput:
    def __init__(self, filename, terminal=sys.stdout):
        self.terminal = terminal
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()


def _vibrational_energy_contribution(temperature, vib_energies, verbose=False):
    """Change in internal energy from vibrations (0 K -> T), in eV."""
    kT = units.kB * temperature
    dU = 0.0
    for energy in vib_energies:
        if energy <= 0:
            continue
        dU += energy / (np.exp(energy / kT) - 1.0)
    return dU


def get_free_energies(vib_energies, temperature=300, fugacity=1e5):
    """Same interface as qe_zpe_entropy: gas vs ads from cwd path."""
    vib_real = vib_energies_for_thermo(vib_energies)
    if not vib_real:
        raise ValueError("No real (positive) vibrational frequencies for thermochemistry.")
    pwd = os.getcwd()
    if 'gases' in pwd and HAS_CATMAP:
        status = 'gas'
        molecule = catmap.molecule
        gas_name = os.path.basename(pwd)
        if gas_name == 'H2_ref':
            gas_name = 'H2'
        gas_name_g = gas_name + '_g'
        if gas_name_g not in ideal_gas_params:
            raise KeyError(f"Gas {gas_name_g} not in ideal_gas_params.")
        gpars = ideal_gas_params[gas_name_g]
        symmetry, geometry, spin = gpars[:3]
        try:
            atoms = molecule(gas_name)
        except Exception:
            print(f"Error: {gas_name} not in ase database; reading qn.traj")
            atoms = read('qn.traj')
        therm = IdealGasThermo(
            vib_real, geometry,
            atoms=atoms, symmetrynumber=symmetry,
            spin=spin)
        ZPE = therm.get_ZPE_correction()
        H = therm.get_enthalpy(temperature, verbose=False)
        Cp = H - ZPE
        dS = therm.get_entropy(temperature, fugacity, verbose=False)
        dS_1bar2p = -units.kB * np.log(fugacity / therm.referencepressure)
        F = H - temperature * dS
        TS = temperature * dS
        return status, ZPE, Cp, H, dS_1bar2p, dS, TS, F
    else:
        status = 'ads'
        therm = HarmonicThermo(vib_real)
        ZPE = therm.get_ZPE_correction()
        U = therm.get_internal_energy(temperature=temperature, verbose=False)
        F = therm.get_helmholtz_energy(temperature=temperature, verbose=False)
        Cpv = _vibrational_energy_contribution(temperature, vib_real)
        dS = therm.get_entropy(temperature=temperature, verbose=False)
        TS = temperature * dS
        return status, ZPE, U, F, Cpv, dS, TS


if __name__ == "__main__":
    sys.stdout = DualOutput("thermo.txt")
    now = datetime.now()
    print("=" * 60)
    print("Current time:", now.strftime("%Y-%m-%d %H:%M:%S"))
    print()

    outcar_path = os.environ.get("VASP_OUTCAR", "OUTCAR")
    if not os.path.isfile(outcar_path):
        print(f"Error: {outcar_path} not found.")
        sys.exit(1)
    frequencies = extract_frequencies_from_outcar(outcar_path)
    n_imag = sum(1 for e in frequencies if e < 0)
    if n_imag:
        print(f"Note: {n_imag} imaginary mode(s) excluded from thermochemistry.")
    print(f"Frequencies (eV): {[round(e, 6) for e in frequencies]}")
    print()

    T = 300  # K
    pwd = os.getcwd()
    if 'gas' in pwd and HAS_CATMAP:
        fugacity = 1e5
        print("Gas phase thermochemistry (eV), IdealGasThermo")
        print()
        status, ZPE, Cp, H, dS_1bar2p, dS, TS, F = get_free_energies(
            frequencies, T, fugacity=fugacity)
        print(f"T(K)\t ZPE \t +Cp\t -TS \t F")
        print(f"{T}\t {ZPE:.3f}\t {Cp:.3f}\t {TS:.3f}\t {F:.3f}")
        print(f"enthalpy correction (E+ZPE+Cp) at {T} K       : {H:.3f} eV")
        print(f"entropy at {T} K                              : {dS:.8f} eV/K")
        print(f"entropy correction from 1 bar to {fugacity} Pa: {dS_1bar2p:.8f} eV")
    else:
        if 'gas' in pwd and not HAS_CATMAP:
            print("Warning: catmap not found; treating as adsorption.")
        print("Adsorption phase (eV)")
        print("T(K)\t ZPE \t +Cv\t -TS\t F")
        status, ZPE, U, F, Cpv, dS, TS = get_free_energies(frequencies, T)
        print(f"{T}\t {ZPE:.3f}\t {Cpv:.3f}\t {TS:.3f}\t {F:.3f}")
    print()
