# MoCKA/semantic/query_engine/collision_governance.py
# Phase7-B-5 - Collision Governance v0 (authority design, not resolution)
#
# 契約: docs/contracts/phase7_b5_collision_governance_v1.md
#
# 重要な前提: 「衝突解消=アルゴリズム」ではなく「衝突解消=権限設計」。
# どちらのソースが正しいかをデータでは決められないため、本ファイルは
# 衝突を分類・記録・エスカレーションするだけであり、一切解消しない。
#
# 絶対禁止（契約3章より、完全禁止）:
#   - 自動マージ
#   - スコアリングによる決定
#   - "最適解"生成
#   - collision logの圧縮・削除
#
# 既存OrderNormalizer/StructuralTraceReaderのメソッド・出力構造は
# 変更しない。

from dataclasses import dataclass, field
from typing import Sequence

from semantic.query_engine.order_normalizer import OrderCollision

CLASSIFICATION_STRUCTURAL = "structural_collision"
CLASSIFICATION_SEMANTIC = "semantic_collision"
CLASSIFICATION_SOURCE = "source_collision"

STATE_UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class GovernedCollisionRecord:
    from_cluster: str
    to_cluster: str
    classification: str
    algorithmic_note: str
    relation_types: Sequence[str] = field(default_factory=tuple)
    sources: Sequence[str] = field(default_factory=tuple)
    state: str = STATE_UNRESOLVED
    escalated: bool = False


class CollisionEscalationHook:
    """Human Gateへのエスカレーション通知インターフェース(Layer C入口)。

    v1では記録のみ。実際の通知手段(Slack/メール等)の具象実装は将来
    フェーズ。escalate()内で衝突を解消・状態変更することは恒久的に禁止。
    drift_monitor.HumanGateHookとは型を分離する(対象が異なるため統合しない)。
    """

    def escalate(self, records: Sequence[GovernedCollisionRecord]) -> None:
        pass


class CollisionClassifier:
    """OrderCollisionを3分類のいずれかに機械的に振り分ける(Layer A・提案のみ)。

    分類はフィールド欠落等の構造的事実に基づくものであり、「どちらが
    正しいか」の意味判断は一切含まない。algorithmic_noteは参考情報に
    過ぎず、採用すべき結論ではない。
    """

    def classify(self, collision: OrderCollision) -> "tuple[str, str]":
        relation_types = tuple(collision.relation_types)
        sources = tuple(collision.sources)

        if len(relation_types) != len(sources) or not relation_types:
            return (
                CLASSIFICATION_STRUCTURAL,
                "structure mismatch: relation_types/sources count differs or empty (advisory only)",
            )

        if {"decision_trace", "merge_graph"} == set(sources) and len(set(relation_types)) > 1:
            return (
                CLASSIFICATION_SOURCE,
                "decision_trace.json carries diameter_limit_hit while merge_graph.json does not; "
                "discrepancy is explainable by field availability difference (advisory only)",
            )

        return (
            CLASSIFICATION_SEMANTIC,
            "relation_types differ without an explainable field-availability gap (advisory only)",
        )


class CollisionGovernor:
    """OrderCollisionを分類・記録・エスカレーションするだけの統治層。

    解消(state遷移)は行わない。state は常に"unresolved"で開始する。
    """

    def __init__(
        self,
        classifier: "CollisionClassifier | None" = None,
        escalation_hook: "CollisionEscalationHook | None" = None,
    ):
        self._classifier = classifier or CollisionClassifier()
        self._escalation_hook = escalation_hook or CollisionEscalationHook()

    def govern(self, collisions: Sequence[OrderCollision]) -> Sequence[GovernedCollisionRecord]:
        records = []
        for collision in collisions:
            classification, note = self._classifier.classify(collision)
            records.append(
                GovernedCollisionRecord(
                    from_cluster=collision.from_cluster,
                    to_cluster=collision.to_cluster,
                    classification=classification,
                    algorithmic_note=note,
                    relation_types=collision.relation_types,
                    sources=collision.sources,
                    state=STATE_UNRESOLVED,
                    escalated=True,
                )
            )

        if records:
            self._escalation_hook.escalate(records)

        return tuple(records)
