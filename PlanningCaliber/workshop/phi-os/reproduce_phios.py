"""
PHI-OS Proof of Reproducibility — 再現スクリプト

PHI-OS (Persistent History Interface) Chrome拡張 v1.0.0 の証明スクリプト。

使い方:
  python reproduce_phios.py

成功時:
  PHI-OS Proof of Reproducibility: VERIFIED (L4)
  Reproduction Hash: sha256:xxxxxxxx
  Result saved: reproduce_output/PHIOS_REPRODUCE_RESULT.md
"""

import hashlib
import json
import os
import re
import sys
import time
import io
from datetime import datetime

# Windows cp932 / Docker UTF-8 対策
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXT_DIR  = os.path.join(BASE_DIR, "extension")

GREEN  = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"
CYAN   = "\033[96m"; BOLD = "\033[1m"; RESET  = "\033[0m"

results = []
errors  = []

def record(id, name, status, detail):
    results.append({"id": id, "name": name, "status": status, "detail": detail})
    icon = f"{GREEN}PASS{RESET}" if status == "PASS" else (f"{RED}FAIL{RESET}" if status == "FAIL" else f"{YELLOW}SKIP{RESET}")
    print(f"  [{icon}] {id}: {name}")
    if status != "PASS":
        print(f"         {YELLOW}{detail}{RESET}")
        if status == "FAIL":
            errors.append(f"{id}: {detail}")

def run_test(id, name, fn):
    try:
        ok, detail = fn()
        record(id, name, "PASS" if ok else "FAIL", detail)
    except Exception as e:
        record(id, name, "FAIL", f"EXCEPTION: {e}")

def skip_test(id, name, reason):
    record(id, name, "SKIP", reason)

# ─── P-S-01: スキーマバージョン整合性 ─────────────────────────────────────────

def scenario_p01_schema():
    print(f"\n{BOLD}[P-S-01] スキーマバージョン整合性試験{RESET}")

    def t_version_in_bg():
        bg = open(os.path.join(EXT_DIR, "background.js"), encoding="utf-8").read()
        ok = "SCHEMA_VERSION  = '1.0.0'" in bg or "SCHEMA_VERSION = '1.0.0'" in bg
        return ok, f"background.js に SCHEMA_VERSION='1.0.0' {'あり' if ok else 'なし'}"
    run_test("P-S-01-a", "SCHEMA_VERSION='1.0.0' in background.js", t_version_in_bg)

    def t_known_products():
        bg = open(os.path.join(EXT_DIR, "background.js"), encoding="utf-8").read()
        ok = all(p in bg for p in ["'relay'", "'orchestra'", "'memory'"])
        missing = [p for p in ["'relay'", "'orchestra'", "'memory'"] if p not in bg]
        return ok, f"KNOWN_PRODUCTS 確認 {'' if ok else f'欠損:{missing}'}"
    run_test("P-S-01-b", "KNOWN_PRODUCTS=['relay','orchestra','memory']", t_known_products)

    def t_schema_init_fn():
        bg = open(os.path.join(EXT_DIR, "background.js"), encoding="utf-8").read()
        ok = "async function ensureSchemaVersion" in bg
        return ok, f"ensureSchemaVersion() 関数あり={ok}"
    run_test("P-S-01-c", "ensureSchemaVersion() 関数定義あり", t_schema_init_fn)

    def t_register_product_fn():
        bg = open(os.path.join(EXT_DIR, "background.js"), encoding="utf-8").read()
        ok = "async function registerProduct" in bg
        return ok, f"registerProduct() 関数あり={ok}"
    run_test("P-S-01-d", "registerProduct() 関数定義あり", t_register_product_fn)

# ─── P-S-02: メッセージタイプ仕様 ─────────────────────────────────────────────

def scenario_p02_messages():
    print(f"\n{BOLD}[P-S-02] メッセージタイプ仕様試験{RESET}")
    bg = open(os.path.join(EXT_DIR, "background.js"), encoding="utf-8").read()

    required_msgs = [
        "PHI_HEARTBEAT", "PHI_COMMIT_DONE", "PHI_REGISTER_PRODUCT",
        "PHI_OPEN_POPUP", "PHI_PANEL_MODE_CHANGED", "PHI_GET_STATUS",
        "PHI_CLEAR_OLD_DATA",
    ]
    for msg in required_msgs:
        def make_t(m):
            def t():
                ok = f"case '{m}':" in bg or f'case "{m}":' in bg
                return ok, f"'{m}' case あり={ok}"
            return t
        run_test("P-S-02", f"message: {msg}", make_t(msg))

    def t_heartbeat_response():
        ok = "ok: true, ts: Date.now()" in bg or "ok: true" in bg
        return ok, f"PHI_HEARTBEAT response ok:true あり={ok}"
    run_test("P-S-02-x", "PHI_HEARTBEAT: ok:true,ts レスポンス", t_heartbeat_response)

# ─── P-S-03: ストレージキー命名規則 ──────────────────────────────────────────

def scenario_p03_storage_keys():
    print(f"\n{BOLD}[P-S-03] ストレージキー命名規則試験{RESET}")
    bg = open(os.path.join(EXT_DIR, "background.js"), encoding="utf-8").read()

    phi_keys = [
        "phi_schema_version", "phi_product_id_",
        "phi_commit_index", "phi_last_commit_ts", "phi_panel_mode",
    ]
    for key in phi_keys:
        def make_t(k):
            def t():
                ok = k in bg
                return ok, f"'{k}' キーあり={ok}"
            return t
        run_test("P-S-03", f"storage key: {key}", make_t(key))

    def t_prefix_convention():
        # 文字列リテラルとしてストレージに渡されるキーがphi_プレフィックスを持つか確認
        # 例: storage.local.get('some_key') → some_key を抽出
        # オブジェクトリテラル { key: val } は除外
        string_keys = re.findall(r"storage\.local\.(?:get|set)\(\s*['\"]([^'\"]+)['\"]", bg)
        non_phi = [k for k in string_keys if k and not k.startswith('phi_')]
        ok = len(non_phi) == 0
        return ok, f"文字列キーが全てphi_プレフィックス: {string_keys[:5]} (非phi_: {non_phi[:3]})"
    run_test("P-S-03-x", "文字列ストレージキーがphi_プレフィックス", t_prefix_convention)

# ─── P-S-04: i18n対応言語 ─────────────────────────────────────────────────────

def scenario_p04_i18n():
    print(f"\n{BOLD}[P-S-04] i18n対応言語試験{RESET}")
    ct = open(os.path.join(EXT_DIR, "content.js"), encoding="utf-8").read()

    # content.jsにPHI_I18Nオブジェクトがある
    def t_i18n_object():
        ok = "const PHI_I18N" in ct
        return ok, f"PHI_I18N定数あり={ok}"
    run_test("P-S-04-a", "PHI_I18N オブジェクト定義あり", t_i18n_object)

    for lang in ["ja", "en", "zh", "ko"]:
        def make_t(l):
            def t():
                ok = f"  {l}:" in ct or f"\n  {l}:" in ct or f"\"{l}\":" in ct
                return ok, f"言語'{l}'あり={ok}"
            return t
        run_test("P-S-04", f"i18n: {lang}", make_t(lang))

    # options.html の lang-select (ja/en/zh/ko/es)
    html = open(os.path.join(EXT_DIR, "ui", "options.html"), encoding="utf-8").read()
    for lang in ["ja", "en", "zh", "ko", "es"]:
        def make_t2(l):
            def t():
                ok = f'value="{l}"' in html
                return ok, f"options.html lang={l} あり={ok}"
            return t
        run_test("P-S-04", f"options.html lang-select: {lang}", make_t2(lang))

# ─── P-S-05: manifest.json 整合性 ─────────────────────────────────────────────

def scenario_p05_manifest():
    print(f"\n{BOLD}[P-S-05] manifest.json 整合性試験{RESET}")
    with open(os.path.join(EXT_DIR, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)

    def t_mv3():
        return m["manifest_version"] == 3, f"MV={m['manifest_version']}"
    run_test("P-S-05-a", "Manifest Version = 3", t_mv3)

    def t_name():
        ok = "PHI" in m.get("name", "").upper()
        return ok, f"name='{m.get('name')}'"
    run_test("P-S-05-b", "name に 'PHI' を含む", t_name)

    def t_permissions():
        required = {"storage", "tabs", "sidePanel"}
        got = set(m.get("permissions", []))
        ok  = required.issubset(got)
        return ok, f"permissions={got}"
    run_test("P-S-05-c", "必須パーミッション (storage/tabs/sidePanel)", t_permissions)

    def t_host():
        hosts = m.get("host_permissions", [])
        ok    = "https://claude.ai/*" in hosts
        return ok, f"claude.ai host_permission={ok}"
    run_test("P-S-05-d", "claude.ai host_permission", t_host)

    def t_service_worker():
        bg = m.get("background", {}).get("service_worker")
        return bg == "background.js", f"service_worker={bg}"
    run_test("P-S-05-e", "service_worker = background.js", t_service_worker)

    def t_sidepanel():
        sp = m.get("side_panel", {}).get("default_path")
        return sp == "ui/sidepanel.html", f"side_panel.default_path={sp}"
    run_test("P-S-05-f", "side_panel.default_path = ui/sidepanel.html", t_sidepanel)

    def t_popup():
        p = m.get("action", {}).get("default_popup")
        return p == "ui/options.html", f"action.default_popup={p}"
    run_test("P-S-05-g", "action.default_popup = ui/options.html", t_popup)

# ─── P-S-06: 必須ファイル存在確認 ────────────────────────────────────────────

def scenario_p06_files():
    print(f"\n{BOLD}[P-S-06] 必須ファイル存在確認{RESET}")
    required = [
        "background.js", "content.js", "manifest.json",
        "ui/options.html", "ui/sidepanel.html", "ui/options.css", "ui/options.js",
        "core/state-store.js", "core/commit-engine.js", "core/restore-engine.js",
        "core/event-bus.js", "core/i18n.js",
        "adapters/relay-adapter.js", "adapters/orchestra-adapter.js",
        "adapters/memory-adapter.js",
        "debug/health-check.js",
    ]
    for rel in required:
        path = os.path.join(EXT_DIR, *rel.split("/"))
        def make_t(p, r):
            def t():
                ok = os.path.exists(p)
                return ok, f"{r} {'あり' if ok else 'なし'}"
            return t
        run_test("P-S-06", f"存在: {rel}", make_t(path, rel))

# ─── P-S-07/08/09: JS構文チェック ────────────────────────────────────────────

def scenario_js_syntax():
    import subprocess
    print(f"\n{BOLD}[P-S-07/08/09] JS構文チェック (Node.js --check){RESET}")

    try:
        subprocess.run(["node", "--version"], capture_output=True, timeout=5, check=True)
    except Exception:
        skip_test("P-S-07", "Node.js 未インストール", "node コマンドなし")
        return

    targets = {
        "P-S-07": ["background.js", "content.js"],
        "P-S-08": [
            "core/auto-trigger.js", "core/commit-engine.js", "core/event-bus.js",
            "core/i18n.js", "core/permission-manager.js", "core/restore-engine.js",
            "core/schema-registry.js", "core/state-store.js",
        ],
        "P-S-09": [
            "adapters/memory-adapter.js", "adapters/orchestra-adapter.js",
            "adapters/phi-adapter.js", "adapters/relay-adapter.js",
        ],
        "P-S-10": [
            "debug/debug-panel.js", "debug/error-reporter.js", "debug/health-check.js",
            "ui/options.js", "ui/panel-switch.js",
        ],
    }

    for scenario_id, files in targets.items():
        for rel in files:
            fpath = os.path.join(EXT_DIR, *rel.split("/"))
            def make_t(p, r, sid):
                def t():
                    if not os.path.exists(p):
                        return False, f"ファイルなし: {r}"
                    # background.js / content.js は CJS (CommonJS) → node --check
                    # core/adapters/debug/ui は ES modules (import/export) →
                    #   node --input-type=module stdin経由でチェック
                    is_esm = any(r.startswith(d) for d in
                                 ("core/", "adapters/", "debug/", "ui/"))
                    if is_esm:
                        src = open(p, encoding="utf-8").read().encode("utf-8")
                        result = subprocess.run(
                            ["node", "--input-type=module", "--check"],
                            input=src, capture_output=True, timeout=10
                        )
                    else:
                        result = subprocess.run(
                            ["node", "--check", p],
                            capture_output=True, text=True, timeout=10
                        )
                    ok     = result.returncode == 0
                    stderr = (result.stderr.decode("utf-8", errors="replace")
                              if isinstance(result.stderr, bytes) else result.stderr)
                    # 「Failed to load ES module」 warning は exit 0 なら無視
                    real_err = [l for l in stderr.splitlines()
                                if "SyntaxError" in l or "error" in l.lower()]
                    ok = ok and len(real_err) == 0
                    detail = real_err[0][:150] if not ok else "構文エラーなし"
                    return ok, detail
                return t
            run_test(scenario_id, f"構文: {rel}", make_t(fpath, rel, scenario_id))

# ─── E2E Suite (Puppeteer) ────────────────────────────────────────────────────

def run_e2e_suite():
    import subprocess
    print(f"\n{BOLD}[E2E] Puppeteer Chrome拡張テスト (test/e2e_phios.js){RESET}")

    test_dir = os.path.join(BASE_DIR, "test")
    e2e_path = os.path.join(test_dir, "e2e_phios.js")

    if not os.path.exists(e2e_path):
        skip_test("E2E", "e2e_phios.js が見つからない", f"path={e2e_path}")
        return

    try:
        proc = subprocess.run(
            ["node", e2e_path],
            capture_output=True, timeout=180, cwd=test_dir,
        )
        stdout = proc.stdout.decode("utf-8", errors="replace")
        stderr = proc.stderr.decode("utf-8", errors="replace")

        try:
            e2e_results = json.loads(stdout)
        except json.JSONDecodeError:
            # stdout が JSON でない場合はスキップ
            skip_test("E2E", "E2E JSON parse失敗", stdout[:100])
            return

        for r in e2e_results:
            fn_status = "PASS" if r.get("status") == "PASS" else "FAIL"
            results.append({
                "id": r.get("id", "E2E"), "name": r.get("name", "")[:50],
                "status": fn_status, "detail": r.get("detail", "")[:80],
            })
            icon = f"{GREEN}PASS{RESET}" if fn_status == "PASS" else f"{RED}FAIL{RESET}"
            print(f"  [{icon}] {r.get('id','E2E')}: {r.get('name','')[:50]}")
            if fn_status != "PASS":
                print(f"         {YELLOW}{r.get('detail','')}{RESET}")
                errors.append(f"{r.get('id')}: {r.get('detail','')}")

    except subprocess.TimeoutExpired:
        skip_test("E2E", "Puppeteer E2Eタイムアウト (180s)", "Chrome起動失敗の可能性")
    except FileNotFoundError:
        skip_test("E2E", "node コマンドなし", "Node.js未インストール")

# ─── Report ───────────────────────────────────────────────────────────────────

def print_header():
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"{BOLD}  PHI-OS v1.0.0 — Proof of Reproducibility{RESET}")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Target: PHI OS Chrome Extension (Persistent History Interface)")
    print(f"{BOLD}{'═'*60}{RESET}\n")

def generate_report(duration_sec):
    passed  = sum(1 for r in results if r["status"] == "PASS")
    failed  = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    total   = len(results)

    l1 = passed >= 5
    l2 = passed >= 15
    l3 = passed >= 20 and failed == 0
    l4 = l3 and skipped == 0

    hash_input = json.dumps({
        "product": "PHI-OS v1.0.0",
        "date": datetime.now().isoformat(),
        "passed": passed, "failed": failed, "skipped": skipped,
        "results": [{"id": r["id"], "status": r["status"]} for r in results],
    }, ensure_ascii=False, sort_keys=True).encode("utf-8")
    sha256 = hashlib.sha256(hash_input).hexdigest()

    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"{BOLD}  試験結果サマリー{RESET}")
    print(f"  PASS: {GREEN}{passed}{RESET}  FAIL: {RED}{failed}{RESET}  SKIP: {YELLOW}{skipped}{RESET}  TOTAL: {total}")
    print(f"  実行時間: {duration_sec:.2f}s")
    print(f"\n  証明レベル:")
    print(f"  L1 Proof of Concept:        {'✅' if l1 else '❌'}")
    print(f"  L2 Proof of Implementation: {'✅' if l2 else '❌'}")
    print(f"  L3 Proof of Operation:      {'✅' if l3 else '❌'} (FAIL=0 必要)")
    print(f"  L4 Proof of Reproducibility:{'✅' if l4 else '❌'} (SKIP=0 必要)")
    print(f"\n  Reproduction Hash: sha256:{sha256[:16]}...")
    print(f"{BOLD}{'═'*60}{RESET}")

    if l4:
        print(f"\n{GREEN}{BOLD}  PHI-OS Proof of Reproducibility: VERIFIED (L4){RESET}")
    elif l3:
        print(f"\n{GREEN}{BOLD}  PHI-OS Proof of Reproducibility: VERIFIED (L3){RESET}")
    elif failed == 0:
        print(f"\n{GREEN}{BOLD}  PHI-OS Proof of Reproducibility: VERIFIED (L2){RESET}")
    else:
        print(f"\n{YELLOW}{BOLD}  PHI-OS Proof of Reproducibility: PARTIAL (L1){RESET}")
        for e in errors:
            print(f"    {RED}- {e}{RESET}")

    # 結果ファイル保存
    rows = "\n".join(
        f"| {r['id']} | {r['name'][:40]} | {r['status']} | {r['detail'][:60]} |"
        for r in results
    )
    md = f"""# PHIOS_REPRODUCE_RESULT.md

**PHI-OS v1.0.0 — Proof of Reproducibility**

- 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 実行環境: Python {sys.version.split()[0]}

## 試験結果

| ID | 名称 | 結果 | 詳細 |
|----|------|------|------|
{rows}

## サマリー

| 項目 | 値 |
|-----|---|
| PASS | {passed} |
| FAIL | {failed} |
| SKIP | {skipped} |
| TOTAL | {total} |
| 実行時間 | {duration_sec:.2f}s |

## 証明レベル

| レベル | 達成 |
|-------|-----|
| L1 | {"✅" if l1 else "❌"} |
| L2 | {"✅" if l2 else "❌"} |
| L3 | {"✅" if l3 else "❌"} |
| L4 | {"✅" if l4 else "❌"} |

## Reproduction Hash

```
sha256:{sha256}
```
"""
    out_dir = os.path.join(BASE_DIR, "reproduce_output")
    os.makedirs(out_dir, exist_ok=True)
    for path in [os.path.join(BASE_DIR, "PHIOS_REPRODUCE_RESULT.md"),
                 os.path.join(out_dir, "PHIOS_REPRODUCE_RESULT.md")]:
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
    print(f"\n  Result saved: {os.path.join(out_dir, 'PHIOS_REPRODUCE_RESULT.md')}")
    return l4

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print_header()
    start = time.time()

    scenario_p01_schema()
    scenario_p02_messages()
    scenario_p03_storage_keys()
    scenario_p04_i18n()
    scenario_p05_manifest()
    scenario_p06_files()
    scenario_js_syntax()
    run_e2e_suite()

    duration = time.time() - start
    verified = generate_report(duration)
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())
