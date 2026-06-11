"""
PHI-OS Layer4: mocka本体接続 / 神の伝令受信 — phi_os_poller.py
PHI-OS-SPEC-001 第5章 5.1準拠

通信方式: ポーリング型
取得間隔  : 5分(POLL_INTERVAL_SECONDS, essence_auto_updaterと同期)
エンドポイント: http://localhost:5000/api/living-context

処理フロー:
  1. /api/living-context をポーリング(GET)
  2. 取得成功 -> ingest('mocka', payload) で即時処理(最優先・他ingestをブロック)
  3. 取得失敗 -> mocka_write_event(PHI_OS_ERROR, error_type='MOCKA_POLL_FAIL')
     を記録して継続(停止しない)
"""
import json
import time
import urllib.error
import urllib.request

from phi_os import PHIOS

LIVING_CONTEXT_URL = "http://localhost:5000/api/living-context"
POLL_INTERVAL_SECONDS = 300
REQUEST_TIMEOUT = 5


def fetch_living_context(url: str = LIVING_CONTEXT_URL) -> dict:
    """mocka本体の /api/living-context をGETする。失敗時は例外を送出する。"""
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as res:
        return json.loads(res.read().decode("utf-8"))


def poll_once(hub: PHIOS, url: str = LIVING_CONTEXT_URL) -> dict:
    """
    1回分のポーリングを実行する。

    成功時: ingest('mocka', payload) を実行して結果を返す(status=OK)。
    失敗時: PHI_OS_ERROR(MOCKA_POLL_FAIL)を記録して継続する(status=POLL_FAIL)。
    """
    try:
        payload = fetch_living_context(url)
    except (urllib.error.URLError, OSError, ValueError) as e:
        hub._handle_error("MOCKA_POLL_FAIL", {"url": url, "error": str(e)})
        return {"status": "POLL_FAIL", "error": str(e)}

    result = hub.ingest("mocka", payload)
    return {"status": "OK", "ingest": result, "payload": payload}


def run_loop(hub: PHIOS, max_iterations: int = None, interval: float = POLL_INTERVAL_SECONDS):
    """
    ポーリングループ。max_iterations=None の場合は無限ループ。
    取得失敗時もループは停止しない。
    """
    i = 0
    while max_iterations is None or i < max_iterations:
        poll_once(hub)
        i += 1
        if max_iterations is None or i < max_iterations:
            time.sleep(interval)


if __name__ == "__main__":
    hub = PHIOS("mocka", "core", "001")
    run_loop(hub)
