# nodeinfo.py

This script collects MAC and IP adresses from the local batman-adv interface and it's slave interfaces and outputs a json structure ready to be injected into alfred and consumed by [ffmap-backend](https://github.com/ffnord/ffmap-backend). 

Using `nodeinfo.py`, it is not necessary to manually set static MAC addresses for mesh interfaces on a Freifunk supernode and provide a `aliases.json` for `ffmap-backend`. 

The output is compatible to [meshviewer](https://github.com/tcatm/meshviewer).

## Dependencies

`nodeinfo.py` needs python3 and the pyroute2 module.

## ToDo

Using a batman-adv interface that is added to a local bridge was not tested. 
