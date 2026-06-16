# phi_os/gate_schema.py
# PHI-OS EVENT GATE v1 — Event Payload Schema
from dataclasses import dataclass, field
from typing import Optional
import hashlib, json, uuid
from datetime import datetime, timezone

ALLOWED_WHAT_TYPES = [
    'file_write', 'file_delete', 'design', 'config_change',
    'git_commit', 'git_push', 'test_run', 'deployment',
    'user_voice', 'handshake', 'audit', 'incident', 'todo_update',
    'claude_mcp',  # MCP tool経由イベント
]

ALLOWED_WHO_ROLES = ['executor', 'auditor', 'human', 'automation']


@dataclass
class EventPayload:
    # 5W1H 必須フィールド
    who_actor: str       # 例: Claude-sonnet-4-6, gpt-4o
    who_role: str        # executor|auditor|human|automation
    who_session: str     # SESSION_YYYYMMDD_HHMMSS
    what_type: str       # ALLOWED_WHAT_TYPES から選択
    what_title: str      # 変更の一行要約
    where_path: str      # 絶対パスまたはURL
    where_component: str # モジュール名
    why_purpose: str     # 目的（10文字以上）
    how_trigger: str     # 誰の指示か

    # Replay用（どちらかがあればOK）
    before_state: Optional[str] = None
    after_state: Optional[str] = None
    before_hash: Optional[str] = None
    after_hash: Optional[str] = None

    # 自由記述
    description: str = ''
    tags: str = ''
