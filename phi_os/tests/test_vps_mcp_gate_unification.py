# phi_os/tests/test_vps_mcp_gate_unification.py
# deploy/mocka_mcp_server_vps.py v1.6.0 — pytest suite
#
# VPS版MCPサーバーの mocka_write_event が phi_os.event_gate.process_event() を
# 唯一のevents保存経路として使用していること(Phase5-2.1 Unified Event Entry)を
# 回帰的に保証する。
#
# 検証する制度的性質:
#   1. HTTP経路(/api/gate/event)とMCP経路が同一のDBへ収束すること
#   2. Gate分類値(_source)がHTTP経路と同一の "live" であること
#   3. Integrity署名とHash Chainが付与されること
#   4. 既存イベントDBを破壊しないこと
#   5. Gate Auditで制度違反(violation)として集計されないこと
#   6. _db_write_event()への実呼び出しがゼロであること
import ast
import importlib
import json
import sqlite3
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "interface"))
sys.path.insert(0, str(_REPO_ROOT / "deploy"))

from gate_policy import ALLOWED_SOURCE_VALUES, compute_gate_audit  # noqa: E402

VPS_SERVER_PATH = _REPO_ROOT / "deploy" / "mocka_mcp_server_vps.py"
PREEXISTING_ID = "E20260101_PREEXISTING"


def _build_production_db(db_path: Path):
    """本番と同一形状(_source CHECK制約つき)のevents表を作り、既存行を1件仕込む"""
    values = ", ".join("'%s'" % v for v in sorted(ALLOWED_SOURCE_VALUES))
    con = sqlite3.connect(str(db_path))
    con.execute("""
        CREATE TABLE events (
            event_id TEXT PRIMARY KEY, when_ts TEXT NOT NULL, who_actor TEXT,
            what_type TEXT, where_component TEXT, where_path TEXT,
            why_purpose TEXT, how_trigger TEXT, channel_type TEXT,
            lifecycle_phase TEXT, risk_level TEXT, category_ab TEXT,
            target_class TEXT, title TEXT, short_summary TEXT, before_state TEXT,
            after_state TEXT, change_type TEXT, impact_scope TEXT,
            impact_result TEXT, related_event_id TEXT, trace_id TEXT,
            free_note TEXT, _imported_at TEXT,
            _source TEXT NOT NULL CHECK (_source IN (%s)),
            ai_actor TEXT, session_id TEXT, severity INTEGER, pattern_score REAL,
            recurrence_flag INTEGER DEFAULT 0, verified_by TEXT,
            data_integrity TEXT DEFAULT 'normal', integrity_note TEXT,
            recovered_short_summary TEXT
        )
    """ % values)
    con.execute(
        "INSERT INTO events (event_id, when_ts, who_actor, title, _source) VALUES (?,?,?,?,?)",
        (PREEXISTING_ID, "2026-01-01T00:00:00+00:00", "human", "既存行", "legacy"),
    )
    con.commit()
    con.close()


@pytest.fixture
def vps_env(tmp_path, monkeypatch):
    """
    MOCKA_HOME を temp ディレクトリに向けた状態で VPS MCP サーバーを読み込む。
    戻り値: (vps module, event_gate module, db_path)
    """
    (tmp_path / "data").mkdir()
    db = tmp_path / "data" / "mocka_events.db"
    _build_production_db(db)

    monkeypatch.setenv("MOCKA_HOME", str(tmp_path))
    for mod in [m for m in list(sys.modules)
                if m.startswith("phi_os") and "tests" not in m or m == "mocka_mcp_server_vps"]:
        sys.modules.pop(mod, None)

    vps = importlib.import_module("mocka_mcp_server_vps")
    import phi_os.event_gate as eg
    yield vps, eg, db

    for mod in [m for m in list(sys.modules)
                if m.startswith("phi_os") and "tests" not in m or m == "mocka_mcp_server_vps"]:
        sys.modules.pop(mod, None)


def _write_via_mcp(vps, **overrides):
    args = {
        "title": "TEST: MCP経路からのGate書き込み",
        "description": "Unified Event Entry の検証イベント",
        "author": "Claude-opus-5",
        "why_purpose": "MCP経路がevent_gate.process_event()を経由することの検証",
        "how_trigger": "pytest",
        "tags": "test,unify",
    }
    args.update(overrides)
    return json.loads(vps.execute_tool("mocka_write_event", args))


# -- 1. パス解決 / DB_PATH二重化の防止 ----

def test_gate_is_importable(vps_env):
    vps, _, _ = vps_env
    assert vps.GATE_AVAILABLE, vps.GATE_IMPORT_ERROR


def test_server_and_gate_share_one_db(vps_env):
    vps, eg, db = vps_env
    ok, detail = vps._check_gate_db_alignment()
    assert ok, detail
    assert eg.DB_PATH == str(db)


def test_default_db_path_unchanged_without_mocka_home(monkeypatch):
    """MOCKA_HOME未設定時は従来どおりリポジトリルート基準(Windows本番の挙動不変)"""
    monkeypatch.delenv("MOCKA_HOME", raising=False)
    for mod in [m for m in list(sys.modules) if m.startswith("phi_os") and "tests" not in m]:
        sys.modules.pop(mod, None)
    import phi_os.event_gate as eg
    assert eg.DB_PATH == str(_REPO_ROOT / "data" / "mocka_events.db")


def test_events_schema_probe(vps_env):
    vps, _, _ = vps_env
    ok, note = vps._check_events_schema()
    assert ok, note


# -- 2. HTTP経路とMCP経路の収束 ----

def test_mcp_write_goes_through_gate(vps_env):
    vps, _, db = vps_env
    res = _write_via_mcp(vps)
    assert res["status"] == "ok", res
    assert res["storage"] == "gate/sqlite(in-process)"

    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM events WHERE event_id=?", (res["event_id"],)).fetchone()
    con.close()
    assert row is not None


def test_http_and_mcp_converge_on_same_db(vps_env):
    vps, eg, db = vps_env
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(eg.gate_bp)

    mcp_id = _write_via_mcp(vps)["event_id"]
    r = app.test_client().post("/api/gate/event", json={
        "who_actor": "Claude-opus-5", "who_role": "executor",
        "who_session": "SESSION_20260804_000000", "what_type": "claude_mcp",
        "what_title": "TEST: HTTP経路からのGate書き込み",
        "where_path": "test", "where_component": "test_component",
        "why_purpose": "HTTP経路がMCP経路と同一DBへ収束することの検証",
        "how_trigger": "pytest", "after_state": "written",
    })
    assert r.status_code == 201
    http_id = r.get_json()["event_id"]

    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    rows = {x["event_id"]: x for x in con.execute(
        "SELECT * FROM events WHERE event_id IN (?,?)", (mcp_id, http_id))}
    con.close()
    assert set(rows) == {mcp_id, http_id}
    # 制度差がないこと: 両経路とも同一のGate分類値になる
    assert rows[mcp_id]["_source"] == rows[http_id]["_source"] == "live"
    assert rows[mcp_id]["channel_type"] == rows[http_id]["channel_type"] == "gate"


# -- 3. event_source と MCP由来情報の保持 ----

def test_event_source_is_live_and_mcp_origin_preserved(vps_env):
    """
    event_source は "live"(HTTP経路と同一のGate分類値)。
    MCP由来はtransport属性として channel_type / where_component / how_trigger に保持する。
    """
    vps, _, db = vps_env
    eid = _write_via_mcp(vps)["event_id"]
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM events WHERE event_id=?", (eid,)).fetchone()
    con.close()

    assert row["_source"] == "live"
    assert "event_source=live" in row["free_note"]
    assert "orig_channel=mcp" in row["free_note"]          # channel_type="mcp" の記録
    assert row["where_component"] == "mcp_caliber"
    assert row["what_type"] == "claude_mcp"
    assert row["where_path"] == "mocka_mcp_server_vps.py"
    assert row["how_trigger"] == "pytest"
    assert row["session_id"].startswith("SESSION_")


def test_mcp_is_not_a_valid_source_value():
    """
    event_source="mcp" を使ってはならない根拠の固定化。
    ALLOWED_SOURCE_VALUES 外のため events._source の CHECK制約に違反する。
    """
    assert "mcp" not in ALLOWED_SOURCE_VALUES


def test_unknown_event_source_reports_error_and_leaves_no_signature(vps_env):
    """
    Event creation integrity boundary の固定化。

    許可外のevent_sourceは events._source の CHECK制約に違反する。
    INSERT OR IGNORE は違反を例外にせず握りつぶすため、以前は
    status=ok が返る一方で events行は書き込まれず、event_signatures だけが
    孤児として残っていた(Signature != Evidence の逆転)。

    修正後は status=error を返し、events行も署名も一切残さないこと。
    """
    _, eg, db = vps_env
    res = eg.process_event({
        "who_actor": "Claude-opus-5", "who_role": "executor",
        "who_session": "SESSION_20260804_000000", "what_type": "claude_mcp",
        "what_title": "TEST", "where_path": "t", "where_component": "t",
        "why_purpose": "許可外event_sourceの実挙動の固定化", "how_trigger": "pytest",
        "after_state": "x",
    }, event_source="mcp")

    assert res["status"] == "error", res
    assert res["errors"], res
    con = sqlite3.connect(str(db))
    assert con.execute("SELECT COUNT(*) FROM events WHERE event_id=?",
                       (res["event_id"],)).fetchone()[0] == 0
    # 存在しないイベントの署名を残さないこと。
    # 書き込みが成立しない場合はsignatures表自体が作られないこともあるため、
    # 表の有無を確認したうえで件数を検証する。
    has_table = con.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='event_signatures'"
    ).fetchone()[0]
    if has_table:
        assert con.execute("SELECT COUNT(*) FROM event_signatures WHERE event_id=?",
                           (res["event_id"],)).fetchone()[0] == 0
    con.close()


# -- 4. Integrity署名 / Hash Chain ----

def test_signature_and_hash_chain_applied(vps_env):
    vps, _, db = vps_env
    import phi_os.integrity as integ
    eid = _write_via_mcp(vps)["event_id"]

    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM events WHERE event_id=?", (eid,)).fetchone()
    sig = con.execute("SELECT * FROM event_signatures WHERE event_id=?", (eid,)).fetchone()
    assert sig is not None
    assert sig["algorithm"] == "sha256"
    assert sig["signature_version"] in integ.KNOWN_SIGNATURE_VERSIONS
    assert row["trace_id"] == sig["current_hash"]
    assert row["related_event_id"] == sig["previous_hash"]

    chain = integ.verify_chain(con)
    con.close()
    # 仕込んだ既存レガシー行はGate確立前のバックログなので未署名で正しい
    real = [a for a in chain["anomalies"]
            if not (a["type"] == "unsigned_event" and a["event_id"] == PREEXISTING_ID)]
    assert real == [], real


# -- 5. 既存イベントDBを壊さないこと ----

def test_existing_events_are_untouched(vps_env):
    vps, _, db = vps_env
    _write_via_mcp(vps)
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    pre = con.execute("SELECT * FROM events WHERE event_id=?", (PREEXISTING_ID,)).fetchone()
    total = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    con.close()
    assert pre is not None
    assert pre["_source"] == "legacy"
    assert pre["title"] == "既存行"
    assert total == 2  # 既存1 + 新規1


# -- 6. Gate Audit 分類 ----

def test_mcp_events_are_not_audit_violations(vps_env):
    vps, _, db = vps_env
    _write_via_mcp(vps)
    con = sqlite3.connect(str(db))
    audit = compute_gate_audit(con, "2026-06-16")
    con.close()
    assert audit["violation_events"] == 0, audit
    assert audit["real_time_events"] == 1, audit
    assert audit["gate_passthrough_rate_percent"] == 100.0, audit


# -- 7. Gate検証の伝搬 / Gate不在時の挙動 ----

@pytest.mark.parametrize("args,expected_fragment", [
    ({"title": "t", "description": "d"}, "author is required"),
    ({"title": "", "description": "d", "author": "Claude-opus-5"}, "title is required"),
    ({"title": "t", "description": "", "author": "Claude-opus-5"}, "description is required"),
])
def test_empty_required_fields_are_rejected_not_autofilled(vps_env, args, expected_fragment):
    """GL7-VALIDATION-MISSING-BUG是正: 空値は自動補填せず検知してREJECTする"""
    vps, _, db = vps_env
    res = json.loads(vps.execute_tool("mocka_write_event", args))
    assert res["status"] == "gate_rejected"
    assert any(expected_fragment in e for e in res["errors"]), res
    con = sqlite3.connect(str(db))
    assert con.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 1  # 既存行のみ
    con.close()


def test_gate_validation_errors_propagate(vps_env):
    """Gate側のREJECT(why_purpose 10文字未満)が呼び出し元まで伝わる"""
    vps, _, _ = vps_env
    res = _write_via_mcp(vps, description="短い", why_purpose="")
    assert res["status"] == "gate_rejected"
    assert any("REJECT-03" in e for e in res["errors"]), res


def test_legacy_actor_is_normalized(vps_env):
    """レガシー値 'Claude' は既定Actorへ正規化され、REJECT-01にならない"""
    vps, _, db = vps_env
    res = _write_via_mcp(vps, author="Claude")
    assert res["status"] == "ok", res
    con = sqlite3.connect(str(db))
    actor = con.execute("SELECT who_actor FROM events WHERE event_id=?",
                        (res["event_id"],)).fetchone()[0]
    con.close()
    assert actor == vps._DEFAULT_ACTOR


# -- 8. 直接INSERT経路が復活していないこと ----

def test_no_direct_insert_call_remains():
    """
    _db_write_event()/next_event_id() への実呼び出しがゼロであること。
    定義自体は残す(参照停止確認後に削除する方針)ため、AST で呼び出しのみを判定する。
    """
    tree = ast.parse(VPS_SERVER_PATH.read_text(encoding="utf-8"))
    calls = [n.func.id for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id in ("_db_write_event", "next_event_id")]
    assert calls == [], calls


def test_process_event_called_with_live_source():
    tree = ast.parse(VPS_SERVER_PATH.read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "process_event"]
    assert len(calls) == 1
    kwargs = {k.arg: getattr(k.value, "value", None) for k in calls[0].keywords}
    assert kwargs.get("event_source") == "live", kwargs
