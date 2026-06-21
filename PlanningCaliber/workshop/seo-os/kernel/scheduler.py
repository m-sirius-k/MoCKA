import sqlite3, uuid, json, os
from datetime import datetime
from kernel.logger import info, warn, error

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/jobs.db")
PIPELINE_DIR = os.path.join(os.path.dirname(__file__), "../pipelines")

# platform -> 既存pipeline名の対応表（Phase1はWordPressのみ確定）
# Phase2でx/github等のcapability/pipelineが整備されたら追記する
_PLATFORM_PIPELINE_MAP = {
    "wordpress": "blog_pipeline",
}


def convert_publish_queue_to_job(item: dict) -> dict:
    """
    pure層: publish_queueの1行をjobsテーブルへINSERTするための行データに変換するだけ。
    DB接続・ファイルI/O・HTTP呼び出しは一切行わない。

    マッピング:
      jobs.title    <- f"[publish_queue] {content_id} -> {platform}"（追跡用）
      jobs.type     <- "publish"（固定）
      jobs.status   <- "approved"（_execute_job()の既存取得条件WHERE status='approved'に乗せる）
      jobs.priority <- publish_queue.priority
      jobs.pipeline <- _PLATFORM_PIPELINE_MAP[platform]（未対応platformは空文字＝デフォルトpipeline）
      jobs.content  <- publish_queue.payload
      jobs.target   <- platform
      jobs.note     <- "source=publish_queue:{publish_queue.id}"（監査追跡用の出自記録）
    """
    platform = item.get("platform", "")
    now = datetime.now().isoformat()
    return {
        "id":          str(uuid.uuid4()),
        "title":       f"[publish_queue] {item.get('content_id', '')} -> {platform}",
        "type":        "publish",
        "status":      "approved",
        "priority":    item.get("priority", 3),
        "pipeline":    _PLATFORM_PIPELINE_MAP.get(platform, ""),
        "content":     item.get("payload", ""),
        "target":      platform,
        "policy":      "",
        "author":      "system:publish_queue",
        "ai_draft":    0,
        "created_at":  now,
        "approved_at": now,
        "note":        f"source=publish_queue:{item.get('id', '')}",
    }


def classify_tick(publish_item: dict | None, job_item: dict | None) -> dict:
    """
    pure層: 副作用なし。読み取り済みの2件(publish_queue/jobs)から
    「今tickでどちらを処理すべきか」だけを判定して返す。
    DB接続・ファイルI/O・HTTP呼び出しは一切行わない。

    優先順位: publish_queue優先。
    理由: publish_queueはSEO-OS kernelの「入力層」(外部入力バッファ)であり、
    詰まらせると上流(PR-OS/Caliber)からの到達が滞留する。jobsは内部実行管理で
    既にqueued/running状態を持ち得るため、入力層の処理を優先する。
    """
    if publish_item is not None:
        return {"target": "publish_queue", "item": publish_item}
    if job_item is not None:
        return {"target": "jobs", "item": job_item}
    return {"target": "none", "item": None}


class Scheduler:
    """
    責務を限定する（thin Scheduler）:
    1. publish_queue / jobs から次の処理対象を取得（読み取りのみ）
    2. classify_tick（pure層）でどちらを処理するか判定
    3. 判定結果に応じてexecute層（DB更新・adapter実行）を呼ぶ
    """

    def _fetch_next_publish_item(self, conn) -> dict | None:
        row = conn.execute("""
            SELECT * FROM publish_queue
            WHERE status='pending'
            ORDER BY priority, created_at
            LIMIT 1
        """).fetchone()
        return dict(row) if row else None

    def _fetch_next_job(self, conn) -> dict | None:
        # 'retry'はmax1回までの再試行対象。approvedと同等に即時処理対象とする(Phase1簡素優先)
        row = conn.execute("""
            SELECT * FROM jobs
            WHERE status IN ('approved', 'retry')
            ORDER BY priority, approved_at
            LIMIT 1
        """).fetchone()
        return dict(row) if row else None

    def run_once(self):
        """
        tick本体。個別item処理の例外は_execute_job()/_execute_publish_queue_item()
        内部で吸収されるが、想定外の例外（fetch失敗・classify_tick自体のバグ等）が
        漏れてきた場合の最終防波堤としてもここでtry/exceptする。
        1件・1tickの異常で呼び出し元のループ全体を停止させない。
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            publish_item = self._fetch_next_publish_item(conn)
            job_item = self._fetch_next_job(conn)
            conn.close()

            decision = classify_tick(publish_item, job_item)

            if decision["target"] == "publish_queue":
                return self._execute_publish_queue_item(decision["item"])
            if decision["target"] == "jobs":
                return self._execute_job(decision["item"])
            return None
        except Exception as e:
            error(f"[Scheduler] tick失敗(このtickのみ・次回tickは継続): {e}")
            return None

    def _execute_job(self, job: dict):
        job_id = job["id"]
        conn = sqlite3.connect(DB_PATH)
        try:
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
        except Exception as e:
            self._fail(conn, job_id, None, f"Job起動前エラー: {e}")
            conn.close()
            return
        conn.close()

        self._execute_steps(job, steps, ph_id, total)

    def _execute_publish_queue_item(self, item: dict):
        """
        execute層（薄い変換専任）: publish_queueの1件をjobsテーブル行に変換してINSERTし、
        publish_queue側を'transferred'に更新するだけ。
        実際の配信実行・adapter呼び出し・監査ログ記録は次tick以降の既存_execute_job()経路に
        すべて委ねる（実行系の二重化を避けるため、ここではadapterを直接叩かない）。

        platform_statusがinactive(active化されていない)のplatformは、
        まだ配信対象として確定していないためjobsへ変換せずpublish_queueに留め置く。
        次回tickでplatform_statusがactiveに変わった時点で再評価しjobsへ変換する(replay設計)。

        例外発生時はpublish_queueをstatus='failed'にして1件だけ切り離す。
        publish_queueはclassify_tickで常に優先されるため、ここで失敗を吸収せずpending
        のまま残すと、不正payload1件がjobsレーンを永久にブロックする(poison message化)。
        """
        item_id = item.get("id", "")
        conn = sqlite3.connect(DB_PATH)
        try:
            platform = item.get("platform", "")
            content_id = item.get("content_id", "")

            status_row = conn.execute(
                "SELECT status FROM platform_status WHERE content_id=? AND platform=?",
                (content_id, platform)).fetchone()
            is_active = (status_row is None) or (status_row[0] == "active")

            if not is_active:
                info(f"[Scheduler] publish_queue留め置き(platform_status inactive): "
                     f"{item_id} / platform={platform}")
                return None

            job_row = convert_publish_queue_to_job(item)
            conn.execute("""
                INSERT INTO jobs
                (id,title,type,status,priority,pipeline,content,target,policy,
                 author,ai_draft,created_at,approved_at,note)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (job_row["id"], job_row["title"], job_row["type"], job_row["status"],
                  job_row["priority"], job_row["pipeline"], job_row["content"],
                  job_row["target"], job_row["policy"], job_row["author"],
                  job_row["ai_draft"], job_row["created_at"], job_row["approved_at"],
                  job_row["note"]))
            conn.commit()

            now = datetime.now().isoformat()
            conn.execute(
                "UPDATE publish_queue SET status='transferred', processed_at=? WHERE id=?",
                (now, item_id))
            conn.commit()

            info(f"[Scheduler] publish_queue→jobs変換完了: {item_id} -> job {job_row['id']}")
            return job_row["id"]
        except Exception as e:
            error(f"[Scheduler] publish_queue変換失敗(この1件のみ・tick継続): {item_id} / {e}")
            try:
                now = datetime.now().isoformat()
                conn.execute(
                    "UPDATE publish_queue SET status='failed', processed_at=?, error=? WHERE id=?",
                    (now, str(e), item_id))
                conn.commit()
            except Exception as e2:
                error(f"[Scheduler] publish_queue失敗記録すら失敗: {item_id} / {e2}")
            return None
        finally:
            conn.close()

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

    def _append_note(self, conn, job_id, new_note):
        """
        note列は出自記録(source=publish_queue:{id}等)を保持するため上書き禁止。
        既存noteに" | "区切りで追記するだけ(JSON化はPhase1見送り)。
        """
        row = conn.execute("SELECT note FROM jobs WHERE id=?", (job_id,)).fetchone()
        existing = row[0] if row and row[0] else ""
        updated = f"{existing} | {new_note}" if existing else new_note
        conn.execute("UPDATE jobs SET note=? WHERE id=?", (updated, job_id))
        conn.commit()

    def _fail(self, conn, job_id, ph_id, reason):
        """
        retry機構: 最大1回まで。retry_count<1ならstatus='retry'にして
        次tickで即再処理対象(_fetch_next_jobがapproved同様に拾う)とする。
        retry_count>=1なら(=1回再試行済み)status='failed'で確定。
        間隔は空けずシンプルに即時再処理(Phase1簡素優先)。
        """
        now = datetime.now().isoformat()
        row = conn.execute("SELECT retry_count FROM jobs WHERE id=?", (job_id,)).fetchone()
        retry_count = row[0] if row and row[0] is not None else 0

        if retry_count < 1:
            new_status = "retry"
            retry_count += 1
        else:
            new_status = "failed"

        conn.execute(
            "UPDATE jobs SET status=?, retry_count=? WHERE id=?",
            (new_status, retry_count, job_id))
        conn.commit()
        self._append_note(conn, job_id, f"error={reason}")

        if ph_id:
            conn.execute("""
                UPDATE pipeline_history
                SET status='failed', finished_at=? WHERE id=?
            """, (now, ph_id))
            conn.commit()
        error(f"[Scheduler] Job{new_status}: {job_id} / {reason} (retry_count={retry_count})")
