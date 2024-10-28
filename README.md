# Information

This repository contains the code for this workshop presentation: Thanh Le, Yusheng Ji, Thanh-Trung Nguyen, John C.S. Lui , " X-armed Bandits for Optimizing Information Freshness in Robots Communication ", IEICE SeMI Vietnam Workshop, Danang, Oct. 2024.

# How to use the code

Main working directory is "core":
```bash
cd core
```

### Step 1: create adhoc wifi link
On `pi01`
```bash
python3 main.py --scenario=wifi_off
python3 main.py --scenario=wifi_on --ip=192.168.1.1
```

On `pi02`
```bash
python3 main.py --scenario=wifi_off
python3 main.py --scenario=wifi_on --ip=192.168.1.2
```

### Step 2: using traffic control command to limit bandwidth

Add interface wlan0
```bash
sudo tc qdisc add dev wlan0 root handle 5:0 hfsc default 1
```

Set bandwidth limit, start from 30Mbit/sec to 35Mbit/sec
```bash
sudo tc class add dev wlan0 parent 5:0 classid 5:1 hfsc sc rate 30Mbit ul rate 35Mbit
```

Set packet loss probability at 0.5%, 50% next step loss probability, set delay 15+-1.5ms using distribution
```bash
sudo tc qdisc add dev wlan0 parent 5:1 netem loss 0.5% 50% delay 15ms 1.5ms 75%
sudo tc qdisc add dev wlan0 parent 5:1 netem loss 0.5% 50% delay 15ms 1.5ms distribution normal
sudo tc qdisc add dev wlan0 parent 5:1 netem loss 0.5% 50% delay 15ms 1.5ms distribution pareto
sudo tc qdisc add dev wlan0 parent 5:1 netem loss 0.5% 50% delay 15ms 1.5ms distribution paretonormal
```

Show current status
```bash
sudo tc qdisc show dev wlan0
```

Reset to default
```bash
sudo tc qdisc del dev wlan0 root
```

In short, in both rasberry pi, run
```bash
python3 main.py --scenario=tc_off
python3 main.py --scenario=tc_on
```

### Step 3: Synchronize time

Installing the "chrony" NTP server is done in a terminal/ssh session via
```bash
sudo apt install chrony
```
and then edit the config file with
```bash
sudo vim /etc/chrony/chrony.conf
```
adding, at the end, these 3 lines
```
server 127.127.1.0
allow
local
```
will create a NTP pseudo server and using the internal clock as reference.
Restart, after the changes, with
```bash
sudo systemctl daemon-reload
sudo systemctl restart chronyd
```

Check status with
```bash
sudo systemctl status chronyd
```

Configure clients
For other RPi:s/devices, acting as clients, in the LAN that has to be synched, edit the config file with
```bash
sudo vim /etc/systemd/timesyncd.conf
```
and after the "[Time]" line just add
```
NTP=nnn.nn.n.n
```
which is the IP, or hostname, of your NTP server. Then restart and check with
```bash
sudo systemctl daemon-reload
sudo systemctl restart systemd-timesyncd
sudo systemctl status systemd-timesyncd
```

### Step 4: Learn best sampling rate
On pi02
```bash
python3 main.py --scenario=receive --receiver=<enter receiver name here> --display_mode=<enter display mode here>
```
Possible algorithm at the receivers are "greedy/finite_difference/vhct".
Possible display modes are "image/aoi".

On pi01
```bash
python3 main.py --scenario=send --display_mode=<enter display mode here>
```

To plot figures:
```bash
python3 main.py --scenario=plot_metric --metric=peak_aoi
python3 main.py --scenario=plot_metric --metric=n_packet
python3 main.py --scenario=legend_metric
```
