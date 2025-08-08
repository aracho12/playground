from ase.build import fcc111, surface, bulk
from ase.io import write
from ase.io import read

# read atoms from command line
import sys
if len(sys.argv) < 2:
    print("Usage: python slab_generate.py <atoms.json>")
    sys.exit()

atoms = read(sys.argv[1])

slab = surface(atoms, miller_indices=(1,1,1), layers=4)
slab.center(vacuum=10.0, axis=2)

write('slab.traj',slab)
#slab = fcc111('Pt', size=(3,3,4), vacuum=8, orthogonal=False, periodic=True)
#write('slab.json',slab)




