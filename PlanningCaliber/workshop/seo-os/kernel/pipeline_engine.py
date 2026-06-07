import json, os, uuid, sqlite3
from datetime import datetime
from kernel.logger import info, warn, error
from caliber.caliber_manager import request_capability
from gate.ai_gate import AIGate
from gate.policy_engine import PolicyEngine

DB_PATH      = os.path.join(os.path.dirname(__file__),
                             "../data/jobs.db")
PIPELINE_DIR = os.path.join(os.path.dirname(__file__),
                             "../pipelines")

class PipelineEngine:
    """
    Pipeline JSONを読み込み、Step単位で実行する。
    Schedulerの後継。Phase3からここが主体。

    Step種別:
      capability  → Caliber経由でWorker実行
      gate        → AI Gate品質検査
      policy      → Policy判定
      human_gate  → 博士承認待ちに変更して停止
    """

    def run(self, job: dict) -> dict:
        job_id   = job["id"]
        pipeline = job.get("pipeline", "")
        steps    = self._load(pipeline)
        total    = len(steps)

        info(f"[Pipeline] 開始: {job_id} / {pipeline} ({total}steps)")
        self._update_job(job_id, "running")

        ph_id    = self._init_history(job_id, pipeline, total)
        ai_gate  = AIGate()
        policy   = PolicyEngine()
        gate_result = {}

        for i, step in enumerate(steps, 1):
            kind = step.get("type", "capability")
            info(f"[Pipeline] Step {i}/{total}: type={kind}")
            self._update_progress(ph_id, i)

            if kind == "gate":
                gate_result = ai_gate.check(
                    job, job.get("policy",""))
                if not gate_result["passed"] and \
                   step.get("on_fail") == "reject":
                    return self._fail(
                        job_id, ph_id,
                        f"AI Gate不合格: {gate_result}")
                continue

            if kind == "policy":
                verdict = policy.evaluate(job, gate_result)
                v = verdict["verdict"]

                if v == "reject":
                    return self._fail(
                        job_id, ph_id, verdict["reason"])

                if v == "human_gate":
                    self._update_job(job_id, "approved",
                                     note="Policy: 博士承認待ち")
                    self._update_history(
                        ph_id, "paused", i)
                    info(f"[Pipeline] human_gate: {job_id}")
                    return {"success": False,
                            "reason": "human_gate",
                            "verdict": verdict}

                if v == "auto_deploy":
                    info(f"[Pipeline] auto_deploy: {job_id}")
                continue

            if kind == "capability":
                cap       = step.get("capability","")
                selection = step.get("selection","priority")
                worker    = request_capability(cap, tag="prod",
                                                strategy=selection)

                if not worker:
                    if step.get("required", True):
                        return self._fail(
                            job_id, ph_id,
                            f"Capability不足: {cap}")
                    warn(f"[Pipeline] {cap} スキップ")
                    continue

                try:
                    result = worker.execute(job)
                    if not result.get("success"):
                        raise Exception(
                            result.get("error","Worker失敗"))
                    self._save_artifact(
                        job_id, cap,
                        result.get("result_url",""))
                except Exception as e:
                    error(f"[Pipeline] Step{i}失敗: {e}")
                    if step.get("required", True):
                        self._rollback(job_id, i, steps)
                        return self._fail(
                            job_id, ph_id, str(e))
                    warn(f"[Pipeline] Step{i} スキップ")
                continue

        self._done(job_id, ph_id, total)
        return {"success": True,
                "job_id": job_id,
                "pipeline": pipeline}

    def _load(self, name: str) -> list:
        path = os.path.join(PIPELINE_DIR, f"{name}.json")
        if not name or not os.path.exists(path):
            warn(f"[Pipeline] {name} 未定義 → default使用")
            return [{"order":1,"type":"capability",
                     "capability":"upload_html",
                     "required":False}]
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return sorted(data.get("steps",[]),
                      key=lambda s: s.get("order",0))

    def _init_history(self, job_id, pipeline, total) -> str:
        ph_id = str(uuid.uuid4())
        conn  = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO pipeline_history
            (id,job_id,pipeline,current_step,
             total_steps,status,started_at)
            VALUES (?,?,?,0,?,'running',?)
        """, (ph_id, job_id, pipeline,
              total, datetime.now().isoformat()))
        conn.commit(); conn.close()
        return ph_id

    def _update_progress(self, ph_id, step):
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE pipeline_history SET current_step=? WHERE id=?",
            (step, ph_id))
        conn.commit(); conn.close()

    def _update_history(self, ph_id, status, step):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            UPDATE pipeline_history
            SET status=?, current_step=?, finished_at=?
            WHERE id=?
        """, (status, step, datetime.now().isoformat(), ph_id))
        conn.commit(); conn.close()

    def _update_job(self, job_id, status, note=""):
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE jobs SET status=?, note=? WHERE id=?",
            (status, note, job_id))
        conn.commit(); conn.close()

    def _save_artifact(self, job_id, capability, url):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO artifacts
            (id,job_id,type,path,created_at)
            VALUES (?,?,?,?,?)
        """, (str(uuid.uuid4()), job_id,
              capability, url,
              datetime.now().isoformat()))
        conn.commit(); conn.close()

    def _rollback(self, job_id, failed_step, steps):
        warn(f"[Pipeline] Rollback: {job_id} step={failed_step}")
        self._update_job(job_id, "rollback")
        for step in reversed(steps[:failed_step-1]):
            cap    = step.get("capability","")
            worker = request_capability(cap)
            if worker and hasattr(worker, "rollback"):
                worker.rollback(job_id)

    def _fail(self, job_id, ph_id, reason) -> dict:
        self._update_job(job_id, "failed", note=reason)
        self._update_history(ph_id, "failed", 0)
        error(f"[Pipeline] 失敗: {job_id} / {reason}")
        return {"success": False, "reason": reason}

    def _done(self, job_id, ph_id, total):
        now = datetime.now().isoformat()
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE jobs SET status='done', deployed_at=? WHERE id=?",
            (now, job_id))
        conn.execute("""
            UPDATE pipeline_history
            SET status='done', finished_at=?, current_step=?
            WHERE id=?
        """, (now, total, ph_id))
        conn.commit(); conn.close()
        info(f"[Pipeline] 完了: {job_id}")
