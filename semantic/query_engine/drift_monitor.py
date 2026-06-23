# MoCKA/semantic/query_engine/drift_monitor.py
# Phase7-C-2 - Drift Monitor v0 (skeleton, "意味OSの自己免疫層")
#
# 契約: docs/contracts/drift_monitor_contract_v1.md
#       docs/contracts/drift_monitor_scoring_v1.md
#
# 責務: Phase7-A/Bの既存結果(canonical/intent/explanation/replay)を
#       束ねたconsistency_vectorを時系列で比較し、意味レベルのdriftを
#       検知・記録する。新しい意味は作らない。
#
# 重要な区別（drift_monitor_contract_v1.md1章より）:
#   relay/replay_audit.py(状態レベルdrift)とは別概念であり、統合しない。
#
# 絶対条件:
#   - PHI-OSへの書き込み、cluster再計算、embedding再生成、
#     decision_traceの改変は行わない。
#   - 既存スナップショットの上書き・削除は行わない（append-only）。
#   - 自動修復・自動ロールバック・自動cluster再計算は行わない。
#   - HumanGateHook.notify()は記録のみ。実際の通知手段の具象実装は
#     Phase7-C-3以降。

from dataclasses import dataclass, field
from typing import Optional, Sequence

from semantic.query_engine.meaning_query_engine import (
    CanonicalSearchResult,
    IntentSearchResult,
)
from semantic.query_engine.explanation_builder import ExplanationResult

DRIFT_WEIGHTS = {
    "canonical_drift": 3,
    "explanation_drift": 2,
    "intent_drift": 1,
}


@dataclass(frozen=True)
class ConsistencyVector:
    canonical_trace_id: str
    canonical: CanonicalSearchResult
    explanation: ExplanationResult
    intent: Optional[IntentSearchResult] = None


@dataclass(frozen=True)
class AnomalyRecord:
    canonical_trace_id: str
    drift_type: str
    detected_at: str
    before: dict
    after: dict
    weight: int


class HumanGateHook:
    """異常検知の通知インターフェース。

    v1では記録のみ。実際の通知手段(Slack/メール等)の具象実装は
    Phase7-C-3以降。notify()内でcluster再計算・自動修復・
    自動ロールバックを行うことは恒久的に禁止。
    """

    def notify(self, records: Sequence[AnomalyRecord]) -> None:
        pass


class ConsistencyEvaluator:
    """2つのConsistencyVector(前回・今回)を比較し、driftを検知する。

    新規計算・推論は行わない。読み取り比較のみ。
    """

    def evaluate(
        self,
        previous: ConsistencyVector,
        current: ConsistencyVector,
        detected_at: str,
    ) -> Sequence[AnomalyRecord]:
        records = []

        if previous.canonical.cluster_id != current.canonical.cluster_id:
            records.append(
                AnomalyRecord(
                    canonical_trace_id=current.canonical_trace_id,
                    drift_type="canonical_drift",
                    detected_at=detected_at,
                    before={"cluster_id": previous.canonical.cluster_id},
                    after={"cluster_id": current.canonical.cluster_id},
                    weight=DRIFT_WEIGHTS["canonical_drift"],
                )
            )

        if (
            previous.explanation.why_this_meaning != current.explanation.why_this_meaning
            or previous.explanation.final_judgement != current.explanation.final_judgement
        ):
            records.append(
                AnomalyRecord(
                    canonical_trace_id=current.canonical_trace_id,
                    drift_type="explanation_drift",
                    detected_at=detected_at,
                    before={
                        "why_this_meaning": previous.explanation.why_this_meaning,
                        "final_judgement": previous.explanation.final_judgement,
                    },
                    after={
                        "why_this_meaning": current.explanation.why_this_meaning,
                        "final_judgement": current.explanation.final_judgement,
                    },
                    weight=DRIFT_WEIGHTS["explanation_drift"],
                )
            )

        prev_refs = self._canonical_aligned_refs(previous)
        curr_refs = self._canonical_aligned_refs(current)
        if prev_refs != curr_refs:
            records.append(
                AnomalyRecord(
                    canonical_trace_id=current.canonical_trace_id,
                    drift_type="intent_drift",
                    detected_at=detected_at,
                    before={"aligned_refs": prev_refs},
                    after={"aligned_refs": curr_refs},
                    weight=DRIFT_WEIGHTS["intent_drift"],
                )
            )

        return tuple(records)

    def _canonical_aligned_refs(self, vector: ConsistencyVector) -> tuple:
        if vector.intent is None:
            return tuple()
        return tuple(
            ref for ref in vector.intent.cluster_refs if ref == vector.canonical.cluster_id
        )


class DriftScorer:
    """AnomalyRecord列からスコアを計算する(記録のみ、自動アクションなし)。"""

    def score(self, records: Sequence[AnomalyRecord]) -> int:
        return sum(record.weight for record in records)


class DriftMonitor:
    """ConsistencyEvaluator/DriftScorer/HumanGateHookを統合する最小構成。

    cluster再計算・embedding再生成・自動修復は一切行わない。
    """

    def __init__(
        self,
        evaluator: Optional[ConsistencyEvaluator] = None,
        scorer: Optional[DriftScorer] = None,
        human_gate_hook: Optional[HumanGateHook] = None,
    ):
        self._evaluator = evaluator or ConsistencyEvaluator()
        self._scorer = scorer or DriftScorer()
        self._human_gate_hook = human_gate_hook or HumanGateHook()
        self._records: list = []

    def observe(
        self,
        previous: ConsistencyVector,
        current: ConsistencyVector,
        detected_at: str,
    ) -> int:
        records = self._evaluator.evaluate(previous, current, detected_at)
        self._records.extend(records)
        if records:
            self._human_gate_hook.notify(records)
        return self._scorer.score(records)

    def history(self) -> Sequence[AnomalyRecord]:
        return tuple(self._records)
