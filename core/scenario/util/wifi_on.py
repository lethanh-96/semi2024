import os

def wifi_on(args):
    cmds = [
        f'sudo ip link set wlan0 down',
        f'sudo iwconfig wlan0 mode ad-hoc',
        f'rfkill unblock wifi',
        f'sudo ip link set up mtu 1500 dev wlan0',
        f'sudo iwconfig wlan0 essid klab-adhoc',
        f'sudo ifconfig wlan0 {args.ip} netmask 255.255.255.0',
    ]
    for cmd in cmds:
        print(cmd)
        os.system(cmd)
