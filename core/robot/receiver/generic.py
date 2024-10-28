import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import threading
import time
import os

class GenericReceiver:

    def __init__(self, args):
        # save args
        self.args = args
        # data
        self.csv_data = {'timestamp': [], 'n_packet': [], 'action': [], 'n_wait': [], 'delay': [], 'peak_aoi': [], 'temperature': []}
        self.latest_update_timestamp = None
        self.is_completed = False
        self.ts   = []
        self.aois = []

    def update_csv(self, now, n_packet, action, n_wait, delay, peak_aoi, temperature=1):
        self.csv_data['timestamp'].append(now)
        self.csv_data['n_packet'].append(n_packet)
        self.csv_data['action'].append(action)
        self.csv_data['n_wait'].append(n_wait)
        self.csv_data['delay'].append(delay)
        self.csv_data['peak_aoi'].append(peak_aoi)
        self.csv_data['temperature'].append(temperature)

    def export_csv(self):
        # extract args
        args = self.args
        # load data to pandas
        df = pd.DataFrame(self.csv_data)
        # dump pandas data frame to csv file
        path = os.path.join(args.csv_dir, f'{args.receiver}_{args.seed:d}.csv')
        df.to_csv(path, index=None)

    def receive_message(self):
        # extract args
        args = self.args
        # bind
        address = (args.to_ip, args.to_port)
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn.bind(address)
        # handling incoming messages
        # TODO
        # close receiving socket
        conn.close()

    def send_action(self):
        # extract args
        args = self.args
        # bind
        address = (args.to_ip, args.to_port)
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn.bind(address)
        # sending action
        # TODO
        # close receiving socket
        conn.close()

    def track_aoi(self):
        # extract args
        args = self.args
        # wait until 1st packet has arrived
        while self.latest_update_timestamp is None:
            # wait for next timeslot to measure AoI
            time.sleep(args.dt / 2)
        t = 0
        while not self.is_completed:
            # measure aoi and add aoi+timestamp to list
            aoi = time.time() - self.latest_update_timestamp
            self.ts.append(t)
            self.aois.append(aoi)
            t += 1
            # wait for next timeslot to measure AoI
            time.sleep(args.dt / 2)

    def display_aoi(self):
        # extract args
        args = self.args
        # enable interactive mode
        plt.ion()
        # wait for 1st packet has arrive
        while len(self.aois) <= 0:
            # wait for next display interval
            time.sleep(args.display_update_interval)
        # place holder a line
        line, = plt.plot([0], [0], linewidth=1.0)
        # decorate
        plt.ylabel('AoI')
        plt.xlabel('time (s)')
        # plot
        while not self.is_completed:
            # extract t_max
            t_max = max(self.ts) + 1
            # extract data
            ts = np.arange(t_max) * args.dt / 2
            aois = np.array(self.aois[:t_max])
            # plot aoi
            line.set_data(ts, aois)
            # recompute limits and rescale
            x_min = max((t_max + 10) * args.dt / 2 - 10, - 10 * args.dt / 2)
            x_max = (t_max + 10) * args.dt / 2
            plt.xlim(x_min, x_max)
            y_min = np.min(aois[max(int(x_min / args.dt * 2), 0): t_max])
            y_max = np.max(aois[max(int(x_min / args.dt * 2), 0): t_max])
            plt.ylim(-0.01 + y_min, y_max + 0.01)
            # draw new data
            plt.draw()
            # wait for next display interval
            plt.pause(args.display_update_interval)

    def display_image(self):
        # extract args
        args = self.args
        # turn on the interactive mode.
        plt.ion()
        # create a figure and an axis.
        fig, ax = plt.subplots()
        # wait until the 1st packet
        while self.start_timestamp is None:
            time.sleep(args.dt)
        # create the 1st imshow plot.
        img = ax.imshow(self.image, cmap='gray')
        # loop update the plot
        while not self.is_completed:
            # update the image data
            img.set_data(self.image)
            # pause the plot
            plt.pause(args.dt)

    def display(self):
        # extract args
        args = self.args
        # choose display mode
        if args.display_mode == 'aoi':
            self.display_aoi()
        elif args.display_mode == 'image':
            self.display_image()
        else:
            raise NotImplementedError

    def run(self):
        # extract args
        args = self.args
        # create two threads for bidirectional communication
        t1 = threading.Thread(target=self.receive_message)
        t2 = threading.Thread(target=self.send_action)
        # create one thread to track AoI
        t3 = threading.Thread(target=self.track_aoi)
        # start both thread
        t1.start()
        t2.start()
        t3.start()
        # interactive display on the main thread
        self.display()
        # wait for both thread to finish
        t1.join()
        t2.join()
        t3.join()
        # export csv
        self.export_csv()
