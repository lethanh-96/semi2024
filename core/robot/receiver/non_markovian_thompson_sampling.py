from robot.receiver.generic import GenericReceiver
import numpy as np
import threading
import socket
import json
import time

class NonMarkovianThompsonSamplingReceiver(GenericReceiver):

    def __init__(self, args):
        super().__init__(args)
        # shared data between threads
        self.is_completed  = False
        self.action        = 0
        self.lock          = threading.Lock()
        self.peak_aoi_list = []
        # thompson sampling parameters
        self.mean          = np.full([args.n_state, args.n_state], 0.5)
        self.count         = np.ones([args.n_state, args.n_state])
        self.var           = np.ones([args.n_state, args.n_state])
        self.learning_step = 0
        self.n_wait = self.state = self.next_state = 0
        # save old n_wait_list, reward for delayed distribution update
        self.n_wait_list   = []
        self.reward_list   = []

    def receive_message(self):
        # extract args
        args = self.args
        # bind
        address = (args.to_ip, args.to_port)
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn.bind(address)
        print(f'[+] receiving message at {address=}')
        # ==========================
        # handling incoming messages
        # ==========================
        # initialize
        n_packet       = 0
        prev_data      = {'timestamp': time.time()}
        # listen to sender's messages
        while 1:
            try:
                # listen for one packet
                data, _ = conn.recvfrom(2048)
                # decode data
                data = json.loads(data.decode())
                # check if completed, inform other threads to stop
                if data['quit']:
                    self.is_completed = True
                    break
                # try to decode sender's data
                try:
                    # update new delay and peak aoi
                    now             = time.time()
                    delay           = now - data['timestamp']
                    peak_aoi        = now - prev_data['timestamp']
                    n_packet       += 1
                    prev_data       = data
                    self.n_wait     = data['n_wait']
                    self.next_state = self.n_wait
                    # add peak aoi to list for making decision about action
                    with self.lock:
                        self.peak_aoi_list.append(peak_aoi)
                    # update csv_data
                    self.update_csv(now, n_packet, self.action, self.n_wait, delay, peak_aoi)
                except json.decoder.JSONDecodeError:
                    pass
            except KeyboardInterrupt:
                # gracefully exit
                break
        # ===
        # end
        # ===
        # close receiving socket
        conn.close()

    def select_action(self):
        # extract args
        args   = self.args
        # extract historical data
        if len(self.n_wait_list) == 0:
            n_wait_mean = args.n_wait_initial
        else:
            n_wait_mean = int(np.min(self.n_wait_list))
        # select action using Gaussian reward distribution
        theta  = np.random.randn(args.n_state) * np.sqrt(self.var[n_wait_mean, :]) + self.mean[n_wait_mean, :]
        n_wait = np.argmax(theta)
        n_wait = int(n_wait)
        return n_wait

    def update_sampling_distribution(self):
        # extract args
        args = self.args
        # check if enough of delay
        if len(self.n_wait_list) >= args.n_delay:
            # extract n_wait and reward
            n_wait_mean = int(np.min(self.n_wait_list))
            n_wait      = self.n_wait_list[0]
            reward      = np.mean(self.reward_list[0])
            print(f'{n_wait_mean=} {n_wait=} {reward=:0.3f}')
            # update sampling distribution
            self.mean[n_wait_mean, n_wait]  += (reward - self.mean[n_wait_mean, n_wait]) / self.count[n_wait_mean, n_wait] ** args.exp_coeff
            self.count[n_wait_mean, n_wait] += 1
            self.var[n_wait_mean, n_wait]    = 1 / self.count[n_wait_mean, n_wait] ** args.exp_coeff
            # pop 1st element from n_wait and reward list
            self.n_wait_list.pop(0)
            self.reward_list.pop(0)

    def send_action(self):
        # extract args
        args = self.args
        # bind
        address = (args.from_ip, args.from_port)
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # ==============
        # sending action
        # ==============
        # initialize
        self.n_wait = 0
        # select and send the initial action
        n_wait = self.select_action()
        response = json.dumps({'n_wait': n_wait})
        conn.sendto(response.encode(), address)
        while 1:
            try:
                if len(self.peak_aoi_list) >= args.n_sample_min:
                    # compute reward
                    reward = 1 - np.clip(np.mean(self.peak_aoi_list), 0, 0.5) / 0.5
                    # save n_wait and reward
                    self.n_wait_list.append(n_wait)
                    self.reward_list.append(reward)
                    # print(f'{self.state=} {self.next_state=} {n_wait=} {reward=:0.2f}')
                    # update Q-table
                    self.update_sampling_distribution()
                    # update state
                    self.state = self.next_state
                    # clear peak aoi list after used
                    with self.lock:
                        self.peak_aoi_list.clear()
                    # select new action
                    n_wait = self.select_action()
                    response = json.dumps({'n_wait': n_wait})
                    conn.sendto(response.encode(), address)
                # stopping condition
                if self.is_completed:
                    # dump data to return to sender
                    response = json.dumps({'n_wait': n_wait})
                    conn.sendto(response.encode(), address)
                    break
                # sleep
                time.sleep(args.update_action_interval)
            except KeyboardInterrupt:
                # gracefully exit
                break
        # ===
        # end
        # ===
        # close receiving socket
        conn.close()
