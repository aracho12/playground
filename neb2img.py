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
)
ase_view.config.uc_dash_pattern=(.6,.4) # "help": "A (length, gap) dash pattern for unit cell lines."
ase_view.config.canvas_color_background = "white"
ase_view.config.canvas_background_opacity = 0.2

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


if len(sys.argv)==2:
    if sys.argv[1] == '-h':
        print("Usage: python3 neb2img.py POSCAR or CONTCAR")
    else:
        filename = sys.argv[1]
else:
    filename='CONTCAR'
    

fol='.'
dir_list = [name for name in os.listdir(fol) if os.path.isdir(name)]
dir_list = [d for d in dir_list if d[-1].isdigit() and d[0].isdigit()]
dir_list.sort()
num_dir = len(dir_list)
print(dir_list)

# Get the number of rows and columns for the subplots
num_row = 1
num_col = num_dir

fig, _ = plt.subplots(dpi=300, figsize=(9,5))
_.axis("off")

for i in range(num_dir):
    if filename in os.listdir(dir_list[i]):
        ax = fig.add_subplot(num_row, num_col, i+1)
        os.chdir(dir_list[i])
        atoms=read(filename)
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
        os.chdir('..')
        
# save the figure
plt.savefig('neb2img.png', dpi=300, bbox_inches='tight')
print("neb2img.png created")

fig, _ = plt.subplots(dpi=300, figsize=(7,3.5))
_.axis("off")
for i in range(num_dir):
    if filename in os.listdir(dir_list[i]):
        num_row = 2
        num_col = 3
        ax = fig.add_subplot(num_row, num_col, i+1)
        os.chdir(dir_list[i])
        svgs=single_view(atoms)
        string=svgs.tostring()       
        svg_string = string
        png_file = cairosvg.svg2png(bytestring=svg_string)
        fp = io.BytesIO(png_file)
        with fp:
            img = mpimg.imread(fp, format='png')
        ax.imshow(img)
        ax.set_title(dir_list[i], fontsize='small')
        ax.axis("off")
        os.chdir('..')        
plt.subplots_adjust(wspace=0, hspace=0.2)

# save the figure
plt.savefig('neb2repeat.png', dpi=300, bbox_inches='tight')
    
print("neb2repeat.png created")

end_time = time.time()
running_time = end_time - start_time

print("Running time:", running_time, "seconds")
# plt.show()
