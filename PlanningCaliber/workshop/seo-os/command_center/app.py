import sys, os, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, jsonify
from kernel.job_engine import (create_job, approve_job,
                                reject_job, get_jobs, get_job)
from data.init_db import init
from caliber.health_checker import run_health_check, get_capabilities
from caliber.caliber_manager import get_worker_stats, list_capabilities as caliber_list_capabilities
from caliber.lifecycle_manager import LifecycleManager
from kernel.pipeline_engine import PipelineEngine
from kernel.artifact_manager import get as get_artifacts

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/jobs.db")

init()
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/jobs")
def api_jobs():
    status = request.args.get("status")
    return jsonify(get_jobs(status))

@app.route("/api/jobs", methods=["POST"])
def api_create():
    d = request.json
    jid = create_job(
        title    = d.get("title",""),
        job_type = d.get("type","blog"),
        content  = d.get("content",""),
        target   = d.get("target",""),
        priority = int(d.get("priority", 3)),
        pipeline = d.get("pipeline",""),
        ai_draft = int(d.get("ai_draft", 0)),
        note     = d.get("note","")
    )
    return jsonify({"ok": True, "id": jid})

@app.route("/api/jobs/<job_id>/approve", methods=["POST"])
def api_approve(job_id):
    approve_job(job_id)
    return jsonify({"ok": True})

@app.route("/api/health")
def api_health():
    return jsonify(run_health_check())

@app.route("/api/capabilities")
def api_capabilities():
    return jsonify(get_capabilities())

@app.route("/api/jobs/<job_id>/reject", methods=["POST"])
def api_reject(job_id):
    reason = (request.json or {}).get("reason", "")
    reject_job(job_id, reason)
    return jsonify({"ok": True})

@app.route("/api/caliber/capabilities")
def api_caliber_caps():
    return jsonify(caliber_list_capabilities())

@app.route("/api/caliber/lifecycle")
def api_lifecycle():
    lm = LifecycleManager()
    return jsonify(lm.all_states())

@app.route("/api/caliber/recover/<worker_name>", methods=["POST"])
def api_recover(worker_name):
    LifecycleManager().recover(worker_name)
    return jsonify({"ok": True})

@app.route("/api/jobs/<job_id>/run", methods=["POST"])
def api_run(job_id):
    job = get_job(job_id)
    if not job:
        return jsonify({"ok": False, "error": "Job not found"}), 404
    engine = PipelineEngine()
    result = engine.run(job)
    return jsonify(result)

@app.route("/api/artifacts/<job_id>")
def api_artifacts(job_id):
    return jsonify(get_artifacts(job_id))

@app.route("/api/pipeline/<job_id>")
def api_pipeline(job_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT * FROM pipeline_history
        WHERE job_id=?
        ORDER BY started_at DESC LIMIT 1
    """, (job_id,)).fetchone()
    conn.close()
    return jsonify(dict(row) if row else {})

@app.route("/api/worker/stats")
def api_worker_stats():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    stats = get_worker_stats(conn)
    conn.close()
    return jsonify(stats)

if __name__ == "__main__":
    app.run(port=8750, debug=True)
