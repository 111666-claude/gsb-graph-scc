"""朴素参考实现：对每个节点分别做正向、反向可达性，取交集得到强连通分量。

时间 O(V*(V+E))，仅用于与 Kosaraju 结果逐组比对，不用于规模场景。
只用标准库。
"""

from collections import deque

from graphscc.scc import parse_edges


def _build_adjacency(edges):
    adjacency = {}
    reverse = {}
    for source, target in edges:
        adjacency.setdefault(source, []).append(target)
        reverse.setdefault(target, []).append(source)
        adjacency.setdefault(target, [])
        reverse.setdefault(source, [])
    return adjacency, reverse


def _reachable(start, adjacency):
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in adjacency.get(node, ()):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen


def naive_components(edges):
    """正向可达 ∩ 反向可达 = 与该节点互相可达的节点集合。"""
    adjacency, reverse = _build_adjacency(edges)
    groups = []
    claimed = set()
    for node in adjacency:
        if node in claimed:
            continue
        group = _reachable(node, adjacency) & _reachable(node, reverse)
        claimed.update(group)
        groups.append(sorted(group))
    groups.sort(key=lambda group: group[0])
    return groups


def naive_components_from_lines(lines):
    return naive_components(parse_edges(lines))
