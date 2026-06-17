"""dep_graph/graph.py — DependencyGraph: JSON/SVG/HTML出力"""
from __future__ import annotations
import json
from command_index.db import CommandIndexDB
from command_index.registry import CommandRegistry

_CAT_COLORS = {
    "seo":          "#4a9eff",
    "publish":      "#3dba6c",
    "distribution": "#9b72f0",
    "caliber":      "#f0a500",
    "governance":   "#e54b4b",
    "context":      "#2ab9a8",
}


class DependencyGraph:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()
        self._registry = CommandRegistry(self._db)

    def to_json(self) -> str:
        rows = self._db.execute("SELECT from_id, to_id, dep_type FROM dependencies")
        nodes_ids = set()
        edges = []
        for r in rows:
            nodes_ids.add(r["from_id"])
            nodes_ids.add(r["to_id"])
            edges.append({"from": r["from_id"], "to": r["to_id"], "type": r["dep_type"]})
        nodes = []
        for nid in sorted(nodes_ids):
            cmd = self._registry.get(nid)
            nodes.append({
                "id": nid,
                "label": nid,
                "category": cmd.category if cmd else "unknown",
                "description": cmd.description if cmd else "",
            })
        return json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2)

    def to_svg(self, width: int = 900, height: int = 600) -> str:
        data = json.loads(self.to_json())
        nodes = data["nodes"]
        edges = data["edges"]
        if not nodes:
            return f'<svg width="{width}" height="80"><text x="20" y="30" fill="#888">No dependencies</text></svg>'

        # レイアウト: カテゴリ別に列配置
        cat_order = ["seo", "publish", "distribution", "caliber", "governance", "context"]
        cols: dict[str, list] = {c: [] for c in cat_order}
        for n in nodes:
            cat = n.get("category", "unknown")
            cols.setdefault(cat, []).append(n)

        pos: dict[str, tuple[int, int]] = {}
        col_x = 20
        for cat in cat_order:
            ns = cols.get(cat, [])
            for i, n in enumerate(ns):
                pos[n["id"]] = (col_x, 60 + i * 50)
            if ns:
                col_x += 160

        lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="#4a9eff"/></marker></defs>',
            '<rect width="100%" height="100%" fill="#070d14"/>',
        ]
        id_to_node = {n["id"]: n for n in nodes}
        for e in edges:
            x1, y1 = pos.get(e["from"], (0, 0))
            x2, y2 = pos.get(e["to"], (0, 0))
            lines.append(
                f'<line x1="{x1+120}" y1="{y1+10}" x2="{x2}" y2="{y2+10}" '
                f'stroke="#4a9eff" stroke-width="1.5" opacity="0.6" marker-end="url(#arrow)"/>'
            )
        for nid, (x, y) in pos.items():
            n = id_to_node.get(nid, {})
            cat = n.get("category", "unknown")
            color = _CAT_COLORS.get(cat, "#666")
            lines.append(
                f'<rect x="{x}" y="{y}" width="130" height="24" rx="4" '
                f'fill="{color}22" stroke="{color}" stroke-width="1"/>'
            )
            lines.append(
                f'<text x="{x+4}" y="{y+16}" fill="{color}" '
                f'font-size="10" font-family="monospace">{nid}</text>'
            )
        lines.append("</svg>")
        return "\n".join(lines)

    def to_html(self) -> str:
        svg = self.to_svg()
        graph_json = self.to_json()
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>SEO Command Index — Dependency Graph</title>
<style>
body{{background:#070d14;color:#cdd9e5;font-family:monospace;padding:20px}}
h1{{color:#4a9eff;font-size:16px;margin-bottom:12px}}
.graph-svg{{border:1px solid #1e2f45;border-radius:8px;margin-bottom:16px}}
pre{{background:#0d1520;border:1px solid #1e2f45;border-radius:6px;padding:12px;
     font-size:11px;overflow:auto;max-height:300px}}
</style>
</head>
<body>
<h1>SEO Command Index — Dependency Graph</h1>
<div class="graph-svg">{svg}</div>
<h2 style="font-size:13px;color:#6b8099;margin-bottom:8px">Graph JSON</h2>
<pre>{graph_json}</pre>
</body>
</html>"""
