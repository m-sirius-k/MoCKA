"""
MoCKA Core Kernel — phios_integration.external_interfaces

責務:
  Memory / Relay / Orchestra への将来接続のためのインターフェース(ABC)を
  定義する。

  本Phaseではインターフェース定義とAdapter構造(no-op実装)のみを導入し、
  実データ保存・実通信・実行制御は一切行わない。

データフロー(将来):
  Event -> PHI-OS -> Prism -> AnalysisResult
    -> MemoryAdapter (no-op)
    -> RelayAdapter (no-op)
    -> OrchestraAdapter (no-op)
"""

from abc import ABC, abstractmethod


class MemoryWriterInterface(ABC):
    """将来、Prism/PHI-OS出力をMemoryへ書き込むためのインターフェース。

    実保存・DB接続・File IOは禁止。Mock(no-op)のみ許可。
    """

    @abstractmethod
    def write_analysis(self, result) -> None:
        """AnalysisResultを書き込む(将来実装)。"""
        raise NotImplementedError

    @abstractmethod
    def write_context(self, context) -> None:
        """Contextを書き込む(将来実装)。"""
        raise NotImplementedError

    @abstractmethod
    def write_observation(self, observation) -> None:
        """Observationを書き込む(将来実装)。"""
        raise NotImplementedError


class RelayAdapterInterface(ABC):
    """将来、セッション間でContextを引き継ぐためのインターフェース。

    永続化・UI連携・実通信は禁止。
    """

    @abstractmethod
    def push_context(self, context) -> None:
        """Contextをセッションへ送り出す(将来実装)。"""
        raise NotImplementedError

    @abstractmethod
    def pull_context(self, session_id):
        """指定セッションのContextを取得する(将来実装)。"""
        raise NotImplementedError

    @abstractmethod
    def merge_context(self, context_a, context_b):
        """2つのContextを統合する(将来実装)。"""
        raise NotImplementedError


class OrchestraAdapterInterface(ABC):
    """将来、Orchestraの実行制御と接続するためのインターフェース。

    実行・LLM呼び出し・Workflow制御は禁止。ダミー戻り値のみ許可。
    """

    @abstractmethod
    def plan(self, observation):
        """Observationから計画案を返す(将来実装、ダミー)。"""
        raise NotImplementedError

    @abstractmethod
    def suggest_actions(self, context):
        """Contextから提案アクション群を返す(将来実装、ダミー)。"""
        raise NotImplementedError

    @abstractmethod
    def evaluate_state(self, cognitive_state):
        """CognitiveStateを評価する(将来実装、ダミー)。"""
        raise NotImplementedError
