"""
graph_loader.py -- TIC Dependency Graph Loader (Phase3)

dependency_graph.jsonl（append-only構造グラフ）を読み込み、
コンポーネント間の依存・影響関係を参照するための最小限のAPIを提供する。

判断・予測・学習は一切行わない。グラフの読み取りのみ。
"""

import json
from pathlib import Path

GRAPH_PATH = Path("C:/Users/sirok/MoCKA/data/tic/dependency_graph.jsonl")


def load_edges() -> list:
    if not GRAPH_PATH.exists():
        return []
    edges = []
    with open(GRAPH_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                edges.append(json.loads(line))
            except Exception:
                continue
    return edges


def get_impacts(component: str, edges: list = None) -> list:
    """component が影響を与える先（type=impacts, from=component）のリスト"""
    edges = edges if edges is not None else load_edges()
    return [e["to"] for e in edges if e["from"] == component and e["type"] == "impacts"]


def get_dependencies(component: str, edges: list = None) -> list:
    """component が依存する先（type=depends_on, from=component）のリスト"""
    edges = edges if edges is not None else load_edges()
    return [e["to"] for e in edges if e["from"] == component and e["type"] == "depends_on"]


def get_affected_by(component: str, edges: list = None) -> list:
    """component に影響を受けるもの（type=impacts, to=component の from 側）のリスト"""
    edges = edges if edges is not None else load_edges()
    return [e["from"] for e in edges if e["to"] == component and e["type"] == "impacts"]
