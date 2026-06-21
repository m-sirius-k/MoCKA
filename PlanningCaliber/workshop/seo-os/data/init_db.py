import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

def init():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS jobs (
        id          TEXT PRIMARY KEY,
        title       TEXT NOT NULL,
        type        TEXT NOT NULL,
        status      TEXT DEFAULT 'pending',
        priority    INTEGER DEFAULT 3,
        pipeline    TEXT,
        content     TEXT,
        target      TEXT,
        policy      TEXT,
        author      TEXT DEFAULT 'きむら博士',
        ai_draft    INTEGER DEFAULT 0,
        retry_count INTEGER DEFAULT 0,
        created_at  TEXT,
        approved_at TEXT,
        deployed_at TEXT,
        result_url  TEXT,
        note        TEXT
    );
    CREATE TABLE IF NOT EXISTS artifacts (
        id         TEXT PRIMARY KEY,
        job_id     TEXT,
        type       TEXT,
        path       TEXT,
        hash       TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS queue (
        id          TEXT PRIMARY KEY,
        job_id      TEXT NOT NULL,
        worker      TEXT NOT NULL,
        capability  TEXT NOT NULL,
        status      TEXT DEFAULT 'queued',
        priority    INTEGER DEFAULT 3,
        retry_count INTEGER DEFAULT 0,
        max_retry   INTEGER DEFAULT 3,
        queued_at   TEXT,
        started_at  TEXT,
        finished_at TEXT,
        result      TEXT,
        error       TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs(id)
    );
    CREATE TABLE IF NOT EXISTS worker_history (
        id           TEXT PRIMARY KEY,
        job_id       TEXT NOT NULL,
        worker       TEXT NOT NULL,
        capability   TEXT NOT NULL,
        status       TEXT DEFAULT 'running',
        started_at   TEXT,
        finished_at  TEXT,
        duration_ms  INTEGER,
        artifact     TEXT,
        error        TEXT,
        retry_count  INTEGER DEFAULT 0,
        FOREIGN KEY (job_id) REFERENCES jobs(id)
    );
    CREATE TABLE IF NOT EXISTS pipeline_history (
        id           TEXT PRIMARY KEY,
        job_id       TEXT NOT NULL,
        pipeline     TEXT NOT NULL,
        current_step INTEGER DEFAULT 0,
        total_steps  INTEGER DEFAULT 0,
        status       TEXT DEFAULT 'running',
        started_at   TEXT,
        finished_at  TEXT
    );
    CREATE TABLE IF NOT EXISTS worker_registry (
        name        TEXT PRIMARY KEY,
        state       TEXT DEFAULT 'ready',
        updated_at  TEXT
    );
    CREATE TABLE IF NOT EXISTS worker_metrics (
        worker_name          TEXT PRIMARY KEY,
        success_count        INTEGER DEFAULT 0,
        failure_count        INTEGER DEFAULT 0,
        avg_duration_ms      REAL    DEFAULT 0.0,
        last_success         TEXT,
        last_failure         TEXT,
        consecutive_failures INTEGER DEFAULT 0,
        updated_at           TEXT
    );
    CREATE TABLE IF NOT EXISTS decision_ledger (
        id                TEXT PRIMARY KEY,
        timestamp         TEXT NOT NULL,
        pipeline          TEXT,
        capability        TEXT NOT NULL,
        strategy          TEXT NOT NULL,
        selected_worker   TEXT NOT NULL,
        candidate_workers TEXT,
        selection_reason  TEXT,
        job_id            TEXT,
        operator          TEXT DEFAULT 'system',
        outcome           TEXT
    );
    CREATE TABLE IF NOT EXISTS decision_policy (
        id          TEXT PRIMARY KEY,
        name        TEXT UNIQUE NOT NULL,
        capability  TEXT,
        rule_type   TEXT NOT NULL,
        rule_value  TEXT NOT NULL,
        enabled     INTEGER DEFAULT 1,
        created_at  TEXT,
        note        TEXT
    );
    CREATE TABLE IF NOT EXISTS audit_log (
        id        TEXT PRIMARY KEY,
        job_id    TEXT,
        action    TEXT,
        actor     TEXT,
        detail    TEXT,
        timestamp TEXT
    );
    CREATE TABLE IF NOT EXISTS publish_queue (
        id           TEXT PRIMARY KEY,
        content_id   TEXT NOT NULL,
        platform     TEXT NOT NULL,
        payload      TEXT,
        status       TEXT DEFAULT 'pending',
        priority     INTEGER DEFAULT 3,
        source       TEXT DEFAULT 'pr_os',
        created_at   TEXT,
        processed_at TEXT,
        result_url   TEXT,
        error        TEXT
    );
    CREATE TABLE IF NOT EXISTS platform_status (
        id           TEXT PRIMARY KEY,
        content_id   TEXT NOT NULL,
        platform     TEXT NOT NULL,
        status       TEXT DEFAULT 'pending',
        result_url   TEXT,
        error        TEXT,
        updated_at   TEXT
    );
    """)
    conn.commit()

    # 既存DB(jobs.db既存ファイル)にはCREATE TABLE IF NOT EXISTSが効かないため
    # 既存テーブルへのカラム追加はALTER TABLEで個別に対応する
    try:
        conn.execute("ALTER TABLE jobs ADD COLUMN retry_count INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # 既に列が存在する場合

    conn.close()
    print("[OK] jobs.db初期化完了")

if __name__ == "__main__":
    init()
