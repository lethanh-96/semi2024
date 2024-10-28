from statsmodels.nonparametric.smoothers_lowess import lowess
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import japanize_matplotlib
import pandas as pd
import numpy as np
import os

def legend_metric(args):
    # change figure size for poster
    fig        = plt.figure()
    fig_legend = plt.figure(figsize=(16, 3))
    plt.rcParams.update({'font.size': 35})
    # decorate
    colors = [
        'black',
        'blue',
        'red',
    ]
#     labels = [
#         'ゼロ待機',
#         '有限差分',
#         'XAB',
#     ]
    labels = [
        'zero-wait',
        'finite-different',
        'XAB',
    ]
    # plot random data
    ax = fig.add_subplot(111)
    lines = []
    for color in colors:
        line, = ax.plot(np.arange(10), np.random.rand(10), color=color, linewidth=5.0)
        lines.append(line)
    # draw legend
    fig_legend.legend(lines, labels, ncol=3)
    # save legend
    fig_legend.tight_layout()
    path = os.path.join(args.figure_dir, f'{args.scenario}.jpg')
    fig_legend.savefig(path)
