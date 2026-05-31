"""
mocka_mcp_server_vps.py v1.5.1
MoCKA Memory Caliber -- MCP Server (VPS edition)
パス設定を環境変数 / デフォルト値で解決（Linux対応）
"""

import json, hashlib, datetime, re, sqlite3, os
from pathlib import Path
from flask import Flask, request
from flask_cors import CORS

# ── パス設定（環境変数 > デフォルト）──
_HOME = Path(os.environ.get("MOCKA_HOME", Path.home() / "mocka"))
BASE           = _HOME
OVERVIEW_PATH  = _HOME / "MOCKA_OVERVIEW.json"
TODO_PATH      = _HOME / "MOCKA_TODO.json"
KNOWLEDGE_GATE = _HOME / "data"
DB_PATH        = _HOME / "data" / "mocka_events.db"
PUBLIC_URL     = os.environ.get("MOCKA_PUBLIC_URL", "https://mocka.nsjp.org")

EVENTS_FIELDS = [
    "event_id","when","who_actor","what_type","where_component","where_path",
    "why_purpose","how_trigger","channel_type","lifecycle_phase","risk_level",
    "category_ab","target_class","title","short_summary","before_state",
    "after_state","change_type","impact_scope","impact_result",
    "related_event_id","trace_id","free_note"
]

# ── DB ヘルパー ──
def _get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS claude_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, tool TEXT, args TEXT, result_summary TEXT
    )""")
    con.commit()
    return con

def _sanitize(text):
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    text = text.lstrip("﻿").replace("�", "")
    if text.count("?") >= 3 and len(text.replace("?","").strip()) < len(text) * 0.5:
        return ""
    return text

def _db_read_events(n=None):
    try:
        con = _get_db()
        cur = con.cursor()
        sql = "SELECT * FROM events ORDER BY rowid" + (" DESC LIMIT ?" if n else "")
        cur.execute(sql, (n,) if n else ())
        if not cur.description:
            return []
        cols = [d[0] for d in cur.description]
        rows = []
        for r in cur.fetchall():
            row = dict(zip(cols, r))
            if "when_ts" in row and "when" not in row:
                row["when"] = row["when_ts"]
            rows.append(row)
        con.close()
        return rows
    except Exception as e:
        print(f"[MCP] db_read_events error: {e}")
        return []

def _db_write_event(row: dict):
    try:
        safe = {k: _sanitize(str(v)) for k, v in row.items()}
        con = _get_db()
        cur = con.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO events
            (event_id, when_ts, who_actor, what_type, where_component, where_path,
             why_purpose, how_trigger, channel_type, lifecycle_phase, risk_level,
             category_ab, target_class, title, short_summary, before_state,
             after_state, change_type, impact_scope, impact_result,
             related_event_id, trace_id, free_note)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            safe.get("event_id",""), safe.get("when",""), safe.get("who_actor",""),
            safe.get("what_type",""), safe.get("where_component",""), safe.get("where_path",""),
            safe.get("why_purpose",""), safe.get("how_trigger",""), safe.get("channel_type",""),
            safe.get("lifecycle_phase",""), safe.get("risk_level",""), safe.get("category_ab",""),
            safe.get("target_class",""), safe.get("title",""), safe.get("short_summary",""),
            safe.get("before_state",""), safe.get("after_state",""), safe.get("change_type",""),
            safe.get("impact_scope",""), safe.get("impact_result",""),
            safe.get("related_event_id",""), safe.get("trace_id",""), safe.get("free_note",""),
        ))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(f"[MCP] db_write_event error: {e}")
        return False

# ── ユーティリティ ──
def read_events(n=20):
    rows = _db_read_events()
    return rows[-n:] if n else rows

def search_events(query):
    q = query.lower()
    return [r for r in _db_read_events() if any(q in str(v).lower() for v in r.values())]

def search_knowledge_gate(query):
    q = query.lower()
    results = []
    if not KNOWLEDGE_GATE.exists():
        return results
    for md in KNOWLEDGE_GATE.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8")
            if q in text.lower():
                for i, line in enumerate(text.splitlines()):
                    if q in line.lower():
                        snippet = "\n".join(text.splitlines()[max(0,i-1):i+3])
                        results.append({"file": str(md.relative_to(BASE)), "snippet": snippet.strip()})
                        break
        except:
            pass
    return results

def next_event_id():
    today = datetime.date.today().strftime("%Y%m%d")
    try:
        con = _get_db()
        cur = con.cursor()
        cur.execute("SELECT event_id FROM events WHERE event_id LIKE ?", (f"E{today}_%",))
        ids = [r[0] for r in cur.fetchall()]
        con.close()
        rx = re.compile(rf"E{today}_(\d+)")
        nums = [int(m.group(1)) for eid in ids for m in [rx.search(eid)] if m]
    except:
        nums = []
    return f"E{today}_{(max(nums)+1 if nums else 1):03d}"

def auto_log(tool_name, args, result_summary):
    try:
        ts  = datetime.datetime.now().isoformat()
        arg = json.dumps(args, ensure_ascii=False)[:200]
        res = _sanitize(str(result_summary))[:200]
        con = _get_db()
        con.execute(
            "INSERT INTO claude_sessions (timestamp, tool, args, result_summary) VALUES (?,?,?,?)",
            (ts, tool_name, arg, res)
        )
        con.commit()
        con.close()
    except:
        pass

def load_todo():
    return json.loads(TODO_PATH.read_text(encoding="utf-8-sig"))

def save_todo(data):
    data["meta"]["updated"] = datetime.date.today().isoformat()
    data["meta"]["updated_by"] = "Claude"
    TODO_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# ── ツール定義 ──
TOOLS = [
    {"name":"mocka_get_overview","description":"MOCKA_OVERVIEW.json を返す","inputSchema":{"type":"object","properties":{},"required":[]}},
    {"name":"mocka_get_essence","description":"MoCKA本質サマリーを返す","inputSchema":{"type":"object","properties":{},"required":[]}},
    {"name":"mocka_get_todo","description":"MOCKA_TODO.json を返す","inputSchema":{"type":"object","properties":{},"required":[]}},
    {"name":"mocka_add_todo","description":"新規TODOをMOCKA_TODO.jsonに追加する","inputSchema":{"type":"object","properties":{"id":{"type":"string"},"title":{"type":"string"},"status":{"type":"string","default":"未着手"},"priority":{"type":"string","default":"中"},"category":{"type":"string"},"description":{"type":"string"},"assigned_to":{"type":"string"},"note":{"type":"string"},"reference_event":{"type":"string"}},"required":["id","title"]}},
    {"name":"mocka_update_todo","description":"TODO statusを更新する","inputSchema":{"type":"object","properties":{"id":{"type":"string"},"status":{"type":"string"},"note":{"type":"string"}},"required":["id","status"]}},
    {"name":"mocka_list_events","description":"最新Nイベントを返す","inputSchema":{"type":"object","properties":{"n":{"type":"integer","default":20}},"required":[]}},
    {"name":"mocka_read_event","description":"IDでイベント取得","inputSchema":{"type":"object","properties":{"id":{"type":"string"}},"required":["id"]}},
    {"name":"mocka_search","description":"全文検索","inputSchema":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}},
    {"name":"mocka_write_event","description":"イベント追記","inputSchema":{"type":"object","properties":{"title":{"type":"string"},"description":{"type":"string"},"tags":{"type":"string"},"author":{"type":"string","default":"Claude"},"why_purpose":{"type":"string"},"how_trigger":{"type":"string"}},"required":["title","description"]}},
    {"name":"mocka_seal","description":"SHA-256ハッシュ検証","inputSchema":{"type":"object","properties":{},"required":[]}},
]

def execute_tool(name, args):
    try:
        if name == "mocka_get_overview":
            if not OVERVIEW_PATH.exists():
                return json.dumps({"error": f"not found: {OVERVIEW_PATH}"})
            result = json.loads(OVERVIEW_PATH.read_text(encoding="utf-8-sig"))
            auto_log(name, args, "overview loaded")
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif name == "mocka_get_essence":
            essence_path = BASE / "lever_essence.json"
            if not essence_path.exists():
                return json.dumps({"error": "lever_essence.json not found"})
            data = json.loads(essence_path.read_text(encoding="utf-8"))
            result = {
                "INCIDENT": data.get("INCIDENT", ""),
                "PHILOSOPHY": data.get("PHILOSOPHY", ""),
                "OPERATION": data.get("OPERATION", ""),
            }
            auto_log(name, args, "essence loaded")
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif name == "mocka_get_todo":
            if not TODO_PATH.exists():
                return json.dumps({"error": f"not found: {TODO_PATH}"})
            result = load_todo()
            auto_log(name, args, "todo loaded")
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif name == "mocka_add_todo":
            if not TODO_PATH.exists():
                return json.dumps({"error": f"not found: {TODO_PATH}"})
            todo_id = args.get("id", "").strip()
            title   = args.get("title", "").strip()
            if not todo_id or not title:
                return json.dumps({"error": "id and title are required"})
            data = load_todo()
            all_ids = [t.get("id") for t in data.get("todos", [])] + [t.get("id") for t in data.get("completed", [])]
            if todo_id in all_ids:
                return json.dumps({"error": f"{todo_id} already exists"})
            new_todo = {
                "id": todo_id, "title": title,
                "status": args.get("status", "未着手"),
                "priority": args.get("priority", "中"),
                "category": args.get("category", ""),
                "description": args.get("description", ""),
                "assigned_to": args.get("assigned_to", "Claude"),
                "note": args.get("note", ""),
                "reference_event": args.get("reference_event", ""),
                "created_at": datetime.datetime.now().isoformat()
            }
            data["todos"].append(new_todo)
            save_todo(data)
            auto_log(name, args, f"added {todo_id}")
            return json.dumps({"status": "ok", "id": todo_id, "action": "added"}, ensure_ascii=False)

        elif name == "mocka_update_todo":
            if not TODO_PATH.exists():
                return json.dumps({"error": f"not found: {TODO_PATH}"})
            todo_id    = args.get("id", "")
            new_status = args.get("status", "")
            note       = args.get("note", "")
            data = load_todo()
            updated = False
            for item in data.get("todos", []):
                if item.get("id") == todo_id:
                    item["status"] = new_status
                    if note:
                        item["note"] = note
                    item["updated_at"] = datetime.datetime.now().isoformat()
                    if new_status == "完了":
                        item["completed_at"] = datetime.date.today().isoformat()
                        data.setdefault("completed", []).append(item)
                        data["todos"].remove(item)
                    updated = True
                    break
            if not updated:
                return json.dumps({"error": f"{todo_id} not found"})
            save_todo(data)
            auto_log(name, args, f"updated {todo_id} -> {new_status}")
            return json.dumps({"status": "ok", "id": todo_id, "new_status": new_status}, ensure_ascii=False)

        elif name == "mocka_list_events":
            events = read_events(int(args.get("n", 20)))
            auto_log(name, args, f"{len(events)} events")
            return json.dumps({"count": len(events), "events": events}, ensure_ascii=False, indent=2)

        elif name == "mocka_read_event":
            eid   = args.get("id", "")
            found = [e for e in read_events(9999) if e.get("event_id") == eid]
            auto_log(name, args, "found" if found else "not found")
            return json.dumps(found[0] if found else {"error": "not found"}, ensure_ascii=False, indent=2)

        elif name == "mocka_search":
            q  = args.get("query", "")
            ev = search_events(q)
            kg = search_knowledge_gate(q)
            auto_log(name, args, f"events:{len(ev)} kg:{len(kg)}")
            return json.dumps({"query": q, "events_hits": ev, "knowledge_gate_hits": kg}, ensure_ascii=False, indent=2)

        elif name == "mocka_write_event":
            eid = next_event_id()
            ts  = datetime.datetime.now().isoformat()
            row = {f: "" for f in EVENTS_FIELDS}
            row.update({
                "event_id": eid, "when": ts,
                "who_actor": args.get("author", "Claude"),
                "what_type": "claude_mcp",
                "where_component": "mcp_caliber",
                "where_path": "mocka_mcp_server_vps.py",
                "why_purpose": args.get("why_purpose", ""),
                "how_trigger": args.get("how_trigger", ""),
                "title": args.get("title", ""),
                "short_summary": args.get("description", ""),
                "free_note": args.get("tags", ""),
                "lifecycle_phase": "in_operation",
                "risk_level": "normal",
                "channel_type": "mcp",
            })
            ok = _db_write_event(row)
            auto_log(name, args, f"written {eid}")
            return json.dumps({"status": "ok" if ok else "error", "event_id": eid, "when": ts, "storage": "sqlite"}, ensure_ascii=False)

        elif name == "mocka_seal":
            rows    = _db_read_events()
            payload = json.dumps(rows, ensure_ascii=False, sort_keys=True).encode("utf-8")
            h       = hashlib.sha256(payload).hexdigest()
            result  = {"sha256": h, "source": "sqlite", "event_count": len(rows),
                       "timestamp": datetime.datetime.now().isoformat()}
            auto_log(name, args, h[:16])
            return json.dumps(result, ensure_ascii=False)

        return json.dumps({"error": f"unknown tool: {name}"})

    except Exception as e:
        return json.dumps({"error": str(e)})

# ── Flask アプリ ──
app = Flask(__name__)
CORS(app, origins="*")

@app.route("/mcp", methods=["GET", "POST"])
def mcp_endpoint():
    if request.method == "GET":
        return json.dumps({"name": "mocka-memory-caliber", "version": "1.5.1-vps"}), 200, {"Content-Type": "application/json"}
    body   = request.get_json()
    method = body.get("method", "")
    req_id = body.get("id")
    params = body.get("params", {})
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "mocka-memory-caliber", "version": "1.5.1-vps"}}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        result = {"content": [{"type": "text", "text": execute_tool(params.get("name", ""), params.get("arguments", {}))}], "isError": False}
    else:
        return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"unknown: {method}"}}), 200, {"Content-Type": "application/json"}
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}, ensure_ascii=False), 200, {"Content-Type": "application/json"}

@app.route("/.well-known/oauth-protected-resource", defaults={"subpath": ""})
@app.route("/.well-known/oauth-protected-resource/<path:subpath>")
def oauth_resource(subpath):
    return json.dumps({"resource": PUBLIC_URL, "authorization_servers": []}), 200, {"Content-Type": "application/json"}

@app.route("/.well-known/oauth-authorization-server")
def oauth_server():
    return json.dumps({}), 200, {"Content-Type": "application/json"}

@app.route("/register", methods=["POST"])
def register():
    return json.dumps({"client_id": "mocka-mcp", "client_secret": "none"}), 200, {"Content-Type": "application/json"}

@app.route("/health")
def health():
    rows = _db_read_events()
    return json.dumps({
        "status": "ok", "version": "1.5.1-vps", "port": 5002,
        "overview_exists": OVERVIEW_PATH.exists(),
        "todo_exists": TODO_PATH.exists(),
        "storage": "sqlite", "event_count": len(rows),
        "tools": [t["name"] for t in TOOLS],
        "public_url": PUBLIC_URL,
    }, ensure_ascii=False), 200, {"Content-Type": "application/json"}

@app.route("/agent/tools", methods=["GET"])
def agent_tools():
    return json.dumps({"tools": [t["name"] for t in TOOLS], "usage": "POST /agent/<tool_name>"}), 200, {"Content-Type": "application/json"}

@app.route("/agent/<tool_name>", methods=["POST", "GET"])
def agent_call(tool_name):
    args = {}
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        args = body.get("args", body)
    result = execute_tool(tool_name, args)
    return result, 200, {"Content-Type": "application/json; charset=utf-8"}

if __name__ == "__main__":
    port = int(os.environ.get("MOCKA_PORT", 5002))
    print(f"MoCKA MCP Server v1.5.1-vps -- http://localhost:{port}/mcp")
    print(f"MOCKA_HOME: {BASE}")
    print(f"DB: {DB_PATH}")
    print(f"Tools: {len(TOOLS)}")
    app.run(host="127.0.0.1", port=port, debug=False)
