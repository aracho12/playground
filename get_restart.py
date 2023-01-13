import numpy as np
import logging
import os
import sys
import subprocess
from ase.io import write, read
from ase import Atoms, Atom
from ase.io.trajectory import Trajectory
home=os.path.expanduser('~')
sys.path.append(os.path.abspath(home+'/bin/for_a_happy_life'))
from  bader_get_charge_vasp_py3_new  import *
import logging.config
# ================== Logger ================================
def Logger(file_name):
    formatter = logging.Formatter(fmt='%(asctime)s | %(message)s',
                                  datefmt='%Y/%m/%d %H:%M:%S') # %I:%M:%S %p AM|PM format
    logging.basicConfig(filename = '%s.log' %(file_name),format= '%(asctime)s | %(message)s',
                                  datefmt='%Y/%m/%d %H:%M:%S', filemode = 'w', level = logging.INFO)
    log_obj = logging.getLogger()
    log_obj.setLevel(logging.DEBUG)
    # log_obj = logging.getLogger().addHandler(logging.StreamHandler())

    # console printer
    screen_handler = logging.StreamHandler(stream=sys.stdout) #stream=sys.stdout is similar to normal print
    screen_handler.setFormatter(formatter)
    logging.getLogger().addHandler(screen_handler)

    #log_obj.info("Logger object created successfully..")
    return log_obj
# =======================================================
logger = Logger('post-process')

if(len(sys.argv)>1):
    file=sys.argv[1]
    traj = Trajectory(file)
    atoms = traj[-1]
    energy=atoms.get_potential_energy()
    forces=atoms.get_forces()
    logger.info(energy)    
    subprocess.check_output("ase convert -f -n -1 %s  -o json moments.json " %(file), shell=True)
else:
    logger.info('get energy from OUTCAR')
    file='OUTCAR'
    energy=subprocess.check_output("grep py= OUTCAR | tail -1 | gawk '{print $7}' ", shell=True)
    energy=float(energy)
    logger.info(energy)
    atoms=read(file)
    forces=atoms.get_forces()
    subprocess.check_output("ase convert -f -n -1 OUTCAR -o json moments.json ", shell=True)
    #subprocess.check_output("ase convert -f -n -1 OUTCAR -o cif moments.cif ", shell=True)
    logger.info('create moments.json')
    traj2=Trajectory('moments.traj',  'w')
    traj2.write(atoms, energy=energy)
    logger.info('create moments.traj')
    
try:
    atoms_charge=get_bader_charges(file)
    write_charge_traj=True
    if write_charge_traj:
        logger.info("get bader charges")
except:
    write_charge_traj=False
    if not write_charge_traj:
        logger.error("can't get bader charges ; LAECHG = False")
try:
    os.system("grep LORBIT INCAR | grep -v '#' ")
    write_magmom=True
    if write_magmom:
        logger.info("get magnetic moments")
except:
    write_magmom=False
    if not write_magmom:
        logger.error("can't get magnetic moments ; LORBIT off")
moments=[]
moments2=[]
if write_magmom:
    moms=atoms.get_magnetic_moments()
    atoms.set_initial_magnetic_moments(moms)
    logger.info("set initial magnetic moments")

if write_charge_traj:
    atoms.set_initial_charges(atoms_charge)
    logger.info("set initial charges")
write('restart.json', atoms)
logger.info("write restart.json")
sum=0.0
largest=0.0
for a in range(len(atoms)):
    if write_magmom:
        if(np.abs(moms[a])>0.1):
            moments.append([atoms[a].symbol,a,moms[a]])
        if(len(sys.argv)>2):
            if(atoms[a].symbol==element):
                moments2.append(moms[a])
for a in range(len(atoms)):
    force=np.sqrt(forces[a][0]**2+forces[a][1]**2+forces[a][2]**2)
    sum+=force
    if(force>largest):
        largest=force

if(len(sys.argv)>2):
    print (moments2)
    
else:
    print ('Moments from file %s' %(file))
    for i in range(len(moments)):
        logger.info(f'{moments[i]} ,')
    logger.info(f'largest force {largest} {sum}')
    # print ('Forces')
    # print ('largest force ',largest,' ',sum)
    if (largest < 0.03):
        logger.info('CONVERGED')
        # print ('CONVERGED')
        subprocess.check_output("echo $PWD ' : CONVERGED with ENERGY %.6f' and MAX FORCE of %.3f > DONE " %(energy, largest), shell=True)
    else:
        logger.info('NOT CONVERGED')
        #print ('NOT CONVERGED')
        subprocess.check_output("echo $PWD ' : CONVERGED with ENERGY %.6f' and MAX FORCE of %.3f > NOT_DONE " %(energy, largest), shell=True)
