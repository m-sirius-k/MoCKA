"""
MoCKA 3.0 — Memory Layer
memory_store.py

責務:
  すべての記憶(MemoryEntry)を統一フォーマットで保存する中核ストレージ。

  - 保存先: memory/data/memory_store.json (JSON配列、追記型)
  - memory_type別の保存上限(memory_registry.RETENTION_POLICIES)を超えた場合、
    古いエントリから除外する(直近優先)。
  - Governance Layer / GL1-7 とは独立しており、これらをimportしない。
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from memory_model import MemoryEntry
from memory_registry import get_retention_policy

STORE_DIR = Path(__file__).resolve().parent / "data"
STORE_PATH = STORE_DIR / "memory_store.json"


class MemoryStore:
    """MemoryEntryをJSONファイルに永続化する中核ストレージ。"""

    def __init__(self, store_path: Path = STORE_PATH):
        self._store_path = Path(store_path)
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._store_path.exists():
            self._write_all([])

    def all(self) -> tuple:
        """保存済みの全MemoryEntryを返す(古い順)。"""
        raw = self._read_all()
        return tuple(MemoryEntry.from_dict(item) for item in raw)

    def append(self, entry: MemoryEntry) -> MemoryEntry:
        """MemoryEntryを1件追記する。memory_type別の保存上限を超えた場合は古いものから除外する。"""
        raw = self._read_all()
        raw.append(entry.to_dict())
        raw = self._apply_retention(raw)
        self._write_all(raw)
        return entry

    def next_memory_id(self, memory_type: str) -> str:
        """memory_typeごとに連番のmemory_idを発行する(M_<type>_<seq>)。"""
        raw = self._read_all()
        seq = sum(1 for item in raw if item.get("memory_type") == memory_type) + 1
        return f"M_{memory_type}_{seq:06d}"

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def _read_all(self) -> list:
        if not self._store_path.exists():
            return []
        with open(self._store_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    def _write_all(self, raw: list) -> None:
        with open(self._store_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _apply_retention(raw: list) -> list:
        by_type = {}
        for item in raw:
            by_type.setdefault(item.get("memory_type"), []).append(item)

        kept = []
        for memory_type, items in by_type.items():
            policy = get_retention_policy(memory_type)
            kept.extend(items[-policy.max_entries:])

        # timestamp順(挿入順を概ね保持)に整列
        kept.sort(key=lambda item: item.get("timestamp", ""))
        return kept
