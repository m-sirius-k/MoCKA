"""api/app.py — SEO Command Index REST API (Phase 9)
Endpoints:
  GET  /api/v3/search?q=&category=&limit=
  POST /api/v3/execute   {"command_id": "..."}
  GET  /api/v3/history?limit=
  GET  /api/v3/recommend/<command_id>
  GET  /api/v3/context
  GET  /api/v3/graph?format=json|svg|html
  GET  /api/v3/ranking?limit=
  GET  /api/v3/audit?limit=
  GET  /api/v3/workflows
  GET  /api/v3/commands
  GET  /api/v3/commands/<id>
"""
from __future__ import annotations
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, jsonify, request, Response
from command_index import CommandRegistry, CategoryManager, CommandIndexDB
from semantic import MeaningSearch, SimilarityRanking
from context_bridge import ContextBridge
from recommendation import RecommendationEngine, WorkflowRecommendation
from learning import LearningEngine
from dep_graph import DependencyGraph
from audit import AuditLogger


def create_app(db_path=None) -> Flask:
    app = Flask(__name__)
    if isinstance(db_path, CommandIndexDB):
        db = db_path
    else:
        db = CommandIndexDB(db_path)
    reg = CommandRegistry(db)
    cats = CategoryManager(db)
    search = MeaningSearch(db)
    ranking = SimilarityRanking(db)
    ctx = ContextBridge()
    rec = RecommendationEngine(db)
    wf = WorkflowRecommendation(db)
    learn = LearningEngine(db)
    graph = DependencyGraph(db)
    audit = AuditLogger(db)

    @app.route("/api/v3/search")
    def api_search():
        q = request.args.get("q", "")
        category = request.args.get("category") or None
        limit = int(request.args.get("limit", 10))
        results = ranking.rank(q, limit=limit, category=category)
        audit.log("search", {"q": q, "category": category, "count": len(results)})
        return jsonify({"results": [r.to_dict() for r in results],
                        "count": len(results), "query": q})

    @app.route("/api/v3/execute", methods=["POST"])
    def api_execute():
        data = request.json or {}
        command_id = data.get("command_id", "")
        cmd = reg.get(command_id)
        if not cmd:
            return jsonify({"ok": False, "error": "command not found"}), 404
        learn.record(command_id, "success")
        audit.log("execute", {"command_id": command_id})
        return jsonify({"ok": True, "command": cmd.to_dict()})

    @app.route("/api/v3/history")
    def api_history():
        limit = int(request.args.get("limit", 20))
        return jsonify(learn.recent(limit))

    @app.route("/api/v3/recommend/<command_id>")
    def api_recommend(command_id):
        results = rec.full(command_id)
        audit.log("recommend", {"command_id": command_id})
        return jsonify([r.to_dict() for r in results])

    @app.route("/api/v3/context")
    def api_context():
        return jsonify(ctx.get_memory_runtime())

    @app.route("/api/v3/graph")
    def api_graph():
        fmt = request.args.get("format", "json")
        audit.log("graph", {"format": fmt})
        if fmt == "svg":
            return Response(graph.to_svg(), mimetype="image/svg+xml")
        if fmt == "html":
            return Response(graph.to_html(), mimetype="text/html")
        return jsonify(json.loads(graph.to_json()))

    @app.route("/api/v3/ranking")
    def api_ranking():
        limit = int(request.args.get("limit", 10))
        return jsonify(learn.ranking(limit))

    @app.route("/api/v3/audit")
    def api_audit():
        limit = int(request.args.get("limit", 20))
        return jsonify(audit.recent(limit))

    @app.route("/api/v3/workflows")
    def api_workflows():
        return jsonify(wf.list_workflows())

    @app.route("/api/v3/commands")
    def api_commands():
        category = request.args.get("category") or None
        cmds = reg.list_all(category=category)
        return jsonify({"commands": [c.to_dict() for c in cmds],
                        "count": len(cmds)})

    @app.route("/api/v3/commands/<command_id>")
    def api_command(command_id):
        cmd = reg.get(command_id)
        if not cmd:
            return jsonify({"error": "not found"}), 404
        return jsonify({
            "command": cmd.to_dict(),
            "recommendations": [r.to_dict() for r in rec.full(command_id)],
            "workflows": wf.recommend_for_command(command_id),
        })

    @app.route("/api/v3/categories")
    def api_categories():
        return jsonify(cats.list_categories())

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=8761, debug=True, use_reloader=False)
