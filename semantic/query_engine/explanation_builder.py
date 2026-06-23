# MoCKA/semantic/query_engine/explanation_builder.py
# Phase7-A-3 - Explanation Builder v0 (skeleton, Meaning Reconstruction Layer)
#
# 契約: docs/contracts/explanation_builder_contract_v1.md
#
# 責務: canonical(主軸・必須) / intent(補強・任意) / trace_path(必須) から
#       4要素固定順の説明(why_this_meaning / activated_structures /
#       compression_process / final_judgement)を読み取りのみで再構築する。
#
# 絶対条件（契約3章・4章より）:
#   - PHI-OSへの書き込み、cluster再計算、embedding再生成、
#     decision_traceの再実行・改変は行わない。
#   - canonicalが未確定(found=False)の場合は呼び出し不可。
#   - trace_pathが取得できない場合はINSUFFICIENT_TRACEを返す。
#   - activated_structuresはintent結果のうちcanonicalのcluster_idと
#     一致するものだけを採用する（契約3章「intent側のnoise除去」）。
#
# 実データ接続(TraceReaderの具象実装)はまだ行わない。
# 理由: 意味の形(本契約が定義する4要素の出力構造)が確定する前に
# データ層へ降りると、後から意味の形を変えられなくなる(契約5章)。

from dataclasses import dataclass, field
from typing import Optional, Sequence

from semantic.query_engine.meaning_query_engine import (
    CanonicalSearchResult,
    IntentSearchResult,
)

INSUFFICIENT_TRACE = "INSUFFICIENT_TRACE"


@dataclass(frozen=True)
class ExplanationResult:
    why_this_meaning: str
    activated_structures: Sequence[str] = field(default_factory=tuple)
    compression_process: Sequence[str] = field(default_factory=tuple)
    final_judgement: str = ""
    error: Optional[str] = None


class TraceReader:
    """decision_traceの経路(trace_path)を読み取るインターフェース。

    実データ接続はPhase7-A-4で具象実装を注入する。本クラスは
    read-onlyのプロトコル定義のみ。
    """

    def get_trace_path(self, cluster_id: str) -> Sequence[str]:
        raise NotImplementedError


class ExplanationBuilder:
    """読み取り専用のExplanation Builder(Meaning Reconstruction Layer)。

    cluster再計算・embedding再生成・decision_traceの改変・
    PHI-OSへの書き込みは一切行わない。
    """

    def __init__(self, trace_reader: TraceReader):
        self._trace_reader = trace_reader

    def build(
        self,
        canonical: CanonicalSearchResult,
        trace_path: Optional[Sequence[str]] = None,
        intent: Optional[IntentSearchResult] = None,
    ) -> ExplanationResult:
        if not canonical.found or canonical.cluster_id is None:
            return ExplanationResult(
                why_this_meaning="",
                final_judgement="",
                error="CANONICAL_NOT_FOUND",
            )

        resolved_trace_path = (
            trace_path
            if trace_path is not None
            else self._trace_reader.get_trace_path(canonical.cluster_id)
        )
        if not resolved_trace_path:
            return ExplanationResult(
                why_this_meaning="",
                final_judgement="",
                error=INSUFFICIENT_TRACE,
            )

        activated_structures = self._activated_structures(canonical, intent)

        why_this_meaning = self._why_this_meaning(canonical, resolved_trace_path)
        compression_process = tuple(resolved_trace_path)
        final_judgement = self._final_judgement(
            canonical, activated_structures, compression_process
        )

        return ExplanationResult(
            why_this_meaning=why_this_meaning,
            activated_structures=activated_structures,
            compression_process=compression_process,
            final_judgement=final_judgement,
        )

    def _activated_structures(
        self,
        canonical: CanonicalSearchResult,
        intent: Optional[IntentSearchResult],
    ) -> Sequence[str]:
        if intent is None:
            return tuple()
        return tuple(
            ref for ref in intent.cluster_refs if ref == canonical.cluster_id
        )

    def _why_this_meaning(
        self, canonical: CanonicalSearchResult, trace_path: Sequence[str]
    ) -> str:
        return (
            f"cluster {canonical.cluster_id} is reached via trace path: "
            f"{' -> '.join(trace_path)}"
        )

    def _final_judgement(
        self,
        canonical: CanonicalSearchResult,
        activated_structures: Sequence[str],
        compression_process: Sequence[str],
    ) -> str:
        structure_note = (
            "with intent-aligned structure"
            if activated_structures
            else "with no intent-aligned structure"
        )
        return (
            f"cluster {canonical.cluster_id} confirmed via "
            f"{len(compression_process)}-step trace, {structure_note}"
        )
