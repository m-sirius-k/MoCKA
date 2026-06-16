# runtime/config/config_loader.py
# MoCKA v1.2.1+ — 設定ファイルローダー
# config.yaml を読み込み、各層に制御パラメータを提供する。

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from error import ConfigError

_DEFAULT_PATH = Path(__file__).resolve().parent / "config.yaml"


class ConfigLoader:
    """
    runtime/config/config.yaml を読み込む。
    yaml が使えない環境ではデフォルト値にフォールバックする。
    """

    _DEFAULTS: Dict[str, Any] = {
        "phi":     {"low": 0.3, "high": 0.7},
        "timeline":{"window": 20},
        "audit":   {"strict": True},
        "runtime": {"mode": "stable"},
    }

    def __init__(self, path: Path | str | None = None) -> None:
        self._path = Path(path) if path else _DEFAULT_PATH

    def load(self) -> Dict[str, Any]:
        """設定を読み込む。失敗時はデフォルト値を返す。"""
        if not self._path.exists():
            return dict(self._DEFAULTS)
        try:
            import yaml
            with self._path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return {**self._DEFAULTS, **data}
        except ImportError:
            # PyYAML 未インストール時はデフォルト値で継続
            return dict(self._DEFAULTS)
        except Exception as e:
            raise ConfigError(f"config load failed: {e}") from e

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """セクション・キー指定で値を取得する。"""
        return self.load().get(section, {}).get(key, default)
