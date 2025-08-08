from ase.build import fcc111, surface, bulk
from ase.atoms import Atoms
from ase.io import write
from ase.io import read

# read atoms from command line
import sys
if len(sys.argv) < 2:
    print("Usage: python slab_generate.py <atoms.json>")
    sys.exit()

atoms = read(sys.argv[1])

lattice = 4.0
atoms = Atoms('Ni3Cu',    scaled_positions=[(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)],
    cell=[lattice, lattice, lattice],
    pbc=True)
slab = surface(atoms, (1, 0, 0), 2)
slab.center(vacuum=10, axis=2)

# supercell
sc = slab * (2,2,1)

write('slab.traj',sc)

#slab = fcc111('Pt', size=(3,3,4), vacuum=8, orthogonal=False, periodic=True)
#write('slab.json',slab)



