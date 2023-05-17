# Playground
for fun!!
script for vasp calculation

# B
- bulk\_lattice.py: calculate bulk lattice parameter using ase (manually)
- bulk\_optimize.py: calculate bulk lattice parameter using ase (isif=3)

# C
- change\_cell\_size.py: Change the cell size of the input file by adding 10 Angstroms to the c axis

# D
- dat2csv.py: Convert .dat to .csv
- del.py : Delete atoms specified by index

# F
- find\_o\_type.py: distinguish the OOH, OH and O atoms in the input file.
- fixatom.py: fix atoms in slab

# G
- get\_allmagmoms.py: Extract magmom values for each atom from the json file converted by ase.
- getdistance\_pair.py: Calculate the distance between the specified indexes for all folders.

# H
- hbond.py: find hydrogen bonds in a given structure.

# L
- layer\_grouping.py: Element, index grouping by layer in a given structure.

# N
- nebplot.py: plot the spline curve of NEB result

# P
- povshot.py: Generates a recolored Povray image at the specified index.

# R
- rearrange\_symbols.py: rearrange chemical symbols of input file

# S
- select\_iter.py: Generates the structure of the selected iteration.
- show\_ini\_fin.py: Generate POSCAR and CONTCAR images from calculation folders
- showatoms.py: show the coordinates and information of atoms 

# W
- wrap\_cell.py: wrap cell and merge multiple XDATCAR files into one trajectory file
