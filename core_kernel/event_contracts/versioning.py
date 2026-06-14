"""
MoCKA Core Kernel — event_contracts.versioning

責務:
  Event Schemaのバージョン管理。

  - SUPPORTED_VERSIONS は、現在このcore_kernelが「検証・解釈可能」な
    event_versionの集合を表す。
  - 新しいバージョンを追加する場合はSUPPORTED_VERSIONSに追記し、
    既存バージョンを削除しないことで後方互換性を維持する。
"""

from .event_schema import EVENT_SCHEMA_VERSION

# サポート対象のevent_version。EVENT_SCHEMA_VERSIONは常に含まれる。
SUPPORTED_VERSIONS = frozenset({EVENT_SCHEMA_VERSION})


def is_supported_version(event_version: str) -> bool:
    """event_versionがSUPPORTED_VERSIONSに含まれるかを返す。"""
    return event_version in SUPPORTED_VERSIONS


def is_current_version(event_version: str) -> bool:
    """event_versionが現行のEVENT_SCHEMA_VERSIONと一致するかを返す。"""
    return event_version == EVENT_SCHEMA_VERSION
