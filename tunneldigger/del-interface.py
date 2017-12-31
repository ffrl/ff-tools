#!/usr/bin/env python3
import argparse
from pyroute2 import IPDB

def main(tunnel_id, session_id, interface, tunnel_mtu, endpoint0, endpoint1, address, uuid):
    print("Removing interface {0} of node ID {1}".format(interface, uuid))
    del_from_bridge(interface)

def del_from_bridge(interface):
    try:
        ipdb = IPDB()
        with ipdb.interfaces[interface].ro as brport:
            ipdb.interfaces[brport.master].del_port(brport.index)
            ipdb.interfaces[brport.master].commit()
    except:
        raise

def parse_args():
    parser = argparse.ArgumentParser(description="tunneldigger broker hook for pre-down")
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
