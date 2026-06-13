"""
MoCKA 3.0 — Governance Layer 3 (GL3)
thinking_mode.py

責務:
  現在どの思考モードで動くべきかを判定し、
  そのモードに適合しない行動を抑制する。

  Thinking Modeは単なるフラグではなく、推論の前提条件として扱う。
  モード変更は明示的な状態遷移(GL2 Working Memory更新)で行う。
  モード判定と実際の推論処理は分離する(本モジュールは判定/検証のみ)。
"""

import re
from enum import Enum

from working_memory import WorkingMemoryEngine


class ThinkingMode(Enum):
    VISION         = "vision"          # 未来構想
    ARCHITECTURE   = "architecture"    # 制度設計
    IMPLEMENTATION = "implementation"  # コード実装
    AUDIT          = "audit"           # 検証
    EMERGENCY      = "emergency"       # 障害対応


# モード判定のためのキーワード(優先順位順)
_MODE_KEYWORDS = [
    (ThinkingMode.EMERGENCY, [
        "incident", "インシデント", "障害", "緊急", "rollback", "down",
    ]),
    (ThinkingMode.AUDIT, [
        "audit", "監査", "review", "レビュー", "verify", "検証", "確認",
    ]),
    (ThinkingMode.IMPLEMENTATION, [
        "implement", "実装", "fix", "修正", "commit", "code", "コード",
    ]),
    (ThinkingMode.VISION, [
        "vision", "構想", "future", "将来", "roadmap", "ロードマップ",
    ]),
    (ThinkingMode.ARCHITECTURE, [
        "architecture", "design", "設計", "engine", "エンジン", "plan", "計画",
    ]),
]

# 各モードで禁止される行動
_FORBIDDEN_ACTIONS = {
    ThinkingMode.VISION: {
        "write_code", "edit_file", "git_commit",
    },
    ThinkingMode.ARCHITECTURE: {
        "write_code", "git_commit",
    },
    ThinkingMode.IMPLEMENTATION: {
        "speculate_without_grounding",
    },
    ThinkingMode.AUDIT: {
        "write_code", "edit_file", "git_commit",
    },
    ThinkingMode.EMERGENCY: set(),
}


class ThinkingModeEngine:
    """
    回答前に現在Modeを判定する。
    Modeが変われば推論方法も変更する。
    """

    def __init__(self):
        self.wm = WorkingMemoryEngine()

    def detect_mode(self, task: str, context: dict | None = None) -> ThinkingMode:
        """
        taskおよびcontextからThinkingModeを判定する。
        判定結果はGL2 Working Memoryへ反映しない(検出のみ)。
        反映は明示的な状態遷移としてset_mode()で行う。
        """
        text = task.lower()
        if context:
            text += " " + " ".join(str(v).lower() for v in context.values())

        for mode, keywords in _MODE_KEYWORDS:
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw.lower()) + r"\b", text):
                    return mode

        return ThinkingMode.IMPLEMENTATION

    def get_current_mode(self) -> ThinkingMode | None:
        """GL2 Working Memoryに記録された現在のモードを取得する。"""
        memory = self.wm.snapshot()
        value = memory.get("current_thinking_mode")
        if value is None:
            return None
        return ThinkingMode(value)

    def set_mode(self, mode: ThinkingMode, event: str) -> dict:
        """
        明示的な状態遷移としてモードをGL2へ記録する。
        毎回答での暗黙的な変更は禁止。
        """
        return self.wm.update(event, {"current_thinking_mode": mode.value})

    def validate_action_for_mode(self, action: str, mode: ThinkingMode | None = None) -> bool:
        """
        actionが現在モードで許可されているかを検証する。
        許可されていない場合はFalseを返す(=警告対象)。
        """
        if mode is None:
            mode = self.get_current_mode()
        if mode is None:
            return True
        return action not in _FORBIDDEN_ACTIONS.get(mode, set())


def main():
    engine = ThinkingModeEngine()
    mode = engine.detect_mode("GL3 Thinking Mode Engine implementation")
    print("detected mode:", mode.value)
    print("write_code allowed in IMPLEMENTATION:",
          engine.validate_action_for_mode("write_code", ThinkingMode.IMPLEMENTATION))
    print("write_code allowed in AUDIT:",
          engine.validate_action_for_mode("write_code", ThinkingMode.AUDIT))


if __name__ == "__main__":
    main()
