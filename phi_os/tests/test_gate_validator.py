# tests/test_gate_validator.py
# CONTRACT-INTEGRATION-TEST-SPEC-V1: phi_os.gate_validator.validate()の実行可能テスト
# 対象: phi_os/gate_validator.py:8-43 (validate)
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from phi_os.gate_validator import validate
from phi_os.gate_schema import ALLOWED_WHAT_TYPES


def _valid_payload(**overrides):
    payload = {
        "who_actor": "Claude-sonnet-4-6",
        "who_session": "SESSION_20260623_120000",
        "why_purpose": "統合テスト用イベント記録",
        "how_trigger": "mcp_tool_call",
        "where_path": "mocka_mcp_server.py",
        "what_type": ALLOWED_WHAT_TYPES[0],
        "after_state": "test",
    }
    payload.update(overrides)
    return payload


# --- 正常系 (VALID) -----------------------------------------------------

def test_valid_payload_passes():
    errors = validate(_valid_payload())
    assert errors == []


# --- 境界系 (EDGE) — REJECT-01〜07を1項目ずつ単独違反させる ---------------

def test_reject01_who_actor_empty():
    errors = validate(_valid_payload(who_actor=""))
    assert errors == ["REJECT-01: who_actor必須 (例: Claude-sonnet-4-6)"]


def test_reject01_who_actor_legacy_claude():
    errors = validate(_valid_payload(who_actor="claude"))
    assert errors == ["REJECT-01: who_actor必須 (例: Claude-sonnet-4-6)"]


def test_reject02_who_session_invalid_prefix():
    errors = validate(_valid_payload(who_session="invalid_prefix"))
    assert errors == ["REJECT-02: who_session形式不正 (SESSION_YYYYMMDD_HHMMSS)"]


def test_reject03_why_purpose_too_short():
    errors = validate(_valid_payload(why_purpose="短い"))
    assert errors == ["REJECT-03: why_purpose 10文字以上必須"]


def test_reject04_how_trigger_empty():
    errors = validate(_valid_payload(how_trigger=""))
    assert errors == ["REJECT-04: how_trigger必須"]


def test_reject05_where_path_empty():
    errors = validate(_valid_payload(where_path=""))
    assert errors == ["REJECT-05: where_path必須"]


def test_reject06_what_type_not_allowed():
    errors = validate(_valid_payload(what_type="未許可タイプ"))
    assert len(errors) == 1
    assert errors[0].startswith("REJECT-06:")


def test_reject07_before_and_after_both_missing():
    payload = _valid_payload()
    payload.pop("after_state", None)
    errors = validate(payload)
    assert errors == ["REJECT-07: before/afterどちらか必須(Replay不能)"]


# --- 破壊系 (MALFORMED) ---------------------------------------------------

def test_malformed_empty_dict_returns_errors_without_exception():
    errors = validate({})
    assert isinstance(errors, list)
    assert len(errors) > 0


def test_malformed_operational_only_payload_rejected_by_governance_lane():
    # validate_operational向けの軽量payloadをgovernance lane(validate)に
    # 誤って渡した場合、REJECT-02〜07が正しく発生し例外なく処理されることを確認
    operational_payload = {
        "who_actor": "Claude-sonnet-4-6",
        "what_type": ALLOWED_WHAT_TYPES[0],
        "where_component": "mcp_caliber",
    }
    errors = validate(operational_payload)
    assert isinstance(errors, list)
    codes = {e.split(":")[0] for e in errors}
    assert "REJECT-02" in codes
    assert "REJECT-03" in codes
    assert "REJECT-04" in codes
    assert "REJECT-05" in codes
    assert "REJECT-07" in codes
