from PyXAB.synthetic_obj.Garland import Garland
from PyXAB.algos.Zooming import Zooming
from PyXAB.algos.VHCT import VHCT

import matplotlib.pyplot as plt
import numpy as np
import os

def benchmark(algo):
    # parameter for xab
    n_round   = 1000
    target    = Garland()
    domain    = [[0, 1]]
    algo      = algo(domain=domain)
    # initialize
    cumulative_regret      = 0
    cumulative_regret_list = []
    # run
    for t in range(1, n_round + 1):
        # select point
        point  = algo.pull(t)
        # compute reward
        reward = target.f(point) + np.random.uniform(-0.1, 0.1)
        algo.receive_reward(t, reward)
        # compute regret
        instant_regret     = target.fmax - target.f(point)
        cumulative_regret += instant_regret
        cumulative_regret_list.append(cumulative_regret)
    return cumulative_regret_list

def test(args):
    # run benchmark for VHCT
    cumulative_regret_list = benchmark(VHCT)
    # plot regret
    plt.plot(cumulative_regret_list, label='VHCT')
    # run benchmark for Zooming
    cumulative_regret_list = benchmark(Zooming)
    # plot regret
    plt.plot(cumulative_regret_list, label='Zooming')
    # decorate
    plt.xlabel('rounds')
    plt.xlabel('regret')
    plt.legend()
    # save plot
    plt.tight_layout()
    path = os.path.join(args.figure_dir, f'regret.pdf')
    plt.savefig(path)
