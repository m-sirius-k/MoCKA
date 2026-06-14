"""
MoCKA Core Kernel — prism.provider

責務:
  PrismをPHI-OS等の外部から利用するためのProvider。

  本モジュールはPrismの「接続口」であり、PHI-OSとの実動連携
  (Capability登録・呼び出し配線)は行わない。登録処理自体は
  外部(PHI-OS起動シーケンス)の責務である。

公開API:
  - analyze(event)
  - analyze_many(events)
  - get_capabilities()
  - get_version()
  - health_check()

Read Only保証:
  Core Kernel(core_store)に対しては、以下のみ利用する。
    - Registry.get() / list() / snapshot()
    - Lifecycle.get_state() / snapshot()
    - Capability参照
  register() / transition() / set() / remove() / clear() は呼び出さない。
"""

from .analyzer import AnalysisResult, PrismAnalyzer
from .version import PRISM_VERSION

CAPABILITY_COGNITION = "cognition"


class PrismProvider:
    """PHI-OS等から利用されるPrismの接続口。"""

    def __init__(self, registry=None, lifecycle=None, type_registry=None):
        """
        Args:
            registry: core_store.ModuleRegistry (読み取り専用利用、省略可)
            lifecycle: core_store.LifecycleManager (読み取り専用利用、省略可)
            type_registry: event_contracts.EventTypeRegistry (省略可)
        """
        self._registry = registry
        self._lifecycle = lifecycle
        self._analyzer = PrismAnalyzer(
            registry=registry,
            lifecycle=lifecycle,
            type_registry=type_registry,
        )

    # ------------------------------------------------------------------
    # 認知処理API
    # ------------------------------------------------------------------

    def analyze(self, event: dict) -> AnalysisResult:
        """単一のEventを解析する。"""
        return self._analyzer.analyze(event)

    def analyze_many(self, events) -> AnalysisResult:
        """複数のEventを解析する。"""
        return self._analyzer.analyze_many(events)

    # ------------------------------------------------------------------
    # Capability / バージョン情報
    # ------------------------------------------------------------------

    def get_capabilities(self) -> tuple:
        """Prismが提供するCapability名のタプルを返す。

        登録処理自体は行わない(外部の起動シーケンスが担当する)。
        """
        return (CAPABILITY_COGNITION,)

    def get_version(self) -> str:
        """Prismのバージョン文字列を返す。"""
        return PRISM_VERSION

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    def health_check(self) -> dict:
        """Prismの稼働状況を返す。

        Returns:
            dict: {
                "version": str,
                "status": "ok" | "degraded",
                "pipeline_ready": bool,
                "engine_status": dict,
                "supported_capabilities": list,
            }
        """
        engine_status = self._check_engines()
        pipeline_ready = all(engine_status.values())
        status = "ok" if pipeline_ready else "degraded"

        return {
            "version": self.get_version(),
            "status": status,
            "pipeline_ready": pipeline_ready,
            "engine_status": engine_status,
            "supported_capabilities": list(self.get_capabilities()),
        }

    def _check_engines(self) -> dict:
        pipeline = self._analyzer._pipeline
        engines = {
            "semantic_engine": pipeline._semantic_engine,
            "correlation_engine": pipeline._correlation_engine,
            "context_engine": pipeline._context_engine,
            "cognitive_state_engine": pipeline._cognitive_state_engine,
            "observation_engine": pipeline._observation_engine,
        }
        return {name: engine is not None for name, engine in engines.items()}
