# -*- coding: utf-8 -*-
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR      = Path(__file__).parent.parent / "data"
OVERVIEW_PATH = DATA_DIR / "MOCKA_OVERVIEW.json"
ESSENCE_PATH  = DATA_DIR / "lever_essence.json"
TODO_PATH     = DATA_DIR / "MOCKA_TODO.json"
DB_PATH       = DATA_DIR / "mocka_events.db"

ACTIVE_STATUSES = {"未着手", "進行中"}
PRIORITY_ORDER  = {"最高": 0, "高": 1, "中": 2, "低": 3}


class ContextBuilder:

    def build(self, mode: str = "standard", ai_hint: str = None) -> dict:
        mode    = mode if mode in ("compact", "standard", "extended") else "standard"
        base    = self._load_base()
        todo    = self._load_todo(mode)
        essence = self._load_essence(mode)
        events  = self._load_events(mode)
        return self._assemble(base, todo, essence, events, mode)

    # ------------------------------------------------------------------ loaders

    def _load_base(self) -> dict:
        try:
            raw          = json.loads(OVERVIEW_PATH.read_text(encoding="utf-8"))
            phase        = raw.get("current_phase", "")
            next_actions = raw.get("next_actions", {})
            immediate    = next_actions.get("immediate", [])
            goal         = immediate[0] if immediate else ""
            return {
                "phase":         phase,
                "goal":          goal,
                "last_decision": self._last_decision(),
            }
        except Exception:
            return {"phase": "", "goal": "", "last_decision": ""}

    def _last_decision(self) -> str:
        """最新イベントのtitle + when_ts を返す（when_time は誤カラム名）"""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cur  = conn.cursor()
            # 正: when_ts  (×when_time)
            cur.execute(
                "SELECT title, when_ts FROM events ORDER BY when_ts DESC LIMIT 1"
            )
            row = cur.fetchone()
            conn.close()
            if row and row[0]:
                return f"{row[0]}（{str(row[1])[:10]}）"
        except Exception:
            pass
        return ""

    def _load_todo(self, mode: str) -> list:
        try:
            raw    = json.loads(TODO_PATH.read_text(encoding="utf-8"))
            todos  = raw.get("todos", [])
            active = [t for t in todos if t.get("status") in ACTIVE_STATUSES]
            active.sort(key=lambda t: PRIORITY_ORDER.get(t.get("priority", "低"), 9))
            if mode == "compact":
                active = [t for t in active if t.get("priority") in ("最高", "高")]
            elif mode == "standard":
                active = active[:20]
            # extended = 全件
            return [
                {
                    "id":       t.get("id", ""),
                    "title":    t.get("title", ""),
                    "priority": t.get("priority", ""),
                    "status":   t.get("status", ""),
                }
                for t in active
            ]
        except Exception:
            return []

    def _load_essence(self, mode: str) -> str:
        try:
            raw = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
            if mode == "extended":
                return json.dumps(raw, ensure_ascii=False)
            operation  = raw.get("OPERATION", "")
            philosophy = raw.get("PHILOSOPHY", "")
            return (operation + "\n" + philosophy)[:500]
        except Exception:
            return ""

    def _load_events(self, mode: str) -> list:
        limit = {"compact": 3, "standard": 5, "extended": 30}.get(mode, 5)
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cur  = conn.cursor()
            # 正: when_ts / short_summary  (×when_time / ×description / ×tags)
            cur.execute(
                "SELECT event_id, title, short_summary, when_ts, what_type "
                "FROM events ORDER BY when_ts DESC LIMIT ?",
                (limit,)
            )
            rows = cur.fetchall()
            conn.close()
            return [
                {
                    "id":            r[0],
                    "title":         r[1],
                    "short_summary": r[2],
                    "when":          r[3],
                    "what_type":     r[4],
                }
                for r in rows
            ]
        except Exception:
            return []

    # ----------------------------------------------------------------- assemble

    def _assemble(self, base, todo, essence, events, mode) -> dict:
        body = {
            "meta": {
                "version":      "1.1",
                "mode":         mode,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "phase":         base["phase"],
            "goal":          base["goal"],
            "last_decision": base["last_decision"],
            "active_todo":   todo,
        }
        if mode in ("standard", "extended"):
            body["essence_summary"] = essence
            body["recent_events"]   = events
        if mode == "compact":
            body["recent_events"] = events
        size = len(json.dumps(body, ensure_ascii=False).encode("utf-8"))
        body["meta"]["size_bytes"] = size
        return body

    # --------------------------------------------------------------- shortcuts

    def build_for_gpt(self):     return self.build("standard", "gpt")
    def build_for_gemini(self):  return self.build("extended", "gemini")
    def build_for_compact(self): return self.build("compact")
