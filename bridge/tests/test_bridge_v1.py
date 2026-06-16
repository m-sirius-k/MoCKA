# bridge/tests/test_bridge_v1.py
# PHI-OS ↔ Personal Lexicon Bridge v1 統合テスト

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from bridge.conflict_engine import ConflictEngine
from bridge.conflict_types import ConflictJudgment, ConflictState, BridgeRecord
from bridge.mapping_registry import MappingRegistry
from bridge.phi_personal_bridge import PhiPersonalBridge
from bridge.auto_mapper import AutoMapper


# ─── フィクスチャ ──────────────────────────────────────────────────────────────

@pytest.fixture
def engine():
    return ConflictEngine()


@pytest.fixture
def bridge(tmp_path):
    registry = MappingRegistry(db_path=str(tmp_path / "test_bridge.db"))
    b = PhiPersonalBridge(registry=registry, engine=ConflictEngine())
    yield b
    b.close()


@pytest.fixture
def auto_mapper(bridge):
    phi_store    = {}
    personal_store = {}
    mapper = AutoMapper(
        bridge=bridge,
        phi_os_fetcher=lambda t: phi_store.get(t),
        personal_fetcher=lambda t: personal_store.get(t),
    )
    mapper._phi_store     = phi_store
    mapper._personal_store = personal_store
    return mapper


# ─── Phase 1: 衝突エンジン ─────────────────────────────────────────────────────

class TestConflictEngine:

    def test_same_term_different_meaning_is_full_conflict(self, engine):
        """同一 term・差分意味 → FULL_CONFLICT"""
        result = engine.detect(
            "evolution",
            phi_os_meaning="Drift-driven meaning mutation over semantic gravity",
            personal_meaning="人が意図して学習によって変化させること",
        )
        assert result.judgment == ConflictJudgment.FULL_CONFLICT
        assert result.state == ConflictState.CONFLICT

    def test_matching_meanings_normal(self, engine):
        """意味が一致 → MATCH / NORMAL"""
        result = engine.detect("concept", "an abstract idea", "an abstract idea")
        assert result.judgment == ConflictJudgment.MATCH
        assert result.state == ConflictState.NORMAL

    def test_drift_when_phi_missing(self, engine):
        """PHI-OS に意味なし → DRIFT"""
        result = engine.detect("unknown_term", None, "人が定義した意味")
        assert result.judgment == ConflictJudgment.SEMANTIC_DRIFT
        assert result.state == ConflictState.DRIFT

    def test_drift_when_personal_missing(self, engine):
        """Personal に意味なし → DRIFT"""
        result = engine.detect("new_term", "PHI-OS defined meaning", None)
        assert result.state == ConflictState.DRIFT

    def test_both_none_is_normal(self, engine):
        """両方 None → MATCH / NORMAL（衝突なし）"""
        result = engine.detect("ghost_term", None, None)
        assert result.judgment == ConflictJudgment.MATCH
        assert result.state == ConflictState.NORMAL


# ─── Phase 1: 状態遷移 ─────────────────────────────────────────────────────────

class TestConflictStateTransition:

    def _make_record(self, state: ConflictState) -> BridgeRecord:
        import datetime
        return BridgeRecord(
            term="x",
            phi_os_meaning="a",
            personal_meaning="b",
            state=state,
            last_sync=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            conflict_reason="",
        )

    def test_locked_does_not_transition(self, engine):
        """LOCKED は transition しない"""
        record = self._make_record(ConflictState.LOCKED)
        new_state = engine.transition(record, ConflictJudgment.MATCH)
        assert new_state == ConflictState.LOCKED

    def test_normal_to_conflict(self, engine):
        record = self._make_record(ConflictState.NORMAL)
        new_state = engine.transition(record, ConflictJudgment.FULL_CONFLICT)
        assert new_state == ConflictState.CONFLICT

    def test_drift_to_normal(self, engine):
        record = self._make_record(ConflictState.DRIFT)
        new_state = engine.transition(record, ConflictJudgment.MATCH)
        assert new_state == ConflictState.NORMAL


# ─── Phase 2: Bridge registry ──────────────────────────────────────────────────

class TestBridgeRegistry:

    def test_register_and_get_dual_view(self, bridge):
        """登録後に dual_view が取得できる"""
        bridge.register_mapping(
            "institution",
            phi_os_meaning="自己強化する意味構造体",
            personal_meaning="組織・制度",
        )
        view = bridge.get_dual_view("institution")
        assert view["registered"] is True
        assert view["phi_os_meaning"] == "自己強化する意味構造体"
        assert view["personal_meaning"] == "組織・制度"
        assert view["state"] is not None

    def test_unregistered_term_dual_view(self, bridge):
        """未登録 term の dual_view は registered=False"""
        view = bridge.get_dual_view("nonexistent")
        assert view["registered"] is False
        assert view["phi_os_meaning"] is None

    def test_conflict_is_stored_not_resolved(self, bridge):
        """CONFLICT 状態は自動解決されず Bridge に保存される"""
        bridge.register_mapping(
            "evolution",
            phi_os_meaning="Drift-driven semantic mutation via gravity collapse",
            personal_meaning="人間が意識的に変化させること",
        )
        view = bridge.get_dual_view("evolution")
        assert view["state"] == ConflictState.CONFLICT.value
        # 両方の意味が保持されている
        assert view["phi_os_meaning"] is not None
        assert view["personal_meaning"] is not None


# ─── Phase 3: auto mapper ──────────────────────────────────────────────────────

class TestAutoMapper:

    def test_unknown_term_stores_drift(self, auto_mapper):
        """未知 term（両 fetcher が None）→ NORMAL で保存（暴走しない）"""
        record = auto_mapper.map_term("totally_unknown")
        assert record.state == ConflictState.NORMAL  # 両方 None = NORMAL

    def test_conflict_stored_in_bridge_only(self, auto_mapper):
        """CONFLICT term は Bridge に保存される"""
        auto_mapper._phi_store["gravity"]    = "意味場の重力崩壊現象"
        auto_mapper._personal_store["gravity"] = "重力（物理）"

        record = auto_mapper.map_term("gravity")
        assert record.state == ConflictState.CONFLICT
        # Bridge に保存されていることを確認
        view = auto_mapper.bridge.get_dual_view("gravity")
        assert view["registered"] is True

    def test_auto_mapper_does_not_modify_meanings(self, auto_mapper):
        """AutoMapper は意味を変更しない"""
        auto_mapper._phi_store["phi_term"]    = "PHI original"
        auto_mapper._personal_store["phi_term"] = "Personal original"

        auto_mapper.map_term("phi_term")
        view = auto_mapper.bridge.get_dual_view("phi_term")
        assert view["phi_os_meaning"] == "PHI original"
        assert view["personal_meaning"] == "Personal original"


# ─── Phase 4: 双方向同期 ───────────────────────────────────────────────────────

class TestBidirectionalSync:

    def test_sync_from_phi_does_not_touch_personal(self, bridge):
        """PHI-OS 側の同期は Personal 意味を変えない"""
        bridge.register_mapping("anchor", phi_os_meaning="v1", personal_meaning="固定点")
        bridge.sync_from_phi_os("anchor", "v2_updated")
        view = bridge.get_dual_view("anchor")
        assert view["phi_os_meaning"] == "v2_updated"
        assert view["personal_meaning"] == "固定点"

    def test_sync_from_personal_does_not_touch_phi(self, bridge):
        """Personal 側の同期は PHI-OS 意味を変えない"""
        bridge.register_mapping("anchor2", phi_os_meaning="PHI定義", personal_meaning="v1")
        bridge.sync_from_personal("anchor2", "v2_personal")
        view = bridge.get_dual_view("anchor2")
        assert view["phi_os_meaning"] == "PHI定義"
        assert view["personal_meaning"] == "v2_personal"

    def test_locked_term_not_synced(self, bridge):
        """LOCKED term は同期を受け付けない"""
        bridge.register_mapping("locked_term", phi_os_meaning="original", personal_meaning="元の意味")
        bridge.lock("locked_term")
        bridge.sync_from_phi_os("locked_term", "new_phi_meaning")
        view = bridge.get_dual_view("locked_term")
        assert view["phi_os_meaning"] == "original"
        assert view["state"] == ConflictState.LOCKED.value

    def test_drift_state_transition(self, bridge):
        """片方のみ存在 → DRIFT、両方揃うと再判定"""
        bridge.register_mapping("drifter", phi_os_meaning="PHI意味", personal_meaning=None)
        view1 = bridge.get_dual_view("drifter")
        assert view1["state"] == ConflictState.DRIFT.value

        bridge.sync_from_personal("drifter", "PHI意味")  # 同じ意味を入れる
        view2 = bridge.get_dual_view("drifter")
        assert view2["state"] == ConflictState.NORMAL.value

    def test_conflict_state_preserved(self, bridge):
        """CONFLICT は自動解決されない"""
        bridge.register_mapping(
            "disputed",
            phi_os_meaning="完全に異なる定義A — 抽象的意味変動空間",
            personal_meaning="完全に異なる定義B — 具体的物理現象",
        )
        view = bridge.get_dual_view("disputed")
        assert view["state"] == ConflictState.CONFLICT.value

        # 再同期しても CONFLICT のまま
        bridge.sync_from_phi_os("disputed", "更新後の完全異質な定義C — 別次元の概念体系")
        view2 = bridge.get_dual_view("disputed")
        assert view2["state"] == ConflictState.CONFLICT.value
