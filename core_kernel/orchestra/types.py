"""
MoCKA Core Kernel — orchestra.types

Orchestra実行層が扱うイベント型定義。
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Event:
    event_id: str
    event_type: str
    session_id: str
    timestamp: float
    payload: Dict[str, Any]
