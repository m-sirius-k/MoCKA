# -*- coding: utf-8 -*-
# MoCKA AI Connector Framework v1
# Role: AI Adapter Layer (MoCKA AI Architecture v2.0)
# Port: 5010 | Internal connector - NOT for public exposure
# Connects: GPT/Gemini/Copilot -> MoCKA MCP (port:5002)
# ref: E20260610_010 / TODO_268
import json
import sys
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from context_builder import ContextBuilder
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from auth import require_api_key
import auth as auth_module
from connector_caliber import ConnectorCaliber
import adapter_gpt
import adapter_gemini
import adapter_copilot
import adapter_perplexity   # TODO_269
import adapter_genspark     # TODO_270

sys.path.insert(0, str(Path(__file__).parent.parent / "interface"))
from event_buffer import get_buffer  # Phase5-1: Gate Enforcement(db直書き禁止)

app = Flask(__name__)
CORS(app)

builder = ContextBuilder()

DB_PATH  = Path(__file__).parent.parent / "data" / "mocka_events.db"
DATA_DIR = Path(__file__).parent.parent / "data"

connector = ConnectorCaliber(
    db_path=DB_PATH,
    context_builder=builder,
    auth=auth_module,
    adapters={
        'gpt':        adapter_gpt,
        'gemini':     adapter_gemini,
        'copilot':    adapter_copilot,
        'perplexity': adapter_perplexity,   # TODO_269
        'genspark':   adapter_genspark,     # TODO_270
    },
)
connector.register(app)


@app.before_request
def check_auth():
    require_api_key()


# ---------- GET endpoints ----------

@app.route("/api/v1/context")
def get_context():
    mode = request.args.get("mode", "standard")
    return jsonify(builder.build(mode))


@app.route("/api/v1/todo")
def get_todo():
    ctx = builder.build("standard")
    return jsonify({"active_todo": ctx["active_todo"]})


@app.route("/api/v1/phase")
def get_phase():
    ctx = builder.build("compact")
    return jsonify({"phase": ctx["phase"]})


@app.route("/api/v1/essence")
def get_essence():
    try:
        raw = json.loads((DATA_DIR / "lever_essence.json").read_text(encoding="utf-8"))
        return jsonify(raw)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/last_event")
def get_last_event():
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur  = conn.cursor()
        # 正: when_ts / short_summary  (when_time / description は誤カラム名)
        cur.execute(
            "SELECT event_id, title, short_summary, when_ts, what_type "
            "FROM events ORDER BY when_ts DESC LIMIT 1"
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return jsonify({}), 404
        return jsonify({
            "id":            row[0],
            "title":         row[1],
            "short_summary": row[2],
            "when":          row[3],
            "what_type":     row[4],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/summary")
def get_summary():
    ctx = builder.build("compact")
    summary = (
        f"[{ctx['phase'][:50]}] "
        f"目標: {ctx['goal'][:80]} "
        f"最終決定: {ctx['last_decision'][:60]}"
    )[:200]
    return jsonify({"summary": summary})


@app.route("/api/v1/health")
def health():
    return jsonify({
        "status":  "ok",
        "service": "MoCKA Gateway",
        "version": "1.1",
        "port":    5010,
        "time":    datetime.now(timezone.utc).isoformat(),
    })


# ---------- POST endpoint ----------

@app.route("/api/v1/event", methods=["POST"])
def post_event():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    actor  = data.get("actor", {})
    vendor = actor.get("vendor", "Unknown")
    model  = actor.get("model", "")
    source = actor.get("source", "Direct")

    title         = data.get("title", "").strip()
    short_summary = data.get("description", "").strip()   # リクエスト側はdescription可
    tags_raw      = data.get("tags", [])
    tags_str      = ",".join(tags_raw) if isinstance(tags_raw, list) else str(tags_raw)

    if not title:
        return jsonify({"error": "title is required"}), 400

    try:
        now = datetime.now(timezone.utc)
        # who_actor = "vendor/model" 形式で格納
        # ai_actor  = source（Orchestra等）
        # タグ専用カラムなし → what_type に gateway_event を、free_note にタグを格納
        who_actor = f"{vendor}/{model}" if model else vendor

        # Phase5-1: 生SQL INSERT INTO events禁止 → Local Buffer経由でGateへ統一
        get_buffer().push({
            "title":           title,
            "short_summary":   short_summary,
            "when":            now.isoformat(),
            "who_actor":       who_actor,
            "ai_actor":        source,
            "what_type":       "gateway_event",
            "free_note":       tags_str,
            "where_component": "gateway",
            "lifecycle_phase": "in_operation",
            "why_purpose":     data.get("why_purpose", "multi_ai_record"),
        })
        return jsonify({"status": "ok"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=False)
