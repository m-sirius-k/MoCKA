"""mcp_server.py — PHI-OS SEO Command Index v3 MCP Server (Phase 11)

MCP Tools:
  command.search      — クエリでコマンド検索
  command.execute     — コマンド実行+学習記録
  command.context     — ContextRuntime状態取得
  command.graph       — 依存グラフ取得
  command.recommend   — コマンド推薦
"""
from __future__ import annotations
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify
from command_index import CommandRegistry, CategoryManager, CommandIndexDB
from semantic import MeaningSearch, SimilarityRanking
from context_bridge import ContextBridge
from recommendation import RecommendationEngine
from learning import LearningEngine
from dep_graph import DependencyGraph
from audit import AuditLogger
from runtime import UnifiedRuntime

app = Flask(__name__)
_db = CommandIndexDB()
_reg = CommandRegistry(_db)
_search = MeaningSearch(_db)
_ranking = SimilarityRanking(_db)
_ctx = ContextBridge()
_rec = RecommendationEngine(_db)
_learn = LearningEngine(_db)
_graph = DependencyGraph(_db)
_audit = AuditLogger(_db)
_runtime = UnifiedRuntime(_db)


def mcp_ok(data: dict) -> dict:
    return {"ok": True, "data": data}


def mcp_err(msg: str, code: int = 400):
    return jsonify({"ok": False, "error": msg}), code


# ── MCP Tool: command.search ──────────────────────────────────────────────────
@app.route("/mcp/command.search", methods=["POST"])
def mcp_search():
    body = request.json or {}
    q = body.get("query", "")
    if not q:
        return mcp_err("query required")
    category = body.get("category") or None
    limit = int(body.get("limit", 10))
    results = _ranking.rank(q, limit=limit, category=category)
    _audit.log("mcp.search", {"query": q, "count": len(results)})
    return jsonify(mcp_ok({
        "query": q,
        "results": [r.to_dict() for r in results],
        "count": len(results),
    }))


# ── MCP Tool: command.execute ─────────────────────────────────────────────────
@app.route("/mcp/command.execute", methods=["POST"])
def mcp_execute():
    body = request.json or {}
    command_id = body.get("command_id", "")
    if not command_id:
        return mcp_err("command_id required")
    cmd = _reg.get(command_id)
    if not cmd:
        return mcp_err(f"command not found: {command_id}", 404)
    gate = _runtime.execution_gate(cmd.category, command_id)
    if not gate.get("passed", True):
        _audit.log("mcp.execute.blocked", {"command_id": command_id, "gate": gate})
        return mcp_err(f"execution blocked by gate: {gate.get('status')}", 403)
    _learn.record(command_id, "success")
    _audit.log("mcp.execute", {"command_id": command_id})
    return jsonify(mcp_ok({
        "command": cmd.to_dict(),
        "gate": gate,
        "recommendations": [r.to_dict() for r in _rec.next_recommended(command_id)[:3]],
    }))


# ── MCP Tool: command.context ─────────────────────────────────────────────────
@app.route("/mcp/command.context", methods=["GET", "POST"])
def mcp_context():
    ctx = _ctx.get_memory_runtime()
    state = _runtime.state()
    return jsonify(mcp_ok({"memory_runtime": ctx, "runtime_state": state}))


# ── MCP Tool: command.graph ───────────────────────────────────────────────────
@app.route("/mcp/command.graph", methods=["POST"])
def mcp_graph():
    body = request.json or {}
    fmt = body.get("format", "json")
    _audit.log("mcp.graph", {"format": fmt})
    if fmt == "svg":
        return app.response_class(_graph.to_svg(), mimetype="image/svg+xml")
    if fmt == "html":
        return app.response_class(_graph.to_html(), mimetype="text/html")
    return jsonify(mcp_ok(json.loads(_graph.to_json())))


# ── MCP Tool: command.recommend ───────────────────────────────────────────────
@app.route("/mcp/command.recommend", methods=["POST"])
def mcp_recommend():
    body = request.json or {}
    command_id = body.get("command_id", "")
    if not command_id:
        return mcp_err("command_id required")
    rec_type = body.get("type", "full")
    if rec_type == "next":
        results = _rec.next_recommended(command_id)
    elif rec_type == "related":
        results = _rec.related(command_id)
    elif rec_type == "dependency":
        results = _rec.dependency_recommend(command_id)
    else:
        results = _rec.full(command_id)
    _audit.log("mcp.recommend", {"command_id": command_id, "type": rec_type})
    return jsonify(mcp_ok({
        "command_id": command_id,
        "type": rec_type,
        "recommendations": [r.to_dict() for r in results],
    }))


# ── Health / Boot ─────────────────────────────────────────────────────────────
@app.route("/mcp/health", methods=["GET"])
def mcp_health():
    v = _runtime.validate()
    return jsonify({"ok": True, "resumable": v["resumable"], "issues": v["issues"]})


@app.route("/mcp/boot", methods=["POST"])
def mcp_boot():
    ctx = _runtime.boot()
    return jsonify(mcp_ok({"booted": True, "protocol": ctx.get("protocol")}))


@app.route("/mcp/resume", methods=["POST"])
def mcp_resume():
    result = _runtime.resume()
    return jsonify(mcp_ok(result))


@app.route("/mcp/snapshot", methods=["POST"])
def mcp_snapshot():
    path = _runtime.snapshot()
    return jsonify(mcp_ok({"saved": str(path)}))


if __name__ == "__main__":
    _runtime.boot()
    print("[SEO-OS MCP] booting on port 8762...")
    app.run(port=8762, debug=False, use_reloader=False)
