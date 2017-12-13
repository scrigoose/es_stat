#! /usr/bin/python3

import re
import json
import sys
import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class Node:
    def __init__(self, node_name, node_type):
        self.name = node_name
        self.type = node_type
        self.objs = {}
        self.data_frame = None
        self.keys = set()

    def add_json(self, dt, jsonobj):
        self.objs[dt] = jsonobj

    def create_data_frame(self):
        vals = list(self.objs.values())
        self.data_frame = pd.io.json.json_normalize(vals)
        ind = pd.DatetimeIndex(list(self.objs.keys()))
        self.data_frame.set_index(ind, inplace=True)
        return self.data_frame

    def get_keys(self):
        for obj in self.objs.values():
            self._retrieve_keys_from_obj(obj)
            break
        return self.keys

    def get_plot_data(self, field, scale=1):
        if (not field in self.get_keys()):
            print("No such field: {}".format(field))
            raise ValueError
        values = []
        times = []
        for dt, obj in self.objs.items():
            field_val = self._get_field_from_json(obj, field.split('.'))
            if (field_val):
                times.append(dt)
                values.append(field_val * scale)
        return times, values

    def _retrieve_keys_from_obj(self, jsonobj, prefix=[]):
        if isinstance(jsonobj, dict):
            for k, v in jsonobj.items():
                new_prefix = prefix[:]
                new_prefix.append(k)
                self._retrieve_keys_from_obj(v, new_prefix)
        else:
            self.keys.add('.'.join(prefix))

    def _get_field_from_json(self, jsonobj, fieldpath):
        return jsonobj if not fieldpath else self._get_field_from_json(jsonobj[fieldpath[0]], fieldpath[1:])


class Stats():
    def __init__(self, filepath = ""):
        self.nodes = {}
        if filepath:
            self.load(filepath)

    def load(self, filepath):
        with open(filepath, "r") as f:
            for line in f.readlines():
                if "----" in line:
                    continue
                dt, jsonobj = self._process_line(line)
                if jsonobj:
                    self._store_obj(dt, jsonobj)

    def get_nodes_types(self):
        ret = {}
        for k, v in self.nodes.items():
            ret[k] = v.type
        return ret

    def _process_line(self, line):
        jsonobj = None
        dt = None
        matched = re.match('(\d+-\d+-\d+\s\d+:\d+:\d+)(.*)', line)
        if matched:
            try:
                jsonobj = json.loads(matched.group(2))
                dt = datetime.strptime(matched.group(1), "%Y-%m-%d %H:%M:%S")
            except:
                return None, None
        return dt, jsonobj

    def _store_obj(self, dt, jsonobj):
        if "nodes" in jsonobj:
            for k,v in jsonobj["nodes"].items():
                if "attributes" in v and "tag" in v["attributes"]:
                    n = self._add_node(k, v["attributes"]["tag"])
                    n.add_json(dt, v)

    def _add_node(self, name, tag):
        if not name in self.nodes.keys():
            self.nodes[name] = Node(name, tag)
        return self.nodes[name]


def show_nodes(filepath):
    s = Stats(filepath)
    for name, tag in s.get_nodes_types().items():
        print("{0} - {1}".format(name, tag))
    return s.get_nodes_types().items()


def show_fields(filepath):
    s = Stats(filepath)
    keys = set()
    for _, node in s.nodes.items():
        keys = node.get_keys()
        break
    [print(k) for k in sorted(keys)]
    return keys


def process_line(line):
    jsonobj = None
    dt = None
    matched = re.match('(\d+-\d+-\d+\s\d+:\d+:\d+)(.*)', line)
    if matched:
        jsonobj = json.loads(matched.group(2))
        dt = datetime.strptime(matched.group(1), "%Y-%m-%d %H:%M:%S")
    return dt, jsonobj


def add_plot(x_vals, y_vals, label, scale):
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(x_vals, y_vals)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    ax.xaxis.set_minor_locator(mdates.HourLocator())
    ax.grid(True)
    fig.autofmt_xdate()
    plt.title(label)
    plt.xlabel("date")
    plt.ylabel('x{}'.format(scale))


def main(filepath, field, scale, node_name):
    s = Stats(filepath)
    if node_name == 'all':
        for name, node in s.nodes.items():
            times, values = node.get_plot_data(field, scale)
            add_plot(times, values, ' - '.join([name, field]), scale)
    else:
        if node_name in s.nodes:
            times, values = s.nodes[node_name].get_plot_data(field, scale)
            add_plot(times, values, field, scale)
        else:
            print("No such node: {}".format(node_name))
            raise ValueError
    plt.show()

def print_header(text, tab='-'):
    print(80 * tab)
    print(text)
    print(80 * tab)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="Filename with logs")
    parser.add_argument("-f", "--field", type=str, help="Field name to analyze")
    parser.add_argument("-n", "--node", type=str, help="Selected node", default="all")
    parser.add_argument("-s", "--scale", type=int, help="Factor by which values are scaled", default=1)
    args = parser.parse_args()
    if args.field:
        try:
            main(args.filename, args.field, args.scale, args.node)
        except:
            exit(1)
    else:
        print_header("Possible keys in {0}".format(args.filename))
        show_fields(args.filename)
        print_header("Data available for nodes:")
        show_nodes(args.filename)
