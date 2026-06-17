"""audit/logger.py — AuditLogger: 全操作の監査ログをEvent Runtimeへ自動保存"""
from __future__ import annotations
import json
import requests
from datetime import datetime, timezone
from command_index.db import CommandIndexDB

_MCP_URL = "http://localhost:5002"


class AuditLogger:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()
        self._ensure_table()

    def _ensure_table(self) -> None:
        self._db._conn().execute(
            "CREATE TABLE IF NOT EXISTS audit_log ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "action TEXT NOT NULL,"
            "payload TEXT,"
            "logged_at TEXT NOT NULL"
            ")"
        )
        if not self._db._in_memory:
            with self._db._conn() as conn:
                conn.commit()

    def log(self, action: str, payload: dict | None = None,
            emit_event: bool = True) -> None:
        now = datetime.now(timezone.utc).isoformat()
        payload_str = json.dumps(payload or {}, ensure_ascii=False)
        try:
            conn = self._db._conn()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS audit_log ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "action TEXT NOT NULL, payload TEXT, logged_at TEXT NOT NULL)"
            )
            conn.execute(
                "INSERT INTO audit_log(action,payload,logged_at) VALUES(?,?,?)",
                (action, payload_str, now)
            )
            conn.commit()
            if not self._db._in_memory:
                conn.close()
        except Exception:
            pass

        if emit_event:
            self._emit(action, payload or {})

    def recent(self, limit: int = 20) -> list[dict]:
        try:
            conn = self._db._conn()
            rows = conn.execute(
                "SELECT action, payload, logged_at FROM audit_log "
                "ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            result = []
            for r in rows:
                try:
                    p = json.loads(r["payload"])
                except Exception:
                    p = {}
                result.append({"action": r["action"], "payload": p,
                               "logged_at": r["logged_at"]})
            if not self._db._in_memory:
                conn.close()
            return result
        except Exception:
            return []

    def _emit(self, action: str, payload: dict) -> None:
        event_payload = {
            "title": f"AUDIT: {action}",
            "description": json.dumps(payload, ensure_ascii=False)[:200],
            "author": "SEOCommandIndex-v3",
            "tags": f"audit,seo_command_index,{action}",
        }
        try:
            requests.post(f"{_MCP_URL}/event", json=event_payload, timeout=0.5)
        except Exception:
            pass
