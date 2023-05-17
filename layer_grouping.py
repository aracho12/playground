""" find the index of the oxygen atoms and hydrogen atoms along the layers """
from ase.io import read
import os 
import subprocess
import argparse   
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input file', default='CONTCAR')
parser.add_argument('-l', '--list', help='show in list type', default=False, action='store_true')
parser.add_argument('-a', '--all', help='show all atoms', default=False, action='store_true')
args = parser.parse_args()

if args.input:
    filename=args.input
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        print('Use -i option to specify input file')
        exit()
    else:
        print('Your inputfile is:', filename)

atoms=read(filename)

""" grouping atoms along the layers """

# extract integer only from the z coordinates
group={}
for atom in atoms:
    if args.all:
        z_int=int(atom.z)
    else:
        if atom.symbol != 'Pt':
            z_int=int(atom.z)
        else:
            continue
    if z_int in group:
        if atom.symbol in group[z_int]:
            group[z_int][atom.symbol].append(atom.index)
        else:
            group[z_int][atom.symbol]=[atom.index]
    else:
        group[z_int]={}
        group[z_int][atom.symbol]=[atom.index]
group=dict(sorted(group.items()))

for i, key in enumerate(group):
    print(f"  [ {i+1} ] {key} Å ".center(40, '-'))
    for key2 in group[key]:
        if args.list:
            print(key2, len(group[key][key2]), group[key][key2])
        else:
            print(key2, len(group[key][key2]), np.array(group[key][key2]))

