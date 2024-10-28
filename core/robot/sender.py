import matplotlib.pyplot as plt
import numpy as np
import threading
import random
import string
import socket
import json
import time

class Sender:

    def __init__(self, args):
        # save args
        self.args = args
        # shared data between threads
        self.is_completed    = False
        self.n_wait          = 0
        self.image           = np.full([args.image_height, args.image_width], 255)
        self.start_timestamp = None

    def generate_random_content(self):
        # extract args
        args = self.args
        return ''.join(random.choices(string.ascii_letters, k=args.content_length))

    def receive_action(self):
        # extract args
        args = self.args
        # bind
        address = (args.from_ip, args.from_port)
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn.bind(address)
        action = 0
        print(f'[+] receiving action at {address=}')
        # ==========================
        # handling incoming messages
        # ==========================
        # listen to sender's action
        while 1:
            try:
                # listen for one packet
                data, _ = conn.recvfrom(2048)
                # try to decode the receiver action
                try:
                    # decode data
                    data = json.loads(data.decode())
                    # decode action
                    if 'action' in data:
                        action = int(data['action'])
                        # update n_wait
                        self.n_wait = max(0, self.n_wait + action)
                        self.n_wait = min(self.n_wait, args.n_state - 1)
                    elif 'n_wait' in data:
                        self.n_wait = float(data['n_wait'])
                    action_delay = time.time() - data['timestamp']
                    print(f'[+] {action=} {self.n_wait=} {action_delay=:0.3f}')
                except json.decoder.JSONDecodeError:
                    pass
                # stopping condition
                if self.is_completed:
                    break
            except KeyboardInterrupt:
                # gracefully exit
                break
        # close receiving socket
        conn.close()

    def send_message(self):
        # extract args
        args = self.args
        # bind
        address = (args.to_ip, args.to_port)
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, 0x01)
        # initialize
        self.start_timestamp = start_timestamp = now = time.time()
        processing_time = 0
        # sending action
        while now - start_timestamp < args.duration:
            try:
                # wait n_wait * dt
                wait_time = max(0, self.n_wait * args.dt - processing_time)
                time.sleep(wait_time)
                # print(f'[+] {self.n_wait=} {wait_time=:0.6f}s')
                # generate message
                tic = time.time()
                data = json.dumps({'timestamp': tic,
                                   'quit'     : False,
                                   'n_wait'   : self.n_wait,
                                   'content'  : self.generate_random_content()})
                # send
                conn.sendto(data.encode(), address)
                now = time.time()
                processing_time = now - tic
            except KeyboardInterrupt:
                # gracefully exit
                self.is_completed = True
                break
        # send final data to the receiver
        data = json.dumps({'timestamp': time.time(), 'quit': True, 'content': ''})
        conn.sendto(data.encode(), address)
        # inform other threads
        self.is_completed = True
        # close receiving socket
        conn.close()

    def track_image(self):
        # extract args
        args = self.args
        X = args.image_height // args.image_step
        Y = args.image_width // args.image_step
        prev_x = 0
        # update the image
        while not self.is_completed:
            if self.start_timestamp is not None:
                # extract timestamp and location of new patch of data
                t = int((time.time() - self.start_timestamp) / args.dt)
                x = t // Y % X
                y = t % Y
                # register new data to self.image
                self.image[0: (x + 1) * args.image_step, \
                           0: (y + 1) * args.image_step] = 0
                # reset plot if needed
                if x < prev_x :
                    self.image[:, :] = 255
                prev_x = x
            # sleep
            time.sleep(args.dt)

    def display_image(self):
        # extract args
        args = self.args
        # turn on the interactive mode.
        plt.ion()
        # create a figure and an axis.
        fig, ax = plt.subplots()
        # Create the imshow plot.
        img = ax.imshow(self.image, cmap='gray')
        # Loop update the plot
        while not self.is_completed:
            # update the image data
            img.set_data(self.image)
            # pause the plot
            plt.pause(args.dt)

    def run(self):
        # extract args
        args = self.args
        # create two threads for bidirectional communication
        t1 = threading.Thread(target=self.send_message)
        t2 = threading.Thread(target=self.receive_action)
        # start both thread
        t1.start()
        t2.start()
        # display image on main thread
        if args.display_mode == 'image':
            t3 = threading.Thread(target=self.track_image)
            t3.start()
            self.display_image()
        # wait for all threads to finish
        t1.join()
        t2.join()
        if args.display_mode == 'image':
            t3.join()
