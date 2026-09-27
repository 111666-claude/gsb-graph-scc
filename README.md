# graph-scc

有向图的强连通分量（迭代式 Kosaraju，两次 DFS），只用 Python 标准库。

```
python3 -m graphscc.cli --edges sample/graph.txt
python3 -m graphscc.cli --edges sample/graph.txt --counters
python3 -m unittest discover -s tests -v
```

## 口径

- **强连通 = 互相可达**：`a -> b` 单向不算同一个分量。`sample/graph.txt`
  包含三条双向边 `a<->b`、`c<->d`、`e<->f` 和一条单向桥 `b->c`，输出
  `[["a","b"],["c","d"],["e","f"]]`；单向桥不会把两端并入同一分量。
- 分量内部按字典序排序，分量之间按「最小成员」排序，输出与边表插入顺序无关。
- 自环算一个大小为 1 的分量；所有在边表里出现的端点（包括只有单方向边的端点）
  都属于某个分量；空输入返回 `[]`。
- 不变量：每条边的两端要么在同一分量，要么分属两个分量且缩点后只有一个方向
  可达（缩点图是 DAG）；结果与「对每个节点做正反向两次可达性、取交集」的
  朴素参考实现（`tests/reference.py`）逐组一致。
- 规模：迭代式 Kosaraju，O(V+E) 时间、O(V+E) 内存，无递归深度限制；
  实测 10 万节点、100 万边约 2 秒跑完。

## 输入校验

边表每行两个空白分隔的字段「源 目标」；空行与 `#` 注释行跳过。
字段数不为 2 的行直接报错，错误信息带 1 起始的行号，CLI 退出码为 2。

## 输出

不带新参数时格式不变：

```
[["a", "b"], ["c", "d"], ["e", "f"]]
components=3 nodes=6
```

加 `--counters` 额外打印一行 DFS 计数：

```
dfs_visits=12 edge_scans=12 passes=2
```

- `dfs_visits`：两次 DFS 中节点首次被访问的总次数（每个分量/节点每次 DFS 一次，
  总计 2V）。
- `edge_scans`：两次 DFS 扫描邻接边的总次数（总计 2E）。

## 目录

```
graphscc/scc.py   边表解析与迭代式 Kosaraju 分量计算
graphscc/cli.py   命令行入口（--edges、--counters）
tests/test_scc.py unittest 用例（含 1000 张随机图与朴素实现逐组比对）
tests/reference.py 朴素参考实现：每节点正反两次可达性取交集，O(V(V+E))
sample/graph.txt  三条双向边 + 一条单向桥
```
