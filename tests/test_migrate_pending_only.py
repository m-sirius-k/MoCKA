"""A案の試験：移行は必ず PENDING に留まり、approve / reject を呼ばない。既存の擬似遷移は一覧のみ（状態不変）。
実行: python3 -m unittest tests.test_migrate_pending_only -v
flask は未導入でも動くよう、phi_os.human_gate が要求する Blueprint だけを差し替える。
DB とキューは一時ファイル。実データには触れない。"""
import json
import os
import sqlite3
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if "flask" not in sys.modules:
    fake = types.ModuleType("flask")
    class Blueprint:  # noqa: D401 - 試験用の最小スタブ
        def __init__(self, *a, **k):
            pass
        def route(self, *a, **k):
            return lambda f: f
    fake.Blueprint = Blueprint
    fake.request = None
    fake.jsonify = lambda *a, **k: None
    sys.modules["flask"] = fake

from phi_os import human_gate as hg  # noqa: E402
from phi_os import migrate_prevention_queue as mig  # noqa: E402


def _queue():
    return {"queue": [
        {"id": "PQ_NEW", "status": "NEW", "recurrence_key": "k1", "component": "c", "what_type": "w", "severity": "s"},
        {"id": "PQ_APPROVED", "status": "approved", "recurrence_key": "k2"},
        {"id": "PQ_REJECTED", "status": "rejected", "recurrence_key": "k3"},
    ]}


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = os.path.join(self.tmp, "events.db")
        self.qpath = Path(self.tmp) / "prevention_queue.json"
        self.qpath.write_text(json.dumps(_queue(), ensure_ascii=False), encoding="utf-8")
        self._saved = (hg.DB_PATH, mig.QUEUE_PATH)
        hg.DB_PATH = self.db
        mig.QUEUE_PATH = self.qpath

    def tearDown(self):
        hg.DB_PATH, mig.QUEUE_PATH = self._saved

    def _events(self):
        c = sqlite3.connect(self.db)
        try:
            return c.execute("SELECT request_id, action, next_state, payload FROM human_gate_events").fetchall()
        finally:
            c.close()

    def test_every_migrated_item_stays_pending(self):
        summary = mig.migrate(dry_run=False)
        self.assertEqual(summary["migrated"], 3)
        for rid in ("PQ_NEW", "PQ_APPROVED", "PQ_REJECTED"):
            self.assertEqual(hg.get_state(rid), "PENDING", rid + " は PENDING に留まる")

    def test_approve_and_reject_are_never_called(self):
        def boom(*a, **k):
            raise AssertionError("migration must not call approve/reject")
        orig = (hg.approve, hg.reject)
        hg.approve, hg.reject = boom, boom
        try:
            mig.migrate(dry_run=False)
        finally:
            hg.approve, hg.reject = orig
        actions = {a for (_, a, _, _) in self._events()}
        self.assertEqual(actions, {"submit"})

    def test_legacy_decisions_carry_unverified_flag(self):
        mig.migrate(dry_run=False)
        payloads = {rid: json.loads(p) for (rid, a, n, p) in self._events()}
        self.assertEqual(payloads["PQ_APPROVED"]["migration_flag"], "MIGRATION_UNVERIFIED")
        self.assertEqual(payloads["PQ_APPROVED"]["legacy_decision"], "APPROVED")
        self.assertEqual(payloads["PQ_REJECTED"]["legacy_decision"], "REJECTED")
        self.assertIsNone(payloads["PQ_NEW"]["migration_flag"])

    def test_dry_run_writes_nothing(self):
        summary = mig.migrate(dry_run=True)
        self.assertEqual(summary["migrated"], 3)
        self.assertEqual(self._events(), [])

    def test_rerun_is_idempotent(self):
        mig.migrate(dry_run=False)
        again = mig.migrate(dry_run=False)
        self.assertEqual(again["migrated"], 0)
        self.assertEqual(again["skipped_existing"], 3)

    def test_existing_pseudo_transitions_are_listed_without_state_change(self):
        # 旧版が書いた擬似承認を再現（旧コードの挙動）
        hg.submit({"request_id": "PQ_OLD", "source": "prevention_queue_migration"})
        hg.approve("PQ_OLD", {"note": "pseudo-transition from migration, no original PENDING history"})
        before = hg.get_state("PQ_OLD")
        found = mig.find_legacy_pseudo_transitions()
        self.assertEqual([f["request_id"] for f in found], ["PQ_OLD"])
        self.assertEqual(hg.get_state("PQ_OLD"), before, "一覧の作成は状態を変えない")


if __name__ == "__main__":
    unittest.main()
