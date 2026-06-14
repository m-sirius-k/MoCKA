"""
MoCKA Core Kernel — event_contracts.replay_contract

責務:
  イベントを「再生(Replay)」する際に最低限満たすべき契約を定義する。

  - Replay Engineそのものは実装しない。
  - ここで定義するのは「Replay可能であるための必要条件」のみ。

契約内容:
  1. 一意性    : event_id によって個々のEventが一意に識別できること。
  2. 順序性    : timestamp によって発生順に並び替え可能であること。
  3. 自己完結性: payload に再生対象の状態変化が含まれていること
                 (外部参照無しに、このEvent単体で意味が成立すること)。
  4. 出自明示  : source_module によって、どのモジュールが発生させたかが
                 判別できること。
"""

from .event_schema import REQUIRED_FIELDS
from .validation import validate_event

# Replay可能であるために必須となるフィールド。
# REQUIRED_FIELDSのサブセットであり、追加のフィールドを要求しない。
REPLAY_REQUIRED_FIELDS = (
    "event_id",
    "timestamp",
    "source_module",
    "payload",
)

assert set(REPLAY_REQUIRED_FIELDS).issubset(set(REQUIRED_FIELDS)), (
    "REPLAY_REQUIRED_FIELDS must be a subset of event_schema.REQUIRED_FIELDS"
)


def is_replayable(event: dict) -> bool:
    """EventがReplay Contractを満たすかを判定する。

    Event Schemaとしてvalidであり、かつREPLAY_REQUIRED_FIELDSが
    すべて存在し、payloadが空でないことを要求する。
    """
    result = validate_event(event)
    if not result.valid:
        return False

    for field_name in REPLAY_REQUIRED_FIELDS:
        if field_name not in event:
            return False

    if not event["payload"]:
        return False

    return True


def sort_key(event: dict):
    """Replay順序を決定するためのソートキー(timestamp)。"""
    return event["timestamp"]
