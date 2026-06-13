"""
MoCKA 3.0 — Governance Layer 4 (GL4)
knowledge_mass.py

責務:
  検索順位に重要度(Mass)を組み込む。
  Score = Match x Knowledge_Mass x Current_Context

  本モジュールはRankingのみを担当する。検索処理(候補の取得)は実装しない。
  候補リスト(category + match score)を受け取り、再ランキングして返す。
"""

from dataclasses import dataclass, field

from grounding_engine import RepositoryGroundingEngine
from working_memory import WorkingMemoryEngine
from thinking_mode import ThinkingModeEngine, ThinkingMode
from reasoning_governance import ReasoningGovernanceEngine
from execution_governance import ExecutionGovernanceEngine

KNOWLEDGE_MASS = {
    "project_constitution": 1.00,
    "architecture":         0.95,
    "repository_rules":     0.90,
    "current_task":         0.85,
    "working_memory":       0.80,
    "recent_events":        0.70,
    "temporary_memo":       0.20,
}

# ThinkingModeごとのcategory別 Current_Context 重み補正
# 1.0 = 補正なし。GL3で判定したモードに応じて重視すべきcategoryを強調する。
_CONTEXT_WEIGHTS = {
    ThinkingMode.EMERGENCY: {
        "recent_events": 1.3,
        "repository_rules": 1.2,
    },
    ThinkingMode.AUDIT: {
        "repository_rules": 1.3,
        "architecture": 1.1,
    },
    ThinkingMode.IMPLEMENTATION: {
        "current_task": 1.3,
        "working_memory": 1.2,
    },
    ThinkingMode.ARCHITECTURE: {
        "architecture": 1.3,
        "project_constitution": 1.1,
    },
    ThinkingMode.VISION: {
        "project_constitution": 1.2,
        "architecture": 1.1,
    },
}


@dataclass
class ScoredCandidate:
    candidate: dict
    match: float
    mass: float
    context: float
    score: float = field(init=False)

    def __post_init__(self):
        self.score = self.match * self.mass * self.context


class KnowledgeMassEngine:
    """
    GL1(Grounding)/GL2(Working Memory)/GL3(Thinking Mode)/
    GL6(Reasoning Governance)/GL7(Execution Governance)の結果を利用し、
    候補のRankingにMassとCurrent_Contextを組み込む。

    検索処理(候補取得)は実装しない。rank()は候補リストを受け取るのみ。
    """

    def __init__(self):
        self.grounding_engine = RepositoryGroundingEngine()
        self.wm = WorkingMemoryEngine()
        self.tm = ThinkingModeEngine()
        self.reasoning = ReasoningGovernanceEngine()
        self.execution = ExecutionGovernanceEngine()

    def get_mass(self, category: str) -> float:
        return KNOWLEDGE_MASS.get(category, KNOWLEDGE_MASS["temporary_memo"])

    def get_current_context(self, category: str) -> float:
        """
        GL3の現在ThinkingModeに基づき、categoryのCurrent_Context重みを返す。
        モード未設定時は1.0(補正なし)。
        """
        mode = self.tm.get_current_mode()
        if mode is None:
            return 1.0
        return _CONTEXT_WEIGHTS.get(mode, {}).get(category, 1.0)

    def score(self, candidate: dict) -> ScoredCandidate:
        """
        candidate例: {"id": ..., "category": "working_memory", "match": 0.8, ...}
        Score = Match x Knowledge_Mass x Current_Context
        """
        category = candidate.get("category", "temporary_memo")
        match = float(candidate.get("match", 0.0))
        mass = self.get_mass(category)
        context = self.get_current_context(category)
        return ScoredCandidate(candidate=candidate, match=match, mass=mass, context=context)

    def rank(self, candidates: list) -> list:
        """
        候補リストをScore降順で並び替えて返す。
        各要素は ScoredCandidate。
        """
        scored = [self.score(c) for c in candidates]
        return sorted(scored, key=lambda sc: sc.score, reverse=True)

    def status(self) -> dict:
        """
        GL1/GL2/GL3/GL6/GL7の現在状態を取得し、Rankingの前提条件として返す。
        Repositoryに存在する情報は人間へ質問しない。
        """
        grounding = self.grounding_engine.ground("knowledge_mass_status")
        memory = self.wm.snapshot()
        mode = self.tm.get_current_mode()
        checklist = self.reasoning.enforce_pre_answer_checklist()
        return {
            "repository_root": grounding.repository_root,
            "current_branch": grounding.current_branch,
            "current_task": memory.get("current_task"),
            "current_thinking_mode": mode.value if mode else None,
            "pre_answer_checklist_ok": checklist.ok,
            "knowledge_mass": dict(KNOWLEDGE_MASS),
        }


def main():
    engine = KnowledgeMassEngine()

    candidates = [
        {"id": "constitution", "category": "project_constitution", "match": 0.6},
        {"id": "event_E058",   "category": "recent_events",         "match": 0.9},
        {"id": "memo",         "category": "temporary_memo",        "match": 0.95},
        {"id": "task_gl4",     "category": "current_task",          "match": 0.7},
    ]

    ranked = engine.rank(candidates)
    for sc in ranked:
        print(f"{sc.candidate['id']:>12}  match={sc.match:.2f} mass={sc.mass:.2f} "
              f"context={sc.context:.2f} -> score={sc.score:.4f}")

    print()
    print(engine.status())


if __name__ == "__main__":
    main()
