from workers.base_worker import BaseWorker
from datetime import datetime
from kernel.logger import info, error

class SFTPWorker(BaseWorker):
    name = "sftp"
    version = "1.0.0"
    capabilities = ["upload_html", "upload_asset"]

    def execute(self, job: dict) -> dict:
        started = datetime.now().isoformat()
        try:
            info(f"[SFTP] 実行: {job['id']} → {job.get('target','')}")

            # Phase2: 動作確認用モック実装
            # Phase3以降: paramiko で実際のSFTP転送
            # import paramiko
            # ssh = paramiko.SSHClient()
            # ssh.connect("www1003.sakura.ne.jp", username="nsjp", password="...")
            # sftp = ssh.open_sftp()
            # sftp.put(local_path, remote_path)

            result_url = f"https://mocka.nsjp.org/lp/{job.get('target','')}"
            self._record_history(
                job["id"], "upload_html",
                "done", started,
                artifact=result_url)
            return {
                "success": True,
                "result_url": result_url,
                "artifact_path": "",
                "error": ""
            }
        except Exception as e:
            error(f"[SFTP] 失敗: {e}")
            self._record_history(
                job["id"], "upload_html",
                "failed", started, error=str(e))
            return {"success": False, "result_url": "",
                    "artifact_path": "", "error": str(e)}

    def health_check(self) -> bool:
        # TODO: paramiko接続テスト（Phase3）
        return True
