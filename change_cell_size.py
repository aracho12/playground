from ase.io import read, write
import sys
import os

if len(sys.argv)==2:
    if sys.argv[1] == '-h':
        print("Usage: python3 change_cell_size.py [input file]")
    else:
        input_file=sys.argv[1]
else:
    if os.path.exists('final_with_calculator.json'):
        input_file='final_with_calculator.json'
    else:
        print("Usage: python3 change_cell_size.py [input file]")
        exit()
print("Input file: ", input_file)

atoms = read(input_file)
print(f'before: {atoms.cell}')
atoms.set_cell([atoms.cell[0],atoms.cell[1],[0.,0.,atoms.cell[2,2]+10]],scale_atoms=False)
print(f'after: {atoms.cell}')
write('resized.json',atoms)

