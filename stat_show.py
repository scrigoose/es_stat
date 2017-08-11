#! /usr/bin/python3

import re
import json
import sys
import matplotlib.pyplot as plt
from datetime import datetime


def get_field_from_json(jsonobj, fieldpath):
    return jsonobj if not fieldpath else get_field_from_json(jsonobj[fieldpath[0]], fieldpath[1:])

def print_keys(jsonobj, prefix = []):
    if isinstance(jsonobj, dict):
        for k, v in jsonobj.items():
            new_prefix = prefix[:]
            new_prefix.append(k)
            print_keys(v, new_prefix)
    else:
        print('.'.join(prefix))


def process_line(line):
    jsonobj = None
    dt = None
    matched = re.match('(\d+-\d+-\d+\s\d+:\d+:\d+)(.*)', line)
    if matched:
        jsonobj = json.loads(matched.group(2))
        dt = datetime.strptime(matched.group(1), "%Y-%m-%d %H:%M:%S")
    return dt, jsonobj


def show_keys_in_file(filepath):
    with open(filepath, "r") as f:
        line = f.readline()
        _, jsonobj = process_line(line)
        if jsonobj:
            print_keys(jsonobj)
            


def main(filepath, field, scale):
    times = []
    values = []
    with open(filepath, "r") as f:
        for line in f.readlines():
            dt, jsonobj = process_line(line)
            times.append(dt)
            field_val = get_field_from_json(jsonobj, field.split('.'))
            values.append(field_val * scale)

    fig = plt.figure(1)
    plt.plot(times, values)
    fig.autofmt_xdate()
    plt.show()


if __name__ == "__main__":
    filename = ""
    field = ""
    scale = 1
    if len(sys.argv) < 2:
        print("Usage: {0} <filepath> [<filed>] [<scale>]".format(sys.argv[0]))
        sys.exit(1)
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        print("Possible keys in {0}".format(filename))
        show_keys_in_file(filename)
        print("Usage: {0} <filepath> [<filed>] [<scale>]".format(sys.argv[0]))
        sys.exit(0)
    if len(sys.argv) > 2:
        filename = sys.argv[1]
        field = sys.argv[2]
    if len(sys.argv) > 3:
        scale = float(sys.argv[3])
    main(filename, field, scale)