import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def plot_aoi_load(args):
    # load csv data
    path = os.path.join(args.csv_dir, f'debug_6.csv')
    df = pd.read_csv(path)
    # for each waiting time, filter it's AoI
    loads = []
    aois  = []
    for n_wait in [19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]:
        load = 1 / (n_wait * args.dt * 128)
        aoi  = df[df['n_wait'] == n_wait]['peak_aoi'].to_numpy().mean()
        loads.append(load)
        aois.append(aoi)
    # plot
    plt.plot(loads, aois, 'k-o', label='D/G/1')
    # decorate
    plt.xlim((0, 1.5))
    plt.xlabel('load')
    plt.ylabel('average AoI')
    plt.legend()
    # save
    plt.tight_layout()
    path = os.path.join(args.figure_dir, f'{args.scenario}.pdf')
    plt.savefig(path)
