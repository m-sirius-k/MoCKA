# -*- coding: utf-8 -*-
"""Dependency Graph Builder (Phase 5 Cross-Layer Consistency Engine)

役割:
  - layer間依存構造グラフ生成 (data flow graph)
  - circular dependency検出

MoCKAの既知データフロー (architecture review / MOCKA_OVERVIEW 準拠):
    semantic -> decision -> memory -> self_audit -> feedback -> learning
    reality  -> report   (Phase 4-2 -> Phase 4-3, 一方向)
    report   -> self_audit (governance audit はreport governanceを参照)
    learning -> memory (Learning StateはMemory Coherenceに影響, drift監視対象)

このグラフは固定定義(コードから自動抽出ではない)。Phase5の目的は
「定義された依存構造に対して矛盾を検出すること」であり、依存構造自体の
自動推論はスコープ外。
"""

from dataclasses import dataclass, field

# edge: (from_layer, to_layer)
DEPENDENCY_EDGES = [
    ("semantic", "decision"),
    ("decision", "memory"),
    ("memory", "self_audit"),
    ("self_audit", "feedback"),
    ("feedback", "learning"),
    ("reality", "report"),
    ("report", "self_audit"),
    ("learning", "memory"),   # フィードバックループ(意図的)
]

ALL_LAYERS = [
    "semantic", "decision", "memory", "self_audit",
    "feedback", "learning", "reality", "report",
]


@dataclass
class DependencyGraph:
    nodes: list = field(default_factory=lambda: list(ALL_LAYERS))
    edges: list = field(default_factory=lambda: list(DEPENDENCY_EDGES))
    cycles: list = field(default_factory=list)


def _find_cycles(nodes, edges):
    """DFSベースで単純な閉路を検出する。"""
    adj = {n: [] for n in nodes}
    for src, dst in edges:
        adj.setdefault(src, []).append(dst)

    cycles = []
    visiting = set()
    visited = set()
    path = []

    def dfs(node):
        visiting.add(node)
        path.append(node)
        for nxt in adj.get(node, []):
            if nxt in visiting:
                cycle_start = path.index(nxt)
                cycles.append(path[cycle_start:] + [nxt])
            elif nxt not in visited:
                dfs(nxt)
        path.pop()
        visiting.discard(node)
        visited.add(node)

    for n in nodes:
        if n not in visited:
            dfs(n)

    return cycles


def build() -> DependencyGraph:
    cycles = _find_cycles(ALL_LAYERS, DEPENDENCY_EDGES)
    return DependencyGraph(nodes=list(ALL_LAYERS), edges=list(DEPENDENCY_EDGES), cycles=cycles)


if __name__ == "__main__":
    g = build()
    print("nodes:", g.nodes)
    print("edges:", g.edges)
    print("cycles:", g.cycles)
