# MoCKA/semantic/query_engine/projection_candidate.py
# Phase9-2 - Semantic Projection Layer v0 (structure only, no algorithm)
#
# 契約: docs/contracts/phase9_1_semantic_projection_v1.md (5章)
#
# 重要な前提: ここはアルゴリズムを含まない。EventCandidate/NLCandidateは
# 「候補の形」を固定するだけであり、生成・選択・ランキングのロジックは
# Phase9-3以降に分離する。

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EventCandidate:
    cluster_id: str
    canonical_trace_id: Optional[str] = None
    rationale: Optional[str] = None


@dataclass(frozen=True)
class NLCandidate:
    identifier: str
    text: str
    source_field: str
