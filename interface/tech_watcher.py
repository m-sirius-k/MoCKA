"""
tech_watcher.py v2.0  -- TIC Tech Watcher (3段階アラート分離版)
外部ソースの変更を差分検知し、CRITICAL/WARNING/INFO の3段階で評価する。

アラートレベル定義:
  CRITICAL : API削除・廃止・認証変更・破壊的変更 → prevention_queue + evaluation_queue
  WARNING  : 新バージョン・新機能・非推奨宣言     → evaluation_queue のみ
  INFO     : ドキュメント更新・軽微な変更         → events.db のみ（queue不追加）

自己監視:
  7日間変化なし → TECH_WATCH_STALE 発報
  3日連続変化   → TECH_WATCH_NOISE 発報
"""

import json
import sys
import io
import hashlib
import datetime
import re
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TIC_DIR      = Path("C:/Users/sirok/MoCKA/data/tic")
SOURCES_PATH = TIC_DIR / "watch_sources.json"
HASHES_PATH  = TIC_DIR / "watch_hashes.json"
QUEUE_PATH   = TIC_DIR / "evaluation_queue.jsonl"
PREV_QUEUE   = Path("C:/Users/sirok/MoCKA/data/prevention_queue.json")
MCP_URL      = "http://localhost:5002/agent/mocka_write_event"
TIMEOUT      = 15

# ── アラート定義 ──────────────────────────────────────────────────────────────

ALERT_LEVELS = {
    "CRITICAL": {
        "keywords": [
            "removed", "breaking", "deprecated", "required", "廃止", "削除",
            "incompatible", "no longer supported", "end of life", "breaking change",
        ],
        "action": "prevention_queue + evaluation_queue",
    },
    "WARNING": {
        "keywords": [
            "new", "added", "updated", "improvement", "feature", "追加", "新機能",
            "release", "version", "v1.", "v2.", "v3.", "proposed", "experimental",
        ],
        "action": "evaluation_queue",
    },
    "INFO": {
        "keywords": [],   # それ以外全て
        "action": "events_db_only",
    },
}

PARSERS = {
    "anthropic_api_notes": {
        "extract_pattern": r"(?:v\d+\.\d+|added|removed|deprecated|breaking|new)[^\n]*",
        "critical_keywords": ["removed", "deprecated", "breaking", "required", "廃止", "削除"],
        "warning_keywords":  ["added", "new", "updated", "追加", "新機能"],
    },
    "claude_code_notes": {
        "extract_pattern": r"(?:v\d+\.\d+\.\d+|breaking change|new feature|removed)[^\n]*",
        "critical_keywords": ["breaking change", "removed"],
        "warning_keywords":  ["new feature", "improvement", "added"],
    },
    "chrome_mv3": {
        "extract_pattern": r"(?:removed|deprecated|no longer|new|added|experimental)[^\n]*",
        "critical_keywords": ["removed", "deprecated", "no longer supported"],
        "warning_keywords":  ["new", "added", "experimental"],
    },
    "stripe_changelog": {
        "extract_pattern": r"(?:\d{4}-\d{2}-\d{2}|added|removed|deprecated)[^\n]*",
        "critical_keywords": ["removed", "deprecated", "required"],
        "warning_keywords":  ["new", "added", "updated"],
    },
    "mcp_spec": {
        "extract_pattern": r"(?:breaking|removed|incompatible|new|added|proposed)[^\n]*",
        "critical_keywords": ["breaking", "removed", "incompatible"],
        "warning_keywords":  ["new", "added", "proposed"],
    },
}


# ── アラートレベル判定 ────────────────────────────────────────────────────────

def classify_alert(source_id: str, content: bytes) -> tuple:
    """
    コンテンツを解析してアラートレベルと要約を返す。
    Returns: (level, summary)
    """
    try:
        text = content.decode("utf-8", errors="replace").lower()
    except Exception:
        return "INFO", "コンテンツ解析不可"

    parser = PARSERS.get(source_id, {})
    pattern = parser.get("extract_pattern", "")

    # 抽出テキスト（パターンマッチ部分のみ）
    if pattern:
        matches = re.findall(pattern, text[:5000], re.IGNORECASE)
        extract = " ".join(matches[:10])
    else:
        extract = text[:500]

    # キーワードマッチ
    critical_kw = parser.get("critical_keywords", ALERT_LEVELS["CRITICAL"]["keywords"])
    warning_kw  = parser.get("warning_keywords",  ALERT_LEVELS["WARNING"]["keywords"])

    found_critical = [kw for kw in critical_kw if kw in text[:3000]]
    found_warning  = [kw for kw in warning_kw  if kw in text[:3000]]

    if found_critical:
        summary = f"キーワード検出: {found_critical[:3]}"
        return "CRITICAL", summary
    if found_warning:
        summary = f"変更検出: {found_warning[:3]}"
        return "WARNING", summary

    return "INFO", "軽微な変更またはノイズ"


# ── GitHub / HTTP 取得 ────────────────────────────────────────────────────────

def fetch_content(url: str) -> tuple:
    """URL のコンテンツを取得して (bytes, error_str) を返す"""
    try:
        import urllib.request
        req = urllib.request.Request(
            url, headers={"User-Agent": "MoCKA-TIC-Watcher/2.0"}
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read(), None
    except Exception as e:
        return None, str(e)


def content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


# ── persistence ──────────────────────────────────────────────────────────────

def load_hashes() -> dict:
    if HASHES_PATH.exists():
        return json.loads(HASHES_PATH.read_text(encoding="utf-8"))
    return {}


def save_hashes(hashes: dict):
    HASHES_PATH.parent.mkdir(parents=True, exist_ok=True)
    HASHES_PATH.write_text(json.dumps(hashes, ensure_ascii=False, indent=2), encoding="utf-8")


def next_queue_id() -> str:
    count = 0
    if QUEUE_PATH.exists():
        with open(QUEUE_PATH, encoding="utf-8") as f:
            count = sum(1 for _ in f)
    return f"TQ{(count + 1):03d}"


def append_evaluation_queue(entry: dict):
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def push_prevention(source_name: str, summary: str, url: str):
    PREV_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    try:
        raw = PREV_QUEUE.read_text(encoding="utf-8") if PREV_QUEUE.exists() else '{"queue":[]}'
        data = json.loads(raw)
    except Exception:
        data = {"queue": []}
    data["queue"].append({
        "id": f"TECH_CRITICAL_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "type": "TECH_CRITICAL",
        "source": source_name,
        "summary": summary,
        "url": url,
        "detected_at": datetime.datetime.now().isoformat(),
        "status": "NEW",
    })
    PREV_QUEUE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ── MoCKA 記録 ───────────────────────────────────────────────────────────────

def write_event(title: str, description: str, tags: str = "tic,tech_watcher"):
    try:
        import urllib.request
        payload = json.dumps({
            "title": title, "description": description, "tags": tags,
            "why_purpose": "外部技術変更の3段階差分監視",
            "how_trigger": "tech_watcher.py v2.0",
        }).encode("utf-8")
        req = urllib.request.Request(
            MCP_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass


# ── 自己監視ロジック ──────────────────────────────────────────────────────────

def check_watcher_health(hashes: dict):
    """ウォッチャー自身の健全性チェック"""
    if not hashes:
        return
    now = datetime.datetime.now()
    all_no_change = True
    change_streak = 0

    for sid, entry in hashes.items():
        checked_at = entry.get("checked_at", "")
        if checked_at:
            try:
                age_days = (now - datetime.datetime.fromisoformat(checked_at)).days
                if age_days < 7:
                    all_no_change = False
            except Exception:
                pass
        # streak はchange_countフィールドで追跡（簡易版）
        streak = entry.get("change_streak", 0)
        change_streak = max(change_streak, streak)

    if all_no_change and len(hashes) > 0:
        write_event(
            "TECH_WATCH_STALE: 7日間変化検出なし",
            "全ソースで7日間変化なし。パーサー死活確認が必要。",
            "tic,tech_watcher,stale",
        )
        print("  [STALE ] 7日間変化なし → TECH_WATCH_STALE 発報")

    if change_streak >= 3:
        write_event(
            "TECH_WATCH_NOISE: 3日連続変化検出",
            f"連続{change_streak}日変化検出。ノイズフィルタ見直しが必要。",
            "tic,tech_watcher,noise",
        )
        print(f"  [NOISE ] {change_streak}日連続変化 → TECH_WATCH_NOISE 発報")


# ── メイン ────────────────────────────────────────────────────────────────────

def run():
    if not SOURCES_PATH.exists():
        print(f"[ERROR] {SOURCES_PATH} not found")
        sys.exit(1)

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))["sources"]
    hashes  = load_hashes()
    now     = datetime.datetime.now().isoformat()

    print()
    print("=" * 60)
    print(f"  MoCKA Tech Watcher v2.0  {datetime.date.today()}")
    print("  3段階アラート: CRITICAL / WARNING / INFO")
    print("=" * 60)

    stats = {"CRITICAL": 0, "WARNING": 0, "INFO": 0, "ERROR": 0, "NO_CHANGE": 0}

    for src in sources:
        sid   = src["id"]
        name  = src["name"]
        url   = src["url"]

        content, err = fetch_content(url)

        if err:
            print(f"  [ERROR ] {name}")
            print(f"           {err}")
            stats["ERROR"] += 1
            write_event(
                f"TECH_WATCH_ERROR: {name}",
                f"取得失敗: {url} / {err}",
                "tic,tech_watcher,error",
            )
            continue

        h    = content_hash(content)
        prev = hashes.get(sid, {}).get("hash")

        if prev and prev == h:
            print(f"  [OK    ] {name}  (変更なし, hash: {h})")
            stats["NO_CHANGE"] += 1
            write_event(
                f"TECH_WATCH_OK: {name}",
                f"変更なし hash={h}",
                "tic,tech_watcher,ok",
            )
            # streak リセット
            hashes.setdefault(sid, {})["change_streak"] = 0
        else:
            # 変化あり → アラートレベル判定
            level, summary = classify_alert(sid, content)
            stats[level] += 1

            level_icons = {"CRITICAL": "[CRIT  ]", "WARNING": "[WARN  ]", "INFO": "[INFO  ]"}
            print(f"  {level_icons[level]} {name}")
            if prev:
                print(f"           hash変化: {prev} → {h}")
            else:
                print(f"           初回登録: hash={h}")
            print(f"           {level}: {summary}")

            # streak カウント
            streak = hashes.get(sid, {}).get("change_streak", 0) + 1
            hashes.setdefault(sid, {})["change_streak"] = streak

            # MoCKA 記録
            write_event(
                f"TECH_{level}_DETECTED: {name}",
                f"hash変化 {prev}→{h} | {summary}",
                f"tic,tech_watcher,{level.lower()}",
            )

            # queue 投入（INFO は除外）
            if level in ("CRITICAL", "WARNING"):
                entry = {
                    "id":                next_queue_id(),
                    "detected_at":       now,
                    "source_id":         sid,
                    "source_name":       name,
                    "url":               url,
                    "alert_level":       level,
                    "summary":           summary,
                    "status":            "NEW",
                    "impact_components": src.get("impact_components", []),
                    "prev_hash":         prev,
                    "new_hash":          h,
                    "action_required":   level == "CRITICAL",
                    "risk_score":        None,
                    "sandbox_result":    None,
                    "human_decision":    None,
                }
                append_evaluation_queue(entry)

            # CRITICAL は prevention_queue にも投入
            if level == "CRITICAL":
                push_prevention(name, summary, url)
                print(f"           → prevention_queue 投入済み")

        hashes[sid] = {
            **hashes.get(sid, {}),
            "hash":       h,
            "url":        url,
            "checked_at": now,
            "name":       name,
        }

    save_hashes(hashes)
    check_watcher_health(hashes)

    # サマリー
    print()
    print(f"  CRITICAL: {stats['CRITICAL']}件  WARNING: {stats['WARNING']}件  "
          f"INFO: {stats['INFO']}件  変化なし: {stats['NO_CHANGE']}件  ERROR: {stats['ERROR']}件")
    print("=" * 60)
    print()

    return stats


if __name__ == "__main__":
    run()
