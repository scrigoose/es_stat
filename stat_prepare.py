import json
import re
import argparse


def prepare_file(fpath):
    with open(fpath) as f_in:
        with open(fpath + "_ref", 'w') as f_out:
            for line in f_in.readlines():
                if "------" in line:
                    continue
                matched = re.match('(\d+-\d+-\d+\s\d+:\d+:\d+)(.*)', line)
                if matched:
                    f_out.write(matched.group(1))
                    f_out.write('\n')
                    f_out.write(matched.group(2))
                    f_out.write('\n')
                else:
                    f_out.write(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fname", type=str, help="Filename with logs to prepare")
    args = parser.parse_args()
    prepare_file(args.fname)