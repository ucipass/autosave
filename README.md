# autosave

Automatically save configuration files, mac tables and arp tables of several routers and/or switched based on an inventory file

## Installation

Clone the github repository:

    git clone https://github.com/ucipass/autosave

## Usage

All files are created in the autosave directory.

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
