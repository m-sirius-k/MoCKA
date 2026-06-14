"""
MoCKA Core Kernel — core_store.registry

責務:
  Module / Service / Event Type の共通登録機構。

  - 登録のみを行う(strict mode未満では起動・実行制御は行わない)。
  - 既存モジュール(Orchestra/Relay/Memory)からの強制利用は行わない。
  - 重複登録はエラーとする(同一カテゴリ・同一idの再登録のみ許可=update)。

追加機能(監査・商用向け):
  - snapshot() : 現在の登録状態をdictで取得(監査用)
  - freeze()   : 起動後の登録固定(商用ではfreeze後の追加登録を禁止)
  - validate() : 依存解決・不足Capability・循環依存の検査
  - export()   : JSON出力(GUI/監査向け)
"""

import json
from pathlib import Path

from .metadata import ModuleMetadata


class ModuleRegistry:
    """Module / Service / Event Type を登録・参照する共通レジストリ。"""

    CATEGORIES = ("module", "service", "event_type")

    def __init__(self):
        self._entries = {category: {} for category in self.CATEGORIES}
        self._frozen = False

    # ------------------------------------------------------------
    # 登録 / 参照
    # ------------------------------------------------------------

    def register(self, category: str, metadata: ModuleMetadata, overwrite: bool = False) -> ModuleMetadata:
        """指定カテゴリへmetadataを登録する。

        Args:
            category: "module" | "service" | "event_type"
            metadata: ModuleMetadata
            overwrite: Trueの場合、既存登録を上書きする。Falseで既存があればエラー。

        Returns:
            登録されたModuleMetadata

        Raises:
            RuntimeError: freeze()済みの場合
            ValueError: 未知のcategory、または重複登録(overwrite=False時)
        """
        if self._frozen:
            raise RuntimeError(
                f"registry is frozen; cannot register '{metadata.module_id}' in '{category}'"
            )
        self._validate_category(category)
        table = self._entries[category]
        if not overwrite and metadata.module_id in table:
            raise ValueError(
                f"'{metadata.module_id}' is already registered in '{category}' "
                f"(use overwrite=True to update)"
            )
        table[metadata.module_id] = metadata
        return metadata

    def get(self, category: str, module_id: str) -> ModuleMetadata:
        """登録済みのModuleMetadataを取得する。未登録の場合はKeyError。"""
        self._validate_category(category)
        return self._entries[category][module_id]

    def list(self, category: str) -> tuple:
        """指定カテゴリに登録済みの全ModuleMetadataを返す。"""
        self._validate_category(category)
        return tuple(self._entries[category].values())

    def is_registered(self, category: str, module_id: str) -> bool:
        self._validate_category(category)
        return module_id in self._entries[category]

    def unregister(self, category: str, module_id: str) -> None:
        """登録を削除する。未登録の場合はKeyError。

        Raises:
            RuntimeError: freeze()済みの場合
        """
        if self._frozen:
            raise RuntimeError(f"registry is frozen; cannot unregister '{module_id}' from '{category}'")
        self._validate_category(category)
        del self._entries[category][module_id]

    # ------------------------------------------------------------
    # ① Snapshot
    # ------------------------------------------------------------

    def snapshot(self) -> dict:
        """現在の登録状態をdictで取得する(監査用)。

        Returns:
            {
              "modules": {module_id: metadata.to_dict(), ...},
              "services": {...},
              "event_types": {...},
              "frozen": bool,
            }
        """
        return {
            "modules": {mid: m.to_dict() for mid, m in self._entries["module"].items()},
            "services": {mid: m.to_dict() for mid, m in self._entries["service"].items()},
            "event_types": {mid: m.to_dict() for mid, m in self._entries["event_type"].items()},
            "frozen": self._frozen,
        }

    # ------------------------------------------------------------
    # ② Freeze
    # ------------------------------------------------------------

    def freeze(self) -> None:
        """起動後の登録を固定する。以後register()/unregister()はRuntimeErrorとなる。"""
        self._frozen = True

    @property
    def is_frozen(self) -> bool:
        return self._frozen

    # ------------------------------------------------------------
    # ③ Capability Validation
    # ------------------------------------------------------------

    def validate(self) -> dict:
        """依存解決・不足Capability・循環依存を検査する。

        dependencyの要素は以下のいずれかとして解釈する:
          - 他モジュールの module_id           -> モジュール依存
          - "capability:<name>" 形式の文字列   -> Capability依存
                (登録済みのいずれかのモジュールがそのcapabilityを持つこと)

        Returns:
            {
              "valid": bool,
              "missing_dependencies": [{"module_id": ..., "missing": ...}, ...],
              "missing_capabilities": [{"module_id": ..., "missing": ...}, ...],
              "circular_dependencies": [[module_id, ...], ...],
            }
        """
        modules = self._entries["module"]

        all_capabilities = set()
        for meta in modules.values():
            all_capabilities.update(meta.capability)

        missing_dependencies = []
        missing_capabilities = []

        for module_id, meta in modules.items():
            for dep in meta.dependency:
                if dep.startswith("capability:"):
                    cap_name = dep[len("capability:"):]
                    if cap_name not in all_capabilities:
                        missing_capabilities.append({"module_id": module_id, "missing": cap_name})
                else:
                    if dep not in modules:
                        missing_dependencies.append({"module_id": module_id, "missing": dep})

        circular_dependencies = self._find_cycles(modules)

        valid = not (missing_dependencies or missing_capabilities or circular_dependencies)

        return {
            "valid": valid,
            "missing_dependencies": missing_dependencies,
            "missing_capabilities": missing_capabilities,
            "circular_dependencies": circular_dependencies,
        }

    @staticmethod
    def _find_cycles(modules: dict) -> list:
        """module間のdependency(module_id参照のみ)から循環依存を検出する(DFS)。"""

        def module_deps(meta: ModuleMetadata):
            return [d for d in meta.dependency if not d.startswith("capability:") and d in modules]

        WHITE, GRAY, BLACK = 0, 1, 2
        color = {mid: WHITE for mid in modules}
        cycles = []

        def visit(node, path):
            color[node] = GRAY
            path.append(node)
            for dep in module_deps(modules[node]):
                if color.get(dep) == GRAY:
                    cycle_start = path.index(dep)
                    cycles.append(path[cycle_start:] + [dep])
                elif color.get(dep, WHITE) == WHITE:
                    visit(dep, path)
            path.pop()
            color[node] = BLACK

        for module_id in modules:
            if color[module_id] == WHITE:
                visit(module_id, [])

        return cycles

    # ------------------------------------------------------------
    # ④ Export
    # ------------------------------------------------------------

    def export(self, path=None) -> str:
        """登録状態をJSON文字列として出力する。

        Args:
            path: 指定した場合、JSONをこのパスにも書き出す。

        Returns:
            JSON文字列(snapshot()の内容)
        """
        text = json.dumps(self.snapshot(), ensure_ascii=False, indent=2)
        if path is not None:
            Path(path).write_text(text, encoding="utf-8")
        return text

    # ------------------------------------------------------------
    # internal
    # ------------------------------------------------------------

    def _validate_category(self, category: str) -> None:
        if category not in self.CATEGORIES:
            raise ValueError(f"unknown category '{category}' (expected one of {self.CATEGORIES})")
