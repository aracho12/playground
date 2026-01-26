
import os
import sys
import numpy as np
from ase.io import read, write
import subprocess
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
home=os.path.expanduser('~')
homebin=home+'/bin'
vtstscript = 'vtstscripts-972'
vtstscript_path = homebin+'/'+vtstscript

def run_bader():
    subprocess.run(['{}/chgsum.pl'.format(vtstscript_path), 'AECCAR0', 'AECCAR2'])
    subprocess.run(['bader', 'CHGCAR', '-ref', 'CHGCAR_sum'])
    return True


def get_bader_charges(traj='OUTCAR'):
    """
    Calculates net charges for atoms based on Bader analysis (ACF.dat) and a structure file.
    
    Args:
        traj (str): Path to the structure file (e.g., OUTCAR, POSCAR, .traj). Default is 'OUTCAR'.
        
    Returns:
        list: A list of calculated net charges.
    """
    
    # Check if input files exist
    if not os.path.exists("ACF.dat"):
        # check if AECCAR0 and AECCAR2 exist
        if os.path.exists('AECCAR0') and os.path.exists('AECCAR2'):
            run_bader()
        else:
            print("Error: AECCAR0 and AECCAR2 do not exist.")
            return []        

    # Parse ACF.dat to get Bader charges
    # ACF.dat format:
    # ... header ...
    #    1      x      y      z      CHARGE      MIN_DIST      ATOMIC_VOL
    # ...
    bader_raw_charges = []
    try:
        with open("ACF.dat", "r") as f:
            for line in f:
                parts = line.split()
                # Data lines start with an integer index and have enough columns
                if parts and parts[0].isdigit() and len(parts) >= 5:
                    # Column 5 (index 4) contains the charge
                    bader_raw_charges.append(float(parts[4]))
    except Exception as e:
        print(f"Error parsing ACF.dat: {e}")
        return []

    bader_raw_charges = np.array(bader_raw_charges)

    # Read structure to get atom symbols
    try:
        atoms = read(traj)
        symbols = atoms.get_chemical_symbols()
    except Exception as e:
        print(f"Error reading structure from {traj}: {e}")
        return []

    # Validation
    if len(symbols) != len(bader_raw_charges):
        print(f"Error: Number of atoms in {traj} ({len(symbols)}) does not match entries in ACF.dat ({len(bader_raw_charges)}).")
        return []

    # ZVAL (Valence Electron) Dictionary
    # This defines the reference number of valence electrons for neutral atoms.
    # Note: These values depend on the specific POTCARs used (e.g. _sv, _pv potentials).
    zval_dict = {
        'H': 1, 'Li': 1, 'Na': 1, 'K': 7, 'Rb': 1, 'Cs': 1, # Alkalis
        'Be': 2, 'Mg': 2, 'Ca': 2, 'Sr': 2, 'Ba': 2,        # Alkaline earths
        'Sc': 3, 'Y': 11, 'La': 11,                         # Group 3 (Y_sv, La usually 11 in VASP)
        'Ti': 4, 'Zr': 12.0, 'Hf': 4,                       # Group 4 (Zr_sv=12)
        'V': 5, 'Nb': 11.0, 'Ta': 5,                        # Group 5 (Nb_pv=11)
        'Cr': 6, 'Mo': 14, 'W': 6,                          # Group 6 (Mo_pv=14)
        'Mn': 7, 'Tc': 7.0, 'Re': 7,                        # Group 7
        'Fe': 8, 'Ru': 8.0, 'Os': 8,                        # Group 8
        'Co': 9, 'Rh': 9.0, 'Ir': 9,                        # Group 9
        'Ni': 10, 'Pd': 10.0, 'Pt': 10,                     # Group 10
        'Cu': 11, 'Ag': 11.0, 'Au': 11,                     # Group 11
        'Zn': 12, 'Cd': 12.0, 'Hg': 12,                     # Group 12
        'B': 3, 'Al': 3, 'Ga': 3, 'In': 3.0, 'Tl': 3,       # Group 13
        'C': 4, 'Si': 4, 'Ge': 4, 'Sn': 4.0, 'Pb': 4,       # Group 14
        'N': 5, 'P': 5, 'As': 5, 'Sb': 5.0, 'Bi': 5,        # Group 15
        'O': 6, 'S': 6, 'Se': 6, 'Te': 6, 'Po': 6,          # Group 16
        'F': 7, 'Cl': 7, 'Br': 7, 'I': 7,                   # Group 17
        'Ce': 12, 'Sm': 11                                  # Lanthanides (VASP specific)
    }

    net_charges = []
    out_filename = 'bader_charges.tsv'
    
    print(f"Writing charges to {out_filename}...")
    
    with open(out_filename, 'w') as f:
        f.write("# index\t name\t charge\n")
        
        for i, symbol in enumerate(symbols):
            if symbol not in zval_dict:
                print(f"Warning: Element {symbol} not in ZVAL dictionary. Net charge set to NaN.")
                net_charge = float('nan')
            else:
                # Net Charge = ZVAL - Bader Charge
                net_charge = zval_dict[symbol] - bader_raw_charges[i]
            
            # Formatting
            net_charge_round = round(net_charge, 2)
            net_charges.append(net_charge_round)
            
            # Print to stdout and file
            print(f"index: {i}\t name: {symbol}\t charge: {net_charge:.2f}")
            f.write(f"{i}\t {symbol}\t {net_charge:.6f}\n")

    return net_charges

if __name__ == "__main__":

    # if restart.json exists, copy it to initial.json
    if os.path.exists('restart.json'):
        subprocess.run(['cp', 'restart.json', 'initial.json'])
        logger.info("copy restart.json to initial.json")
    else:
        logger.info("restart.json does not exist")

    # Allow passing trajectory file as argument
    traj_file = 'OUTCAR'
    if len(sys.argv) > 1:
        traj_file = sys.argv[1]
    write_charge_traj, write_magmom = False, False
    atoms = read(traj_file)
    energy = atoms.get_potential_energy()
    forces = atoms.get_forces()
    logger.info(f"get energy from {traj_file}")
    logger.info(f"energy: {energy}")
        
    charges = get_bader_charges(traj_file)
    if charges:
        logger.info("get bader charges")
        write_charge_traj=True
        atoms = read(traj_file)
        atoms.set_initial_charges(charges)
        write('atoms_bader_charge.json', atoms)
        logger.info("write atoms_bader_charge.json")
    else:
        print("Error: No charges found. Please run bader analysis first.")
        write_charge_traj=False
    try:
        os.system("grep LORBIT INCAR | grep -v '#' ")
        moms=atoms.get_magnetic_moments()
        write_magmom=True
    except:
        write_magmom=False
        if not write_magmom:
            logger.error("can't get magnetic moments ; LORBIT or SPIN off")

    if write_magmom:
        moms=atoms.get_magnetic_moments()
        atoms.set_initial_magnetic_moments(moms)
        logger.info("set initial magnetic moments")
    
    if write_charge_traj:
        atoms.set_initial_charges(charges)
        logger.info("set initial charges")
        write('atoms_bader_charge.json', atoms)
        logger.info("write atoms_bader_charge.json")
        # remove AECCAR0, AECCAR2, CHG, CHGCAR_sum
        subprocess.run(['rm', 'AECCAR*', 'CHG*'])
        logger.info("remove AECCAR* and CHG*")
    else:
        print("Error: No charges found. Please run bader analysis first.")
    write('restart.json', atoms)
    logger.info("write restart.json")
    sum=0.0
    largest=0.0
    for a in range(len(atoms)):
        force=np.sqrt(forces[a][0]**2+forces[a][1]**2+forces[a][2]**2)
        sum+=force
        if(force>largest):
            largest=force
    logger.info(f"largest force: {largest}")
    logger.info(f"sum of forces: {sum}")
    if (largest < 0.03):
        logger.info('CONVERGED')
        subprocess.check_output("echo $PWD ' : CONVERGED with ENERGY %.6f' and MAX FORCE of %.3f > DONE " %(energy, largest), shell=True)
    else:
        logger.info('NOT CONVERGED')
        subprocess.check_output("echo $PWD ' : CONVERGED with ENERGY %.6f' and MAX FORCE of %.3f > NOT_DONE " %(energy, largest), shell=True)
