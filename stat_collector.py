#! /bin/python3

import subprocess
import os
import time
import argparse


CMD = "curl --insecure --cert {0} --key {1} https://{2}:9200/_nodes/stats/{3}"


def get_stat(endpoint, ip, cert="", key=""):
    cert_part = ""
    if cert:
        cert_part = "--cert " + cert
    key_part = ""
    if key:
        key_part = "--key " + key
    cmd = CMD.format(cert_part, key_part, ip, endpoint)
    args = cmd.split()
    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode("utf-8")


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def store_in_file(fpath, data):
    with open(fpath, 'a') as outfile:
        st = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        outfile.write("{0}  {1}".format(st, data))
        outfile.write("\n")


def collect_stat(endpoint, ip, cert, key, output):
    process_stat = get_stat(endpoint, ip, cert, key)
    path = "/".join([output, endpoint.split('/')[-1]])
    store_in_file(path, process_stat)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", type=str, help="Elastic node ip")
    parser.add_argument("-c", "--cert", type=str, help="Path to elastic cert", default="")
    parser.add_argument("-k", "--key", type=str, help="Path to elastic key", default="")
    parser.add_argument("-o", "--out", type=str, help="Path to output folder", default="output")
    args = parser.parse_args()
    endpoints = ["stats/process", "stats/jvm", "stats/os", "stats/indices", "stats/transport", "stats/http", "stats/fs", "hot_threads"]
    create_dir(args.out)
    while True:
        for ep in endpoints:
            collect_stat(ep, args.ip, args.cert, args.key, args.out)
        time.sleep(300)
