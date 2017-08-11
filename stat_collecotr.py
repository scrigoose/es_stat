#! /bin/python3

import json
import subprocess
import os
import time


CERT_PATH = ""
KEY_PATH = ""
HOST_IP = "10.0.5.1"
CMD = "curl --insecure --cert {0} --key {1} https://{2}:9200/_nodes/stats/{3}"


def get_stat(endpoint):
    cmd = CMD.format(CERT_PATH, KEY_PATH, HOST_IP, endpoint)
    args = cmd.split()
    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    obj = json.loads(stdout.decode("utf-8"))
    return obj


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def store_in_file(fpath, data):
    with open(fpath, 'a') as outfile:
        st = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        outfile.write("{0}  {1}".format(st, data))
        outfile.write("\n")


def process_node_entry(k, v, endpoint):
    if "tag" in v["attributes"]:
        if v["attributes"]["tag"] == "data":
            create_dir(k)
            store_in_file("{0}/{1}".format(k, endpoint), json.dumps(v[endpoint]))


def collect_stat(endpoint):
    process_stat = get_stat(endpoint)
    for k, v in process_stat["nodes"].items():
        process_node_entry(k, v, endpoint)


if __name__ == "__main__":
    endpoints = ["process", "jvm", "os", "indices", "transport", "fs", "http"]
    while True:
        for ep in endpoints:
            collect_stat(ep)
        time.sleep(300)
