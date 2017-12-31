#!/usr/bin/env python3
import argparse
import json
from copy import deepcopy

def main(input_file, output_file, plz_range=range(40210,40721)):
    geodata = read_jsonfile(input_file)
    output = {"type": "FeatureCollection", "crs": None, "features": []}
    for f in range(len(geodata["features"])):
        try:
            for p in plz_range:
                if geodata["features"][f]["properties"]["plz"] == str(p):
                    output["features"].append(deepcopy(geodata["features"][f]))
                    break
        except:
            pass
    write_jsonfile(output_file, output)
 
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
        with open(file, "w") as data_file:
            data_file.write(json.dumps(content, ensure_ascii=False))
            data_file.close()
    except:
        print("Couldn't write json file")
        raise

def parse_args():
    parser = argparse.ArgumentParser(
        description="filter geoip file for range of zip codes (Postleitzahl)")
    parser.add_argument("--input_file", type=str, required=True,
                        help="json file to read from")
    parser.add_argument("--output_file", type=str, required=True,
                        help="json file to write into")
    parser.add_argument("--plz_range", nargs="+", required=False,
                        help="list of zip codes to filter (space seperated)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(input_file=args.input_file, output_file=args.output_file, plz_range=args.plz_range )
