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
        # Task 9: Risk / Opportunity (Structural Intelligence)
        "risk":            "MoCKAサーバー停止でイベント記録が失われる",
        "opportunity":     "常時稼働が確認できれば制度ログの信頼性が証明される",
        "beta_candidate":  "observation_as_institution",
    },
    "caliber_pipeline": {
        "method": "http_get",
        "url": "http://localhost:5679/health",
        "timeout": 5,
        "expect_status": [200],
        "risk":            "Caliberが止まるとEssence生成が停止し知識蒸留が断絶する",
        "opportunity":     "パイプライン健全性が確認できれば自動知識蒸留の効果を証明できる",
        "beta_candidate":  "process_institutionalization",
    },
    "anthropic_api": {
        "method": "http_get",
        "url": "https://api.anthropic.com/v1/models",
        "timeout": 10,
        "expect_status": [200, 401],
        "risk":            "APIスキーマ変更でCaliberおよびMCPが壊れる可能性",
        "opportunity":     "新エンドポイントでvasAI機能拡張・Claude 4.x活用が可能",
        "beta_candidate":  "api_institutionalization",
    },
    "stripe_worker": {
        "method": "http_get",
        "url": "https://orchestra-license.nsjpkimura-mocka.workers.dev/health",
        "timeout": 10,
        "expect_status": [200],
        "risk":            "課金ワーカー停止でライセンス検証が機能せずユーザー影響が出る",
        "opportunity":     "Cloudflare Workers活用でサーバーレス課金基盤の安定性を証明できる",
        "beta_candidate":  "stability_through_standards",
    },
    "sqlite_integrity": {
        "method": "sqlite_check",
        "path": "C:/Users/sirok/MoCKA/data/mocka_events.db",
        "pragma": "integrity_check",
        "risk":            "DB破損はMoCKA制度の根幹崩壊を意味する（全記録消失）",
        "opportunity":     "integrity_check通過の積み上げがデータ整合性の証拠になる",
        "beta_candidate":  "data_integrity_protocol",
    },
    "mcp_schema_hash": {
        "method": "file_hash",
        "path": "C:/Users/sirok/MoCKA/mocka_mcp_server.py",
        "hash_store": str(HASH_STORE),
        "risk":            "MCPスキーマ無断変更でClaudeとのプロトコルが破壊される",
        "opportunity":     "hash一致の証拠積み上げでコード改ざん検知制度を確立できる",
        "beta_candidate":  "institutionalized_connection",
    },
    "relay_dom_selector": {
        "method": "relay_dom",
        "url": "https://claude.ai",
        "timeout": 8,
        "key_patterns": ["contenteditable", "ProseMirror", "data-testid"],
        "risk":            "claude.ai DOM変更でRelayが完全停止する（非公式依存の典型）",
        "opportunity":     "DOM生存確認によりMCP移行の緊急度を定量的に判断できる",
        "beta_candidate":  "institutionalized_connection",
    },
}


# ── チェック実装 ──

def check_http_get(cfg: dict) -> tuple:
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(
            cfg["url"],
            headers={"User-Agent": "MoCKA-TIC-HealthCheck/1.0"},
        )
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


def check_relay_dom(cfg: dict) -> tuple:
    """claude.ai 疎通確認 HTTP200=PASS セレクター確認はRelay拡張に委譲"""
    url = cfg["url"]
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "MoCKA-HealthCheck/1.0"})
        with urllib.request.urlopen(req, timeout=cfg.get("timeout", 8)) as r:
            status = r.status
        return (status == 200), f"HTTP {status} (claude.ai 疎通OK)"
    except Exception as e:
        return False, f"接続エラー: {e}"

# ── health_baseline.json（全チェック差分検知）──

BASELINE_PATH = Path("C:/Users/sirok/MoCKA/interface/health_baseline.json")


def _load_baseline() -> dict:
    if BASELINE_PATH.exists():
        try:
            return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_baseline(results: list):
    data = {r["component"]: {"ok": r["ok"], "detail": r["detail"]} for r in results}
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_check(name: str, cfg: dict) -> dict:
    method = cfg["method"]
    try:
        if method == "http_get":
            ok, detail = check_http_get(cfg)
        elif method == "sqlite_check":
            ok, detail = check_sqlite(cfg)
        elif method == "file_hash":
            ok, detail = check_file_hash(cfg)
        elif method == "relay_dom":
            ok, detail = check_relay_dom(cfg)
        else:
            ok, detail = False, f"unknown method: {method}"
    except Exception as e:
        ok, detail = False, f"例外: {e}"
    return {
        "component":     name,
        "status":        "PASS" if ok else "FAIL",
        "detail":        detail,
        "ok":            ok,
        "risk":          cfg.get("risk", ""),
        "opportunity":   cfg.get("opportunity", ""),
        "beta_candidate":cfg.get("beta_candidate", ""),
    }


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

    # 前回比で悪化したコンポーネントを DEGRADED として検知
    baseline = _load_baseline()
    degraded = [r["component"] for r in results
                if not r["ok"] and baseline.get(r["component"], {}).get("ok") is True]

    overall  = "ALL PASS" if not fails else ("DEGRADED" if degraded else ("PARTIAL" if passed > 0 else "FAIL"))
    color    = GREEN if not fails else RED

    print()
    print(f"  Overall: {color}{overall} ({passed}/{total}){RESET}")
    print("=" * 40)
    print()

    # [HEALTH] 形式のサマリ行（MoCKA-START.bat ログ用）
    icon = "✅" if not fails else "⚠️"
    print(f"[HEALTH] {icon} {passed}/{total} PASS" +
          (f"  DEGRADED: {degraded}" if degraded else "") +
          (f"  FAIL: {[r['component'] for r in fails]}" if fails else ""))

    # baseline 更新
    _save_baseline(results)

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
