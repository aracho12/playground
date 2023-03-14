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

