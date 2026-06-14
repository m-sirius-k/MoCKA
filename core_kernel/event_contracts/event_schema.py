"""
MoCKA Core Kernel — event_contracts.event_schema

責務:
  全モジュール共通のEvent構造(契約)を定義する。

  - ここで定義する構造はあくまで「契約」であり、Bus/Queue/Dispatcherなどの
    実行機構は持たない。
  - 既存モジュール(Orchestra等)が現在出力しているevent dict
    ({id, session_id, source, type, payload, timestamp}) とはフィールド名が
    異なる場合があるが、今回は既存実装を変更しないため、対応付けは行わない。
"""

import uuid as _uuid
from datetime import datetime, timezone

EVENT_SCHEMA_VERSION = "1.0"

# Event Schemaにおいて必須となるフィールド
REQUIRED_FIELDS = (
    "event_id",
    "event_type",
    "event_version",
    "source_module",
    "timestamp",
    "payload",
)

# 任意フィールド(存在する場合は型検証の対象となる)
OPTIONAL_FIELDS = (
    "target_module",
    "metadata",
)

ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS


def build_event(
    event_type: str,
    source_module: str,
    payload: dict,
    target_module: str = None,
    metadata: dict = None,
    event_version: str = EVENT_SCHEMA_VERSION,
    event_id: str = None,
    timestamp: str = None,
) -> dict:
    """Event Schemaに従ったEvent dictを構築する。

    event_id / timestamp は省略時に自動生成する。
    target_module / metadata は省略可能(契約上のOPTIONAL_FIELDS)。

    Returns:
        Event Schemaに準拠したdict(REQUIRED_FIELDSをすべて含む)
    """
    event = {
        "event_id": event_id or str(_uuid.uuid4()),
        "event_type": event_type,
        "event_version": event_version,
        "source_module": source_module,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "payload": dict(payload) if payload is not None else {},
    }
    if target_module is not None:
        event["target_module"] = target_module
    if metadata is not None:
        event["metadata"] = dict(metadata)
    return event
