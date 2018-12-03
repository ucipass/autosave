from netmiko import Netmiko
from getpass import getpass
import re
import yaml
import sys
import csv
import time
import os
import argparse

dir = os.path.dirname(os.path.realpath(__file__))
dir = os.path.join(dir, 'ntc-templates','templates')
os.environ["NET_TEXTFSM"] = dir
print(os.environ["NET_TEXTFSM"])

def sshShowRun(device_type):
    global inventory
    global mac

    host = "10.255.254.10"
    username = "aarato"
    password = "C!sc0123"
    try:
        print("Saving configration file for:", host)
        net_connect = Netmiko(host=host, username=username, password=password, device_type=device_type, timeout=10)
        hostname = net_connect.find_prompt()
        hostname = re.sub('#','', hostname )
        cmd_output = net_connect.send_command("term len 0", use_textfsm=False)
        cmd_output = net_connect.send_command("show interface status", use_textfsm=True)
        if 'hostname' in cmd_output:
            print("  Saved Configuration files as:")
        else:
            print("  Configration file was NOT saved for:", cmd_output)
    except Exception as e:
        print("  Configration file was NOT saved for:", host)
        print(e)

sshShowRun("cisco_ios")
