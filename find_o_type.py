"""
Ara Cho, Mar, 2023 @SUNCAT
description: This script is used to distinguish the OOH, OH and O atoms in the input file.
usage: python3 test.py -i final_with_calculator.json
"""

from ase.io import read
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input file', default='final_with_calculator.json')
args = parser.parse_args()

if args.input:
    print('Your inputfile is:', args.input)
    if os.path.exists(args.input):
        atoms=read(args.input)
    else:
        print('The input file does not exist.')
        print('usage: python3 test.py -i filename')
        exit()

o_index = [atom.index for atom in atoms if atom.symbol=='O']
h_index = [atom.index for atom in atoms if atom.symbol=='H']


headers = ['O1_index', 'O_type', 'H1_index', 'Distance_(Å)', 'H2_index', 'Distance_(Å)','O2_index', 'Distance_(Å)']
# Print table headers
print('{:<15s} {:<15s} {:<15s} {:<15s} {:<15s} {:<15s} {:<15s} {:<15s}'.format(*headers))

for i in o_index:
    neighbors = []
    h_neighbors = []
    for j in o_index:
        if i != j:
            d = atoms.get_distance(i, j, mic=True)
            if d < 1.6:
                neighbors.append((j, d))
    for j in h_index:
        d = atoms.get_distance(i, j, mic=True)
        if d < 1.2:
            h_neighbors.append((j, d))

    if len(neighbors) == 0 and len(h_neighbors) == 0:
        row = [i, 'O', '', '', '', '']
        print('{:<15d} {:<15s} {:<15s} {:<15s} {:<15s} {:<15s}'.format(*row))
    elif len(neighbors) == 1 and len(h_neighbors) == 1:
        o_neighbor, o_d = neighbors[0]
        h_neighbor, h_d = h_neighbors[0]
        row = [i, 'OOH', h_neighbor, f'{h_d:.3f}', '', '', o_neighbor, f'{o_d:.3f}']
        print('{:<15d} {:<15s} {:<15d} {:<15s} {:<15s} {:<15s} {:<15d} {:<15s}'.format(*row))
    elif len(neighbors) == 0 and len(h_neighbors) == 1:
        h_neighbor, h_d = h_neighbors[0]
        row = [i, 'OH', h_neighbor, f'{h_d:.3f}', '', '', '','']
        print('{:<15d} {:<15s} {:<15d} {:<15s} {:<15s} {:<15s} {:<15s} {:<15s}'.format(*row))
    elif len(neighbors) == 0 and len(h_neighbors) == 2:
        h1_neighbor, h1_d = h_neighbors[0]
        h2_neighbor, h2_d = h_neighbors[1]
        row = [i, 'H2O', h1_neighbor, f'{h1_d:.3f}', h2_neighbor, f'{h2_d:.3f}', '', '']
        print('{:<15d} {:<15s} {:<15d} {:<15s} {:<15d} {:<15s} {:<15s} {:<15s}'.format(*row))
