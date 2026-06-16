# personal_lexicon.py
# Personal Lexicon v1 — 人間側の意味安定辞書
#
# 設計思想:
#   「正しさ」ではなく「納得」を保存する
#   「最適化」ではなく「思考の固定」を目的とする
#   AIではなく人間の意味空間に属する
#
# 制約:
#   version管理なし（上書き型・常に最新理解のみ）
#   外部依存なし（sqlite3標準のみ）
#   PHI-OS / MoCKA との連携コードなし

import sqlite3
import datetime
from typing import Optional


DB_DEFAULT = "personal_lexicon.db"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class PersonalLexicon:
    """
    人間の意味空間に属する軽量用語集。
    意味は1つに固定（多義禁止）。バージョン管理なし。
    """

    def __init__(self, db_path: str = DB_DEFAULT):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS personal_terms (
            term       TEXT PRIMARY KEY,
            meaning    TEXT NOT NULL,
            note       TEXT,
            category   TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ─── 登録（上書き型） ───────────────────────────────────────

    def add_term(
        self,
        term: str,
        meaning: str,
        note: str = "",
        category: str = "",
    ) -> None:
        """
        用語を登録する。既存の場合は上書き（意味を更新）。
        updated_at を必ず更新し、初回登録時は created_at も同値でセット。
        """
        t = _now()
        self.conn.execute(
            """
            INSERT INTO personal_terms (term, meaning, note, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(term) DO UPDATE SET
                meaning    = excluded.meaning,
                note       = excluded.note,
                category   = excluded.category,
                updated_at = excluded.updated_at
            """,
            (term, meaning, note, category, t, t),
        )
        self.conn.commit()

    # ─── 取得 ───────────────────────────────────────────────────

    def get(self, term: str) -> Optional[dict]:
        """
        単一用語を取得する。存在しない場合は None。
        """
        row = self.conn.execute(
            "SELECT * FROM personal_terms WHERE term = ?", (term,)
        ).fetchone()
        return dict(row) if row else None

    # ─── 全一覧 ─────────────────────────────────────────────────

    def list_all(self, category: str = "") -> list[dict]:
        """
        全用語を term の昇順で返す。
        category を指定するとそのカテゴリのみ絞り込む。
        """
        if category:
            rows = self.conn.execute(
                "SELECT * FROM personal_terms WHERE category = ? ORDER BY term",
                (category,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM personal_terms ORDER BY term"
            ).fetchall()
        return [dict(r) for r in rows]

    # ─── 削除 ───────────────────────────────────────────────────

    def delete_term(self, term: str) -> bool:
        """
        用語を削除する。
        Returns: True = 削除成功 / False = 存在しなかった
        """
        cur = self.conn.execute(
            "DELETE FROM personal_terms WHERE term = ?", (term,)
        )
        self.conn.commit()
        return cur.rowcount > 0

    # ─── 表示ヘルパー ───────────────────────────────────────────

    def show(self, term: str) -> None:
        """用語を人間が読みやすい形式で標準出力する。"""
        entry = self.get(term)
        if entry is None:
            print(f"[not found] {term}")
            return
        print(f"【{entry['term']}】")
        print(f"  意味     : {entry['meaning']}")
        if entry["note"]:
            print(f"  補足     : {entry['note']}")
        if entry["category"]:
            print(f"  カテゴリ : {entry['category']}")
        print(f"  更新日   : {entry['updated_at']}")

    def show_all(self, category: str = "") -> None:
        """全用語を人間が読みやすい形式で標準出力する。"""
        entries = self.list_all(category)
        if not entries:
            print("（登録なし）")
            return
        for e in entries:
            cat = f"  [{e['category']}]" if e["category"] else ""
            print(f"  {e['term']}{cat} : {e['meaning']}")


# ─── CLI エントリポイント ────────────────────────────────────────

if __name__ == "__main__":
    import sys

    db = PersonalLexicon()

    args = sys.argv[1:]

    if not args:
        print("使い方:")
        print("  python personal_lexicon.py add <用語> <意味> [補足] [カテゴリ]")
        print("  python personal_lexicon.py get <用語>")
        print("  python personal_lexicon.py list [カテゴリ]")
        print("  python personal_lexicon.py delete <用語>")
        sys.exit(0)

    cmd = args[0]

    if cmd == "add":
        if len(args) < 3:
            print("エラー: add <用語> <意味> [補足] [カテゴリ]")
            sys.exit(1)
        term     = args[1]
        meaning  = args[2]
        note     = args[3] if len(args) > 3 else ""
        category = args[4] if len(args) > 4 else ""
        db.add_term(term, meaning, note, category)
        print(f"登録: 【{term}】= {meaning}")

    elif cmd == "get":
        if len(args) < 2:
            print("エラー: get <用語>")
            sys.exit(1)
        db.show(args[1])

    elif cmd == "list":
        category = args[1] if len(args) > 1 else ""
        db.show_all(category)

    elif cmd == "delete":
        if len(args) < 2:
            print("エラー: delete <用語>")
            sys.exit(1)
        ok = db.delete_term(args[1])
        print(f"削除: 【{args[1]}】{'完了' if ok else '（存在しなかった）'}")

    else:
        print(f"不明なコマンド: {cmd}")
        sys.exit(1)

    db.close()
