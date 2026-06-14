"""
MoCKA Core Kernel — event_contracts.event_types

責務:
  event_type文字列を一元管理する。

  - EventType: 既知のevent_type定数(指示書に列挙されたもの)
  - EventTypeRegistry: event_typeの登録・参照を行う共通機構。
    core_store.ModuleRegistry の "event_type" カテゴリとは独立しており、
    今回はcore_storeへの変更・統合は行わない(契約レイヤー単独で完結する)。
"""


class EventType:
    """既知のevent_type定数。"""

    CHANGE_START = "CHANGE_START"
    CHANGE_DONE = "CHANGE_DONE"
    CONTEXT_CAPTURE = "CONTEXT_CAPTURE"
    CONTEXT_RESTORE = "CONTEXT_RESTORE"
    MODULE_REGISTERED = "MODULE_REGISTERED"
    MODULE_LOADED = "MODULE_LOADED"
    LIFECYCLE_CHANGED = "LIFECYCLE_CHANGED"

    ALL = (
        CHANGE_START,
        CHANGE_DONE,
        CONTEXT_CAPTURE,
        CONTEXT_RESTORE,
        MODULE_REGISTERED,
        MODULE_LOADED,
        LIFECYCLE_CHANGED,
    )


class EventTypeRegistry:
    """event_typeの登録・参照を行う共通機構。

    既知のEventType.ALLは初期登録済み。未知のevent_typeは
    register()で追加できる(将来モジュールの拡張用)。
    """

    def __init__(self, preregister_known: bool = True):
        self._types = {}
        if preregister_known:
            for event_type in EventType.ALL:
                self.register(event_type, description=f"built-in: {event_type}")

    def register(self, event_type: str, description: str = "", overwrite: bool = False) -> None:
        """event_typeを登録する。

        Raises:
            ValueError: 既に登録済み(overwrite=False時)
        """
        if not overwrite and event_type in self._types:
            raise ValueError(f"event_type '{event_type}' is already registered")
        self._types[event_type] = {"event_type": event_type, "description": description}

    def is_registered(self, event_type: str) -> bool:
        return event_type in self._types

    def get(self, event_type: str) -> dict:
        """登録情報を取得する。未登録の場合はKeyError。"""
        return dict(self._types[event_type])

    def list(self) -> tuple:
        """登録済みの全event_type文字列を返す(ソート済み)。"""
        return tuple(sorted(self._types.keys()))
