"""
Ara Cho, Mar, 2023 @SUNCAT
description: generate POSCAR and CONTCAR images from calculation folders
usage: python show_ini_fin.py [dir path] default:'.'
run this script in the directory where NEB folders (00,01,02..) are located

it requires ase_notebook package

TODO:
- seperate rows when the number of images is large
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
    atom_font_size=15,
    axes_length=30,
    canvas_size=(400, 400),
    zoom=1.2, #"3D camera zoom."
    show_bonds=True, # "Show atomic bonds."
    atom_show_label=True,
    atom_label_by="index", # "element", "index", "tag", "magmom", "charge", "array"
    atom_lighten_by_depth = 0.0,
    radii_scale=1.5,
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
        svgs, max_columns=1, scale=1.0, label=False)

def single_view(atoms,rot='0x',repeat=(2,2,1),zoom=1.0):
    svgs = []
    atoms.info["unit_cell_repeat"]=(repeat)
    ase_view2=ase_view.copy()
    #ase_view.config.atom_show_label = True
    ase_view2.config.canvas_size = (800,500)
    #ase_view2.config.canvas_crop=(100,250,50,300) #left,right,top,bottom
    
    # Bond
    ase_view2.config.show_bonds=True
    ase_view2.config.bond_opacity= 1.0 # (0~1)
    #ase_view2.config.bond_pairs_filter=[('Li', 'S'), ('S','S')]
    
    ase_view2.config.rotations = rot
    ase_view2.config.radii_scale=1.5
    ase_view2.config.atom_show_label = False
    ase_view2.config.show_unit_cell = True
    ase_view2.config.zoom=zoom
    ase_view2.config.atom_opacity=1.0
    ase_view2.config.show_axes=False
    
    ase_view2.show_uc_repeats= True
    ase_view2.config.camera_fov=10.0
    svg=ase_view2.make_svg(atoms, center_in_uc=False, repeat_uc=repeat)
    svg_string = "".join([svg.tostring()])
    return svg

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
        initial=[a for a in os.listdir() if a.startswith('initial_')][0]
        if max_force < 0.03:
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



# if len(sys.argv)==2:
#     if sys.argv[1] == '-h':
#         print("Usage: python3 neb2img.py POSCAR or CONTCAR")
#     else:
#         current_dir = sys.argv[1]
# else:
#     filename='CONTCAR'
    

fol='.'
dir_list = [name for name in os.listdir(fol) if os.path.isdir(name)]
dir_list = [d for d in dir_list if d[-1].isdigit() and d[0].isdigit()]
dir_list.sort()
num_dir = len(dir_list)
print(dir_list)

# Get the number of rows and columns for the subplots
# num_row = 1
# num_col = num_dir



for i in range(num_dir):
    os.chdir(dir_list[i])
    fig, _ = plt.subplots(dpi=250, figsize=(5,6))
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
        ax.set_title(dir_list[i], fontsize='small')
        ax.axis("off")
        # create folder
    textbox=fig.text(0.5, 0.0, 'This is a text box', ha='center', fontsize=10,
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))
    textbox.set_text(f'{status}\nE0: {E0} eV\nMax force: {max_force} eV/A')
    fig.tight_layout()
    plt.subplots_adjust(bottom=0.1)
    if not os.path.exists('../img'):
        os.makedirs('../img')
    plt.savefig('../img/{}.png'.format(dir_list[i]), dpi=250, bbox_inches='tight')
    print(f'{dir_list[i]}\t initial: {initial}, final: {final}')
    plt.close(fig)
    os.chdir('..')

# fig, _ = plt.subplots(dpi=300, figsize=(7,3.5))
# _.axis("off")
# for i in range(num_dir):
#     if filename in os.listdir(dir_list[i]):
#         num_row = 2
#         num_col = 3
#         ax = fig.add_subplot(num_row, num_col, i+1)
#         os.chdir(dir_list[i])
#         svgs=single_view(atoms)
#         string=svgs.tostring()       
#         svg_string = string
#         png_file = cairosvg.svg2png(bytestring=svg_string)
#         fp = io.BytesIO(png_file)
#         with fp:
#             img = mpimg.imread(fp, format='png')
#         ax.imshow(img)
#         ax.set_title(dir_list[i], fontsize='small')
#         ax.axis("off")
#         os.chdir('..')        
# plt.subplots_adjust(wspace=0, hspace=0.2)

# # save the figure
# plt.savefig('neb2repeat.png', dpi=300, bbox_inches='tight')
    
# print("neb2repeat.png created")

# end_time = time.time()
# running_time = end_time - start_time

# print("Running time:", running_time, "seconds")
# # plt.show()
