# main.py
# MoCKA v1.2.1+ — 運用制度OS（統合版）
# 実行: python main.py

from __future__ import annotations

from core.bridge.phi_personal_bridge import PhiPersonalBridge, ConflictInput
from core.phi.phi_bridge_governance import PhiOS
from core.cognitive.cognitive_core import CognitiveCore
from core.timeline.semantic_timeline_engine import SemanticTimelineEngine
from audit.system_audit import SystemAudit
from runtime.execution.runner import Runner
from runtime.monitoring.observer import Observer
from runtime.config.config_loader import ConfigLoader


class MoCKA:
    """
    MoCKA 運用制度OS。

    パイプライン:
        Runner → _internal_cycle → Observer → 統一出力

    層の役割:
        core    — 意味処理（変更禁止）
        runtime — 実行制御 / 観測 / 設定
        audit   — 監査のみ（判断禁止）
    """

    def __init__(self) -> None:
        self.config   = ConfigLoader()
        self.timeline = SemanticTimelineEngine()
        self.bridge   = PhiPersonalBridge()
        self.phi      = PhiOS()
        self.core     = CognitiveCore(self.timeline)
        self.audit    = SystemAudit(self.timeline)
        self.runner   = Runner(self)
        self.observer = Observer()

    def run_cycle(self, event: ConflictInput) -> dict:
        """
        公開インターフェース。
        Runnerが実行し、Observerが統一形式に変換して返す。
        """
        result = self.runner.run(event)
        return self.observer.snapshot(
            cycle_id=f"{self.runner.cycle_count:03d}",
            result=result,
        )

    def _internal_cycle(self, event: ConflictInput) -> dict:
        """
        内部パイプライン（Runnerが呼ぶ）。
        Bridge → PHI-OS → Timeline → CognitiveCore → Audit
        """
        # 1. Bridge — conflict状態評価（意味変更なし）
        conflict = self.bridge.register(event)

        # 2. PHI-OS — pure classify
        decision = self.phi.classify(conflict)

        # 3. Timeline — 追記のみ
        self.timeline.append_event(
            term=event.term,
            phi_value=event.phi_value,
            personal_value=event.personal_value,
            conflict_state=conflict.state,
            phi_decision=decision,
        )

        # 4. CognitiveCore — 観測サマリ
        state = self.core.summarize()

        # 5. Audit — 整合性・適合性検証
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

    print("=== MoCKA v1.2.1+ ===")
    print(f"CYCLE:       {result['cycle']}")
    print(f"DECISION:    {result['decision']}")
    print(f"DRIFT:       {result['drift']}")
    print(f"STABILITY:   {result['stability']}")
    print(f"AUDIT:       {result['audit']}")
    print(f"HEALTH:      {result['health']}")
