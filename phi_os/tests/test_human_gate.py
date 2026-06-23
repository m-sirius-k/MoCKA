# phi_os/tests/test_human_gate.py
# PHI-OS Human Gate State Model v1 — pytest suite
import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
import phi_os.human_gate as hg


@pytest.fixture
def conn(tmp_path):
    db_file = str(tmp_path / 'test_human_gate.db')
    c = sqlite3.connect(db_file)
    c.row_factory = sqlite3.Row
    hg._ensure_table(c)
    yield c
    c.close()


def test_submit_creates_pending(conn):
    event = hg.submit({"request_id": "R1", "what": "test"}, conn=conn)
    assert event["next_state"] == "PENDING"
    assert event["previous_state"] is None
    assert hg.get_state("R1", conn=conn) == "PENDING"


def test_submit_duplicate_request_id_rejected(conn):
    hg.submit({"request_id": "R1"}, conn=conn)
    with pytest.raises(hg.HumanGateError):
        hg.submit({"request_id": "R1"}, conn=conn)


def test_approve_from_pending_succeeds(conn):
    hg.submit({"request_id": "R2"}, conn=conn)
    event = hg.approve("R2", conn=conn)
    assert event["previous_state"] == "PENDING"
    assert event["next_state"] == "APPROVED"
    assert hg.get_state("R2", conn=conn) == "APPROVED"


def test_reject_from_pending_succeeds(conn):
    hg.submit({"request_id": "R3"}, conn=conn)
    event = hg.reject("R3", conn=conn)
    assert event["next_state"] == "REJECTED"


def test_expire_from_pending_succeeds(conn):
    hg.submit({"request_id": "R4"}, conn=conn)
    event = hg.expire("R4", conn=conn)
    assert event["next_state"] == "EXPIRED"


def test_approve_on_nonexistent_request_id_rejected(conn):
    with pytest.raises(hg.HumanGateError):
        hg.approve("DOES_NOT_EXIST", conn=conn)


def test_approve_already_approved_rejected(conn):
    hg.submit({"request_id": "R5"}, conn=conn)
    hg.approve("R5", conn=conn)
    with pytest.raises(hg.HumanGateError):
        hg.approve("R5", conn=conn)


def test_reject_already_rejected_rejected(conn):
    hg.submit({"request_id": "R6"}, conn=conn)
    hg.reject("R6", conn=conn)
    with pytest.raises(hg.HumanGateError):
        hg.reject("R6", conn=conn)


@pytest.mark.parametrize("from_state,setup", [
    ("PENDING", lambda c, rid: hg.submit({"request_id": rid}, conn=c)),
    ("APPROVED", lambda c, rid: (hg.submit({"request_id": rid}, conn=c), hg.approve(rid, conn=c))),
    ("REJECTED", lambda c, rid: (hg.submit({"request_id": rid}, conn=c), hg.reject(rid, conn=c))),
])
def test_cancel_allowed_from_pending_approved_rejected(conn, from_state, setup):
    rid = f"RC_{from_state}"
    setup(conn, rid)
    event = hg.cancel(rid, conn=conn)
    assert event["next_state"] == "CANCELED"


def test_cancel_from_expired_rejected(conn):
    hg.submit({"request_id": "R7"}, conn=conn)
    hg.expire("R7", conn=conn)
    with pytest.raises(hg.HumanGateError):
        hg.cancel("R7", conn=conn)


def test_cancel_is_final_state(conn):
    hg.submit({"request_id": "R8"}, conn=conn)
    hg.cancel("R8", conn=conn)
    with pytest.raises(hg.HumanGateError):
        hg.approve("R8", conn=conn)
    with pytest.raises(hg.HumanGateError):
        hg.cancel("R8", conn=conn)


def test_list_pending_returns_only_pending_latest_state(conn):
    hg.submit({"request_id": "P1"}, conn=conn)
    hg.submit({"request_id": "P2"}, conn=conn)
    hg.submit({"request_id": "P3"}, conn=conn)
    hg.approve("P2", conn=conn)

    pending = hg.list_pending(conn=conn)
    pending_ids = {row["request_id"] for row in pending}
    assert pending_ids == {"P1", "P3"}


def test_state_is_reconstructed_from_events_not_stored_separately(conn):
    # 「stateは保存しない、eventのみ保存する」という永続ルールの検証。
    # human_gate_eventsテーブルにはnext_state列はあるが、別のstateテーブルは存在しない。
    hg.submit({"request_id": "R9"}, conn=conn)
    hg.approve("R9", conn=conn)
    tables = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    assert tables == {"human_gate_events"}
    assert hg.get_state("R9", conn=conn) == "APPROVED"
