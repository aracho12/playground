from sys import argv
from ase.io import write, read
import os.path
#print(argv[0])
if len(argv) > 1:
	inputfile=argv[1]
	print("show:",inputfile)
	slab = read(inputfile)
elif os.path.isfile('CONTCAR'):
	print("show: CONTCAR")
	slab = read('CONTCAR')
elif os.path.isfile("POSCAR"):
	print("show: POSCAR")
	slab = read("POSCAR")
elif os.path.isfile("restart.json"):
	print("show: restart.json")
	slab = read("restart.json")
else:
	print("there is no input file")
	print("CONTCAR/POSCAR/restart.json")

mask = [atom for atom in slab]
for x in mask:
	print(f'{x.x:10f} {x.y:10f} {x.z:10f} | {x.symbol} {x.index}')
