# MoCKA/semantic/query_engine/observation_surface.py
# Phase8-4 - Observation Surface v0 (separated visualization, not UI)
#
# 契約: docs/contracts/phase8_4_observation_surface_v1.md
#
# 重要な定義: 「理解させるUI」ではなく「理解できないまま見えるUI」。
# trace_view/cluster_view/collision_view/ruling_viewは完全に分離され、
# 互いに参照・比較・統合・正規化されない(Phase8-2の非統合保証を継続)。
#
# 絶対禁止（契約4章より）:
#   - trace_viewとcluster_viewの統合・比較・差分表示
#   - 正規化表示・統一ビューの生成
#   - 派生データ・要約・スコア化の生成
#   - Orchestrator出力の加工・並び替え・フィルタリング
#   - 再計算・推論・補正

from typing import Optional, Sequence

from semantic.query_engine.data_binding import RealClusterReader
from semantic.query_engine.structural_recovery import StructuralTraceReader
from semantic.query_engine.collision_governance import GovernedCollisionRecord
from semantic.query_engine.human_gate import HumanGateRulingStore, RulingRecord
from semantic.query_engine.human_gate_interface import (
    CollisionStateTracker,
    CollisionView,
    build_collision_view,
)
from semantic.query_engine.execution_orchestrator import OrchestrationResult


def trace_view(reader: RealClusterReader, canonical_trace_id: str) -> Optional[str]:
    """Phase7-A4のcanonical解決結果のみを返す(read-only snapshot)。"""
    return reader.resolve_canonical(canonical_trace_id)


def cluster_view(reader: StructuralTraceReader, identifier: str) -> dict:
    """Phase7-B3のrecover_structure結果のみを返す(read-only snapshot)。"""
    return reader.recover_structure(identifier)


def collision_view_channel(
    collision: GovernedCollisionRecord,
    state_tracker: CollisionStateTracker,
    ruling_store: HumanGateRulingStore,
    re_detected: bool = False,
) -> CollisionView:
    """Phase7-B7のCollisionViewをそのまま返す(read-only snapshot)。"""
    return build_collision_view(collision, state_tracker, ruling_store, re_detected=re_detected)


def ruling_view(ruling_store: HumanGateRulingStore, from_cluster: str, to_cluster: str) -> Sequence[RulingRecord]:
    """Phase7-B6のruling履歴のみを返す(read-only snapshot)。"""
    return ruling_store.get_rulings(from_cluster, to_cluster)


class EventFeedMirror:
    """ExecutionOrchestratorの出力を加工せず受信順のまま保持するミラー。

    並び替え・フィルタリング・統合は一切行わない。
    """

    def __init__(self):
        self._feed: list = []

    def mirror(self, result: OrchestrationResult) -> OrchestrationResult:
        self._feed.append(result)
        return result

    def feed(self) -> Sequence[OrchestrationResult]:
        return tuple(self._feed)
