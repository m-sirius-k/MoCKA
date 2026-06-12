# test_integration_incident.py
"""
[シナリオ2: 異常系] インシデント発生から復帰までのE2Eテスト

AI応答なし(タイムアウト) -> Incident記録 -> State DEGRADED遷移
  -> Fluid Coordinate ΔZ低下 -> Human Gate介入 -> State ACTIVE復帰 -> ΔZ回復記録
"""
import csv

from .. import decision_ledger, fluid_connector
from ..state_machine import ISEState, can_transition, transition


def test_incident_recovery_scenario(tmp_path, monkeypatch):
    ledger_path = tmp_path / "decision_ledger.jsonl"
    trajectory_path = tmp_path / "trajectory.csv"
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", ledger_path)
    monkeypatch.setattr(fluid_connector, "TRAJECTORY_PATH", trajectory_path)

    # 前提: セッションはACTIVE
    state = ISEState.ACTIVE

    # 1. AI応答なし(タイムアウト) -> Incident記録
    incident_entry = decision_ledger.append_decision(
        decision_type="incident",
        actor="ISE",
        before="awaiting_response",
        after="timeout",
        reason="AI応答タイムアウト検知",
    )
    assert incident_entry["type"] == "incident"

    # 2. State DEGRADED遷移
    assert can_transition(state, ISEState.DEGRADED) is True
    state_degraded = transition(state, ISEState.DEGRADED)
    assert state_degraded == ISEState.DEGRADED

    degrade_entry = decision_ledger.append_decision(
        decision_type="state_transition",
        actor="ISE",
        before=state.value,
        after=state_degraded.value,
        reason="incident_timeout",
        prev_hash=incident_entry["hash"],
    )

    # 3. Fluid Coordinate ΔZ低下を記録
    delta_down = fluid_connector.compute_delta(state.value, state_degraded.value)
    assert delta_down["dz"] < 0

    fluid_connector.notify_trajectory(
        state.value, state_degraded.value, event_id="E_INCIDENT_001"
    )

    # 4. Human Gate介入 -> State ACTIVE復帰
    assert can_transition(state_degraded, ISEState.ACTIVE) is True
    state_recovered = transition(state_degraded, ISEState.ACTIVE)
    assert state_recovered == ISEState.ACTIVE

    recover_entry = decision_ledger.append_decision(
        decision_type="state_transition",
        actor="Human",
        before=state_degraded.value,
        after=state_recovered.value,
        reason="human_gate_recovery",
        prev_hash=degrade_entry["hash"],
    )
    assert recover_entry["actor"] == "Human"

    # 5. ΔZ回復を記録
    delta_up = fluid_connector.compute_delta(state_degraded.value, state_recovered.value)
    assert delta_up["dz"] > 0

    fluid_connector.notify_trajectory(
        state_degraded.value, state_recovered.value, event_id="E_INCIDENT_002"
    )

    # 6. 最終確認: Decision Ledgerチェーン整合性 & trajectory.csvに2行記録
    ok, msg = decision_ledger.verify_chain()
    assert ok is True
    assert "3 entries OK" in msg

    with open(trajectory_path, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert len(rows) == 2
