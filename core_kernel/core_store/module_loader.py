"""
MoCKA Core Kernel — core_store.module_loader

責務:
  ModuleRegistryに登録済みのモジュールを、LifecycleManagerと連動させて
  初期化(ロード)する。

  - factory(呼び出し可能オブジェクト)の登録と、それを用いたインスタンス生成のみを行う。
  - 実際のOrchestra/Relay/Memory等のfactoryをここに登録するかどうかは利用側の判断に委ねる
    (今回はCore Store側の機構追加のみ)。
"""

from .lifecycle import LifecycleManager, LifecycleState
from .registry import ModuleRegistry


class ModuleLoader:
    """ModuleRegistry + LifecycleManagerと連動してモジュールをロードする。"""

    def __init__(self, registry: ModuleRegistry, lifecycle: LifecycleManager = None):
        self._registry = registry
        self._lifecycle = lifecycle or LifecycleManager()
        self._factories = {}   # module_id -> callable
        self._instances = {}   # module_id -> instance

    @property
    def lifecycle(self) -> LifecycleManager:
        return self._lifecycle

    def register_factory(self, module_id: str, factory) -> None:
        """module_idのインスタンスを生成するfactory(引数無し呼び出し可能オブジェクト)を登録する。

        Raises:
            KeyError: module_idが ModuleRegistry の "module" カテゴリに未登録
        """
        # 登録済みモジュールであることを確認する(存在しなければKeyError)
        self._registry.get("module", module_id)
        self._factories[module_id] = factory
        self._lifecycle.register(module_id)

    def load(self, module_id: str):
        """module_idのインスタンスを生成し、LifecycleStateを遷移させる。

        - 初回呼び出し: REGISTERED -> INITIALIZING -> ACTIVE (失敗時はFAILED)
        - 既にロード済みの場合はキャッシュされたインスタンスを返す。

        Raises:
            KeyError: factoryが未登録
            Exception: factory()が例外を投げた場合、その例外をそのまま再送出する
                       (LifecycleStateはFAILEDに遷移する)。
        """
        if module_id in self._instances:
            return self._instances[module_id]

        if module_id not in self._factories:
            raise KeyError(f"no factory registered for module '{module_id}'")

        self._lifecycle.transition(module_id, LifecycleState.INITIALIZING)
        try:
            instance = self._factories[module_id]()
        except Exception:
            self._lifecycle.transition(module_id, LifecycleState.FAILED)
            raise

        self._instances[module_id] = instance
        self._lifecycle.transition(module_id, LifecycleState.ACTIVE)
        return instance

    def get_instance(self, module_id: str):
        """ロード済みインスタンスを返す。未ロードの場合はNone。"""
        return self._instances.get(module_id)

    def is_loaded(self, module_id: str) -> bool:
        return module_id in self._instances
