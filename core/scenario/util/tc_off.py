import os

def tc_off(args):
    cmds = [
        'sudo tc qdisc del dev wlan0 root'
    ]
    for cmd in cmds:
        print(cmd)
        os.system(cmd)
