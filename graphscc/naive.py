"""朴素参考实现：对每个节点分别做正、反向可达性，取交集。

O(V(V+E))，只用于小图上与 Tarjan 结果逐组比对，不作为正式算法。
"""


def components(edges):
    vertices = set()
    forward = {}
    reverse = {}
    for source, target in edges:
        vertices.add(source)
        vertices.add(target)
        forward.setdefault(source, set()).add(target)
        reverse.setdefault(target, set()).add(source)
    for vertex in vertices:
        forward.setdefault(vertex, set())
        reverse.setdefault(vertex, set())

    def reachable(graph, start):
        seen = {start}
        pending = [start]
        while pending:
            node = pending.pop()
            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    pending.append(neighbor)
        return seen

    assigned = set()
    groups = []
    for vertex in vertices:
        if vertex in assigned:
            continue
        same = reachable(forward, vertex) & reachable(reverse, vertex)
        assigned |= same
        groups.append(sorted(same))
    groups.sort(key=lambda group: group[0])
    return groups
