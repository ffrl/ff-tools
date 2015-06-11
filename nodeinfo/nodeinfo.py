#!/usr/bin/env python3
# Author: Markus Lindenberg <markus@lindenberg.io>

import sys
import json
from socket import gethostname
import argparse
from pyroute2 import IPRoute

def main():
	parser = argparse.ArgumentParser(description='Collect node information for alfred.')
	parser.add_argument('--prefix', dest='prefix', default='', help='Add hostname prefix')
	parser.add_argument('--interface', dest='interface', default='bat0', help='Local mesh interface')
	args = parser.parse_args()

	ip = IPRoute()
	ifattrs = [(iface['index'], dict(iface['attrs'])) for iface in ip.get_links()]

	try:
		meshif = [(attrs[0], attrs[1]['IFLA_ADDRESS']) for attrs in ifattrs if attrs[1]['IFLA_IFNAME'] == args.interface][0]
	except IndexError:
		sys.exit('Mesh interface %s not found.' % args.interface)


	mesh_interfaces = {'wireless': [], 'tunnel': [], 'other': []}
	for index, attrs in ifattrs:
		linkinfo = dict(attrs['IFLA_LINKINFO']['attrs'])
		if not linkinfo.get('IFLA_INFO_SLAVE_KIND') == 'batadv':
			continue

		kind = linkinfo.get('IFLA_INFO_KIND')
		if kind == 'tun':
			mesh_interfaces['tunnel'].append(attrs['IFLA_ADDRESS'])
		elif kind == 'gretap':
			mesh_interfaces['other'].append(attrs['IFLA_ADDRESS'])
		elif kind == 'dummy':
			mesh_interfaces['tunnel'].append(attrs['IFLA_ADDRESS'])
		else:
			continue

	addresses = [dict(addr['attrs'])['IFA_ADDRESS'] for addr in ip.get_addr() if addr['index'] == meshif[0] and addr['family'] == 10]

	result = {
		'node_id': meshif[1].replace(':', ''),
		'network': {
			'mac': meshif[1],
			'addresses': addresses,
			'mesh': {
				'bat0': {
					'interfaces': mesh_interfaces
				}
			}
		},
		'hostname': '%s%s' % (args.prefix, gethostname()),
	}

	json.dump(result, sys.stdout, separators=(',', ':'))


if __name__ == '__main__':
	main()
