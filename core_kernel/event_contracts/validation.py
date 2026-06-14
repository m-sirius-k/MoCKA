"""
MoCKA Core Kernel — event_contracts.validation

責務:
  Event Schema(event_schema.py)に基づく検証機構。

  - 不正なEventを「受理しない」ことを目的とする(ここではエラー一覧を返すのみで、
    受理/拒否の実行制御自体はBus/Dispatcher側の責務とする=今回実装しない)。
"""

from dataclasses import dataclass, field
from datetime import datetime

from .event_schema import ALL_FIELDS, REQUIRED_FIELDS
from .event_types import EventTypeRegistry
from .versioning import is_supported_version


@dataclass(frozen=True)
class ValidationResult:
    """validate_event()の結果。"""

    valid: bool
    errors: tuple = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {"valid": self.valid, "errors": list(self.errors)}


def _is_iso8601(value) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_event(event: dict, type_registry: EventTypeRegistry = None) -> ValidationResult:
    """EventがEvent Schemaに準拠しているかを検証する。

    Args:
        event: 検証対象のEvent dict
        type_registry: 指定した場合、event_typeが登録済みであることも検証する。

    Returns:
        ValidationResult(valid, errors)
    """
    errors = []

    if not isinstance(event, dict):
        return ValidationResult(valid=False, errors=("event must be a dict",))

    # 1. 必須フィールドの存在確認
    for field_name in REQUIRED_FIELDS:
        if field_name not in event:
            errors.append(f"missing required field: '{field_name}'")

    # 2. 未知フィールドの検出
    for field_name in event:
        if field_name not in ALL_FIELDS:
            errors.append(f"unknown field: '{field_name}'")

    # 3. 型検証(存在するフィールドのみ)
    if "event_id" in event and not isinstance(event["event_id"], str):
        errors.append("'event_id' must be a string")

    if "event_type" in event and not isinstance(event["event_type"], str):
        errors.append("'event_type' must be a string")

    if "event_version" in event:
        if not isinstance(event["event_version"], str):
            errors.append("'event_version' must be a string")
        elif not is_supported_version(event["event_version"]):
            errors.append(f"unsupported event_version: '{event['event_version']}'")

    if "source_module" in event and not isinstance(event["source_module"], str):
        errors.append("'source_module' must be a string")

    if "target_module" in event and event["target_module"] is not None and not isinstance(event["target_module"], str):
        errors.append("'target_module' must be a string or null")

    if "timestamp" in event and not _is_iso8601(event["timestamp"]):
        errors.append("'timestamp' must be an ISO8601 string")

    if "payload" in event and not isinstance(event["payload"], dict):
        errors.append("'payload' must be a dict")

    if "metadata" in event and not isinstance(event["metadata"], dict):
        errors.append("'metadata' must be a dict")

    # 4. event_type登録確認(任意)
    if type_registry is not None and "event_type" in event and isinstance(event["event_type"], str):
        if not type_registry.is_registered(event["event_type"]):
            errors.append(f"unregistered event_type: '{event['event_type']}'")

    return ValidationResult(valid=not errors, errors=tuple(errors))
