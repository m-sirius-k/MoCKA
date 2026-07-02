"""
mocka_endpoints.py -- Endpoint Registry Resolver

MOCKA_ENDPOINTS.json (唯一の設定源) からホスト/ポート/パスを解決する層。
起源: E20260702_1595449490459 (localhost名前解決障害 -> 127.0.0.1で暫定対処 -> 本格移行)

設計原則(TODO_設計メモ準拠):
- 接続先の直書き禁止。呼び出し側は get_endpoint_url(name, path_key) 経由のみとする。
- REGISTRY_PATH のみ例外的にハードコードを許容する
  (これ以上下に一元化層を作ると循環になるため)。
"""

import json
from pathlib import Path
from functools import lru_cache

REGISTRY_PATH = Path("C:/Users/sirok/MoCKA/data/MOCKA_ENDPOINTS.json")


@lru_cache(maxsize=1)
def _load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def get_endpoint_url(name: str, path_key: str = "status") -> str:
    registry = _load_registry()
    if name not in registry:
        raise KeyError(f"MOCKA_ENDPOINTS.json に未登録のサービス: {name}")
    entry = registry[name]
    paths = entry.get("paths", {})
    if path_key not in paths:
        raise KeyError(f"{name} に path_key='{path_key}' が未登録です")
    return f"{entry['protocol']}://{entry['connect_host']}:{entry['port']}{paths[path_key]}"


def get_bind_host(name: str) -> str:
    registry = _load_registry()
    return registry[name]["bind_host"]
