import os

def tc_on(args):
    cmds = [
        'sudo tc qdisc add dev wlan0 root handle 1:0 tbf rate 1mbit burst 25kb limit 250kb',
        'sudo tc qdisc show dev wlan0',
    ]
    for cmd in cmds:
        print('[+]', cmd)
        os.system(cmd)
