"""
Context Runtime v2 — Layer 3: MemoryContext
責務: AI全体の共通理解。5W1H・判断・インシデント歴・教訓を保持する。
MemoryはログではなくAIが人間へ確認する前に参照する唯一の運用正本。
"""
from __future__ import annotations
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_DB_PATH = Path(__file__).parents[2] / "data" / "mocka_events.db"
_SNAPSHOT_DIR = Path(__file__).parents[2] / "data" / "context_snapshots"


@dataclass
class FiveW1H:
    who: str = ""
    what: str = ""
    why: str = ""
    where: str = ""
    when: str = ""
    how: str = ""

    def to_dict(self) -> dict:
        return {"who": self.who, "what": self.what, "why": self.why,
                "where": self.where, "when": self.when, "how": self.how}

    @classmethod
    def from_dict(cls, d: dict) -> "FiveW1H":
        return cls(**{k: d.get(k, "") for k in ("who", "what", "why", "where", "when", "how")})


@dataclass
class DecisionRecord:
    decision: str = ""
    reason: str = ""
    evidence: str = ""
    related_events: list = field(default_factory=list)
    related_files: list = field(default_factory=list)
    related_directories: list = field(default_factory=list)
    related_urls: list = field(default_factory=list)
    related_documents: list = field(default_factory=list)
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "reason": self.reason,
            "evidence": self.evidence,
            "related_events": self.related_events,
            "related_files": self.related_files,
            "related_directories": self.related_directories,
            "related_urls": self.related_urls,
            "related_documents": self.related_documents,
            "timestamp": self.timestamp,
        }


@dataclass
class MemoryContext:
    # --- 5W1H ---
    five_w1h: FiveW1H = field(default_factory=FiveW1H)

    # --- Decisions ---
    architecture_decisions: list = field(default_factory=list)   # list[DecisionRecord]
    completed_tasks: list = field(default_factory=list)
    pending_tasks: list = field(default_factory=list)

    # --- Incident History ---
    incident_history: list = field(default_factory=list)
    lessons_learned: list = field(default_factory=list)

    # --- Related Objects ---
    related_files: list = field(default_factory=list)
    related_directories: list = field(default_factory=list)
    related_urls: list = field(default_factory=list)
    related_documents: list = field(default_factory=list)
    related_events: list = field(default_factory=list)

    # --- Meta ---
    updated_at: str = ""
    event_count: int = 0

    @classmethod
    def load(cls, limit_incidents: int = 10, limit_events: int = 20) -> "MemoryContext":
        ctx = cls()
        ctx.updated_at = datetime.now(timezone.utc).isoformat()
        ctx._load_from_db(limit_incidents, limit_events)
        ctx._load_from_snapshot()
        return ctx

    def _load_from_db(self, limit_incidents: int, limit_events: int) -> None:
        if not _DB_PATH.exists():
            return
        try:
            conn = sqlite3.connect(str(_DB_PATH))
            conn.row_factory = sqlite3.Row

            # 総イベント数
            row = conn.execute("SELECT COUNT(*) as cnt FROM events").fetchone()
            self.event_count = row["cnt"] if row else 0

            # 最新イベント (5W1H カラム構造)
            rows = conn.execute(
                "SELECT event_id, what_type, why_purpose, who_actor FROM events "
                "ORDER BY rowid DESC LIMIT ?", (limit_events,)
            ).fetchall()
            self.related_events = [
                {
                    "event_id": r["event_id"],
                    "what": r["what_type"] or "",
                    "why": (r["why_purpose"] or "")[:80],
                    "who": r["who_actor"] or "",
                }
                for r in rows
            ]

            # インシデント履歴 (why_purpose に incident を含む)
            rows = conn.execute(
                "SELECT event_id, what_type, why_purpose FROM events "
                "WHERE why_purpose LIKE ? OR what_type LIKE ? "
                "ORDER BY rowid DESC LIMIT ?",
                ("%incident%", "%INCIDENT%", limit_incidents)
            ).fetchall()
            self.incident_history = [
                {
                    "event_id": r["event_id"],
                    "what": r["what_type"] or "",
                    "why": (r["why_purpose"] or "")[:200],
                }
                for r in rows
            ]

            # Architecture Decisions
            rows = conn.execute(
                "SELECT event_id, what_type, why_purpose FROM events "
                "WHERE why_purpose LIKE ? OR why_purpose LIKE ? "
                "ORDER BY rowid DESC LIMIT 10",
                ("%architecture%", "%decision%")
            ).fetchall()
            self.architecture_decisions = [
                DecisionRecord(
                    decision=r["what_type"] or "",
                    evidence=r["event_id"],
                    reason=(r["why_purpose"] or "")[:300],
                    timestamp=r["event_id"][:12] if r["event_id"] else "",
                ).to_dict()
                for r in rows
            ]

            conn.close()
        except Exception:
            pass

    def _load_from_snapshot(self) -> None:
        snap = _SNAPSHOT_DIR / "memory_context_latest.json"
        if not snap.exists():
            return
        try:
            data = json.loads(snap.read_text(encoding="utf-8"))
            # スナップショットからペンディングタスク・教訓・5W1Hを復元
            self.pending_tasks = data.get("pending_tasks", self.pending_tasks)
            self.lessons_learned = data.get("lessons_learned", self.lessons_learned)
            w = data.get("five_w1h", {})
            if w:
                self.five_w1h = FiveW1H.from_dict(w)
        except Exception:
            pass

    def record_decision(self, decision: str, reason: str,
                        evidence: str = "", related_events: list | None = None,
                        related_files: list | None = None) -> DecisionRecord:
        rec = DecisionRecord(
            decision=decision,
            reason=reason,
            evidence=evidence,
            related_events=related_events or [],
            related_files=related_files or [],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.architecture_decisions.insert(0, rec.to_dict())
        return rec

    def add_lesson(self, lesson: str) -> None:
        entry = {"lesson": lesson, "at": datetime.now(timezone.utc).isoformat()}
        self.lessons_learned.insert(0, entry)

    def set_5w1h(self, who: str = "", what: str = "", why: str = "",
                 where: str = "", when: str = "", how: str = "") -> None:
        self.five_w1h = FiveW1H(
            who=who or self.five_w1h.who,
            what=what or self.five_w1h.what,
            why=why or self.five_w1h.why,
            where=where or self.five_w1h.where,
            when=when or self.five_w1h.when,
            how=how or self.five_w1h.how,
        )

    def to_dict(self) -> dict:
        return {
            "layer": "Memory",
            "five_w1h": self.five_w1h.to_dict(),
            "architecture_decisions": self.architecture_decisions[:10],
            "completed_tasks": self.completed_tasks,
            "pending_tasks": self.pending_tasks,
            "incident_history": self.incident_history,
            "lessons_learned": self.lessons_learned,
            "related_files": self.related_files,
            "related_directories": self.related_directories,
            "related_urls": self.related_urls,
            "related_documents": self.related_documents,
            "related_events": self.related_events[:20],
            "updated_at": self.updated_at,
            "event_count": self.event_count,
        }
