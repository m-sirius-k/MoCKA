#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phi_os/process_manager.py (TODO_271)
PHI-OS Process Manager — PID管理・終了管理・Restart管理

MoCKA-START.bat が起動する全プロセスをPHI-OSの制御下に置く。
stale process問題の恒久解決。

Usage:
  python phi_os/process_manager.py --start    # 全プロセス起動
  python phi_os/process_manager.py --status   # 稼働状況確認
  python phi_os/process_manager.py --stop     # 全プロセス停止
  python phi_os/process_manager.py --restart <name>  # 単一プロセス再起動
"""
import sys
import io
import os
import json
import time
import argparse
import subprocess
import datetime
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path("C:/Users/sirok/MoCKA")
PID_FILE = ROOT / "data" / "phi_os_pids.json"
MCP_URL  = "http://localhost:5002/agent/mocka_write_event"

# MoCKA管理対象プロセス一覧
# (TODO_271 note: sync_watch.pyも含める)
MANAGED_PROCESSES = {
    "ping_generator": {
        "cmd": ["python", "interface/ping_generator.py"],
        "cwd": str(ROOT),
        "daemon": True,
        "restart": True,
        "desc": "5分間隔essence ping生成",
    },
    "tech_watcher": {
        "cmd": ["python", "interface/tech_watcher.py"],
        "cwd": str(ROOT),
        "daemon": False,
        "restart": False,
        "desc": "TIC技術変化監視 (起動時1回実行)",
    },
    "risk_scorer": {
        "cmd": ["python", "interface/risk_scorer.py"],
        "cwd": str(ROOT),
        "daemon": False,
        "restart": False,
        "desc": "リスクスコア計算 (起動時1回実行)",
    },
    "risk_interpreter": {
        "cmd": ["python", "interface/risk_interpreter.py"],
        "cwd": str(ROOT),
        "daemon": False,
        "restart": False,
        "desc": "リスク解釈 (起動時1回実行)",
    },
    "sync_watch": {
        "cmd": ["python", "PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py"],
        "cwd": str(ROOT),
        "daemon": True,
        "restart": True,
        "desc": "Cloudflare export 10分周期常駐デーモン (TODO_341)",
    },
    "mocka_app": {
        "cmd": ["python", "app.py"],
        "cwd": str(ROOT),
        "daemon": True,
        "restart": True,
        "desc": "COMMAND CENTER Flask server (port:5000)",
    },
    "mocka_mcp": {
        "cmd": ["python", "mocka_mcp_server.py"],
        "cwd": str(ROOT),
        "daemon": True,
        "restart": True,
        "desc": "MCP Caliber server (port:5002)",
    },
    "mocka_caliber": {
        "cmd": ["python", "caliber/chat_pipeline/mocka_caliber_server.py"],
        "cwd": str(ROOT),
        "daemon": True,
        "restart": True,
        "desc": "Caliber pipeline server (port:5679)",
    },
    "mocka_connector": {
        "cmd": ["python", "gateway/gateway.py"],
        "cwd": str(ROOT),
        "daemon": True,
        "restart": True,
        "desc": "AI Connector Gateway",
    },
}


def load_pids() -> dict:
    if PID_FILE.exists():
        try:
            return json.loads(PID_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_pids(pids: dict):
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(json.dumps(pids, ensure_ascii=False, indent=2), encoding="utf-8")


def is_alive(pid: int) -> bool:
    try:
        import psutil
        return psutil.pid_exists(pid) and psutil.Process(pid).status() != "zombie"
    except ImportError:
        # psutil未インストール時はWindowsのtasklist使用
        try:
            out = subprocess.check_output(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                encoding="utf-8", errors="replace"
            )
            return str(pid) in out
        except Exception:
            return False


def start_process(name: str, cfg: dict, pids: dict) -> int | None:
    existing_pid = pids.get(name, {}).get("pid")
    if existing_pid and is_alive(existing_pid):
        print(f"  [SKIP] {name}: already running (pid={existing_pid})")
        return existing_pid

    cmd_path = Path(cfg["cwd"]) / cfg["cmd"][1]
    if not cmd_path.exists():
        print(f"  [SKIP] {name}: script not found: {cmd_path}")
        return None

    try:
        proc = subprocess.Popen(
            cfg["cmd"],
            cwd=cfg["cwd"],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            if sys.platform == "win32" else 0,
        )
        pids[name] = {
            "pid": proc.pid,
            "started_at": datetime.datetime.now().isoformat(),
            "cmd": " ".join(cfg["cmd"]),
            "desc": cfg["desc"],
        }
        print(f"  [START] {name}: pid={proc.pid} | {cfg['desc']}")
        return proc.pid
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return None


def stop_process(name: str, pids: dict):
    info = pids.get(name, {})
    pid = info.get("pid")
    if not pid:
        print(f"  [SKIP] {name}: no PID recorded")
        return
    try:
        import psutil
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)
            p.terminate()
            p.wait(timeout=5)
            print(f"  [STOP] {name}: pid={pid} terminated")
        else:
            print(f"  [SKIP] {name}: pid={pid} not alive")
    except ImportError:
        try:
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
            print(f"  [STOP] {name}: pid={pid} killed")
        except Exception as e:
            print(f"  [ERROR] {name}: stop failed: {e}")
    pids.pop(name, None)


def cmd_status():
    pids = load_pids()
    print()
    print("PHI-OS Process Status")
    print("-" * 60)
    for name, cfg in MANAGED_PROCESSES.items():
        info = pids.get(name, {})
        pid  = info.get("pid")
        if pid and is_alive(pid):
            status = f"[RUN] pid={pid}"
        elif pid:
            status = f"[DEAD] pid={pid} (stale)"
        else:
            status = "[OFF]"
        print(f"  {name:<20} {status:<20} {cfg['desc']}")
    print()


def cmd_start():
    pids = load_pids()
    print("Starting managed processes...")
    for name, cfg in MANAGED_PROCESSES.items():
        start_process(name, cfg, pids)
    save_pids(pids)
    write_event("PHI_OS_PM_START", f"Process Manager: all processes start initiated")


def cmd_stop():
    pids = load_pids()
    print("Stopping managed processes...")
    for name in list(pids.keys()):
        stop_process(name, pids)
    save_pids(pids)
    write_event("PHI_OS_PM_STOP", "Process Manager: all processes stopped")


def cmd_restart(name: str):
    if name not in MANAGED_PROCESSES:
        print(f"Unknown process: {name}")
        return
    pids = load_pids()
    stop_process(name, pids)
    time.sleep(1)
    start_process(name, MANAGED_PROCESSES[name], pids)
    save_pids(pids)
    write_event(f"PHI_OS_PM_RESTART: {name}", f"Process restarted: {name}")


def write_event(title: str, desc: str):
    try:
        import urllib.request
        payload = json.dumps({
            "title": title, "description": desc,
            "tags": "phi_os,process_manager,todo_271",
            "why_purpose": "PHI-OSプロセス管理",
            "how_trigger": "phi_os/process_manager.py",
        }).encode("utf-8")
        req = urllib.request.Request(
            MCP_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PHI-OS Process Manager (TODO_271)")
    parser.add_argument("--start",   action="store_true", help="全プロセス起動")
    parser.add_argument("--status",  action="store_true", help="稼働状況確認")
    parser.add_argument("--stop",    action="store_true", help="全プロセス停止")
    parser.add_argument("--restart", metavar="NAME",      help="単一プロセス再起動")
    args = parser.parse_args()

    if args.start:
        cmd_start()
    elif args.status:
        cmd_status()
    elif args.stop:
        cmd_stop()
    elif args.restart:
        cmd_restart(args.restart)
    else:
        cmd_status()
