# test_integration_lifecycle.py
"""
[シナリオ1: 正常系] 制度ライフサイクル全体のE2Eテスト

Event発生 -> Decision Ledger更新 -> Institution State更新
  -> ISE knock相当(認証) -> Adapter実行 -> ACK -> Verification -> Seal相当
"""
import json

from .. import decision_ledger
from ..state_machine import ISEState, can_transition, transition
from ..institution_contract import check_contract, KnockRequest
from ..ai_session_state import AISessionStore
from ..provider_chain import ProviderChain
from ..state_provider import StateProvider
from ..schema import ProjectStatus, Warning, TodoItem
from ..revision_manager import RevisionStore, update_institution_state
from verification.verify_api import verify


class _StubProvider(StateProvider):
    def get_project_status(self):
        return ProjectStatus(phase=1, mission="integration test", priority=["P1"])

    def get_active_warnings(self):
        return [Warning(id="W_INT", level="ACTIVE", description="integration warning")]

    def get_active_todos(self):
        return [TodoItem(id="T_INT", title="integration todo", priority="高", status="未着手")]

    def get_decision_revision(self):
        return 1

    def get_guideline_revision(self):
        return 1


def test_lifecycle_normal_scenario(tmp_path, monkeypatch):
    ledger_path = tmp_path / "decision_ledger.jsonl"
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", ledger_path)

    # 1. Event発生 -> Decision Ledger更新
    entry = decision_ledger.append_decision(
        decision_type="knock_response",
        actor="Claude",
        before="none",
        after="received",
        reason="integration_test_event",
    )
    assert "hash" in entry

    # 2. Institution State更新 (revision++)
    state_path = tmp_path / "current_state.json"
    store = RevisionStore(tmp_path / "revision_store.json")
    provider = ProviderChain([_StubProvider()])

    state1 = update_institution_state(provider, store, state_path)
    assert state1.revision == 1

    # 同じ内容で再度更新してもrevisionは増えない（差分なし）
    state2 = update_institution_state(provider, store, state_path)
    assert state2.revision == state1.revision

    with open(state_path, encoding="utf-8") as f:
        saved = json.load(f)
    assert saved["revision"] == state1.revision

    # 3. ISE knock相当: 認証・能力照合
    session_store = AISessionStore(tmp_path / "ai_session_state.json")
    req = KnockRequest(
        ai_id="Claude",
        capability=["CAP_STATE_READ"],
        role="trial",
        signature="",
        current_revision=state1.revision,
        timestamp=0,
    )
    decision = check_contract(req, session_store)
    assert decision.allowed is True

    # 4. Adapter実行 (Commission -> Execute)
    commission = {"commission_id": "C_INT_001", "task": "report current state"}
    result = {"commission_id": commission["commission_id"], "output": "ok"}

    # 5. ACK -> Decision Ledgerに記録
    ack_entry = decision_ledger.append_decision(
        decision_type="knock_response",
        actor="Claude",
        before="received",
        after="acked",
        reason="integration_test_ack",
        prev_hash=entry["hash"],
    )
    assert ack_entry["prev_hash"] == entry["hash"]

    # 6. State遷移: INITIALIZING -> ACTIVE
    assert can_transition(ISEState.INITIALIZING, ISEState.ACTIVE) is True
    new_state = transition(ISEState.INITIALIZING, ISEState.ACTIVE)
    assert new_state == ISEState.ACTIVE

    # 7. Verification: チェーン整合性確認
    result_v = verify()
    assert result_v["verified"] is True
    assert result_v["entry_count"] == 2

    # 8. Seal相当: 最終的にチェーンがOKであること
    ok, msg = decision_ledger.verify_chain()
    assert ok is True
    assert "2 entries OK" in msg
