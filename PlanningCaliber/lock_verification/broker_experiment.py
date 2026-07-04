"""
broker_experiment.py
候補3(仲介プロセス/キュー)のH3-1(仲介プロセスダウン時、全経路が停止するか)を検証する
最小実装。3workerはgitに直接触れず、queue_dir配下にリクエストファイルを書くだけ。
broker.pyが起動していれば、それを拾ってsandbox_repoにcommitする。
broker未起動の場合、リクエストが滞留するだけで誰もcommitしないことを確認する。
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime

QUEUE_DIR = Path(r"C:\Users\sirok\MoCKA\PlanningCaliber\lock_verification\broker_queue")
ROOT = Path(r"C:\Users\sirok\MoCKA\PlanningCaliber\lock_verification\sandbox_repo")


def worker_submit(worker_id):
    QUEUE_DIR.mkdir(exist_ok=True)
    req = {"worker_id": worker_id, "submitted_at": datetime.now().isoformat()}
    (QUEUE_DIR / f"req_{worker_id}_{time.time()}.json").write_text(
        json.dumps(req), encoding="utf-8")
    return req


def broker_process_once():
    """brokerが1回だけキューを処理する(常駐ループではなくワンショット、実験用)"""
    if not QUEUE_DIR.exists():
        return []
    processed = []
    for f in sorted(QUEUE_DIR.glob("req_*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        (ROOT / "dummy.txt").write_text(
            f"broker processed worker {data['worker_id']} at {datetime.now().isoformat()}\n",
            encoding="utf-8")
        import subprocess
        subprocess.run(["git", "add", "-A"], cwd=str(ROOT), capture_output=True)
        subprocess.run(["git", "commit", "-m", f"broker: worker{data['worker_id']}"],
                        cwd=str(ROOT), capture_output=True)
        f.unlink()
        processed.append(data)
    return processed


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "submit":
        print(json.dumps(worker_submit(sys.argv[2])))
    elif mode == "broker_run_once":
        print(json.dumps(broker_process_once()))
    elif mode == "queue_status":
        n = len(list(QUEUE_DIR.glob("req_*.json"))) if QUEUE_DIR.exists() else 0
        print(json.dumps({"pending_requests": n}))
