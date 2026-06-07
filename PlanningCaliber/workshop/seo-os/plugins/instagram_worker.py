from workers.base_worker import BaseWorker
from datetime import datetime
from kernel.logger import info, error

class InstagramWorker(BaseWorker):
    name         = "instagram"
    version      = "1.0.0"
    capabilities = ["post_instagram"]
    priority     = 4
    tags         = ["prod"]

    def execute(self, job: dict) -> dict:
        started = datetime.now().isoformat()
        try:
            info(f"[Instagram] 投稿: {job['id']}")

            # Phase4: モック実装
            # Phase5以降: Meta Graph API実装

            result_url = \
                f"https://instagram.com/p/mock_{job['id']}"
            self._record_history(
                job["id"], "post_instagram",
                "done", started, artifact=result_url)
            return {"success": True,
                    "result_url": result_url,
                    "artifact_path": "",
                    "error": ""}
        except Exception as e:
            error(f"[Instagram] 失敗: {e}")
            self._record_history(
                job["id"], "post_instagram",
                "failed", started, error=str(e))
            return {"success": False, "result_url": "",
                    "artifact_path": "", "error": str(e)}

    def health_check(self) -> bool:
        return True
