# Autosave

Automatically save configuration files, mac tables and arp tables of several routers and/or switched based on an inventory file

## Installation

Make sure python 3 is installed on your system.
Clone the github repository:

    git clone https://github.com/ucipass/autosave

## Inventory file

The inventory file contains hostnames/ip addresses and ssh credentials in order to retreive data.
The inventory file is in YAML format and will be created automatically if there is not one in the autosave directory.
The file can be edited with a text editor to edit/add/delete sections.


See example inventory.yml file below:

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

All files are created in the autosave directory.

Verify connectivity and credentials to hosts defined in inventory file:

    python3 autosave.py -c

Save confugration file:

    python3 autosave.py -c

Save ARP table:

    python3 autosave.py -a

Save MAC table:

    python3 autosave.py -m

To get help, just run

    python3 autosave.py --help

