"""
Ara Cho, Apr 2023 @SUNCAT
description: generate POSCAR and CONTCAR images from calculation folders
usage: python show_ini_fin.py [-r]
run this script in the directory where folders (00,01,02..) are located

it requires ase_notebook package
"""

from ase_notebook import AseView, ViewConfig, get_example_atoms, concatenate_svgs, svg_to_pdf
import base64
import cairosvg
import os
import io
from ase import Atom, Atoms
from ase.io import read, write
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import sys
import time
import numpy as np

start_time = time.time()

config = ViewConfig()
ase_view = AseView(config)
ase_view = AseView(
    rotations="45x,45y,45z",
    atom_font_size=14,
    axes_length=30,
    canvas_size=(400, 400),
    zoom=1.2, #"3D camera zoom."
    show_bonds=True, # "Show atomic bonds."
    atom_show_label=True,
    atom_label_by="index", # "element", "index", "tag", "magmom", "charge", "array"
    atom_lighten_by_depth = 0.0,
    radii_scale=1.35,
    bond_pairs_filter=[('Li', 'S'), ('S', 'S')],
    bond_opacity=1.0,
    atom_opacity=1.0,
)
ase_view.config.uc_dash_pattern=(.6,.4) # "help": "A (length, gap) dash pattern for unit cell lines."
ase_view.config.canvas_color_background = "white"
# ase_view.config.canvas_background_opacity = 0.0

def atoms_view(atoms):
    svgs = []
    for rot in ["-60x", "0x", "-90x"]:
        ase_view.config.rotations = rot
        if rot == "0x":
            ase_view.config.atom_show_label = True
        else:
            ase_view.config.atom_show_label = False
        svgs.append(
            ase_view.make_svg(atoms, center_in_uc=False)
        )
    return concatenate_svgs(
        svgs, max_columns=1, scale=1.2, label=False)


ase_view2=ase_view.copy()
ase_view2.config.canvas_size = (400,400) #(800,500)
ase_view2.config.show_bonds=False
ase_view2.config.atom_show_label = False
ase_view2.config.show_unit_cell = True
ase_view2.config.camera_fov=10.0
ase_view2.config.zoom=1.2
ase_view2.config.radii_scale=1.0

def single_view(atoms,rot='0x',repeat=(2,2,1),zoom=1.0):
    svgs = []
    atoms.info["unit_cell_repeat"]=(repeat)

    #ase_view2.config.canvas_crop=(100,250,50,300) #left,right,top,bottom
    
    # Bond
    ase_view2.config.show_bonds=False
    ase_view2.config.bond_opacity= 1.0 # (0~1)
    #ase_view2.config.bond_pairs_filter=[('Li', 'S'), ('S','S')]
    
    ase_view2.config.rotations = rot
    
    ase_view2.config.zoom=zoom
    ase_view2.config.atom_opacity=1.0
    ase_view2.config.show_axes=False
    
    ase_view2.config.camera_fov=10.0
    svg=ase_view2.make_svg(atoms, center_in_uc=False, repeat_uc=repeat)
    svg_string = "".join([svg.tostring()])
    return svg

def atoms_view2(atoms,repeat=(2,2,1)):
    atoms2=atoms.copy()
    atoms2.info["unit_cell_repeat"]=(repeat)
    svgs = []
    for rot in ["-60x", "0x", "-90x"]:
        ase_view2.config.rotations = rot
        if rot == "0x":
            ase_view2.config.atom_show_label = False
        else:
            ase_view2.config.atom_show_label = False
        svgs.append(
            ase_view2.make_svg(atoms2, center_in_uc=False, repeat_uc=repeat)
        )
    return concatenate_svgs(
        svgs, max_columns=1, scale=1.0, label=False)

""" check if file exists """
def get_iteration():
    if 'OSZICAR' in os.listdir():
        with open("OSZICAR") as f:
            lines = f.readlines()
            E0_list = [line.split() for line in lines if "E0" in line][-1]
            iteration = E0_list[0]
            E0=E0_list[4]
            return iteration, E0
    else:
        return 0, 0

def select_input():
    # final
    if 'final_with_calculator.json' in os.listdir():
        final='final_with_calculator.json'
        atoms=read(final)
        E0=atoms.get_potential_energy()
        forces = atoms.get_forces()
        max_force = np.max(np.sqrt(np.sum(forces**2, axis=1)))
        max_force = round(max_force, 3)
        if any(fname.startswith("initial_") for fname in os.listdir()):
            initial = next(fname for fname in os.listdir() if fname.startswith("initial_"))
        else:
            initial = "restart.json"
        if max_force <= 0.030:
            status='Converged'
        else:
            status='Not_converged'
    else:
        if 'CONTCAR' in os.listdir() and os.path.getsize('CONTCAR') > 0:
            iteration, E0 = get_iteration()
            os.system('ase convert -f OUTCAR running_{}.json'.format(iteration))
            initial=[a for a in os.listdir() if a.startswith('initial_')][0]
            final='running_{}.json'.format(iteration)
            status='Running'
            atoms=read(final)
            forces = atoms.get_forces()
            max_force = np.max(np.sqrt(np.sum(forces**2, axis=1)))
            max_force = round(max_force, 3)

        else:
            status='Not_started'
            initial='restart.json'
            final='restart.json'
            max_force = 0
            E0 = 0
    return initial, final, status, E0, max_force


repeat=False
if len(sys.argv)==2:
    if sys.argv[1] == '-h':
        print("Usage: python3 neb2img.py POSCAR or CONTCAR")
    elif sys.argv[1] == '-r':
        repeat=True
    

fol='.'
dir_list = [name for name in os.listdir(fol) if os.path.isdir(name)]
dir_list = [d for d in dir_list if d[-1].isdigit() and d[0].isdigit()]
dir_list.sort()
num_dir = len(dir_list)
if num_dir == 0:
    dir_list=['.']
    num_dir=1
    img_path='./img'
else:
    img_path='../img'
print(dir_list)
input_files=['ini', 'fin']
# Get the number of rows and columns for the subplots
# num_row = 1
# num_col = num_dir


if repeat==False:
    for i in range(num_dir):
        os.chdir(dir_list[i])
        fig, _ = plt.subplots(dpi=250, figsize=(4.5,6))
        _.axis("off")
        initial, final, status, E0, max_force = select_input()
        for j, atoms in enumerate([initial, final]):
            ax = fig.add_subplot(1, 2, j+1)
            atoms=read(atoms)
            svgs=atoms_view(atoms)
            string=svgs.tostr()
            svg_string = string
            png_file = cairosvg.svg2png(bytestring=svg_string)
            fp = io.BytesIO(png_file)
            with fp:
                img = mpimg.imread(fp, format='png')
            ax.imshow(img)
            ax.set_title(f'{dir_list[i]}_{input_files[j]}', fontsize='small')
            ax.axis("off")
            # create folder
        textbox=fig.text(0.5, 0.0, 'This is a text box', ha='center', fontsize=10,
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))
        textbox.set_text(f'{status}\nE0: {E0} eV\nMax force: {max_force} eV/A')
        fig.tight_layout()
        plt.subplots_adjust(bottom=0.1)
        if not os.path.exists(f'{img_path}'):
            os.makedirs(f'{img_path}')
        if dir_list == ['.']:
            plt.savefig(f'{img_path}/final_1x1.png', dpi=250, bbox_inches='tight')
        else:
            plt.savefig(f'{img_path}/{dir_list[i]}.png', dpi=250, bbox_inches='tight')
        print(f'{dir_list[i]}\t initial: {initial}, final: {final}')
        plt.close(fig)
        os.chdir('..')

elif repeat:
    print("2x2 cell")
    for i in range(num_dir):
        os.chdir(dir_list[i])
        fig, _ = plt.subplots(dpi=250, figsize=(5,6))
        _.axis("off")
        initial, final, status, E0, max_force = select_input()
        
        for j, atoms in enumerate([initial, final]):
            ax = fig.add_subplot(1,2, j+1)
            atoms=read(atoms)
            svgs=atoms_view2(atoms) #svgs.tostring() if single_view() svgs.tostr() if atoms_view2()   
            string=svgs.tostr()
            svg_string = string
            png_file = cairosvg.svg2png(bytestring=svg_string)
            fp = io.BytesIO(png_file)
            with fp:
                img = mpimg.imread(fp, format='png')
            ax.imshow(img)
            ax.set_title(f'{dir_list[i]}_{input_files[j]}', fontsize='small')
            ax.axis("off")
            # create folder
        fig.tight_layout()

        if not os.path.exists(f'{img_path}'):
            os.makedirs(f'{img_path}')
        plt.savefig(f'{img_path}/final_2x2_{dir_list[i]}.png', dpi=250, bbox_inches='tight')
        print(f'{dir_list[i]}\t initial: {initial}, final: {final}')
        plt.close(fig)
        os.chdir('..')
        # save the figure
            

end_time = time.time()
running_time = end_time - start_time

print("Running time:", running_time, "seconds")
