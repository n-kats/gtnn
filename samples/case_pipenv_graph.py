from argparse import ArgumentParser
import json
from types import SimpleNamespace

from gtnn_vis.export_networkx import to_networkx, preview


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("input", help="result of `pipenv graph --json`")
    parser.add_argument("--output", help="path to output result image")
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.input) as f_in:
        data = json.load(f_in)

    graph = parse_graph(data)
    preview(to_networkx(graph), path=args.output)


def parse_graph(data):
    packs = [item["package"] for item in data]
    nodes = [p["key"] for p in packs]
    edges = [
        SimpleNamespace(
            source=dep["key"],
            target=item["package"]["key"],
        ) for item in data for dep in item["dependencies"]
    ]

    return SimpleNamespace(nodes=nodes, edges=edges)


if __name__ == '__main__':
    main()
