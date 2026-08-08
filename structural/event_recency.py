"""
event_recency.py

MoCKA全体でevents.dbの「直近性(recency)」を判定する基準を一元化する
共有モジュール。

背景: events.dbのwhen_ts列には、ISO8601形式(YYYY-MM-DD...)でない
破損値(2026-07-05確認時点で145/14646件、ハッシュ文字列・別形式日付・
YYYYMMDD_HHMMSS形式等)が混入している。ORDER BY when_ts DESCは単純な
文字列比較のため、これらの破損値が文字列として大きいと判定され、
無関係な古いデータが「最新」として誤って扱われる。

この判定基準(何が有効なwhen_tsか)を、gateway/context_builder.pyと
mocka_mcp_server.pyの双方が独立にハードコードしていた状態(Single Source
of Truthの不在)を解消するため、本モジュールに一元化する。

注意: 本モジュールはSQL文そのものは提供しない。呼び出し元ごとに
SELECT列・追加条件・LIMITが異なるため、クエリ構造は各呼び出し元に残し、
「有効なwhen_tsとは何か」という判定基準の値だけをここに集約する。
"""

# ISO8601形式(YYYY-MM-DD...)の先頭一致を要求するSQLite GLOBパターン。
# この定数を変更する場合は、参照している全箇所(grep "VALID_WHEN_TS_GLOB")
# が同時に更新されることを確認すること。
VALID_WHEN_TS_GLOB = "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*"


def valid_when_ts_clause(column: str = "when_ts") -> str:
    """SQLのWHERE句断片を返す(呼び出し側でAND連結して使うこと)。

    例: f"WHERE {other_condition} AND {valid_when_ts_clause()}"
    """
    return f"{column} GLOB '{VALID_WHEN_TS_GLOB}'"
