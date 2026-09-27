import io
import os
import random
import tempfile
import unittest
from contextlib import redirect_stdout

from graphscc.cli import main
from graphscc.scc import components, kosaraju, parse_edges
from tests.reference import naive_components


SAMPLE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sample",
    "graph.txt",
)


def canonical(groups):
    return sorted(tuple(group) for group in groups)


class ParseTest(unittest.TestCase):
    def test_parse_skips_comments_and_blank_lines(self):
        self.assertEqual(parse_edges(["# x", "a b", "", "  "]), [("a", "b")])

    def test_parse_rejects_bad_line_with_line_number(self):
        with self.assertRaises(ValueError) as caught:
            parse_edges(["a b", "x", "c d"])
        self.assertIn("第 2 行", str(caught.exception))

    def test_parse_three_fields_reports_line_number(self):
        with self.assertRaises(ValueError) as caught:
            parse_edges(["# comment", "a b", "a b c"])
        self.assertIn("第 3 行", str(caught.exception))

    def test_empty_input(self):
        self.assertEqual(parse_edges([]), [])
        self.assertEqual(components([]), [])


class ComponentsTest(unittest.TestCase):
    def test_two_node_cycle(self):
        self.assertEqual(components([("a", "b"), ("b", "a")]), [["a", "b"]])

    def test_single_direction_does_not_merge(self):
        self.assertEqual(components([("a", "b")]), [["a"], ["b"]])

    def test_sample_graph(self):
        with open(SAMPLE_PATH, encoding="utf-8") as handle:
            edges = parse_edges(handle.readlines())
        # 需求口径：sample/graph.txt 必须是这个结果；
        # 样例文件里 e/f 是双向边，b->c 仍是单向桥，不能并入。
        self.assertEqual(
            components(edges),
            [["a", "b"], ["c", "d"], ["e", "f"]],
        )

    def test_one_way_edge_between_pairs_does_not_merge(self):
        # 同样的三条双向边之间放一条单向桥：桥两端必须各自留在自己的分量。
        groups = components(
            parse_edges(
                [
                    "a b",
                    "b a",
                    "b c",
                    "c d",
                    "d c",
                    "e f",
                ]
            )
        )
        self.assertEqual(groups, [["a", "b"], ["c", "d"], ["e"], ["f"]])

    def test_sorted_group_members(self):
        self.assertEqual(components([("b", "a"), ("a", "b")]), [["a", "b"]])

    def test_groups_sorted_by_minimum_member(self):
        edges = [("z", "y"), ("y", "z"), ("m", "n"), ("n", "m"), ("a", "a")]
        self.assertEqual(
            components(edges),
            [["a"], ["m", "n"], ["y", "z"]],
        )

    def test_insertion_order_does_not_change_output(self):
        edges = [("z", "y"), ("y", "z"), ("m", "n"), ("n", "m")]
        first = components(edges)
        self.assertEqual(components(list(reversed(edges))), first)

    def test_self_loop_is_own_component(self):
        self.assertEqual(components([("s", "s")]), [["s"]])

    def test_self_loop_does_not_absorb_one_way_neighbor(self):
        self.assertEqual(
            components([("s", "s"), ("s", "t")]),
            [["s"], ["t"]],
        )

    def test_endpoint_without_mutual_edge_is_grouped(self):
        # x 只有出边、z 只有入边：必须各自单独成组，不能漏掉。
        self.assertEqual(
            components([("x", "y"), ("y", "z")]),
            [["x"], ["y"], ["z"]],
        )

    def test_two_isolated_pairs(self):
        groups = components(
            [("a", "b"), ("b", "a"), ("c", "d"), ("d", "c")]
        )
        self.assertEqual(groups, [["a", "b"], ["c", "d"]])

    def test_duplicate_edges(self):
        self.assertEqual(
            components([("a", "b"), ("a", "b"), ("b", "a")]),
            [["a", "b"]],
        )

    def test_diamond_without_cycle(self):
        edges = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
        self.assertEqual(
            components(edges),
            [["a"], ["b"], ["c"], ["d"]],
        )

    def test_counters(self):
        edges = [("a", "b"), ("b", "a"), ("b", "c"), ("c", "d"), ("d", "c")]
        groups, counters = kosaraju(edges)
        self.assertEqual(groups, [["a", "b"], ["c", "d"]])
        self.assertEqual(counters["dfs_visits"], 2 * 4)
        self.assertEqual(counters["edge_scans"], 2 * len(edges))
        self.assertEqual(counters["passes"], 2)


class InvariantTest(unittest.TestCase):
    def test_no_edge_runs_both_ways_between_components(self):
        edges = parse_edges(
            [
                "a b",
                "b a",
                "b c",
                "c d",
                "d c",
                "e f",
                "f e",
                "d g",
            ]
        )
        groups, _ = kosaraju(edges)
        membership = {
            node: index for index, group in enumerate(groups) for node in group
        }
        forward = set(edges)
        for source, target in edges:
            if membership[source] != membership[target]:
                # 缩点后必须是 DAG：反向边不能同时存在。
                self.assertNotIn((target, source), forward)


class ReferenceComparisonTest(unittest.TestCase):
    def test_manual_cases_match_reference(self):
        cases = [
            [],
            [("a", "b")],
            [("a", "a")],
            [("a", "b"), ("b", "a"), ("b", "c"), ("c", "d"), ("d", "c")],
            [("x", "y"), ("y", "z"), ("z", "x"), ("x", "w")],
        ]
        for edges in cases:
            self.assertEqual(
                canonical(components(edges)),
                canonical(naive_components(edges)),
                msg=edges,
            )

    def test_matches_reference_on_1000_random_graphs(self):
        rng = random.Random(20260927)
        for trial in range(1000):
            order = rng.randint(0, 9)
            nodes = ["n%02d" % index for index in range(order)]
            edges = []
            for _ in range(rng.randint(0, 3 * max(order, 1))):
                source = nodes[rng.randrange(order)] if order else "n00"
                target = nodes[rng.randrange(order)] if order else "n00"
                edges.append((source, target))
            expected = naive_components(edges)
            actual = components(edges)
            self.assertEqual(canonical(actual), canonical(expected), msg=trial)
            self.assertEqual(actual, expected, msg=trial)


class CliTest(unittest.TestCase):
    def _run(self, content, *extra_args):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
            tmp.write(content)
            path = tmp.name
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                status = main(["--edges", path, *extra_args])
            return status, output.getvalue()
        finally:
            os.unlink(path)

    def test_sample_output_format(self):
        status, output = self._run(
            "a b\nb a\nb c\nc d\nd c\ne f\n"
        )
        self.assertEqual(status, 0)
        lines = output.splitlines()
        self.assertEqual(
            lines[0],
            '[["a", "b"], ["c", "d"], ["e"], ["f"]]',
        )
        self.assertEqual(lines[1], "components=4 nodes=6")

    def test_counters_line(self):
        status, output = self._run("a b\nb a\n", "--counters")
        self.assertEqual(status, 0)
        lines = output.splitlines()
        self.assertEqual(lines[0], '[["a", "b"]]')
        self.assertIn("dfs_visits=4", lines[2])

    def test_empty_file_prints_empty_list(self):
        status, output = self._run("# only a comment\n\n")
        self.assertEqual(status, 0)
        self.assertEqual(output.splitlines()[0], "[]")
        self.assertEqual(output.splitlines()[1], "components=0 nodes=0")

    def test_bad_line_reports_line_number(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
            tmp.write("a b\nonly-one-field\n")
            path = tmp.name
        try:
            import contextlib

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                status = main(["--edges", path])
            self.assertEqual(status, 2)
            self.assertIn("第 2 行", stderr.getvalue())
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
