# phi_os/dictionary.py
# PHI-OS語彙コア辞書 v1 — MoCKA意味記憶の統一管理レイヤ
# 参照: PHI_OS_CONSTITUTION_v1.md / INSTITUTION_RUNTIME_v1.md

import sqlite3
import datetime
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ─────────────────────────────────────────────────────────────
# 定数・列挙型
# ─────────────────────────────────────────────────────────────

class TermOrigin(str, Enum):
    MANUAL   = "manual"    # 博士または人間が登録
    UNKNOWN  = "unknown"   # Unknown 80%分解から暫定登録
    INFERRED = "inferred"  # 推論エンジンが自動生成


class MeaningStatus(str, Enum):
    ACTIVE     = "active"
    DEPRECATED = "deprecated"
    DRAFT      = "draft"
    DRIFTED    = "drifted"  # Semantic Gravityが閾値を下回った状態


class RelationType(str, Enum):
    DEPENDS_ON  = "depends_on"
    GENERALIZES = "generalizes"
    SPECIALIZES = "specializes"
    CONFLICTS   = "conflicts"
    SYNONYM     = "synonym"


# ─────────────────────────────────────────────────────────────
# データクラス
# ─────────────────────────────────────────────────────────────

@dataclass
class ResolvedMeaning:
    term_id: str
    meaning_id: str
    definition: str
    version: int
    stability_score: float
    semantic_gravity: float
    status: str


@dataclass
class DriftedTerm:
    term_id: str
    meaning_id: str
    semantic_gravity: float
    status: str


# ─────────────────────────────────────────────────────────────
# ユーティリティ
# ─────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ─────────────────────────────────────────────────────────────
# PHI-OS辞書本体
# ─────────────────────────────────────────────────────────────

class PhiOSDictionary:
    """
    MoCKA全体における意味記憶の統一管理。
    語彙の一意性保証・意味バージョン管理・Semantic Gravity連動・
    Unknown領域からの暫定登録を担う「意味の運用空間」。
    """

    def __init__(self, db_path: str = "phi_os_dictionary.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()

        cur.executescript("""
        CREATE TABLE IF NOT EXISTS terms (
            term_id    TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            origin     TEXT NOT NULL DEFAULT 'manual'
        );

        CREATE TABLE IF NOT EXISTS meanings (
            meaning_id       TEXT PRIMARY KEY,
            term_id          TEXT NOT NULL,
            version          INTEGER NOT NULL,
            definition       TEXT NOT NULL,
            stability_score  REAL NOT NULL DEFAULT 0.0,
            semantic_gravity REAL NOT NULL DEFAULT 0.0,
            status           TEXT NOT NULL DEFAULT 'active',
            created_at       TEXT NOT NULL,
            FOREIGN KEY (term_id) REFERENCES terms(term_id)
        );

        CREATE TABLE IF NOT EXISTS dependencies (
            id            TEXT PRIMARY KEY,
            from_term     TEXT NOT NULL,
            to_term       TEXT NOT NULL,
            relation_type TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_meanings_term  ON meanings(term_id);
        CREATE INDEX IF NOT EXISTS idx_meanings_ver   ON meanings(term_id, version DESC);
        CREATE INDEX IF NOT EXISTS idx_dep_from       ON dependencies(from_term);
        """)

        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ─── TERM ───────────────────────────────────────────────

    def register_term(self, term_id: str, origin: TermOrigin = TermOrigin.MANUAL) -> bool:
        """
        Term を登録する。既存の場合は何もしない（INSERT OR IGNORE）。
        Returns: True = 新規登録 / False = 既存スキップ
        """
        cur = self.conn.cursor()
        t = _now()
        cur.execute(
            "INSERT OR IGNORE INTO terms (term_id, created_at, updated_at, origin) VALUES (?, ?, ?, ?)",
            (term_id, t, t, origin.value),
        )
        self.conn.commit()
        return cur.rowcount > 0

    def term_exists(self, term_id: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM terms WHERE term_id=?", (term_id,))
        return cur.fetchone() is not None

    # ─── MEANING ────────────────────────────────────────────

    def add_meaning(
        self,
        term_id: str,
        definition: str,
        stability_score: float = 0.0,
        semantic_gravity: float = 0.0,
        origin: TermOrigin = TermOrigin.MANUAL,
    ) -> str:
        """
        Meaning を追加し、バージョンをインクリメントする。
        Term が未登録であれば自動登録する。
        Returns: meaning_id
        """
        self.register_term(term_id, origin)

        cur = self.conn.cursor()

        # 既存バージョンを deprecated に変更
        cur.execute(
            "UPDATE meanings SET status=? WHERE term_id=? AND status=?",
            (MeaningStatus.DEPRECATED.value, term_id, MeaningStatus.ACTIVE.value),
        )

        # 次バージョン番号を採番
        cur.execute("SELECT MAX(version) FROM meanings WHERE term_id=?", (term_id,))
        row = cur.fetchone()
        version = (row[0] or 0) + 1

        meaning_id = _gen_id("meaning")

        cur.execute(
            """
            INSERT INTO meanings
                (meaning_id, term_id, version, definition,
                 stability_score, semantic_gravity, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                meaning_id, term_id, version, definition,
                stability_score, semantic_gravity,
                MeaningStatus.ACTIVE.value, _now(),
            ),
        )

        # term の updated_at を更新
        cur.execute("UPDATE terms SET updated_at=? WHERE term_id=?", (_now(), term_id))

        self.conn.commit()
        return meaning_id

    # ─── RESOLVE ────────────────────────────────────────────

    def resolve(self, term_id: str) -> Optional[ResolvedMeaning]:
        """
        Term の最新アクティブ意味を返す。
        存在しない場合は None。
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT meaning_id, term_id, definition, version,
                   stability_score, semantic_gravity, status
            FROM meanings
            WHERE term_id=?
            ORDER BY version DESC
            LIMIT 1
            """,
            (term_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return ResolvedMeaning(
            term_id=row["term_id"],
            meaning_id=row["meaning_id"],
            definition=row["definition"],
            version=row["version"],
            stability_score=row["stability_score"],
            semantic_gravity=row["semantic_gravity"],
            status=row["status"],
        )

    def resolve_all_versions(self, term_id: str) -> list[ResolvedMeaning]:
        """Term の全バージョン履歴を version 降順で返す。"""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT meaning_id, term_id, definition, version,
                   stability_score, semantic_gravity, status
            FROM meanings
            WHERE term_id=?
            ORDER BY version DESC
            """,
            (term_id,),
        )
        return [
            ResolvedMeaning(
                term_id=r["term_id"],
                meaning_id=r["meaning_id"],
                definition=r["definition"],
                version=r["version"],
                stability_score=r["stability_score"],
                semantic_gravity=r["semantic_gravity"],
                status=r["status"],
            )
            for r in cur.fetchall()
        ]

    # ─── UPDATE STABILITY ───────────────────────────────────

    def update_gravity(
        self, term_id: str, stability_score: float, semantic_gravity: float
    ) -> bool:
        """
        最新バージョンの stability_score / semantic_gravity を更新する。
        semantic_gravity が drift_threshold を下回ると status が "drifted" になる。
        Returns: True = 更新成功 / False = Term 未存在
        """
        if not self.term_exists(term_id):
            return False

        cur = self.conn.cursor()

        # drift 判定
        drift_threshold = 0.3
        new_status = (
            MeaningStatus.DRIFTED.value
            if semantic_gravity < drift_threshold
            else MeaningStatus.ACTIVE.value
        )

        cur.execute(
            """
            UPDATE meanings
            SET stability_score=?, semantic_gravity=?, status=?
            WHERE term_id=? AND version=(
                SELECT MAX(version) FROM meanings WHERE term_id=?
            )
            """,
            (stability_score, semantic_gravity, new_status, term_id, term_id),
        )
        self.conn.commit()
        return cur.rowcount > 0

    # ─── DEPENDENCY ─────────────────────────────────────────

    def add_dependency(
        self, from_term: str, to_term: str, relation_type: RelationType
    ) -> str:
        """
        Term 間の依存関係を登録する。
        Returns: dependency id
        """
        cur = self.conn.cursor()
        dep_id = _gen_id("dep")
        cur.execute(
            "INSERT INTO dependencies (id, from_term, to_term, relation_type) VALUES (?, ?, ?, ?)",
            (dep_id, from_term, to_term, relation_type.value),
        )
        self.conn.commit()
        return dep_id

    def get_dependencies(self, term_id: str) -> list[dict]:
        """term_id が from_term となっている依存関係を返す。"""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, from_term, to_term, relation_type FROM dependencies WHERE from_term=?",
            (term_id,),
        )
        return [dict(r) for r in cur.fetchall()]

    # ─── DRIFT DETECTION ────────────────────────────────────

    def detect_drift(self, threshold: float = 0.3) -> list[DriftedTerm]:
        """
        semantic_gravity が threshold を下回る Term 一覧を返す。
        Semantic Gravity Model との連動ポイント。
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT m.term_id, m.meaning_id, m.semantic_gravity, m.status
            FROM meanings m
            INNER JOIN (
                SELECT term_id, MAX(version) AS max_ver
                FROM meanings
                GROUP BY term_id
            ) latest ON m.term_id = latest.term_id AND m.version = latest.max_ver
            WHERE m.semantic_gravity < ?
            ORDER BY m.semantic_gravity ASC
            """,
            (threshold,),
        )
        return [
            DriftedTerm(
                term_id=r["term_id"],
                meaning_id=r["meaning_id"],
                semantic_gravity=r["semantic_gravity"],
                status=r["status"],
            )
            for r in cur.fetchall()
        ]

    # ─── UNKNOWN 吸収 ───────────────────────────────────────

    def absorb_unknown(self, term_id: str, definition: str) -> str:
        """
        Unknown領域からの暫定登録。origin=unknown で登録し
        stability_score=0.0 / semantic_gravity=0.1 で開始する。
        Returns: meaning_id
        """
        return self.add_meaning(
            term_id=term_id,
            definition=definition,
            stability_score=0.0,
            semantic_gravity=0.1,
            origin=TermOrigin.UNKNOWN,
        )

    # ─── STATS ──────────────────────────────────────────────

    def stats(self) -> dict:
        """辞書の統計情報を返す。"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM terms")
        term_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM meanings WHERE status='active'")
        active_meanings = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM dependencies")
        dep_count = cur.fetchone()[0]

        drifted = self.detect_drift()

        return {
            "total_terms": term_count,
            "active_meanings": active_meanings,
            "total_dependencies": dep_count,
            "drifted_terms": len(drifted),
        }
