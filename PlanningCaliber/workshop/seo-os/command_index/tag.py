"""command_index/tag.py — TagManager"""
from __future__ import annotations
from .db import CommandIndexDB


class TagManager:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()

    def add(self, command_id: str, tag: str) -> None:
        self._db.execute_write(
            "INSERT OR IGNORE INTO tags(command_id,tag) VALUES(?,?)",
            (command_id, tag.lower())
        )

    def remove(self, command_id: str, tag: str) -> None:
        self._db.execute_write(
            "DELETE FROM tags WHERE command_id=? AND tag=?",
            (command_id, tag.lower())
        )

    def list_for_command(self, command_id: str) -> list[str]:
        rows = self._db.execute(
            "SELECT tag FROM tags WHERE command_id=? ORDER BY tag", (command_id,)
        )
        return [r["tag"] for r in rows]

    def find_commands_by_tag(self, tag: str) -> list[str]:
        rows = self._db.execute(
            "SELECT DISTINCT command_id FROM tags WHERE tag=?", (tag.lower(),)
        )
        return [r["command_id"] for r in rows]

    def top_tags(self, limit: int = 20) -> list[dict]:
        rows = self._db.execute(
            "SELECT tag, COUNT(*) as count FROM tags GROUP BY tag "
            "ORDER BY count DESC LIMIT ?", (limit,)
        )
        return [dict(r) for r in rows]
