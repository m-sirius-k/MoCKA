#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connector Router (TODO_273)

ConnectorCaliber の connector_query は ai名を直接指定する（静的ルーティング）。
ConnectorRouter は「Capability」または「Role」を指定すると、
AICapabilityRegistry を参照して最適AIを動的に選択する（動的ルーティング）。

エンドポイント:
  POST /api/v1/connector/route
    body: {"capability": "web_search", "query": "...", "context_mode": "compact"}
    → best_for("web_search") でAIを選択し、connector_queryと同形式で返す

  POST /api/v1/connector/route/role
    body: {"role": "R05", "query": "...", "context_mode": "compact"}
    → best_for_role("R05") でAIを選択し、connector_queryと同形式で返す

  GET /api/v1/connector/capabilities
    → 登録済みCapability一覧 + 各Capabilityのbest_AI

統合方法:
  connector_caliber.py の register() 内で ConnectorRouter(self).register(app) を呼ぶ。
"""
from __future__ import annotations

import sys
import os

from flask import jsonify, request

# ai_capability_registry は interface/ 配下にある
_MOCKA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _MOCKA_ROOT not in sys.path:
    sys.path.insert(0, _MOCKA_ROOT)

from interface.ai_capability_registry import registry as _cap_registry

ROUTER_ID = "connector_router_v1"


class ConnectorRouter:
    """
    Capability/Roleベースの動的AIルーター。
    ConnectorCaliber インスタンスを受け取り、そのコンテキスト・アダプタを共有する。
    """

    def __init__(self, caliber):
        self._caliber = caliber   # ConnectorCaliber インスタンス

    def register(self, app):
        caliber = self._caliber

        # ── Capability ルーティング ──────────────────────────────

        @app.route("/api/v1/connector/route", methods=["POST"])
        def connector_route_capability():
            data       = request.get_json(silent=True) or {}
            capability = data.get("capability", "reasoning")
            query      = data.get("query", "")
            context_mode = data.get("context_mode", "compact")
            exclude    = data.get("exclude", [])

            best_ai = _cap_registry.best_for(capability, exclude=exclude)
            if best_ai is None:
                return jsonify({"error": f"no AI found for capability: {capability}"}), 404

            ai_info     = _cap_registry.get_ai_info(best_ai)
            adapter_key = ai_info["adapter_key"]

            if adapter_key not in caliber.adapters:
                return jsonify({
                    "error": f"adapter not loaded: {adapter_key} (for {best_ai})",
                    "hint": "gateway.py に adapter を追加してください",
                }), 503

            context = caliber.cb.build(context_mode)
            result = {
                "ai":          best_ai,
                "adapter_key": adapter_key,
                "capability":  capability,
                "query":       query,
                "context":     context,
                "routing":     {
                    "method":    "capability",
                    "score":     ai_info["capabilities"].get(capability, 0.0),
                    "trust":     ai_info["trust_level"],
                },
            }
            caliber._record_event(best_ai, f"[route:{capability}] {query}", result)
            return jsonify(result)

        # ── Role ルーティング ─────────────────────────────────────

        @app.route("/api/v1/connector/route/role", methods=["POST"])
        def connector_route_role():
            data         = request.get_json(silent=True) or {}
            role_id      = data.get("role", "R01")
            query        = data.get("query", "")
            context_mode = data.get("context_mode", "compact")
            exclude      = data.get("exclude", [])

            best_ai = _cap_registry.best_for_role(role_id, exclude=exclude)
            if best_ai is None:
                return jsonify({"error": f"no AI found for role: {role_id}"}), 404

            ai_info     = _cap_registry.get_ai_info(best_ai)
            adapter_key = ai_info["adapter_key"]

            if adapter_key not in caliber.adapters:
                return jsonify({
                    "error": f"adapter not loaded: {adapter_key} (for {best_ai})",
                    "hint": "gateway.py に adapter を追加してください",
                }), 503

            context = caliber.cb.build(context_mode)
            result = {
                "ai":          best_ai,
                "adapter_key": adapter_key,
                "role":        role_id,
                "query":       query,
                "context":     context,
                "routing":     {
                    "method":    "role",
                    "trust":     ai_info["trust_level"],
                },
            }
            caliber._record_event(best_ai, f"[route:role={role_id}] {query}", result)
            return jsonify(result)

        # ── Capability 一覧 ───────────────────────────────────────

        @app.route("/api/v1/connector/capabilities", methods=["GET"])
        def connector_capabilities():
            caps = _cap_registry.all_capabilities()
            result = {
                "capabilities": [
                    {
                        "name":    cap,
                        "best_ai": _cap_registry.best_for(cap),
                        "candidates": [
                            {"ai": c["ai"], "score": c["score"]}
                            for c in _cap_registry.candidates_for(cap, min_score=0.6)
                        ],
                    }
                    for cap in caps
                ],
                "router": ROUTER_ID,
            }
            return jsonify(result)

        # ── ルーター健全性 ────────────────────────────────────────

        @app.route("/api/v1/connector/router/health", methods=["GET"])
        def connector_router_health():
            snapshot = _cap_registry.snapshot()
            return jsonify({
                "status":  "ok",
                "router":  ROUTER_ID,
                "ai_count": snapshot["ai_count"],
                "capabilities": snapshot["capabilities"],
            })
