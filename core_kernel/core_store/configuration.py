"""
MoCKA Core Kernel — core_store.configuration

責務:
  共通設定の一元管理(任意利用)。

  - dict由来の設定とJSONファイル由来の設定を統一的に扱う。
  - 既存モジュールの設定ファイル(例: orchestra_config.json)を
    上書き・移動するものではない。利用したい側が明示的に読み込む。
"""

import json
from pathlib import Path


class ConfigStore:
    """共通設定を一元的に保持・参照するための最小限の設定ストア。"""

    def __init__(self, defaults: dict = None):
        self._values = dict(defaults or {})

    @classmethod
    def from_file(cls, path, defaults: dict = None) -> "ConfigStore":
        """JSONファイルから設定を読み込む。

        ファイルが存在しない/読み込みに失敗した場合はdefaultsのみで構築する
        (既存モジュールのフォールバック挙動と同様、エラーにしない)。
        """
        store = cls(defaults)
        path = Path(path)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    store._values.update(data)
            except (json.JSONDecodeError, OSError):
                pass
        return store

    def get(self, key: str, default=None):
        return self._values.get(key, default)

    def set(self, key: str, value) -> None:
        self._values[key] = value

    def update(self, values: dict) -> None:
        self._values.update(values)

    def as_dict(self) -> dict:
        return dict(self._values)
