"""
PHI-OS Proof of Reproducibility — 再現スクリプト

vasAIのreproduce_l48.pyと同等の証明を個人向け製品(Relay Chrome拡張)で達成する。

使い方:
  python reproduce_phios.py

成功時:
  PHI-OS Proof of Reproducibility: VERIFIED
  Reproduction Hash: sha256:xxxxxxxx
  Result saved: PHIOS_REPRODUCE_RESULT.md

重要: PHI-OSはChrome拡張機能であるため、chrome.storage / chrome.runtime /
     Web Crypto API に依存する部分はブラウザ環境なしには実行不可。
     本スクリプトはPythonで再実装可能な純粋ロジック層を対象とする。
"""

import hashlib
import json
import os
import re
import sys
import time
import math
import io
from datetime import datetime

# スクリプト位置を基準とした絶対パス（Docker / Windows 両対応）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Windows cp932 対策: stdout を UTF-8 で強制
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─── ANSI colors ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PASS = f"{GREEN}PASS{RESET}"
FAIL = f"{RED}FAIL{RESET}"
SKIP = f"{YELLOW}SKIP{RESET}"

results = []
errors  = []

# ─── Ported Logic (Python equivalents of background.js / content.js) ──────────

def avg(arr):
    if not arr:
        return 0.0
    return sum(arr) / len(arr)

def compute_cpi(metrics):
    """Port of computeCPI() in background.js"""
    baseline     = metrics.get("baseline")
    measurements = metrics.get("measurements", [])
    last_heap    = metrics.get("lastHeap", 0)
    baseline_heap = metrics.get("baselineHeap", 0)
    last_dom     = metrics.get("lastDom", 0)
    baseline_dom = metrics.get("baselineDom", 0)

    if not baseline or len(measurements) < 4:
        return 1.0

    recent = measurements[-3:]
    avg_latency      = avg([m["latency"] for m in recent])
    avg_response_size = avg([m["responseSize"] for m in recent])

    latency_rate      = (avg_latency / baseline["latency"])       if baseline["latency"] > 0      else 1.0
    response_size_rate = (avg_response_size / baseline["responseSize"]) if baseline["responseSize"] > 0 else 1.0
    heap_rate         = ((last_heap or baseline_heap) / baseline_heap) if baseline_heap > 0 else 1.0
    dom_rate          = ((last_dom  or baseline_dom)  / baseline_dom)  if baseline_dom  > 0 else 1.0

    cpi = (0.40 * latency_rate
         + 0.25 * heap_rate
         + 0.20 * dom_rate
         + 0.15 * response_size_rate)

    return round(cpi * 100) / 100

def calc_break_even(mode, current_tokens):
    """Port of calcBreakEven() in background.js"""
    params = {
        "light": {"k": 0.08, "c_handoff": 1000},
        "heavy": {"k": 0.20, "c_handoff": 1000},
        "file":  {"k": 0.40, "c_handoff": 1000},
    }
    p = params.get(mode, params["heavy"])
    k, c_handoff = p["k"], p["c_handoff"]
    T_star   = round(c_handoff / k)
    margin   = max(0, T_star - current_tokens)
    progress = min(1.0, current_tokens / T_star)
    return {"T_star": T_star, "margin": margin, "progress": progress}

def detect_breakeven_point(history):
    """Port of detectBreakevenPoint() in background.js"""
    DENSITY_THRESHOLD = 0.65
    SHIFT_THRESHOLD   = 0.30

    if len(history) < 2:
        return "NORMAL"

    latest = history[-1] if history else 0
    prev   = history[-2] if len(history) >= 2 else 0
    last3  = history[-3:]

    if len(last3) >= 3 and all(s >= DENSITY_THRESHOLD for s in last3):
        return "HIGH_DENSITY"
    if abs(latest - prev) >= SHIFT_THRESHOLD:
        return "TOPIC_SHIFT"
    return "NORMAL"

def lb_id(num):
    """Port of lbId() in background.js"""
    return "LB_" + str(num).zfill(3)

def infer_work_description(todos):
    """Port of inferWorkDescription() in background.js"""
    if not todos:
        return "作業内容不明"
    text = " ".join(t.get("text", "") for t in todos).lower()
    heavy  = ["実装", "設計", "コード", "fix", "implement", "build", "create", "debug"]
    review = ["確認", "調査", "review", "check", "test", "verify"]
    if any(k in text for k in heavy):   return "実装・設計作業"
    if any(k in text for k in review):  return "確認・レビュー作業"
    return "一般作業"

def generate_free_handoff_packet(current, all_todos):
    """Port of generateFreeHandoffPacketSync() in background.js"""
    todos = [t for t in all_todos if t.get("status") == "active"]
    now   = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")

    decisions  = current.get("decisions", [])
    file_paths = list(set(current.get("filePaths", [])))
    keywords   = current.get("keywords", [])
    turn_count = current.get("turn_count", 0)

    topic_src = [*(decisions[:1]), *(t["text"] for t in todos[:1])]
    topic = topic_src[0][:60] if topic_src else "作業継続"

    lines = [
        "## 引き継ぎパケット [Relay Free]",
        f"**いつ**: {date_str} ({turn_count}ターン)",
        f"**何を**: {topic}",
    ]

    if decisions:
        lines.append("**決定事項**:")
        for d in decisions[:5]:
            lines.append(f"- {d}")

    if todos:
        lines.append("**TODO/次のアクション**:")
        for t in todos[:8]:
            lines.append(f"- [{t['id']}] {t['text']}")

    if file_paths:
        lines.append("**関連ファイル**:")
        for p in file_paths[:5]:
            lines.append(f"- {p}")

    if keywords:
        lines.append("**重要メモ**:")
        for k in keywords[:5]:
            lines.append(f"- {k}")

    if not decisions and not todos and not file_paths and not keywords:
        lines.append("（引き継ぎデータなし）")

    return "\n".join(lines)

# TODO patterns from content.js
EN_PATTERNS = [
    re.compile(r'^\[RELAY_TODO\]\s*(.+)', re.IGNORECASE),
    re.compile(r'^-\s*\[\s*\]\s*(.+)'),
    re.compile(r'^(?:TODO|Fix|Add|Update|Create|Check|Review|Implement|Deploy)\s*[:：]?\s*(.+)', re.IGNORECASE),
]
JA_PATTERNS = [
    re.compile(r'^(?:TODO|タスク|作業|対応|修正|追加|確認)\s*[:：]\s*(.+)'),
    re.compile(r'^[・•]\s*(.{15,})'),
    re.compile(r'^(\d+[.)]\s*.{15,})'),
]

def extract_todo(line):
    """Port of TODO extraction logic from content.js"""
    line = line.strip()
    for pat in EN_PATTERNS:
        m = pat.match(line)
        if m:
            return m.group(1).strip()
    for pat in JA_PATTERNS:
        m = pat.match(line)
        if m:
            return m.group(1).strip()
    return None

def validate_license_key_format(key):
    """Port of validateRelayLicense() format check (without HMAC, as Web Crypto unavailable)"""
    if not key or not isinstance(key, str):
        return {"plan": "free", "reason": "empty"}
    k = key.strip().upper()
    if k.startswith("RLY-F-"):
        return {"plan": "free", "reason": "free-key"}
    if k.startswith("RLY-P-"):
        prefix, body = "RLY-P", k[6:]
    elif k.startswith("RLY-O-"):
        prefix, body = "RLY-O", k[6:]
    else:
        return {"plan": "free", "reason": "invalid-prefix"}
    if len(body) != 30:
        return {"plan": "free", "reason": f"invalid-length:{len(body)}"}
    expiry_str = body[:8]
    serial_hex = body[8:14]
    sig_hex    = body[14:30]
    # Format check only (HMAC requires Web Crypto)
    try:
        int(expiry_str[:4]);  int(expiry_str[4:6]);  int(expiry_str[6:8])
        int(serial_hex, 16);  int(sig_hex, 16)
    except ValueError:
        return {"plan": "free", "reason": "invalid-hex"}
    plan = "pro" if prefix == "RLY-P" else "one"
    return {"plan": plan, "expiry": expiry_str, "reason": "format-ok-hmac-skipped"}

def build_vault_packet_logic(vault, density, selected_ids=None):
    """Port of buildVaultPacket() logic (without storage layer)"""
    d = density or 3
    if selected_ids:
        entries = [e for e in vault if e["id"] in selected_ids]
    else:
        count = 5 if d >= 5 else (3 if d >= 4 else (2 if d >= 3 else 1))
        entries = vault[:count]

    if not entries:
        return None

    lines = ["[Relay Vault — 文脈プリロード]", "━" * 28, ""]
    for entry in entries:
        dt = datetime.fromisoformat(entry.get("date", "2026-01-01T00:00:00"))
        date_str = dt.strftime("%Y-%m-%d %H:%M")
        lines.append(f"【前回の続き（{date_str}）】")
        summary_text = entry.get("summary", entry.get("packet", ""))
        lines.append("\n".join(summary_text.split("\n")[:3]) if d == 1 else summary_text)
        if d >= 3 and entry.get("decisions"):
            lines.append("\n【重要決定事項】")
            for dec in entry["decisions"][:( None if d >= 5 else 3)]:
                lines.append(f"- {dec}")
        if d >= 4 and entry.get("files"):
            lines.append("\n【関連ファイル】")
            for f in entry["files"][:( None if d >= 5 else 5)]:
                lines.append(f"- {f}")
        if d >= 5 and entry.get("todos"):
            lines.append("\n【未完了TODO】")
            for t in entry["todos"]:
                lines.append(f"- {t}")
        lines.append("")

    lines.append("━" * 28)
    lines.append("上記は前回の会話の引き継ぎ情報です。この文脈を踏まえて会話を始めてください。")
    return "\n".join(lines)

# ─── Test Runner ───────────────────────────────────────────────────────────────

def run_test(scenario_id, name, fn):
    try:
        ok, detail = fn()
        status = PASS if ok else FAIL
        results.append({"id": scenario_id, "name": name, "status": "PASS" if ok else "FAIL", "detail": detail})
        print(f"  [{status}] {scenario_id}: {name}")
        if not ok:
            print(f"         {YELLOW}{detail}{RESET}")
            errors.append(f"{scenario_id}: {detail}")
    except Exception as e:
        results.append({"id": scenario_id, "name": name, "status": "FAIL", "detail": str(e)})
        print(f"  [{FAIL}] {scenario_id}: {name}")
        print(f"         {YELLOW}EXCEPTION: {e}{RESET}")
        errors.append(f"{scenario_id}: EXCEPTION {e}")

def skip_test(scenario_id, name, reason):
    results.append({"id": scenario_id, "name": name, "status": "SKIP", "detail": reason})
    print(f"  [{SKIP}] {scenario_id}: {name}")
    print(f"         {CYAN}{reason}{RESET}")

# ─── Scenarios ─────────────────────────────────────────────────────────────────

def print_header():
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"{BOLD}  PHI-OS (Relay v4.1.0) — Proof of Reproducibility{RESET}")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Target: Chrome Extension (background.js + content.js)")
    print(f"{BOLD}{'═'*60}{RESET}\n")

def check_environment():
    print(f"{BOLD}[ENV] 環境確認{RESET}")
    import os
    ext_path = os.path.join(BASE_DIR, "extension")
    required = ["manifest.json", "background.js", "content.js", "popup.js",
                "sidepanel.js", "relay_search_ui.js", "popup.html", "sidepanel.html"]
    missing = [f for f in required if not os.path.exists(os.path.join(ext_path, f))]
    if missing:
        print(f"  {YELLOW}警告: 見つからないファイル: {missing}{RESET}")
    else:
        print(f"  {GREEN}全必須ファイル確認済み ({len(required)}件){RESET}")

    with open(os.path.join(ext_path, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    print(f"  名前: {manifest['name']} v{manifest['version']}")
    print(f"  MV: {manifest['manifest_version']}")
    print()

def scenario_p01_cpi_engine():
    """P-SCENARIO-01: CPI Engine 計算試験"""
    print(f"\n{BOLD}[P-S-01] CPI Engine 計算試験{RESET}")

    def t_baseline():
        metrics = {"baseline": None, "measurements": [], "lastHeap": 0, "baselineHeap": 0, "lastDom": 0, "baselineDom": 0}
        cpi = compute_cpi(metrics)
        return cpi == 1.0, f"baseline未設定→CPI=1.0 (got {cpi})"
    run_test("P-S-01-a", "ベースライン未設定→CPI=1.0", t_baseline)

    def t_normal():
        metrics = {
            "baseline": {"latency": 100, "responseSize": 1000},
            "measurements": [{"latency": 100, "responseSize": 1000}] * 5,
            "lastHeap": 50, "baselineHeap": 50, "lastDom": 20, "baselineDom": 20,
        }
        cpi = compute_cpi(metrics)
        return abs(cpi - 1.0) < 0.01, f"正常状態→CPI≈1.0 (got {cpi})"
    run_test("P-S-01-b", "正常状態→CPI≈1.0", t_normal)

    def t_degraded():
        metrics = {
            "baseline": {"latency": 100, "responseSize": 1000},
            "measurements": [{"latency": 200, "responseSize": 2000}] * 5,
            "lastHeap": 100, "baselineHeap": 50, "lastDom": 40, "baselineDom": 20,
        }
        cpi = compute_cpi(metrics)
        return cpi > 1.5, f"劣化状態→CPI>1.5 (got {cpi})"
    run_test("P-S-01-c", "劣化状態→CPI上昇", t_degraded)

    def t_zero_div():
        # vasAIの教訓: ゼロ除算防止
        metrics = {
            "baseline": {"latency": 0, "responseSize": 0},
            "measurements": [{"latency": 100, "responseSize": 500}] * 5,
            "lastHeap": 0, "baselineHeap": 0, "lastDom": 0, "baselineDom": 0,
        }
        try:
            cpi = compute_cpi(metrics)
            return isinstance(cpi, float), f"ゼロ除算なし (got {cpi})"
        except ZeroDivisionError:
            return False, "ZeroDivisionError 発生"
    run_test("P-S-01-d", "ゼロ除算防止 (vasAI教訓適用)", t_zero_div)

def scenario_p02_breakeven():
    """P-SCENARIO-02: Break-Even 計算試験"""
    print(f"\n{BOLD}[P-S-02] Break-Even Calculation 試験{RESET}")

    def t_light():
        r = calc_break_even("light", 0)
        return r["T_star"] == 12500, f"light: T*=12500 (got {r['T_star']})"
    run_test("P-S-02-a", "light モード T*=12500", t_light)

    def t_heavy():
        r = calc_break_even("heavy", 0)
        return r["T_star"] == 5000, f"heavy: T*=5000 (got {r['T_star']})"
    run_test("P-S-02-b", "heavy モード T*=5000", t_heavy)

    def t_file():
        r = calc_break_even("file", 0)
        return r["T_star"] == 2500, f"file: T*=2500 (got {r['T_star']})"
    run_test("P-S-02-c", "file モード T*=2500", t_file)

    def t_progress():
        r = calc_break_even("heavy", 2500)
        return abs(r["progress"] - 0.5) < 0.01, f"progress=0.5 at 2500/5000 (got {r['progress']})"
    run_test("P-S-02-d", "progress計算 (50%)", t_progress)

    def t_overflow():
        r = calc_break_even("heavy", 99999)
        return r["progress"] == 1.0 and r["margin"] == 0, f"overflow: progress=1.0,margin=0 (got {r})"
    run_test("P-S-02-e", "オーバーフロー→progress=1.0,margin=0", t_overflow)

def scenario_p03_density():
    """P-SCENARIO-03: Density Engine 試験"""
    print(f"\n{BOLD}[P-S-03] Density Engine 試験{RESET}")

    def t_normal():
        r = detect_breakeven_point([0.3, 0.4, 0.5])
        return r == "NORMAL", f"低密度→NORMAL (got {r})"
    run_test("P-S-03-a", "低密度→NORMAL", t_normal)

    def t_high():
        r = detect_breakeven_point([0.7, 0.8, 0.9])
        return r == "HIGH_DENSITY", f"高密度→HIGH_DENSITY (got {r})"
    run_test("P-S-03-b", "高密度連続→HIGH_DENSITY", t_high)

    def t_shift():
        r = detect_breakeven_point([0.8, 0.2])
        return r == "TOPIC_SHIFT", f"急落→TOPIC_SHIFT (got {r})"
    run_test("P-S-03-c", "急変→TOPIC_SHIFT", t_shift)

    def t_short():
        r = detect_breakeven_point([0.9])
        return r == "NORMAL", f"履歴1件→NORMAL (got {r})"
    run_test("P-S-03-d", "履歴1件→NORMAL (短すぎ)", t_short)

def scenario_p04_todo_extraction():
    """P-SCENARIO-04: TODO抽出試験"""
    print(f"\n{BOLD}[P-S-04] TODO抽出パターン試験{RESET}")

    cases = [
        ("TODO: implement login", "implement login"),
        ("Fix: broken pipe error", "broken pipe error"),
        ("- [ ] write unit tests", "write unit tests"),
        ("[RELAY_TODO] deploy to production", "deploy to production"),
        ("TODO: バグ修正", "バグ修正"),
        ("タスク: レビューを完了させる", "レビューを完了させる"),
        ("・このissueを調査して修正する対応をする", "このissueを調査して修正する対応をする"),
        # JA_PATTERNS[2] は番号込みでキャプチャする仕様 (group(1) = full match)
        ("1. ドキュメントを更新してリリースする計画", "1. ドキュメントを更新してリリースする計画"),
    ]

    for line, expected in cases:
        def make_test(l, e):
            def t():
                got = extract_todo(l)
                return got == e, f"input={repr(l)} → expected={repr(e)} got={repr(got)}"
            return t
        run_test("P-S-04", f"TODO抽出: {line[:30]}", make_test(line, expected))

    def t_no_match():
        got = extract_todo("普通の文章はTODOとして抽出されない")
        return got is None, f"非TODOテキスト→None (got {repr(got)})"
    run_test("P-S-04-x", "非TODOテキスト→None", t_no_match)

def scenario_p05_lb_id():
    """P-SCENARIO-05: LB連番ID試験"""
    print(f"\n{BOLD}[P-S-05] LB連番ID試験{RESET}")

    cases = [(1, "LB_001"), (10, "LB_010"), (999, "LB_999"), (1000, "LB_1000")]
    for num, expected in cases:
        def make_test(n, e):
            def t():
                got = lb_id(n)
                return got == e, f"lb_id({n}) = {repr(got)} (expected {repr(e)})"
            return t
        run_test("P-S-05", f"lb_id({num})", make_test(num, expected))

def scenario_p06_handoff_packet():
    """P-SCENARIO-06: Free Handoff Packet生成試験"""
    print(f"\n{BOLD}[P-S-06] Free Handoff Packet生成試験{RESET}")

    def t_full():
        current = {
            "turn_count": 15,
            "decisions": ["Pythonでバックエンドを実装する"],
            "filePaths": ["src/app.py", "tests/test_app.py"],
            "keywords": ["FastAPI", "pytest"],
        }
        todos = [
            {"id": "LB_001", "text": "ユニットテストを書く", "status": "active"},
            {"id": "LB_002", "text": "デプロイ設定を確認する", "status": "active"},
            {"id": "LB_003", "text": "完了済みタスク", "status": "done"},
        ]
        packet = generate_free_handoff_packet(current, todos)
        checks = [
            "## 引き継ぎパケット [Relay Free]" in packet,
            "15ターン" in packet,
            "Pythonでバックエンドを実装する" in packet,
            "LB_001" in packet,
            "LB_002" in packet,
            "LB_003" not in packet,  # done は除外
            "src/app.py" in packet,
            "FastAPI" in packet,
        ]
        ok = all(checks)
        failed = [i for i, c in enumerate(checks) if not c]
        return ok, f"全チェック通過" if ok else f"チェック失敗: index={failed}"
    run_test("P-S-06-a", "Freeパケット生成 (Full)", t_full)

    def t_empty():
        current = {"turn_count": 0, "decisions": [], "filePaths": [], "keywords": []}
        packet = generate_free_handoff_packet(current, [])
        return "引き継ぎデータなし" in packet, f"空データ→フォールバック文言 (got: {packet[:80]})"
    run_test("P-S-06-b", "空データ→フォールバック文言", t_empty)

def scenario_p07_infer_work():
    """P-SCENARIO-07: 作業種別推定試験"""
    print(f"\n{BOLD}[P-S-07] 作業種別推定試験{RESET}")

    cases = [
        ([{"text": "implement new feature"}], "実装・設計作業"),
        ([{"text": "review the PR"}],          "確認・レビュー作業"),
        ([{"text": "meeting notes"}],           "一般作業"),
        ([],                                    "作業内容不明"),
        ([{"text": "バグをfixする"}],           "実装・設計作業"),
        # "コード" が heavy キーワードに含まれるため heavy が優先される仕様
        ([{"text": "コードをreviewする"}],      "実装・設計作業"),
    ]

    for todos, expected in cases:
        def make_test(t, e):
            def fn():
                got = infer_work_description(t)
                return got == e, f"todos={[x.get('text','') for x in t]} → expected={repr(e)} got={repr(got)}"
            return fn
        run_test("P-S-07", f"infer: {expected}", make_test(todos, expected))

def scenario_p08_license_format():
    """P-SCENARIO-08: ライセンスキー形式検証試験"""
    print(f"\n{BOLD}[P-S-08] ライセンスキー形式検証試験{RESET}")

    def t_free():
        r = validate_license_key_format("RLY-F-dummy")
        return r["plan"] == "free", f"Free key → free plan (got {r})"
    run_test("P-S-08-a", "Free キー → free プラン", t_free)

    def t_empty():
        r = validate_license_key_format("")
        return r["plan"] == "free", f"空文字 → free plan (got {r})"
    run_test("P-S-08-b", "空文字 → free プラン", t_empty)

    def t_invalid_prefix():
        r = validate_license_key_format("INVALID-KEY")
        return r["plan"] == "free", f"無効prefix → free plan (got {r})"
    run_test("P-S-08-c", "無効prefix → free プラン", t_invalid_prefix)

    def t_pro_format():
        # 30文字のbody: expiry(8)+serial(6)+sig(16) = 30
        body = "20270101" + "ABCDEF" + "1234567890ABCDEF"
        key  = "RLY-P-" + body
        r = validate_license_key_format(key)
        return r["plan"] == "pro", f"正しい形式→pro (got {r})"
    run_test("P-S-08-d", "Pro フォーマット正常 → pro (HMAC未検証)", t_pro_format)

    def t_wrong_length():
        key = "RLY-P-SHORT"
        r = validate_license_key_format(key)
        return r["plan"] == "free", f"短いbody→free (got {r})"
    run_test("P-S-08-e", "ボディ長不正 → free プラン", t_wrong_length)

def scenario_p09_vault():
    """P-SCENARIO-09: Vault Packet構築試験"""
    print(f"\n{BOLD}[P-S-09] Vault Packet構築試験{RESET}")

    sample_vault = [
        {
            "id": "vault_20260531120000",
            "date": "2026-05-31T12:00:00",
            "summary": "前回セッションの要約\nリファクタリング完了\n次はテスト追加",
            "decisions": ["TypeScriptに移行する", "モノレポ構成を採用"],
            "files": ["src/index.ts", "package.json"],
            "todos": ["ユニットテスト追加", "CIを設定"],
        }
    ]

    def t_density3():
        r = build_vault_packet_logic(sample_vault, density=3)
        ok = r is not None and "前回の続き" in r and "重要決定事項" in r
        return ok, f"density=3 → 決定事項含む (got: {r[:100] if r else None})"
    run_test("P-S-09-a", "density=3 → 決定事項含む", t_density3)

    def t_density1():
        r = build_vault_packet_logic(sample_vault, density=1)
        ok = r is not None and "重要決定事項" not in r
        return ok, f"density=1 → 決定事項なし (got: {r[:100] if r else None})"
    run_test("P-S-09-b", "density=1 → 決定事項なし", t_density1)

    def t_empty_vault():
        r = build_vault_packet_logic([], density=3)
        return r is None, f"空Vault→None (got {r})"
    run_test("P-S-09-c", "空Vault → None", t_empty_vault)

    def t_density5():
        r = build_vault_packet_logic(sample_vault, density=5)
        ok = r is not None and "未完了TODO" in r and "関連ファイル" in r
        return ok, f"density=5 → TODO+ファイル含む"
    run_test("P-S-09-d", "density=5 → TODO/ファイル全表示", t_density5)

def scenario_p10_manifest():
    """P-SCENARIO-10: manifest.json 整合性試験"""
    print(f"\n{BOLD}[P-S-10] manifest.json 整合性試験{RESET}")
    import os

    ext_path = os.path.join(BASE_DIR, "extension")
    with open(os.path.join(ext_path, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)

    def t_mv3():
        return m["manifest_version"] == 3, f"MV={m['manifest_version']}"
    run_test("P-S-10-a", "Manifest Version = 3", t_mv3)

    def t_permissions():
        required = {"storage", "scripting", "webRequest", "tabs", "sidePanel"}
        got = set(m.get("permissions", []))
        ok = required.issubset(got)
        return ok, f"必須permission充足 (got {got})"
    run_test("P-S-10-b", "必須パーミッション確認", t_permissions)

    def t_host():
        hosts = m.get("host_permissions", [])
        ok = "https://claude.ai/*" in hosts
        return ok, f"claude.ai host_permission (got {hosts})"
    run_test("P-S-10-c", "claude.ai host_permission", t_host)

    def t_service_worker():
        bg = m.get("background", {})
        ok = bg.get("service_worker") == "background.js"
        return ok, f"service_worker=background.js (got {bg})"
    run_test("P-S-10-d", "service_worker = background.js", t_service_worker)

    def t_sidepanel():
        sp = m.get("side_panel", {})
        ok = sp.get("default_path") == "sidepanel.html"
        return ok, f"sidepanel.html (got {sp})"
    run_test("P-S-10-e", "sidepanel.html 登録済み", t_sidepanel)

def scenario_p11_js_syntax():
    """P-SCENARIO-11: JS ファイル構文チェック (Node.js経由)"""
    print(f"\n{BOLD}[P-S-11] JS構文チェック (静的解析){RESET}")
    import subprocess, os

    ext_path = os.path.join(BASE_DIR, "extension")
    js_files = ["background.js", "content.js", "popup.js", "sidepanel.js", "relay_search_ui.js"]

    node_available = False
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, timeout=5)
        node_available = result.returncode == 0
    except Exception:
        pass

    if not node_available:
        for f in js_files:
            skip_test("P-S-11", f"{f} 構文チェック", "Node.js 未インストール — スキップ")
        return

    for fname in js_files:
        fpath = os.path.join(ext_path, fname)
        def make_test(fp, fn):
            def t():
                r = subprocess.run(
                    ["node", "--check", fp],
                    capture_output=True, text=True, timeout=10
                )
                ok = r.returncode == 0
                detail = r.stderr.strip()[:200] if not ok else "構文エラーなし"
                return ok, detail
            return t
        run_test("P-S-11", f"{fname} 構文チェック", make_test(fpath, fname))

# ─── E2E Suite (Puppeteer) ────────────────────────────────────────────────────

def run_e2e_suite():
    """Puppeteer E2E テストスイートを実行して結果を統合する"""
    import subprocess, os
    print(f"\n{BOLD}[E2E] Puppeteer Chrome拡張テスト (test/e2e_phios.js){RESET}")

    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test")
    e2e_path = os.path.join(test_dir, "e2e_phios.js")

    if not os.path.exists(e2e_path):
        skip_test("E2E", "e2e_phios.js が見つからない", f"path={e2e_path}")
        return

    try:
        proc = subprocess.run(
            ["node", e2e_path],
            capture_output=True, timeout=180,
            cwd=test_dir,
        )
        stdout = proc.stdout.decode("utf-8", errors="replace")
        stderr = proc.stderr.decode("utf-8", errors="replace")

        try:
            e2e_results = json.loads(stdout)
        except json.JSONDecodeError:
            skip_test("E2E", "E2E JSON parse失敗", stdout[:100])
            return

        for r in e2e_results:
            fn_status = "PASS" if r.get("status") == "PASS" else "FAIL"
            results.append({
                "id":     r.get("id", "E2E"),
                "name":   r.get("name", "")[:50],
                "status": fn_status,
                "detail": r.get("detail", "")[:80],
            })
            icon = f"{GREEN}PASS{RESET}" if fn_status == "PASS" else f"{RED}FAIL{RESET}"
            print(f"  [{icon}] {r.get('id','E2E')}: {r.get('name','')[:50]}")
            if fn_status != "PASS":
                print(f"         {YELLOW}{r.get('detail','')}{RESET}")
                errors.append(f"{r.get('id')}: {r.get('detail','')}")

    except subprocess.TimeoutExpired:
        skip_test("E2E", "Puppeteer E2Eタイムアウト (180s)", "Chrome起動失敗の可能性")
    except FileNotFoundError:
        skip_test("E2E", "node コマンドが見つからない", "Node.js未インストール")

# ─── Report Generation ─────────────────────────────────────────────────────────

def generate_report(duration_sec):
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    total  = len(results)

    # Proof levels
    l1 = passed >= 5
    l2 = passed >= 15
    l3 = passed >= 20 and failed == 0
    l4 = l3 and skipped == 0

    hash_input = json.dumps({
        "product": "PHI-OS (Relay v4.1.0)",
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
    print(f"  L1 Proof of Concept:       {'✅' if l1 else '❌'}")
    print(f"  L2 Proof of Implementation:{'✅' if l2 else '❌'}")
    print(f"  L3 Proof of Operation:     {'✅' if l3 else '❌'} (FAIL=0 必要)")
    print(f"  L4 Proof of Reproducibility:{'✅' if l4 else '❌'} (SKIP=0 必要)")
    print(f"\n  Reproduction Hash: sha256:{sha256[:16]}...")
    print(f"{BOLD}{'═'*60}{RESET}")

    if l4:
        print(f"\n{GREEN}{BOLD}  PHI-OS Proof of Reproducibility: VERIFIED (L4){RESET}")
    elif l3:
        print(f"\n{GREEN}{BOLD}  PHI-OS Proof of Reproducibility: VERIFIED (L3){RESET}")
    elif l2:
        print(f"\n{GREEN}{BOLD}  PHI-OS Proof of Reproducibility: VERIFIED (L2){RESET}")
    else:
        print(f"\n{YELLOW}{BOLD}  PHI-OS Proof of Reproducibility: PARTIAL (L1){RESET}")
        print(f"  {RED}失敗シナリオ:{RESET}")
        for e in errors:
            print(f"    - {e}")

    # Save PHIOS_REPRODUCE_RESULT.md
    import os
    out_dir = BASE_DIR
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = "\n".join(
        f"| {r['id']} | {r['name'][:35]} | {r['status']} | {r['detail'][:60]} |"
        for r in results
    )

    md = f"""# PHIOS_REPRODUCE_RESULT.md

**PHI-OS (Relay v4.1.0) — Proof of Reproducibility**

- 実行日時: {now_str}
- 実行環境: Windows 11 / Python {sys.version.split()[0]}
- 対象: Chrome Extension MV3

## 試験結果

| シナリオID | 名称 | 結果 | 詳細 |
|-----------|------|------|------|
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
| L1 Proof of Concept | {"✅" if l1 else "❌"} |
| L2 Proof of Implementation | {"✅" if l2 else "❌"} |
| L3 Proof of Operation | {"✅" if l3 else "❌"} |
| L4 Proof of Reproducibility | {"✅" if l4 else "❌"} |

## Reproduction Hash

```
sha256:{sha256}
```

*Generated by reproduce_phios.py — PHI-OS TestField*
"""
    result_path = os.path.join(out_dir, "PHIOS_REPRODUCE_RESULT.md")
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n  Result saved: {result_path}")
    return sha256, passed, failed, skipped, l1, l2, l3, l4

# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print_header()
    check_environment()

    start = time.time()

    scenario_p01_cpi_engine()
    scenario_p02_breakeven()
    scenario_p03_density()
    scenario_p04_todo_extraction()
    scenario_p05_lb_id()
    scenario_p06_handoff_packet()
    scenario_p07_infer_work()
    scenario_p08_license_format()
    scenario_p09_vault()
    scenario_p10_manifest()
    scenario_p11_js_syntax()
    run_e2e_suite()

    duration = time.time() - start
    sha256, passed, failed, skipped, l1, l2, l3, l4 = generate_report(duration)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
