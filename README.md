# autosave

Automatically save configuration files, mac tables and arp tables of several routers and/or switched based on an inventory file

## Installation

git clone https://github.com/ucipass/autosave

## Usage

Verify connectivity and SSH credentials to hosts defined in inventory file:

    python3 autosave.py -c

Save confugration file:

    python3 autosave.py -c

Save ARP table:

    python3 autosave.py -a

Save MAC table:

    python3 autosave.py -m

To get help, just run

    python3 autosave.py --help

## Use cases

### Inventory files

The inventory files is created automatically if there is none in the same directory where the python file is located.
The inventory files is in YAML format. See example file below:
    - Files
        - 1
        - 2
