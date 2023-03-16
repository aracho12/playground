import sys
import csv

if len(sys.argv) !=2:
    print("Usage: python3 dat2csv.py filename.dat")
    sys.exit(1)
filename = sys.argv[1]

with open(filename, "r") as f:
	data = f.read()
	rows=[line.split() for line in data.split("\n")]

""" remove .dat from filename """
filename = filename[:-4]
with open(filename + ".csv", "w") as f:
	# write header
	if filename == 'neb.dat' or 'spline.dat':
		f.write("#,Reaction Coordinate,Relative Energy (eV),force\n")
	writer = csv.writer(f)
	writer.writerows(rows)

