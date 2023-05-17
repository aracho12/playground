""" 
generating povray images from ase atoms objects 
ref: https://github.com/WMD-group/ASE-Tutorials/tree/master/povray-tools
"""
from ase.data import colors
from ase.io import read, write
from ase.io.trajectory import Trajectory
import numpy as np
import sys
import os 
import subprocess
import argparse   

class AsePov():
    def __init__(self, atoms):
        self.atoms=atoms
        farver=[]
        text=[]
        self.kwargs = {}
        for a in self.atoms:
            farver.append(colors.jmol_colors[a.number,:])
            text.append('ase3')
        self.kwargs['colors']=farver
        self.kwargs['textures']=text

    def set_specific_colors(self,at,at_color):
        farver=self.kwargs['colors']
        for i in range(len(at)):	
            if type(at_color[i])==float or type(at_color[i])==int:

                farve=farver[at[i]]*at_color[i]
                farver[at[i]]=np.array([min(1,farve[0]),min(1,farve[1]),min(1,farve[2])])
            else:
                farver[at[i]]=at_color[i]
        self.kwargs['colors']=farver

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input file', default='CONTCAR')
parser.add_argument('-n', '--num', help='n_th image', default=None)
parser.add_argument('-o', '--oxygen', help='oxygen index', default=None, type=int, nargs='+')
parser.add_argument('-o2', '--oxygen2', help='oxygen2 index', default=None, type=int, nargs='+')
parser.add_argument('-h1', '--hydrogen1', help='hydrogen index1', default=None, type=int, nargs='+')
parser.add_argument('-h2', '--hydrogen2', help='hydrogen index2', default=None, type=int, nargs='+')
parser.add_argument('-h3', '--hydrogen3', help='hydrogen index3', default=None, type=int, nargs='+')
parser.add_argument('-r', '--rotation', help='rotation e.g. 90z,-75x', default=['90z,-75x','-75x','-90z,-75x'], type=str, nargs='+')
# parser.add_argument('-s', '--specific', help='set specific colors', default=False, action='store_true')
args = parser.parse_args()

if args.input:
    filename=args.input
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        print('Use -i option to specify input file')
        exit()
    else:
        atoms=read(filename)
        if 'POSCAR' in filename:
            subprocess.run(['ase', 'convert', '-f', filename, 'initial.json'])
            filename='initial.json'
            atoms=read(filename)
        elif 'CONTCAR' in filename:
            subprocess.run(['ase', 'convert', '-f', filename, 'final.json'])
            filename='final.json'
            atoms=read(filename)
        elif 'traj' in filename:
            if args.num:
                num=args.num
                traj = Trajectory(filename)
                atoms = traj[num]
                print('n_th image:', num)
            else:
                traj = Trajectory(filename)
                atoms = traj[-1]
                print('n_th image: last')
        print('Your inputfile is:', filename)
else:
    print('Use -i option to specify input file')
    exit()

PovRay=AsePov(atoms)

if args.oxygen:
    oxygen=args.oxygen
    print('oxygen index:', oxygen)
    if len(oxygen) > 0:
        oxygen=[int(i) for i in oxygen]
        oxygen_color=[(255, 192, 203)]*len(oxygen) # pink
        if oxygen_color[0][0] > 1:
            oxygen_color=np.array(oxygen_color)/255
        PovRay.set_specific_colors(oxygen,oxygen_color)

if args.oxygen2:
    oxygen2=args.oxygen2
    print('oxygen_2 index:', oxygen2)
    if len(oxygen2) > 0:
        oxygen2=[int(i) for i in oxygen2]
        oxygen_color2=[(195, 177, 225)]*len(oxygen2) # purple
        if oxygen_color2[0][0] > 1:
            oxygen_color2=np.array(oxygen_color2)/255
        PovRay.set_specific_colors(oxygen2,oxygen_color2)

if args.hydrogen1:
    hydrogen1=args.hydrogen1
    print('hydrogen_1 index:', hydrogen1)
    if len(hydrogen1) > 0:
        hydrogen1=[int(i) for i in hydrogen1]
        hydrogen_color1=[(116, 241, 247)]*len(hydrogen1) # blue
        if hydrogen_color1[0][0] > 1:
            hydrogen_color1=np.array(hydrogen_color1)/255
        PovRay.set_specific_colors(hydrogen1,hydrogen_color1)

if args.hydrogen2:
    hydrogen2=args.hydrogen2
    print('hydrogen_2 index:', hydrogen2)
    if len(hydrogen2) > 0:
        hydrogen2=[int(i) for i in hydrogen2]
        hydrogen_color2=[(170, 255, 0)]*len(hydrogen2) # green
        if hydrogen_color2[0][0] > 1:
            hydrogen_color2=np.array(hydrogen_color2)/255
        PovRay.set_specific_colors(hydrogen2,hydrogen_color2)

if args.hydrogen3:
    hydrogen3=args.hydrogen3
    print('hydrogen_3 index:', hydrogen3)
    if len(hydrogen3) > 0:
        hydrogen3=[int(i) for i in hydrogen3]
        hydrogen_color3=[(255, 255, 0)]*len(hydrogen3) # yellow
        if hydrogen_color3[0][0] > 1:
            hydrogen_color3=np.array(hydrogen_color3)/255
        PovRay.set_specific_colors(hydrogen3,hydrogen_color3)

if args.rotation:
    rotation=args.rotation
    print('rotation:', rotation)

filename_without_extension = os.path.splitext(filename)[0]

for j, rot in enumerate(rotation): 
    renderer=write(f'{filename_without_extension}_{j}.pov', atoms, rotation=rot,
                    show_unit_cell=0,
                    colors=PovRay.kwargs['colors'],
                    povray_settings=dict(     
                    display=False,
                    pause=False,
                    canvas_width=300,
                    #canvas_height=560,
                    background='White',
                    transparent=False,
                    #   bondatoms=bonded_atoms,
                    camera_type='perspective',
                    # transmittances=transmittances,
                    textures=PovRay.kwargs['textures'])
                    )
    renderer.render()