"""强连通分量：Tarjan 思路的实现。只用标准库。"""


def parse_edges(lines):
    edges = []
    for line in lines:
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        fields = text.split()
        if len(fields) != 2:
            raise ValueError("每行应该是 源 目标：%r" % text)
        edges.append((fields[0], fields[1]))
    return edges


def components(edges):
    """把节点分成强连通分量。

    缺陷：用并查集把「有边相连」的节点并在一起，等价于求无向连通分量，会吞掉单向可达的节点。
    """
    parent = {}

    def find(node):
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(left, right):
        root_left, root_right = find(left), find(right)
        if root_left != root_right:
            parent[root_left] = root_right

    for source, target in edges:
        union(source, target)
    groups = {}
    for node in parent:
        groups.setdefault(find(node), []).append(node)
    return [sorted(group) for group in groups.values()]
