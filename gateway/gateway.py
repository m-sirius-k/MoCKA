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
from dotenv import load_dotenv

load_dotenv()

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
import adapter_claude       # STEP 6: HAB Common Core integration
import adapter_copilot
import adapter_perplexity   # TODO_269
import adapter_genspark     # TODO_270
from multi_dispatcher import dispatch_multi_request  # STEP 7: Multi-AI Socket E2E

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
        'claude':     adapter_claude,       # STEP 6: HAB Common Core integration
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


# ---------- Socket Outbound (AI API Call) ----------

@app.route("/api/v1/socket/request", methods=["POST"])
def socket_request():
    """
    Socket outbound: HAB → AI via Socket.
    Call external AI API (Claude/GPT) and return response.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    ai = data.get("ai", "").lower()
    request_text = data.get("request", "")
    model = data.get("model", "")
    title = data.get("title", "Socket Request")

    if not ai:
        return jsonify({"error": "ai parameter required (claude|gpt)"}), 400
    if not request_text:
        return jsonify({"error": "request parameter required"}), 400

    try:
        if ai == "claude":
            from adapters_claude_socket import ClaudeSocket
            socket = ClaudeSocket()
            model = model or "claude-opus-5"
            result = socket.request(request_text, model, title)
        elif ai == "gpt":
            from adapters_gpt_socket import GPTSocket
            socket = GPTSocket()
            model = model or "gpt-4"
            result = socket.request(request_text, model, title)
        elif ai == "gemini":
            from adapters_gemini_socket import GeminiSocket
            socket = GeminiSocket()
            model = model or "gemini-2.0-flash"
            result = socket.request(request_text, model, title)
        elif ai == "perplexity":
            from adapters_perplexity_socket import PerplexitySocket
            socket = PerplexitySocket()
            model = model or "sonar-pro"
            result = socket.request(request_text, model, title)
        else:
            return jsonify({"error": f"unsupported ai: {ai} (claude|gpt|gemini|perplexity)"}), 400

        return jsonify(result), (200 if result.get("status") == "ok" else 400)

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Socket request error: {str(e)}",
            "ai": ai,
        }), 500


@app.route("/api/v1/socket/multi_request", methods=["POST"])
def socket_multi_request():
    """
    Multi-AI Socket: HAB → Multiple AI Providers via Sockets.
    Dispatch single request to multiple AI providers and collect responses.
    Each provider response is recorded separately in HAB.

    Request body:
    {
        "request": "text to send to all AIs",
        "providers": ["gpt", "claude", "gemini", "perplexity"] (optional),
        "models": {"gpt": "gpt-4", ...} (optional),
        "title": "Multi-AI Request" (optional)
    }

    Response:
    {
        "status": "all_ok" | "partial_ok" | "all_error",
        "request_id": "common ID for all providers",
        "results": [
            {
                "provider": "gpt|claude|gemini|perplexity",
                "status": "ok|error|NOT_VERIFIED",
                "response": "...",
                "model": "...",
                "usage": {...},
                "error": "..." (if error),
                "timestamp": "...",
                "request_id": "..."
            }
        ],
        "summary": {
            "total": int,
            "ok": int,
            "error": int,
            "not_verified": int
        },
        "timestamp": "..."
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    request_text = data.get("request", "")
    providers = data.get("providers", None)
    models = data.get("models", None)
    title = data.get("title", "Multi-AI Socket Request")

    if not request_text:
        return jsonify({"error": "request parameter required"}), 400

    try:
        result = dispatch_multi_request(
            request_text=request_text,
            providers=providers,
            models=models,
            title=title,
        )

        # Record multi-request event to HAB
        try:
            now = datetime.now(timezone.utc)
            summary = result.get("summary", {})
            summary_text = (
                f"ok={summary.get('ok', 0)}, "
                f"error={summary.get('error', 0)}, "
                f"not_verified={summary.get('not_verified', 0)}"
            )

            get_buffer().push({
                "title": f"Multi-AI Request: {title}",
                "short_summary": summary_text,
                "when": now.isoformat(),
                "who_actor": "MultiAI/Dispatcher",
                "ai_actor": "Socket",
                "what_type": "multi_ai_request",
                "free_note": f"request_id={result.get('request_id')}",
                "where_component": "gateway_multi_dispatcher",
                "lifecycle_phase": "in_operation",
                "why_purpose": "multi_ai_e2e_test",
            })
        except Exception as hab_err:
            # Log but don't fail if HAB recording fails
            pass

        return jsonify(result), (200 if result.get("status") != "all_error" else 400)

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Multi-request dispatch error: {str(e)}",
        }), 500


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
