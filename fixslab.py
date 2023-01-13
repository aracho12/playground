from ase.constraints import FixAtoms, FixedPlane
from ase.io import write, read
import os
import sys
# read input 
if os.path.isfile('final_with_calculator.json'):
    inputfile='final_with_calculator.json'
elif os.path.isfile('restart.json'):
    inputfile='restart.json'
elif os.path.isfile('CONTCAR'):
    inputfile='CONTCAR'
elif os.path.isfile('POSCAR'):
    inputfile='POSCAR'
else:
    print("there is no structure file")
    sys.exit()

atoms = read(inputfile)
pt_info = [atom.z for atom in atoms if atom.symbol=='Pt']
pt_slab=max(pt_info) 
c=FixAtoms(indices=[atom.index for atom in atoms if atom.z < pt_slab+0.5])
atoms.set_constraint(c)
write('restart.json',atoms)
print("{}: slab is successfully fixed".format(inputfile))

