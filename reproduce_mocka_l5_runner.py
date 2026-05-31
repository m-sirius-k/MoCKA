"""
MoCKA L5 Runner — サーバー3本起動 → reproduce_mocka.py 実行
SKIP=0 / PASS=49 / FAIL=0 を目指す

使い方（Docker内）:
  python reproduce_mocka_l5_runner.py
"""

import subprocess
import sys
import time
import os
import socket
import io

# UTF-8強制
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def wait_for_port(port, timeout=15.0, interval=0.5):
    """ポートが開くまで待機"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect(("127.0.0.1", port))
            s.close()
            return True
        except Exception:
            time.sleep(interval)
    return False


def start_server(name, cmd, port, env=None):
    """サーバーをバックグラウンド起動してポート開通を確認"""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    merged_env["PYTHONIOENCODING"] = "utf-8"
    merged_env["PYTHONUTF8"] = "1"

    print(f"  [{name}] 起動中... (port {port})", flush=True)
    proc = subprocess.Popen(
        cmd,
        cwd=BASE_DIR,
        env=merged_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if wait_for_port(port, timeout=20.0):
        print(f"  {GREEN}[{name}] port {port} 開通{RESET}", flush=True)
        return proc
    else:
        proc.terminate()
        print(f"  {RED}[{name}] port {port} タイムアウト{RESET}", flush=True)
        return None


def main():
    print(f"\n{BOLD}{'═'*62}{RESET}")
    print(f"{BOLD}  MoCKA L5 Runner — フルスペック再現性証明{RESET}")
    print(f"{BOLD}{'═'*62}{RESET}\n")

    procs = []

    # ── サーバー1: app.py (port 5000) ──────────────────────────────
    # mocka_events.db がない環境用に最小限の環境変数を設定
    app_env = {
        "MOCKA_ROOT": BASE_DIR,
        "MOCKA_DB": os.path.join(BASE_DIR, "data", "mocka_events.db"),
    }
    p1 = start_server(
        "app.py",
        [sys.executable, "-X", "utf8", "app.py"],
        5000,
        env=app_env,
    )
    if p1:
        procs.append(p1)

    # ── サーバー2: mocka_caliber_server.py (port 5679) ─────────────
    caliber_path = os.path.join(BASE_DIR, "caliber", "chat_pipeline", "mocka_caliber_server.py")
    if os.path.exists(caliber_path):
        p2 = start_server(
            "caliber_server",
            [sys.executable, "-X", "utf8", caliber_path],
            5679,
        )
        if p2:
            procs.append(p2)
    else:
        print(f"  {YELLOW}[caliber_server] ファイルなし — スキップ{RESET}", flush=True)

    # ── サーバー3: mocka_mcp_server.py (port 5002) ─────────────────
    p3 = start_server(
        "mcp_server",
        [sys.executable, "-X", "utf8", "mocka_mcp_server.py"],
        5002,
    )
    if p3:
        procs.append(p3)

    print(f"\n  起動済みサーバー: {len(procs)}本\n", flush=True)

    # ── reproduce_mocka.py を実行 ──────────────────────────────────
    print(f"{BOLD}{'─'*62}{RESET}")
    print(f"{BOLD}  reproduce_mocka.py 実行開始{RESET}")
    print(f"{BOLD}{'─'*62}{RESET}\n", flush=True)

    result = subprocess.run(
        [sys.executable, "-X", "utf8", os.path.join(BASE_DIR, "reproduce_mocka.py")],
        cwd=BASE_DIR,
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"},
    )

    # ── サーバー後片付け ───────────────────────────────────────────
    print(f"\n  サーバー停止中...", flush=True)
    for p in procs:
        try:
            p.terminate()
            p.wait(timeout=5)
        except Exception:
            pass

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
