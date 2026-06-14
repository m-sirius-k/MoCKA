"""
MoCKA Core Kernel — core_store.lifecycle

責務:
  モジュール単位のライフサイクル状態を管理する。

  - 状態と許可された遷移のみを管理する(各モジュールの内部実装には関与しない)。
  - PHI-OS(将来)はこのLifecycleManagerを介してモジュールの健全性を観測する想定だが、
    今回はCore Store内の管理機構の追加のみで、PHI-OSとの統合は行わない。
"""


class LifecycleState:
    """モジュールが取り得るライフサイクル状態。"""

    REGISTERED = "registered"      # ModuleRegistryに登録済み、未初期化
    INITIALIZING = "initializing"  # 初期化処理中
    ACTIVE = "active"               # 正常稼働中
    DEGRADED = "degraded"           # 部分的に機能している(警告状態)
    STOPPED = "stopped"             # 明示的に停止
    FAILED = "failed"                # 初期化/稼働中に致命的エラー

    ALL = (REGISTERED, INITIALIZING, ACTIVE, DEGRADED, STOPPED, FAILED)


# 許可された状態遷移 (from -> {to, ...})
_ALLOWED_TRANSITIONS = {
    LifecycleState.REGISTERED: {LifecycleState.INITIALIZING, LifecycleState.FAILED},
    LifecycleState.INITIALIZING: {LifecycleState.ACTIVE, LifecycleState.FAILED},
    LifecycleState.ACTIVE: {LifecycleState.DEGRADED, LifecycleState.STOPPED, LifecycleState.FAILED},
    LifecycleState.DEGRADED: {LifecycleState.ACTIVE, LifecycleState.STOPPED, LifecycleState.FAILED},
    LifecycleState.STOPPED: {LifecycleState.INITIALIZING},
    LifecycleState.FAILED: {LifecycleState.INITIALIZING, LifecycleState.STOPPED},
}


class LifecycleManager:
    """module_id -> LifecycleState の管理、および許可された遷移の検証を行う。"""

    def __init__(self):
        self._states = {}  # module_id -> LifecycleState

    def register(self, module_id: str) -> str:
        """モジュールをLifecycleState.REGISTEREDとして登録する(冪等)。

        既に登録済みの場合は現在の状態をそのまま返す。
        """
        return self._states.setdefault(module_id, LifecycleState.REGISTERED)

    def get_state(self, module_id: str) -> str:
        """現在の状態を取得する。未登録の場合はKeyError。"""
        return self._states[module_id]

    def transition(self, module_id: str, target_state: str) -> str:
        """module_idの状態をtarget_stateへ遷移させる。

        Raises:
            KeyError: module_idが未登録
            ValueError: target_stateが未知、または許可されていない遷移
        """
        if target_state not in LifecycleState.ALL:
            raise ValueError(f"unknown lifecycle state '{target_state}'")

        current = self._states[module_id]
        allowed = _ALLOWED_TRANSITIONS.get(current, set())
        if target_state not in allowed:
            raise ValueError(
                f"invalid lifecycle transition for '{module_id}': '{current}' -> '{target_state}'"
            )

        self._states[module_id] = target_state
        return target_state

    def can_transition(self, module_id: str, target_state: str) -> bool:
        current = self._states.get(module_id)
        if current is None:
            return False
        return target_state in _ALLOWED_TRANSITIONS.get(current, set())

    def snapshot(self) -> dict:
        """module_id -> state の現在状態をdictで返す(監査用)。"""
        return dict(self._states)
