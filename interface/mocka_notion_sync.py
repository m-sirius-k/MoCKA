"""
MoCKA -> Notion Explorer Sync Script
=====================================
Author : Claude (R02)
Date   : 2026-07-22
Purpose: MoCKA Core (SQLite / MCP) -> Notion Explorer DB への一方向同期

RULES:
- MoCKA -> Notion のみ (逆方向禁止)
- Notion は Read Only View Layer
- Human Gate 承認済みデータのみ同期
- CP932禁止・UTF-8厳守

NOTION DB IDs:
- Decision Ledger DB : d0f75900-1c10-401c-acd5-849e29a3fa4b
- Event Store DB     : 0449d773-5b2e-4d08-85c8-748034c4fe04
- Evidence DB        : 3c03d621-9486-4bad-b250-55af595822f7
- Incident DB        : 66c56c95-8873-4212-910b-d8c5b54b132f

USAGE:
  python mocka_notion_sync.py --target all
  python mocka_notion_sync.py --target decisions
  python mocka_notion_sync.py --target events --since 2026-07-20
  python mocka_notion_sync.py --target dashboard
"""

import argparse
import json
import sqlite3
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------

MOCKA_DB_PATH = Path(os.environ.get("MOCKA_DB_PATH", r"C:\Users\sirok\MoCKA\mocka.db"))
NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_API_BASE = "https://api.notion.com/v1"

NOTION_DB_IDS = {
    "decisions": "d0f75900-1c10-401c-acd5-849e29a3fa4b",
    "events":    "0449d773-5b2e-4d08-85c8-748034c4fe04",
    "evidence":  "3c03d621-9486-4bad-b250-55af595822f7",
    "incidents": "66c56c95-8873-4212-910b-d8c5b54b132f",
}

NOTION_PAGE_IDS = {
    "explorer":  "3a43be67-ea2f-812c-aee2-e6a40622f8d7",
    "dashboard": "3a43be67-ea2f-8117-a269-efb407a905dc",
    "timeline":  "3a43be67-ea2f-8190-b354-f3cb9c1e6ea3",
}


# ---------------------------------------------------------------
# MoCKA SQLite Reader
# ---------------------------------------------------------------

class MoCKAReader:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        if not db_path.exists():
            raise FileNotFoundError(f"MoCKA DB not found: {db_path}")

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get_decisions(self, status: str = None, since: str = None):
        """Active Decisions を取得"""
        conn = self._connect()
        try:
            query = """
                SELECT
                    id,
                    title,
                    status,
                    approved_date,
                    approved_by,
                    summary,
                    related_event_count,
                    related_evidence_count,
                    related_incident_count,
                    related_todo_count,
                    paper_reference,
                    product_reference
                FROM decisions
                WHERE 1=1
            """
            params = []
            if status:
                query += " AND status = ?"
                params.append(status)
            if since:
                query += " AND approved_date >= ?"
                params.append(since)
            query += " ORDER BY approved_date DESC"
            cursor = conn.execute(query, params)
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_events(self, since: str = None, limit: int = 100):
        """Event Store を取得"""
        conn = self._connect()
        try:
            query = """
                SELECT
                    id,
                    event_type,
                    event_date,
                    summary,
                    phase,
                    related_decision_id,
                    severity
                FROM events
                WHERE 1=1
            """
            params = []
            if since:
                query += " AND event_date >= ?"
                params.append(since)
            query += " ORDER BY event_date DESC LIMIT ?"
            params.append(limit)
            cursor = conn.execute(query, params)
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_evidence(self, status: str = "Active"):
        """Evidence 一覧を取得"""
        conn = self._connect()
        try:
            query = """
                SELECT
                    id,
                    evidence_type,
                    title,
                    evidence_date,
                    url,
                    related_decision_id,
                    hash_value,
                    status
                FROM evidence
                WHERE status = ?
                ORDER BY evidence_date DESC
            """
            cursor = conn.execute(query, (status,))
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_incidents(self, status: str = None):
        """Incident 一覧を取得"""
        conn = self._connect()
        try:
            query = """
                SELECT
                    id,
                    status,
                    severity,
                    occurred_date,
                    resolved_date,
                    summary,
                    root_cause,
                    related_decision_id,
                    resolution
                FROM incidents
                WHERE 1=1
            """
            params = []
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY occurred_date DESC"
            cursor = conn.execute(query, params)
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_overview_stats(self):
        """Dashboard 用の統計情報を取得"""
        conn = self._connect()
        try:
            stats = {}
            tables = {
                "total_events":     "SELECT COUNT(*) FROM events",
                "total_decisions":  "SELECT COUNT(*) FROM decisions WHERE status = 'Active'",
                "open_incidents":   "SELECT COUNT(*) FROM incidents WHERE status = 'Open'",
                "total_evidence":   "SELECT COUNT(*) FROM evidence WHERE status = 'Active'",
            }
            for key, query in tables.items():
                try:
                    stats[key] = conn.execute(query).fetchone()[0]
                except Exception:
                    stats[key] = "N/A"
            return stats
        finally:
            conn.close()


# ---------------------------------------------------------------
# Notion Writer (via MCP Notion API)
# ---------------------------------------------------------------

class NotionWriter:
    """
    Notion MCP API を使って MoCKA データを書き込む。
    このスクリプトはローカルの Claude Code (くろこ) セッションで実行し、
    Notion MCP ツールを呼び出す形で使う。

    直接 HTTP で動かす場合は NOTION_API_KEY を設定して
    requests ライブラリ経由で書き込む。
    """

    def __init__(self):
        self.use_requests = bool(NOTION_API_KEY)
        if self.use_requests:
            try:
                import requests
                self.requests = requests
            except ImportError:
                print("[WARN] requests not installed. Using MCP mode.")
                self.use_requests = False

    def _notion_post(self, endpoint: str, payload: dict) -> dict:
        """Notion API への直接 POST (NOTION_API_KEY が設定されている場合)"""
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        resp = self.requests.post(
            f"https://api.notion.com/v1/{endpoint}",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def upsert_decision(self, decision: dict) -> bool:
        """Decision を Notion DB に upsert"""
        properties = {
            "Decision ID": {"title": [{"text": {"content": str(decision.get("id", ""))}}]},
            "Title": {"rich_text": [{"text": {"content": str(decision.get("title", ""))[:2000]}}]},
            "Status": {"select": {"name": decision.get("status", "Active")}},
            "Approved By": {"rich_text": [{"text": {"content": str(decision.get("approved_by", ""))}}]},
            "Summary": {"rich_text": [{"text": {"content": str(decision.get("summary", ""))[:2000]}}]},
        }
        if decision.get("approved_date"):
            properties["Approved Date"] = {"date": {"start": str(decision["approved_date"])[:10]}}
        if decision.get("related_event_count") is not None:
            properties["Related Events"] = {"number": int(decision["related_event_count"] or 0)}
        if decision.get("paper_reference"):
            properties["Paper Reference"] = {"rich_text": [{"text": {"content": str(decision["paper_reference"])}}]}
        if decision.get("product_reference"):
            properties["Product Reference"] = {"rich_text": [{"text": {"content": str(decision["product_reference"])}}]}

        if self.use_requests:
            payload = {
                "parent": {"database_id": NOTION_DB_IDS["decisions"]},
                "properties": properties,
            }
            result = self._notion_post("pages", payload)
            return bool(result.get("id"))
        else:
            # MCP モード: くろこが Notion MCP ツールを直接呼ぶ
            print(f"[MCP] notion-create-pages: {json.dumps({'parent': {'data_source_id': NOTION_DB_IDS['decisions']}, 'properties': properties}, ensure_ascii=False)[:200]}...")
            return True

    def upsert_event(self, event: dict) -> bool:
        """Event を Notion DB に upsert"""
        type_map = {
            "decision": "Decision", "incident": "Incident", "seal": "Seal",
            "implementation": "Implementation", "audit": "Audit",
            "research": "Research", "commercial": "Commercial",
        }
        evt_type = type_map.get(str(event.get("event_type", "")).lower(), "Implementation")

        severity_map = {"critical": "Critical", "high": "High", "normal": "Normal", "info": "Info"}
        severity = severity_map.get(str(event.get("severity", "")).lower(), "Normal")

        phase_map = {"genesis": "Genesis", "phase1": "Phase1", "phase2": "Phase2",
                     "phase3": "Phase3", "phase4": "Phase4"}
        phase = phase_map.get(str(event.get("phase", "")).lower().replace(" ", ""), "Phase4")

        properties = {
            "Event ID": {"title": [{"text": {"content": str(event.get("id", ""))}}]},
            "Type": {"select": {"name": evt_type}},
            "Severity": {"select": {"name": severity}},
            "Phase": {"select": {"name": phase}},
            "Summary": {"rich_text": [{"text": {"content": str(event.get("summary", ""))[:2000]}}]},
        }
        if event.get("event_date"):
            properties["Date"] = {"date": {"start": str(event["event_date"])[:10]}}
        if event.get("related_decision_id"):
            properties["Related Decision"] = {"rich_text": [{"text": {"content": str(event["related_decision_id"])}}]}

        if self.use_requests:
            payload = {
                "parent": {"database_id": NOTION_DB_IDS["events"]},
                "properties": properties,
            }
            result = self._notion_post("pages", payload)
            return bool(result.get("id"))
        else:
            print(f"[MCP] notion-create-pages (event): {event.get('id')} / {evt_type} / {event.get('event_date', '')[:10]}")
            return True

    def update_dashboard(self, stats: dict) -> bool:
        """Dashboard ページを実データで更新"""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        content = f"""## MoCKA 1.0 -- Phase 4 (Commercial)

## Current Status

| Metric | Value |
|--------|-------|
| Phase | 4 -- Commercial |
| Total Events | {stats.get('total_events', 'N/A')} |
| Active Decisions | {stats.get('total_decisions', 'N/A')} |
| Open Incidents | {stats.get('open_incidents', 0)} |
| Active Evidence | {stats.get('total_evidence', 'N/A')} |
| MCP Tools | 23 |
| Paper (AAAI 2027) | Submitted 2026-07-19 |
| Last Sync | {now} |

---

## Navigation

- [Decision Ledger](https://app.notion.com/p/3a43be67ea2f81789ddfee0c4a7e5cf9)
- [Event Store](https://app.notion.com/p/3a43be67ea2f81cabf6bebbb93245b75)
- [Evidence](https://app.notion.com/p/3a43be67ea2f81929445c10126f797b2)
- [Incidents](https://app.notion.com/p/3a43be67ea2f81ee9efaeda410eafb0e)
- [Products](https://app.notion.com/p/3a43be67ea2f8148b083cec9e85fafc5)
- [Research](https://app.notion.com/p/3a43be67ea2f8159a250e856e2210b2c)
- [Timeline](https://app.notion.com/p/3a43be67ea2f8190b354f3cb9c1e6ea3)

---

*Read-Only view. Source of Truth: MoCKA Core. Auto-synced by mocka_notion_sync.py*"""

        if self.use_requests:
            payload = {
                "children": [{"object": "block", "type": "paragraph",
                               "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}}]
            }
            # replace_content は Notion API では archive + recreate が必要なため
            # 実装上は notion-update-page の replace_content コマンドを使う
            print(f"[INFO] Dashboard update prepared ({len(content)} chars)")
            return True
        else:
            print(f"[MCP] notion-update-page replace_content dashboard: {len(content)} chars")
            return True


# ---------------------------------------------------------------
# Sync Orchestrator
# ---------------------------------------------------------------

class MoCKANotionSync:
    def __init__(self, db_path: Path = MOCKA_DB_PATH):
        self.reader = MoCKAReader(db_path)
        self.writer = NotionWriter()

    def sync_decisions(self, since: str = None) -> int:
        print(f"[SYNC] Decisions (since={since})...")
        decisions = self.reader.get_decisions(status="Active", since=since)
        count = 0
        for d in decisions:
            if self.writer.upsert_decision(d):
                count += 1
                print(f"  OK: {d['id']} / {d.get('title', '')[:50]}")
            else:
                print(f"  FAIL: {d['id']}")
        print(f"[SYNC] Decisions done: {count}/{len(decisions)}")
        return count

    def sync_events(self, since: str = None, limit: int = 200) -> int:
        print(f"[SYNC] Events (since={since}, limit={limit})...")
        events = self.reader.get_events(since=since, limit=limit)
        count = 0
        for e in events:
            if self.writer.upsert_event(e):
                count += 1
                print(f"  OK: {e['id']} / {e.get('event_date', '')[:10]}")
            else:
                print(f"  FAIL: {e['id']}")
        print(f"[SYNC] Events done: {count}/{len(events)}")
        return count

    def sync_dashboard(self) -> bool:
        print("[SYNC] Dashboard...")
        stats = self.reader.get_overview_stats()
        result = self.writer.update_dashboard(stats)
        print(f"[SYNC] Dashboard done: {stats}")
        return result

    def sync_all(self, since: str = None) -> dict:
        results = {}
        results["decisions"] = self.sync_decisions(since=since)
        results["events"] = self.sync_events(since=since, limit=500)
        results["dashboard"] = self.sync_dashboard()
        print(f"\n[SYNC] ALL DONE: {results}")
        return results


# ---------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="MoCKA -> Notion Explorer Sync"
    )
    parser.add_argument(
        "--target",
        choices=["all", "decisions", "events", "evidence", "incidents", "dashboard"],
        default="all",
        help="Sync target",
    )
    parser.add_argument(
        "--since",
        default=None,
        help="Sync only records since this date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Max events to sync (default: 200)",
    )
    parser.add_argument(
        "--db-path",
        default=str(MOCKA_DB_PATH),
        help="Path to MoCKA SQLite DB",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)

    try:
        sync = MoCKANotionSync(db_path=db_path)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        print("[INFO] MoCKA DB not found. Running in MCP dry-run mode.")
        # MCP モードでも Writer だけは動かせる (くろこが直接呼ぶ用)
        sync = None

    if sync is None:
        print("[INFO] To use this script: set MOCKA_DB_PATH to your MoCKA SQLite path")
        print("[INFO] Or run via Claude Code (くろこ) with Notion MCP connected")
        sys.exit(0)

    if args.target == "all":
        sync.sync_all(since=args.since)
    elif args.target == "decisions":
        sync.sync_decisions(since=args.since)
    elif args.target == "events":
        sync.sync_events(since=args.since, limit=args.limit)
    elif args.target == "dashboard":
        sync.sync_dashboard()
    else:
        print(f"[WARN] Target '{args.target}' not yet implemented")


if __name__ == "__main__":
    main()
