"""
    Ara Cho, Mar, 2023 @SUNCAT
    description:
    This script is used to show the coordinates of atoms in a slab
    usage: python showatoms.py [filename]
"""
from sys import argv
from ase.io import write, read
import os.path
import numpy as np

if len(argv) > 1:
    inputfile=argv[1]
    print("input:",inputfile)
    slab = read(inputfile)
elif os.path.isfile('final_with_calculator.json'):
    print("input: final_with_calculator.json")
    slab = read('final_with_calculator.json')
elif os.path.isfile("restart.json"):
    print("input: restart.json")
    slab = read("restart.json")
elif os.path.isfile('CONTCAR'):
    print("input: CONTCAR")
    slab = read('CONTCAR')
elif os.path.isfile("POSCAR"):
    print("input: POSCAR")
    slab = read("POSCAR")
else:
    print("there is no input file")
    print("usage: python showatoms.py [filename]")

# basic information
print("")
print("Number of atoms: ", slab.get_global_number_of_atoms())
print("Chemical Formula: ", slab.get_chemical_formula())
print("")
print("Unit Cell (Å)")
print(f"{slab.cell[0][0]:3f}   {slab.cell[0][1]:3f}   {slab.cell[0][2]:3f}")
print(f"{slab.cell[1][0]:3f}   {slab.cell[1][1]:3f}   {slab.cell[1][2]:3f}")
print(f"{slab.cell[2][0]:3f}   {slab.cell[2][1]:3f}   {slab.cell[2][2]:3f}")
print("")
lat=slab.cell.cellpar()
print(f"Lengths: {lat[0]:3f}, {lat[1]:3f}, {lat[2]:3f}")
print(f"Angles : {lat[3]:1f}, {lat[4]:1f}, {lat[5]:1f}")
print(f"Volume : {slab.get_volume():3f} Å^3")
print("")
try:
    print("Potential Energy (eV): ", slab.get_potential_energy())
    if slab.calc is not None and slab.calc.name is not None:
        print(f"Calculator: {slab.calc.name}")
    forces = slab.get_forces()
    max_force = np.max(np.sqrt(np.sum(forces**2, axis=1)))
    print(f"Max force: {max_force:.3f} eV/Å")
except Exception as e:
    print(f"An error occurred: {str(e)}")
print("")

if hasattr(slab, 'constraints') and len(slab.constraints) > 0:
    a=slab.constraints[0]
    constraints=a.get_indices()
    for x in slab:
        if x.index in constraints:
            print(f'{x.x:10f} {x.y:10f} {x.z:10f} | {x.symbol} {x.index} F')
        else:
            print(f'{x.x:10f} {x.y:10f} {x.z:10f} | {x.symbol} {x.index} T')
else:
    for x in slab:
        print(f'{x.x:10f} {x.y:10f} {x.z:10f} | {x.symbol} {x.index} T')
