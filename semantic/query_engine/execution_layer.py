# MoCKA/semantic/query_engine/execution_layer.py
# Phase7-D-2 - Semantic Execution Layer v0 (skeleton, MeaningCycleExecutor)
#
# 契約: docs/contracts/semantic_execution_layer_contract_v1.md
#
# 責務: A(Meaning Query Engine)/B(Explanation Builder, Decision Replay
#       System)/C(Drift Monitor)の既存メソッドを契約1章の固定順で
#       呼び出し、1サイクル(Meaning Lifecycle)を実行する。
#
# 絶対条件（契約4章より）:
#   - 既存4層のクラス・メソッド署名は一切変更しない。
#   - PHI-OSへの書き込み、cluster再計算、embedding再生成、
#     decision_traceの改変、既存スナップショットの上書き・削除、
#     自動修復・自動ロールバックは行わない。
#   - 直前サイクルのConsistencyVectorはin-memory保持のみ
#     （永続化はPhase7-D-3以降で別途契約化）。
#
# 実データ接続(各層の具象Reader/Store/Hook)は行わない。
# 本ファイルはFake実装によるサイクル動作確認を前提とした最小実装。

from dataclasses import dataclass
from typing import Optional

from semantic.query_engine.meaning_query_engine import (
    MeaningQueryEngine,
    CanonicalSearchResult,
    IntentSearchResult,
)
from semantic.query_engine.explanation_builder import (
    ExplanationBuilder,
    ExplanationResult,
    INSUFFICIENT_TRACE,
)
from semantic.query_engine.decision_replay import DecisionReplaySystem
from semantic.query_engine.drift_monitor import DriftMonitor, ConsistencyVector

STATUS_OK = "OK"
STATUS_HALTED_CANONICAL_NOT_FOUND = "CYCLE_HALTED:CANONICAL_NOT_FOUND"
STATUS_HALTED_INSUFFICIENT_TRACE = "CYCLE_HALTED:INSUFFICIENT_TRACE"


@dataclass(frozen=True)
class MeaningCycleResult:
    canonical_trace_id: str
    status: str
    canonical: CanonicalSearchResult
    intent: Optional[IntentSearchResult] = None
    explanation: Optional[ExplanationResult] = None
    snapshot_id: Optional[str] = None
    drift_score: Optional[int] = None


class MeaningCycleExecutor:
    """契約1章の6ステップをA/B/C既存層に対して固定順で実行する。

    新しい意味判断ロジックは追加しない。既存層の結果を順番に
    受け渡すだけの統合層。
    """

    def __init__(
        self,
        query_engine: MeaningQueryEngine,
        explanation_builder: ExplanationBuilder,
        replay_system: DecisionReplaySystem,
        drift_monitor: DriftMonitor,
    ):
        self._query_engine = query_engine
        self._explanation_builder = explanation_builder
        self._replay_system = replay_system
        self._drift_monitor = drift_monitor
        self._previous_vector: Optional[ConsistencyVector] = None

    def run_cycle(
        self,
        canonical_trace_id: str,
        intent_text_or_key: Optional[str] = None,
        detected_at: Optional[str] = None,
    ) -> MeaningCycleResult:
        # Step 1: canonical_search
        canonical = self._query_engine.canonical_search(canonical_trace_id)
        if not canonical.found:
            return MeaningCycleResult(
                canonical_trace_id=canonical_trace_id,
                status=STATUS_HALTED_CANONICAL_NOT_FOUND,
                canonical=canonical,
            )

        # Step 2: intent_search（任意）
        intent: Optional[IntentSearchResult] = None
        if intent_text_or_key is not None:
            intent = self._query_engine.intent_search(intent_text_or_key, anchor=canonical)

        # Step 3: explanation生成
        explanation = self._explanation_builder.build(canonical, intent=intent)
        if explanation.error == INSUFFICIENT_TRACE:
            return MeaningCycleResult(
                canonical_trace_id=canonical_trace_id,
                status=STATUS_HALTED_INSUFFICIENT_TRACE,
                canonical=canonical,
                intent=intent,
                explanation=explanation,
            )

        # Step 4: snapshot保存（append-only）
        snapshot_id = self._replay_system.snapshot_explanation(canonical_trace_id, explanation)

        # Step 5: ConsistencyVector構成 + drift比較（前回ベクトルが有る場合のみ）
        current_vector = ConsistencyVector(
            canonical_trace_id=canonical_trace_id,
            canonical=canonical,
            explanation=explanation,
            intent=intent,
        )
        drift_score: Optional[int] = None
        if self._previous_vector is not None:
            drift_score = self._drift_monitor.observe(
                self._previous_vector, current_vector, detected_at=detected_at or ""
            )
        self._previous_vector = current_vector

        # Step 6: MeaningCycleResult
        return MeaningCycleResult(
            canonical_trace_id=canonical_trace_id,
            status=STATUS_OK,
            canonical=canonical,
            intent=intent,
            explanation=explanation,
            snapshot_id=snapshot_id,
            drift_score=drift_score,
        )
