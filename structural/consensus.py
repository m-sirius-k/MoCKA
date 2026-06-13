"""
MoCKA 3.0 — Governance Layer 5 (GL5)
consensus.py

責務:
  AI間の合議・収束判定のみを担当する。
  各AIの回答生成そのものは実装しない(opinions = {agent_name: position}を受け取る)。

Consensus条件:
  agreement_score_threshold = 0.95
  max_iterations            = 10
"""

from collections import Counter
from dataclasses import dataclass, field

from grounding_engine import RepositoryGroundingEngine
from working_memory import WorkingMemoryEngine
from thinking_mode import ThinkingModeEngine
from reasoning_governance import ReasoningGovernanceEngine
from execution_governance import ExecutionGovernanceEngine

CONSENSUS_CONDITIONS = {
    "agreement_score_threshold": 0.95,  # 95%以上で収束
    "max_iterations": 10,               # 最大反復数
}


@dataclass
class RoundResult:
    iteration: int
    opinions: dict
    agreement_score: float
    majority_position: object
    converged: bool


@dataclass
class ConsensusResult:
    converged: bool
    rounds: list = field(default_factory=list)
    final_position: object = None
    reason: str = ""


class ConsensusEngine:
    """
    Agreement Score = (majority_positionを支持するAI数) / (全AI数)
    Threshold以上でconverged=True。
    max_iterations到達で未収束終了。

    合議の進行(各イテレーションでのopinions取得)と
    本Engineによる収束判定は分離する。本Engineは判定のみ行う。
    """

    def __init__(self):
        self.grounding = RepositoryGroundingEngine()
        self.wm = WorkingMemoryEngine()
        self.tm = ThinkingModeEngine()
        self.reasoning = ReasoningGovernanceEngine()
        self.execution = ExecutionGovernanceEngine()
        self.threshold = CONSENSUS_CONDITIONS["agreement_score_threshold"]
        self.max_iterations = CONSENSUS_CONDITIONS["max_iterations"]

    def agreement_score(self, opinions: dict) -> tuple:
        """
        opinions: {agent_name: position}
        多数派positionとAgreement Scoreを返す。
        """
        if not opinions:
            return None, 0.0
        counts = Counter(opinions.values())
        majority_position, majority_count = counts.most_common(1)[0]
        score = majority_count / len(opinions)
        return majority_position, score

    def evaluate_round(self, iteration: int, opinions: dict) -> RoundResult:
        majority_position, score = self.agreement_score(opinions)
        return RoundResult(
            iteration=iteration,
            opinions=dict(opinions),
            agreement_score=score,
            majority_position=majority_position,
            converged=score >= self.threshold,
        )

    def run(self, opinion_rounds: list) -> ConsensusResult:
        """
        opinion_rounds: 各イテレーションのopinions辞書のリスト
          (各イテレーションでのAI間合議結果は呼び出し側が生成する。
           本メソッドは収束判定のみを行う)

        max_iterationsを超えるラウンドは評価しない。
        """
        rounds = []
        for i, opinions in enumerate(opinion_rounds[:self.max_iterations], start=1):
            result = self.evaluate_round(i, opinions)
            rounds.append(result)
            if result.converged:
                return ConsensusResult(
                    converged=True,
                    rounds=rounds,
                    final_position=result.majority_position,
                    reason=f"converged at iteration {i} (score={result.agreement_score:.2f} "
                           f">= threshold {self.threshold})",
                )

        last = rounds[-1] if rounds else None
        return ConsensusResult(
            converged=False,
            rounds=rounds,
            final_position=last.majority_position if last else None,
            reason=f"max_iterations({self.max_iterations}) reached without convergence",
        )

    def status(self) -> dict:
        """GL1/GL2/GL3/GL6/GL7の現在状態をConsensus開始前提として取得する。"""
        grounding = self.grounding.ground("consensus_status")
        memory = self.wm.snapshot()
        mode = self.tm.get_current_mode()
        checklist = self.reasoning.enforce_pre_answer_checklist()
        return {
            "repository_root": grounding.repository_root,
            "current_branch": grounding.current_branch,
            "current_thinking_mode": mode.value if mode else None,
            "pre_answer_checklist_ok": checklist.ok,
            "consensus_conditions": dict(CONSENSUS_CONDITIONS),
        }


def main():
    engine = ConsensusEngine()

    rounds = [
        {"claude": "A", "gpt": "B", "gemini": "A"},
        {"claude": "A", "gpt": "A", "gemini": "A"},
    ]
    result = engine.run(rounds)
    print("converged:", result.converged)
    print("final_position:", result.final_position)
    print("reason:", result.reason)
    for r in result.rounds:
        print(f"  iter={r.iteration} score={r.agreement_score:.2f} converged={r.converged}")

    print()
    print(engine.status())


if __name__ == "__main__":
    main()
