"""
by Ara Cho, May, 2023 @SUNCAT
Description:
    Remove atoms from ase.Atoms object and write to restart.json
Usage: 
    python3 del.py [input_file]
"""

from ase.io import read, write
import os
import sys

if len(sys.argv)==2:
    if sys.argv[1] == '-h':
        print("Usage: python3 del.py [input_file]")
    else:
        input_file=sys.argv[1]
else:
    if os.path.exists('CONTCAR'):
        input_file='CONTCAR'
    else:
        print("Usage: python3 del.py [input_file]")
        exit()
print("Input file: ", input_file)   

atoms = read(input_file)

# remove atoms in index list
print("Removing atoms in index list")
input=input("which atoms to remove? (index starts from 0, separated by space)")
index_list=[int(i) for i in input.split()]
print("atoms to remove: ", index_list)
for i in index_list:
    print(atoms[i].symbol, atoms[i].position)
del atoms[[index_list]]

# write to CONTCAR
print("Writing to restart.json")
write('restart.json',atoms)
