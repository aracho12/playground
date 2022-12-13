from ase import Atoms
from ase.io import read

atoms=read('final_with_calculator.json')
outfilename = 'get_magmom_moments.txt'
outfile=open(outfilename, 'w+')
for atom in atoms:
    sym=atom.symbol
    mag=atoms.get_magnetic_moments()
    mag=mag[atom.index]
    print ('index: '+str(atom.index)+' name: '+atom.symbol+' magmom: '+str(mag), file=outfile)
outfile.close()
outputfile=open(outfilename, "r")
printout=outputfile.readlines()
for line in printout:
    print (line)
