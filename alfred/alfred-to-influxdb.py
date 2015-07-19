#!/usr/bin/env python3
import argparse

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from lib.alfred import Alfred
import datetime
import random
import time
import getpass
import json

USER = 'root'
PASSWORD = 'root'
DBNAME = 'freifunk'
INTERVAL = 1

def main(file, host='localhost', port=8086, socket='/var/run/alfred.sock'):
    jsondata = {}
    if file:
        jsondata=read_jsonfile(file)
    else:
        jsondata=Alfred(unix_sockpath=socket)
    series=create_series(jsondata)
    
    client = InfluxDBClient(host, port, USER, PASSWORD, DBNAME)
    
    print("Create database: " + DBNAME)
    try:
        client.create_database(DBNAME)
    except InfluxDBClientError:
        print("Database already existing, skipping creation")
        pass
    
    print("Create a retention policy")
    try:
        retention_policy = 'freifunk_policy'
        client.create_retention_policy(retention_policy, '7d', 1, default=True)
    except InfluxDBClientError:
        print("Retention policy existing, skipping creation")
        pass
    
    client.write_points(series, retention_policy=retention_policy)
    print("Data written to influxdb!")

def read_jsonfile(file):
    jsondata = {}
    try:
        with open(file) as data_file:    
            jsondata = json.load(data_file)
    except:
        print("Couldn't read json file: ")
    return jsondata

def create_series(jsondata):
    series=[]
    now = datetime.datetime.today()
    for node in jsondata:
        data={}
        keys={'loadavg','uptime','memory','rootfs_usage','clients','traffic','processes','hostname','nodeid'}
        #Use node object / mac address as default tag
        mac = node
        
        #Read all keys
        for key in keys:
            try:
                data[key] = jsondata[node][key]
            except KeyError:
                pass
        
        #Create series for idletime, loadavg, rootfs_usage and uptime
        for metric in ['idletime','loadavg','rootfs_usage','uptime']:
            try:
                pointValues = {}
                pointValues['fields'] = {}
                pointValues['tags'] = {}
                pointValues['time'] = int(now.strftime('%s'))
                pointValues['measurement'] = metric
                pointValues['fields']['value'] = float(data[metric])
                pointValues['tags']['mac'] = mac
                #Append additional tags if existing
                try:
                    pointValues['tags']['hostname'] = data['hostname']
                except:
                    pass
                try:
                    pointValues['tags']['nodeid'] = data['nodeid']
                except:
                    pass
                series.append(pointValues)
            except KeyError:
                pass
        
        #Create series for memory,clients,processes
        for metric in ['memory','clients','processes']:
            try:
                for type in data[metric]:
                    pointValues = {}
                    pointValues['fields'] = {}
                    pointValues['tags'] = {}
                    pointValues['time'] = int(now.strftime('%s'))
                    pointValues['measurement'] = metric
                    pointValues['fields']['value'] = int(data[metric][type])
                    pointValues['fields']['type'] = type
                    pointValues['tags']['mac'] = mac
                    #Append additional tags if existing
                    try:
                        pointValues['tags']['hostname'] = data['hostname']
                    except:
                        pass
                    try:
                        pointValues['tags']['nodeid'] = data['nodeid']
                    except:
                        pass
                    series.append(pointValues)
            except KeyError:
                pass
        
        #Create series for traffic
        try:
            for type_instance in data['traffic']:
                for type in type_instance:
                    pointValues = {}
                    pointValues['fields'] = {}
                    pointValues['tags'] = {}
                    pointValues['time'] = int(now.strftime('%s'))
                    pointValues['measurement'] = metric
                    pointValues['fields']['value'] = int(data[metric][type_instance][type])
                    pointValues['fields']['type'] = type
                    pointValues['fields']['type_instance'] = type_instance
                    pointValues['tags']['mac'] = mac
                    #Append additional tags if existing
                    try:
                        pointValues['tags']['hostname'] = data['hostname']
                    except:
                        pass
                    try:
                        pointValues['tags']['nodeid'] = data['nodeid']
                    except:
                        pass
                    series.append(pointValues)
        except KeyError:
            pass
    return series

def parse_args():
    parser = argparse.ArgumentParser(
        description='export alfred data to influxdb')
    parser.add_argument('--host', type=str, required=False, default='localhost',
                        help='hostname influxdb http API')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port influxdb http API')
    parser.add_argument('--file', type=str, required=False, default='',
                        help='read alfred data from file instead via alfred-json, this disables the use of alfred-json')
    parser.add_argument('--socket', type=str, required=False, default='/var/run/alfred.sock',
                        help='provide socket for alfred-json, optional')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port, file=args.file, socket=args.socket)
