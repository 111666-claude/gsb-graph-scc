"""命令行入口：打印强连通分量。"""

import argparse
import json
import sys

from .scc import components, parse_edges


def build_parser():
    parser = argparse.ArgumentParser(prog="graph-scc", description="强连通分量")
    parser.add_argument("--edges", required=True, help="边表：源 目标")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        with open(args.edges, encoding="utf-8") as handle:
            edges = parse_edges(handle.readlines())
    except (OSError, ValueError) as error:
        print("错误：%s" % error, file=sys.stderr)
        return 2
    groups = components(edges)
    print(json.dumps(groups, ensure_ascii=False))
    print("components=%d nodes=%d" % (len(groups), sum(len(group) for group in groups)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
