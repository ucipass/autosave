# Autosave

Automatically save configuration files, mac tables and arp tables of several routers and/or switches based on an inventory file

## Installation

No installation is necessary as there is a single 64 bit windows executable in the dist directory.

    autosave.exe

Alternatively you can use python3 interpreter to run the program.
Make sure python3 is installed on your system, clone the github repository and install netmiko and textfsm:

    git clone https://github.com/ucipass/autosave
    pip3 install netmiko
    pip3 install textfsm
    python3.exe autosave.py

## Quick Start Example

    C:\autosave>autosave.exe
    You have no inventory file: inventory.yml!
    Would you like to create it? y/n (Default: no):
    y
    What would you like to add to inventory?
    (i)os/n(x)os/(n)othing (Default: (n)othing)
    i
    Enter hostname or IP address:
    10.255.254.1
    Enter username address:
    admin
    Enter password:
    Password:
    Verifying credentials....
    What would you like to add to inventory?
    (i)os/n(x)os/(n)othing (Default: (n)othing)
    n
    Press (c) to retreive configuration files!
    Press (a) to retreive ARP tables!
    Press (m) to retreive MAC tables!
    Press (v) to to verify inventory reachability!
    Press (e) to exite!
    c
    Saving configration file for: 10.255.254.1
      Saved Configuration files as: C:\autosave\config\VoiceLab-Switch_CONFIG_20181205-125301.txt
    
    C:\autosave>

## Inventory file

The inventory file contains hostnames/ip addresses and ssh credentials in order to retreive data.
The inventory file (default: inventory.yml) is in YAML format and will be created automatically if there is not one in the autosave directory.
The file can be edited with a text editor to edit/add/delete sections.


See sample inventory.yml file below:

    cisco_ios:
    - host: 172.18.100.221
      password: cisco
      username: admin
    - host: 172.18.100.222
      password: cisco
      username: admin
    cisco_nxos:
    - host: 172.18.100.223
      password: cisco
      username: admin
    - host: 172.18.100.224
      password: cisco
      username: admin

## Usage

All files are created in the same autosave directory.

    autosave.exe [-h] [-c] [-m] [-a] [-v] [-f [FILENAME]]
    
    optional arguments:
      -h, --help            show this help message and exit
      -c, --config          retrieve configuration files
      -m, --mac             retrieve MAC tables
      -a, --arp             retrieve ARP tables
      -v, --verify          verify hosts are accessible
      -f [FILENAME], --filename [FILENAME]
                            inventory file in YAML format

## Examples

Verify connectivity and credentials for hosts defined in the default inventory.yml file:

    python3 autosave.py -c

Save confugration files for hosts defined in the default inventory.yml file:

    python3 autosave.py -c

Save ARP tables for hosts defined in the default inventory.yml file:

    python3 autosave.py -a

Save MAC tablesfor hosts defined in the default inventory.yml file:

    python3 autosave.py -m

Save configuration files, MAC Tables, ARP tables for hosts defined in an alternative inventory2.yml file:

    python3 autosave.py -c -a -m -f inventory2.yml

To get help, just run

    python3 autosave.py --help

## Results

Files are saved in subdirectories (config,mac,arp)
There is a consolidated _ALL_ files with sorted mac and arp entries from all files.
