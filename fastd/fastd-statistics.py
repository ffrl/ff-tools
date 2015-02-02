#!/usr/bin/env python2
import socket
import sys
import os
import json
import datetime
import argparse

def recv_data(the_socket):
    total_data=[]
    while True:
        data = the_socket.recv(8192)
        if not data: break
        total_data.append(data)
    return ''.join(total_data)

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--socket', help='Fastd socket file', required=True)
args = vars(parser.parse_args())

print >>sys.stderr, 'Connecting to %s' % args['socket']

client = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
try:
    client.connect(args['socket'])
    message = recv_data(client)
    try:
        fastd_data = json.loads(message.decode('utf-8'))
        print "=============Fastd Statistics============="
        print "Fastd Uptime:", str(datetime.timedelta(milliseconds=int(fastd_data["uptime"])))
        print "Connected Clients:", len(fastd_data["peers"])
        print "RX packets:", fastd_data["statistics"]["rx"]["packets"]
        print "RX bytes:", fastd_data["statistics"]["rx"]["bytes"]
        print "RX reordered packets:", fastd_data["statistics"]["rx_reordered"]["packets"]
        print "RX reordered bytes:", fastd_data["statistics"]["rx_reordered"]["bytes"]
        print "TX packets:", fastd_data["statistics"]["tx"]["packets"]
        print "TX bytes:", fastd_data["statistics"]["tx"]["bytes"]
        print "TX dropped packets:", fastd_data["statistics"]["tx_dropped"]["packets"]
        print "TX dropped bytes:", fastd_data["statistics"]["tx_dropped"]["bytes"]
        print "TX error packets:", fastd_data["statistics"]["tx_error"]["packets"]
        print "TX error bytes:", fastd_data["statistics"]["tx_error"]["bytes"]
    except (ValueError, KeyError, TypeError):
        print "JSON format error"
except:
    pass
