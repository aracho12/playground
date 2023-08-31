"""
Ara Cho, Mar, 2023 @SUNCAT
description: distinguish the OOH, OH and O atoms in the input file.
usage: python3 find_o_type.py [filename]

Output: print following table 
O_type  O1_idx  H1_idx H2_idx O2_idx  d(O1-H1)(Å) d(O1-H2)(Å) d(O1-O2)(Å)
    OH      36      47                      0.983
    OH      37      43                      1.003
    OH      38      46                      1.016
   H2O      39      46     48               1.025       1.029
   H2O      40      46     49               1.022       1.024
   OOH      42      50            41        1.000                   1.403
"""


import pandas as pd
from ase.io import read
import os
import numpy as np
import sys
import subprocess

cutoff=0
if len(sys.argv)==2:
    if sys.argv[1] == '-h':
        print("Usage: python3 find_o_type.py [input_file] [-s]")
    else:
        input_file=sys.argv[1]
elif len(sys.argv)==3:
    input_file=sys.argv[1]
    if not os.path.exists(input_file):
        print("{} is not exists".format(input_file))
        exit()
    if sys.argv[2] == '-s':
        subprocess.call('python ~/bin/for_a_happy_life/layer_grouping.py -i {}'.format(input_file), shell=True)
        print("")
        cutoff_in=input('please enter a cutoff value for a z direction: ')
        cutoff=float(cutoff_in)
else:
    if os.path.exists('final_with_calculator.json'):
        input_file='final_with_calculator.json'
    else:
        print(sys.argv)
        print("Usage: python3 find_o_type.py [input_file]")
        exit()
print("Input file: ", input_file)   


atoms=read(input_file)


if cutoff == 0:
    o_index = [atom.index for atom in atoms if atom.symbol=='O']
    h_index = [atom.index for atom in atoms if atom.symbol=='H']
else:
    print("Cutoff: ", cutoff)
    o_index = [atom.index for atom in atoms if atom.symbol=='O' and atom.z < cutoff]
    h_index = [atom.index for atom in atoms if atom.symbol=='H' and atom.z < cutoff]

data = []

for i in o_index:
    row = {}
    neighbors = []
    h_neighbors = []
    for j in o_index:
        if i != j:
            d = atoms.get_distance(i, j, mic=True)
            if d < 1.6:
                neighbors.append((j, d))
    for j in h_index:
        d = atoms.get_distance(i, j, mic=True)
        if d < 1.2:
            h_neighbors.append((j, d))

    row['O1_idx'] = i

    if len(neighbors) == 0 and len(h_neighbors) == 0:
        row['O_type'] = 'O'
    elif len(neighbors) == 1 and len(h_neighbors) == 1:
        o_neighbor, o_d = neighbors[0]
        h_neighbor, h_d = h_neighbors[0]
        row.update({'O_type': 'OOH', 'H1_idx': int(h_neighbor), 'd(O1-H1)(Å)': h_d, 'O2_idx': int(o_neighbor), 'd(O1-O2)(Å)': o_d})
    elif len(neighbors) == 0 and len(h_neighbors) == 1:
        h_neighbor, h_d = h_neighbors[0]
        row.update({'O_type': 'OH', 'H1_idx': int(h_neighbor), 'd(O1-H1)(Å)': h_d})
    elif len(neighbors) == 0 and len(h_neighbors) == 2:
        h1_neighbor, h1_d = h_neighbors[0]
        h2_neighbor, h2_d = h_neighbors[1]
        row.update({'O_type': 'H2O', 'H1_idx': int(h1_neighbor), 'd(O1-H1)(Å)': h1_d, 'H2_idx': int(h2_neighbor), 'd(O1-H2)(Å)': h2_d})
    elif len(neighbors) == 0 and len(h_neighbors) == 3:
        h1_neighbor, h1_d = h_neighbors[0]
        h2_neighbor, h2_d = h_neighbors[1]
        h3_neighbor, h3_d = h_neighbors[2]
        row.update({'O_type': 'H3O', 'H1_idx': int(h1_neighbor), 'd(O1-H1)(Å)': h1_d, 'H2_idx': int(h2_neighbor), 'd(O1-H2)(Å)': h2_d, 'H3_idx': int(h3_neighbor), 'd(O1-H3)(Å)': h3_d})
    elif len(neighbors) == 1 and len(h_neighbors) == 0:
        o_neighbor, o_d = neighbors[0]
        row.update({'O_type': 'O2', 'O2_idx': int(o_neighbor), 'd(O1-O2)(Å)': o_d})

    data.append(row)

df = pd.DataFrame(data)
if 'H3_idx' not in df.columns:
    new_order = ['O_type', 'O1_idx', 'H1_idx', 'H2_idx', 'O2_idx', 'd(O1-H1)(Å)', 'd(O1-H2)(Å)', 'd(O1-O2)(Å)']
elif 'O2_idx' not in df.columns:
    new_order = ['O_type', 'O1_idx', 'H1_idx', 'H2_idx', 'H3_idx', 'd(O1-H1)(Å)', 'd(O1-H2)(Å)', 'd(O1-H3)(Å)']
elif 'H3_idx' not in df.columns and 'O2_idx' not in df.columns:
    new_order = ['O_type', 'O1_idx', 'H1_idx', 'H2_idx', 'd(O1-H1)(Å)', 'd(O1-H2)(Å)']
else:
    new_order = ['O_type', 'O1_idx', 'H1_idx', 'H2_idx', 'O2_idx', 'H3_idx', 'd(O1-H1)(Å)', 'd(O1-H2)(Å)', 'd(O1-H3)(Å)', 'd(O1-O2)(Å)']
df = df.reindex(columns=new_order)
df = df.dropna(subset=['O_type'])


# df = df.drop(columns=['O_idxs'])

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)

idx_cols = [col for col in df.columns if 'idx' in col]
dist_cols = [col for col in df.columns if 'd(' in col]

# remove the rows when O_type is O2, [O1_idx, O2_idx] are duplicated

df = df.dropna(subset=['O_type'])
df = df.replace('', float('nan'))
df = df.fillna(0)

# if 'O2' in df['O_type'].unique():
#     o2_df = df[df['O_type'] == 'O2'].copy()
#     o2_df[['O1_idx', 'O2_idx']] = np.sort(o2_df[['O1_idx', 'O2_idx']], axis=1)
#     df.loc[df['O_type'] == 'O2', ['O1_idx', 'O2_idx']] = o2_df[['O1_idx', 'O2_idx']]

#     o2_df = o2_df.drop_duplicates(subset=['O1_idx', 'O2_idx'], keep='first')
#     df = pd.concat([df[df['O_type'] != 'O2'], o2_df])

# remove the rows when O_type is O2, [O1_ids or O2_idx] are included in OOH already.

ooh_df = df[df['O_type'] == 'OOH']
o2_df = df[df['O_type'] == 'O2']

o2_to_remove = []
for idx, row in o2_df.iterrows():
    o1, o2 = row['O1_idx'], row['O2_idx']
    if o1 in ooh_df['O1_idx'].values or o1 in ooh_df['O2_idx'].values or \
       o2 in ooh_df['O1_idx'].values or o2 in ooh_df['O2_idx'].values:
        o2_to_remove.append(idx)

df = df.drop(index=o2_to_remove).reset_index(drop=True)


for col in idx_cols:
    df[col] = df[col].astype(int)
    df[col] = df[col].replace({0: ''})

for col in dist_cols:
    df[col] = df[col].round(3)

for col in dist_cols:
    if df[col].notna().all():
        df[col] = df[col].replace({0: '', 0.000: ''})


print(df.to_string(index=False))
df.to_csv('o_type.csv', index=False)
#print('Data saved to o_type.csv')
