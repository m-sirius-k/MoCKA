#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connector Log — Institution Log Extension (TODO_274)

Connector呼び出しの詳細記録を events.db の connector_log テーブルに保存する。
events テーブル（MoCKAコアイベント台帳）とは独立したテーブルで、
Connector固有のメタデータ（AI名/実行時間/成否/再利用可否）を管理する。

テーブル設計:
  connector_log
    id             INTEGER PRIMARY KEY AUTOINCREMENT
    logged_at      TEXT     (ISO 8601 UTC)
    ai_name        TEXT     (例: "ChatGPT", "Perplexity")
    adapter_key    TEXT     (例: "gpt", "perplexity")
    query_hash     TEXT     (クエリ内容のSHA256先頭16文字 — 検索用)
    context_ref    TEXT     (使用したContextのphase + goal先頭50文字)
    execution_ms   INTEGER  (Gateway → AI呼び出し所要時間 ms)
    success        INTEGER  (1=成功, 0=失敗)
    reusable       INTEGER  (1=再利用可能な回答, 0=一時的)
    event_id_ref   TEXT     (events テーブルの参照 event_id)
    capability     TEXT     (使用したCapability, e.g. "web_search")
    role_id        TEXT     (使用したRole, e.g. "R05")
    error_detail   TEXT     (失敗時のエラー詳細)

連携:
  ConnectorCaliber._record_event() から ConnectorLog.record() を呼び出す。
  Lifecycle Manager (TODO_275) はこのテーブルを読んでEssence候補を抽出する。
"""
from __future__ import annotations

import hashlib
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_DB_PATH = Path(os.environ.get("MOCKA_ROOT", r"C:\Users\sirok\MoCKA")) / "data" / "mocka_events.db"

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS connector_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_at    TEXT    NOT NULL,
    ai_name      TEXT    NOT NULL,
    adapter_key  TEXT    NOT NULL,
    query_hash   TEXT,
    context_ref  TEXT,
    execution_ms INTEGER,
    success      INTEGER NOT NULL DEFAULT 1,
    reusable     INTEGER NOT NULL DEFAULT 0,
    event_id_ref TEXT,
    capability   TEXT,
    role_id      TEXT,
    error_detail TEXT
)
"""


def _hash_query(query: str) -> str:
    return hashlib.sha256(query.encode("utf-8", errors="replace")).hexdigest()[:16]


def _context_ref(context: Optional[dict]) -> str:
    if not context:
        return ""
    phase = context.get("phase", "")[:30]
    goal  = context.get("goal", "")[:30]
    return f"{phase} / {goal}"


class ConnectorLog:
    """
    Connector呼び出しの制度ログ。
    ConnectorCaliber._record_event() から統合して使用する。
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._db = Path(db_path or _DB_PATH)
        self._ensure_table()

    def _ensure_table(self):
        try:
            conn = sqlite3.connect(str(self._db))
            conn.execute(_CREATE_SQL)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ConnectorLog] テーブル初期化エラー: {e}")

    def record(self,
               ai_name:      str,
               adapter_key:  str,
               query:        str,
               context:      Optional[dict] = None,
               execution_ms: Optional[int] = None,
               success:      bool = True,
               reusable:     bool = False,
               event_id_ref: Optional[str] = None,
               capability:   Optional[str] = None,
               role_id:      Optional[str] = None,
               error_detail: Optional[str] = None) -> int:
        """
        Connector呼び出し1件をconnector_logに記録する。

        Args:
            ai_name:      AI名 (e.g. "ChatGPT")
            adapter_key:  アダプターキー (e.g. "gpt")
            query:        送信クエリ文字列
            context:      ContextBuilder.build()の戻り値 (dict)
            execution_ms: 実行時間 (ms)
            success:      成功フラグ
            reusable:     回答の再利用可否（Lifecycle Managerが参照）
            event_id_ref: eventsテーブルの対応イベントID
            capability:   使用Capability (e.g. "web_search")
            role_id:      使用Role ID (e.g. "R05")
            error_detail: 失敗時のエラー詳細

        Returns:
            挿入レコードのid (int)、失敗時は -1
        """
        try:
            conn = sqlite3.connect(str(self._db))
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO connector_log
                   (logged_at, ai_name, adapter_key, query_hash, context_ref,
                    execution_ms, success, reusable, event_id_ref,
                    capability, role_id, error_detail)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    datetime.now(timezone.utc).isoformat(),
                    ai_name[:100],
                    adapter_key[:50],
                    _hash_query(query),
                    _context_ref(context),
                    execution_ms,
                    1 if success else 0,
                    1 if reusable else 0,
                    event_id_ref,
                    capability[:50] if capability else None,
                    role_id[:10] if role_id else None,
                    error_detail[:500] if error_detail else None,
                )
            )
            conn.commit()
            row_id = cur.lastrowid
            conn.close()
            return row_id
        except Exception as e:
            print(f"[ConnectorLog] 記録エラー: {e}")
            return -1

    def recent(self, limit: int = 20, ai_name: Optional[str] = None,
               success_only: bool = False) -> list[dict]:
        """最近のConnector呼び出しを取得する（Lifecycle Manager用）"""
        try:
            conn = sqlite3.connect(str(self._db))
            conn.row_factory = sqlite3.Row
            where = []
            params = []
            if ai_name:
                where.append("ai_name = ?")
                params.append(ai_name)
            if success_only:
                where.append("success = 1")
            where_sql = f"WHERE {' AND '.join(where)}" if where else ""
            rows = conn.execute(
                f"SELECT * FROM connector_log {where_sql} ORDER BY id DESC LIMIT ?",
                params + [limit]
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"[ConnectorLog] 読み込みエラー: {e}")
            return []

    def stats(self) -> dict:
        """Connector呼び出し統計（監査用）"""
        try:
            conn = sqlite3.connect(str(self._db))
            total     = conn.execute("SELECT COUNT(*) FROM connector_log").fetchone()[0]
            success_c = conn.execute("SELECT COUNT(*) FROM connector_log WHERE success=1").fetchone()[0]
            reusable_c = conn.execute("SELECT COUNT(*) FROM connector_log WHERE reusable=1").fetchone()[0]
            by_ai     = dict(conn.execute(
                "SELECT ai_name, COUNT(*) FROM connector_log GROUP BY ai_name"
            ).fetchall())
            conn.close()
            return {
                "total":        total,
                "success":      success_c,
                "failure":      total - success_c,
                "reusable":     reusable_c,
                "by_ai":        by_ai,
            }
        except Exception as e:
            return {"error": str(e)}


# シングルトン（ConnectorCaliber から import して使う）
connector_log = ConnectorLog()
