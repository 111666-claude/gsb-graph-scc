# graph-scc

有向图的强连通分量（迭代版 Tarjan），只用 Python 标准库。

```
python3 -m graphscc.cli --edges sample/graph.txt
python3 -m graphscc.cli --edges sample/graph.txt --counters
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **强连通 = 互相可达**：`a -> b` 单向不算同一个分量。`sample/graph.txt` 里
  `a<->b`、`c<->d`、`e<->f`，加上一条单向边 `b -> c`，输出
  `[["a","b"],["c","d"],["e","f"]]`；不能把单向边当无向边合并成
  `[["a","b","c","d"],["e","f"]]`。
- 分量内部按字典序排序，分量之间按「最小成员」排序，输出稳定，与边的插入顺序无关。
- 自环算一个大小为 1 的分量；任何出现在边表里的端点（哪怕没有任何关联边）
  都单独成组，不漏节点。
- 不变量：每条边的两端要么在同一分量、要么分属两个分量且只有一个方向可达；
  与「对每个节点做正反向两次可达性、取交集」的朴素参考实现
  （`graphscc/naive.py`）结果逐组一致。
- 规模：10 万节点、100 万边在 O(V+E) 时间、O(V+E) 内存内完成；
  迭代式 DFS，不受递归深度限制；不对每个节点各做一次可达性搜索。

## 实现

- `components(edges, counters=None)`：迭代版 Tarjan，一次 DFS 求出全部分量。
  传入 `counters` 字典时回填 `nodes`、`edges`、`dfs_visits`、`edge_scans`。
- `--counters` 额外打印一行，例如 `dfs_visits=6 edges_scanned=7`。
- 边表每行必须是两个空白分隔的字段；`#` 开头与空行跳过，字段数不对时报错
  并指出 1 起始的物理行号；空输入返回空列表 `[]`。

## 输出

```
[["a", "b"], ["c", "d"], ["e", "f"]]
components=3 nodes=6
```

## 目录

```
graphscc/scc.py    边表解析与 Tarjan 分量计算
graphscc/naive.py  朴素参考实现（正反两次可达取交集，仅供对照）
graphscc/cli.py    命令行入口（--edges、--counters）
tests/             unittest 用例（含 1000 张随机图逐组比对）
sample/graph.txt   三条双向边 + 一条单向边
```
