"""
MoCKA Core Kernel — core_store.capability_registry

責務:
  「どのCapabilityをどのモジュールが提供するか」を管理する。

  ModuleRegistryの ModuleMetadata.capability は「モジュールが持つ属性の宣言」
  に過ぎず、Capability名から提供元モジュールを逆引きする手段が無かった。
  CapabilityRegistryはこの逆引き(capability -> providers)を一元管理する。

  - registry.validate()の "capability:<name>" 解決とは独立しており、
    将来validate()がここを参照する形に統合できる(今回は未統合・追加のみ)。
"""


class CapabilityRegistry:
    """Capability名 -> 提供モジュールID集合 の対応を管理する。"""

    def __init__(self):
        self._providers = {}  # capability_name -> set(module_id)

    def register_provider(self, capability: str, module_id: str) -> None:
        """module_idがcapabilityを提供することを登録する(冪等)。"""
        self._providers.setdefault(capability, set()).add(module_id)

    def unregister_provider(self, capability: str, module_id: str) -> None:
        """登録を取り消す。未登録の場合は何もしない。"""
        providers = self._providers.get(capability)
        if providers is None:
            return
        providers.discard(module_id)
        if not providers:
            del self._providers[capability]

    def providers(self, capability: str) -> tuple:
        """capabilityを提供するmodule_idの集合を返す(無ければ空タプル)。"""
        return tuple(sorted(self._providers.get(capability, ())))

    def has_provider(self, capability: str) -> bool:
        return bool(self._providers.get(capability))

    def all_capabilities(self) -> tuple:
        """登録済みの全capability名を返す。"""
        return tuple(sorted(self._providers.keys()))

    def snapshot(self) -> dict:
        """現在の対応関係をdictで返す(監査用)。"""
        return {cap: sorted(mods) for cap, mods in self._providers.items()}
