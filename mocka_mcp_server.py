"""
mocka_mcp_server.py v1.2.0
MoCKA Memory Caliber -- MCP Server
"""

import json, csv, hashlib, datetime, re
from pathlib import Path
from flask import Flask, request
from flask_cors import CORS

BASE           = Path(r"C:\Users\sirok\MoCKA")
OVERVIEW_PATH  = Path(r"C:\Users\sirok\MOCKA_OVERVIEW.json")
TODO_PATH      = Path(r"C:\Users\sirok\MOCKA_TODO.json")
KNOWLEDGE_GATE = BASE / "data"
EVENTS_CSV     = BASE / "data" / "events.csv"
FALLBACK_EVENTS = [BASE / "data" / "events.csv", BASE / "events.csv"]
AUTO_LOG_CSV   = BASE / "data" / "claude_sessions.csv"

EVENTS_FIELDS = ["event_id","when","who_actor","what_type","where_component","where_path","why_purpose","how_trigger","channel_type","lifecycle_phase","risk_level","category_ab","target_class","title","short_summary","before_state","after_state","change_type","impact_scope","impact_result","related_event_id","trace_id","free_note"]

app = Flask(__name__)
CORS(app, origins="*")

def find_events_csv():
    if EVENTS_CSV.exists(): return EVENTS_CSV
    for p in FALLBACK_EVENTS:
        if p.exists(): return p
    return None

def read_events(n=20):
    path = find_events_csv()
    if not path: return []
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f): rows.append(dict(row))
    return rows[-n:]

def search_events(query):
    path = find_events_csv()
    if not path: return []
    q = query.lower()
    with open(path, encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f) if any(q in str(v).lower() for v in r.values())]

def search_knowledge_gate(query):
    q = query.lower()
    results = []
    if not KNOWLEDGE_GATE.exists(): return results
    for md in KNOWLEDGE_GATE.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8")
            if q in text.lower():
                for i, line in enumerate(text.splitlines()):
                    if q in line.lower():
                        snippet = "\n".join(text.splitlines()[max(0,i-1):i+3])
                        results.append({"file": str(md.relative_to(BASE)), "snippet": snippet.strip()})
                        break
        except: pass
    return results

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
    return h.hexdigest()

def next_event_id():
    today = datetime.date.today().strftime("%Y%m%d")
    events = read_events(9999)
    pattern = re.compile(rf"E{today}_(\d+)")
    nums = [int(m.group(1)) for e in events for m in [pattern.search(e.get("event_id",""))] if m]
    return f"E{today}_{(max(nums)+1 if nums else 1):03d}"

def auto_log(tool_name, args, result_summary):
    try:
        ts = datetime.datetime.now().isoformat()
        row = {"timestamp": ts, "tool": tool_name, "args": json.dumps(args, ensure_ascii=False)[:200], "result": str(result_summary)[:200]}
        exists = AUTO_LOG_CSV.exists()
        with open(AUTO_LOG_CSV, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=row.keys())
            if not exists: w.writeheader()
            w.writerow(row)
    except: pass

TOOLS = [
    {"name":"mocka_get_overview","description":"MOCKA_OVERVIEW.json を返す","inputSchema":{"type":"object","properties":{},"required":[]}},
    {"name":"mocka_get_todo","description":"MOCKA_TODO.json を返す。全AIが現在地とTODOを即理解できる","inputSchema":{"type":"object","properties":{},"required":[]}},
    {"name":"mocka_update_todo","description":"TODO_IDのstatusを更新する","inputSchema":{"type":"object","properties":{"id":{"type":"string"},"status":{"type":"string"},"note":{"type":"string"}},"required":["id","status"]}},
    {"name":"mocka_list_events","description":"events.csv 最新N件","inputSchema":{"type":"object","properties":{"n":{"type":"integer","default":20}},"required":[]}},
    {"name":"mocka_read_event","description":"IDでイベント取得","inputSchema":{"type":"object","properties":{"id":{"type":"string"}},"required":["id"]}},
    {"name":"mocka_search","description":"全文検索","inputSchema":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}},
    {"name":"mocka_write_event","description":"イベント追記","inputSchema":{"type":"object","properties":{"title":{"type":"string"},"description":{"type":"string"},"tags":{"type":"string"},"author":{"type":"string","default":"Claude"},"why_purpose":{"type":"string"},"how_trigger":{"type":"string"}},"required":["title","description"]}},
    {"name":"mocka_seal","description":"SHA-256ハッシュ","inputSchema":{"type":"object","properties":{},"required":[]}}
]

def execute_tool(name, args):
    try:
        if name == "mocka_get_overview":
            if not OVERVIEW_PATH.exists(): return json.dumps({"error": f"not found: {OVERVIEW_PATH}"})
            result = json.loads(OVERVIEW_PATH.read_text(encoding="utf-8-sig"))
            auto_log(name, args, "overview loaded")
            return json.dumps(result, ensure_ascii=False, indent=2)
        elif name == "mocka_get_todo":
            if not TODO_PATH.exists(): return json.dumps({"error": f"not found: {TODO_PATH}"})
            result = json.loads(TODO_PATH.read_text(encoding="utf-8-sig"))
            auto_log(name, args, f"todo loaded")
            return json.dumps(result, ensure_ascii=False, indent=2)
        elif name == "mocka_update_todo":
            if not TODO_PATH.exists(): return json.dumps({"error": f"not found: {TODO_PATH}"})
            todo_id = args.get("id","")
            new_status = args.get("status","")
            note = args.get("note","")
            data = json.loads(TODO_PATH.read_text(encoding="utf-8-sig"))
            updated = False
            for item in data.get("todos", []):
                if item.get("id") == todo_id:
                    item["status"] = new_status
                    if note: item["note"] = note
                    item["updated_at"] = datetime.datetime.now().isoformat()
                    if new_status == "完了":
                        item["completed_at"] = datetime.date.today().isoformat()
                        data.setdefault("completed", []).append(item)
                        data["todos"].remove(item)
                    updated = True
                    break
            if not updated: return json.dumps({"error": f"{todo_id} not found"})
            data["meta"]["updated"] = datetime.date.today().isoformat()
            data["meta"]["updated_by"] = "Claude"
            TODO_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            auto_log(name, args, f"updated {todo_id} -> {new_status}")
            return json.dumps({"status":"ok","id":todo_id,"new_status":new_status}, ensure_ascii=False)
        elif name == "mocka_list_events":
            events = read_events(int(args.get("n", 20)))
            auto_log(name, args, f"{len(events)} events")
            return json.dumps({"count": len(events), "events": events}, ensure_ascii=False, indent=2)
        elif name == "mocka_read_event":
            eid = args.get("id","")
            found = [e for e in read_events(9999) if e.get("event_id") == eid]
            auto_log(name, args, "found" if found else "not found")
            return json.dumps(found[0] if found else {"error": "not found"}, ensure_ascii=False, indent=2)
        elif name == "mocka_search":
            q = args.get("query","")
            ev = search_events(q)
            kg = search_knowledge_gate(q)
            auto_log(name, args, f"events:{len(ev)} kg:{len(kg)}")
            return json.dumps({"query":q,"events_hits":ev,"knowledge_gate_hits":kg}, ensure_ascii=False, indent=2)
        elif name == "mocka_write_event":
            path = find_events_csv() or EVENTS_CSV
            path.parent.mkdir(parents=True, exist_ok=True)
            eid = next_event_id()
            ts = datetime.datetime.now().isoformat()
            row = {f: "" for f in EVENTS_FIELDS}
            row["event_id"]       = eid
            row["when"]           = ts
            row["who_actor"]      = args.get("author", "Claude")
            row["what_type"]      = "claude_mcp"
            row["where_component"]= "mcp_caliber"
            row["where_path"]     = "mocka_mcp_server.py"
            row["why_purpose"]    = args.get("why_purpose", "")
            row["how_trigger"]    = args.get("how_trigger", "")
            row["title"]          = args.get("title", "")
            row["short_summary"]  = args.get("description", "")
            row["free_note"]      = args.get("tags", "")
            row["lifecycle_phase"]= "in_operation"
            row["risk_level"]     = "normal"
            row["channel_type"]   = "mcp"
            with open(path, "a", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
                w.writerow(row)
            auto_log(name, args, f"written {eid}")
            return json.dumps({"status":"ok","event_id":eid,"when":ts}, ensure_ascii=False)
        elif name == "mocka_seal":
            path = find_events_csv()
            if not path: return json.dumps({"error":"events.csv not found"})
            h = sha256_file(path)
            result = {"sha256":h,"file":str(path),"timestamp":datetime.datetime.now().isoformat()}
            auto_log(name, args, h[:16])
            return json.dumps(result, ensure_ascii=False)
        return json.dumps({"error":f"unknown tool: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@app.route("/mcp", methods=["GET","POST"])
def mcp_endpoint():
    if request.method == "GET":
        return json.dumps({"name":"mocka-memory-caliber","version":"1.2.0"}), 200, {"Content-Type":"application/json"}
    body = request.get_json()
    method, req_id, params = body.get("method",""), body.get("id"), body.get("params",{})
    if method == "initialize":
        result = {"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"mocka-memory-caliber","version":"1.2.0"}}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        result = {"content":[{"type":"text","text":execute_tool(params.get("name",""),params.get("arguments",{}))}],"isError":False}
    else:
        return json.dumps({"jsonrpc":"2.0","id":req_id,"error":{"code":-32601,"message":f"unknown: {method}"}}), 200, {"Content-Type":"application/json"}
    return json.dumps({"jsonrpc":"2.0","id":req_id,"result":result}, ensure_ascii=False), 200, {"Content-Type":"application/json"}

@app.route("/.well-known/oauth-protected-resource", defaults={"subpath":""})
@app.route("/.well-known/oauth-protected-resource/<path:subpath>")
def oauth_resource(subpath):
    return json.dumps({"resource":"https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev","authorization_servers":[]}), 200, {"Content-Type":"application/json"}

@app.route("/.well-known/oauth-authorization-server")
def oauth_server():
    return json.dumps({}), 200, {"Content-Type":"application/json"}

@app.route("/register", methods=["POST"])
def register():
    return json.dumps({"client_id":"mocka-mcp","client_secret":"none"}), 200, {"Content-Type":"application/json"}

@app.route("/health")
def health():
    ep = find_events_csv()
    return json.dumps({"status":"ok","version":"1.2.0","port":5002,"overview_exists":OVERVIEW_PATH.exists(),"todo_exists":TODO_PATH.exists(),"events_csv":str(ep) if ep else None,"tools":[t["name"] for t in TOOLS]}, ensure_ascii=False), 200, {"Content-Type":"application/json"}

if __name__ == "__main__":
    print("MoCKA MCP Server v1.2.0 -- http://localhost:5002/mcp")
    print(f"Tools: {len(TOOLS)}")
    app.run(host="0.0.0.0", port=5002, debug=False)
