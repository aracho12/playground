"""
calculate distance between two atoms
get each indexes pair from command line argument and calculate distance
i.g) python3 getdistance_pair.py -i final_with_calculator.json -p 1,2 3,4 5,6
$ python getdistance_pair.py -p 42,50 42,41
Your inputfile is: CONTCAR
Your pair is: ['42,50', '42,41']
Pairs            [42, 50]         [42, 41]
00               1.027            1.480
01               1.016            1.696
02               1.001            2.117
03               0.991            2.460
04               0.985            2.603
"""
import sys
from ase.io import read
from ase import Atom
from ase import Atoms
from ase import neighborlist
import argparse
import numpy as np
import math
import time
import random
import os

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input file', default='CONTCAR')
parser.add_argument('-p', '--pairs', help='Pairs separated by space (e.g., 1,2 1,3 ..)', type=str, nargs='+')

args = parser.parse_args()

if args.input:
    print('Your inputfile is:', args.input)
    #atoms = read(args.input)
else:
    print('No inputfile is given. Default is CONTCAR')

fol='.'
dir_list = [name for name in os.listdir(fol) if os.path.isdir(name)]
dir_list = [d for d in dir_list if d[-1].isdigit() and d[0].isdigit()]
dir_list.sort()
num_dir = len(dir_list)
#print(dir_list)


if args.pairs:
    print('Your pair is:', args.pairs)
    pairs = args.pairs
    header = ['Pairs']
    distances = []
    for pair in pairs:
        pair = pair.split(',')
        pair = [int(i) for i in pair]
        distance = 'Distance_'+str(pair[0])+'_'+str(pair[1])
        distances.append(distance)
        header.append(str(pair))
    print('  '.join([h.ljust(15) for h in header]))

    if num_dir > 0:
        for d in dir_list:
            os.chdir(d)
            atoms = read(args.input)
            line=[d]
            for pair in pairs:
                pair = pair.split(',')
                pair = [int(i) for i in pair]
                distance = atoms.get_distance(pair[0], pair[1])
                line.append(f'{distance:.3f}')
            print('  '.join([str(l).ljust(15) for l in line]))
            os.chdir('..')
    else:
        line=['.']
        for pair in pairs:
            pair = pair.split(',')
            pair = [int(i) for i in pair]
            distance = atoms.get_distance(pair[0], pair[1])
            line.append(f'{distance:.3f}')
        print('  '.join([str(l).ljust(15) for l in line]))
