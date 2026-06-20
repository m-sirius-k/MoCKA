# -*- coding: utf-8 -*-
# MoCKA Index Writer v1.0
# Role: 5W1H Index — AI活動の一次証跡。Writeより前に来る「文明の原本」。
# ref: E20260610_10454
import sqlite3
import sys
import time
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "interface"))
from event_buffer import get_buffer  # Phase5-1: Gate Enforcement(db直書き禁止)

MOCKA_INDEX_VERSION = '1.0'


@dataclass
class MoCKAIndex:
    who: str          # 'gpt' / 'claude' / 'gemini' / 'human' etc.
    what: str         # 行ったこと
    why: str          # 目的・理由
    where: str        # フェーズ・コンテキスト
    how: str          # 手段・方法
    when: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: str = ''
    session_id: str = ''


class IndexWriter:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def write(self, index: MoCKAIndex) -> str:
        short_summary = f'[INDEX] {index.who}: {index.what}'[:200]
        tags_str = f'INDEX,{index.who}' + (f',{index.tags}' if index.tags else '')
        free_note = (
            f'{tags_str}\n'
            f'Who:{index.who}\nWhat:{index.what}\nWhy:{index.why}\n'
            f'Where:{index.where}\nHow:{index.how}'
        )

        # Phase5-1: 生SQL INSERT INTO events禁止 → Local Buffer経由でGateへ統一
        d = datetime.now(timezone.utc).strftime('%Y%m%d')
        micros_of_day = time.time_ns() // 1000 % 1_000_000_000
        event_id = f"E{d}_{micros_of_day:09d}{secrets.token_hex(2)}"

        get_buffer().push({
            "event_id":        event_id,
            "title":           f'INDEX: {index.who}',
            "short_summary":   short_summary,
            "when":            index.when,
            "who_actor":       index.who,
            "ai_actor":        'index_writer',
            "what_type":       'index',
            "free_note":       free_note,
            "where_component": index.where,
            "why_purpose":     index.why,
            "how_trigger":     index.how,
            "lifecycle_phase": 'in_operation',
            "session_id":      index.session_id,
        })
        return event_id

    def search(self, keyword='', who='', limit=10) -> list:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        query = "SELECT event_id, when_ts, short_summary, free_note FROM events WHERE free_note LIKE '%INDEX%'"
        params = []
        if keyword:
            query += " AND short_summary LIKE ?"
            params.append(f'%{keyword}%')
        if who:
            query += " AND who_actor = ?"
            params.append(who)
        query += " ORDER BY when_ts DESC LIMIT ?"
        params.append(limit)
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return rows

    def to_relay(self, index: MoCKAIndex) -> dict:
        return {
            'who': index.who,
            'what': index.what,
            'why': index.why,
            'where': index.where,
            'how': index.how,
            'when': index.when,
            'tags': index.tags,
            'session_id': index.session_id,
        }

    def to_markdown(self, index: MoCKAIndex) -> str:
        return (
            "## MoCKA Index\n"
            "| Who | What | Why | Where | How | When |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            f"| {index.who} | {index.what} | {index.why} | {index.where} | {index.how} | {index.when} |"
        )


if __name__ == '__main__':
    import argparse
    from pathlib import Path

    DB_PATH = Path(__file__).parent.parent / "data" / "mocka_events.db"

    parser = argparse.ArgumentParser(description='MoCKA Index Writer')
    parser.add_argument('--who')
    parser.add_argument('--what')
    parser.add_argument('--why')
    parser.add_argument('--where')
    parser.add_argument('--how')
    parser.add_argument('--tags', default='')
    parser.add_argument('--session-id', default='')
    parser.add_argument('--search', action='store_true')
    parser.add_argument('--keyword', default='')
    parser.add_argument('--limit', type=int, default=10)
    args = parser.parse_args()

    writer = IndexWriter(str(DB_PATH))

    if args.search:
        for row in writer.search(keyword=args.keyword, who=args.who or '', limit=args.limit):
            print(row)
    else:
        index = MoCKAIndex(
            who=args.who, what=args.what, why=args.why,
            where=args.where, how=args.how,
            tags=args.tags, session_id=args.session_id,
        )
        event_id = writer.write(index)
        print(f'Index登録完了: {event_id}')
