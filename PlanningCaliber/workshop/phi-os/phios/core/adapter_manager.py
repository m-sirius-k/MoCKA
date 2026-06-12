# phi_os/core/adapter_manager.py
"""AI Adapterのレジストリ（プロセス内シングルトン）"""
from __future__ import annotations

from adapter.adapter_interface import AIAdapter

_registry: dict[str, AIAdapter] = {}


def register(ai_id: str, adapter: AIAdapter) -> None:
    _registry[ai_id] = adapter


def get(ai_id: str) -> AIAdapter:
    if ai_id not in _registry:
        raise KeyError(f"Unknown adapter: '{ai_id}'")
    return _registry[ai_id]


def list_adapters() -> list[str]:
    return list(_registry.keys())


def reset() -> None:
    """テスト用: レジストリをクリアする"""
    _registry.clear()
