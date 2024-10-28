from statsmodels.nonparametric.smoothers_lowess import lowess
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import japanize_matplotlib
import pandas as pd
import numpy as np
import os


def plot_metric(args):
    # change figure size for poster
    plt.figure(figsize=(12, 10))
    plt.rcParams.update({'font.size': 35})
    # define the list of policy to compare
    receivers = [
        'greedy',
        'finite_different',
        'vhct',
    ]
    labels    = [
        'ゼロ待機',
        '有限差分',
        'XAB',
    ]
    colors    = [
        'black',
        'blue',
        'red',
    ]
    seeds = np.arange(10)

    for j, (receiver, label) in enumerate(zip(receivers, labels)):
        Y = []
        len_min = np.inf
        for seed in seeds:
            # set args
            args.receiver = receiver
            args.seed     = seed
            # load csv data
            path = os.path.join(args.csv_dir, f'{args.receiver}_{args.seed}.csv')
            # print(path)
            df = pd.read_csv(path)
            x = df['timestamp'].to_numpy()
            x = x - np.min(x)
            y = df[args.metric].to_numpy()
            Y.append(y)
            if len(x) < len_min:
                x_len_min = x
                len_min   = len(x)
        # crop data to len_min
        for i in range(len(Y)):
            Y[i] = Y[i][:len_min]
        Y = np.array(Y)
        x_len_min = np.array(x_len_min)
        y = np.mean(Y, axis=0)
        if args.metric == 'peak_aoi':
            # calculate the lowess smooth
            smoothed = lowess(y, x_len_min)
            lowess_values = smoothed[:, 1]
            values = smoothed[:, 0]
            # plot
            plt.plot(x_len_min, lowess_values, color=colors[j], linewidth=5.0)
            plt.scatter(x_len_min, y, color=colors[j], s=0.3)
        else:
            plt.plot(x_len_min, y, color=colors[j], linewidth=5.0)

    # decorate
    # plt.xlabel('時刻「秒」')
    plt.xlabel('timestamp(s)')
    if args.metric == 'peak_aoi':
        plt.ylabel('AoI')
    elif args.metric == 'n_packet':
        # plt.ylabel('送信パケット数')
        plt.ylabel('#packet')
    else:
        plt.ylabel(args.metric)
    # plt.legend()
    if args.metric in ['delay', 'peak_aoi']:
        plt.ylim((-0.1, 1))
    # save figure
    plt.tight_layout()
    path = os.path.join(args.figure_dir, f'{args.metric}.jpg')
    plt.savefig(path)
