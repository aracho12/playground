from ase.build import fcc111
from ase.io import write

slab = fcc111('Pt', size=(3,3,4), vacuum=8, orthogonal=False, periodic=True)
write('slab.json',slab)
