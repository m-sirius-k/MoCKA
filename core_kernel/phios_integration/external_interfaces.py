"""
MoCKA Core Kernel — phios_integration.external_interfaces

責務:
  将来のMemory / Relay / Orchestra連携のための接続インターフェースを
  定義する(未実装)。

  本Phaseではインターフェースの定義のみを行い、実装・呼び出し・
  接続配線は一切行わない。具象クラスは将来のPhaseで追加される。
"""

from abc import ABC, abstractmethod


class MemoryWriterInterface(ABC):
    """将来、Prism解析結果をMemoryへ書き込むためのインターフェース(未実装)。"""

    @abstractmethod
    def write(self, analysis_result: dict) -> None:
        raise NotImplementedError("MemoryWriterInterfaceは未実装です(Phase 8時点)")


class RelayAdapterInterface(ABC):
    """将来、Prism解析結果をRelayへ送信するためのインターフェース(未実装)。"""

    @abstractmethod
    def send(self, analysis_result: dict) -> None:
        raise NotImplementedError("RelayAdapterInterfaceは未実装です(Phase 8時点)")


class OrchestraNotifierInterface(ABC):
    """将来、Prism解析結果をOrchestraへ通知するためのインターフェース(未実装)。"""

    @abstractmethod
    def notify(self, analysis_result: dict) -> None:
        raise NotImplementedError("OrchestraNotifierInterfaceは未実装です(Phase 8時点)")
