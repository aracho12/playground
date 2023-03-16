import sys
from ase.io import read, write
from ase.constraints import FixAtoms, FixedPlane
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input file', default='final_with_calculator.json')
parser.add_argument('-f', '--fix', help='fix element', type=int)
parser.add_argument('-r', '--relax', help='index for relax; others will be fixed', type=str)
args = parser.parse_args()

if args.input:
    print('Your inputfile is:', args.input)

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

if args.fix:
    print('fix element:', args.fix)
    atoms=read(args.input)
    fix_info = [atom.index for atom in atoms if atom.symbol==args.fix]
    c=FixAtoms(indices=fix_info)
    atoms.set_constraint(c)
    write('restart.json',atoms)
    print("{}: slab is successfully fixed".format(args.input))
