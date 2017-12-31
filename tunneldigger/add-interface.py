#!/usr/bin/env python3
import argparse
import json
import os
from pyroute2 import IPDB
from copy import deepcopy

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
CONFIG=os.path.join(__location__, "nodes.json")
BRIDGE_PREFIX="td"
DEFAULT_BRIDGE="tunneldigger"
MTU=1364

def main(tunnel_id, session_id, interface, tunnel_mtu, endpoint0, endpoint1, address, uuid):
    nodedata = read_jsonfile(CONFIG)
    for n in range(len(nodedata["nodes"])):
        if nodedata["nodes"][n]["nodeinfo"]["node_id"] == uuid:
            node = deepcopy(nodedata["nodes"][n])
            break
    try:
        bridge = BRIDGE_PREFIX + node["nodeinfo"]["location"]["plz"][:-1]
        print("NodeID {0} ({1}) has zip code {2}, adding interface {3} to bridge {4}".format(node["nodeinfo"]["node_id"], node["nodeinfo"]["hostname"], node["nodeinfo"]["location"]["plz"], interface, bridge))
    except:
        bridge = DEFAULT_BRIDGE
        print("NodeID {0} not found or has no zip code set, adding interface {1} to default bridge {2}".format(uuid, interface, bridge))
    set_mtu(interface)
    add_to_bridge(interface, bridge)

def set_mtu(interface):
    ipdb = IPDB()
    try:
        with ipdb.interfaces[interface] as iface:
            iface.set_mtu(MTU)
            iface.up()
    except:
        raise

def add_to_bridge(interface, bridge=DEFAULT_BRIDGE):
    ipdb = IPDB()
    try:
        with ipdb.interfaces[bridge] as br:
            br.add_port(interface)
    except KeyError:
        if bridge != DEFAULT_BRIDGE:
            print("Couldn't add interface to bridge, trying default bridge")
            try:
                with ipdb.interfaces[DEFAULT_BRIDGE] as br:
                    br.add_port(interface)
            except:
                raise
        else:
            raise
    except:
        raise
    print("Interface added")

def read_jsonfile(file):
    jsondata = {}
    try:
        with open(file) as data_file:
            jsondata = json.load(data_file)
            data_file.close()
    except:
        print("Couldn't read json file")
        raise
    return jsondata

def parse_args():
    parser = argparse.ArgumentParser(description="tunneldigger broker hook for session.up")
    parser.add_argument("tunnel_id", type=str)
    parser.add_argument("session_id", type=str)
    parser.add_argument("interface", type=str)
    parser.add_argument("tunnel_mtu", type=str)
    parser.add_argument("endpoint0", type=str)
    parser.add_argument("endpoint1", type=str)
    parser.add_argument("address", type=str)
    parser.add_argument("uuid", type=str)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(
         tunnel_id=args.tunnel_id,
         session_id=args.session_id,
         interface=args.interface,
         tunnel_mtu=args.tunnel_mtu,
         endpoint0=args.endpoint0,
         endpoint1=args.endpoint1,
         address=args.address,
         uuid=args.uuid
    )
