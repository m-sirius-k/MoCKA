# main.py
# MoCKA v1.2.1 — 起動可能な単一制度OS
# 実行: python main.py

from __future__ import annotations

from core.bridge.phi_personal_bridge import PhiPersonalBridge, ConflictInput
from core.phi.phi_bridge_governance import PhiOS
from core.cognitive.cognitive_core import CognitiveCore
from core.timeline.semantic_timeline_engine import SemanticTimelineEngine
from audit.system_audit import SystemAudit


class MoCKA:
    """
    Bridge → PHI-OS → Timeline → CognitiveCore → Audit の
    単一パイプラインを構成する制度OS。

    設計原則:
    - 意味を変更しない
    - データは append only
    - 判断は PHI-OS のみ
    - 監査は Audit のみ
    """

    def __init__(self) -> None:
        self.timeline = SemanticTimelineEngine()
        self.bridge   = PhiPersonalBridge()
        self.phi      = PhiOS()
        self.core     = CognitiveCore(self.timeline)
        self.audit    = SystemAudit(self.timeline)

    def run_cycle(self, event: ConflictInput) -> dict:
        """
        1サイクルの処理パイプライン。
        外部イベントを受け取り、decision / state / audit を返す。
        """
        # 1. Bridge — conflict状態を評価（意味は変更しない）
        conflict = self.bridge.register(event)

        # 2. PHI-OS — pure classify（severity → decision）
        decision = self.phi.classify(conflict)

        # 3. Timeline — 追記のみ（唯一の履歴源）
        self.timeline.append_event(
            term=event.term,
            phi_value=event.phi_value,
            personal_value=event.personal_value,
            conflict_state=conflict.state,
            phi_decision=decision,
        )

        # 4. CognitiveCore — 観測サマリ生成（データ変更なし）
        state = self.core.summarize()

        # 5. Audit — 整合性・安定性検証
        report = self.audit.check(state)

        return {
            "decision": decision,
            "state":    state,
            "audit":    report,
        }


if __name__ == "__main__":
    system = MoCKA()

    result = system.run_cycle(
        ConflictInput(
            term="auth",
            phi_value="認証制度",
            personal_value="ログイン",
            severity=0.6,
        )
    )

    print("=== MoCKA v1.2.1 ===")
    print(f"DECISION:    {result['decision']}")
    print(f"STABILITY:   {result['state']['stability']}")
    print(f"DRIFT:       {result['state']['drift']}")
    print(f"AUDIT:       {result['audit']['status']}")
    print(f"CONSISTENCY: {result['audit']['consistency']}")
