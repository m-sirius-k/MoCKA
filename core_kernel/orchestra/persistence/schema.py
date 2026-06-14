"""
MoCKA Core Kernel — orchestra.persistence.schema

SQLite永続化層のテーブル定義。
"""

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    session_id TEXT,
    event_type TEXT,
    timestamp REAL,
    payload TEXT
);

CREATE TABLE IF NOT EXISTS executions (
    execution_id TEXT PRIMARY KEY,
    session_id TEXT,
    node_id TEXT,
    timestamp REAL,
    context TEXT,
    result TEXT
);

CREATE TABLE IF NOT EXISTS outputs (
    output_id TEXT PRIMARY KEY,
    session_id TEXT,
    timestamp REAL,
    data TEXT
);
"""
