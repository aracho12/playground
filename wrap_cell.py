"""
Ara Cho, May, 2023 @SUNCAT
description: wrap cell and merge multiple XDATCAR files into one trajectory file
usage: python3 wrap_cell.py -i [input_files] (-o [output_file])
"""

from ase.io.vasp import read_vasp_xdatcar
from ase.io.trajectory import Trajectory
from ase.io import read, write
import sys
import os
import argparse  

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input file(s)', type=str, nargs='+')
parser.add_argument('-o', '--output', help='output file', type=str)
parser.add_argument('-c', '--cutoff', help='cutoff iteration of first file', type=int)
args = parser.parse_args()

if args.input:
    print('Your inputfile is:', args.input)
    input_files=args.input
    if len(input_files)==1:
        #input_files=input_files[0]
        if 'XDATCAR' in input_files:
            multi=True
        elif 'CONTCAR' or 'POSCAR' in input_files:
            multi=False
            input_files=input_files[0]
            filename=input_files
        elif 'json' in input_files:
            input_files=input_files[0]
            multi=False
            extension=input_files.split('.')[-1]
            filename=input_files.split('.')[0]
    else:
        multi=True
else:
    if os.path.exists('XDATCAR'):
        input_files='XDATCAR'
        multi=True
    else:
        print("Usage: python3 wrap_cell.py -i [input_files]")
        exit()

if args.output:
    output_file=args.output
else:
    if multi:
        output_file='aimd_sum.traj'
    else:
        if 'json' in input_files:
            output_file=f'{filename}_wrap.{extension}'
        else:
            output_file=f'{filename}_wrap.vasp'

if args.cutoff:
    cutoff=args.cutoff
    print(f'cutoff iteration of the first file: {cutoff}')
else:
    cutoff=1
if multi:
    if len(input_files) > 1:
        traj2=Trajectory(output_file, 'w')
        print("Multiple input files are given. The output file is aimd_sum.traj")
    else:
        traj2=Trajectory('aimd.traj', 'w')
        print("The output file is aimd.traj")

    for i, input_file in enumerate(input_files):
        traj = read_vasp_xdatcar(input_file,index=0)
        for j, atoms in enumerate(traj):
            if i==0 and j in list(range(1,cutoff)):
                continue
            atoms.set_cell([atoms.cell[0],atoms.cell[1],atoms.cell[2]],scale_atoms=True)
            atoms.wrap()
            traj2.write(atoms)
    print(f"total iterations: {len(traj2)}")
    print(f"wrap_cell.py is successfully done")
else:
    atoms=read(input_files)
    atoms.set_cell([atoms.cell[0],atoms.cell[1],atoms.cell[2]],scale_atoms=True)
    atoms.wrap()
    write(output_file, atoms)
    print(f"output file: {output_file}")

