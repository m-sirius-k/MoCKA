# MoCKA/semantic/query_engine/decision_replay.py
# Phase7-B-2 - Decision Replay System v0 (skeleton)
#
# 契約: docs/contracts/decision_replay_system_contract_v1.md
#
# 責務: 意味生成の決定過程(decision_trace)を再現し、explanationを
#       不変スナップショットとして保存・比較する。
#
# 重要な区別（契約1章より）:
#   本ファイルの"Replay"は relay/replay_engine.py 等(RelayKernelの
#   状態を再構築するReplay)とは別概念であり、対象も依存層も異なる。
#   既存Relay層への変更・統合・参照は行わない。
#
# 絶対条件（契約4章より）:
#   - PHI-OSへの書き込み、cluster再計算、embedding再生成、
#     decision_traceの改変は行わない。
#   - 既存スナップショットの上書き・削除は行わない（append-only）。
#   - 既存Relay層(relay/replay_engine.py等)への変更・統合は行わない。
#
# 実データ接続(DecisionTraceReader/SnapshotStoreの具象実装)は
# Phase7-B-3以降。本ファイルはインターフェース定義+最小ロジックのみ。

from dataclasses import dataclass, field
from typing import Optional, Sequence

from semantic.query_engine.explanation_builder import ExplanationResult


@dataclass(frozen=True)
class ReplayedTrace:
    canonical_trace_id: str
    cluster_id: str
    trace_path: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class SnapshotDiff:
    snapshot_id_a: str
    snapshot_id_b: str
    changed_fields: Sequence[str] = field(default_factory=tuple)


class DecisionTraceReader:
    """decision_traceの経路(trace_path)を読み取るインターフェース。

    explanation_builder.TraceReaderと役割は近いが、Decision Replay
    Systemは契約上Meaning Query Engineに依存する独立層であるため、
    別プロトコルとして定義する(契約1章: 既存Relay層とは統合しない、
    かつPhase7-AとPhase7-Bの契約境界も保つ)。実データ接続は
    Phase7-B-3で具象実装を注入する。
    """

    def get_trace_path(self, cluster_id: str) -> Sequence[str]:
        raise NotImplementedError


class SnapshotStore:
    """ExplanationResultの不変スナップショットを保存するインターフェース。

    append-onlyを構造的に保証する: 上書き・削除メソッドは存在しない。
    実データ接続はPhase7-B-3で具象実装を注入する。
    """

    def save_snapshot(self, canonical_trace_id: str, explanation: ExplanationResult) -> str:
        """新規スナップショットを追加し、新規snapshot_idを返す。"""
        raise NotImplementedError

    def get_snapshot(self, snapshot_id: str) -> Optional[ExplanationResult]:
        raise NotImplementedError

    def list_snapshots(self, canonical_trace_id: str) -> Sequence[str]:
        """時系列順(古い->新しい)のsnapshot_id一覧を返す。"""
        raise NotImplementedError


class DecisionReplaySystem:
    """読み取り+append-only追加のみのDecision Replay System。

    cluster再計算・embedding再生成・decision_traceの改変・
    既存スナップショットの上書き・既存Relay層への変更は一切行わない。
    """

    def __init__(self, trace_reader: DecisionTraceReader, snapshot_store: SnapshotStore):
        self._trace_reader = trace_reader
        self._snapshot_store = snapshot_store

    def replay_decision(self, canonical_trace_id: str, cluster_id: str) -> ReplayedTrace:
        """canonical anchorを起点にtrace_pathを再現する(読み取りのみ)。"""
        trace_path = self._trace_reader.get_trace_path(cluster_id)
        return ReplayedTrace(
            canonical_trace_id=canonical_trace_id,
            cluster_id=cluster_id,
            trace_path=tuple(trace_path),
        )

    def snapshot_explanation(self, canonical_trace_id: str, explanation: ExplanationResult) -> str:
        """ExplanationResultを不変スナップショットとして追加する(上書きしない)。"""
        return self._snapshot_store.save_snapshot(canonical_trace_id, explanation)

    def compare_snapshots(self, snapshot_id_a: str, snapshot_id_b: str) -> SnapshotDiff:
        """2つのスナップショットを比較し、差分のあるフィールド名を返す(読み取りのみ)。"""
        snap_a = self._snapshot_store.get_snapshot(snapshot_id_a)
        snap_b = self._snapshot_store.get_snapshot(snapshot_id_b)

        if snap_a is None or snap_b is None:
            return SnapshotDiff(
                snapshot_id_a=snapshot_id_a,
                snapshot_id_b=snapshot_id_b,
                changed_fields=tuple(),
            )

        changed = tuple(
            field_name
            for field_name in (
                "why_this_meaning",
                "activated_structures",
                "compression_process",
                "final_judgement",
            )
            if getattr(snap_a, field_name) != getattr(snap_b, field_name)
        )
        return SnapshotDiff(
            snapshot_id_a=snapshot_id_a,
            snapshot_id_b=snapshot_id_b,
            changed_fields=changed,
        )
