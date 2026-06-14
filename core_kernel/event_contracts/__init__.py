"""
MoCKA Core Kernel — event_contracts

Core Kernel(core_store)の上位層として、全モジュール共通の
「イベントの制度的契約」を定義する。

このパッケージは:
  - イベントを生成/送受信するBus/Queue/Dispatcherを持たない。
  - Orchestra/Relay/Memory/PHI-OSのいずれにも接続しない。
  - 単独でimport・利用・テスト可能である。

公開コンポーネント:
  - EVENT_SCHEMA_VERSION : 現行イベントスキーマのバージョン
  - REQUIRED_FIELDS / OPTIONAL_FIELDS : Event Schemaのフィールド定義
  - build_event          : 規約に従ったEvent dictを生成するヘルパー
  - SUPPORTED_VERSIONS   : サポート対象のevent_versionの集合
  - is_supported_version : バージョン互換性チェック
  - validate_event       : Event Schema検証
  - EventType            : 既知のevent_type定数
  - EventTypeRegistry    : event_typeの登録・参照機構
  - REPLAY_REQUIRED_FIELDS / is_replayable : Replay Contract
"""

from .event_schema import (
    EVENT_SCHEMA_VERSION,
    REQUIRED_FIELDS,
    OPTIONAL_FIELDS,
    build_event,
)
from .versioning import SUPPORTED_VERSIONS, is_supported_version
from .validation import ValidationResult, validate_event
from .event_types import EventType, EventTypeRegistry
from .replay_contract import REPLAY_REQUIRED_FIELDS, is_replayable

__all__ = [
    "EVENT_SCHEMA_VERSION",
    "REQUIRED_FIELDS",
    "OPTIONAL_FIELDS",
    "build_event",
    "SUPPORTED_VERSIONS",
    "is_supported_version",
    "ValidationResult",
    "validate_event",
    "EventType",
    "EventTypeRegistry",
    "REPLAY_REQUIRED_FIELDS",
    "is_replayable",
]
