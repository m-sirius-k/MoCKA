"""
MoCKA 3.0 — Memory Layer
memory_binding_store.py

責務:
  MemoryBindingTraceを管理・永続化する。

  - 保存先: memory/data/memory_binding_ledger.jsonl
  - JSONL形式(JSON Lines: 1行1レコード)
  - Append-only ledger
  - Decision Ledgerと並行する独立台帳
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from memory_binding_trace import MemoryBindingTrace


STORE_DIR = Path(__file__).resolve().parent / "data"
BINDING_LEDGER_PATH = STORE_DIR / "memory_binding_ledger.jsonl"


class MemoryBindingStore:
    """MemoryBindingTraceをJSONLファイルに永続化するStore。"""

    def __init__(self, ledger_path: Path = BINDING_LEDGER_PATH):
        self._ledger_path = Path(ledger_path)
        self._ledger_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._ledger_path.exists():
            self._ledger_path.touch()

    def all(self) -> tuple:
        """保存済みの全MemoryBindingTraceを返す(挿入順)。"""
        if not self._ledger_path.exists():
            return ()

        traces = []
        with open(self._ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    traces.append(MemoryBindingTrace.from_dict(data))
        return tuple(traces)

    def append(self, trace: MemoryBindingTrace) -> MemoryBindingTrace:
        """MemoryBindingTraceを1件追記する。"""
        with open(self._ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace.to_dict(), ensure_ascii=False) + "\n")
        return trace

    def find_by_decision_id(self, decision_id: str) -> tuple:
        """指定decision_idに関連するTraceをすべて返す。"""
        return tuple(t for t in self.all() if t.decision_id == decision_id)

    def find_by_knowledge_record_id(self, knowledge_record_id: str) -> tuple:
        """指定memory_idに関連するTraceをすべて返す。"""
        return tuple(t for t in self.all() if t.knowledge_record_id == knowledge_record_id)

    def next_binding_id(self) -> str:
        """連番のbinding_idを発行する(BIND_<date>_<seq>)。"""
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        all_traces = self.all()
        today_count = sum(1 for t in all_traces if t.binding_id.startswith(f"BIND_{date_str}"))
        return f"BIND_{date_str}_{today_count + 1:06d}"

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
