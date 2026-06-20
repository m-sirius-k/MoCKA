#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
interface/schema_audit.py -- Phase5-1.5 起動時Schema Audit

events._source列の実DBスキーマ（CREATE TABLE文）が、Gate Policy
(interface/gate_policy.ALLOWED_SOURCE_VALUES)と完全一致しているかを
起動時に検証する。

設計案（2案を提示。現状はWARN方式を既定値として実装）:
  - WARN方式（既定）: 不一致を検出してもプロセスは継続するが、
    health_check.py / COMMAND CENTER上に警告を出す。
    起動失敗が業務（記録継続）を止めるリスクより、ズレの早期発見を優先する場合に適する。
  - FAIL-FAST方式（環境変数 MOCKA_SCHEMA_AUDIT_STRICT=1で有効化）:
    不一致時にRuntimeErrorで起動を停止する。
    「記録制度の一致」を「記録の継続」より優先する場合に適する。
    Gate Policy変更時にMigrationを忘れたまま起動する事故を機械的に防止できる。

呼び出し側（app.py起動シーケンス等）は audit_schema() の戻り値(ok, message)を見て、
MOCKA_SCHEMA_AUDIT_STRICT=1の場合のみ ok=False を起動失敗として扱うこと。
"""

import os
import re
import sqlite3
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "interface"))
from gate_policy import ALLOWED_SOURCE_VALUES, POLICY_VERSION  # noqa: E402

DB_PATH = _REPO_ROOT / "data" / "mocka_events.db"

_CHECK_VALUES_RE = re.compile(r"_source\s+TEXT\s+NOT\s+NULL\s+CHECK\s*\(\s*_source\s+IN\s*\(([^)]*)\)\s*\)")


def _parse_check_values(create_sql: str) -> set:
    m = _CHECK_VALUES_RE.search(create_sql)
    if not m:
        return set()
    raw = m.group(1)
    return {v.strip().strip("'") for v in raw.split(",") if v.strip()}


def audit_schema(db_path: Path = DB_PATH) -> tuple:
    """
    events._source列のスキーマがGate Policyと一致するかを検証する。
    戻り値: (ok: bool, message: str)
    """
    if not db_path.exists():
        return False, f"DB not found: {db_path}"

    try:
        conn = sqlite3.connect(str(db_path))
        row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='events'"
        ).fetchone()
    except Exception as e:
        return False, f"sqlite_master読み取りエラー: {e}"
    finally:
        conn.close()

    if not row or not row[0]:
        return False, "eventsテーブルが見つからない"

    create_sql = row[0]

    if "_source TEXT NOT NULL CHECK" not in create_sql.replace("\n", " "):
        return False, (
            "_source列がNOT NULL CHECK制約化されていない（Phase5-1.5未適用）。"
            "scripts/migrate_source_check.pyを実行すること。"
        )

    db_values = _parse_check_values(create_sql)
    if not db_values:
        return False, "_source列のCHECK制約値を解析できなかった"

    if db_values != set(ALLOWED_SOURCE_VALUES):
        missing_in_db = set(ALLOWED_SOURCE_VALUES) - db_values
        extra_in_db = db_values - set(ALLOWED_SOURCE_VALUES)
        detail = []
        if missing_in_db:
            detail.append(f"DB側に無い値(Gate Policyのみ): {sorted(missing_in_db)}")
        if extra_in_db:
            detail.append(f"DB側のみに存在する値: {sorted(extra_in_db)}")
        return False, (
            f"_source CHECK制約とGate Policy(v{POLICY_VERSION})が不一致。 "
            + " / ".join(detail)
        )

    return True, f"_source CHECK制約はGate Policy v{POLICY_VERSION}と完全一致"


def enforce(strict: bool = None) -> None:
    """
    app.py等の起動シーケンスから呼び出す。
    strict未指定時は環境変数 MOCKA_SCHEMA_AUDIT_STRICT で判定する。
    """
    if strict is None:
        strict = os.environ.get("MOCKA_SCHEMA_AUDIT_STRICT", "0") == "1"

    ok, message = audit_schema()
    if ok:
        print(f"[schema_audit] OK: {message}")
        return

    print(f"[schema_audit] WARNING: {message}")
    if strict:
        raise RuntimeError(f"[schema_audit] Schema Audit失敗（MOCKA_SCHEMA_AUDIT_STRICT=1）: {message}")


if __name__ == "__main__":
    ok, message = audit_schema()
    print(f"{'OK' if ok else 'NG'}: {message}")
    sys.exit(0 if ok else 1)
