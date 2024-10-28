import argparse
import os

base_folder = os.path.dirname(os.path.dirname(__file__))

def create_dirs(args):
    for d in [args.csv_dir, args.figure_dir]:
        if not os.path.exists(d):
            os.makedirs(d)

def get_args():
    # create args parser
    parser = argparse.ArgumentParser()
    # scenario
    parser.add_argument('--scenario', type=str, default='main')
    # networking
    parser.add_argument('--ip', type=str, default='192.168.1.1')
    parser.add_argument('--from_ip', type=str, default='192.168.1.1')
    parser.add_argument('--from_port', type=int, default=6000)
    parser.add_argument('--to_ip', type=str, default='192.168.1.2')
    parser.add_argument('--to_port', type=int, default=6000)
    parser.add_argument('--content_length', type=int, default=1024)
    # aoi algorithm
    parser.add_argument('--receiver', type=str, default='periodic')
    parser.add_argument('--dt', type=float, default=0.005)
    parser.add_argument('--update_action_interval', type=float, default=0.001)
    parser.add_argument('--n_wait_initial', type=int, default=1)
    parser.add_argument('--n_sample_min', type=int, default=50)
    # q-learning
    parser.add_argument('--n_state', type=int, default=5)
    parser.add_argument('--n_action', type=int, default=3)
    parser.add_argument('--learning_rate', type=float, default=0.01)
    parser.add_argument('--gamma', type=float, default=0.99)
    parser.add_argument('--start_temperature', type=float, default=1.0)
    parser.add_argument('--end_temperature', type=float, default=0.05)
    parser.add_argument('--decay_rate', type=float, default=0.95)
    parser.add_argument('--decay_gap', type=int, default=1)
    # delayed q-learning
    parser.add_argument('--n_delay', type=int, default=5)
    # thompson sampling
    parser.add_argument('--exp_coeff', type=float, default=1.0)
    # simulation
    parser.add_argument('--duration', type=float, default=30)
    parser.add_argument('--seed', type=int, default=0)
    # plot
    parser.add_argument('--metric', type=str, default='peak_aoi')
    # display
    parser.add_argument('--display_mode', type=str, default='image')
    parser.add_argument('--display_update_interval', type=float, default=0.1)
    # visualization
    parser.add_argument('--image_width', type=int, default=400)
    parser.add_argument('--image_height', type=int, default=200)
    parser.add_argument('--image_step', type=int, default=10)
    # I/O
    parser.add_argument('--csv_dir', type=str, default=f'{base_folder}/data/csv')
    parser.add_argument('--figure_dir', type=str, default=f'{base_folder}/data/figure')
    # parse args
    args = parser.parse_args()
    # create dirs if not existed
    create_dirs(args)
    return args

def print_args(args):
    # print(args)
    pass
