from robot.receiver.generic import GenericReceiver
import numpy as np
import socket
import json
import time

class GreedyReceiver(GenericReceiver):

    def __init__(self, args):
        super().__init__(args)

        # shared data between threads
        self.is_completed    = False
        self.action          = 0
        self.n_wait          = 0
        self.image           = np.full([args.image_height, args.image_width], 255)
        self.start_timestamp = None

    def receive_message(self):
        # extract args
        args = self.args
        X = args.image_height // args.image_step
        Y = args.image_width // args.image_step
        prev_x = 0
        prev_y = 0
        # bind
        address = (args.to_ip, args.to_port)
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn.bind(address)
        conn.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, 0x02)
        print(f'[+] receiving message at {address=}')
        # ==========================
        # handling incoming messages
        # ==========================
        # initialize
        integer_action = 0
        n_packet       = 0
        prev_data      = {'timestamp': time.time()}
        # listen to sender's messages
        while 1:
            try:
                # listen for one packet
                data, _ = conn.recvfrom(2048)
                # decode data
                data = json.loads(data.decode())
                # START TRACK IMAGE
                # register start timestamp
                if self.start_timestamp is None:
                    self.start_timestamp = data['timestamp']
                # extract timestamp and location of new patch of data
                t = int((data['timestamp'] - self.start_timestamp) / args.dt)
                x = t // Y % X
                y = t % Y
                # reset plot if needed
                if x < prev_x:
                    self.image[:, :] = 255
                # register new data to self.image
                self.image[x * args.image_step: (x + 1) * args.image_step, \
                           y * args.image_step: (y + 1) * args.image_step] = 0
                # update prev_x and prev_y
                prev_x, prev_y = x, y
                # END TRACK IMAGE
                # check if completed, inform other threads to stop
                if data['quit']:
                    self.is_completed = True
                    break
                # try to decode sender's data
                try:
                    # update new delay and peak aoi
                    now       = time.time()
                    # update timestamp
                    self.latest_update_timestamp = data['timestamp']
                    delay     = now - data['timestamp']
                    peak_aoi  = now - prev_data['timestamp']
                    n_packet += 1
                    prev_data = data
                    print(f'{n_packet=} {delay=:0.6f}s {peak_aoi=:0.6f}')
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

    def send_action(self):
        # extract args
        args = self.args
        # bind
        address = (args.from_ip, args.from_port)
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # ==============
        # sending action
        # ==============
        while 1:
            try:
                # send new binary action back
                pass
                # stopping condition
                if self.is_completed:
                    # send a response back to the sender
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
