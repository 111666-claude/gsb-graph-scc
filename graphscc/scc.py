"""强连通分量：迭代式 Kosaraju（两次 DFS）。只用标准库。

时间 O(V+E)，内存 O(V+E)。强连通 = 两节点互相可达，
单向边不会把两端并进同一个分量。
"""


def parse_edges(lines):
    """解析边表：每行两个字段「源 目标」；空行与 # 注释行跳过。

    非空非注释行字段数不为 2 时报错，错误信息带 1 起始的行号。
    """
    edges = []
    for lineno, line in enumerate(lines, 1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        fields = text.split()
        if len(fields) != 2:
            raise ValueError(
                "第 %d 行应该是两个字段（源 目标），实际有 %d 个字段：%r"
                % (lineno, len(fields), text)
            )
        edges.append((fields[0], fields[1]))
    return edges


def _build_adjacency(edges):
    """同时建正向/反向邻接表；所有边端点都作为键（含孤立端点）。"""
    adjacency = {}
    reverse = {}
    for source, target in edges:
        adjacency.setdefault(source, []).append(target)
        reverse.setdefault(target, []).append(source)
        adjacency.setdefault(target, [])
        reverse.setdefault(source, [])
    return adjacency, reverse


def kosaraju(edges):
    """返回 ``(groups, counters)``：强连通分量列表与 DFS 计数。

    groups：每个分量是按字典序排好的节点列表，分量之间按最小成员排序。
    counters：``dfs_visits``（DFS 访问节点的次数，两次 DFS 合计）、
    ``edge_scans``（扫描邻接边的次数）、``passes``（DFS 趟数，恒为 2）。
    """
    adjacency, reverse = _build_adjacency(edges)

    visited = set()
    order = []
    dfs_visits = 0
    edge_scans = 0

    # 第一次 DFS（正向图）：记录完成顺序。显式栈 + 邻接下标，避免递归深度限制。
    for start in adjacency:
        if start in visited:
            continue
        visited.add(start)
        dfs_visits += 1
        stack = [start]
        positions = [0]
        while stack:
            node = stack[-1]
            neighbors = adjacency[node]
            index = positions[-1]
            if index < len(neighbors):
                neighbor = neighbors[index]
                positions[-1] = index + 1
                edge_scans += 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    dfs_visits += 1
                    stack.append(neighbor)
                    positions.append(0)
            else:
                stack.pop()
                positions.pop()
                order.append(node)

    # 第二次 DFS（反向图）：按完成顺序逆序弹出，每次 DFS 得到一个分量。
    assigned = {}
    groups = []
    component_id = 0
    for start in reversed(order):
        if start in assigned:
            continue
        assigned[start] = component_id
        dfs_visits += 1
        stack = [start]
        group = [start]
        while stack:
            node = stack.pop()
            for neighbor in reverse[node]:
                edge_scans += 1
                if neighbor not in assigned:
                    assigned[neighbor] = component_id
                    dfs_visits += 1
                    stack.append(neighbor)
                    group.append(neighbor)
        groups.append(group)
        component_id += 1

    groups = [sorted(group) for group in groups]
    groups.sort(key=lambda group: group[0])
    counters = {
        "dfs_visits": dfs_visits,
        "edge_scans": edge_scans,
        "passes": 2,
    }
    return groups, counters


def components(edges):
    """把节点分成强连通分量；单向边不会合并两端。"""
    return kosaraju(edges)[0]
