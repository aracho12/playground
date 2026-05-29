"""
by Ara Cho, May, 2023 @SUNCAT
Description:
    Add water molecules to Pt slab
Usage:
    python3 pt-water.py [input_file]
"""

from ase.io import read, write
import os
import sys
from ase.constraints import FixAtoms, FixedPlane

if len(sys.argv)==2:
    if sys.argv[1] == '-h':
        print("Usage: python3 pt-water.py [input_file].json")
    else:
        input_file=sys.argv[1]
else:
    if os.path.exists('final_with_calculator.json'):
        input_file='final_with_calculator.json'
    else:
        print("Usage: python3 pt-water.py [input_file]")
        exit()
print("Input file: ", input_file)   

atoms = read(input_file)

# resize the cell
print('Resizing the cell')
print(f'before: {atoms.cell}')
atoms.set_cell([atoms.cell[0],atoms.cell[1],[0.,0.,atoms.cell[2,2]+10]],scale_atoms=False)
print(f'after: {atoms.cell}')
print("")

# remove bottom layer of Pt and fix second layer of Pt slab
print("Removing bottom layer of Pt and fixing second layer of Pt slab")
Pt_bottom=[atom.index for atom in atoms if atom.symbol=='Pt' and atom.position[2]<1.7]
del atoms[[Pt_bottom]]
Pt_second=[atom.index for atom in atoms if atom.symbol=='Pt' and atom.position[2]<7]
c=FixAtoms(indices=Pt_second)
atoms.set_constraint(c)
print("")

# add water molecules
print("Adding water molecules")
homebin=os.environ['HOME']+'/bin'
W=read(homebin+'/for_a_happy_life/water.json')
W.set_cell(atoms.cell, scale_atoms=False)
zmin=W.positions[:,2].min()
zmax=atoms.positions[:,2].max()
W.positions += (0,0, zmax-zmin + 2.0)
interface= atoms + W
write('interface.json',interface)
#rearrange symbols
print("")
print("Rearranging symbols")
import subprocess
subprocess.run(['python3',homebin+'/for_a_happy_life/rearrange_symbols.py', 'interface.json'])
print("mv reordered.json interface.json")
subprocess.run(['mv','reordered.json','interface.json'])
print("interface.json is generated")