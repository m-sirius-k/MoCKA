"""
MoCKA 3.0 — Self-Learning Kernel
update_validator.py

責務:
  LearningActionをLearning Queueへ登録する前の安全性検証を行う。

  検証項目:
    - governance_compliance: governance_status が "PASS" であること
    - allowed_target: 学習対象パラメータがRegistryで許可されていること
    - max_delta: |delta| が MAX_DELTA 以下であること
    - bounds: 適用後の値が PARAM_BOUNDS の範囲内であること
    - risk_increase: risk_weights系パラメータを増加させる場合、
      増加量が RISK_INCREASE_LIMIT 以下であること
    - stability: 直近の適用実績から算出するstability_scoreが
      STABILITY_THRESHOLD以上であること

  いずれかの検証に失敗した場合、ValidationResult.passed=False となり、
  Learning Queueでは当該Updateのstatusが"rejected"になる
  (learning_queue.LearningQueue.enqueue参照)。
"""

from typing import Sequence

from learning_model import LearningAction, ValidationResult
from learning_registry import (
    MAX_DELTA,
    RISK_INCREASE_LIMIT,
    STABILITY_THRESHOLD,
    STABILITY_WINDOW,
    get_param_bounds,
    is_allowed_target,
    is_risk_weight,
)


class UpdateValidator:
    def validate(
        self,
        action: LearningAction,
        governance_status: str,
        recent_statuses: Sequence[str] = (),
    ) -> ValidationResult:
        checks = {}
        reasons = []

        # 1. Governance準拠
        checks["governance_compliance"] = governance_status == "PASS"
        if not checks["governance_compliance"]:
            reasons.append(
                f"governance_status='{governance_status}' is not 'PASS'"
            )

        # 2. 学習対象として許可されているか
        checks["allowed_target"] = is_allowed_target(action.parameter)
        if not checks["allowed_target"]:
            reasons.append(f"parameter '{action.parameter}' is not an allowed learning target")

        # 3. 最大変化量
        checks["max_delta"] = abs(action.delta) <= MAX_DELTA
        if not checks["max_delta"]:
            reasons.append(
                f"|delta|={abs(action.delta)} exceeds MAX_DELTA={MAX_DELTA}"
            )

        # 4. 範囲内チェック
        bounds = get_param_bounds(action.parameter)
        if bounds is not None:
            lower, upper = bounds
            checks["bounds"] = lower <= action.proposed_value <= upper
            if not checks["bounds"]:
                reasons.append(
                    f"proposed_value={action.proposed_value} is outside bounds {bounds}"
                )
        else:
            checks["bounds"] = False
            reasons.append(f"no bounds defined for parameter '{action.parameter}'")

        # 5. risk上昇防止
        if is_risk_weight(action.parameter) and action.delta > 0:
            checks["risk_increase"] = action.delta <= RISK_INCREASE_LIMIT
            if not checks["risk_increase"]:
                reasons.append(
                    f"risk weight increase delta={action.delta} exceeds "
                    f"RISK_INCREASE_LIMIT={RISK_INCREASE_LIMIT}"
                )
        else:
            checks["risk_increase"] = True

        # 6. stability
        stability_score = self.stability_score(recent_statuses)
        checks["stability"] = stability_score >= STABILITY_THRESHOLD
        if not checks["stability"]:
            reasons.append(
                f"stability_score={stability_score} is below STABILITY_THRESHOLD={STABILITY_THRESHOLD}"
            )

        passed = all(checks.values())
        return ValidationResult(passed=passed, checks=checks, reasons=tuple(reasons))

    @staticmethod
    def stability_score(recent_statuses: Sequence[str]) -> float:
        """
        直近 STABILITY_WINDOW 件のLearningUpdate.statusのうち、
        "applied"の割合が高いほどstability_scoreは低くなる
        (短期間に学習更新が集中している = 不安定とみなす)。
        履歴が無い場合は安定(1.0)とみなす。
        """
        window = recent_statuses[-STABILITY_WINDOW:]
        if not window:
            return 1.0
        applied_count = sum(1 for s in window if s == "applied")
        return max(0.0, 1.0 - (applied_count / STABILITY_WINDOW))
