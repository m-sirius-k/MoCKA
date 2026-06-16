# bridge/tests/test_phi_ui_integration.py
# PHI-OS統治層 + Conflict UI 統合テスト
#
# 検証フロー: bridge → ConflictEvent → PHI-OS process() → Decision → UI render()

import sys, os, io
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest

from bridge.conflict_types import BridgeRecord, ConflictState
from bridge.conflict_engine import ConflictEngine
from bridge.mapping_registry import MappingRegistry
from bridge.phi_personal_bridge import PhiPersonalBridge

from phi_os.phi_bridge_governance import (
    ConflictEvent,
    Decision,
    DecisionKind,
    PhiBridgeGovernance,
    event_from_bridge_record,
    severity_from_state,
)
from ui.conflict_view_model import (
    ConflictVisualNode,
    ConflictEdge,
    ConflictGraph,
    build_graph_from_records,
)
from ui.conflict_renderer import ConflictRenderer


# ─── フィクスチャ ──────────────────────────────────────────────────────────────

@pytest.fixture
def governance():
    return PhiBridgeGovernance()


@pytest.fixture
def bridge(tmp_path):
    registry = MappingRegistry(db_path=str(tmp_path / "integration.db"))
    b = PhiPersonalBridge(registry=registry, engine=ConflictEngine())
    yield b
    b.close()


def _make_event(term: str, severity: float, state: str = "CONFLICT") -> ConflictEvent:
    return ConflictEvent(
        term=term,
        phi_os_meaning="PHI側の定義",
        personal_meaning="Personal側の定義",
        conflict_state=state,
        conflict_reason="テスト用衝突",
        severity=severity,
    )


# ─── T1: ConflictEvent → Decision 変換 ────────────────────────────────────────

class TestDecisionPipeline:

    def test_event_converts_to_decision(self, governance):
        """ConflictEvent が Decision に変換される"""
        event = _make_event("evolution", severity=0.9)
        decision = governance.process(event)
        assert isinstance(decision, Decision)
        assert decision.term == "evolution"
        assert decision.event_id == event.event_id

    def test_decision_is_logged(self, governance):
        """Decision はログに保持される"""
        event = _make_event("term_a", severity=0.5)
        governance.process(event)
        assert len(governance.decisions()) == 1
        assert governance.decisions()[0].term == "term_a"

    def test_decision_does_not_modify_meanings(self, governance):
        """Decision 生成は意味を変更しない"""
        event = _make_event("immutable", severity=0.8)
        decision = governance.process(event)
        assert event.phi_os_meaning == "PHI側の定義"
        assert event.personal_meaning == "Personal側の定義"


# ─── T1: Severity ベース3分岐 ─────────────────────────────────────────────────

class TestSeverityRouting:

    def test_low_severity_observe(self, governance):
        """severity < 0.3 → OBSERVE"""
        event = _make_event("low_term", severity=0.1, state="DRIFT")
        decision = governance.process(event)
        assert decision.kind == DecisionKind.OBSERVE

    def test_boundary_observe(self, governance):
        """severity = 0.29 → OBSERVE"""
        decision = governance.process(_make_event("x", severity=0.29))
        assert decision.kind == DecisionKind.OBSERVE

    def test_mid_severity_tag(self, governance):
        """0.3 <= severity < 0.7 → TAG"""
        event = _make_event("mid_term", severity=0.5)
        decision = governance.process(event)
        assert decision.kind == DecisionKind.TAG

    def test_boundary_tag_low(self, governance):
        """severity = 0.3 → TAG"""
        decision = governance.process(_make_event("y", severity=0.3))
        assert decision.kind == DecisionKind.TAG

    def test_boundary_tag_high(self, governance):
        """severity = 0.69 → TAG"""
        decision = governance.process(_make_event("z", severity=0.69))
        assert decision.kind == DecisionKind.TAG

    def test_high_severity_route(self, governance):
        """severity >= 0.7 → ROUTE"""
        event = _make_event("high_term", severity=0.9)
        decision = governance.process(event)
        assert decision.kind == DecisionKind.ROUTE

    def test_boundary_route(self, governance):
        """severity = 0.7 → ROUTE"""
        decision = governance.process(_make_event("w", severity=0.7))
        assert decision.kind == DecisionKind.ROUTE

    def test_filter_by_kind(self, governance):
        """DecisionKind でフィルタ取得できる"""
        governance.process(_make_event("a", severity=0.1))
        governance.process(_make_event("b", severity=0.5))
        governance.process(_make_event("c", severity=0.9))
        assert len(governance.decisions_by_kind(DecisionKind.OBSERVE)) == 1
        assert len(governance.decisions_by_kind(DecisionKind.TAG))     == 1
        assert len(governance.decisions_by_kind(DecisionKind.ROUTE))   == 1


# ─── T2: UI Node/Edge 描画 ────────────────────────────────────────────────────

class TestUIRendering:

    def _make_node(self, term: str, state: str, severity: float = 0.5) -> ConflictVisualNode:
        return ConflictVisualNode(
            term=term,
            phi_value=f"PHI:{term}",
            personal_value=f"PER:{term}",
            state=state,
            severity=severity,
        )

    def test_node_renders_required_fields(self):
        """Node 描画が TERM/PHI/PERSONAL/STATE/SEVERITY を含む"""
        node = self._make_node("concept", "CONFLICT", severity=0.9)
        buf = io.StringIO()
        renderer = ConflictRenderer(out=buf)
        renderer.render_node(node)
        output = buf.getvalue()

        assert "concept" in output
        assert "PHI:concept" in output
        assert "PER:concept" in output
        assert "CONFLICT" in output
        assert "0.900" in output

    def test_edge_renders_in_graph(self):
        """Edge がグラフ描画に含まれる"""
        graph = ConflictGraph()
        graph.add_node(self._make_node("alpha", "NORMAL"))
        graph.add_node(self._make_node("beta", "DRIFT"))
        graph.add_edge(ConflictEdge(source_term="alpha", target_term="beta", relation="DEPENDS_ON"))

        buf = io.StringIO()
        ConflictRenderer(out=buf).render_graph(graph)
        output = buf.getvalue()

        assert "alpha" in output
        assert "beta" in output
        assert "DEPENDS_ON" in output

    def test_render_does_not_modify_graph(self):
        """render は Graph を変更しない"""
        graph = ConflictGraph()
        graph.add_node(self._make_node("immutable_node", "NORMAL"))

        buf = io.StringIO()
        ConflictRenderer(out=buf).render_graph(graph)

        # render 後もノードが同じ
        node = graph.get_node("immutable_node")
        assert node is not None
        assert node.state == "NORMAL"
        assert node.phi_value == "PHI:immutable_node"

    def test_conflict_only_render(self):
        """render_conflicts_only は CONFLICT のみ出力する"""
        graph = ConflictGraph()
        graph.add_node(self._make_node("c1", "CONFLICT"))
        graph.add_node(self._make_node("n1", "NORMAL"))

        buf = io.StringIO()
        ConflictRenderer(out=buf).render_conflicts_only(graph)
        output = buf.getvalue()

        assert "c1" in output
        assert "n1" not in output


# ─── T3: bridge → PHI-OS → UI フロー ──────────────────────────────────────────

class TestFullIntegration:

    def test_full_pipeline(self, bridge):
        """bridge → ConflictEvent → Decision → Graph → render の完全フロー"""
        # 1. Bridge に衝突 term を登録
        bridge.register_mapping(
            "gravity",
            phi_os_meaning="意味場の重力崩壊現象 — 語彙が引力を失い別の意味圏に落下する",
            personal_meaning="物体を地面に引っ張る物理的な力",
        )

        # 2. Bridge レコードから ConflictEvent 生成
        record = bridge.registry.get("gravity")
        event = event_from_bridge_record(record)
        assert event.severity == severity_from_state(record.state.value)

        # 3. PHI-OS 統治層で Decision 生成
        gov = PhiBridgeGovernance()
        decision = gov.process(event)
        assert decision.kind in (DecisionKind.TAG, DecisionKind.ROUTE, DecisionKind.OBSERVE)

        # 4. Graph 構築
        records = bridge.registry.list_all()
        graph = build_graph_from_records(records)
        node = graph.get_node("gravity")
        assert node is not None
        assert node.phi_value is not None
        assert node.personal_value is not None

        # 5. Renderer — 変更なしで出力
        buf = io.StringIO()
        ConflictRenderer(out=buf).render_graph(graph)
        output = buf.getvalue()
        assert "gravity" in output
        assert node.state in output

    def test_conflict_is_not_resolved_through_pipeline(self, bridge):
        """パイプライン通過後も衝突は解決されない"""
        bridge.register_mapping(
            "disputed",
            phi_os_meaning="完全に異質な定義X",
            personal_meaning="完全に異質な定義Y",
        )
        record = bridge.registry.get("disputed")
        original_state = record.state.value

        # PHI-OS 通過
        gov = PhiBridgeGovernance()
        gov.process(event_from_bridge_record(record))

        # Bridge の state が変わっていないこと
        after = bridge.registry.get("disputed")
        assert after.state.value == original_state

    def test_phi_and_personal_preserved_after_full_flow(self, bridge):
        """フロー後も PHI / Personal 両値が保持される"""
        phi_def = "意味場の中の引力的凝集点"
        per_def = "自分が信じている核心的な概念"
        bridge.register_mapping("core", phi_os_meaning=phi_def, personal_meaning=per_def)

        records = bridge.registry.list_all()
        graph = build_graph_from_records(records)
        node = graph.get_node("core")

        assert node.phi_value == phi_def
        assert node.personal_value == per_def
