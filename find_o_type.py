"""
Ara Cho, Mar, 2023 @SUNCAT
description: distinguish the OOH, OH and O atoms in the input file.
usage: python3 find_o_type.py -i [filename]

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
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input file', default='final_with_calculator.json')
args = parser.parse_args()

if args.input:
    print('Your inputfile is:', args.input)
    if os.path.exists(args.input):
        atoms=read(args.input)
    else:
        print('The input file does not exist.')
        print('usage: python3 find_o_type.py -i filename')
        exit()

o_index = [atom.index for atom in atoms if atom.symbol=='O']
h_index = [atom.index for atom in atoms if atom.symbol=='H']

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
        row.update({'O_type': 'H2O', 'H1_idx': int(h_neighbor), 'd(O1-H1)(Å)': h1_d, 'H2_idx': int(h2_neighbor), 'd(O1-H2)(Å)': h2_d})
    elif len(neighbors) == 1 and len(h_neighbors) == 0:
        o_neighbor, o_d = neighbors[0]
        row.update({'O_type': 'O2', 'O2_idx': int(o_neighbor), 'd(O1-O2)(Å)': o_d})

    data.append(row)

df = pd.DataFrame(data)
new_order = ['O_type', 'O1_idx', 'H1_idx', 'H2_idx', 'O2_idx', 'd(O1-H1)(Å)', 'd(O1-H2)(Å)', 'd(O1-O2)(Å)']
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

if 'O2' in df['O_type'].unique():
    o2_df = df[df['O_type'] == 'O2'].copy()
    o2_df[['O1_idx', 'O2_idx']] = np.sort(o2_df[['O1_idx', 'O2_idx']], axis=1)
    df.loc[df['O_type'] == 'O2', ['O1_idx', 'O2_idx']] = o2_df[['O1_idx', 'O2_idx']]

    o2_df = o2_df.drop_duplicates(subset=['O1_idx', 'O2_idx'], keep='first')
    df = pd.concat([df[df['O_type'] != 'O2'], o2_df])

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
