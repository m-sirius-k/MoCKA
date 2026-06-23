# MoCKA/semantic/query_engine/projection_result.py
# Phase9-2 - Semantic Projection Layer v0 (structure only, no algorithm)
#
# 契約: docs/contracts/phase9_1_semantic_projection_v1.md (2章・5章)
#
# 重要な前提: ProjectionResultはcandidatesをそのまま束ねるだけの
# 戻り値型である。単一候補への収束(best選択・自動採択)は構造的に
# 表現しない(フィールドは常にSequence、単一値フィールドは持たない)。

from dataclasses import dataclass, field
from typing import Sequence, Union

from semantic.query_engine.projection_candidate import EventCandidate, NLCandidate

DIRECTION_NL_TO_EVENT = "nl_to_event"
DIRECTION_EVENT_TO_NL = "event_to_nl"


@dataclass(frozen=True)
class ProjectionResult:
    direction: str
    query: str
    candidates: Sequence[Union[EventCandidate, NLCandidate]] = field(default_factory=tuple)
