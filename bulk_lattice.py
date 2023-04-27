from ase import Atom, Atoms
import ase.calculators.vasp as vasp_calculator
import os
from ase.build import bulk 
import numpy as np
import shutil

# set up
opt_lattice=3.926216
metal='Pt'
cell='fcc'

xc='PBE'
ivdw=12

ispin=1
kpts=(12,12,12)
encut=500


lattice = [-0.2,-0.1,-0.05,-0.04,-0.03,-0.02,-0.01,0.00,0.01,0.02,0.03,0.04,0.05,0.1,0.2]
LC = [] 
for lc in lattice:
    LC.append(round(lc + opt_lattice,3)) 
fcc_energies=[]

for a in LC:
    os.mkdir('{}'.format(a))
    shutil.copy("run_vasp.py", "{}/run_vasp.py".format(a))
    os.chdir('{}'.format(a))
    atoms = bulk(metal, cell, a=a, cubic=True)
    
    calc=vasp_calculator.Vasp(
        istart=0,
        encut=encut,
        xc=xc,
        kpts=kpts,
        npar=8,
        nelm=100,
        algo='normal',
        ibrion=2,
        isif=2,
        ediffg=-0.03,
        ediff=1e-4,
        prec='Normal',
        nsw=400,
        lvtot=False,
        ispin=ispin,
        lwave=False,
        laechg=False,
        lreal='Auto',
        ivdw=ivdw,
		setups='recommended',
    )

    atoms.set_calculator(calc)
    e=atoms.get_potential_energy()
    fcc_energies.append(e)
    print(f"{a}\t  {e}")
    os.chdir('..')

import matplotlib.pyplot as plt 
plt.plot(LC, fcc_energies, color='blue')
plt.xlabel('Lattice constant ($\AA$)')
plt.ylabel('Total energy (eV)')
plt.savefig('Pt-fcc.png')

#print('#+blname: Pt-fcc-energies')
#print('| lattice constant ($\AA$) | Total Energy (eV) |')
#for lc, e in zip(LC, fcc_energies):
#    print(' | {0} | {1} |'.format(lc,e))

