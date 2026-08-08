"""MoCKA DB Helper Interface Part1

SQLite read interface and common utilities.
"""

import csv
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


try:
    from phi_os.event.event_gate import process_event
except ImportError:
    process_event = None


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "mocka_events.db"
CSV_PATH = DATA_DIR / "events.csv"

CSV_WRITE_ENABLED = False


def _get_connection(
    db_path: Union[str, Path] = DB_PATH
) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    data = dict(row)

    if "payload" in data and isinstance(data["payload"], str):
        try:
            data["payload"] = json.loads(data["payload"])
        except (json.JSONDecodeError, TypeError):
            pass

    return data


def _read_events_csv(
    csv_path: Union[str, Path] = CSV_PATH
) -> List[Dict[str, Any]]:
    path = Path(csv_path)

    if not path.exists():
        return []

    events = []

    try:
        with open(
            path,
            mode="r",
            encoding="utf-8-sig",
            newline=""
        ) as f:
            reader = csv.DictReader(f)

            for row in reader:
                events.append(dict(row))

    except Exception:
        return []

    return events


def _count_events_csv(
    csv_path: Union[str, Path] = CSV_PATH
) -> int:
    return len(_read_events_csv(csv_path))


def read_events(
    limit: Optional[int] = None,
    offset: int = 0,
    db_path: Union[str, Path] = DB_PATH,
) -> List[Dict[str, Any]]:
    """
    SQLite蜆ｪ蜈医〒繧､繝吶Φ繝亥叙蠕励・
    DB荳榊ｭ伜惠譎ゅ・縺ｿCSV fallback縲・
    """

    path = Path(db_path)

    if not path.exists():
        events = _read_events_csv(CSV_PATH)
        return (
            events[offset:offset + limit]
            if limit is not None
            else events[offset:]
        )

    try:
        with _get_connection(path) as conn:

            query = """
            SELECT *
            FROM events
            ORDER BY rowid ASC
            """

            params = []

            if limit is not None:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])

            rows = conn.execute(
                query,
                params
            ).fetchall()

            return [
                _dict_from_row(row)
                for row in rows
            ]

    except sqlite3.Error:
        events = _read_events_csv(CSV_PATH)

        return (
            events[offset:offset + limit]
            if limit is not None
            else events[offset:]
        )
def write_event(
    row: dict,
    channel: str = None
) -> bool:
    """
    Event Gate邨檎罰縺ｮ蜚ｯ荳縺ｮ譖ｸ縺崎ｾｼ縺ｿ蜈･蜿｣縲・
    """

    if process_event is None:
        raise RuntimeError(
            "event_gate.process_event unavailable"
        )

    result = process_event(
        row,
        event_source=channel or "db_helper"
    )

    return (
        isinstance(result, dict)
        and result.get("status") == "ok"
    )


def count_events(
    db_path: Union[str, Path] = DB_PATH
) -> int:
    """
    繧､繝吶Φ繝育ｷ乗焚蜿門ｾ励・
    """

    path = Path(db_path)

    if not path.exists():
        return _count_events_csv(CSV_PATH)

    try:
        with _get_connection(path) as conn:

            row = conn.execute(
                "SELECT COUNT(*) FROM events"
            ).fetchone()

            return row[0] if row else 0

    except sqlite3.Error:
        return _count_events_csv(CSV_PATH)


def get_event(
    event_id: Union[str, int],
    db_path: Union[str, Path] = DB_PATH
) -> Optional[Dict[str, Any]]:
    """
    event_id謖・ｮ壼叙蠕励・
    """

    path = Path(db_path)

    if not path.exists():
        for event in _read_events_csv(CSV_PATH):
            if str(event.get("event_id")) == str(event_id):
                return event
        return None

    try:
        with _get_connection(path) as conn:

            row = conn.execute(
                """
                SELECT *
                FROM events
                WHERE event_id = ?
                """,
                (event_id,)
            ).fetchone()

            if row:
                return _dict_from_row(row)

    except sqlite3.Error:
        pass

    return None


def search_events(
    keyword: str,
    limit: int = 50,
    db_path: Union[str, Path] = DB_PATH
) -> List[Dict[str, Any]]:
    """
    title / short_summary / free_note讀懃ｴ｢縲・
    """

    path = Path(db_path)

    if not path.exists():
        events = _read_events_csv(CSV_PATH)

        result = []

        for event in events:
            text = " ".join(
                str(event.get(k, ""))
                for k in [
                    "title",
                    "short_summary",
                    "free_note"
                ]
            )

            if keyword.lower() in text.lower():
                result.append(event)

        return result[:limit]


    try:
        with _get_connection(path) as conn:

            rows = conn.execute(
                """
                SELECT *
                FROM events
                WHERE title LIKE ?
                   OR short_summary LIKE ?
                   OR free_note LIKE ?
                ORDER BY rowid DESC
                LIMIT ?
                """,
                (
                    f"%{keyword}%",
                    f"%{keyword}%",
                    f"%{keyword}%",
                    limit
                )
            ).fetchall()

            return [
                _dict_from_row(row)
                for row in rows
            ]

    except sqlite3.Error:
        return []
def get_next_event_id() -> str:
    """
    次のevent_id生成。
    MoCKA蠖｢蠑・
    EYYYYMMDD + time + random
    """

    from datetime import datetime, timezone
    import secrets
    import time

    now = datetime.now(timezone.utc)

    date_part = now.strftime("%Y%m%d")
    time_part = (
        time.time_ns() // 1000
        % 1000000000
    )

    return (
        f"E{date_part}_"
        f"{time_part:09d}"
        f"{secrets.token_hex(2)}"
    )


def main():
    print("--- MoCKA db_helper diagnostics ---")
    print(f"DB: {DB_PATH}")
    print(f"CSV: {CSV_PATH}")
    print(
        f"Event Gate available: "
        f"{process_event is not None}"
    )

    print(
        f"Event Count: "
        f"{count_events()}"
    )


if __name__ == "__main__":
    main()
