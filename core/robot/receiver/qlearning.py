from robot.receiver.generic import GenericReceiver
import numpy as np
import threading
import socket
import json
import time

class QLearningReceiver(GenericReceiver):

    def __init__(self, args):
        super().__init__(args)

        # shared data between threads
        self.is_completed  = False
        self.action        = 0
        self.lock          = threading.Lock()
        self.peak_aoi_list = []
        self.q_table       = np.zeros([args.n_state, args.n_action])
        self.temperature   = args.start_temperature
        self.learning_step = 0
        self.n_wait = self.state = self.next_state = 0

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
                    self.update_csv(now, n_packet, self.action, self.n_wait, delay, peak_aoi, self.temperature)
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
        args = self.args
        # select action using Boltzman distribution
        probs  = np.exp(self.q_table[self.state, :] / self.temperature)
        probs  = probs / np.sum(probs)
        action = np.random.choice([-1, 0, 1], p=probs)
        action = int(action)
        return action

    def update_q_table(self, state, next_state, action, reward):
        # extract args
        args = self.args
        # compute updated q value
        current_q = self.q_table[state, action]
        probs = np.exp(self.q_table[next_state, :] / self.temperature)
        probs = probs / np.sum(probs)
        expected_next_value = np.mean(probs * self.q_table[next_state, :])
        updated_q = (1 - args.learning_rate) * current_q + \
                    args.learning_rate * (reward + args.gamma * expected_next_value)
        # update it on q table
        self.q_table[state, action] = updated_q

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
        action = self.select_action()
        response = json.dumps({'action': action})
        conn.sendto(response.encode(), address)
        while 1:
            try:
                if len(self.peak_aoi_list) >= args.n_sample_min:
                    # compute reward
                    reward = 1 - np.mean(self.peak_aoi_list)
                    print(f'{self.state=} {self.next_state=} {action=} {reward=:0.2f}')
                    # update Q-table
                    self.update_q_table(self.state, self.next_state, action, reward)
                    # update state
                    self.state = self.next_state
                    # add learning step and reduce temperature
                    self.learning_step += 1
                    if self.learning_step % args.decay_gap == 0:
                        self.temperature *= args.decay_rate
                        self.temperature = max(self.temperature, args.end_temperature)
                    # clear peak aoi list after used
                    with self.lock:
                        self.peak_aoi_list.clear()
                    # select new action
                    action = self.select_action()
                    response = json.dumps({'action': action, 'timestamp': time.time()})
                    conn.sendto(response.encode(), address)
                # stopping condition
                if self.is_completed:
                    # send a final response back to the sender
                    action   = 0
                    # dump data to return to sender
                    response = json.dumps({'action': action, 'timestamp': time.time()})
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
