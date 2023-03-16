"""
    This script is used to show the coordinates of atoms in a slab
    usage: python randomthings.py [filename]
    if no filename is given, it will try to read CONTCAR/POSCAR/restart.json
    if no file is found, it will print "there is no input file"
"""
from sys import argv
from ase.io import write, read
import os.path
#print(argv[0])
if len(argv) > 1:
    inputfile=argv[1]
    print("show:",inputfile)
    slab = read(inputfile)
elif os.path.isfile('CONTCAR'):
    print("show: CONTCAR")
    slab = read('CONTCAR')
elif os.path.isfile("POSCAR"):
    print("show: POSCAR")
    slab = read("POSCAR")
elif os.path.isfile("restart.json"):
    print("show: restart.json")
    slab = read("restart.json")
else:
    print("there is no input file")
    print("CONTCAR/POSCAR/restart.json")

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
