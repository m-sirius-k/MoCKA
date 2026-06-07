from workers.base_worker import BaseWorker
from datetime import datetime
from kernel.logger import info, error

class WordPressWorker(BaseWorker):
    name = "wordpress"
    version = "1.0.0"
    capabilities = ["publish_blog", "publish_lp"]

    def execute(self, job: dict) -> dict:
        started = datetime.now().isoformat()
        try:
            info(f"[WordPress] 実行: {job['id']} / {job['title']}")

            # Phase2: モック実装
            # Phase3以降: WordPress REST API実装
            # import requests
            # res = requests.post(
            #   "https://mocka.nsjp.org/wp-json/wp/v2/pages",
            #   auth=(WP_USER, WP_APP_PASSWORD),
            #   json={"title": job["title"],
            #         "content": job["content"],
            #         "status": "publish"})

            result_url = f"https://mocka.nsjp.org/?p={job['id'][-4:]}"
            self._record_history(
                job["id"], "publish_blog",
                "done", started, artifact=result_url)
            return {
                "success": True,
                "result_url": result_url,
                "artifact_path": "",
                "error": ""
            }
        except Exception as e:
            error(f"[WordPress] 失敗: {e}")
            self._record_history(
                job["id"], "publish_blog",
                "failed", started, error=str(e))
            return {"success": False, "result_url": "",
                    "artifact_path": "", "error": str(e)}

    def health_check(self) -> bool:
        # TODO: REST API疎通テスト（Phase3）
        return True
