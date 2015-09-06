#!/usr/bin/env python3
import argparse
import json

def main(file):
    jsondata = {}
    jsondata=read_jsonfile(file)
    hits=jsondata["hits"]["hits"]
    for node in range(len(hits)):
        nodeaddr=""
        try:
            for ip6addr in hits[node]["_source"]["nodeinfo"]["network"]["addresses"]:
                if ip6addr.startswith('2a03'):
                    nodeaddr=ip6addr
                    break
            print(nodeaddr, end=" 1; #")
            print(hits[node]["_source"]["nodeinfo"]["hostname"])
        except:
            print("# Invalid node ignored! : ", end="")
            print(hits[node]["_id"])
    

def read_jsonfile(file):
    jsondata = {}
    try:
        with open(file) as data_file:    
            jsondata = json.load(data_file)
    except:
        print("Couldn't read json file: ")
    return jsondata

def parse_args():
    parser = argparse.ArgumentParser(
        description='create nginx geoip filter file from alfred elasticsearch data')
    parser.add_argument('--file', type=str, required=True, default='',
                        help='json file to read')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(file=args.file)