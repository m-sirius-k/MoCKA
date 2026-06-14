"""
MoCKA Core Kernel — core_store

将来のPHI-OS/各レイヤーが利用しうる共通基盤(追加のみ)。

このパッケージは既存のOrchestra/Relay/Memoryからは一切参照されない。
利用は任意であり、既存モジュールの動作には影響しない。

公開コンポーネント:
  - ModuleMetadata     : モジュールのメタ情報
  - ModuleRegistry     : モジュール/サービス/イベント種別の登録機構
  - ConfigStore        : 共通設定の一元管理
  - PersistenceBackend : 永続化の抽象インターフェース(実装はまだ無い)
  - InMemoryBackend    : テスト用の最小実装
  - CapabilityRegistry : Capability -> 提供モジュールの逆引き
  - LifecycleManager   : モジュール単位のライフサイクル状態管理
  - LifecycleState     : ライフサイクル状態定数
  - ModuleLoader       : Registry/Lifecycleと連動したモジュールロード
"""

from .metadata import ModuleMetadata
from .registry import ModuleRegistry
from .configuration import ConfigStore
from .persistence_interface import PersistenceBackend, InMemoryBackend
from .capability_registry import CapabilityRegistry
from .lifecycle import LifecycleManager, LifecycleState
from .module_loader import ModuleLoader

__all__ = [
    "ModuleMetadata",
    "ModuleRegistry",
    "ConfigStore",
    "PersistenceBackend",
    "InMemoryBackend",
    "CapabilityRegistry",
    "LifecycleManager",
    "LifecycleState",
    "ModuleLoader",
]
