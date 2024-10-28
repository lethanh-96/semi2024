from robot.receiver.generic import GenericReceiver
import socket
import json
import time

class PeriodicReceiver(GenericReceiver):

    def __init__(self, args):
        super().__init__(args)

        # shared data between threads
        self.is_connected = False
        self.is_completed = False
        self.action       = 0
        self.n_wait       = args.n_wait_initial

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
                # check if completed, inform other threads to stop
                if data['quit']:
                    self.is_completed = True
                    break
                # try to decode sender's data
                try:
                    # update new delay and peak aoi
                    now       = time.time()
                    delay     = now - data['timestamp']
                    peak_aoi  = now - prev_data['timestamp']
                    n_packet += 1
                    prev_data = data
                    self.is_connected = True
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
        # sleep until connected
        while not self.is_connected:
            time.sleep(args.update_action_interval)
        # send initial action
        response = json.dumps({'action': args.n_wait_initial, 'timestamp': time.time()})
        conn.sendto(response.encode(), address)
        # wait until end
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
