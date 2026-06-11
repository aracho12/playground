from ase import Atom, Atoms
import ase.calculators.vasp as vasp_calculator
import os
import subprocess
from ase.build import bulk 
import numpy as np
import shutil

# lattice using isif=3

initial_lattice=3.94
metal='Pt'
cell='fcc'

xc='PBE'
ivdw=11

ispin=1
kpts=(12,12,12)
encut=650


atoms = bulk(metal, cell, a=initial_lattice, cubic=True)

calc=vasp_calculator.Vasp(
    istart=0,
    encut=encut,
    xc=xc,
    kpts=kpts,
    prec='Accurate',
    ivdw=ivdw,
    isif=3, # isif=3
    npar=8,
    nelm=100,
    algo='normal',
    ibrion=2,
    ediffg=-0.03,
    ediff=1e-4,
    nsw=400,
    lvtot=False,
    ispin=ispin,
    lwave=False,
    laechg=False,
    lreal=False,
	setups='recommended',
)

atoms.set_calculator(calc)
atoms.get_potential_energy()

from ase.io.trajectory import Trajectory
traj2=Trajectory('final_with_calculator.traj', 'w')
traj2.write(atoms)
print ('after write')
subprocess.call('ase convert -f final_with_calculator.traj final_with_calculator.json', shell=True)

