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
HEALTH_OK_INTERVAL = 30  # HEALTH_OK は 30 回に 1 回だけ記録する
_health_ok_counter_file = TIC_DIR / "health_ok_counter.txt"

def _get_health_ok_count() -> int:
    try:
        return int(_health_ok_counter_file.read_text(encoding="utf-8").strip())
    except Exception:
        return 0

def _increment_health_ok_count() -> int:
    n = _get_health_ok_count() + 1
    try:
        _health_ok_counter_file.parent.mkdir(parents=True, exist_ok=True)
        _health_ok_counter_file.write_text(str(n), encoding="utf-8")
    except Exception:
        pass
    return n

GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"

HEALTH_CHECKS = {
    "python_env": {
        "method": "python_env",
        "risk":            "PYTHONUTF8等の不正値でFatal Python errorが発生し全プロセスが起動不能になる",
        "opportunity":     "起動時検知により環境変数汚染を即座に捕捉できる",
        "beta_candidate":  "encoding_policy",
    },
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
        "url": "http://localhost:5000/relay/status",
        "timeout": 5,
        "stale_seconds": 300,
        "optional": True,
        "risk":            "Relay拡張停止でclaudeとの疎通が失われる",
        "opportunity":     "ping監視によりRelay稼働状況を定量的に把握できる",
        "beta_candidate":  "institutionalized_connection",
    },
    "env_bom": {
        "method": "env_bom",
        "risk":            ".envのBOM付きUTF-8でMOCKA_ENDPOINTがNone化し全接続失敗する",
        "opportunity":     "BOM早期検知でエンコーディング起因の無音障害を防止できる",
        "beta_candidate":  "encoding_policy",
    },
    "phi_os_audit": {
        "method": "phi_os_audit",
        "risk":            "Gate外からのDB直接書き込みはPHI-OS信頼境界を破壊する",
        "opportunity":     "Gate経由率100%の継続証明でPHI-OS制度的信頼性を確立できる",
        "beta_candidate":  "governance_integrity",
    },
    "auth_key_drive": {
        "method": "auth_key_drive",
        "optional": True,
        "risk":            "認証キードライブ(A:)未接続でWatcherがFirestore接続できずクラッシュする",
        "opportunity":     "未接続を起動時に明示検知すればWatcherスキップ+案内表示で原因不明のクラッシュを防止できる",
        "beta_candidate":  "encoding_policy",
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


def check_phi_os_audit() -> tuple:
    """
    PHI-OS Gate定期監査 (TODO_324)
    Gate経由率100% / Direct Write 0件 / Actor未設定0件 を継続監視する。
    """
    db_path = Path("C:/Users/sirok/MoCKA/data/mocka_events.db")
    if not db_path.exists():
        return True, "DB not found (skip)"
    try:
        con = sqlite3.connect(str(db_path))

        # audit_violationsテーブル存在確認
        tbl = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_violations'"
        ).fetchone()
        if not tbl:
            con.close()
            return True, "audit_violations table not yet installed (run: python phi_os/audit_trigger.py --install)"

        new_violations = con.execute(
            "SELECT COUNT(*) FROM audit_violations WHERE status = 'NEW'"
        ).fetchone()[0]

        total_events = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        gate_events  = con.execute(
            "SELECT COUNT(*) FROM events WHERE channel_type = 'gate'"
        ).fetchone()[0]
        no_actor = con.execute(
            "SELECT COUNT(*) FROM events WHERE who_actor IS NULL OR who_actor = ''"
        ).fetchone()[0]
        con.close()

        gate_rate = (gate_events / total_events * 100) if total_events > 0 else 100
        issues = []
        if new_violations > 0:
            issues.append(f"Direct Write違反 {new_violations}件")
        if gate_rate < 95:
            issues.append(f"Gate経由率 {gate_rate:.1f}% (<95%)")
        if no_actor > 0:
            issues.append(f"Actor未設定 {no_actor}件")

        if issues:
            return False, " | ".join(issues) + f" (total={total_events} gate={gate_rate:.1f}%)"
        return True, (
            f"Gate経由率{gate_rate:.1f}% Direct-Write 0件 Actor-OK"
            f" (total={total_events})"
        )
    except Exception as e:
        return False, f"監査エラー: {e}"


def check_auth_key_drive() -> tuple:
    """
    認証キードライブ(A:)の接続確認 (Watcherクラッシュ対応)
    mocka_watcher.py の KEY_PATH 由来のドライブ文字が接続されているか確認する。
    """
    import os
    key_path = os.environ.get(
        "MOCKA_FIREBASE_KEY_PATH",
        r"A:\secrets\mocka-knowledge-gate-firebase-adminsdk-fbsvc-53613922c1.json",
    ).strip()
    drive, _ = os.path.splitdrive(key_path)
    if not drive:
        return True, "KEY_PATHにドライブ指定なし (skip)"
    if os.path.exists(drive + "\\"):
        return True, f"認証キードライブ({drive}) 接続済み"
    return False, f"認証キードライブ({drive})が接続されていません。挿入してください"


def check_env_bom() -> tuple:
    """
    .envファイルのBOM（U+FEFF）検知 (TODO_296)
    BOM付きUTF-8でpython-dotenvがキーを認識せずMOCKA_ENDPOINTがNone化した実例対応。
    """
    env_path = Path("C:/Users/sirok/MoCKA/.env")
    if not env_path.exists():
        return True, ".env not found (skip)"
    raw = env_path.read_bytes()
    if raw.startswith(b'\xef\xbb\xbf'):
        return False, ".envにBOM検出 (BOM付きUTF-8) -> MOCKA_ENDPOINTがNone化するリスク"
    return True, ".env BOMなし OK"


def check_python_env() -> tuple:
    """
    Python環境変数の妥当性チェック（PYTHONUTF8等）
    無効値が存在する場合 os.environ 全体をファイルにダンプする。
    2026-06-19: PYTHONUTF8 invalid value で全プロセス起動不能になった事例対応
    """
    import os
    issues = []
    val = os.environ.get("PYTHONUTF8")
    if val is not None and val not in ("0", "1", ""):
        issues.append(f"PYTHONUTF8='{val}' (有効値は '0'/'1'/未設定)")
    pythonioencoding = os.environ.get("PYTHONIOENCODING", "")
    if pythonioencoding and pythonioencoding.lower() not in ("utf-8", "utf_8", "utf8", ""):
        issues.append(f"PYTHONIOENCODING='{pythonioencoding}' (utf-8推奨)")

    if issues:
        _dump_env_snapshot("python_env_invalid", issues)
        return False, " | ".join(issues)
    return True, f"PYTHONUTF8={repr(val) if val is not None else '(unset)'} OK"


def _dump_env_snapshot(trigger: str, errors: list):
    """
    環境変数スナップショットをタイムスタンプ付きファイルに書き出す。
    子プロセス起動失敗・env不正値検知時のフォールバックキャプチャ用。
    """
    import os
    dump_dir = Path("C:/Users/sirok/MoCKA/data/tic/env_dumps")
    dump_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = dump_dir / f"env_dump_{ts}_{trigger}.json"
    payload = {
        "timestamp": datetime.datetime.now().isoformat(),
        "trigger": trigger,
        "errors": errors,
        "environ": dict(os.environ),
    }
    out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def check_relay_dom(cfg: dict) -> tuple:
    """Relay拡張の生存確認: app.py /relay/status を参照（last_ping が stale_seconds 以内ならPASS）"""
    import urllib.request
    import urllib.error
    url = cfg["url"]
    stale = cfg.get("stale_seconds", 300)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MoCKA-TIC-HealthCheck/1.0"})
        with urllib.request.urlopen(req, timeout=cfg.get("timeout", 5)) as r:
            data = json.loads(r.read().decode())
        if data.get("alive"):
            return True, f"Relay alive (last_ping: {data.get('last_ping', '?')}, v{data.get('version', '?')})"
        last = data.get("last_ping")
        if last:
            return False, f"Relay ping stale (>{stale}s): last_ping={last}"
        return False, "Relay: last_ping なし（claude.aiタブ未オープン、または拡張未起動）"
    except urllib.error.URLError:
        return False, "MoCKAサーバー未起動 (localhost:5000 に接続できません)"
    except Exception as e:
        return False, f"エラー: {e}"

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
        if method == "python_env":
            ok, detail = check_python_env()
        elif method == "http_get":
            ok, detail = check_http_get(cfg)
        elif method == "sqlite_check":
            ok, detail = check_sqlite(cfg)
        elif method == "file_hash":
            ok, detail = check_file_hash(cfg)
        elif method == "relay_dom":
            ok, detail = check_relay_dom(cfg)
        elif method == "env_bom":
            ok, detail = check_env_bom()
        elif method == "phi_os_audit":
            ok, detail = check_phi_os_audit()
        elif method == "auth_key_drive":
            ok, detail = check_auth_key_drive()
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

def _accept_mcp_schema_change():
    """現在のmocka_mcp_server.pyのハッシュをHASH_STOREに書き込んで承認する"""
    cfg = HEALTH_CHECKS["mcp_schema_hash"]
    path = Path(cfg["path"])
    store_path = Path(cfg["hash_store"])
    h = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.write_text(
        json.dumps({"path": str(path), "hash": h, "updated": datetime.datetime.now().isoformat()},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"HASH_STORE更新完了: {h}")


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

    # optional チェック（relay_dom_selector 等）は overall 計算から除外
    required = [r for r in results if not HEALTH_CHECKS[r["component"]].get("optional")]
    optional = [r for r in results if     HEALTH_CHECKS[r["component"]].get("optional")]

    total    = len(required)
    passed   = sum(1 for r in required if r["ok"])
    fails    = [r for r in required if not r["ok"]]

    # optional FAIL は WARN 表示（画面には出すが overall に影響しない）
    YELLOW = "\033[93m"
    for r in optional:
        if not r["ok"]:
            r["status"] = "WARN"

    # 前回比で悪化したコンポーネントを DEGRADED として検知
    baseline = _load_baseline()
    degraded = [r["component"] for r in required
                if not r["ok"] and baseline.get(r["component"], {}).get("ok") is True]

    overall  = "ALL PASS" if not fails else ("DEGRADED" if degraded else ("PARTIAL" if passed > 0 else "FAIL"))
    color    = GREEN if not fails else RED

    print()
    print(f"  Overall: {color}{overall} ({passed}/{total}){RESET}")
    if optional:
        warn_items = [r for r in optional if not r["ok"]]
        if warn_items:
            print(f"  {YELLOW}WARN (optional): {[r['component'] for r in warn_items]}{RESET}")
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
        # 子プロセス起動失敗疑いの場合 os.environ を即時キャプチャ
        server_fails = [r for r in fails if r["component"] in ("mocka_server", "caliber_pipeline")]
        if server_fails:
            fail_names = [r["component"] for r in server_fails]
            fail_details = [r["detail"] for r in server_fails]
            _dump_env_snapshot("server_launch_fail_" + "_".join(fail_names), fail_details)
        write_event(
            "HEALTH_FAIL: ヘルスチェック異常検出",
            f"FAIL: {[r['component'] for r in fails]} | {overall}",
            "tic,health_check,health_fail",
        )
    else:
        count = _increment_health_ok_count()
        if count % HEALTH_OK_INTERVAL == 1:
            write_event(
                "HEALTH_OK: ヘルスチェック全件正常",
                f"必須{total}件PASS @ {now_str} (累計{count}回目)",
                "tic,health_check,health_ok",
            )

    return entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MoCKA TIC Health Check")
    parser.add_argument("--component", help="単体チェック対象コンポーネント名")
    parser.add_argument("--accept-change", action="store_true",
                        help="現在のmcp_schema_hashをHASH_STOREに書き込んで承認する")
    args = parser.parse_args()
    if args.accept_change:
        _accept_mcp_schema_change()
    else:
        run(target=args.component)
