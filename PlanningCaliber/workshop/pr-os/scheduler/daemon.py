"""
PR-OS Scheduler Daemon
キューを定期ポーリングし、期限到来ジョブを自動実行する。
TSIヘルスチェックも定期実行。

実行:
  python scheduler/daemon.py           # フォアグラウンド
  python scheduler/daemon.py --once    # 1回だけ実行して終了
"""
import os
import sys
import time
import signal
import argparse
import threading
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DAEMON_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "logs", "daemon.log")

# ── Config ─────────────────────────────────────────────
SCHEDULER_INTERVAL_SEC = 60    # スケジューラーチェック間隔（秒）
TSI_INTERVAL_SEC       = 300   # TSIヘルスチェック間隔（秒）
running = True


# ── Logger ─────────────────────────────────────────────
def log(msg: str, level: str = "INFO"):
    ts   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(DAEMON_LOG), exist_ok=True)
    with open(DAEMON_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── Scheduler tick ──────────────────────────────────────
def scheduler_tick():
    from scheduler.scheduler import run_due
    try:
        results = run_due(dry_run=False)
        if results:
            ok  = sum(1 for r in results if r.get("success"))
            ng  = len(results) - ok
            log(f"Scheduler: {len(results)} job(s) processed — OK:{ok} NG:{ng}")
        else:
            log("Scheduler: no due jobs", "DEBUG")
    except Exception as e:
        log(f"Scheduler error: {e}", "ERROR")


# ── TSI tick ───────────────────────────────────────────
def tsi_tick():
    from scheduler.tsi import run
    try:
        summary = run(verbose=False)
        alerts  = summary.get("new_alerts", [])
        log(f"TSI: OK={summary['ok']} Disabled={summary['disabled']} "
            f"Error={summary['error']} Alerts={len(alerts)}")
        for a in alerts:
            log(f"TSI ALERT [{a['severity'].upper()}]: {a['message']}", "WARN")
    except Exception as e:
        log(f"TSI error: {e}", "ERROR")


# ── Signal handler ──────────────────────────────────────
def _stop(sig, frame):
    global running
    log("Daemon stopping (signal received)...")
    running = False

signal.signal(signal.SIGINT,  _stop)
signal.signal(signal.SIGTERM, _stop)


# ── Main loop ───────────────────────────────────────────
def run_daemon(once: bool = False):
    global running

    log("=" * 50)
    log("PR-OS Daemon starting")
    log(f"  Scheduler interval : {SCHEDULER_INTERVAL_SEC}s")
    log(f"  TSI interval       : {TSI_INTERVAL_SEC}s")
    log("=" * 50)

    if once:
        log("Running single tick (--once mode)")
        scheduler_tick()
        tsi_tick()
        log("Single tick complete.")
        return

    last_tsi = 0.0

    while running:
        now = time.time()

        # スケジューラー毎ティック
        scheduler_tick()

        # TSI は間隔ごと
        if now - last_tsi >= TSI_INTERVAL_SEC:
            tsi_tick()
            last_tsi = now

        # 次のティックまでスリープ（1秒刻みで停止シグナルに応答）
        for _ in range(SCHEDULER_INTERVAL_SEC):
            if not running:
                break
            time.sleep(1)

    log("PR-OS Daemon stopped.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="PR-OS Scheduler Daemon")
    p.add_argument("--once", action="store_true",
                   help="1回だけ実行して終了")
    args = p.parse_args()
    run_daemon(once=args.once)
