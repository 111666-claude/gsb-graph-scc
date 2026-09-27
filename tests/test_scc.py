import os
import random
import unittest

from graphscc.naive import components as naive_components
from graphscc.scc import components, parse_edges

SAMPLE = os.path.join(os.path.dirname(__file__), "..", "sample", "graph.txt")


class ParseTest(unittest.TestCase):
    def test_parse_skips_comments(self):
        self.assertEqual(parse_edges(["# x", "a b", ""]), [("a", "b")])

    def test_parse_rejects_bad_line(self):
        with self.assertRaises(ValueError) as raised:
            parse_edges(["a b", "a b c"])
        self.assertIn("第 2 行", str(raised.exception))

    def test_parse_rejects_single_field_with_lineno(self):
        with self.assertRaises(ValueError) as raised:
            parse_edges(["# comment", "", "lonely"])
        self.assertIn("第 3 行", str(raised.exception))

    def test_empty_input(self):
        self.assertEqual(parse_edges([]), [])
        self.assertEqual(components([]), [])


class ComponentsTest(unittest.TestCase):
    def test_two_node_cycle(self):
        self.assertEqual(components([("a", "b"), ("b", "a")]), [["a", "b"]])

    def test_single_direction_does_not_merge(self):
        groups = components([("a", "b")])
        self.assertEqual(groups, [["a"], ["b"]])

    def test_empty_graph(self):
        self.assertEqual(components([]), [])

    def test_sorted_group_members(self):
        groups = components([("b", "a"), ("a", "b")])
        self.assertEqual(groups, [["a", "b"]])

    def test_isolated_pair(self):
        groups = components([("a", "b"), ("b", "a"), ("c", "d"), ("d", "c")])
        self.assertEqual(groups, [["a", "b"], ["c", "d"]])

    def test_sample_output(self):
        with open(SAMPLE, encoding="utf-8") as handle:
            edges = parse_edges(handle.readlines())
        self.assertEqual(
            components(edges), [["a", "b"], ["c", "d"], ["e", "f"]]
        )

    def test_groups_sorted_by_minimum_member(self):
        # z->a->x 是一条链；y 自环；全部都是单节点分量。
        edges = [("z", "a"), ("a", "x"), ("y", "y")]
        self.assertEqual(components(edges), [["a"], ["x"], ["y"], ["z"]])

    def test_self_loop_is_its_own_component(self):
        groups = components([("x", "x"), ("y", "z"), ("z", "y")])
        self.assertEqual(groups, [["x"], ["y", "z"]])

    def test_every_endpoint_gets_a_group(self):
        # b 和 c 作为边的端点出现，但没有任何边把它们带回：仍要成组。
        groups = components([("a", "b"), ("c", "a")])
        self.assertEqual(groups, [["a"], ["b"], ["c"]])

    def test_duplicate_edges(self):
        groups = components([("a", "b"), ("a", "b"), ("b", "a")])
        self.assertEqual(groups, [["a", "b"]])

    def test_counters(self):
        counters = {}
        groups = components(
            [("a", "b"), ("b", "a"), ("a", "c"), ("d", "d")],
            counters=counters,
        )
        self.assertEqual(groups, [["a", "b"], ["c"], ["d"]])
        self.assertEqual(counters["nodes"], 4)
        self.assertEqual(counters["edges"], 4)
        self.assertEqual(counters["dfs_visits"], 4)
        self.assertEqual(counters["edge_scans"], 4)


class InvariantTest(unittest.TestCase):
    def _partition_of(self, groups):
        partition = {}
        for cid, group in enumerate(groups):
            for node in group:
                partition[node] = cid
        return partition

    def test_edges_go_within_or_one_way_between_components(self):
        edges = [
            ("a", "b"), ("b", "a"), ("b", "c"),
            ("c", "d"), ("d", "c"), ("e", "f"), ("f", "e"),
            ("a", "e"),
        ]
        groups = components(edges)
        partition = self._partition_of(groups)
        between = {}
        for source, target in edges:
            left, right = partition[source], partition[target]
            if left == right:
                continue
            key = (left, right)
            reverse = (right, left)
            self.assertNotIn(
                reverse, between,
                "分量 %r 与 %r 之间出现双向边，却未被合并" % (
                    groups[left], groups[right]
                ),
            )
            between[key] = True


class RandomComparisonTest(unittest.TestCase):
    def test_matches_naive_reference_on_random_graphs(self):
        rng = random.Random(20260927)
        names = [chr(code) for code in range(ord("a"), ord("h"))]
        for _ in range(1000):
            edge_count = rng.randrange(0, 15)
            edges = [
                (rng.choice(names), rng.choice(names)) for _ in range(edge_count)
            ]
            self.assertEqual(
                components(edges),
                naive_components(edges),
                msg="edges=%r" % edges,
            )

    def test_matches_naive_reference_on_larger_random_graph(self):
        rng = random.Random(4242)
        nodes = ["n%03d" % i for i in range(300)]
        edges = [
            (rng.choice(nodes), rng.choice(nodes)) for _ in range(1200)
        ]
        self.assertEqual(components(edges), naive_components(edges))


if __name__ == "__main__":
    unittest.main()
