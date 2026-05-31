"""
health_check.py  -- TIC Health Check
MoCKA-START.bat 起動時に走る「地震計」。
7項目をチェックし、FAILはprevention_queueに投入する。

Usage:
  python health_check.py              # 全チェック
  python health_check.py --component mocka_server  # 単体チェック
"""

import json
import sys
import io
import sqlite3
import hashlib
import datetime
import argparse
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── パス ──
TIC_DIR       = Path("C:/Users/sirok/MoCKA/data/tic")
HEALTH_LOG    = TIC_DIR / "health_log.jsonl"
HASH_STORE    = TIC_DIR / "mcp_schema_hash.json"
PREV_QUEUE    = Path("C:/Users/sirok/MoCKA/data/prevention_queue.json")
MCP_URL       = "http://localhost:5002/agent/mocka_write_event"

GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"

HEALTH_CHECKS = {
    "mocka_server": {
        "method": "http_get",
        "url": "http://localhost:5000/loop/status",
        "timeout": 5,
        "expect_status": [200],
    },
    "caliber_pipeline": {
        "method": "http_get",
        "url": "http://localhost:5679/health",
        "timeout": 5,
        "expect_status": [200],
    },
    "anthropic_api": {
        "method": "http_get",
        "url": "https://api.anthropic.com/v1/models",
        "timeout": 10,
        "expect_status": [200, 401],
    },
    "stripe_worker": {
        "method": "http_get",
        "url": "https://orchestra-license.nsjpkimura.workers.dev/health",
        "timeout": 10,
        "expect_status": [200],
    },
    "sqlite_integrity": {
        "method": "sqlite_check",
        "path": "C:/Users/sirok/MoCKA/data/mocka_events.db",
        "pragma": "integrity_check",
    },
    "mcp_schema_hash": {
        "method": "file_hash",
        "path": "C:/Users/sirok/MoCKA/mocka_mcp_server.py",
        "hash_store": str(HASH_STORE),
    },
    "python_imports": {
        "method": "import_test",
        "modules": ["janome", "httpx", "flask", "sqlite3", "hashlib"],
    },
}


# ── チェック実装 ──

def check_http_get(cfg: dict) -> tuple:
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(cfg["url"])
        with urllib.request.urlopen(req, timeout=cfg["timeout"]) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception as e:
        return False, f"接続エラー: {e}"
    expected = cfg.get("expect_status", [200])
    if status in expected:
        note = "(疎通確認OK)" if status == 401 else "OK"
        return True, f"{status} {note}"
    return False, f"HTTP {status} (期待値: {expected})"


def check_sqlite(cfg: dict) -> tuple:
    path = cfg["path"]
    if not Path(path).exists():
        return False, f"DB not found: {path}"
    try:
        con = sqlite3.connect(path)
        cur = con.execute("PRAGMA integrity_check")
        result = cur.fetchone()[0]
        con.close()
        if result == "ok":
            return True, "ok"
        return False, f"integrity_check: {result}"
    except Exception as e:
        return False, str(e)


def check_file_hash(cfg: dict) -> tuple:
    path = Path(cfg["path"])
    store_path = Path(cfg["hash_store"])
    if not path.exists():
        return False, f"ファイル不在: {path}"
    h = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    if store_path.exists():
        stored = json.loads(store_path.read_text(encoding="utf-8"))
        prev = stored.get("hash", "")
        if prev and prev != h:
            return False, f"ハッシュ変更検出!\n{'':26}前回: {prev}\n{'':26}今回: {h}"
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.write_text(
        json.dumps({"path": str(path), "hash": h, "updated": datetime.datetime.now().isoformat()},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return True, f"変更なし (hash: {h})"


def check_imports(cfg: dict) -> tuple:
    failed = []
    for mod in cfg["modules"]:
        try:
            __import__(mod)
        except ImportError:
            failed.append(mod)
    if failed:
        return False, f"インポート失敗: {failed}"
    return True, "全モジュール正常"


def run_check(name: str, cfg: dict) -> dict:
    method = cfg["method"]
    try:
        if method == "http_get":
            ok, detail = check_http_get(cfg)
        elif method == "sqlite_check":
            ok, detail = check_sqlite(cfg)
        elif method == "file_hash":
            ok, detail = check_file_hash(cfg)
        elif method == "import_test":
            ok, detail = check_imports(cfg)
        else:
            ok, detail = False, f"unknown method: {method}"
    except Exception as e:
        ok, detail = False, f"例外: {e}"
    return {"component": name, "status": "PASS" if ok else "FAIL", "detail": detail, "ok": ok}


# ── MoCKA 記録 ──

def write_event(title: str, description: str, tags: str = "tic,health_check"):
    try:
        import urllib.request
        payload = json.dumps({
            "title": title, "description": description,
            "tags": tags, "why_purpose": "TICヘルスチェック",
            "how_trigger": "health_check.py",
        }).encode("utf-8")
        req = urllib.request.Request(
            MCP_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass


# ── prevention_queue 投入 ──

def push_prevention(fails: list):
    if not fails:
        return
    PREV_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(PREV_QUEUE.read_text(encoding="utf-8")) if PREV_QUEUE.exists() else {"queue": []}
    except Exception:
        data = {"queue": []}
    for r in fails:
        data["queue"].append({
            "id": f"TECH_ALERT_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{r['component']}",
            "type": "TECH_ALERT",
            "component": r["component"],
            "detail": r["detail"],
            "detected_at": datetime.datetime.now().isoformat(),
            "status": "NEW",
        })
    PREV_QUEUE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ── ヘルスログ追記 ──

def append_health_log(results: list, overall: str):
    TIC_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "overall": overall,
        "checks": [{"component": r["component"], "status": r["status"], "detail": r["detail"]} for r in results],
        "fail_count": sum(1 for r in results if not r["ok"]),
    }
    with open(HEALTH_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


# ── メイン ──

def run(target: str = None):
    checks = {k: v for k, v in HEALTH_CHECKS.items() if target is None or k == target}
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print("=" * 40)
    print(f"MoCKA Health Check  {now_str}")
    print("=" * 40)

    results = []
    width = max(len(k) for k in checks)
    for name, cfg in checks.items():
        r = run_check(name, cfg)
        results.append(r)
        color = GREEN if r["ok"] else RED
        status = f"{color}{r['status']}{RESET}"
        detail_lines = r["detail"].split("\n")
        print(f"  {name:<{width}}  {status}  {detail_lines[0]}")
        for extra in detail_lines[1:]:
            print(f"  {extra}")

    total    = len(results)
    passed   = sum(1 for r in results if r["ok"])
    fails    = [r for r in results if not r["ok"]]
    overall  = "ALL PASS" if not fails else ("DEGRADED" if passed > 0 else "FAIL")
    color    = GREEN if not fails else RED

    print()
    print(f"  Overall: {color}{overall} ({passed}/{total}){RESET}")
    print("=" * 40)
    print()

    # ログ・記録
    entry = append_health_log(results, overall)

    if fails:
        push_prevention(fails)
        write_event(
            "HEALTH_FAIL: ヘルスチェック異常検出",
            f"FAIL: {[r['component'] for r in fails]} | {overall}",
            "tic,health_check,health_fail",
        )
    else:
        write_event(
            "HEALTH_OK: ヘルスチェック全件正常",
            f"全{total}件PASS @ {now_str}",
            "tic,health_check,health_ok",
        )

    return entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MoCKA TIC Health Check")
    parser.add_argument("--component", help="単体チェック対象コンポーネント名")
    args = parser.parse_args()
    run(target=args.component)
