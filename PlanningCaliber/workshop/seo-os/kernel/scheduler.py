import sqlite3, uuid, json, os
from datetime import datetime
from kernel.logger import info, warn, error

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/jobs.db")
PIPELINE_DIR = os.path.join(os.path.dirname(__file__), "../pipelines")

class Scheduler:
    """
    責務を限定する（thin Scheduler）:
    1. Queueから次のJobを取得
    2. Pipelineを読み込む
    3. Capabilityを要求する（Worker名は知らない）
    4. 結果をQueueへ反映
    """

    def run_once(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        job = conn.execute("""
            SELECT * FROM jobs
            WHERE status='approved'
            ORDER BY priority, approved_at
            LIMIT 1
        """).fetchone()

        if not job:
            conn.close()
            return None

        job = dict(job)
        job_id = job["id"]
        pipeline_name = job.get("pipeline", "")

        info(f"[Scheduler] Job取得: {job_id} / {job['title']}")

        conn.execute(
            "UPDATE jobs SET status='queued' WHERE id=?",
            (job_id,))
        conn.commit()

        steps = self._load_pipeline(pipeline_name)
        total = len(steps)

        ph_id = str(uuid.uuid4())
        started = datetime.now().isoformat()
        conn.execute("""
            INSERT INTO pipeline_history
            (id,job_id,pipeline,current_step,total_steps,status,started_at)
            VALUES (?,?,?,?,?,?,?)
        """, (ph_id, job_id, pipeline_name, 0, total, "running", started))
        conn.commit()

        conn.execute(
            "UPDATE jobs SET status='running' WHERE id=?",
            (job_id,))
        conn.commit()
        conn.close()

        self._execute_steps(job, steps, ph_id, total)

    def _load_pipeline(self, name: str) -> list:
        path = os.path.join(PIPELINE_DIR, f"{name}.json")
        if not name or not os.path.exists(path):
            warn(f"[Scheduler] Pipeline未定義: {name} → デフォルト使用")
            return [{"order":1,"capability":"upload_html"}]
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return sorted(data.get("steps", []), key=lambda s: s["order"])

    def _execute_steps(self, job, steps, ph_id, total):
        from caliber.caliber_manager import request_capability
        job_id = job["id"]
        conn = sqlite3.connect(DB_PATH)

        for i, step in enumerate(steps, 1):
            capability = step.get("capability", "")
            info(f"[Scheduler] Step {i}/{total}: {capability}")

            conn.execute("""
                UPDATE pipeline_history
                SET current_step=? WHERE id=?
            """, (i, ph_id))
            conn.commit()

            worker = request_capability(capability)
            if not worker:
                if step.get("required", False):
                    self._fail(conn, job_id, ph_id,
                               f"Capability不足: {capability}")
                    conn.close()
                    return
                warn(f"[Scheduler] {capability} スキップ")
                continue

            try:
                result = worker.execute(job)
                if not result.get("success"):
                    raise Exception(result.get("error", "Worker失敗"))
                info(f"[Scheduler] Step {i} 完了: {result.get('result_url','')}")
            except Exception as e:
                error(f"[Scheduler] Step {i} 失敗: {e}")
                if step.get("required", True):
                    self._fail(conn, job_id, ph_id, str(e))
                    conn.close()
                    return

        now = datetime.now().isoformat()
        conn.execute(
            "UPDATE jobs SET status='done', deployed_at=? WHERE id=?",
            (now, job_id))
        conn.execute("""
            UPDATE pipeline_history
            SET status='done', finished_at=?, current_step=?
            WHERE id=?
        """, (now, total, ph_id))
        conn.commit()
        conn.close()
        info(f"[Scheduler] Job完了: {job_id}")

    def _fail(self, conn, job_id, ph_id, reason):
        now = datetime.now().isoformat()
        conn.execute(
            "UPDATE jobs SET status='failed', note=? WHERE id=?",
            (reason, job_id))
        conn.execute("""
            UPDATE pipeline_history
            SET status='failed', finished_at=? WHERE id=?
        """, (now, ph_id))
        conn.commit()
        error(f"[Scheduler] Job失敗: {job_id} / {reason}")
