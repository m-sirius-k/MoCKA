"""
MoCKA Core Kernel — phios_integration.adapters

責務:
  Memory / Relay / Orchestra 接続インターフェースのno-op実装(Adapter)。

  すべて「未実行・未保存・未制御」であり、副作用を持たない。
  将来の実装(File IO/DB/実通信/実行エンジン接続)へのHookとしてのみ存在する。
"""

from .external_interfaces import (
    MemoryWriterInterface,
    OrchestraAdapterInterface,
    RelayAdapterInterface,
)


class NoOpMemoryAdapter(MemoryWriterInterface):
    """Memory接続のno-op実装。実保存・File IO・DB接続は行わない。"""

    def write_analysis(self, result) -> None:
        return None

    def write_context(self, context) -> None:
        return None

    def write_observation(self, observation) -> None:
        return None


class NoOpRelayAdapter(RelayAdapterInterface):
    """Relay接続のno-op実装。永続化・UI連携・実通信は行わない。"""

    def push_context(self, context) -> None:
        return None

    def pull_context(self, session_id):
        return None

    def merge_context(self, context_a, context_b):
        """ダミーのマージ結果を返す。実際の統合ロジックは持たない。"""
        return {
            "merged": False,
            "context_a": context_a,
            "context_b": context_b,
        }


class NoOpOrchestraAdapter(OrchestraAdapterInterface):
    """Orchestra接続のno-op実装。実行・LLM呼び出し・Workflow制御は行わない。"""

    def plan(self, observation):
        """ダミーの計画案を返す。実行は行わない。"""
        return {"status": "not_implemented", "plan": None}

    def suggest_actions(self, context):
        """ダミーの提案アクション群を返す。実行は行わない。"""
        return {"status": "not_implemented", "actions": []}

    def evaluate_state(self, cognitive_state):
        """ダミーの評価結果を返す。状態遷移制御は行わない。"""
        return {"status": "not_implemented", "evaluation": None}
