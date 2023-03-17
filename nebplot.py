"""
Ara Cho, Mar, 2023 @SUNCAT
description: plot the spline curve of NEB result.
usage: python nebplot.py
"""

import matplotlib
from matplotlib import pyplot as plt
from aloha import plot_setting # you can turn off the plot_setting
import csv
from matplotlib.ticker import AutoMinorLocator

def pretty_plot(width=None, height=None, plt=None, dpi=None):
    if plt is None:
        plt = matplotlib.pyplot
        if width is None:
            width = matplotlib.rcParams["figure.figsize"][0]
        if height is None:
            height = matplotlib.rcParams["figure.figsize"][1]
        if dpi is not None:
            matplotlib.rcParams["figure.dpi"] = dpi

        fig = plt.figure(figsize=(width, height))
        ax = fig.add_subplot(1, 1, 1)
        matplotlib.rcParams["xtick.minor.visible"]=True
        matplotlib.rcParams["ytick.minor.visible"]=True
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.xaxis.set_minor_locator(AutoMinorLocator(2)) 
    return plt

def splineplot(width=None, height=None, dpi=None, plt=None, show_energy=True):
    x = []
    y = []
    int_x = []
    int_y = []

    with open("spline.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)  # Skip header row
        for row in reader:
            num = float(row[0])
            reaction_coordinate = float(row[1])
            relative_energy = float(row[2])

            x.append(reaction_coordinate)
            y.append(relative_energy)

            if num.is_integer():
                int_x.append(reaction_coordinate)
                int_y.append(relative_energy)

    # Generate the graph

    plt = pretty_plot(width=width, height=height, dpi=dpi, plt=plt)
    plt.plot(x, y, color='#455A64')

    for i, (xval, yval) in enumerate(zip(int_x, int_y)):
        plt.scatter(xval, yval, facecolors='#D32F2F', edgecolors='black',marker="o",zorder=2)
        if show_energy:
            to_plot = [(int_x[0], int_y[0]), (int_x[-1], int_y[-1])]
            max_y = max(int_y)
            min_y = min(int_y)
            max_y_idx = int_y.index(max_y)
            to_plot.append((int_x[max_y_idx], max_y))
            if i == 0 or i == len(int_x)-1 or yval == max_y:
                plt.text(xval, yval, round(yval,2), horizontalalignment='center', verticalalignment='bottom', color='black')

    ylim_max = max_y+(max_y-min_y)*0.1
    plt.ylim(top=ylim_max)
    plt.xlabel("Distance along the path (Å)")
    plt.ylabel("Relative Energy (eV)")
    #plt.grid()
    plt.savefig('neb_spline.png', dpi=300, bbox_inches='tight')
    #plt.show()
    print("neb_spline.png is generated")

splineplot()
