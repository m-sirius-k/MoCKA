"""
tests/test_seal_auth_record.py
AUTO_SEAL M1 Phase 4 Runtime Debug: T1-T7。
sandbox/tmp_path のみを対象とし、本番 decision_ledger.jsonl には触れない。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "governance"))
from seal_auth_record import (  # noqa: E402
    write_auth_record, read_auth_records, verify_auth_record, find_duplicate_request_ids,
)


def _rec(**kw):
    base = {
        "seal_request_id": "SR_1", "requester": "kimura_hakase",
        "decision_id": "DC_x", "approved_by": "kimura_hakase",
        "approval_timestamp": "2026-07-13T00:00:00Z",
    }
    base.update(kw)
    return base


def test_backward_compat(tmp_path):
    # T1: 旧行(拡張なし)と新行(拡張あり)が同一ファイルで両方 parse できる
    p = tmp_path / "l.jsonl"
    write_auth_record(p, {"decision_id": "DC_old", "approved_by": "kimura_hakase"})
    write_auth_record(p, _rec())
    assert len(read_auth_records(p)) == 2


def test_approved_by_system_rejected():
    # T2: approved_by=system は不合格
    ok, r = verify_auth_record(_rec(approved_by="system:seal_governance_gate"))
    assert not ok and "approved_by_not_human" in r


def test_approved_by_human_ok():
    # T3: approved_by=human は合格
    ok, r = verify_auth_record(_rec())
    assert ok and r == []


def test_missing_required():
    # T4: 必須フィールド欠落は不合格
    ok, r = verify_auth_record(_rec(seal_request_id=""))
    assert not ok and "missing:seal_request_id" in r


def test_duplicate_request_ids(tmp_path):
    # T5: seal_request_id の重複を検出
    p = tmp_path / "l.jsonl"
    write_auth_record(p, _rec(seal_request_id="SR_dup"))
    write_auth_record(p, _rec(seal_request_id="SR_dup"))
    assert "SR_dup" in find_duplicate_request_ids(p)


def test_pending_ref_required_for_auto():
    # T6: AUTO由来(requester=system:auto_audit_loop)は pending_ref 必須
    ok, r = verify_auth_record(_rec(requester="system:auto_audit_loop"))
    assert not ok and "missing:pending_ref" in r
    ok2, _ = verify_auth_record(
        _rec(requester="system:auto_audit_loop", pending_ref="AUTO_SEAL_PENDING_x"))
    assert ok2


def test_jsonl_integrity(tmp_path):
    # T7: append-only JSONL の整合(有効JSONL・改行終端)
    p = tmp_path / "l.jsonl"
    write_auth_record(p, _rec())
    txt = p.read_text(encoding="utf-8")
    assert txt.endswith("\n")
    for line in txt.splitlines():
        json.loads(line)
