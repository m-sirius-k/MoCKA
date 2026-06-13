"""
MoCKA 3.0 — Self-Learning Kernel
learning_engine.py

責務:
  Feedback Loop(Phase 3-2)が生成する FeedbackProposal を解析し、
  Learning Kernelが扱える「学習アクション(LearningAction)」へ変換する。

  処理内容:
    - feedback解析: suggested_change から parameter/suggested_delta/direction を抽出
    - layer分類: target_layer + parameter を learning_registry.LEARNING_PARAM_MAP で
      Learning Stateのパラメータパスへマッピング
    - delta変換: direction(increase/decrease) と invertフラグから実際のdelta値を算出
    - learning action生成: LearningAction を構築

  weight_adjustment / reuse_weight_adjustment / memory_decay /
  intent_threshold_adjustment 以外のfeedback_type(rationale_improvement,
  memory_reinforcement, context_improvement, registry_candidate)は
  「重み更新」ではないため、本Engineではconvert()がNoneを返す
  (Learning Kernelの対象外 = 提案として保持されるが学習アクション化しない)。
"""

from typing import Optional

from learning_model import LearningAction
from learning_registry import get_param_mapping
from weight_state_store import WeightStateStore


class LearningEngine:
    def convert(
        self,
        proposal,
        state_store: Optional[WeightStateStore] = None,
    ) -> Optional[LearningAction]:
        """
        FeedbackProposalをLearningActionへ変換する。
        対応する重みパラメータが存在しない場合はNoneを返す。
        """
        suggested_change = proposal.suggested_change or {}
        weight_adjustment = suggested_change.get("weight_adjustment", {})

        parameter = weight_adjustment.get("parameter")
        suggested_delta = weight_adjustment.get("suggested_delta")
        direction = weight_adjustment.get("direction")

        if parameter is None or suggested_delta is None or direction not in ("increase", "decrease"):
            return None

        mapping = get_param_mapping(proposal.target_layer, parameter)
        if mapping is None:
            return None

        path = mapping["path"]
        invert = mapping["invert"]

        magnitude = abs(suggested_delta)
        sign = 1.0 if direction == "increase" else -1.0
        if invert:
            sign *= -1.0
        delta = sign * magnitude

        store = state_store or WeightStateStore()
        current_value = store.get_value(path)
        proposed_value = current_value + delta

        return LearningAction(
            action_id=f"LA-{proposal.feedback_id}",
            source_feedback_id=proposal.feedback_id,
            target_layer=proposal.target_layer,
            parameter=path,
            delta=delta,
            current_value=current_value,
            proposed_value=proposed_value,
            priority=self._priority_for_confidence(proposal.confidence),
            rationale=weight_adjustment.get("reason", ""),
        )

    def convert_many(self, proposals, state_store: Optional[WeightStateStore] = None):
        store = state_store or WeightStateStore()
        actions = []
        for proposal in proposals:
            action = self.convert(proposal, state_store=store)
            if action is not None:
                actions.append(action)
        return tuple(actions)

    @staticmethod
    def _priority_for_confidence(confidence: float) -> str:
        if confidence >= 0.7:
            return "high"
        if confidence >= 0.4:
            return "medium"
        return "low"
