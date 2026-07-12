"""
mocka_mcp_server.py v1.5.0
MoCKA Memory Caliber -- MCP Server
変更点: mocka_add_todo追加（新規TODO登録をClaudeから直接実行可能に）
"""

import json, csv, hashlib, datetime, re, sqlite3, unicodedata, os, sys, time, secrets
from pathlib import Path
from dotenv import load_dotenv
import requests
from flask import Flask, request, Response
from flask_cors import CORS

load_dotenv()
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# GL1~GL7 Governance Pipeline (MoCKA 3.0)
sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA\structural")))
from event_recency import valid_when_ts_clause  # noqa: E402

# TODO_428/DC_20260709_001: 一次データ駆動のCurrent View Generator(additive、mocka_get_overviewの
# 既存戻り値は変更せずcurrent_viewキーとして追加するのみ)。
sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA\scripts\state")))
try:
    import overview_current_generator as _overview_current_gen
except Exception as _ocg_err:
    print(f"[WARN] overview_current_generator unavailable (current_view will be omitted): {_ocg_err}", flush=True)
    _overview_current_gen = None
try:
    from governance_pipeline import GovernancePipeline, READ_ONLY_TOOLS
    _governance = GovernancePipeline()
except Exception as _gov_err:
    print(f"[ERROR] Governance Pipeline unavailable (Fail Closed for governed tools): {_gov_err}", flush=True)
    _governance = None
    READ_ONLY_TOOLS = {
        "mocka_get_overview", "mocka_get_essence", "mocka_get_todo", "mocka_list_events",
        "mocka_read_event", "mocka_search", "mocka_get_incidents", "mocka_get_guidelines",
        "mocka_get_command_center", "mocka_check_utf8",
    }

# KN-004 Registry (六層構造) — 既存TODO管理(status/contract_status)とは完全に独立したドメイン
REGISTRY_MODULE_PATH = Path(r"C:\Users\sirok\MoCKA\PlanningCaliber\workshop\registry_kn004")
sys.path.insert(0, str(REGISTRY_MODULE_PATH))
try:
    import registry_store
except Exception as _registry_err:
    print(f"[ERROR] registry_store unavailable: {_registry_err}", flush=True)
    registry_store = None

# TODO_385: status(通常5値)とcontract_status(Architecture Contract系9語彙)を
# 別軸のenumに分離（TODO_384は両者を1つの集合に混在させていたが、設計成果物/基準仕様等
# 「紐付く契約のライフサイクル状態」と通常タスクの「進行度」は意味が異なるため分離する）
TODO_STATUS_ENUM = {"未着手", "進行中", "完了", "保留", "廃止"}

CONTRACT_STATUS_ENUM = {
    "DECISION_RECORDED", "DONE_LOCKED", "ALTERNATE_IMPLEMENTED", "SPEC_OBSOLETE",
    "SUPERSEDED", "CLOSED", "確定", "Phase3停止中(設計待ち)", "調査済み",
}

MOCKA_ENDPOINT = os.environ.get("MOCKA_ENDPOINT", "")
if not MOCKA_ENDPOINT:
    print("[ERROR] 環境変数 MOCKA_ENDPOINT が未設定です。.env.example を参照して設定してください。", flush=True)

BASE           = Path(r"C:\Users\sirok\MoCKA")
OVERVIEW_PATH  = Path(r"C:\Users\sirok\MOCKA_OVERVIEW.json")
TODO_PATH      = Path(r"C:\Users\sirok\MoCKA\data\MOCKA_TODO_ACTIVE.json")
KNOWLEDGE_GATE = BASE / "data"
EVENTS_CSV     = BASE / "data" / "events.csv"  # 廃止済み（互換保持のみ）
FALLBACK_EVENTS = [BASE / "data" / "events.csv", BASE / "events.csv"]
AUTO_LOG_CSV   = BASE / "data" / "claude_sessions.csv"
DB_PATH        = BASE / "data" / "mocka_events.db"

# TODO_361: Decision Ledger Reconnection — DECISION_LEDGER_SCHEMA_v1.md(docs/mocka3/)準拠
DECISIONS_DIR       = BASE / "data" / "decisions"
DECISION_LEDGER_PATH = DECISIONS_DIR / "decision_ledger.jsonl"

# Sprint3: Integrity Classification — 3層ログ構造(Decision=判断/Integrity=異常/
# Reconnection=修復)のうち「何が壊れていたか」を記録する層。Decision Ledgerと
# 対称構造(JSONL、append-only、3ツール)。
INTEGRITY_DIR                = BASE / "data" / "integrity"
INTEGRITY_CLASSIFICATION_PATH = INTEGRITY_DIR / "integrity_classification.jsonl"

# [PHI-OS GATE v1 2026-06-16] Phase 3 — GATEプロキシ設定
GATE_URL        = "http://localhost:5000/api/gate/event"
SESSION_ID      = "SESSION_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
_DEFAULT_ACTOR  = "Claude-code-sonnet-4-6"  # who_actor未指定時のデフォルト

# ============================================================
# SQLite接続ヘルパー（文字化け防御ゲート付き）
# ============================================================
def _get_db():
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    # claude_sessionsテーブルを自動作成（初回のみ）
    con.execute("""CREATE TABLE IF NOT EXISTS claude_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        tool TEXT,
        args TEXT,
        result_summary TEXT
    )""")
    con.commit()
    return con

def _sanitize(text):
    """U+FFFD・BOM・????パターンを除去して安全なUTF-8文字列を返す"""
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    text = text.lstrip("\ufeff")
    text = text.replace("\ufffd", "")
    # ????パターン検出（3個以上の?が連続）
    if text.count("?") >= 3 and len(text.replace("?","").strip()) < len(text) * 0.5:
        return ""  # データ欠損行は空文字で安全化
    return text

def _db_read_events(n=None):
    """SQLiteからevents読み込み（旧CSV互換形式で返す）"""
    try:
        con = _get_db()
        cur = con.cursor()
        integrity_filter = "(data_integrity IN ('normal', 'alt_schema_intentional') OR data_integrity IS NULL)"
        if n:
            cur.execute(f"SELECT * FROM events WHERE {integrity_filter} ORDER BY rowid DESC LIMIT ?", (n,))
        else:
            cur.execute(f"SELECT * FROM events WHERE {integrity_filter} ORDER BY rowid")
        cols = [d[0] for d in cur.description]
        rows = []
        for r in cur.fetchall():
            row = dict(zip(cols, r))
            # when_ts → when の互換マッピング
            if "when_ts" in row and "when" not in row:
                row["when"] = row["when_ts"]
            rows.append(row)
        con.close()
        return rows
    except Exception as e:
        print(f"[MCP] db_read_events error: {e}")
        return []

app = Flask(__name__)
CORS(app, origins="*")

@app.after_request
def add_ngrok_header(response):
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

def find_events_csv():
    if EVENTS_CSV.exists(): return EVENTS_CSV
    for p in FALLBACK_EVENTS:
        if p.exists(): return p
    return None

def read_events(n=20):
    # CSV廃止済み → SQLite参照
    rows = _db_read_events()
    return rows[-n:] if n else rows

def search_events(query):
    # CSV廃止済み → SQLite参照
    q = query.lower()
    rows = _db_read_events()
    PRIMARY_FIELDS = ["title", "short_summary", "description", "free_note", "why_purpose", "who_actor", "what_type", "how_trigger"]
    scored = []
    for r in rows:
        score = 0
        for f in PRIMARY_FIELDS:
            val = str(r.get(f, "")).lower()
            if q in val:
                score += 10
                if val.startswith(q):
                    score += 5
        if r.get("what_type") == "user_voice":
            score = max(0, score - 8)
        if score > 0:
            scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:30]]

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

def _update_working_context_live(title: str, why_purpose: str, ai: str = "",
                                  event_id: str = "", tags: str = "") -> None:
    # CONTEXT_RUNTIME_CONNECTION_INSTRUCTIONS.md P0/P1 + P3指示書 STEP2:
    # mocka_write_event発火の唯一の集約点でWorkingContextを更新し、
    # 定期Snapshot(15分 or 100件)トリガーを評価し、Context Runtime側へイベントを伝播する。
    # next_event_id()には一切触れない。mocka_events.dbへの新規書き込みも行わない
    # （event_runtime_log.jsonへの追記のみ）。失敗してもイベント書込自体は妨げない。
    try:
        import sys as _sys
        _repo_root = str(Path(r"C:\Users\sirok\MoCKA"))
        if _repo_root not in _sys.path:
            _sys.path.insert(0, _repo_root)
        from phi_os.context.working_context import WorkingContext
        from phi_os.context.context_scheduler import maybe_snapshot
        from phi_os.context.context_runtime import emit_event_to_context_runtime
        WorkingContext.live_update(
            current_task=title, current_goal=why_purpose, current_ai=ai,
        )
        tags_lower = (tags or "").lower()
        if "change_start" in tags_lower:
            event_type = "CHANGE_START"
        elif "decision" in tags_lower:
            event_type = "DECISION_RECORD"
        elif "incident" in tags_lower:
            event_type = "INCIDENT_REGISTER"
        else:
            event_type = "CHANGE_DONE"
        emit_event_to_context_runtime(
            event_type=event_type, event_id=event_id,
            payload={"title": title, "why_purpose": why_purpose, "tags": tags},
        )
        maybe_snapshot()
    except Exception:
        pass

def _write_reopen_event(todo_id: str, new_status: str, reason: str) -> str:
    # TODO_442案(a): completedからの差し戻しを訂正イベントとしてGATE経由でappendする。
    # Event ledgerのappend-only原則を守るため、差し戻し自体を必ず新規イベントとして
    # 記録し、既存イベントの書き換え・削除は一切行わない。GATE書込に失敗した場合は
    # 例外を上位(mocka_update_todo側)へ伝播させ、記録なき差し戻しを許可しない。
    title = f"REOPEN: {todo_id} completedから{new_status}へ差し戻し"
    desc  = f"対象: {todo_id}\n差し戻し後status: {new_status}\n理由: {reason}"
    gate_payload = {
        "who_actor":       _DEFAULT_ACTOR,
        "who_role":        "executor",
        "who_session":     SESSION_ID,
        "what_type":       "claude_mcp",
        "what_title":      title,
        "where_path":      "mocka_mcp_server.py",
        "where_component": "mcp_caliber",
        "why_purpose":     reason[:80],
        "how_trigger":     "mocka_update_todo(reopen)",
        "after_state":     desc[:200],
        "description":     desc,
        "tags":            f"todo_reopen,{todo_id},append_only,todo_442",
    }
    try:
        r = requests.post(GATE_URL, json=gate_payload, timeout=5)
        if r.status_code == 201:
            return r.json().get("event_id", "?")
        raise RuntimeError(f"GATE rejected {r.status_code}: {r.text[:120]}")
    except requests.exceptions.ConnectionError:
        import sys as _sys
        _repo_root = str(Path(r"C:\Users\sirok\MoCKA"))
        if _repo_root not in _sys.path:
            _sys.path.insert(0, _repo_root)
        from phi_os.event_gate import process_event as _gate_process_event
        result = _gate_process_event(gate_payload, event_source="direct_allowed:recovery")
        if result["status"] == "ok":
            return result["event_id"]
        raise RuntimeError(f"GATE offline fallback rejected: {result.get('errors')}")

def auto_log(tool_name, args, result_summary):
    # CSV廃止済み → SQLite(claude_sessionsテーブル)に記録
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
    except: pass

def load_todo():
    return json.loads(TODO_PATH.read_text(encoding="utf-8-sig"))

# TODO_448: 書き込み監査ログ(save_todo等API経由の書込みのみ記録されるため、
# 記録が無いのに内容が変化していれば非API経路での書込みが疑われる、という
# 消去法的な検知を可能にする。IC_20260712_002/TODO_414(非API経路での配列
# 迷入が疑われ、実際の書込み主体をevents.dbから特定できなかった事例)への対策)
WRITE_AUDIT_PATH = BASE / "data" / "tic" / "write_audit_log.jsonl"

def _log_write_audit(target_path, content, actor=None):
    try:
        WRITE_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp":  datetime.datetime.now().isoformat(),
            "target_path": str(target_path),
            "session_id": SESSION_ID,
            "actor":      actor or _DEFAULT_ACTOR,
            "source":     "api",  # このログ自体がsave_todo経由でのみ生成されるためAPI経路確定
            "sha256":     hashlib.sha256(content.encode("utf-8")).hexdigest()[:16],
        }
        with open(WRITE_AUDIT_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass  # 監査ログの失敗で本処理(TODO書込み)自体を止めない

def verify_write_provenance():
    """TODO_PATHの現在ハッシュとwrite_audit_log.jsonlの最終記録ハッシュを比較する。
    不一致であれば、save_todo()を経由しない書込み(非API経路)が発生した可能性を示す。"""
    if not WRITE_AUDIT_PATH.exists():
        return {"status": "no_audit_log"}
    last = None
    with open(WRITE_AUDIT_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                last = json.loads(line)
            except Exception:
                pass
    if last is None:
        return {"status": "no_valid_entries"}
    current_content = TODO_PATH.read_text(encoding="utf-8-sig")
    current_hash = hashlib.sha256(current_content.encode("utf-8")).hexdigest()[:16]
    match = (current_hash == last.get("sha256"))
    return {
        "status": "match" if match else "mismatch_possible_non_api_write",
        "last_logged_hash": last.get("sha256"),
        "current_hash": current_hash,
        "last_logged_actor": last.get("actor"),
        "last_logged_session_id": last.get("session_id"),
        "last_logged_at": last.get("timestamp"),
    }

def save_todo(data, actor=None):
    data["meta"]["updated"] = datetime.date.today().isoformat()
    data["meta"]["updated_by"] = "Claude"
    tmp_path = TODO_PATH.with_suffix(".json.tmp")
    content = json.dumps(data, ensure_ascii=False, indent=2)
    tmp_path.write_text(content, encoding="utf-8")
    os.replace(tmp_path, TODO_PATH)
    _log_write_audit(TODO_PATH, content, actor=actor)

# ===== TODO_361: Decision Ledger（DECISION_LEDGER_SCHEMA_v1.md準拠） =====
DECISION_STATUS_ENUM = {"Active", "Superseded", "Withdrawn"}

def _read_decisions():
    """decision_ledger.jsonlの全行を読む（append-only。同一decision_idの複数行は
    末尾のものを最新状態として扱う。壊れた行はスキップし件数のみ数える）。"""
    if not DECISION_LEDGER_PATH.exists():
        return [], 0
    records = []
    broken = 0
    with open(DECISION_LEDGER_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                broken += 1
    return records, broken

def _next_decision_id():
    """DC_YYYYMMDD_NNN形式で当日分の次番号を採番する（欠番可・重複禁止）。"""
    today = datetime.date.today().strftime("%Y%m%d")
    records, _ = _read_decisions()
    prefix = f"DC_{today}_"
    used = [
        int(r["decision_id"][len(prefix):])
        for r in records
        if isinstance(r.get("decision_id"), str) and r["decision_id"].startswith(prefix)
        and r["decision_id"][len(prefix):].isdigit()
    ]
    n = (max(used) + 1) if used else 1
    return f"{prefix}{n:03d}"

def _append_decision(record):
    """decision_ledger.jsonlへ1行追記する（append-only、既存行は変更しない）。"""
    DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    with open(DECISION_LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

# ===== Sprint3: Integrity Classification（State x Type分類体系） =====
STATE_ENUM = {"Failure", "Risk", "Unknown"}

TYPE_ENUM_BY_STATE = {
    "Failure": {
        "Transfer Failure", "Synchronization Failure", "Adoption Failure",
        "Exposure Failure", "Runtime Divergence", "Topology Failure",
    },
    "Risk": {"Mirror Risk", "Legacy Residue", "Intent Conflict"},
    "Unknown": {"Not Verified", "Evidence Missing"},
}

CLASSIFICATION_STATUS_ENUM = {"Open", "Resolved", "Superseded"}

def _read_classifications():
    """integrity_classification.jsonlの全行を読む（append-only。壊れた行は
    スキップし件数のみ数える）。"""
    if not INTEGRITY_CLASSIFICATION_PATH.exists():
        return [], 0
    records = []
    broken = 0
    with open(INTEGRITY_CLASSIFICATION_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                broken += 1
    return records, broken

def _next_classification_id():
    """IC_YYYYMMDD_NNN形式で当日分の次番号を採番する（欠番可・重複禁止）。"""
    today = datetime.date.today().strftime("%Y%m%d")
    records, _ = _read_classifications()
    prefix = f"IC_{today}_"
    used = [
        int(r["classification_id"][len(prefix):])
        for r in records
        if isinstance(r.get("classification_id"), str) and r["classification_id"].startswith(prefix)
        and r["classification_id"][len(prefix):].isdigit()
    ]
    n = (max(used) + 1) if used else 1
    return f"{prefix}{n:03d}"

def _append_classification(record):
    """integrity_classification.jsonlへ1行追記する（append-only、既存行は変更しない）。"""
    INTEGRITY_DIR.mkdir(parents=True, exist_ok=True)
    with open(INTEGRITY_CLASSIFICATION_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

TOOLS = [
    {"name":"mocka_get_overview","description":"MOCKA_OVERVIEW.json を返す","inputSchema":{"type":"object","properties":{},"required":[]}},
    {"name":"mocka_get_essence","description":"lever_essence.jsonの最新INCIDENT/PHILOSOPHY/OPERATIONを返す","inputSchema":{"type":"object","properties":{},"required":[]}},
    {"name":"mocka_get_todo","description":"MOCKA_TODO_ACTIVE.json を返す(ACTIVE層のみ。LOCKED/ARCHIVE層は対象外)。全AIが現在地とTODOを即理解できる","inputSchema":{"type":"object","properties":{},"required":[]}},
    {"name":"mocka_add_todo","description":"新規TODOをMOCKA_TODO_ACTIVE.jsonに追加する。IDが既存の場合はエラー。","inputSchema":{"type":"object","properties":{"id":{"type":"string"},"title":{"type":"string"},"status":{"type":"string","default":"未着手"},"contract_status":{"type":"string","description":"Architecture Contract系9語彙のいずれか。通常TODOには指定しない（省略時はフィールド自体を付与しない）"},"priority":{"type":"string","default":"中"},"category":{"type":"string"},"description":{"type":"string"},"assigned_to":{"type":"string"},"note":{"type":"string"},"reference_event":{"type":"string"}},"required":["id","title"]}},
    {"name":"mocka_update_todo","description":"TODO_IDのフィールドを部分更新する（PATCH動作）。status/contract_status/noteを個別に更新可。未指定フィールドは既存値を保持。completedへ移動済みのTODOは直接編集不可(TODO_442)。reason付きでstatusを完了以外へ指定した場合のみ差し戻し(todosへ復帰)を許可する。差し戻し後は通常のPATCH経路で再度完了にすることも可能(往復は正常業務)。","inputSchema":{"type":"object","properties":{"id":{"type":"string"},"status":{"type":"string","description":"省略時は既存値を保持する"},"contract_status":{"type":"string","description":"Architecture Contract系9語彙のいずれか。省略時は既存値を保持する"},"note":{"type":"string","description":"省略時は既存値を保持する"},"reason":{"type":"string","description":"completed状態のTODOを差し戻す場合のみ必須。3文字以上、実質的な理由が必要"}},"required":["id"]}},
    {"name":"mocka_list_events","description":"events.csv 最新N件","inputSchema":{"type":"object","properties":{"n":{"type":"integer","default":20}},"required":[]}},
    {"name":"mocka_read_event","description":"IDでイベント取得","inputSchema":{"type":"object","properties":{"id":{"type":"string"}},"required":["id"]}},
    {"name":"mocka_search","description":"全文検索","inputSchema":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}},
    {"name":"mocka_write_event","description":"イベント追記","inputSchema":{"type":"object","properties":{"title":{"type":"string"},"description":{"type":"string"},"tags":{"type":"string"},"author":{"type":"string","description":"必須: 正確なAI識別子 e.g. Claude-sonnet-4-6, gpt-4o, script:xxx"},"why_purpose":{"type":"string"},"how_trigger":{"type":"string"}},"required":["title","description","author"]}},
    {"name":"mocka_seal","description":"SHA-256ハッシュ","inputSchema":{"type":"object","properties":{},"required":[]}},
    {"name":"mocka_get_incidents","description":"インシデント履歴を取得する（カテゴリ別フィルタ可）","inputSchema":{"type":"object","properties":{"category":{"type":"string","default":""},"limit":{"type":"integer","default":20}},"required":[]}},
    {"name":"mocka_get_guidelines","description":"guidelines.json（行動指針）を返す","inputSchema":{"type":"object","properties":{},"required":[]}},
    {"name":"mocka_get_command_center","description":"COMMAND CENTER（localhost:5000）の現在状態を取得する","inputSchema":{"type":"object","properties":{},"required":[]}},
    {"name":"mocka_check_utf8","description":"指定ファイルのUTF-8妥当性を検証する（BOM・cp932・制御文字検出）","inputSchema":{"type":"object","properties":{"filepath":{"type":"string"}},"required":["filepath"]}},
    {"name":"mocka_registry_get","description":"MoCKA Registry(KN-004六層構造: Identity/Atlas/Reference/Classification/Lifecycle/Metadata)の現在の全データを返す。既存TODO管理とは完全に独立したドメイン。envを明示しない場合は必ずtest環境を参照する(deny-by-default)。","inputSchema":{"type":"object","properties":{"env":{"type":"string","enum":["prod","test"],"default":"test","description":"prod=本番データ, test=検証用データ(既定)。本番を見る場合は明示的にprodを指定すること。"}},"required":[]}},
    {"name":"mocka_registry_add","description":"MoCKA Registryに1件レコードを追加する。書き込み前にスキーマ検証(additionalProperties制約含む)を通過しない場合は拒否される。source_record(PHL参照)は各層で必須。envを明示しない場合は必ずtest環境に書き込む(deny-by-default、本番誤爆防止)。","inputSchema":{"type":"object","properties":{"layer":{"type":"string","enum":["identity","atlas","reference","classification","lifecycle","metadata"]},"record":{"type":"object","description":"追加するレコード本体。各層のスキーマに準拠すること"},"env":{"type":"string","enum":["prod","test"],"default":"test","description":"prod=本番データへ書き込み, test=検証用データへ書き込み(既定)。本番へ書く場合は明示的にprodを指定すること。"}},"required":["layer","record"]}},
    {"name":"mocka_registry_current_state","description":"指定target_idの現在状態をLifecycleの最新レコードから動的に導出して返す(currentフラグは持たない設計のため毎回計算)。envを明示しない場合は必ずtest環境を参照する。","inputSchema":{"type":"object","properties":{"target_id":{"type":"string"},"env":{"type":"string","enum":["prod","test"],"default":"test","description":"prod=本番データ, test=検証用データ(既定)。"}},"required":["target_id"]}},
    {"name":"mocka_decision_write","description":"Decision Ledger(DECISION_LEDGER_SCHEMA_v1.md準拠)に1件記録する。decision_idは省略時DC_YYYYMMDD_NNN形式で自動採番。alternatives必須(却下案が無い場合はoption:N/Aの1件を入れる)。同一決定の状態更新(supersede等)は新規行として追記する(append-only)。","inputSchema":{"type":"object","properties":{"decision_id":{"type":"string","description":"省略時は自動採番"},"title":{"type":"string"},"context":{"type":"string"},"alternatives":{"type":"array","items":{"type":"object","properties":{"option":{"type":"string"},"rejected_reason":{"type":"string"}},"required":["option","rejected_reason"]}},"decision":{"type":"string"},"rationale":{"type":"string"},"impact":{"type":"string"},"related_events":{"type":"array","items":{"type":"string"},"default":[]},"related_documents":{"type":"array","items":{"type":"string"},"default":[]},"approved_by":{"type":"string"},"status":{"type":"string","enum":["Active","Superseded","Withdrawn"],"default":"Active"},"supersedes":{"type":"string"}},"required":["title","context","alternatives","decision","rationale","impact","approved_by"]}},
    {"name":"mocka_decision_get","description":"decision_idを指定してDecision Ledgerから1件取得する(同一IDの複数行がある場合は最新行を返す)。","inputSchema":{"type":"object","properties":{"decision_id":{"type":"string"}},"required":["decision_id"]}},
    {"name":"mocka_decision_list","description":"Decision Ledgerの全件を返す(decision_id毎に最新行のみ、新しい順)。statusでフィルタ可。","inputSchema":{"type":"object","properties":{"status":{"type":"string","enum":["Active","Superseded","Withdrawn"]}},"required":[]}},
    {"name":"mocka_integrity_write","description":"Integrity Classification(State x Type分類体系)に1件記録する。判断・評価・改善提案は含めない、構造的事実の分類のみ。classification_idは省略時IC_YYYYMMDD_NNN形式で自動採番。","inputSchema":{"type":"object","properties":{"classification_id":{"type":"string","description":"省略時は自動採番"},"title":{"type":"string"},"state":{"type":"string","enum":["Failure","Risk","Unknown"]},"type":{"type":"string","description":"stateに応じたTypeを1つ指定(Failure: Transfer/Synchronization/Adoption/Exposure Failure・Runtime/Topology Failure。Risk: Mirror Risk/Legacy Residue/Intent Conflict。Unknown: Not Verified/Evidence Missing)"},"boundary":{"type":"string","description":"任意。元となった6境界分類(設計->実装 等)への参照タグ"},"description":{"type":"string"},"detection_method":{"type":"string","description":"再現可能な検出手順(例: SQLite直接照合、diff比較、HTTP実測)"},"impact_scope":{"type":"string"},"related_events":{"type":"array","items":{"type":"string"},"default":[]},"related_documents":{"type":"array","items":{"type":"string"},"default":[]},"discovered_by":{"type":"string"},"status":{"type":"string","enum":["Open","Resolved","Superseded"],"default":"Open"},"supersedes":{"type":"string"}},"required":["title","state","type","description","detection_method","impact_scope","discovered_by"]}},
    {"name":"mocka_integrity_get","description":"classification_idを指定してIntegrity Classificationから1件取得する(同一IDの複数行がある場合は最新行を返す)。","inputSchema":{"type":"object","properties":{"classification_id":{"type":"string"}},"required":["classification_id"]}},
    {"name":"mocka_integrity_list","description":"Integrity Classificationの全件を返す(classification_id毎に最新行のみ)。state/type/statusでフィルタ可。","inputSchema":{"type":"object","properties":{"state":{"type":"string","enum":["Failure","Risk","Unknown"]},"type":{"type":"string"},"status":{"type":"string","enum":["Open","Resolved","Superseded"]}},"required":[]}}
]

def execute_tool(name, args):
    try:
        if _governance is None:
            # Fail Closed: Governance Pipeline自体が初期化できていない場合、
            # READ_ONLY_TOOLS以外は安全側で実行を停止する。
            if name not in READ_ONLY_TOOLS:
                return json.dumps({
                    "error": "GL_FAIL_CLOSED",
                    "reason": "Governance Pipeline unavailable; governed tool blocked",
                }, ensure_ascii=False)
        else:
            try:
                decision = _governance.before_tool(name, args)
                if not decision.allowed:
                    return json.dumps({
                        "error": "GL7_EXECUTION_BLOCKED",
                        "reason": decision.reason,
                        "thinking_mode": decision.thinking_mode,
                    }, ensure_ascii=False)
            except Exception as _gov_call_err:
                # Fail Closed: before_tool()自体が例外を投げた場合も
                # READ_ONLY_TOOLS以外は安全側で実行を停止する。
                print(f"[ERROR] Governance before_tool failed (Fail Closed): {_gov_call_err}", flush=True)
                if name not in READ_ONLY_TOOLS:
                    return json.dumps({
                        "error": "GL_FAIL_CLOSED",
                        "reason": f"before_tool() raised: {_gov_call_err}",
                    }, ensure_ascii=False)

        if name == "mocka_get_overview":
            if not OVERVIEW_PATH.exists(): return json.dumps({"error": f"not found: {OVERVIEW_PATH}"})
            result = json.loads(OVERVIEW_PATH.read_text(encoding="utf-8-sig"))
            # TODO_428/DC_20260709_001: 一次データから機械的に再集計したCurrent Viewをadditiveに付加する。
            # 既存キー(what_is_mocka/repositories/products等)は一切変更しない。生成失敗時はエラー情報を
            # current_view内に格納し、本体の戻り値には影響させない(フォールバック)。
            if _overview_current_gen is not None:
                try:
                    result["current_view"] = _overview_current_gen.generate()
                except Exception as _cv_err:
                    result["current_view"] = {"error": f"overview_current_generator.generate() failed: {_cv_err}"}
            else:
                result["current_view"] = {"error": "overview_current_generator module unavailable at import time"}
            auto_log(name, args, "overview loaded (with current_view)")
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif name == "mocka_get_essence":
            import urllib.request
            res = urllib.request.urlopen("http://127.0.0.1:5000/get_latest_dna")
            data = json.loads(res.read())
            return json.dumps(data.get("ping", {}).get("ESSENCE_SUMMARY", {}), ensure_ascii=False, indent=2)

        elif name == "mocka_get_todo":
            if not TODO_PATH.exists(): return json.dumps({"error": f"not found: {TODO_PATH}"})
            result = load_todo()
            auto_log(name, args, "todo loaded")
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif name == "mocka_add_todo":
            if not TODO_PATH.exists(): return json.dumps({"error": f"not found: {TODO_PATH}"})
            todo_id = args.get("id", "").strip()
            title   = args.get("title", "").strip()
            if not todo_id or not title:
                return json.dumps({"error": "id and title are required"})
            add_status = args.get("status", "未着手")
            if add_status not in TODO_STATUS_ENUM:
                return json.dumps({"error": f"invalid status: {add_status!r}. allowed: {sorted(TODO_STATUS_ENUM)}"}, ensure_ascii=False)
            add_contract_status = args.get("contract_status", "")
            if add_contract_status and add_contract_status not in CONTRACT_STATUS_ENUM:
                return json.dumps({"error": f"invalid contract_status: {add_contract_status!r}. allowed: {sorted(CONTRACT_STATUS_ENUM)}"}, ensure_ascii=False)
            data = load_todo()
            all_ids = [t.get("id") for t in data.get("todos", [])] + [t.get("id") for t in data.get("completed", [])]
            if todo_id in all_ids:
                return json.dumps({"error": f"{todo_id} already exists"})
            new_todo = {
                "id":              todo_id,
                "title":           title,
                "status":          add_status,
                "priority":        args.get("priority", "中"),
                "category":        args.get("category", ""),
                "description":     args.get("description", ""),
                "assigned_to":     args.get("assigned_to", "Claude"),
                "note":            args.get("note", ""),
                "reference_event": args.get("reference_event", ""),
                "created_at":      datetime.datetime.now().isoformat()
            }
            if add_contract_status:                # 未指定時はキー自体を付与しない(TODO_385設計案1.3案A)
                new_todo["contract_status"] = add_contract_status
            data["todos"].append(new_todo)
            save_todo(data)
            auto_log(name, args, f"added {todo_id}")
            print(f"[MCP] mocka_add_todo: {todo_id} added")
            return json.dumps({"status": "ok", "id": todo_id, "action": "added"}, ensure_ascii=False)

        elif name == "mocka_update_todo":
            if not TODO_PATH.exists(): return json.dumps({"error": f"not found: {TODO_PATH}"})
            todo_id    = args.get("id", "")
            new_status = args.get("status", "")   # 空文字 = 未指定 → 既存値を保持
            new_contract_status = args.get("contract_status", "")  # 空文字 = 未指定 → 既存値を保持
            note       = args.get("note", "")
            reason     = args.get("reason", "").strip()  # TODO_442: completed差し戻し時のみ必須
            if new_status and new_status not in TODO_STATUS_ENUM:
                return json.dumps({"error": f"invalid status: {new_status!r}. allowed: {sorted(TODO_STATUS_ENUM)}"}, ensure_ascii=False)
            if new_contract_status and new_contract_status not in CONTRACT_STATUS_ENUM:
                return json.dumps({"error": f"invalid contract_status: {new_contract_status!r}. allowed: {sorted(CONTRACT_STATUS_ENUM)}"}, ensure_ascii=False)
            data = load_todo()
            updated = False
            effective_status = ""
            reopen_event_id = None
            # 通常経路: ACTIVE(todos)配列内を検索(既存動作、無変更)
            for item in data.get("todos", []):
                if item.get("id") == todo_id:
                    if new_status:                 # 指定された場合のみ更新（PATCH動作）
                        item["status"] = new_status
                    if new_contract_status:        # 指定された場合のみ更新（PATCH動作）
                        item["contract_status"] = new_contract_status
                    if note:                       # 指定された場合のみ更新（PATCH動作）
                        item["note"] = note
                    item["updated_at"] = datetime.datetime.now().isoformat()
                    effective_status = item.get("status", "")
                    if new_status == "完了":
                        item["completed_at"] = datetime.date.today().isoformat()
                        data.setdefault("completed", []).append(item)
                        data["todos"].remove(item)
                    updated = True
                    break

            # TODO_442案(a): todosで見つからない場合のみ、completed配列からの差し戻し
            # を試みる。completedからの直接編集はこの1経路のみに限定し、通常のnote
            # 追記のみ・completedのまま等は一切許可しない(completed維持のまま編集
            # させる案(b)はHuman Gateで却下済み、DC参照)。差し戻し=todos配列へ復帰
            # した後は、上のtodosループが通常通り処理するため、再度"完了"へ戻す
            # (再完了)ことも当然可能。この差し戻し→再完了の往復は正常業務である。
            if not updated:
                for item in data.get("completed", []):
                    if item.get("id") == todo_id:
                        if not new_status or new_status == "完了":
                            return json.dumps({
                                "error": "completed item requires a non-完了 status "
                                         "to reopen (note-only or re-completing a completed "
                                         "item directly is not allowed; TODO_442)"
                            }, ensure_ascii=False)
                        if len(reason) < 3 or reason.strip(".-") == "" or reason.lower() in ("n/a", "na"):
                            return json.dumps({
                                "error": "reason is required to reopen a completed item "
                                         "(non-trivial, min 3 chars; TODO_442)"
                            }, ensure_ascii=False)
                        reopen_event_id = _write_reopen_event(todo_id, new_status, reason)
                        data["completed"].remove(item)
                        item["status"] = new_status
                        if new_contract_status:
                            item["contract_status"] = new_contract_status
                        if note:
                            item["note"] = note
                        item.pop("completed_at", None)
                        item["updated_at"] = datetime.datetime.now().isoformat()
                        data.setdefault("todos", []).append(item)
                        effective_status = new_status
                        updated = True
                        break

            if not updated: return json.dumps({"error": f"{todo_id} not found"})
            save_todo(data)
            auto_log(name, args, f"updated {todo_id} -> {effective_status}")
            result = {"status": "ok", "id": todo_id, "new_status": effective_status}
            if reopen_event_id:
                result["reopen_event_id"] = reopen_event_id
            return json.dumps(result, ensure_ascii=False)

        elif name == "mocka_list_events":
            events = read_events(int(args.get("n", 20)))
            auto_log(name, args, f"{len(events)} events")
            return json.dumps({"count": len(events), "events": events}, ensure_ascii=False, indent=2)

        elif name == "mocka_read_event":
            eid = args.get("id", "")
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
            # [PHI-OS GATE v1 2026-06-16] Phase 3 — GATEプロキシ経由で書き込む
            # GL7-VALIDATION-MISSING-BUG是正: title/description/authorはツール定義上
            # required(352行台のTOOLS登録"required":["title","description","author"])
            # であるにもかかわらず、空文字が自動補填されvalidate()まで隠蔽されていた。
            # レガシー値("Claude"/"claude")の自動正規化は維持しつつ、本当に空の場合は
            # 検知してREJECTする（対応候補どおり、フォールバックを「補完」から
            # 「検知して拒否」へ変更）。
            _title = args.get("title", "").strip()
            _desc = args.get("description", "").strip()
            _actor_raw = args.get("author", "").strip()
            if not _title:
                return json.dumps({"status": "gate_rejected", "errors": ["title is required (empty)"]}, ensure_ascii=False)
            if not _desc:
                return json.dumps({"status": "gate_rejected", "errors": ["description is required (empty)"]}, ensure_ascii=False)
            if not _actor_raw:
                return json.dumps({"status": "gate_rejected", "errors": ["author is required (empty)"]}, ensure_ascii=False)
            # 未指定検知はここまでで完了済み。レガシー値のみ Claude-code-{version} で自動補填
            _actor = _DEFAULT_ACTOR if _actor_raw in ("Claude", "claude") else _actor_raw
            gate_payload = {
                "who_actor":       _actor,
                "who_role":        "executor",
                "who_session":     SESSION_ID,
                "what_type":       "claude_mcp",
                "what_title":      _title,
                "where_path":      "mocka_mcp_server.py",
                "where_component": "mcp_caliber",
                "why_purpose":     args.get("why_purpose", "") or _desc[:80] or _title,
                "how_trigger":     args.get("how_trigger", "") or "mcp_tool_call",
                "after_state":     _desc[:200] or _title,
                "description":     _desc,
                "tags":            args.get("tags", ""),
            }
            try:
                r = requests.post(GATE_URL, json=gate_payload, timeout=5)
                if r.status_code == 201:
                    body = r.json()
                    eid  = body.get("event_id", "?")
                    auto_log(name, args, f"GATE written {eid} event_source=live")
                    _update_working_context_live(_title, gate_payload["why_purpose"], _actor,
                                                  event_id=eid, tags=gate_payload["tags"])
                    return json.dumps({"status": "ok", "event_id": eid,
                                       "when": datetime.datetime.now().isoformat(),
                                       "storage": "gate/sqlite"}, ensure_ascii=False)
                else:
                    # GATEがエラーを返した場合 — rejectedとして呼び出し元に返す
                    auto_log(name, args, f"GATE rejected {r.status_code}: {r.text[:80]}")
                    return json.dumps({"status": "gate_rejected", "errors": r.json().get("errors", []),
                                       "gate_status": r.status_code}, ensure_ascii=False)
            except requests.exceptions.ConnectionError:
                # GATEプロセスがHTTP応答不能な場合のフォールバック。
                # Phase5-2.1 Unified Event Entry: 生SQL直接INSERTは廃止し、
                # phi_os.event_gate.process_event()をインプロセスで直接呼び出す
                # ことで、HTTP経路と完全に同じValidation/Signature/HashChainを
                # 経由させる（事後のmigrate_event_integrity.py補完を不要にする）。
                import sys as _sys
                _repo_root = str(Path(r"C:\Users\sirok\MoCKA"))
                if _repo_root not in _sys.path:
                    _sys.path.insert(0, _repo_root)
                from phi_os.event_gate import process_event as _gate_process_event
                result = _gate_process_event(gate_payload, event_source="direct_allowed:recovery")
                if result["status"] == "ok":
                    eid = result["event_id"]
                    auto_log(name, args, f"GATE offline in-process fallback {eid}")
                    _update_working_context_live(_title, gate_payload["why_purpose"], _actor,
                                                  event_id=eid, tags=gate_payload["tags"])
                    return json.dumps({"status": "ok", "event_id": eid,
                                       "when": datetime.datetime.now().isoformat(),
                                       "storage": "gate/sqlite(in-process)"}, ensure_ascii=False)
                else:
                    auto_log(name, args, f"GATE offline fallback rejected: {result.get('errors')}")
                    return json.dumps({"status": "gate_rejected", "errors": result.get("errors", [])},
                                       ensure_ascii=False)

        elif name == "mocka_seal":
            # CSV廃止済み → SQLite全件JSONハッシュ
            import hashlib as _hl
            rows = _db_read_events()
            payload = json.dumps(rows, ensure_ascii=False, sort_keys=True).encode("utf-8")
            h = _hl.sha256(payload).hexdigest()
            result = {"sha256": h, "source": "sqlite", "event_count": len(rows),
                      "timestamp": datetime.datetime.now().isoformat()}
            auto_log(name, args, h[:16])
            return json.dumps(result, ensure_ascii=False)

        elif name == "mocka_get_incidents":
            category = args.get("category", "")
            limit = int(args.get("limit", 20))
            con = _get_db()
            try:
                if category:
                    rows = con.execute(
                        f"""SELECT event_id, when_ts, title, short_summary, free_note
                           FROM events
                           WHERE (what_type LIKE '%INCIDENT%' OR what_type LIKE '%DANGER%'
                                  OR what_type LIKE '%VIOLATION%' OR what_type LIKE '%MATAKA%'
                                  OR title LIKE '%INCIDENT%' OR title LIKE '%またか%'
                                  OR free_note LIKE ?)
                             AND {valid_when_ts_clause()}
                           ORDER BY when_ts DESC LIMIT ?""",
                        (f"%{category}%", limit)
                    ).fetchall()
                else:
                    rows = con.execute(
                        f"""SELECT event_id, when_ts, title, short_summary, free_note
                           FROM events
                           WHERE (what_type LIKE '%INCIDENT%' OR what_type LIKE '%DANGER%'
                                  OR what_type LIKE '%VIOLATION%' OR what_type LIKE '%MATAKA%'
                                  OR title LIKE '%INCIDENT%' OR title LIKE '%またか%'
                                  OR title LIKE '%CLAIM%')
                             AND {valid_when_ts_clause()}
                           ORDER BY when_ts DESC LIMIT ?""",
                        (limit,)
                    ).fetchall()
                result = [dict(r) for r in rows]
            finally:
                con.close()
            auto_log(name, args, f"{len(result)} incidents")
            return json.dumps({"incidents": result, "count": len(result)}, ensure_ascii=False, indent=2)

        elif name == "mocka_get_guidelines":
            guidelines_path = BASE / "data" / "guidelines.json"
            if not guidelines_path.exists():
                return json.dumps({"error": "guidelines.json not found", "path": str(guidelines_path)}, ensure_ascii=False)
            data = json.loads(guidelines_path.read_text(encoding="utf-8-sig"))
            top = data[:20] if isinstance(data, list) else data
            total = len(data) if isinstance(data, list) else 1
            auto_log(name, args, f"guidelines loaded total={total}")
            return json.dumps({"guidelines": top, "total": total}, ensure_ascii=False, indent=2)

        elif name == "mocka_get_command_center":
            import urllib.request
            results = {}
            endpoints = {
                "loop_status": "http://localhost:5000/loop/status",
                "risk": "http://localhost:5000/risk/recommendation",
                "heinrich": "http://localhost:5000/heinrich/status",
            }
            for ep_name, url in endpoints.items():
                try:
                    with urllib.request.urlopen(url, timeout=3) as resp:
                        results[ep_name] = json.loads(resp.read().decode("utf-8"))
                except Exception as e:
                    results[ep_name] = {"error": str(e)}
            auto_log(name, args, "command center fetched")
            return json.dumps(results, ensure_ascii=False, indent=2)

        elif name == "mocka_check_utf8":
            filepath = args.get("filepath", "")
            p = Path(filepath)
            if not p.exists():
                return json.dumps({"ok": False, "error": f"File not found: {filepath}"}, ensure_ascii=False)
            raw = p.read_bytes()
            result = {
                "filepath": filepath,
                "size_bytes": len(raw),
                "has_bom": raw[:3] == b'\xef\xbb\xbf',
                "ok": True,
                "issues": []
            }
            if result["has_bom"]:
                result["issues"].append("BOM detected (U+FEFF at start)")
                result["ok"] = False
            try:
                text = raw.decode("utf-8")
                result["encoding"] = "utf-8"
                result["line_count"] = text.count('\n')
            except UnicodeDecodeError as e:
                result["ok"] = False
                result["encoding"] = "NOT UTF-8"
                result["issues"].append(f"UTF-8 decode error at byte {e.start}: {e.reason}")
                try:
                    raw.decode("cp932")
                    result["issues"].append("File appears to be cp932 encoded")
                except Exception:
                    result["issues"].append("Cannot decode as cp932 either")
            auto_log(name, args, f"utf8 check ok={result['ok']}")
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif name == "mocka_get_command_center":
            try:
                import urllib.request
                with urllib.request.urlopen("http://localhost:5000/loop/status", timeout=3) as r:
                    loop_data = json.loads(r.read().decode())
                with urllib.request.urlopen("http://localhost:5000/risk/recommendation", timeout=3) as r:
                    risk_data = json.loads(r.read().decode())
                result = {"loop": loop_data, "risk": risk_data, "status": "ok"}
            except Exception as e:
                result = {"error": str(e), "note": "COMMAND CENTER(5000)未起動の可能性"}
            auto_log(name, args, "command_center fetched")
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif name == "mocka_search_incidents":
            query = args.get("query", "")
            limit = int(args.get("limit", 10))
            conn = _get_db()
            cur = conn.cursor()
            integrity_filter = "(data_integrity IN ('normal', 'alt_schema_intentional') OR data_integrity IS NULL)"
            if query:
                cur.execute(
                    "SELECT event_id, when_ts, title, short_summary, risk_level FROM events "
                    f"WHERE {integrity_filter} "
                    "AND (LOWER(risk_level) IN ('incident','danger','critical','high')) "
                    "AND (title LIKE ? OR short_summary LIKE ? OR event_id LIKE ?) "
                    f"AND {valid_when_ts_clause()} "
                    "ORDER BY when_ts DESC LIMIT ?",
                    (f"%{query}%", f"%{query}%", f"%{query}%", limit)
                )
            else:
                cur.execute(
                    "SELECT event_id, when_ts, title, short_summary, risk_level FROM events "
                    f"WHERE {integrity_filter} "
                    "AND LOWER(risk_level) IN ('incident','danger','critical','high') "
                    f"AND {valid_when_ts_clause()} "
                    "ORDER BY when_ts DESC LIMIT ?",
                    (limit,)
                )
            rows = cur.fetchall()
            conn.close()
            incidents = [{"id": r[0], "when": r[1], "title": r[2], "summary": r[3], "risk": r[4]} for r in rows]
            auto_log(name, args, f"{len(incidents)} incidents found")
            return json.dumps(incidents, ensure_ascii=False, indent=2)

        elif name == "mocka_get_phl":
            import os as _os
            BASE_DIR = _os.path.dirname(_os.path.abspath(__file__))
            try:
                with open(_os.path.join(BASE_DIR, "interface", "lever_essence.json"), encoding="utf-8") as f:
                    philosophy = json.load(f).get("PHILOSOPHY", "")
            except Exception as e:
                philosophy = f"error: {e}"
            phl = {
                "philosophy": philosophy,
                "phl_principles": [
                    "不確実性下でのAI動作を制約するPersistent History Layer",
                    "セッションをまたいで文脈を保持・再注入する",
                    "希釈(dilution)に対してPHL再注入で回復する",
                    "SPPとペアで機能: SPP=沈黙禁止 / PHL=文脈保持"
                ],
                "zenodo_doi": "10.5281/zenodo.19606271"
            }
            auto_log(name, args, "phl loaded")
            return json.dumps(phl, ensure_ascii=False, indent=2)

        elif name == "mocka_get_spp":
            spp = {
                "spp_principles": [
                    "Silence Prohibition Protocol: 不確実な状況でも沈黙してはならない",
                    "AIは必ず何らかの応答・警告・報告をする義務がある",
                    "DANGER/CRITICAL検知時は即座にアラートを発する",
                    "Human Gateなしに重要判断を黙って実行してはならない"
                ],
                "governance_rules": [
                    "全AIインタラクションはmocka_write_eventで記録必須",
                    "ファイル変更前後にCHANGE_START/CHANGE_DONE記録",
                    "記録なき作業はMoCKAとして存在しない(E20260516_023)",
                    "AIを信じるな、システムで縛れ"
                ],
                "aies_paper": "Submission 282 / mocka_paper_FINAL_v9_20260509.pdf"
            }
            auto_log(name, args, "spp loaded")
            return json.dumps(spp, ensure_ascii=False, indent=2)

        elif name == "mocka_registry_get":
            if registry_store is None:
                return json.dumps({"error": "registry_store unavailable"}, ensure_ascii=False)
            env = args.get("env", "test")
            if env not in ("prod", "test"):
                return json.dumps({"error": f"invalid env: {env!r}"}, ensure_ascii=False)
            result = registry_store.get_registry(env=env)
            auto_log(name, args, f"registry loaded (env={env})")
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif name == "mocka_registry_add":
            if registry_store is None:
                return json.dumps({"error": "registry_store unavailable"}, ensure_ascii=False)
            layer  = args.get("layer", "")
            record = args.get("record", {})
            env    = args.get("env", "test")
            if layer not in ("identity", "atlas", "reference", "classification", "lifecycle", "metadata"):
                return json.dumps({"error": f"invalid layer: {layer!r}"}, ensure_ascii=False)
            if env not in ("prod", "test"):
                return json.dumps({"error": f"invalid env: {env!r}"}, ensure_ascii=False)
            try:
                added = registry_store.add_record(layer, record, env=env)
            except registry_store.RegistryValidationError as e:
                return json.dumps({"error": "REGISTRY_VALIDATION_FAILED", "reason": str(e)}, ensure_ascii=False)
            auto_log(name, args, f"added to {layer} (env={env})")
            print(f"[MCP] mocka_registry_add: layer={layer} env={env} added")
            return json.dumps({"status": "ok", "layer": layer, "env": env, "record": added}, ensure_ascii=False)

        elif name == "mocka_registry_current_state":
            if registry_store is None:
                return json.dumps({"error": "registry_store unavailable"}, ensure_ascii=False)
            target_id = args.get("target_id", "")
            env       = args.get("env", "test")
            if env not in ("prod", "test"):
                return json.dumps({"error": f"invalid env: {env!r}"}, ensure_ascii=False)
            result = registry_store.get_current_state(target_id, env=env)
            auto_log(name, args, f"current_state computed (env={env})" if result else f"not found (env={env})")
            return json.dumps(result if result else {"error": "not found"}, ensure_ascii=False, indent=2)

        elif name == "mocka_decision_write":
            title    = args.get("title", "").strip()
            context  = args.get("context", "").strip()
            decision = args.get("decision", "").strip()
            rationale = args.get("rationale", "").strip()
            impact   = args.get("impact", "").strip()
            approved_by = args.get("approved_by", "").strip()
            alternatives = args.get("alternatives", [])
            if not all([title, context, decision, rationale, impact, approved_by]):
                return json.dumps({"error": "title/context/decision/rationale/impact/approved_by は全て必須(DECISION_LEDGER_SCHEMA_v1.md準拠)"}, ensure_ascii=False)
            if not isinstance(alternatives, list) or not alternatives:
                return json.dumps({"error": "alternatives は1件以上の配列が必須(却下案が無い場合は option:N/A の1件を入れる)"}, ensure_ascii=False)
            for alt in alternatives:
                if not isinstance(alt, dict) or "option" not in alt or "rejected_reason" not in alt:
                    return json.dumps({"error": "alternatives の各要素は option/rejected_reason を持つオブジェクトである必要がある"}, ensure_ascii=False)
            status = args.get("status", "Active")
            if status not in DECISION_STATUS_ENUM:
                return json.dumps({"error": f"invalid status: {status!r}. allowed: {sorted(DECISION_STATUS_ENUM)}"}, ensure_ascii=False)
            decision_id = args.get("decision_id", "").strip() or _next_decision_id()
            approved_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            record = {
                "decision_id":       decision_id,
                "title":             title,
                "context":           context,
                "alternatives":      alternatives,
                "decision":          decision,
                "rationale":         rationale,
                "impact":            impact,
                "related_events":    args.get("related_events", []),
                "related_documents": args.get("related_documents", []),
                "approved_by":       approved_by,
                "approved_at":       approved_at,
                "supersedes":        args.get("supersedes") or None,
                "superseded_by":     None,
                "status":            status,
            }
            _append_decision(record)
            # companion event（mocka_write_eventと同一GATE経路をtags付きで再利用。
            # what_type=DECISION_MADEのenum拡張はapp.py側GATEのスコープ外のため今回は追加しない）
            event_id = None
            try:
                gate_payload = {
                    "who_actor":       args.get("approved_by", _DEFAULT_ACTOR),
                    "who_role":        "executor",
                    "who_session":     SESSION_ID,
                    "what_type":       "claude_mcp",
                    "what_title":      f"[DECISION_MADE] {decision_id}: {title}",
                    "where_path":      "mocka_mcp_server.py",
                    "where_component": "mcp_caliber",
                    "why_purpose":     rationale[:80] or title,
                    "how_trigger":     "mcp_tool_call",
                    "after_state":     decision[:200] or title,
                    "description":     f"decision_id={decision_id}\ncontext={context}\ndecision={decision}\nrationale={rationale}\nimpact={impact}",
                    "tags":            f"decision_ledger,{decision_id},{status}",
                }
                r = requests.post(GATE_URL, json=gate_payload, timeout=5)
                if r.status_code == 201:
                    event_id = r.json().get("event_id")
            except Exception as _companion_err:
                print(f"[MCP] mocka_decision_write companion event failed: {_companion_err}", flush=True)
            auto_log(name, args, f"decision written {decision_id}")
            return json.dumps({"status": "ok", "decision_id": decision_id, "event_id": event_id}, ensure_ascii=False)

        elif name == "mocka_decision_get":
            decision_id = args.get("decision_id", "")
            records, _ = _read_decisions()
            matches = [r for r in records if r.get("decision_id") == decision_id]
            auto_log(name, args, "found" if matches else "not found")
            return json.dumps(matches[-1] if matches else {"error": "not found"}, ensure_ascii=False, indent=2)

        elif name == "mocka_decision_list":
            status_filter = args.get("status", "")
            records, broken = _read_decisions()
            latest = {}
            for r in records:
                did = r.get("decision_id")
                if did:
                    latest[did] = r  # 後勝ち(append-only前提で末尾が最新)
            result = list(latest.values())
            if status_filter:
                result = [r for r in result if r.get("status") == status_filter]
            result.sort(key=lambda r: r.get("decision_id", ""), reverse=True)
            auto_log(name, args, f"{len(result)} decisions (broken_lines={broken})")
            return json.dumps({"count": len(result), "broken_lines": broken, "decisions": result}, ensure_ascii=False, indent=2)

        elif name == "mocka_integrity_write":
            title       = args.get("title", "").strip()
            state       = args.get("state", "")
            itype       = args.get("type", "")
            description = args.get("description", "").strip()
            detection_method = args.get("detection_method", "").strip()
            impact_scope     = args.get("impact_scope", "").strip()
            discovered_by    = args.get("discovered_by", "").strip()
            if not all([title, state, itype, description, detection_method, impact_scope, discovered_by]):
                return json.dumps({"error": "title/state/type/description/detection_method/impact_scope/discovered_by は全て必須"}, ensure_ascii=False)
            if state not in STATE_ENUM:
                return json.dumps({"error": f"invalid state: {state!r}. allowed: {sorted(STATE_ENUM)}"}, ensure_ascii=False)
            if itype not in TYPE_ENUM_BY_STATE.get(state, set()):
                return json.dumps({"error": f"invalid type {itype!r} for state {state!r}. allowed: {sorted(TYPE_ENUM_BY_STATE.get(state, set()))}"}, ensure_ascii=False)
            status = args.get("status", "Open")
            if status not in CLASSIFICATION_STATUS_ENUM:
                return json.dumps({"error": f"invalid status: {status!r}. allowed: {sorted(CLASSIFICATION_STATUS_ENUM)}"}, ensure_ascii=False)
            classification_id = args.get("classification_id", "").strip() or _next_classification_id()
            discovered_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            record = {
                "classification_id": classification_id,
                "title":              title,
                "state":              state,
                "type":               itype,
                "boundary":           args.get("boundary") or None,
                "description":        description,
                "detection_method":   detection_method,
                "impact_scope":       impact_scope,
                "related_events":     args.get("related_events", []),
                "related_documents":  args.get("related_documents", []),
                "discovered_at":      discovered_at,
                "discovered_by":      discovered_by,
                "status":             status,
                "supersedes":         args.get("supersedes") or None,
                "superseded_by":      None,
            }
            _append_classification(record)
            auto_log(name, args, f"classification written {classification_id}")
            return json.dumps({"status": "ok", "classification_id": classification_id}, ensure_ascii=False)

        elif name == "mocka_integrity_get":
            classification_id = args.get("classification_id", "")
            records, _ = _read_classifications()
            matches = [r for r in records if r.get("classification_id") == classification_id]
            auto_log(name, args, "found" if matches else "not found")
            return json.dumps(matches[-1] if matches else {"error": "not found"}, ensure_ascii=False, indent=2)

        elif name == "mocka_integrity_list":
            state_filter  = args.get("state", "")
            type_filter   = args.get("type", "")
            status_filter = args.get("status", "")
            records, broken = _read_classifications()
            latest = {}
            for r in records:
                cid = r.get("classification_id")
                if cid:
                    latest[cid] = r
            result = list(latest.values())
            if state_filter:
                result = [r for r in result if r.get("state") == state_filter]
            if type_filter:
                result = [r for r in result if r.get("type") == type_filter]
            if status_filter:
                result = [r for r in result if r.get("status") == status_filter]
            result.sort(key=lambda r: r.get("classification_id", ""), reverse=True)
            auto_log(name, args, f"{len(result)} classifications (broken_lines={broken})")
            return json.dumps({"count": len(result), "broken_lines": broken, "classifications": result}, ensure_ascii=False, indent=2)

        return json.dumps({"error": f"unknown tool: {name}"})

    except Exception as e:
        return json.dumps({"error": str(e)})

@app.route("/mcp", methods=["GET", "POST"])
def mcp_endpoint():
    if request.method == "GET":
        return json.dumps({"name": "mocka-memory-caliber", "version": "1.3.0"}), 200, {"Content-Type": "application/json"}
    body   = request.get_json()
    method = body.get("method", "")
    req_id = body.get("id")
    params = body.get("params", {})
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "mocka-memory-caliber", "version": "1.3.0"}}
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
    return json.dumps({"resource": MOCKA_ENDPOINT or "https://localhost:5002", "authorization_servers": []}), 200, {"Content-Type": "application/json"}

@app.route("/.well-known/oauth-authorization-server")
def oauth_server():
    return json.dumps({}), 200, {"Content-Type": "application/json"}

@app.route("/register", methods=["POST"])
def register():
    return json.dumps({"client_id": "mocka-mcp", "client_secret": "none"}), 200, {"Content-Type": "application/json"}

@app.route("/api/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_to_app(subpath):
    """port5000 (app.py / Living Memory API) へのリバースプロキシ（TODO_291）"""
    target_url = f"http://localhost:5000/api/{subpath}"

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={k: v for k, v in request.headers if k.lower() != 'host'},
            json=request.get_json(silent=True),
            params=request.args,
            timeout=10,
        )
        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json'),
        )
    except Exception as e:
        return json.dumps({"error": f"proxy error: {str(e)}"}, ensure_ascii=False), 502, {"Content-Type": "application/json"}


@app.route("/health")
def health():
    rows = _db_read_events()
    return json.dumps({"status": "ok", "version": "1.5.0", "port": 5002,
                       "overview_exists": OVERVIEW_PATH.exists(), "todo_exists": TODO_PATH.exists(),
                       "storage": "sqlite", "event_count": len(rows),
                       "tools": [t["name"] for t in TOOLS]}, ensure_ascii=False), 200, {"Content-Type": "application/json"}


# ========================================
# Agent REST API -- 全AI向け解放エンドポイント
# ========================================
@app.route("/agent/tools", methods=["GET"])
def agent_tools():
    """利用可能ツール一覧"""
    return json.dumps({"tools": [t["name"] for t in TOOLS], "usage": "POST /agent/<tool_name>"}), 200, {"Content-Type": "application/json"}

@app.route("/agent/<tool_name>", methods=["POST", "GET"])
def agent_call(tool_name):
    """全AI向け汎用ツール呼び出し
    POST: {"args": {...}}
    GET:  引数なし（get_overview等）
    """
    args = {}
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        args = body.get("args", body)
    result = execute_tool(tool_name, args)
    return result, 200, {"Content-Type": "application/json; charset=utf-8"}
if __name__ == "__main__":
    print("MoCKA MCP Server v1.5.0 -- http://localhost:5002/mcp")
    print(f"Tools: {len(TOOLS)}")
    app.run(host="0.0.0.0", port=5002, debug=False)