"""
relay_core.tests.test_session_relay

SessionRelay(時間・セッション継続層)に関するテスト。
"""

from core_kernel.event_contracts import build_event
from core_kernel.phios_integration import PrismBridge
from core_kernel.relay_core import SessionRelay


def _make_event(event_type="change_start", source_module="test_module", **kwargs):
    return build_event(
        event_type=event_type,
        source_module=source_module,
        payload={"detail": "test"},
        **kwargs,
    )


def _context():
    bridge = PrismBridge()
    bridge.initialize_prism()
    return bridge.analyze_event(_make_event())["result"].context


# ----------------------------------------------------------------------
# セッション作成
# ----------------------------------------------------------------------

def test_create_session():
    relay = SessionRelay()

    session = relay.create_session("session-1")

    assert session["session_id"] == "session-1"
    assert session["event_ids"] == []
    assert session["context_chain"] == []
    assert session["timestamps"] == []


def test_create_session_is_idempotent():
    relay = SessionRelay()

    relay.create_session("session-1")
    relay.append_context("session-1", _context())
    session_again = relay.create_session("session-1")

    # 既存セッションを破棄しない
    assert len(session_again["context_chain"]) == 1


# ----------------------------------------------------------------------
# コンテキスト追加
# ----------------------------------------------------------------------

def test_append_context_updates_chain_and_event_ids():
    relay = SessionRelay()
    relay.create_session("session-1")
    context = _context()

    session = relay.append_context("session-1", context)

    assert len(session["context_chain"]) == 1
    assert session["context_chain"][0]["context_id"] == context.context_id
    assert set(session["event_ids"]) == set(context.event_ids)
    assert len(session["timestamps"]) == 1


def test_append_context_auto_creates_session():
    relay = SessionRelay()

    session = relay.append_context("new-session", _context())

    assert session["session_id"] == "new-session"
    assert len(session["context_chain"]) == 1


def test_append_context_multiple_times_accumulates():
    relay = SessionRelay()
    relay.create_session("session-1")

    relay.append_context("session-1", _context())
    session = relay.append_context("session-1", _context())

    assert len(session["context_chain"]) == 2
    assert len(session["timestamps"]) == 2


# ----------------------------------------------------------------------
# セッション取得
# ----------------------------------------------------------------------

def test_get_session_returns_none_for_unknown():
    relay = SessionRelay()
    assert relay.get_session("does-not-exist") is None


def test_get_session_returns_snapshot():
    relay = SessionRelay()
    relay.create_session("session-1")
    relay.append_context("session-1", _context())

    session = relay.get_session("session-1")

    assert session["session_id"] == "session-1"
    assert len(session["context_chain"]) == 1


# ----------------------------------------------------------------------
# セッション統合
# ----------------------------------------------------------------------

def test_merge_sessions_combines_chains():
    relay = SessionRelay()
    relay.create_session("session-a")
    relay.create_session("session-b")
    relay.append_context("session-a", _context())
    relay.append_context("session-b", _context())

    merged = relay.merge_sessions("session-a", "session-b")

    assert len(merged["context_chain"]) == 2
    assert len(merged["timestamps"]) == 2
    assert merged["metadata"]["merged_from"] == ["session-a", "session-b"]


def test_merge_sessions_does_not_mutate_originals():
    relay = SessionRelay()
    relay.create_session("session-a")
    relay.create_session("session-b")
    relay.append_context("session-a", _context())

    relay.merge_sessions("session-a", "session-b")

    assert len(relay.get_session("session-a")["context_chain"]) == 1
    assert len(relay.get_session("session-b")["context_chain"]) == 0


def test_merge_sessions_with_unknown_session_ignores_it():
    relay = SessionRelay()
    relay.create_session("session-a")
    relay.append_context("session-a", _context())

    merged = relay.merge_sessions("session-a", "does-not-exist")

    assert len(merged["context_chain"]) == 1


def test_merge_sessions_custom_id():
    relay = SessionRelay()
    relay.create_session("session-a")
    relay.create_session("session-b")

    merged = relay.merge_sessions("session-a", "session-b", merged_session_id="merged-1")

    assert merged["session_id"] == "merged-1"
    assert "merged-1" in relay.list_sessions()


# ----------------------------------------------------------------------
# 永続化なし / Memory非干渉確認
# ----------------------------------------------------------------------

def test_session_relay_has_no_persistence_attributes():
    relay = SessionRelay()
    relay.create_session("session-1")
    relay.append_context("session-1", _context())

    # インメモリ以外の状態(ファイルパス・DB接続等)を一切持たない
    assert set(vars(relay).keys()) == {"_sessions"}


def test_session_relay_does_not_touch_memory_core():
    """SessionRelayはMemoryStoreへの参照を一切持たない。"""
    import core_kernel.relay_core.session_relay as module

    source = module.__file__
    with open(source, encoding="utf-8") as f:
        content = f.read()

    assert "memory_core" not in content
    assert "MemoryStore" not in content
