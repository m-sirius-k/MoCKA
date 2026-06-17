"""dashboard/server.py — DashboardServer: Flask ベースのCommand Center"""
from __future__ import annotations
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template_string, jsonify, request
from command_index import CommandRegistry, CategoryManager, CommandIndexDB
from semantic import MeaningSearch, SimilarityRanking
from context_bridge import ContextBridge
from recommendation import RecommendationEngine, WorkflowRecommendation
from learning import LearningEngine
from dep_graph import DependencyGraph
from audit import AuditLogger

_DASHBOARD_HTML = open(
    os.path.join(os.path.dirname(__file__), "index.html"),
    encoding="utf-8"
).read if os.path.exists(os.path.join(os.path.dirname(__file__), "index.html")) else None


class DashboardServer:
    def __init__(self, db_path=None, port: int = 8760) -> None:
        self._db = CommandIndexDB(db_path)
        self._port = port
        self._reg = CommandRegistry(self._db)
        self._cats = CategoryManager(self._db)
        self._search = MeaningSearch(self._db)
        self._ranking = SimilarityRanking(self._db)
        self._context = ContextBridge()
        self._rec = RecommendationEngine(self._db)
        self._wf = WorkflowRecommendation(self._db)
        self._learn = LearningEngine(self._db)
        self._graph = DependencyGraph(self._db)
        self._audit = AuditLogger(self._db)
        self.app = self._build_app()

    def _build_app(self) -> Flask:
        app = Flask(__name__)

        @app.route("/")
        def index():
            return render_template_string(_build_html())

        @app.route("/api/search")
        def api_search():
            q = request.args.get("q", "")
            cat = request.args.get("category")
            results = self._ranking.rank(q, limit=12, category=cat or None)
            self._audit.log("search", {"query": q, "results": len(results)})
            return jsonify([r.to_dict() for r in results])

        @app.route("/api/categories")
        def api_categories():
            return jsonify(self._cats.list_categories())

        @app.route("/api/commands/<command_id>")
        def api_command(command_id):
            cmd = self._reg.get(command_id)
            if not cmd:
                return jsonify({"error": "not found"}), 404
            return jsonify({
                "command": cmd.to_dict(),
                "recommendations": [r.to_dict() for r in self._rec.full(command_id)],
                "workflows": self._wf.recommend_for_command(command_id),
            })

        @app.route("/api/commands/<command_id>/execute", methods=["POST"])
        def api_execute(command_id):
            cmd = self._reg.get(command_id)
            if not cmd:
                return jsonify({"error": "not found"}), 404
            self._learn.record(command_id, "success")
            self._audit.log("execute", {"command_id": command_id})
            return jsonify({"ok": True, "command": cmd.to_dict()})

        @app.route("/api/context")
        def api_context():
            return jsonify(self._context.get_memory_runtime())

        @app.route("/api/graph")
        def api_graph():
            fmt = request.args.get("format", "json")
            if fmt == "svg":
                from flask import Response
                return Response(self._graph.to_svg(), mimetype="image/svg+xml")
            if fmt == "html":
                from flask import Response
                return Response(self._graph.to_html(), mimetype="text/html")
            return jsonify(json.loads(self._graph.to_json()))

        @app.route("/api/ranking")
        def api_ranking():
            return jsonify(self._learn.ranking())

        @app.route("/api/recommend/<command_id>")
        def api_recommend(command_id):
            return jsonify([r.to_dict() for r in self._rec.full(command_id)])

        @app.route("/api/history")
        def api_history():
            return jsonify(self._learn.recent(limit=20))

        @app.route("/api/workflows")
        def api_workflows():
            return jsonify(self._wf.list_workflows())

        @app.route("/api/audit")
        def api_audit():
            return jsonify(self._audit.recent(20))

        return app

    def run(self, debug: bool = False) -> None:
        self.app.run(port=self._port, debug=debug, use_reloader=False)


def _build_html() -> str:
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        return open(html_path, encoding="utf-8").read()
    return "<h1>Dashboard index.html not found</h1>"
