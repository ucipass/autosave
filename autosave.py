from netmiko import Netmiko
from getpass import getpass
import re
import yaml
import sys
import csv
import time
import six, collections
import argparse

inventoryFile = "inventory.yml"
inventory = { "cisco_ios" : [], 'cisco_nxos' : []}
arp = []
mac = []

def sshVerify(host, username, password, device_type):
    try:
        net_connect = Netmiko(host=host, username=username, password=password, device_type=device_type, timeout=2)
        net_connect.find_prompt()
        return True
    except Exception as e:
        print(e)
        return None

def sshVerifyInventory(device_type):
    global inventory
    for device in inventory[device_type]:
        host=device['host']
        username=device['username']
        password=device['password']
        result = sshVerify(host, username, password, device_type)
        print(host,"accessible:",result)

def sshGetArp(device_type):
    global inventory
    global arp
    header = ['address', 'mac', 'host', 'interface', 'age', 'type']
    for device in inventory[device_type]:
        host_arp = []
        host=device['host']
        username=device['username']
        password=device['password']
        try:
            print("Retrieving ARP table for:", host)
            net_connect = Netmiko(host=host, username=username, password=password, device_type=device_type, timeout=2)
            hostname = net_connect.find_prompt()
            hostname = re.sub('\W+','', hostname )
            cmd_output = net_connect.send_command("show ip arp", use_textfsm=True)
            if not "ailed" in cmd_output:
                print(" ",cmd_output)
                for item in cmd_output:
                    arpEntry = [item['address'], item['mac'], host, item['interface'], item['age'], item['type']]
                    host_arp.append(arpEntry)
                host_arp = sorted(host_arp, key=None, reverse=False)
                timestr = time.strftime("%Y%m%d-%H%M%S")
                filename = hostname + "_ARP_" + timestr + ".csv"
                writeCSV(header, host_arp, filename)
            else:
                print("Failed:\n", cmd_output)
        except Exception as e:
            print(e)
        arp = arp + host_arp
    filename = "ALL_ARP_" + timestr + ".csv"
    arp = sorted(arp, key=None, reverse=False)
    writeCSV(header,arp,filename)

def sshGetMac(device_type):
    global inventory
    global mac
    header = ['vlan','destination_address', 'destination_port', 'type', 'host']
    for device in inventory[device_type]:
        host_mac = []
        host=device['host']
        username=device['username']
        password=device['password']
        try:
            print("Retrieving MAC table for:", host)
            net_connect = Netmiko(host=host, username=username, password=password, device_type=device_type, timeout=2)
            hostname = net_connect.find_prompt()
            hostname = re.sub('\W+','', hostname )
            cmd_output = net_connect.send_command("show mac address-table", use_textfsm=True)
            if not 'nvalid' in cmd_output:
                print(" ",cmd_output)
                for item in cmd_output:
                    macEntry = [item['vlan'], item['destination_address'], item['destination_port'], item['type'], host]
                    host_mac.append(macEntry)
                host_mac = sorted(host_mac, key=None, reverse=False)
                timestr = time.strftime("%Y%m%d-%H%M%S")
                filename = hostname + "_MAC_" + timestr + ".csv"
                writeCSV(header, host_mac, filename)
            else:
                print("  Failed to retrieve MAC table for: ", host)
        except Exception as e:
            print(e)
        mac = mac + host_mac
    mac = sorted(mac, key=None, reverse=False)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = "ALL_MAC_" + timestr + ".csv"
    writeCSV(header,mac,filename)

def sshShowRun(device_type):
    global inventory
    global mac
    for device in inventory[device_type]:
        host=device['host']
        username=device['username']
        password=device['password']
        try:
            print("Saving configration file for:", host)
            net_connect = Netmiko(host=host, username=username, password=password, device_type=device_type, timeout=2)
            hostname = net_connect.find_prompt()
            hostname = re.sub('\W+','', hostname )
            cmd_output = net_connect.send_command("show run", use_textfsm=True)
            timestr = time.strftime("%Y%m%d-%H%M%S")
            filename = hostname + "_CONFIG_" + timestr + ".txt"
            if 'hostname' in cmd_output:
                text_file = open(filename, "w")
                text_file.write(cmd_output)
                text_file.close()
                print("  Saved Configuration files as:",filename)
            else:
                print("  Configration file was NOT saved for:", host)
        except Exception as e:
            print("  Configration file was NOT saved for:", host)
            print(e)

def writeCSV(header,data,filename):
    # sample data [[1,2],[3,4],[5,6]]
    kwargs = {'newline': ''}
    mode = 'w'
    if sys.version_info < (3, 0):
        kwargs.pop('newline', None)
        mode = 'wb'

    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=',')
        writer.writerow(header)
        writer.writerows(data)


def writeYAML(data):
    with open(inventoryFile, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)

def readYAML():
    global inventory
    try:
        with open(inventoryFile, 'r') as stream:
            inventory = yaml.load(stream)
            pass
    except yaml.YAMLError as exc:
        print("YAML Parsing Error, please fix or delete inventory file:", inventoryFile)
        print(exc)
    except FileNotFoundError as exc:
        print("You have no inventory file: "+inventoryFile+"!")
        print("Would you like to add one? y/n (Default: no):")
        answer = input()
        if answer == 'y':
            addEntries()
        else:
            print('Exiting due to missing inventory file.')
            sys.exc_info()[0]
    except:
        print("Unexpected error:")
        print(sys.exc_info()[0])
        raise

def addEntry(device_type):
    print ("Enter hostname or IP address:",)
    host = input()
    print ("Enter username address:",)
    username = input()
    print ("Enter password:",)
    password = getpass('Password:')
    entry = sshVerify(host, username, password, device_type)
    if entry:
        inventory[device_type].append({'host': host, 'username' : username, 'password' : password})
        writeYAML(inventory)

def addEntries():
    answer = ''
    while answer != 'n':
        print ("What would you like to add to inventory?")
        print ("(i)os/n(x)os/(n)othing (Default: (n)othing)")
        answer = input()
        entry = None
        if answer == "i":
            addEntry("cisco_ios")
        elif answer == "x":
            addEntry("cisco_nxos")
        else:
            answer = "n"

#
#  MAIN PROGRAM FLOW
#


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="retrieve configuration files", action="store_true" )
parser.add_argument("-m", "--mac", help="retrieve MAC tables", action="store_true")
parser.add_argument("-a", "--arp", help="retrieve ARP tables", action="store_true")
parser.add_argument("-v", "--verify", help="verify hosts are accessible", action="store_true")
args = parser.parse_args()

if not args.verify and not args.mac and not args.arp and not args.config:
    parser.print_help()
    sys.exc_info()[0]
readYAML()
if args.verify:
    sshVerifyInventory("cisco_ios")
if args.config:
    sshShowRun("cisco_ios")
if args.arp:
    sshGetArp("cisco_ios")
if args.mac:
    sshGetMac("cisco_ios")
