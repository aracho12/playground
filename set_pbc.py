from ase.io import write, read
from sys import argv

if len(argv) > 1:
    inputfile=argv[1]
    print("input:",inputfile)
    slab = read(inputfile)
else:
    print("there is no input file")
    print("usage: python setpbc.py [filename]")

print(slab.get_pbc())

slab.set_pbc((True, True, True))
write('restart.json', slab)
print('write restart.json')

print(slab.get_pbc())
