import os

def wifi_off(args):
    cmds = [
        f'sudo ip link set wlan0 down',
    ]
    for cmd in cmds:
        print(cmd)
        os.system(cmd)
