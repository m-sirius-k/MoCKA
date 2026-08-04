"""
mocka_mcp_server_vps.py v1.6.0
MoCKA Memory Caliber -- MCP Server (VPS edition)
パス設定を環境変数 / デフォルト値で解決（Linux対応）

v1.6.0 変更点（Phase5-2.1 Unified Event Entry への収束）:
  mocka_write_event のイベント保存経路を phi_os.event_gate.process_event() に統一した。
  従来の _db_write_event() による events テーブルへの直接INSERTは、Gate Policy /
  Integrity署名 / Hash Chain のいずれも経由しないため、HTTP経路(/api/gate/event)との
  間に制度差が生じていた。process_event() は
  "Flask route と MCP server のいずれの呼び出し元からも、トランスポート(HTTP/
  インプロセス)を問わずこの関数を経由しなければならない唯一の保存経路"
  として定義されているため、VPS版MCPもこれに収束させる。
"""

import json, hashlib, datetime, re, sqlite3, os, sys
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

SESSION_ID     = "SESSION_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
_DEFAULT_ACTOR = "Claude-code-sonnet-4-6"  # レガシー値("Claude"/"claude")の正規化先

EVENTS_FIELDS = [
    "event_id","when","who_actor","what_type","where_component","where_path",
    "why_purpose","how_trigger","channel_type","lifecycle_phase","risk_level",
    "category_ab","target_class","title","short_summary","before_state",
    "after_state","change_type","impact_scope","impact_result",
    "related_event_id","trace_id","free_note"
]

# --- PHI-OS Event Gate 接続（唯一のevents保存経路） ---
# setup_vps.sh により phi_os/ と interface/ は MOCKA_HOME 直下へ配置される。
# リポジトリから直接起動する場合(deploy/配下にこのファイルがある場合)は
# 1つ上の階層にphi_os/があるため、そちらも候補に含める。
def _resolve_gate_root():
    _here = Path(__file__).resolve().parent
    for cand in (_HOME, _here, _here.parent):
        if (cand / "phi_os" / "event_gate.py").exists():
            return cand
    return None

GATE_ROOT = _resolve_gate_root()
GATE_IMPORT_ERROR = None
process_event = None

if GATE_ROOT is None:
    GATE_IMPORT_ERROR = (
        "phi_os/event_gate.py not found. 探索したルート: "
        + ", ".join(str(p) for p in (_HOME, Path(__file__).resolve().parent,
                                      Path(__file__).resolve().parent.parent))
    )
else:
    if str(GATE_ROOT) not in sys.path:
        sys.path.insert(0, str(GATE_ROOT))
    try:
        # event_gate 側は MOCKA_HOME を見てDB_PATHを解決するため、
        # 本ファイルのDB_PATHと同一のDBへ収束する（_check_gate_db_alignment で検証）。
        from phi_os.event_gate import process_event, DB_PATH as GATE_DB_PATH
    except Exception as e:
        GATE_IMPORT_ERROR = f"{type(e).__name__}: {e}"

GATE_AVAILABLE = process_event is not None


def _check_gate_db_alignment():
    """
    Gate側DB_PATHと本サーバーのDB_PATHが同一ファイルを指すことを検証する。
    ズレていれば "同じevents保存経路" という前提が崩れるため、起動時に検出する。
    戻り値: (ok: bool, detail: str)
    """
    if not GATE_AVAILABLE:
        return False, f"gate unavailable: {GATE_IMPORT_ERROR}"
    mine = os.path.realpath(str(DB_PATH))
    gate = os.path.realpath(str(GATE_DB_PATH))
    if mine != gate:
        return False, f"DB_PATH mismatch: server={mine} gate={gate}"
    return True, mine


# events書き込みに必要な列（Gate _write() が挿入する列のうち、旧スキーマに
# 存在しない可能性があるもの）。不足していると書き込みが失敗するため事前検出する。
_GATE_REQUIRED_COLUMNS = ("session_id", "_source", "when_ts")


def _check_events_schema():
    """events テーブルがGate書き込みに必要な列を備えているかを検証する"""
    try:
        con = sqlite3.connect(str(DB_PATH))
        cols = {r[1] for r in con.execute("PRAGMA table_info(events)").fetchall()}
        con.close()
    except Exception as e:
        return False, f"schema check error: {e}"
    if not cols:
        return False, "events table not found"
    missing = [c for c in _GATE_REQUIRED_COLUMNS if c not in cols]
    if missing:
        return False, "missing columns: " + ",".join(missing)
    return True, "ok"

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
    """
    [DEPRECATED / 削除候補 — v1.6.0で参照停止]

    Gate Policy・Integrity署名・Hash Chainのいずれも経由しない直接INSERTであり、
    Phase5-2.1 Unified Event Entry の "events保存経路は process_event() 以外に
    制度上存在しない" に反する。v1.6.0で mocka_write_event からの呼び出しを
    撤去済みであり、本ファイル内の参照はゼロ。

    即時削除はせず、VPS実機での参照停止を確認した後に削除する。
    新規のイベント保存でこの関数を呼び出してはならない
    （呼び出した時点で制度違反イベント = _source が Gate 分類外になる）。
    """
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
    """
    [DEPRECATED / 削除候補 — v1.6.0で参照停止]
    event_id採番は phi_os.event_gate._next_event_id()（日内マイクロ秒+ランダム4hex・
    並列安全）へ一本化された。本関数のMAX+1方式は並列書き込みで衝突するため、
    新規の採番に使用してはならない。_db_write_event()と同時に削除する。
    """
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
    {"name":"mocka_write_event","description":"イベント追記(PHI-OS Event Gate経由)","inputSchema":{"type":"object","properties":{"title":{"type":"string"},"description":{"type":"string"},"tags":{"type":"string"},"author":{"type":"string","description":"必須: 正確なAI識別子 e.g. Claude-sonnet-4-6, gpt-4o, script:xxx"},"why_purpose":{"type":"string","description":"10文字以上必須(Gate REJECT-03)"},"how_trigger":{"type":"string"}},"required":["title","description","author"]}},
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
            # [PHI-OS GATE / Phase5-2.1 Unified Event Entry — v1.6.0]
            # 生SQLの直接INSERT(_db_write_event)は廃止し、HTTP経路(/api/gate/event)と
            # 完全に同一の process_event() をインプロセスで呼び出す。これにより
            # Validation -> Gate Policy -> Signature -> Hash Chain -> DB Commit が
            # MCP経路にも等しく適用され、HTTP/MCP間の制度差が解消する。
            if not GATE_AVAILABLE:
                # Gateがimportできない場合、直接INSERTへフォールバックしてはならない
                # （それは制度上存在しない保存経路であり、単一経路保証が壊れる）。
                # 記録できないことを隠さず、明示的にエラーとして返す。
                auto_log(name, args, f"gate unavailable: {GATE_IMPORT_ERROR}")
                return json.dumps({
                    "status": "gate_unavailable",
                    "errors": [f"phi_os.event_gate is not importable: {GATE_IMPORT_ERROR}"],
                    "note": "直接INSERTへのフォールバックは行わない（Gate単一経路保証のため）",
                }, ensure_ascii=False)

            # GL7-VALIDATION-MISSING-BUG是正（Windows正本 mocka_mcp_server.py と同一方針）:
            # 空値を自動補填せず、検知してREJECTする。
            _title     = args.get("title", "").strip()
            _desc      = args.get("description", "").strip()
            _actor_raw = args.get("author", "").strip()
            if not _title:
                return json.dumps({"status": "gate_rejected", "errors": ["title is required (empty)"]}, ensure_ascii=False)
            if not _desc:
                return json.dumps({"status": "gate_rejected", "errors": ["description is required (empty)"]}, ensure_ascii=False)
            if not _actor_raw:
                return json.dumps({"status": "gate_rejected", "errors": ["author is required (empty)"]}, ensure_ascii=False)
            # 未指定検知は完了済み。レガシー値のみ既定Actorへ正規化する。
            _actor = _DEFAULT_ACTOR if _actor_raw in ("Claude", "claude") else _actor_raw

            # event_source は "live"（HTTP経路と同一のGate分類値）。
            # MCP由来であることは transport属性として channel_type / where_component /
            # how_trigger に保持する。channel_type="mcp" は event_gate._write() により
            # free_note へ orig_channel=mcp として記録される。
            # ("mcp" を event_source に用いると events._source の CHECK制約
            #  (gate_policy.ALLOWED_SOURCE_VALUES) 外となりINSERTが失敗するうえ、
            #  Gate Auditでも制度違反として集計されてしまう)
            gate_payload = {
                "who_actor":       _actor,
                "who_role":        "executor",
                "who_session":     SESSION_ID,
                "what_type":       "claude_mcp",
                "what_title":      _title,
                "where_path":      "mocka_mcp_server_vps.py",
                "where_component": "mcp_caliber",
                "why_purpose":     args.get("why_purpose", "") or _desc[:80] or _title,
                "how_trigger":     args.get("how_trigger", "") or "mocka_write_event",
                "after_state":     _desc[:200] or _title,
                "description":     _desc,
                "tags":            args.get("tags", ""),
                "channel_type":    "mcp",
            }
            result = process_event(gate_payload, event_source="live")
            if result.get("status") == "ok":
                eid = result["event_id"]
                auto_log(name, args, f"GATE written {eid} event_source=live")
                return json.dumps({
                    "status": "ok", "event_id": eid,
                    "when": datetime.datetime.now().isoformat(),
                    "storage": "gate/sqlite(in-process)",
                }, ensure_ascii=False)
            if result.get("status") == "error":
                # Validationは通ったがevents行が成立しなかった場合。
                # 検証で弾かれた(gate_rejected)のとは原因が異なるため区別して返す。
                # 署名も生成されていない(Event creation integrity boundary)。
                auto_log(name, args, f"GATE write failed: {result.get('errors')}")
                return json.dumps({"status": "gate_error", "errors": result.get("errors", []),
                                   "note": "events行が成立しなかったため署名も生成されていない"},
                                  ensure_ascii=False)
            auto_log(name, args, f"GATE rejected: {result.get('errors')}")
            return json.dumps({"status": "gate_rejected", "errors": result.get("errors", [])},
                              ensure_ascii=False)

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
        return json.dumps({"name": "mocka-memory-caliber", "version": "1.6.0-vps"}), 200, {"Content-Type": "application/json"}
    body   = request.get_json()
    method = body.get("method", "")
    req_id = body.get("id")
    params = body.get("params", {})
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "mocka-memory-caliber", "version": "1.6.0-vps"}}
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
    db_ok, db_detail       = _check_gate_db_alignment()
    schema_ok, schema_note = _check_events_schema()
    return json.dumps({
        "status": "ok", "version": "1.6.0-vps", "port": 5002,
        "overview_exists": OVERVIEW_PATH.exists(),
        "todo_exists": TODO_PATH.exists(),
        "storage": "sqlite", "event_count": len(rows),
        "tools": [t["name"] for t in TOOLS],
        "public_url": PUBLIC_URL,
        # Unified Event Entry の成立条件（v1.6.0）
        "event_gate": {
            "available": GATE_AVAILABLE,
            "root": str(GATE_ROOT) if GATE_ROOT else None,
            "import_error": GATE_IMPORT_ERROR,
            "write_path": "phi_os.event_gate.process_event",
            "event_source": "live",
            "db_aligned": db_ok,
            "db_detail": db_detail,
            "events_schema_ok": schema_ok,
            "events_schema_note": schema_note,
        },
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

def _startup_banner(port):
    print(f"MoCKA MCP Server v1.6.0-vps -- http://localhost:{port}/mcp")
    print(f"MOCKA_HOME: {BASE}")
    print(f"DB: {DB_PATH}")
    print(f"Tools: {len(TOOLS)}")
    if GATE_AVAILABLE:
        db_ok, db_detail = _check_gate_db_alignment()
        print(f"Event Gate: phi_os.event_gate.process_event (root={GATE_ROOT})")
        print(f"Gate DB aligned: {'OK' if db_ok else 'NG'} -- {db_detail}")
        schema_ok, schema_note = _check_events_schema()
        print(f"events schema: {'OK' if schema_ok else 'NG'} -- {schema_note}")
    else:
        print(f"Event Gate: UNAVAILABLE -- {GATE_IMPORT_ERROR}")
        print("  -> mocka_write_event is disabled (直接INSERTへのフォールバックは行わない)")


# gunicorn等でimportされる場合も起動状態を必ずログに残す（記録なき起動を作らない）
_startup_banner(int(os.environ.get("MOCKA_PORT", 5002)))

if __name__ == "__main__":
    port = int(os.environ.get("MOCKA_PORT", 5002))
    app.run(host="127.0.0.1", port=port, debug=False)
