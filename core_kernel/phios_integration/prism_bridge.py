"""
MoCKA Core Kernel — phios_integration.prism_bridge

責務:
  PHI-OSがPrismProviderを呼び出すための接続口(Bridge)。

  PHI-OSは本モジュールを介してPrismの認知結果
  (Context / SemanticAnnotation / CognitiveState / Observation)
  を取得する。取得した結果の保持・返却まではPHI-OS側の責務であり、
  本モジュールはMemory/Relay/Orchestraへの連携を行わない。

Read Only保証:
  PrismProvider経由でCore Kernel(core_store)を参照するのみであり、
  register() / transition() / set() / remove() / clear() は呼び出さない。

異常時の方針:
  Provider未初期化・Validation失敗・Prism例外・空入力のいずれも、
  例外を上位に投げるのではなく "status": "error" を含むdictを返し、
  PHI-OS全体を停止させない。
"""

from core_kernel.event_contracts import validate_event
from core_kernel.prism import PrismError, PrismProvider

from .exceptions import EventValidationError, ProviderNotInitializedError


class PrismBridge:
    """PHI-OSからPrismProviderを呼び出すためのBridge。"""

    def __init__(self):
        self._provider = None

    # ------------------------------------------------------------------
    # 初期化
    # ------------------------------------------------------------------

    def initialize_prism(self, registry=None, lifecycle=None, type_registry=None) -> dict:
        """PrismProviderを初期化する。

        Args:
            registry: core_store.ModuleRegistry (読み取り専用利用、省略可)
            lifecycle: core_store.LifecycleManager (読み取り専用利用、省略可)
            type_registry: event_contracts.EventTypeRegistry (省略可)

        Returns:
            dict: {"status": "ok", "health": <health_check結果>}
        """
        self._provider = PrismProvider(
            registry=registry,
            lifecycle=lifecycle,
            type_registry=type_registry,
        )
        return {"status": "ok", "health": self._provider.health_check()}

    def is_initialized(self) -> bool:
        """PrismProviderが初期化済みかどうかを返す。"""
        return self._provider is not None

    # ------------------------------------------------------------------
    # Event解析
    # ------------------------------------------------------------------

    def analyze_event(self, event: dict) -> dict:
        """単一のEventをPrismで解析する。

        Returns:
            dict: 成功時 {"status": "ok", "result": AnalysisResult}
                  失敗時 {"status": "error", "error": str, "error_type": str}
        """
        return self._run([event], lambda provider, _events: provider.analyze(event))

    def analyze_events(self, events) -> dict:
        """複数のEventをPrismで解析する。

        Returns:
            dict: 成功時 {"status": "ok", "result": AnalysisResult}
                  失敗時 {"status": "error", "error": str, "error_type": str}
        """
        return self._run(events, lambda provider, evts: provider.analyze_many(evts))

    # ------------------------------------------------------------------
    # 内部処理
    # ------------------------------------------------------------------

    def _run(self, events, call) -> dict:
        try:
            self._ensure_initialized()
            events = self._validate(events)
            result = call(self._provider, events)
            return {"status": "ok", "result": result}
        except ProviderNotInitializedError as exc:
            return {"status": "error", "error": str(exc), "error_type": "provider_not_initialized"}
        except EventValidationError as exc:
            return {"status": "error", "error": str(exc), "error_type": "validation_error"}
        except PrismError as exc:
            return {"status": "error", "error": str(exc), "error_type": "prism_error"}

    def _ensure_initialized(self):
        if self._provider is None:
            raise ProviderNotInitializedError("PrismProviderが初期化されていません")

    @staticmethod
    def _validate(events):
        events = list(events)
        if not events:
            raise EventValidationError("解析対象のEventが空です")

        for event in events:
            result = validate_event(event)
            if not result.valid:
                raise EventValidationError(
                    f"event_id={event.get('event_id')!r} の検証に失敗: {result.errors}"
                )

        return events
