"""
MoCKA Core Kernel — prism.interfaces.analyzer_interface

責務:
  Analyzerの公開契約(analyze / analyze_many)を定義する。

  将来、推論ロジック(AI)を差し替える場合も、この契約を満たす限り
  Pipeline/呼び出し側のコードは変更不要であることを保証する。
"""

from abc import ABC, abstractmethod


class AnalyzerInterface(ABC):
    """Prism Analyzerが満たすべき公開契約。"""

    @abstractmethod
    def analyze(self, event: dict):
        """単一のEvent(Event Contract準拠)を解析する。

        Returns:
            AnalysisResult (analyzer.AnalysisResult)
        """
        raise NotImplementedError

    @abstractmethod
    def analyze_many(self, events):
        """複数のEvent(Event Contract準拠)を解析する。

        Args:
            events: Event dictのイテラブル

        Returns:
            AnalysisResult (analyzer.AnalysisResult)
        """
        raise NotImplementedError
