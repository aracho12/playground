from ase.io import write, read
import os.path

if os.path.isfile('CONTCAR'):
	slab = read('CONTCAR')
elif os.path.isfile("POSCAR"):
	slab = read("POSCAR")
elif os.path.isfile("restart.json"):
	slab = read("restart.json")
else:
	print("there is no input file")
	print("CONTCAR/POSCAR/restart.json")

mask = [atom for atom in slab]
for x in mask:
	print(f'{x.x:10f} {x.y:10f} {x.z:10f} | {x.symbol} {x.index}')
