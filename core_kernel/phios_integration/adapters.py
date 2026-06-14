"""
MoCKA Core Kernel — phios_integration.adapters

責務:
  Memory / Relay / Orchestra 接続インターフェースのno-op実装(Adapter)。

  すべて「未実行・未保存・未制御」であり、副作用を持たない。
  将来の実装(File IO/DB/実通信/実行エンジン接続)へのHookとしてのみ存在する。
"""

from core_kernel.memory_core import MemoryStore

from .external_interfaces import (
    MemoryWriterInterface,
    OrchestraAdapterInterface,
    RelayAdapterInterface,
)
from .output_contract import _to_serializable


class NoOpMemoryAdapter(MemoryWriterInterface):
    """Memory接続のno-op実装。実保存・File IO・DB接続は行わない。"""

    def write_analysis(self, result) -> None:
        return None

    def write_context(self, context) -> None:
        return None

    def write_observation(self, observation) -> None:
        return None


class JsonMemoryAdapter(MemoryWriterInterface):
    """MemoryStore(JSON file / in-memory)を介した最小永続化Adapter。

    Prism出力(AnalysisResult/Context/Observation/CognitiveState)を
    MemoryRecord構造へ変換してMemoryStoreへ保存する。

    外部DB/Redis/Network通信/LLM/Workflow制御は行わない。
    PHI-OSはこのAdapter経由でのみMemoryへアクセスする。
    """

    def __init__(self, path=None, store: MemoryStore = None):
        """
        Args:
            path: JSONファイルのパス(省略時はin-memory fallback)
            store: 既存のMemoryStoreを直接指定する場合(省略可)
        """
        self._store = store if store is not None else MemoryStore(path=path)

    # ------------------------------------------------------------------
    # MemoryWriterInterface実装
    # ------------------------------------------------------------------

    def write_analysis(self, result, session_id: str = None) -> dict:
        return self._store.save("analysis_result", _to_serializable(result), session_id=session_id)

    def write_context(self, context, session_id: str = None) -> dict:
        return self._store.save("context", _to_serializable(context), session_id=session_id)

    def write_observation(self, observation, session_id: str = None) -> dict:
        return self._store.save("observation", _to_serializable(observation), session_id=session_id)

    # ------------------------------------------------------------------
    # 読み取りAPI(PHI-OSはこの経路でのみ参照する)
    # ------------------------------------------------------------------

    def load(self, entity_id: str):
        return self._store.load(entity_id)

    def query(self, predicate=None) -> list:
        return self._store.query(predicate)

    def list(self, session_id: str) -> list:
        return self._store.list(session_id)


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
