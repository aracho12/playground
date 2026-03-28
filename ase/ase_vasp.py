#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ase.io import *
from sys import argv, path
import os
from ase.calculators.vasp import Vasp
import ase.calculators.vasp as vasp_calculator
from ase.io import read, write
import numpy as np
import subprocess
import shutil
from ase.build import molecule



mode = argv[1] if len(argv) > 1 else 'slab'
valid_modes = {"slab", "vib", "sp", "charge", "dos", "wf", "gas", "fiscs"}
if mode not in valid_modes:
    raise ValueError(f"Unknown mode='{mode}'. Use one of: {sorted(valid_modes)}")

print(f'Running in {mode.upper()} mode')

# argv[2] (molecule name) is optional, e.g. "python ase_vasp.py vib" has no 3rd arg
molecule_name = argv[2] if len(argv) > 2 else None
if molecule_name is not None:
    print(f'Building molecule: {molecule_name}')

def build_molecule(molecule_name):
    atoms = molecule(molecule_name)
    atoms.set_cell([15,15,15])
    atoms.center()
    write('restart.json', atoms)
    return atoms

# input
if molecule_name is not None:
    atoms = build_molecule(molecule_name)
    atoms.pbc = (True, True, True)
else:
    atoms = read('restart.json')


kpts = (2,4,1)
magmom_total = None 


# common settings (for slab as default)
common_params = {
      'istart': 0, # 0=new job, 1=continuation, 2=same cut-off
      'icharg': 2, # 1=file, 2=atom, 10=const, 11=potentials

      # electronic minimization
      'encut': 500,
      'prec': 'Normal',
      'algo': 'Normal',
      'nelm': 100,
      'ediff': 1e-4, #energy conv. for better forces

      # ionic relaxation
      'ibrion': 2,
      'nsw': 500,
      'isif': 2,   #0=fixed, 2=relax ions, 3=relax cell+ions
      'ediffg': -0.03, # forces
      'ediff': 1e-4, #energy conv. for better forces
      'potim': 0.5,  #time step for ionic relaxation

      # exchange-correlation functional
      'xc': 'PBE',
      'gga': 'PE',
      
      # kpoints
      'kpts': kpts,
      'gamma': False, # Gamma-centered (defaults to Monkhorst-Pack)

      # DOS and occupation
      'ismear': 0,
      'sigma': 0.01,
      
      # spin
      'ispin': 1,
      
      # dft+u
      #ldau_luj={
      #     'Ti':{'L':2, 'U':3.00, 'J':0.0},
      #     'V': {'L':2, 'U':3.25, 'J':0.0}, #Materials Project
      #     'Cr':{'L':2, 'U':3.5, 'J':0.0},  #close to MP
      #     'Mn':{'L':2, 'U':3.75, 'J':0.0},
      #     'Fe':{'L':2, 'U':4.3, 'J':0.0}, # carter 4.3 eV Friebel 3.5 eV
      #     'Co':{'L':2, 'U':3.32, 'J':0.0},
      #     'Ni':{'L':2, 'U':6.45, 'J':0.0}, # This is simply too high, needs to be checked with HSE06
      #     'Cu':{'L':2, 'U':3.0, 'J':0.0}, #we should have some U
      #     'Mo':{'L':2, 'U':4.38, 'J':0.0}, #Materials Project
      #     'W':{'L':2, 'U':6.2, 'J':0.0}, #Materials Project kind of high
      #     'Ce':{'L':3, 'U':4.50, 'J':0.0},
      #     'O':{'L':-1, 'U':0.0, 'J':0.0},
      #     'C':{'L':-1, 'U':0.0, 'J':0.0},
      #     'Au':{'L':-1, 'U':0.0, 'J':0.0},
      #     'Ir':{'L':-1, 'U':0.0, 'J':0.0},
      #     'H':{'L':-1, 'U':0.0, 'J':0.0}},
      #ldauprint=2,
      #lmaxmix=4,
      #lmaxmix=6,

      # dipole correction
      'ldipol': False,
      'idipol': 3,

      # vdW correction
      #'ivdw': 12,

      # output options
      'lwave': False,
      'lcharg': True,
      'laechg': True,
      'lvtot': False,

      # performance
      'npar': 4,
      #'ncore': 4,
      'lreal': 'Auto',

      # setups
      'setups': 'recommended',
}

if magmom_total is not None:
    magmom_per_atom = magmom_total / len(atoms)
    atoms.set_initial_magnetic_moments([magmom_per_atom] * len(atoms))
    common_params["ispin"] = 2
else:
    common_params["ispin"] = 1

def mode_overrides(mode_name: str) -> dict:
    if mode_name == "slab":
        return {}

    if mode_name == "sp":
        return {
            "ibrion": -1,
            "nsw": 0,
            "ediff": 1e-6,
            "potim": None,
            "ediffg": None,
        }

    if mode_name == "charge":
        return {
            "ibrion": -1,
            "nsw": 0,
            "ediff": 1e-6,
            "potim": None,
            "ediffg": None,
            "lcharg": True,   # CHGCAR
            "laechg": True,   # AECCAR0/2
        }

    if mode_name == "dos":
        return {
            "ibrion": -1,
            "nsw": 0,
            "ediff": 1e-6,
            "potim": None,
            "ediffg": None,
            "icharg": 11,     # requires CHGCAR
            "ismear": -5,
            "sigma": 0.05,
            "lorbit": 11,
            "nedos": 2000,
        }

    if mode_name == "wf":
        return {
            "ibrion": -1,
            "nsw": 0,
            "ediff": 1e-6,
            "potim": None,
            "ediffg": None,
            "icharg": 11,     # requires CHGCAR
            "lvtot": True,    # LOCPOT
            "lvhar": True,    # LOCPOT (more robust)
        }

    if mode_name == "vib":
        return {
            "ibrion": 5,
            "nfree": 2,       # 2 or 4
            "potim": 0.015,
            "ediff": 1e-6,
            "isym": 0,
            "lreal": False,
            "laechg": False,
        }
    if mode_name == "gas":
        return {
            "kpts": (1,1,1),
            "gamma": True,
            "ismear": 0,
            "sigma": 0.05,
            "lreal": False,
            "idipol": 4,
            "ldipol": False,
            "laechg": False,
        }

    if mode_name == "fiscs":
        # FI-SCS (Fractionally Ionic Self-Consistent Screening) singlepoint
        # LVDWSCS / IVDW=263 / LVDW_ONECELL are patched directly into INCAR
        # because older ASE versions may not have them in bool_keys/list_bool_keys.
        # ALGO=48 (VeryFast) — ASE string: 'VeryFast'
        return {
            # singlepoint
            "ibrion": -1,
            "nsw":     0,
            "ediff":   1e-5,
            "ediffg":  None,
            "potim":   None,
            # electronic
            "sigma":   0.20,
            "symprec": 1e-8,
            "lorbit":  11,
            "lreal":   False,        # exact projection required for SCS
            "algo":    'VeryFast',   # ALGO=48 in VASP
            # output
            "lcharg":  False,
            "laechg":  False,
            "lwave":   False,
            # performance (reference: npar=1, kpar=2 — adjust to your system)
            "npar":    4,
        }

    return {}


# FISCS-specific tags that ASE may not recognize natively.
# Written directly to INCAR after ASE's write_input() call.
FISCS_INCAR_PATCH = """\
IVDW         = 263     ! FI-SCS (fractionally ionic SCS)
LVDWSCS      = .TRUE.
LVDW_ONECELL = .FALSE. .FALSE. .TRUE.  ! periodic only along z (slab geometry)
"""

def patch_incar_for_fiscs(directory='.'):
    """Append FISCS-specific tags that ASE cannot write natively."""
    incar_path = os.path.join(directory, 'INCAR')
    with open(incar_path, 'a') as f:
        f.write('\n# --- FI-SCS patch ---\n')
        f.write(FISCS_INCAR_PATCH)
    print('FISCS tags appended to INCAR.')


params = dict(common_params)
over = mode_overrides(mode)
for k, v in over.items():
    if v is None:
        params.pop(k, None)
    else:
        params[k] = v

calc = Vasp(**{k: v for k, v in params.items() if v is not None})
atoms.calc = calc

# For FISCS: monkey-patch write_input so the extra tags are appended
# every time ASE writes INCAR (calc.calculate() calls write_input internally).
if mode == "fiscs":
    _orig_write_input = calc.write_input
    def _patched_write_input(atoms, **kwargs):
        _orig_write_input(atoms, **kwargs)
        patch_incar_for_fiscs(calc.directory)
    calc.write_input = _patched_write_input

atoms.get_potential_energy()
from ase.io.trajectory import Trajectory
traj2=Trajectory('final_with_calculator.traj', 'w') 
traj2.write(atoms)
print ('after write')
subprocess.call('ase convert -f final_with_calculator.traj final_with_calculator.json', shell=True)
subprocess.call('ase convert -f OUTCAR full_relax.json', shell=True)
