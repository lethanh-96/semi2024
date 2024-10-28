from robot.receiver.generic import GenericReceiver
import numpy as np
import threading
import socket
import json
import time

class DebugReceiver(GenericReceiver):

    def __init__(self, args):
        super().__init__(args)
        # shared data between threads
        self.is_completed  = False
        self.action        = 0
        self.lock          = threading.Lock()
        self.peak_aoi_list = []
        self.n_wait        = self.state = self.next_state = 0
        self.round         = 0
        self.n_wait_sequence = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

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
        # pull n_wait from list
        n_wait = self.n_wait_sequence[self.round % len(self.n_wait_sequence)]
        return float(n_wait)

    def update_sampling_distribution(self, n_wait, reward):
        # extract args
        args = self.args
        # update sampling distribution
        self.round += 1

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
        response = json.dumps({'n_wait': n_wait, 'timestamp': time.time()})
        conn.sendto(response.encode(), address)
        while 1:
            try:
                if len(self.peak_aoi_list) >= args.n_sample_min:
                    # compute reward
                    avg_peak_aoi = np.mean(self.peak_aoi_list)
                    reward = 1 - avg_peak_aoi / 0.5
                    print(f'{n_wait=:0.2f} {reward=:0.3f}')
                    # update Q-table
                    self.update_sampling_distribution(n_wait, reward)
                    # update state
                    self.state = self.next_state
                    # clear peak aoi list after used
                    with self.lock:
                        self.peak_aoi_list.clear()
                    # select new action
                    n_wait = self.select_action()
                    response = json.dumps({'n_wait': n_wait, 'timestamp': time.time()})
                    conn.sendto(response.encode(), address)
                # stopping condition
                if self.is_completed:
                    # dump data to return to sender
                    response = json.dumps({'n_wait': n_wait, 'timestamp': time.time()})
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
