"""
MoCKA Core Kernel — memory_core.memory_store

責務:
  AnalysisResult / Context / Observation / CognitiveState を
  永続化するための最小永続化層(Minimal Persistence Layer)。

  優先順位:
    1. JSON file store (pathが指定された場合)
    2. In-memory fallback (pathが指定されない場合、またはテスト用)

  禁止:
    - 外部DB(PostgreSQL等)
    - Redis
    - Network通信
    - LLM呼び出し
    - Workflow制御
"""

import json
from pathlib import Path

from .record import MemoryRecord


class MemoryStore:
    """JSONファイル、またはインメモリでMemoryRecordを永続化する。"""

    def __init__(self, path=None):
        """
        Args:
            path: JSONファイルのパス(str/Path)。Noneの場合はin-memory fallback。
        """
        self._path = Path(path) if path is not None else None
        self._records = self._load_all()

    # ------------------------------------------------------------------
    # 公開API
    # ------------------------------------------------------------------

    def save(self, record_type: str, payload, record_id: str = None, session_id: str = None) -> dict:
        """レコードを保存し、保存結果(dict)を返す。"""
        kwargs = {"type": record_type, "payload": payload, "session_id": session_id}
        if record_id is not None:
            kwargs["id"] = record_id

        record = MemoryRecord(**kwargs)
        data = record.to_dict()

        self._records[data["id"]] = data
        self._persist()
        return data

    def load(self, entity_id: str):
        """idを指定してレコードを取得する。存在しない場合はNone。"""
        return self._records.get(entity_id)

    def query(self, predicate=None) -> list:
        """predicate(record)がTrueを返すレコードの一覧を返す。

        predicateがNoneの場合は全件を返す。
        """
        records = list(self._records.values())
        if predicate is None:
            return records
        return [record for record in records if predicate(record)]

    def list(self, session_id: str) -> list:
        """指定session_idに紐づくレコードの一覧を返す。"""
        return self.query(lambda record: record.get("session_id") == session_id)

    # ------------------------------------------------------------------
    # 内部: 永続化
    # ------------------------------------------------------------------

    def _load_all(self) -> dict:
        """JSONファイルからレコードを読み込む。

        ファイルが存在しない、または壊れている場合は空のストアから開始する
        (corrupted fileに対する耐性)。
        """
        if self._path is None or not self._path.exists():
            return {}

        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return {}

        records = data.get("records", {}) if isinstance(data, dict) else {}
        if not isinstance(records, dict):
            return {}
        return records

    def _persist(self) -> None:
        """in-memoryの内容をJSONファイルへ書き出す(pathが指定されている場合のみ)。"""
        if self._path is None:
            return

        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({"records": self._records}, f, ensure_ascii=False, indent=2)
