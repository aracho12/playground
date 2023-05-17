""" Generates the structure of the selected iteration """

from ase.io.vasp import read_vasp_xdatcar
from ase.io.trajectory import Trajectory
from ase.io import read, write
import os
import argparse  

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input file', type=str)
parser.add_argument('-n', '--iteration', help='iteration', type=int, default=-1)
args = parser.parse_args()

if args.input:
    print('Your inputfile is:', args.input)
    input_file=args.input
    if os.path.exists(input_file):
        if 'XDATCAR' in input_file:
            traj = read_vasp_xdatcar(input_file,index=0)
        elif 'traj' in input_file:
            traj = Trajectory(input_file)
        else:
            print("Input file should be XDATCAR or .traj")
            exit()
    else:
        print(f"{input_file} does not exist")
        print('Use -i option to specify input file')
        exit()
else:
    print('Use -i option to specify input file')
    exit()

if args.iteration:
    iteration=args.iteration
    print('iteration:', iteration)
else:
    iteration=0
    print('iteration:', iteration)

atoms=traj[iteration]
if iteration == -1:
    write(f'iter_last.json', atoms)
elif iteration == 0:
    write(f'iter_initial.json', atoms)
else:
    write(f'iter_{iteration}.json', atoms)
