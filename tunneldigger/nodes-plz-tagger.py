#!/usr/bin/env python3
#This program works with the GeoJSON format using EPSG:4326 - wgs84 projection. 
#For best results use a high precision map.
import argparse
import json
from geojson_utils import point_in_polygon
from geojson_utils import point_in_multipolygon
from copy import deepcopy

def main(geojson_file, nodesjson_file, output_file):
    geodata = read_jsonfile(geojson_file)
    nodedata = read_jsonfile(nodesjson_file)
    nodes = []
    for n in range(len(nodedata["nodes"])):
        try:
            point={"type": "Point", "coordinates": [nodedata["nodes"][n]["nodeinfo"]["location"]["longitude"], nodedata["nodes"][n]["nodeinfo"]["location"]["latitude"]]}
        except KeyError:
            nodes.append(deepcopy(nodedata["nodes"][n]))
        else:
            for f in range(len(geodata["features"])):
                if check_location(point, geodata["features"][f]):
                    node = deepcopy(nodedata["nodes"][n])
                    node["nodeinfo"]["location"]["plz"] = deepcopy(geodata["features"][f]["properties"]["plz"])
                    nodes.append(deepcopy(node))
                    break
    if nodes:
        output = {"version": "2", "nodes": nodes, "timestamp": deepcopy(nodedata["timestamp"])}
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
        print("Couldn't read json file")
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
    parser.add_argument("--output_file", type=str, required=True,
                        help="config / json file to write into")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(geojson_file=args.geojson_file, nodesjson_file=args.nodesjson_file, output_file=args.output_file)
