"""
PR-OS Scheduler
予約配信キュー管理 + 実行エンジン
"""
import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

QUEUE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue.json")


# ─────────────────────────────────────────
# Queue I/O
# ─────────────────────────────────────────
def _load() -> dict:
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)

def _save(data: dict):
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────
# Public API
# ─────────────────────────────────────────
def enqueue(ks_id: str, adapter: str, publish_at: str,
            note: str = "") -> dict:
    """
    配信ジョブをキューに追加。
    publish_at: ISO 8601 (例: "2026-06-10T10:00:00+09:00")
    """
    data  = _load()
    queue = data.get("queue", [])

    # 重複チェック
    for job in queue:
        if job["ks_id"] == ks_id and job["adapter"] == adapter and job["status"] == "pending":
            raise ValueError(f"Already queued: {ks_id} / {adapter}")

    job = {
        "job_id":     f"JOB_{len(queue)+1:04d}",
        "ks_id":      ks_id,
        "adapter":    adapter,
        "publish_at": publish_at,
        "status":     "pending",   # pending | running | done | failed | cancelled
        "note":       note,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "result":     None,
    }
    queue.append(job)
    data["queue"] = queue
    _save(data)
    print(f"[Scheduler] Enqueued: {job['job_id']} | {ks_id} → {adapter} @ {publish_at}")
    return job


def cancel(job_id: str) -> bool:
    """ジョブをキャンセル（pending のみ）"""
    data  = _load()
    for job in data["queue"]:
        if job["job_id"] == job_id and job["status"] == "pending":
            job["status"] = "cancelled"
            _save(data)
            print(f"[Scheduler] Cancelled: {job_id}")
            return True
    return False


def get_due_jobs(now: Optional[datetime] = None) -> list:
    """publish_at が現在時刻以前の pending ジョブを返す"""
    now   = now or datetime.now(timezone.utc)
    data  = _load()
    due   = []
    for job in data["queue"]:
        if job["status"] != "pending":
            continue
        try:
            pub = datetime.fromisoformat(job["publish_at"].replace("Z", "+00:00"))
            if pub.tzinfo is None:
                from datetime import timezone as tz
                pub = pub.replace(tzinfo=tz.utc)
            if pub <= now:
                due.append(job)
        except ValueError:
            pass
    return due


def run_due(dry_run: bool = False) -> list:
    """
    期限到来ジョブを実行する。
    dry_run=True の場合は実行せずジョブ一覧のみ返す。
    """
    due = get_due_jobs()
    if not due:
        print("[Scheduler] No due jobs.")
        return []

    # Adapter マップを遅延インポート
    if not dry_run:
        from adapters.wordpress.wp_adapter import WordPressAdapter
        from adapters.x_twitter.x_adapter  import XAdapter
        from adapters.instagram.ig_adapter  import InstagramAdapter
        ADAPTERS = {
            "wordpress": WordPressAdapter,
            "x":         XAdapter,
            "instagram": InstagramAdapter,
        }

    results = []
    data    = _load()

    for job in due:
        print(f"[Scheduler] Running: {job['job_id']} | {job['ks_id']} → {job['adapter']}")
        if dry_run:
            results.append({**job, "dry_run": True})
            continue

        # KSレコード・確定テキスト取得
        try:
            from knowledge_store.ks_manager import get_record
            rec = get_record(job["ks_id"])
            confirmed_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "knowledge_store", "confirmed", f"{job['ks_id']}.md"
            )
            with open(confirmed_path, encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            _update_job(data, job["job_id"], "failed", {"error": str(e)})
            results.append({**job, "error": str(e)})
            continue

        # Adapter実行
        adapter_cls = ADAPTERS.get(job["adapter"])
        if not adapter_cls:
            err = f"Unknown adapter: {job['adapter']}"
            _update_job(data, job["job_id"], "failed", {"error": err})
            results.append({**job, "error": err})
            continue

        try:
            adapter   = adapter_cls()
            converted = adapter.convert(rec, text)
            result    = adapter.publish(converted)
            status    = "done" if result.success else "failed"
            _update_job(data, job["job_id"], status, result.to_dict())

            # KS publish_status 更新
            from knowledge_store.ks_manager import update_publish_status
            pub_status = "published" if result.success else "failed"
            update_publish_status(job["ks_id"], job["adapter"], pub_status)

            results.append(result.to_dict())
        except Exception as e:
            _update_job(data, job["job_id"], "failed", {"error": str(e)})
            results.append({**job, "error": str(e)})

    _save(data)
    return results


def _update_job(data: dict, job_id: str, status: str, result: dict):
    for job in data["queue"]:
        if job["job_id"] == job_id:
            job["status"] = status
            job["result"] = result
            break


def list_jobs(status: str = None) -> list:
    data = _load()
    jobs = data.get("queue", [])
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    return jobs


def queue_summary() -> dict:
    jobs = list_jobs()
    return {
        "total":     len(jobs),
        "pending":   sum(1 for j in jobs if j["status"] == "pending"),
        "done":      sum(1 for j in jobs if j["status"] == "done"),
        "failed":    sum(1 for j in jobs if j["status"] == "failed"),
        "cancelled": sum(1 for j in jobs if j["status"] == "cancelled"),
    }


if __name__ == "__main__":
    # キューテスト
    try:
        job = enqueue("KS_001", "wordpress", "2026-06-06T12:00:00+09:00", note="テスト予約")
        print(json.dumps(job, ensure_ascii=False, indent=2))
    except ValueError as e:
        print(f"Already exists: {e}")

    print("\n--- Queue Summary ---")
    print(json.dumps(queue_summary(), ensure_ascii=False, indent=2))
    print("\n--- Due Jobs (dry run) ---")
    print(run_due(dry_run=True))
