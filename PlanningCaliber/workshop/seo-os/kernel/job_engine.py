import sqlite3, uuid, os
from datetime import datetime

from kernel.logger import info, error

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/jobs.db")
MOCKA_DB = "C:/Users/sirok/MoCKA/data/mocka_events.db"

STATUS = [
    "pending",   # 博士起草・承認待ち
    "review",    # AI校正中
    "approved",  # 承認済み
    "queued",    # Queue投入済み
    "running",   # 実行中
    "done",      # 完了
    "failed",    # 失敗
    "rejected",  # 却下
    "rollback"   # 巻き戻し中
]

def _jid():
    return f"J{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:6].upper()}"

_memory_conn = None

def _con():
    global _memory_conn
    if DB_PATH == ":memory:":
        if _memory_conn is None:
            _memory_conn = sqlite3.connect(DB_PATH)
        conn = _memory_conn
    else:
        conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_job(title, job_type, content="", target="",
               priority=3, pipeline="", ai_draft=0, note=""):
    jid = _jid()
    with _con() as conn:
        conn.execute("""
            INSERT INTO jobs
            (id,title,type,status,priority,pipeline,
             content,target,ai_draft,created_at,note)
            VALUES (?,?,?,'pending',?,?,?,?,?,?,?)
        """, (jid,title,job_type,priority,pipeline,
              content,target,ai_draft,
              datetime.now().isoformat(),note))
        _audit(conn, jid, "created", "system", title)
    info(f"[JOB] 作成: {jid} / {title}")
    _mocka("JOB_CREATED", jid, title)
    return jid

def approve_job(job_id, actor="きむら博士"):
    with _con() as conn:
        conn.execute("""
            UPDATE jobs SET status='approved', approved_at=?
            WHERE id=?
        """, (datetime.now().isoformat(), job_id))
        _audit(conn, job_id, "approved", actor, "")
    info(f"[JOB] 承認: {job_id} by {actor}")
    _mocka("JOB_APPROVED", job_id, f"actor:{actor}")

def reject_job(job_id, reason="", actor="きむら博士"):
    with _con() as conn:
        conn.execute("""
            UPDATE jobs SET status='rejected', note=?
            WHERE id=?
        """, (reason, job_id))
        _audit(conn, job_id, "rejected", actor, reason)
    info(f"[JOB] 却下: {job_id} / {reason}")
    _mocka("JOB_REJECTED", job_id, reason)

def get_jobs(status=None):
    with _con() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM jobs WHERE status=? "
                "ORDER BY priority,created_at", (status,)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM jobs "
                "ORDER BY priority,created_at").fetchall()
    return [dict(r) for r in rows]

def get_job(job_id):
    with _con() as conn:
        row = conn.execute(
            "SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    return dict(row) if row else None

def _audit(conn, job_id, action, actor, detail):
    conn.execute("""
        INSERT INTO audit_log (id,job_id,action,actor,detail,timestamp)
        VALUES (?,?,?,?,?,?)
    """, (str(uuid.uuid4()),job_id,action,actor,
          detail,datetime.now().isoformat()))

def _mocka(event_type, job_id, detail):
    try:
        conn = sqlite3.connect(MOCKA_DB)
        eid = f"ESEOS{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        conn.execute("""
            INSERT INTO events
            (event_id,who_actor,what_type,where_component,
             why_purpose,how_trigger,when_ts)
            VALUES (?,?,?,?,?,?,?)
        """, (eid,"SEO-OS",event_type,"seo_os",
              detail,job_id,datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception:
        pass
