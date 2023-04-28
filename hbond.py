"""
Ara Cho, Apr, 2023 @SUNCAT
description: This script is used to find hydrogen bonds in a given structure.

Usage: python3 hbond.py final_with_calculator.json
O(36) -- H(47) : 2.060 Å
O(37) -- H(48) : 2.038 Å
O(39) -- H(44) : 1.625 Å
O(39) -- H(45) : 1.688 Å
O(40) -- H(41) : 1.602 Å
O(40) -- H(46) : 1.695 Å
"""

from ase.io import read

if len(sys.argv)==2:
    if sys.argv[1] == '-h':
        print("Usage: python3 hbond.py final_with_calculator.json")
    else:
        input_file=sys.argv[1]
        print("Input file: ", input_file)
atoms = read(input_file)

cutoff = 2.3

# finding hydrogen and oxygen indices
h_indices = [i for i, atom in enumerate(atoms) if atom.symbol == 'H']
o_indices = [i for i, atom in enumerate(atoms) if atom.symbol == 'O']

# get hydrogen bonds
hbonds = []
for j, o_index in enumerate(o_indices):
    for i, h_index in enumerate(h_indices):
        neighbor_distance = atoms.get_distance(h_index,o_index,mic=True)
        if 1.2 < neighbor_distance < cutoff:
            hbond = (h_index, o_index, neighbor_distance)
            hbonds.append(hbond)

# print hydrogen bonds
for hbond in hbonds:
    print(f'O({hbond[1]}) -- H({hbond[0]}) : {hbond[2]:.3f} Å')