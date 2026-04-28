import sys
from pathlib import Path

APP = Path("C:/Users/sirok/MoCKA/app.py")
CROSS = Path("C:/Users/sirok/MoCKA/interface/cross_audit.py")

# cross_audit.pyを配置
import shutil
src = Path("C:/Users/sirok/MoCKA/cross_audit.py")
if src.exists():
    shutil.copy(src, CROSS)
    print(f"OK: cross_audit.py -> {CROSS}")
else:
    print(f"NG: {src} not found")
    sys.exit(1)

# app.pyにエンドポイント追加
content = APP.read_text(encoding="utf-8")

MARKER = "if __name__ == '__main__':"
if "cross_audit" in content:
    print("- cross_audit already in app.py")
    sys.exit(0)

INSERT = '''
# ── cross_audit エンドポイント ───────────────────────────────────────────────
try:
    from interface.cross_audit import (
        init_audit_db, create_task, submit_result,
        run_discrepancy_check, get_task_report, list_tasks as list_audit_tasks
    )
    init_audit_db()
    print("[app] cross_audit engine loaded")

    @app.route("/cross_audit/task", methods=["POST"])
    def cross_audit_task():
        data = request.json or {}
        task_text = data.get("task", "")
        agents = data.get("agents", None)
        if not task_text:
            return jsonify({"error": "task required"}), 400
        return jsonify(create_task(task_text, agents))

    @app.route("/cross_audit/submit", methods=["POST"])
    def cross_audit_submit():
        data = request.json or {}
        task_id  = data.get("task_id", "")
        agent    = data.get("agent", "")
        response = data.get("response", "")
        score    = float(data.get("score", 0.0))
        if not task_id or not agent:
            return jsonify({"error": "task_id and agent required"}), 400
        return jsonify(submit_result(task_id, agent, response, score))

    @app.route("/cross_audit/check/<task_id>")
    def cross_audit_check(task_id):
        discs = run_discrepancy_check(task_id)
        return jsonify({"task_id": task_id, "discrepancies": discs, "count": len(discs)})

    @app.route("/cross_audit/report/<task_id>")
    def cross_audit_report(task_id):
        return jsonify(get_task_report(task_id))

    @app.route("/cross_audit/list")
    def cross_audit_list():
        return jsonify(list_audit_tasks())

except Exception as _ce:
    print(f"[app] cross_audit load error: {_ce}")
# ─────────────────────────────────────────────────────────────────────────────

'''

if MARKER in content:
    content = content.replace(MARKER, INSERT + MARKER, 1)
    APP.write_text(content, encoding="utf-8")
    print("OK: cross_audit endpoints added to app.py")
else:
    # マーカーがない場合は末尾に追加
    APP.write_text(content + INSERT, encoding="utf-8")
    print("OK: cross_audit endpoints appended to app.py")
