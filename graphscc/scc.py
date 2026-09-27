"""强连通分量：迭代版 Tarjan，只用标准库。

时间/内存均为 O(V+E)：每条有向边在 DFS 中只被扫描一次，每个节点只被
访问一次。强连通的口径是「互相可达」，单向边不会合并两端。
"""


def parse_edges(lines):
    """解析边表：每行两个空白分隔的字段，# 开头与空行跳过。

    字段数不对时抛 ValueError，错误信息带 1 起始的物理行号。
    """
    edges = []
    for lineno, line in enumerate(lines, start=1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        fields = text.split()
        if len(fields) != 2:
            raise ValueError(
                "第 %d 行必须是两个字段（源 目标），实际 %d 个：%r"
                % (lineno, len(fields), text)
            )
        edges.append((fields[0], fields[1]))
    return edges


def components(edges, counters=None):
    """返回强连通分量列表。

    每个分量内部按字典序排列，分量之间按各自最小成员排列。
    counters 给定时（dict）写入 nodes、edges、dfs_visits、edge_scans 计数。
    迭代式 Tarjan，避免大图上的递归深度问题。
    """
    index_of = {}
    adjacency = []
    edge_count = 0
    for source, target in edges:
        source_id = index_of.get(source)
        if source_id is None:
            source_id = len(index_of)
            index_of[source] = source_id
            adjacency.append([])
        target_id = index_of.get(target)
        if target_id is None:
            target_id = len(index_of)
            index_of[target] = target_id
            adjacency.append([])
        adjacency[source_id].append(target_id)
        edge_count += 1

    names = [None] * len(index_of)
    for name, node_id in index_of.items():
        names[node_id] = name

    node_count = len(index_of)
    index = [0] * node_count
    lowlink = [0] * node_count
    on_stack = [False] * node_count
    stack = []
    groups = []
    dfs_visits = 0
    edge_scans = 0

    for root in range(node_count):
        if index[root]:
            continue
        index[root] = 1
        lowlink[root] = 1
        dfs_visits += 1
        stack.append(root)
        on_stack[root] = True
        # 调用栈：(节点, 下一条待扫描邻接边的位置, 当前深度编号)
        next_index = 2
        work = [(root, 0)]
        while work:
            node, cursor = work[-1]
            neighbors = adjacency[node]
            if cursor < len(neighbors):
                target = neighbors[cursor]
                edge_scans += 1
                work[-1] = (node, cursor + 1)
                if not index[target]:
                    index[target] = next_index
                    lowlink[target] = next_index
                    next_index += 1
                    dfs_visits += 1
                    stack.append(target)
                    on_stack[target] = True
                    work.append((target, 0))
                elif on_stack[target] and index[target] < lowlink[node]:
                    lowlink[node] = index[target]
                continue
            work.pop()
            if lowlink[node] == index[node]:
                members = []
                while True:
                    member = stack.pop()
                    on_stack[member] = False
                    members.append(names[member])
                    if member == node:
                        break
                groups.append(sorted(members))
            if work:
                parent = work[-1][0]
                if lowlink[node] < lowlink[parent]:
                    lowlink[parent] = lowlink[node]

    groups.sort(key=lambda group: group[0])
    if counters is not None:
        counters["nodes"] = node_count
        counters["edges"] = edge_count
        counters["dfs_visits"] = dfs_visits
        counters["edge_scans"] = edge_scans
    return groups
