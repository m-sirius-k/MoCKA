import sqlite3, uuid, os
from datetime import datetime
from kernel.logger import info

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/jobs.db")

def enqueue(job_id: str, worker: str,
            capability: str, priority: int = 3) -> str:
    qid = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO queue
        (id,job_id,worker,capability,status,priority,queued_at)
        VALUES (?,?,?,?,?,?,?)
    """, (qid, job_id, worker, capability,
          "queued", priority, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    info(f"[Queue] 追加: {qid} / {capability}")
    return qid

def dequeue():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT * FROM queue
        WHERE status='queued'
        ORDER BY priority, queued_at
        LIMIT 1
    """).fetchone()
    if row:
        conn.execute(
            "UPDATE queue SET status='running', started_at=? WHERE id=?",
            (datetime.now().isoformat(), row["id"]))
        conn.commit()
    conn.close()
    return dict(row) if row else None

def finish(queue_id: str, success: bool, result: str = ""):
    status = "done" if success else "failed"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        UPDATE queue
        SET status=?, finished_at=?, result=?
        WHERE id=?
    """, (status, datetime.now().isoformat(), result, queue_id))
    conn.commit()
    conn.close()
    info(f"[Queue] 完了: {queue_id} / {status}")

def get_queue_status() -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT * FROM queue
        ORDER BY priority, queued_at
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
