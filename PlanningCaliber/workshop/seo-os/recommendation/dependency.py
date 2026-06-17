"""recommendation/dependency.py — DependencyRecommendation: コマンド間依存グラフ"""
from __future__ import annotations
from command_index.db import CommandIndexDB
from command_index.registry import CommandRegistry
from command_index.metadata import CommandMetadata


class DependencyRecommendation:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()
        self._registry = CommandRegistry(self._db)

    def get_dependencies(self, command_id: str) -> list[CommandMetadata]:
        rows = self._db.execute(
            "SELECT to_id FROM dependencies WHERE from_id=?", (command_id,)
        )
        result = []
        for r in rows:
            cmd = self._registry.get(r["to_id"])
            if cmd:
                result.append(cmd)
        return result

    def get_dependents(self, command_id: str) -> list[CommandMetadata]:
        rows = self._db.execute(
            "SELECT from_id FROM dependencies WHERE to_id=?", (command_id,)
        )
        result = []
        for r in rows:
            cmd = self._registry.get(r["from_id"])
            if cmd:
                result.append(cmd)
        return result

    def dependency_chain(self, command_id: str,
                         visited: set | None = None) -> list[str]:
        """コマンドが必要とする依存をすべてチェーン展開する"""
        if visited is None:
            visited = set()
        if command_id in visited:
            return []
        visited.add(command_id)
        chain = []
        for dep in self.get_dependencies(command_id):
            sub = self.dependency_chain(dep.id, visited)
            chain.extend(sub)
            chain.append(dep.id)
        return chain

    def to_graph(self) -> dict:
        """全依存関係をグラフ形式で返す"""
        rows = self._db.execute("SELECT from_id, to_id, dep_type FROM dependencies")
        nodes = set()
        edges = []
        for r in rows:
            nodes.add(r["from_id"])
            nodes.add(r["to_id"])
            edges.append({"from": r["from_id"], "to": r["to_id"],
                          "type": r["dep_type"]})
        return {"nodes": list(nodes), "edges": edges}

    def to_svg(self) -> str:
        graph = self.to_graph()
        nodes = graph["nodes"]
        edges = graph["edges"]
        if not nodes:
            return "<svg><text>No dependencies</text></svg>"

        w, h = 800, 60 + len(nodes) * 40
        lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">',
                 '<style>text{font-size:11px;font-family:monospace}</style>']
        pos = {n: (100, 40 + i * 40) for i, n in enumerate(sorted(nodes))}
        for e in edges:
            x1, y1 = pos.get(e["from"], (0, 0))
            x2, y2 = pos.get(e["to"], (0, 0))
            lines.append(f'<line x1="{x1+200}" y1="{y1}" x2="{x2+200}" y2="{y2}" '
                         f'stroke="#4a9eff" stroke-width="1" marker-end="url(#arrow)"/>')
        for n, (x, y) in pos.items():
            lines.append(f'<rect x="{x}" y="{y-12}" width="190" height="20" '
                         f'rx="4" fill="#0d1520" stroke="#1e2f45"/>')
            lines.append(f'<text x="{x+4}" y="{y+4}" fill="#cdd9e5">{n}</text>')
        lines.append("</svg>")
        return "\n".join(lines)
