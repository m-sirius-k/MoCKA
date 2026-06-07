from workers.base_worker import BaseWorker
from datetime import datetime
from kernel.logger import info, error

class XWorker(BaseWorker):
    name         = "x"
    version      = "1.0.0"
    capabilities = ["post_x", "schedule_x"]
    priority     = 3
    tags         = ["prod"]

    def execute(self, job: dict) -> dict:
        started = datetime.now().isoformat()
        try:
            content = job.get("content","")
            if len(content) > 140:
                content = content[:137] + "..."

            info(f"[X] 投稿: {job['id']} "
                 f"({len(content)}文字)")

            # Phase4: モック実装
            # Phase5以降: Twitter API v2実装
            # import tweepy
            # client = tweepy.Client(bearer_token=...)
            # client.create_tweet(text=content)

            result_url = f"https://x.com/status/mock_{job['id']}"
            self._record_history(
                job["id"], "post_x",
                "done", started, artifact=result_url)
            return {"success": True,
                    "result_url": result_url,
                    "artifact_path": "",
                    "error": ""}
        except Exception as e:
            error(f"[X] 失敗: {e}")
            self._record_history(
                job["id"], "post_x",
                "failed", started, error=str(e))
            return {"success": False, "result_url": "",
                    "artifact_path": "", "error": str(e)}

    def health_check(self) -> bool:
        return True
