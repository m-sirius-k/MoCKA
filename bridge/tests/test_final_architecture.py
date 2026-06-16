# bridge/tests/test_final_architecture.py
# MoCKA 最終アーキテクチャ準拠テスト
#
# 検証対象: 成功条件①〜④ + graph consistency + state immutability
#
# ① conflict が永続する
# ② どの層も意味を変更しない
# ③ 判断はあるが介入しない
# ④ 観測だけで全構造が成立する
#
# 追加: P1-P4 設計原則の自動検証

import sys, os, io, copy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest

from bridge.conflict_engine import ConflictEngine
from bridge.conflict_types import BridgeRecord, ConflictState
from bridge.mapping_registry import MappingRegistry
from bridge.phi_personal_bridge import PhiPersonalBridge

from phi_os.phi_bridge_governance import (
    ConflictEvent,
    DecisionKind,
    PhiBridgeGovernance,
    event_from_bridge_record,
)
from ui.conflict_view_model import (
    ConflictVisualNode,
    ConflictEdge,
    ConflictGraph,
    build_graph_from_records,
)
from ui.conflict_renderer import ConflictRenderer
from orchestra.conflict_interpreter import ConflictInterpreter, run_full_pipeline


# ─── フィクスチャ ──────────────────────────────────────────────────────────────

@pytest.fixture
def bridge(tmp_path):
    b = PhiPersonalBridge(
        registry=MappingRegistry(db_path=str(tmp_path / "final.db")),
        engine=ConflictEngine(),
    )
    yield b
    b.close()


@pytest.fixture
def governance():
    return PhiBridgeGovernance()


@pytest.fixture
def interpreter():
    return ConflictInterpreter()


def _conflict_record(bridge, term: str) -> BridgeRecord:
    """CONFLICT 状態の BridgeRecord を生成するヘルパー。"""
    bridge.register_mapping(
        term,
        phi_os_meaning="PHIが定義する完全に異なる抽象概念 — 意味重力場の崩壊点",
        personal_meaning="人間が経験から得た具体的かつ固定された認知単位",
    )
    return bridge.registry.get(term)


# ─────────────────────────────────────────────────────────────────────────────
# 成功条件 ① — conflict が永続する
# ─────────────────────────────────────────────────────────────────────────────

class TestCondition1_ConflictPersists:

    def test_conflict_survives_phi_os_processing(self, bridge, governance):
        """PHI-OS 処理後も conflict state は変わらない"""
        record = _conflict_record(bridge, "persist_a")
        assert record.state == ConflictState.CONFLICT

        event = event_from_bridge_record(record)
        governance.process(event)

        after = bridge.registry.get("persist_a")
        assert after.state == ConflictState.CONFLICT

    def test_conflict_survives_ui_render(self, bridge):
        """UI 描画後も conflict state は変わらない"""
        _conflict_record(bridge, "persist_b")
        records = bridge.registry.list_all()
        graph = build_graph_from_records(records)

        buf = io.StringIO()
        ConflictRenderer(out=buf).render_graph(graph)

        after = bridge.registry.get("persist_b")
        assert after.state == ConflictState.CONFLICT

    def test_conflict_survives_orchestra(self, bridge, governance, interpreter):
        """Orchestra 通過後も conflict state は変わらない"""
        record = _conflict_record(bridge, "persist_c")
        event = event_from_bridge_record(record)
        decision = governance.process(event)
        interpreter.interpret(event, decision)

        after = bridge.registry.get("persist_c")
        assert after.state == ConflictState.CONFLICT

    def test_conflict_not_deletable_through_normal_pipeline(self, bridge, governance):
        """パイプラインに conflict 削除 API が存在しない"""
        record = _conflict_record(bridge, "persist_d")
        event = event_from_bridge_record(record)
        decision = governance.process(event)

        # Decision に state 変更メソッドがないことを確認
        assert not hasattr(decision, "resolve")
        assert not hasattr(decision, "delete")
        assert not hasattr(decision, "merge")


# ─────────────────────────────────────────────────────────────────────────────
# 成功条件 ② — どの層も意味を変更しない
# ─────────────────────────────────────────────────────────────────────────────

class TestCondition2_NoLayerModifiesMeaning:

    PHI_DEF = "PHI: 意味が引力崩壊によって別の意味圏に落下する現象"
    PER_DEF = "Personal: 自分が長年使い続けてきた固定された言葉の感覚"

    def _setup(self, bridge, term="meaning_test"):
        bridge.register_mapping(term, phi_os_meaning=self.PHI_DEF, personal_meaning=self.PER_DEF)
        return bridge.registry.get(term)

    def test_phi_os_does_not_modify_meaning(self, bridge, governance):
        record = self._setup(bridge, "m1")
        event = event_from_bridge_record(record)
        governance.process(event)

        after = bridge.registry.get("m1")
        assert after.phi_os_meaning == self.PHI_DEF
        assert after.personal_meaning == self.PER_DEF

    def test_ui_does_not_modify_meaning(self, bridge):
        record = self._setup(bridge, "m2")
        records = bridge.registry.list_all()
        graph = build_graph_from_records(records)

        buf = io.StringIO()
        ConflictRenderer(out=buf).render_graph(graph)

        after = bridge.registry.get("m2")
        assert after.phi_os_meaning == self.PHI_DEF
        assert after.personal_meaning == self.PER_DEF

    def test_orchestra_does_not_modify_meaning(self, bridge, governance, interpreter):
        record = self._setup(bridge, "m3")
        event = event_from_bridge_record(record)
        decision = governance.process(event)
        interp = interpreter.interpret(event, decision)

        # Interpretation は読み取り専用の説明文のみ
        after = bridge.registry.get("m3")
        assert after.phi_os_meaning == self.PHI_DEF
        assert after.personal_meaning == self.PER_DEF

        # interp の summary/detail は元の意味を参照するだけ
        assert "PHI" in interp.detail or self.PHI_DEF[:10] in interp.detail

    def test_full_pipeline_does_not_modify_meaning(self, bridge, governance):
        self._setup(bridge, "m4")
        records_before = bridge.registry.list_all()
        phi_before = {r.term: r.phi_os_meaning for r in records_before}
        per_before  = {r.term: r.personal_meaning for r in records_before}

        run_full_pipeline(records_before, governance)

        records_after = bridge.registry.list_all()
        for r in records_after:
            assert r.phi_os_meaning == phi_before.get(r.term)
            assert r.personal_meaning == per_before.get(r.term)


# ─────────────────────────────────────────────────────────────────────────────
# 成功条件 ③ — 判断はあるが介入しない
# ─────────────────────────────────────────────────────────────────────────────

class TestCondition3_DecisionWithoutIntervention:

    def test_decision_exists_but_bridge_state_unchanged(self, bridge, governance):
        """Decision が生成されるが Bridge state は変わらない"""
        bridge.register_mapping(
            "intervention_test",
            phi_os_meaning="異なる意味A — 完全に別の世界観",
            personal_meaning="異なる意味B — 日常的な感覚",
        )
        record = bridge.registry.get("intervention_test")
        original_state = record.state.value

        event = event_from_bridge_record(record)
        decision = governance.process(event)

        # Decision は存在する
        assert decision is not None
        assert decision.kind in [DecisionKind.OBSERVE, DecisionKind.TAG, DecisionKind.ROUTE]

        # Bridge は変わっていない
        after = bridge.registry.get("intervention_test")
        assert after.state.value == original_state
        assert after.phi_os_meaning == record.phi_os_meaning
        assert after.personal_meaning == record.personal_meaning

    def test_route_decision_does_not_auto_resolve(self, bridge, governance):
        """ROUTE 判断が出ても自動解決しない"""
        bridge.register_mapping(
            "route_test",
            phi_os_meaning="完全異質定義X — 抽象的な意味変動の臨界点",
            personal_meaning="完全異質定義Y — 私が経験した具体的な出来事",
        )
        record = bridge.registry.get("route_test")
        event = event_from_bridge_record(record)
        event.severity = 0.95  # 強制 ROUTE

        decision = governance.process(event)
        assert decision.kind == DecisionKind.ROUTE

        # ROUTE でも Bridge は変わらない
        after = bridge.registry.get("route_test")
        assert after.state == ConflictState.CONFLICT

    def test_orchestra_suggestion_is_not_executed(self, bridge, governance, interpreter):
        """Orchestra の提案は文字列のみ。実行されない。"""
        bridge.register_mapping(
            "suggestion_test",
            phi_os_meaning="定義A",
            personal_meaning="定義B",
        )
        record = bridge.registry.get("suggestion_test")
        event = event_from_bridge_record(record)
        decision = governance.process(event)
        interp = interpreter.interpret(event, decision)

        # suggestion は str 型であり、callable ではない
        assert isinstance(interp.suggestion, str)
        assert callable(interp.suggestion) is False


# ─────────────────────────────────────────────────────────────────────────────
# 成功条件 ④ — 観測だけで全構造が成立する
# ─────────────────────────────────────────────────────────────────────────────

class TestCondition4_ObservationOnly:

    def test_full_read_only_pass(self, bridge, governance, interpreter):
        """全レイヤーを write なしで通過できる"""
        # セットアップ: Bridge だけが書き込む
        bridge.register_mapping("obs_a", phi_os_meaning="PHI定義", personal_meaning="Per定義")

        # 以降は読み取り専用フロー
        records = bridge.registry.list_all()  # 読み取り
        graph   = build_graph_from_records(records)  # 読み取り → Graph構築
        results = run_full_pipeline(records, governance, interpreter)  # 読み取り → 解釈

        buf = io.StringIO()
        ConflictRenderer(out=buf).render_graph(graph)  # 読み取り → 表示

        output = buf.getvalue()
        assert "obs_a" in output
        assert len(results) > 0

        # Bridge に変化なし
        after = bridge.registry.get("obs_a")
        assert after.phi_os_meaning == "PHI定義"
        assert after.personal_meaning == "Per定義"


# ─────────────────────────────────────────────────────────────────────────────
# Graph Consistency Tests (P3: UI は観測のみ)
# ─────────────────────────────────────────────────────────────────────────────

class TestGraphConsistency:

    def test_graph_node_count_matches_registry(self, bridge):
        """Graph のノード数が registry の件数と一致する"""
        bridge.register_mapping("gc_a", phi_os_meaning="A1", personal_meaning="A2")
        bridge.register_mapping("gc_b", phi_os_meaning="B1", personal_meaning="B2")
        bridge.register_mapping("gc_c", phi_os_meaning="C1", personal_meaning="C2")

        records = bridge.registry.list_all()
        graph = build_graph_from_records(records)
        assert graph.summary()["total_nodes"] == len(records)

    def test_graph_state_matches_registry(self, bridge):
        """Graph の各 node.state が registry の state と一致する"""
        bridge.register_mapping(
            "gc_conflict",
            phi_os_meaning="完全に異なる抽象定義 — 意味崩壊の起点",
            personal_meaning="完全に異なる具体定義 — 日常感覚の結晶",
        )
        bridge.register_mapping("gc_normal", phi_os_meaning="同じ意味", personal_meaning="同じ意味")

        records = bridge.registry.list_all()
        graph = build_graph_from_records(records)

        for record in records:
            node = graph.get_node(record.term)
            assert node is not None
            assert node.state == record.state.value

    def test_graph_meanings_match_registry(self, bridge):
        """Graph の node.phi_value / personal_value が registry と一致する"""
        phi_def = "PHI側の正確な定義テキスト"
        per_def = "Personal側の正確な定義テキスト"
        bridge.register_mapping("gc_vals", phi_os_meaning=phi_def, personal_meaning=per_def)

        records = bridge.registry.list_all()
        graph = build_graph_from_records(records)
        node = graph.get_node("gc_vals")

        assert node.phi_value == phi_def
        assert node.personal_value == per_def

    def test_graph_rebuild_is_idempotent(self, bridge):
        """同じ records から graph を2回構築すると同一結果になる"""
        bridge.register_mapping("gc_idem", phi_os_meaning="X", personal_meaning="Y")

        records = bridge.registry.list_all()
        g1 = build_graph_from_records(records)
        g2 = build_graph_from_records(records)

        n1 = g1.get_node("gc_idem")
        n2 = g2.get_node("gc_idem")
        assert n1.state == n2.state
        assert n1.phi_value == n2.phi_value
        assert n1.personal_value == n2.personal_value


# ─────────────────────────────────────────────────────────────────────────────
# State Immutability Tests (P4: Bridge は唯一の状態保持者)
# ─────────────────────────────────────────────────────────────────────────────

class TestStateImmutability:

    def test_phi_os_cannot_change_bridge_state(self, bridge, governance):
        """PHI-OS は Bridge state を変更できない"""
        bridge.register_mapping("si_a", phi_os_meaning="def1", personal_meaning="def2")
        record_before = bridge.registry.get("si_a")

        for severity in [0.1, 0.5, 0.9]:
            event = ConflictEvent(
                term="si_a",
                phi_os_meaning=record_before.phi_os_meaning,
                personal_meaning=record_before.personal_meaning,
                conflict_state=record_before.state.value,
                conflict_reason="test",
                severity=severity,
            )
            governance.process(event)

        record_after = bridge.registry.get("si_a")
        assert record_after.state == record_before.state

    def test_ui_node_mutation_does_not_affect_registry(self, bridge):
        """Graph node の属性を変更しても registry は不変"""
        bridge.register_mapping("si_b", phi_os_meaning="original_phi", personal_meaning="original_per")

        records = bridge.registry.list_all()
        graph = build_graph_from_records(records)
        node = graph.get_node("si_b")

        # node オブジェクトを書き換えても registry には影響しない
        node.phi_value = "TAMPERED"
        node.state = "NORMAL"

        registry_record = bridge.registry.get("si_b")
        assert registry_record.phi_os_meaning == "original_phi"

    def test_locked_state_persists_through_pipeline(self, bridge, governance, interpreter):
        """LOCKED 状態はパイプライン全体を通じて維持される"""
        bridge.register_mapping(
            "si_locked",
            phi_os_meaning="ロック対象の定義A",
            personal_meaning="ロック対象の定義B",
        )
        bridge.lock("si_locked")

        record = bridge.registry.get("si_locked")
        assert record.state == ConflictState.LOCKED

        # PHI-OS 通過
        event = event_from_bridge_record(record)
        governance.process(event)

        # Orchestra 通過
        decision = governance.decisions_for("si_locked")[-1]
        interpreter.interpret(event, decision)

        # UI 通過
        records = bridge.registry.list_all()
        graph = build_graph_from_records(records)
        buf = io.StringIO()
        ConflictRenderer(out=buf).render_graph(graph)

        # LOCKED のまま
        final = bridge.registry.get("si_locked")
        assert final.state == ConflictState.LOCKED

    def test_sync_blocked_on_locked(self, bridge):
        """LOCKED term への sync は完全に無視される"""
        bridge.register_mapping("si_lock2", phi_os_meaning="v1", personal_meaning="p1")
        bridge.lock("si_lock2")

        bridge.sync_from_phi_os("si_lock2", "v2_SHOULD_NOT_APPLY")
        bridge.sync_from_personal("si_lock2", "p2_SHOULD_NOT_APPLY")

        after = bridge.registry.get("si_lock2")
        assert after.phi_os_meaning == "v1"
        assert after.personal_meaning == "p1"
        assert after.state == ConflictState.LOCKED


# ─────────────────────────────────────────────────────────────────────────────
# 設計原則 P1-P4 自動検証
# ─────────────────────────────────────────────────────────────────────────────

class TestDesignPrinciples:

    def test_P1_phi_and_personal_never_merged(self, bridge):
        """P1: PHI と Personal は統合されない。両方が独立して保持される。"""
        bridge.register_mapping(
            "p1_term",
            phi_os_meaning="PHI独自定義",
            personal_meaning="Personal独自定義",
        )
        record = bridge.registry.get("p1_term")
        # 両方が非 None かつ異なる
        assert record.phi_os_meaning is not None
        assert record.personal_meaning is not None
        assert record.phi_os_meaning != record.personal_meaning

    def test_P2_phi_os_is_classifier_not_decider(self, governance):
        """P2: PHI-OS は分類するが意思決定しない。Decision に "execute" がない。"""
        event = ConflictEvent(
            term="p2_test",
            phi_os_meaning="A",
            personal_meaning="B",
            conflict_state="CONFLICT",
            conflict_reason="test",
            severity=0.9,
        )
        decision = governance.process(event)
        # Decision は分類結果のみを持つ
        assert hasattr(decision, "kind")
        assert hasattr(decision, "note")
        # 実行系のメソッドが存在しない
        assert not hasattr(decision, "execute")
        assert not hasattr(decision, "resolve_conflict")
        assert not hasattr(decision, "overwrite_meaning")

    def test_P3_ui_is_observation_only(self, bridge):
        """P3: UI は観測のみ。Graph / Node に state 変更メソッドがない。"""
        bridge.register_mapping("p3_term", phi_os_meaning="x", personal_meaning="y")
        records = bridge.registry.list_all()
        graph = build_graph_from_records(records)
        node = graph.get_node("p3_term")

        # Graph に書き込み系メソッドが存在しない（状態変更系）
        assert not hasattr(graph, "resolve")
        assert not hasattr(graph, "merge_meanings")
        assert not hasattr(graph, "delete_conflict")

        # Node も同様
        assert not hasattr(node, "resolve")
        assert not hasattr(node, "set_state")

    def test_P4_bridge_is_sole_state_authority(self, bridge):
        """P4: Bridge だけが state を変更できる（LOCK/UNLOCK 権限）。"""
        bridge.register_mapping("p4_term", phi_os_meaning="def_a", personal_meaning="def_b")

        # Bridge が LOCK する
        bridge.lock("p4_term")
        assert bridge.registry.get("p4_term").state == ConflictState.LOCKED

        # Bridge が UNLOCK する
        bridge.unlock("p4_term")
        assert bridge.registry.get("p4_term").state != ConflictState.LOCKED
