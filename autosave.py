from netmiko import Netmiko
from getpass import getpass
import textfsm
import re
import yaml
import sys
import csv
import time
import os
import argparse
import io

dir_root = os.path.dirname(os.path.realpath(__file__))
dir_fsm = os.path.join(dir_root, 'templates')
inventoryFile = "inventory.yml"
inventory = { "cisco_ios" : [], 'cisco_nxos' : []}

cisco_ios_show_mac_address_table = """Value DESTINATION_ADDRESS (\w+.\w+.\w+)
Value TYPE (\w+)
Value VLAN (\w+)
Value DESTINATION_PORT (\S+)

Start
  ^Destination\s+Address\s+Address\s+Type\s+VLAN\s+Destination\s+Port -> TYPE1
  ^\s+vlan\s+mac address\s+type\s+learn\s+age\s+ports -> TYPE2
  ^\s+vlan\s+mac address\s+type\s+protocols\s+port -> TYPE3
  ^Vlan\s+Mac Address\s+Type\s+Ports -> TYPE4

TYPE1
  ^${DESTINATION_ADDRESS}\s+${TYPE}\s+${VLAN}\s+${DESTINATION_PORT} -> Record

TYPE2
  ^[\*|\s]\s+${VLAN}\s+${DESTINATION_ADDRESS}\s+${TYPE}\s+\S+\s+\S+\s+${DESTINATION_PORT} -> Record

TYPE3
  ^\s+${VLAN}\s+${DESTINATION_ADDRESS}\s+${TYPE}\s+\S+\s+${DESTINATION_PORT} -> Record

TYPE4
  ^\s+${VLAN}\s+${DESTINATION_ADDRESS}\s+${TYPE}\s+${DESTINATION_PORT} -> Record
"""
cisco_ios_show_ip_arp = """Value Required ADDRESS (\d+\.\d+\.\d+\.\d+)
Value Required AGE ([-\d+]+)
Value Required MAC (\S+)
Value Required TYPE (\S+)
Value INTERFACE (\S+)

Start
  ^Internet\s+${ADDRESS}\s+${AGE}\s+${MAC}\s+${TYPE}\s+${INTERFACE} -> Record
  ^Internet\s+${ADDRESS}\s+${AGE}\s+${MAC}\s+${TYPE} -> Record
"""
cisco_nxos_show_mac_address_table = """Value VLAN (\S+)
Value MAC (\S+)
Value TYPE (\S+)
Value AGE (\S+)
Value SECURE ([TF])
Value NTFY ([TF])
Value PORTS (\S+)

Start
  ^VLAN\s+MAC\s+Address\s+Type\s+age\s+Secure\s+NTFY\s+Ports -> Continue
  ^.*\s${VLAN}\s+${MAC}\s+${TYPE}\s+${AGE}\s+${SECURE}\s+${NTFY}\s+${PORTS} -> Record
"""
cisco_nxos_show_ip_arp = """Value Required ADDRESS (\d+\.\d+\.\d+\.\d+)
Value Required AGE (\S+)
Value Required MAC (\S+)
Value INTERFACE (\S+)

Start
  ^Address\s+Age\s+MAC Address\s+Interface -> Start_record

Start_record
  ^${ADDRESS}\s+${AGE}\s+${MAC}\s+${INTERFACE} -> Record
  ^\s+$$
  ^$$
  ^.* -> Error "LINE NOT FOUND"
"""
fsm = {
    'cisco_ios': {
        'arp': cisco_ios_show_ip_arp,
        'mac': cisco_ios_show_mac_address_table
    },
    'cisco_nxos': {
        'arp': cisco_nxos_show_ip_arp,
        'mac': cisco_nxos_show_mac_address_table
    }
}

def sshVerify(host, username, password, device_type):
    try:
        net_connect = Netmiko(host=host, username=username, password=password, device_type=device_type, timeout=5)
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
    table_all = []
    dir = os.path.dirname(os.path.realpath(__file__))
    dir = os.path.join(dir, 'arp')
    if not os.path.exists(dir):
        os.makedirs(dir)
    #fsm_file = os.path.join(dir_fsm, device_type+"_show_ip_arp.template")
    #re_table = textfsm.TextFSM(open(fsm_file, 'r'))

    for device in inventory[device_type]:
        table = []
        host = device['host']
        username = device['username']
        password = device['password']
        try:
            print("Retrieving ARP table for:", host)
            net_connect = Netmiko(host=host, username=username, password=password, device_type=device_type, timeout=10)
            hostname = net_connect.find_prompt()
            hostname = re.sub('#','', hostname)
            net_connect.send_command("term len 0", use_textfsm=False)
            cmd_output = net_connect.send_command("show ip arp", use_textfsm=False)
            re_table = textfsm.TextFSM(io.StringIO(fsm[device_type]['arp']))
            cmd_output = re_table.ParseText(cmd_output)

            if not "ailed" in cmd_output:
                print(" Success!: ", cmd_output[0], "more...")
                for arpEntry in cmd_output:
                    table.append(arpEntry)
                table = sorted(table, key=None, reverse=False)
                filename = os.path.join(dir, hostname + "_arp_" + time.strftime("%Y%m%d-%H%M%S") + ".csv")
                writeCSV(re_table.header, table, filename)
            else:
                print(" Failed!:\n", cmd_output)
        except Exception as e:
            print(e)
        table_all = table_all + table
    filename = os.path.join(dir, "all_arp_" + time.strftime("%Y%m%d-%H%M%S") + ".csv")
    table_all = sorted(table_all, key=None, reverse=False)
    writeCSV(re_table.header, table_all, filename)


def sshGetMac(device_type):
    global inventory
    table_all = []
    dir = os.path.dirname(os.path.realpath(__file__))
    dir = os.path.join(dir, 'mac')
    if not os.path.exists(dir):
        os.makedirs(dir)
    #fsm_file = os.path.join(dir_fsm, device_type+"_show_ip_arp.template")
    #re_table = textfsm.TextFSM(open(fsm_file, 'r'))

    for device in inventory[device_type]:
        table = []
        host = device['host']
        username = device['username']
        password = device['password']
        try:
            print("Retrieving MAC table for:", host)
            net_connect = Netmiko(host=host, username=username, password=password, device_type=device_type, timeout=10)
            hostname = net_connect.find_prompt()
            hostname = re.sub('#','', hostname)
            net_connect.send_command("term len 0", use_textfsm=False)
            cmd_output = net_connect.send_command("show mac address-table", use_textfsm=False)
            re_table = textfsm.TextFSM(io.StringIO(fsm[device_type]['mac']))
            cmd_output = re_table.ParseText(cmd_output)

            if not "ailed" in cmd_output:
                print(" Success!: ", cmd_output[0], "more...")
                for arpEntry in cmd_output:
                    table.append(arpEntry)
                table = sorted(table, key=None, reverse=False)
                filename = os.path.join(dir, hostname + "_mac_" + time.strftime("%Y%m%d-%H%M%S") + ".csv")
                writeCSV(re_table.header, table, filename)
            else:
                print(" Failed!:\n", cmd_output)
        except Exception as e:
            print(e)
        table_all = table_all + table
    filename = os.path.join(dir, "all_mac_" + time.strftime("%Y%m%d-%H%M%S") + ".csv")
    table_all = sorted(table_all, key=None, reverse=False)
    writeCSV(re_table.header, table_all, filename)

def sshShowRun(device_type):
    global inventory
    global mac
    dir = os.path.dirname(os.path.realpath(__file__))
    dir = os.path.join(dir, 'config')
    if not os.path.exists(dir):
        os.makedirs(dir)
    try:
        iterator = iter(inventory[device_type])
    except Exception as e:
        return False #no good yaml content found
    for device in inventory[device_type]:
        host=device['host']
        username=device['username']
        password=device['password']
        try:
            print("Saving configration file for:", host)
            net_connect = Netmiko(host=host, username=username, password=password, device_type=device_type, timeout=10)
            hostname = net_connect.find_prompt()
            hostname = re.sub('#','', hostname)
            cmd_output = net_connect.send_command("term len 0", use_textfsm=False)
            cmd_output = net_connect.send_command("show run", use_textfsm=False)
            timestr = time.strftime("%Y%m%d-%H%M%S")
            filename = os.path.join(dir, hostname + "_CONFIG_" + timestr + ".txt")
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
    sshVerifyInventory("cisco_nxos")
if args.config:
    sshShowRun("cisco_ios")
    sshShowRun("cisco_nxos")
if args.arp:
    sshGetArp("cisco_ios")
    sshGetArp("cisco_nxos")
if args.mac:
    sshGetMac("cisco_ios")
    sshGetMac("cisco_nxos")
