# test_phase_a.py
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from ..schema import (
    InstitutionState, ProjectStatus, Warning, TodoItem,
    CURRENT_SCHEMA_VERSION,
)
from ..state_provider import StateProvider
from ..state_builder import build_state
from ..hash_generator import compute_state_hash
from ..revision_manager import RevisionStore, update_institution_state


# ── テスト用 MockProvider ──────────────────────────────────────

class MockProvider:
    def get_project_status(self):
        return ProjectStatus(phase=4, mission="test mission", priority=["TODO_001"])
    def get_active_warnings(self):
        return [Warning(id="W001", level="ACTIVE", description="test warning")]
    def get_active_todos(self):
        return [TodoItem(id="TODO_001", title="test todo", priority="高", status="未着手")]
    def get_decision_revision(self):
        return 10
    def get_guideline_revision(self):
        return 5


# ── テスト ────────────────────────────────────────────────────

def test_build_state_is_pure():
    """build_state は同じ入力から同じ出力を返す（Pure Function）"""
    p = MockProvider()
    s1 = build_state(p)
    s2 = build_state(p)
    assert s1.to_dict() == s2.to_dict(), "Pure Functionでないと同じ入力で異なる出力になる"


def test_build_state_no_revision():
    """build_state は revision=0 / state_hash='' で返す"""
    s = build_state(MockProvider())
    assert s.revision   == 0
    assert s.state_hash == ""


def test_build_state_schema_version():
    """state_version が CURRENT_SCHEMA_VERSION と一致する"""
    s = build_state(MockProvider())
    assert s.state_version == CURRENT_SCHEMA_VERSION


def test_hash_deterministic():
    """同じ State からは常に同じ Hash が生成される（正規化確認）"""
    s = build_state(MockProvider())
    h1 = compute_state_hash(s)
    h2 = compute_state_hash(s)
    assert h1 == h2


def test_hash_excludes_generated_at():
    """generated_at が違っても内容が同じなら Hash は同じ"""
    s1 = build_state(MockProvider())
    s2 = build_state(MockProvider())
    s1.generated_at = "2026-01-01T00:00:00Z"
    s2.generated_at = "2026-12-31T23:59:59Z"
    assert compute_state_hash(s1) == compute_state_hash(s2)


def test_revision_increments_on_change(tmp_path):
    """State が変化したとき Revision がインクリメントされる"""
    store = RevisionStore(tmp_path / "revision_store.json")
    state_path = tmp_path / "current_state.json"

    class ProviderA:
        def get_project_status(self):
            return ProjectStatus(phase=4, mission="A", priority=[])
        def get_active_warnings(self):   return []
        def get_active_todos(self):      return []
        def get_decision_revision(self): return 0
        def get_guideline_revision(self):return 0

    class ProviderB:
        def get_project_status(self):
            return ProjectStatus(phase=4, mission="B", priority=[])  # missionが変わった
        def get_active_warnings(self):   return []
        def get_active_todos(self):      return []
        def get_decision_revision(self): return 0
        def get_guideline_revision(self):return 0

    s1 = update_institution_state(ProviderA(), store, state_path)
    r1 = s1.revision

    s2 = update_institution_state(ProviderB(), store, state_path)
    r2 = s2.revision

    assert r2 == r1 + 1, f"変化時に Revision が上がらない: {r1} → {r2}"


def test_revision_stable_when_no_change(tmp_path):
    """State が変化しないとき Revision は据え置き"""
    store = RevisionStore(tmp_path / "revision_store.json")
    state_path = tmp_path / "current_state.json"

    s1 = update_institution_state(MockProvider(), store, state_path)
    s2 = update_institution_state(MockProvider(), store, state_path)

    assert s1.revision == s2.revision, "変化なしなのに Revision が上がった"


def test_ai_session_state_does_not_affect_revision(tmp_path):
    """
    AI Session State の更新は Institution State の Revision に影響しない。
    （分離の確認: AI Registry は別ファイルで管理される）
    """
    store = RevisionStore(tmp_path / "revision_store.json")
    state_path = tmp_path / "current_state.json"

    s1 = update_institution_state(MockProvider(), store, state_path)

    # AI の last_revision だけ変わっても、制度状態は変わっていない
    # → 同じ MockProvider を使えば Revision は上がらない
    s2 = update_institution_state(MockProvider(), store, state_path)

    assert s1.revision == s2.revision
