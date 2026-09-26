import unittest

from graphscc.scc import components, parse_edges


class ParseTest(unittest.TestCase):
    def test_parse_skips_comments(self):
        self.assertEqual(parse_edges(["# x", "a b", ""]), [("a", "b")])

    def test_parse_rejects_bad_line(self):
        with self.assertRaises(ValueError):
            parse_edges(["a b c"])


class ComponentsTest(unittest.TestCase):
    def test_two_node_cycle(self):
        self.assertEqual(components([("a", "b"), ("b", "a")]), [["a", "b"]])

    def test_single_direction_does_not_merge(self):
        groups = components([("a", "b")])
        nodes = sorted(node for group in groups for node in group)
        self.assertEqual(nodes, ["a", "b"])

    def test_empty_graph(self):
        self.assertEqual(components([]), [])

    def test_sorted_group_members(self):
        groups = components([("b", "a"), ("a", "b")])
        self.assertEqual(groups, [["a", "b"]])

    def test_isolated_pair(self):
        groups = components([("a", "b"), ("b", "a"), ("c", "d"), ("d", "c")])
        self.assertEqual(len(groups), 2)
