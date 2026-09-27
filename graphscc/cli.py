"""命令行入口：打印强连通分量。"""

import argparse
import json
import sys

from .scc import kosaraju, parse_edges


def build_parser():
    parser = argparse.ArgumentParser(prog="graph-scc", description="强连通分量")
    parser.add_argument("--edges", required=True, help="边表：每行「源 目标」")
    parser.add_argument(
        "--counters",
        action="store_true",
        help="额外打印 DFS 访问次数等计数",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        with open(args.edges, encoding="utf-8") as handle:
            edges = parse_edges(handle.readlines())
    except (OSError, ValueError) as error:
        print("错误：%s" % error, file=sys.stderr)
        return 2
    groups, counters = kosaraju(edges)
    print(json.dumps(groups, ensure_ascii=False))
    print("components=%d nodes=%d" % (len(groups), sum(len(group) for group in groups)))
    if args.counters:
        print(
            "dfs_visits=%(dfs_visits)d edge_scans=%(edge_scans)d passes=%(passes)d"
            % counters
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
