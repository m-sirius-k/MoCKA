# test_phase_c.py
import json, gzip
from datetime import datetime, timezone, timedelta

from ..schema import InstitutionState, ProjectStatus
from ..provider_chain import ProviderChain
from ..snapshot_manager import (
    should_create_snapshot, create_snapshot, get_last_snapshot_info,
    maybe_create_snapshot, SNAPSHOT_REVISION_THRESHOLD, SNAPSHOT_MAX_GENERATIONS,
)
from ..institution_contract import HMAC_KEY_ID, HMAC_SECRET


# ── Provider Chain ─────────────────────────────────────────────

class ProviderEmpty:
    def get_project_status(self):    return None
    def get_active_warnings(self):   return []
    def get_active_todos(self):      return []
    def get_decision_revision(self): return 3
    def get_guideline_revision(self):return 1

class ProviderA:
    def get_project_status(self):
        return ProjectStatus(phase=5, mission="chain test", priority=["X"])
    def get_active_warnings(self):   return []
    def get_active_todos(self):      return []
    def get_decision_revision(self): return 7
    def get_guideline_revision(self):return 2


def test_provider_chain_falls_through_to_next():
    chain = ProviderChain([ProviderEmpty(), ProviderA()])
    status = chain.get_project_status()
    assert status.phase == 5
    assert status.mission == "chain test"

def test_provider_chain_max_revisions():
    chain = ProviderChain([ProviderEmpty(), ProviderA()])
    assert chain.get_decision_revision() == 7
    assert chain.get_guideline_revision() == 2

def test_provider_chain_default_when_all_empty():
    chain = ProviderChain([ProviderEmpty()])
    status = chain.get_project_status()
    assert status.phase == 0
    assert status.mission == "unknown"


# ── Snapshot Manager ──────────────────────────────────────────

def _make_state(revision: int) -> InstitutionState:
    return InstitutionState(
        state_version=1,
        project=ProjectStatus(phase=1, mission="m", priority=[]),
        warnings=[], todos=[],
        decision_ledger_rev=0, guideline_revision=0,
        revision=revision, state_hash=f"hash{revision}",
        generated_at="2026-01-01T00:00:00+00:00",
    )

def test_should_create_snapshot_by_revision():
    old_time = datetime.now(timezone.utc)
    assert should_create_snapshot(SNAPSHOT_REVISION_THRESHOLD, 0, old_time) is True
    assert should_create_snapshot(SNAPSHOT_REVISION_THRESHOLD - 1, 0, old_time) is False

def test_should_create_snapshot_by_time():
    old_time = datetime.now(timezone.utc) - timedelta(hours=25)
    assert should_create_snapshot(1, 0, old_time) is True

def test_create_snapshot_writes_file(tmp_path):
    state = _make_state(5)
    path = create_snapshot(state, tmp_path)
    assert path.exists()
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    assert d["revision"] == 5

def test_get_last_snapshot_info_empty(tmp_path):
    rev, t = get_last_snapshot_info(tmp_path)
    assert rev == 0

def test_maybe_create_snapshot_first_time(tmp_path):
    state = _make_state(1)
    snap = maybe_create_snapshot(state, tmp_path)
    assert snap is not None
    assert snap.exists()

def test_snapshot_rotation_compresses_old(tmp_path):
    # SNAPSHOT_MAX_GENERATIONS + 2 件のスナップショットを作成
    for rev in range(1, SNAPSHOT_MAX_GENERATIONS + 3):
        create_snapshot(_make_state(rev), tmp_path)

    files = list(tmp_path.iterdir())
    gz_files  = [f for f in files if f.suffix == ".gz"]
    uncompressed = [f for f in files if f.suffix == ".json"]

    assert len(uncompressed) == SNAPSHOT_MAX_GENERATIONS
    assert len(gz_files) >= 1

    # gzip圧縮ファイルが読めること
    with gzip.open(gz_files[0], "rt", encoding="utf-8") as f:
        d = json.load(f)
    assert "revision" in d


# ── HMAC Key ID 方式 ──────────────────────────────────────────

def test_hmac_key_id_loaded():
    assert HMAC_KEY_ID == "KID-001"

def test_hmac_secret_loaded_from_env():
    assert isinstance(HMAC_SECRET, bytes)
    assert len(HMAC_SECRET) > 0
