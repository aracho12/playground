"""
Ara Cho, Mar, 2023 @SUNCAT
description: fix atoms in slab
usage: python fixatom.py -i [filename] -f "element" -r "index" -d [distance]
i.g) python fixatom.py -i POSCAR -f "Pt" # fix all Pt atoms
    python fixatom.py -i POSCAR -r "41,42" # fix all except 41,42
    python fixatom.py -i POSCAR -d 10.0 # fix all atoms below 10.0 Angstrom
"""


import sys
from ase.io import read, write
from ase.constraints import FixAtoms, FixedPlane
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input file', default='final_with_calculator.json')
parser.add_argument('-f', '--fix', help='element to fix', type=str)
parser.add_argument('-r', '--relax', help='index to relax; others will be fixed', type=str)
parser.add_argument('-d', '--distance', help='all atoms will be fixed below distance', type=float)
args = parser.parse_args()

if args.input:
    print('Your inputfile is:', args.input)

if args.fix:
    print('fix element:', args.fix)
    atoms=read(args.input)
    fix_info = [atom.index for atom in atoms if atom.symbol==args.fix]
    c=FixAtoms(indices=fix_info)
    atoms.set_constraint(c)
    write('restart.json',atoms)
    print("{}: slab is successfully fixed".format(args.input))

if args.relax:
    relax_index = [int(index) for index in args.relax.split(',')]
    print('relax atom index:', relax_index)
    atoms=read(args.input)
    all_index=[atom.index for atom in atoms]
    fix_index=list(set(all_index)-set(relax_index))
    c=FixAtoms(indices=fix_index)
    atoms.set_constraint(c)
    write('restart.json',atoms)
    print("{}: slab is successfully fixed".format(args.input))

if args.distance:
    print('fix atoms below distance:', args.distance)
    atoms=read(args.input)
    fix_info = [atom.index for atom in atoms if atom.position[2]<args.distance]
    c=FixAtoms(indices=fix_info)
    atoms.set_constraint(c)
    write('restart.json',atoms)
    print("{}: slab is successfully fixed".format(args.input))