#!/usr/bin/env python3
#This program works with the GeoJSON format using EPSG:4326 - wgs84 projection. 
#For best results use a high precision map.
import argparse
import json
from geojson_utils import point_in_polygon
from geojson_utils import point_in_multipolygon
from copy import deepcopy

def main(geojson_file, nodesjson_file, sitesjson_file, overridesjson_file, output_file):
    geodata = read_jsonfile(geojson_file)
    nodedata = read_jsonfile(nodesjson_file)
    sitesdata = read_jsonfile(sitesjson_file)
    overridesdata = {}
    try:
        overridesdata = read_jsonfile(overridesjson_file)
    except:
        pass
    nodes = []
    for n in range(len(nodedata["nodes"])):
        node = {}
        for o in range(len(overridesdata["overrides"])):
            if overridesdata["overrides"][o]["node_id"] == nodedata["nodes"][n]["nodeinfo"]["node_id"]:
                node = {"node_id": deepcopy(nodedata["nodes"][n]["nodeinfo"]["node_id"]), "domain": deepcopy(overridesdata["overrides"][o]["domain"])}
                break
        if not node:
            try:
                point={"type": "Point", "coordinates": [nodedata["nodes"][n]["nodeinfo"]["location"]["longitude"], nodedata["nodes"][n]["nodeinfo"]["location"]["latitude"]]}
            except KeyError:
                pass
            else:
                for f in range(len(geodata["features"])):
                    if check_location(point, geodata["features"][f]):
                        for s in range(len(sitesdata["sites"])):
                            for d in range(len(sitesdata["sites"][s]["domains"])):
                                for z in range(len(sitesdata["sites"][s]["domains"][d]["zipcodes"])):
                                    if deepcopy(geodata["features"][f]["properties"]["plz"]) == deepcopy(sitesdata["sites"][s]["domains"][d]["zipcodes"][z]):
                                        node = {"node_id": deepcopy(nodedata["nodes"][n]["nodeinfo"]["node_id"]), "domain": deepcopy(sitesdata["sites"][s]["domains"][d]["domain"])}
                                        nodes.append(deepcopy(node))
                                        break
        if not node:
            for s in range(len(sitesdata["sites"])):
                try:
                    if deepcopy(sitesdata["sites"][s]["site_code"]) == deepcopy(nodedata["nodes"][n]["nodeinfo"]["system"]["site_code"]):
                        node = {"node_id": deepcopy(nodedata["nodes"][n]["nodeinfo"]["node_id"]), "domain": deepcopy(sitesdata["sites"][s]["default_domain"])}
                        nodes.append(deepcopy(node))
                except Exception as e:
                    print("Ignoring Node: {0}\n{1}".format(nodedata["nodes"][n]["nodeinfo"]["node_id"], e))
                    pass
    if nodes:
        output = {"version": "1", "nodes": nodes, "timestamp": deepcopy(nodedata["timestamp"])}
        write_jsonfile(output_file, output)
    else:
        print("No nodes found")

def check_location(point, geojson):
    result = False
    if geojson["geometry"]["type"] == "Polygon":
        result = point_in_polygon(point, geojson["geometry"])
    elif geojson["geometry"]["type"] == "MultiPolygon":
        result = point_in_multipolygon(point, geojson["geometry"])
    return result

def read_jsonfile(file):
    jsondata = {}
    try:
        with open(file) as data_file:
            jsondata = json.load(data_file)
            data_file.close()
    except:
        print("Couldn't read json file {0}".format(file))
        raise
    return jsondata

def write_jsonfile(file, content):
    try:
        with open(file, 'w') as data_file:
            data_file.write(json.dumps(content, indent=4, separators=(',', ': '), ensure_ascii=False))
            data_file.close()
    except:
        print("Couldn't write json file")
        raise

def parse_args():
    parser = argparse.ArgumentParser(
        description="create zip code / plz node list")
    parser.add_argument("--geojson_file", type=str, required=True,
                        help="geo json file to read from")
    parser.add_argument("--nodesjson_file", type=str, required=True,
                        help="nodes json file to read from")
    parser.add_argument("--sitesjson_file", type=str, required=True,
                        help="sites json file to read from")
    parser.add_argument("--overridesjson_file", type=str, required=False,
                        help="sites json file to read from")
    parser.add_argument("--output_file", type=str, required=True,
                        help="config / json file to write into")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(geojson_file=args.geojson_file, nodesjson_file=args.nodesjson_file, sitesjson_file=args.sitesjson_file, overridesjson_file=args.overridesjson_file, output_file=args.output_file)
