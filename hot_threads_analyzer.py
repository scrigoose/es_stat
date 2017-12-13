import argparse
import re

NODE_MARKER = ":::"
CPU_MARKER = "cpu usage by thread"

class Node:
    def __init__(self, name, uid, tag):
        self.name = name
        self.uid = uid
        self.tag = tag
        self.threads_cpu = {}

    def add_cpu_usage(self, thread, cpu):
        if thread not in list(self.threads_cpu.keys()):
            self.threads_cpu[thread] = []
        self.threads_cpu[thread].append(cpu)

class HTStat:
    def __init__(self, filepath=""):
        self.nodes = {}
        self.curr_node = None
        if filepath:
            self.load(filepath)

    def load(self, filepath):
        with open(filepath, 'r') as htf:
            for line in htf.readlines():
                self._process_line(line)

    def _process_line(self, line):
        if NODE_MARKER in line:
            self._parse_node(line)
            return
        if CPU_MARKER in line:
            self._parse_cpu_usage(line)
            return

    def _parse_node(self, line):
        matched = re.match('::: {(.*)}{(.*)}{.*}{.*}{.*}{tag=(.*)}', line)
        if matched:
            name, uid, tag = matched.group(1), matched.group(2), matched.group(3)
            if uid not in self.nodes.keys():
                self.nodes[uid] = Node(name, uid, tag)
            self.curr_node = self.nodes[uid]

    def _parse_cpu_usage(self, line):
        matched = re.match("\s+(.*)%.*'(.*)#.*'", line)
        if matched:
            thread, cpu = matched.group(2), float(matched.group(1))
            self.curr_node.add_cpu_usage(thread, cpu)


def main(filepath):
    hts = HTStat(filepath)
    [print(k) for k in sorted(hts.nodes['KZWzfuT0TbKGJ2C8H0FxoQ'].threads_cpu.keys())]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", type=str, help="File path with hot threads logs")
    args = parser.parse_args()
    main(args.filepath)
