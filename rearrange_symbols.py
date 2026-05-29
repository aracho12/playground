""" 
Ara Cho, Apr, 2023@SUNCAT
description: rearrange chemical symbols of input file
usage: python rearrange_symbols.py [input file]

Output: 
POSCAR:  Pt  O   H   O   H   O   H   O   H   O   H   O   H
reorder_symbols: Pt36O7H7
POSCAR_new:  Pt  O   H
"""


from ase.io import read, write
import numpy as np
import sys

if len(sys.argv) !=2:
    print("Usage: python rearrange_symbols.py [input file]")
    sys.exit(1)
filename = sys.argv[1]

W=read(filename)

sc = W.copy()
org_chem_symbols = np.array(sc.get_chemical_symbols())
org_atom_index = np.arange(len(sc), dtype=int)
# Sort first by z-coordinates then by y and x.
rpos = np.round(sc.positions, 4)
new_atom_index = np.lexsort(
        (rpos[:, 0], rpos[:, 1], rpos[:, 2])
        )
sc = sc[new_atom_index]
# Just stick to the original order.
chem_sym_order = []
for ss in org_chem_symbols:
    if not ss in chem_sym_order:
        chem_sym_order.append(ss)
# print(chem_sym_order)
new_atom_index = [ii for ss in chem_sym_order
                 for ii in org_atom_index[sc.symbols == ss]]
sc = sc[new_atom_index]

print("\nreorder_symbols:",sc.symbols)
write(f'POSCAR_new',sc)
print(f'POSCAR_new is generated')
