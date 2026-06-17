"""command_index/registry.py — CommandRegistry: 登録・検索・一覧"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .db import CommandIndexDB
from .metadata import CommandMetadata, CommandStatus

_REGISTRY_JSON = Path(__file__).parent.parent / "data" / "registry.json"

_BUILTIN_COMMANDS = [
    # SEO Engine
    {"id":"seo.analyze","name":"seo.analyze","description":"SEO総合分析を実行する","category":"seo","tags":["seo","analyze","score"],"aliases":["analyze","seo-check"]},
    {"id":"seo.metadata","name":"seo.metadata","description":"メタデータ(title/description/canonical)を生成する","category":"seo","tags":["seo","metadata","title"],"aliases":["meta","metadata"]},
    {"id":"seo.ogp","name":"seo.ogp","description":"OGP(Open Graph)タグを生成する","category":"seo","tags":["seo","ogp","social"],"aliases":["ogp","og"]},
    {"id":"seo.schema","name":"seo.schema","description":"Schema.org構造化データを生成する","category":"seo","tags":["seo","schema","json-ld"],"aliases":["schema","structured-data"]},
    {"id":"seo.keyword","name":"seo.keyword","description":"キーワード密度を分析する","category":"seo","tags":["seo","keyword","density"],"aliases":["keyword","kw"]},
    {"id":"seo.readability","name":"seo.readability","description":"可読性グレードをチェックする","category":"seo","tags":["seo","readability","grade"],"aliases":["readability","grade"]},
    {"id":"seo.sitemap","name":"seo.sitemap","description":"サイトマップXMLを生成する","category":"seo","tags":["seo","sitemap","xml"],"aliases":["sitemap"]},
    {"id":"seo.robots","name":"seo.robots","description":"robots.txtを生成・検証する","category":"seo","tags":["seo","robots","crawl"],"aliases":["robots"]},
    # Publishing Pipeline
    {"id":"publish.job.create","name":"publish.job.create","description":"パブリッシュジョブを作成する","category":"publish","tags":["publish","job","create"],"aliases":["create-job","new-job"],"dependencies":["seo.analyze"]},
    {"id":"publish.job.approve","name":"publish.job.approve","description":"ジョブを承認して配信キューに入れる","category":"publish","tags":["publish","approve","gate"],"aliases":["approve"],"dependencies":["publish.job.create"]},
    {"id":"publish.job.run","name":"publish.job.run","description":"ジョブのパイプラインを実行する","category":"publish","tags":["publish","run","pipeline"],"aliases":["run","execute"],"dependencies":["publish.job.approve"]},
    # Distribution
    {"id":"dist.wordpress","name":"dist.wordpress","description":"WordPress へ配信する","category":"distribution","tags":["dist","wordpress","cms"],"aliases":["wp","wordpress"],"dependencies":["publish.job.run"]},
    {"id":"dist.sftp","name":"dist.sftp","description":"SFTP でファイルを転送する","category":"distribution","tags":["dist","sftp","transfer"],"aliases":["sftp"],"dependencies":["publish.job.run"]},
    {"id":"dist.x","name":"dist.x","description":"X(Twitter) へ投稿する","category":"distribution","tags":["dist","x","social","twitter"],"aliases":["x","twitter"]},
    {"id":"dist.instagram","name":"dist.instagram","description":"Instagram へ投稿する","category":"distribution","tags":["dist","instagram","social"],"aliases":["ig","instagram"]},
    # Caliber
    {"id":"caliber.health","name":"caliber.health","description":"Caliber ワーカーのヘルスチェックを実行する","category":"caliber","tags":["caliber","health","check"],"aliases":["health","health-check"]},
    {"id":"caliber.recommend","name":"caliber.recommend","description":"AI推奨アクションを取得する","category":"caliber","tags":["caliber","recommend","ai"],"aliases":["recommend"]},
    {"id":"caliber.lifecycle","name":"caliber.lifecycle","description":"ワーカーのライフサイクル状態を確認する","category":"caliber","tags":["caliber","lifecycle","worker"],"aliases":["lifecycle"]},
    # Governance
    {"id":"gov.snapshot","name":"gov.snapshot","description":"現在のContext Runtimeスナップショットを保存する","category":"governance","tags":["governance","snapshot","context"],"aliases":["snapshot","snap"]},
    {"id":"gov.audit","name":"gov.audit","description":"監査ログを確認する","category":"governance","tags":["governance","audit","log"],"aliases":["audit"],"dependencies":["gov.snapshot"]},
    {"id":"gov.boundary","name":"gov.boundary","description":"Architecture境界違反チェックを実行する","category":"governance","tags":["governance","boundary","architecture"],"aliases":["boundary-check","arch-check"]},
    # Context
    {"id":"ctx.memory","name":"ctx.memory","description":"Memory Runtimeの現在状態を取得する","category":"context","tags":["context","memory","runtime"],"aliases":["memory","mem"]},
    {"id":"ctx.working","name":"ctx.working","description":"Working Contextを更新する","category":"context","tags":["context","working","task"],"aliases":["working","work"]},
    {"id":"ctx.resume","name":"ctx.resume","description":"前回スナップショットから作業を再開する","category":"context","tags":["context","resume","restore"],"aliases":["resume","restore"]},
]


class CommandRegistry:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()
        self._seed_builtins()

    def _seed_builtins(self) -> None:
        existing = {r["id"] for r in self._db.execute("SELECT id FROM commands")}
        now = datetime.now(timezone.utc).isoformat()
        for c in _BUILTIN_COMMANDS:
            if c["id"] in existing:
                continue
            self._db.execute_write(
                "INSERT INTO commands(id,name,description,category,status,version,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (c["id"], c["name"], c["description"], c["category"],
                 "active", "1.0.0", now, now)
            )
            for alias in c.get("aliases", []):
                try:
                    self._db.execute_write(
                        "INSERT INTO aliases(alias,command_id,created_at) VALUES(?,?,?)",
                        (alias, c["id"], now)
                    )
                except Exception:
                    pass
            for tag in c.get("tags", []):
                try:
                    self._db.execute_write(
                        "INSERT INTO tags(command_id,tag) VALUES(?,?)",
                        (c["id"], tag)
                    )
                except Exception:
                    pass
            for dep in c.get("dependencies", []):
                try:
                    self._db.execute_write(
                        "INSERT INTO dependencies(from_id,to_id) VALUES(?,?)",
                        (c["id"], dep)
                    )
                except Exception:
                    pass
        self._export_registry_json()

    def register(self, meta: CommandMetadata) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._db.execute_write(
            "INSERT OR REPLACE INTO commands"
            "(id,name,description,category,status,version,created_at,updated_at)"
            " VALUES(?,?,?,?,?,?,COALESCE((SELECT created_at FROM commands WHERE id=?),?),?)",
            (meta.id, meta.name, meta.description, meta.category,
             meta.status.value, meta.version, meta.id, now, now)
        )
        for alias in meta.aliases:
            try:
                self._db.execute_write(
                    "INSERT OR IGNORE INTO aliases(alias,command_id,created_at) VALUES(?,?,?)",
                    (alias, meta.id, now)
                )
            except Exception:
                pass
        for tag in meta.tags:
            try:
                self._db.execute_write(
                    "INSERT OR IGNORE INTO tags(command_id,tag) VALUES(?,?)",
                    (meta.id, tag)
                )
            except Exception:
                pass
        self._export_registry_json()

    def get(self, command_id: str) -> Optional[CommandMetadata]:
        rows = self._db.execute(
            "SELECT c.*, GROUP_CONCAT(DISTINCT a.alias) as alias_list, "
            "GROUP_CONCAT(DISTINCT t.tag) as tag_list "
            "FROM commands c "
            "LEFT JOIN aliases a ON a.command_id=c.id "
            "LEFT JOIN tags t ON t.command_id=c.id "
            "WHERE c.id=? GROUP BY c.id", (command_id,)
        )
        if not rows:
            return None
        return self._row_to_meta(rows[0])

    def find_by_alias(self, alias: str) -> Optional[CommandMetadata]:
        rows = self._db.execute(
            "SELECT command_id FROM aliases WHERE alias=?", (alias,)
        )
        if not rows:
            return None
        return self.get(rows[0]["command_id"])

    def list_all(self, category: str | None = None,
                 status: CommandStatus | None = None) -> list[CommandMetadata]:
        where, params = [], []
        if category:
            where.append("c.category=?"); params.append(category)
        if status:
            where.append("c.status=?"); params.append(status.value)
        clause = "WHERE " + " AND ".join(where) if where else ""
        rows = self._db.execute(
            f"SELECT c.*, GROUP_CONCAT(DISTINCT a.alias) as alias_list, "
            f"GROUP_CONCAT(DISTINCT t.tag) as tag_list "
            f"FROM commands c "
            f"LEFT JOIN aliases a ON a.command_id=c.id "
            f"LEFT JOIN tags t ON t.command_id=c.id "
            f"{clause} GROUP BY c.id ORDER BY c.category,c.name",
            tuple(params)
        )
        return [self._row_to_meta(r) for r in rows]

    def search(self, query: str) -> list[CommandMetadata]:
        q = f"%{query}%"
        rows = self._db.execute(
            "SELECT DISTINCT c.id FROM commands c "
            "LEFT JOIN aliases a ON a.command_id=c.id "
            "LEFT JOIN tags t ON t.command_id=c.id "
            "WHERE c.name LIKE ? OR c.description LIKE ? "
            "OR a.alias LIKE ? OR t.tag LIKE ?",
            (q, q, q, q)
        )
        return [self.get(r["id"]) for r in rows if self.get(r["id"])]

    def _row_to_meta(self, r: dict) -> CommandMetadata:
        return CommandMetadata(
            id=r["id"], name=r["name"],
            description=r["description"], category=r["category"],
            status=CommandStatus(r.get("status", "active")),
            version=r.get("version", "1.0.0"),
            aliases=[a for a in (r.get("alias_list") or "").split(",") if a],
            tags=[t for t in (r.get("tag_list") or "").split(",") if t],
            created_at=r.get("created_at", ""),
            updated_at=r.get("updated_at", ""),
        )

    def _export_registry_json(self) -> None:
        try:
            all_cmds = self.list_all()
            data = {
                "version": "3.0",
                "count": len(all_cmds),
                "commands": {c.id: c.to_dict() for c in all_cmds},
            }
            _REGISTRY_JSON.parent.mkdir(parents=True, exist_ok=True)
            _REGISTRY_JSON.write_text(
                __import__("json").dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass
