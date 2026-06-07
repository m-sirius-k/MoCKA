import sqlite3, os, hashlib, uuid
from datetime import datetime
from kernel.logger import info

DB_PATH = os.path.join(os.path.dirname(__file__),
                       "../data/jobs.db")
ARTIFACT_DIR = os.path.join(os.path.dirname(__file__),
                             "../data/artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def save(job_id: str, artifact_type: str,
         content: str, filename: str) -> dict:
    path = os.path.join(ARTIFACT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    h = hashlib.sha256(content.encode()).hexdigest()
    aid = str(uuid.uuid4())

    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO artifacts
        (id,job_id,type,path,hash,created_at)
        VALUES (?,?,?,?,?,?)
    """, (aid, job_id, artifact_type,
          path, h, datetime.now().isoformat()))
    conn.commit(); conn.close()

    info(f"[Artifact] 保存: {filename} hash={h[:8]}")
    return {"id": aid, "path": path, "hash": h}

def get(job_id: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM artifacts WHERE job_id=?",
        (job_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def verify(artifact_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM artifacts WHERE id=?",
        (artifact_id,)).fetchone()
    conn.close()
    if not row or not os.path.exists(row["path"]):
        return False
    with open(row["path"], encoding="utf-8") as f:
        h = hashlib.sha256(f.read().encode()).hexdigest()
    return h == row["hash"]
