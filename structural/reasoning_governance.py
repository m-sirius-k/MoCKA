import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
MoCKA 3.0 — Governance Layer 6 (GL6)
reasoning_governance.py

責務:
  回答開始前の推論順序を制度として固定する。
  推論そのものは実装しない。GL1/GL2/GL3を参照し、
  「回答を開始してよいか」を判定するのみ。
"""

from dataclasses import dataclass, field

from grounding_engine import RepositoryGroundingEngine
from working_memory import WorkingMemoryEngine
from thinking_mode import ThinkingModeEngine

MANDATORY_REASONING_ORDER = [
    "task_receive",
    "working_memory",
    "prohibited_rules",
    "repository_grounding",
    "repository_structure",
    "repository_rules",
    "current_event",
    "current_thinking_mode",
    "knowledge_mass_ranking",
    "reasoning",
    "answer_generation",
]

# 回答開始条件: 以下が完了するまで回答開始禁止
REQUIRED_BEFORE_ANSWER = [
    "repository_grounding",
    "working_memory",
    "current_mode",
    "current_event",
    "current_constraints",
]


@dataclass
class ValidationResult:
    ok: bool
    missing: list = field(default_factory=list)
    detail: str = ""


@dataclass
class ChecklistResult:
    ok: bool
    checklist: dict = field(default_factory=dict)
    missing: list = field(default_factory=list)


class ReasoningGovernanceEngine:
    """
    順序は固定。省略禁止。
    Repositoryに存在する情報は絶対に人間へ質問しない。
    """

    def __init__(self):
        self.grounding = RepositoryGroundingEngine()
        self.wm = WorkingMemoryEngine()
        self.tm = ThinkingModeEngine()

    def validate_reasoning_sequence(self, executed_steps: list) -> ValidationResult:
        """
        executed_stepsがMANDATORY_REASONING_ORDERの
        相対順序を保っているかを検証する。
        (一部省略は許容しないが、未到達ステップは末尾とみなす)
        """
        order_index = {step: i for i, step in enumerate(MANDATORY_REASONING_ORDER)}

        unknown = [s for s in executed_steps if s not in order_index]
        if unknown:
            return ValidationResult(
                ok=False, missing=unknown,
                detail=f"unknown reasoning steps: {unknown}",
            )

        last = -1
        for step in executed_steps:
            idx = order_index[step]
            if idx < last:
                return ValidationResult(
                    ok=False,
                    missing=[step],
                    detail=f"step '{step}' executed out of order",
                )
            last = idx

        return ValidationResult(ok=True)

    def enforce_pre_answer_checklist(self) -> ChecklistResult:
        """
        REQUIRED_BEFORE_ANSWERの各条件をGL1/GL2/GL3から取得し、
        全て満たされているかを判定する。
        """
        checklist = {}

        # repository_grounding (GL1)
        try:
            grounding = self.grounding.ground("pre_answer_checklist")
            checklist["repository_grounding"] = bool(grounding.repository_root)
        except Exception:
            checklist["repository_grounding"] = False

        # working_memory (GL2)
        memory = self.wm.snapshot()
        checklist["working_memory"] = bool(memory.get("current_repository"))

        # current_mode (GL3)
        mode = self.tm.get_current_mode()
        checklist["current_mode"] = mode is not None

        # current_event (GL2)
        checklist["current_event"] = memory.get("current_event") is not None

        # current_constraints (GL2)
        checklist["current_constraints"] = (
            memory.get("current_constraints") is not None
            or memory.get("current_prohibited_rules") is not None
        )

        missing = [k for k in REQUIRED_BEFORE_ANSWER if not checklist.get(k)]
        return ChecklistResult(ok=not missing, checklist=checklist, missing=missing)


def main():
    engine = ReasoningGovernanceEngine()

    seq = MANDATORY_REASONING_ORDER[:5]
    print("sequence valid:", engine.validate_reasoning_sequence(seq).ok)

    result = engine.enforce_pre_answer_checklist()
    print("pre-answer ok:", result.ok)
    print("checklist:", result.checklist)
    print("missing:", result.missing)


if __name__ == "__main__":
    main()
