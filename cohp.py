from pymatgen.io.lobster import Lobsterin

lobsterin = Lobsterin.standard_calculations_from_vasp_files("POSCAR","INCAR","POTCAR",option='standard')

lobsterin.write_INCAR(incar_input="INCAR",incar_output="INCAR.lobster",poscar_input="POSCAR",isym=-1,further_settings={"IBRION":-1})
file=open('./INCAR.lobster','r')
print(file.read())

import os
os.system("mv INCAR INCAR.original")
os.system("mv INCAR.lobster INCAR")

lobsterin.write_lobsterin(path="lobsterin")
file=open('./lobsterin','r')
print(file.read())

print("cohpBetween atom 158 atom 161 orbitalWise")
print("#cohpGenerator from 0.1 to 6.0 type Pt type H orbitalwise")
