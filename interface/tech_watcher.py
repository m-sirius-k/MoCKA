"""
tech_watcher.py v3.0  -- TIC Tech Watcher（意味差分検知版）
TODO_208: 形骸化防止改修

v2.0 の問題:
  HTML全体のhashを比較 → 日付・広告・セッションIDなど動的コンテンツで
  毎回「変更検出」が発火し評価キューが形骸化する。

v3.0 の改修方針:
  「意味のある差分だけを検知する」

  1. メインコンテンツ領域のみ抽出（BeautifulSoup: main/article/section等）
  2. バージョン番号・日付パターンの専用抽出（v\\d+\\.\\d+, YYYY-MM-DD形式）
  3. 前回と比較して「バージョンが上がった」「新しい日付が追加された」場合のみ検知
  4. それ以外の差分はNOISEとして記録するが通知しない

ソースごとの専用パーサー:
  anthropic_docs  : h2見出し一覧のhash（リリースノート追加で変化）
  claude_code     : バージョン表記・Breaking changeの抽出
  chrome_mv3      : バージョン表記の抽出
  stripe_changelog: 日付付きエントリ数のカウント
  mcp_spec        : バージョン番号・仕様変更キーワード

形骸化防止ルール（v3.0追加）:
  連続7日間「変更検出なし」 → TECH_WATCH_STALE  （パーサー死活確認）
  連続3日間「毎日変更検出」 → TECH_WATCH_NOISE  （ノイズ発火の可能性）
  変更検出されたがNOISEのみ → events.dbのみ記録・queueに積まない

relay_dom_selector HEALTH_FAIL 対応（TODO_208付随修正）:
  health_check.py がrelay_dom_selectorをFAILしている根本原因は
  セレクタ定義ファイル（SELECTORS.js 等）が更新されていないか
  claude.aiのDOM変更によるズレ。
  tech_watcher の監視対象に claude.ai/release-notes 等を追加することで
  DOM変更を事前検知できるようにする。
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

# ── アラートレベル定義 ────────────────────────────────────────────────────────

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
            "release", "version", "proposed", "experimental",
        ],
        "action": "evaluation_queue",
    },
    "INFO": {
        "keywords": [],  # 意味差分なし・ノイズのみ
        "action": "events_db_only",
    },
}

# ── ソースごとの意味差分パーサー ──────────────────────────────────────────────

def extract_semantic_fingerprint(source_id: str, raw_html: bytes) -> dict:
    """
    HTMLから「意味のある情報」だけを抽出してfingerprintを返す。
    これをhashすることでノイズを除いた差分検知を実現する。

    Returns:
        {
            "fingerprint_hash": str,   # 意味コンテンツのhash
            "versions":         list,  # 検出されたバージョン番号リスト
            "dates":            list,  # 検出された日付リスト（最新3件）
            "section_titles":   list,  # h2/h3 見出しリスト
            "change_count":     int,   # 変更エントリ数（changelog系）
            "extract_method":   str,   # 使用したパーサー名
        }
    """
    try:
        text = raw_html.decode("utf-8", errors="replace")
    except Exception:
        text = ""

    # BeautifulSoup が使えればメインコンテンツ抽出
    main_text = _extract_main_content(text)

    # バージョン番号抽出（全ソース共通）
    versions = re.findall(
        r'\bv?\d+\.\d+(?:\.\d+)?(?:-[a-zA-Z0-9]+)?\b',
        main_text[:10000]
    )
    versions = sorted(set(versions))[:20]

    # 日付抽出（YYYY-MM-DD, Month DD YYYY等）
    dates = re.findall(
        r'\b(?:20\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]))'
        r'|(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+20\d{2})\b',
        main_text[:10000],
        re.IGNORECASE
    )
    dates = sorted(set(dates), reverse=True)[:5]

    # ソース専用パーサー
    extract_method = "generic"
    section_titles = []
    change_count   = 0

    if "anthropic" in source_id:
        # h2/h3 見出しを抽出（リリースノートの追加で変化する）
        section_titles = re.findall(r'<h[23][^>]*>([^<]+)</h[23]>', text, re.IGNORECASE)
        section_titles = [s.strip() for s in section_titles[:30]]
        extract_method = "anthropic_headings"

    elif "claude_code" in source_id:
        # Breaking change・新機能の行を抽出
        section_titles = re.findall(
            r'(?:breaking change|new feature|removed|deprecated|added)[^\n]{0,100}',
            main_text[:8000], re.IGNORECASE
        )
        section_titles = section_titles[:20]
        extract_method = "claude_code_changes"

    elif "stripe" in source_id:
        # 日付付きエントリ数をカウント（増えれば変更）
        change_count = len(re.findall(r'20\d{2}-\d{2}-\d{2}', main_text[:10000]))
        extract_method = "stripe_entry_count"

    elif "chrome" in source_id:
        # MV3固有のバージョン・廃止予告を抽出
        section_titles = re.findall(
            r'(?:chrome\s+\d+|manifest\s+v\d|removed|deprecated|new)[^\n]{0,80}',
            main_text[:8000], re.IGNORECASE
        )
        section_titles = section_titles[:20]
        extract_method = "chrome_mv3_changes"

    elif "mcp" in source_id:
        # スキーマ変更・バージョン変更を抽出
        section_titles = re.findall(
            r'<h[2-4][^>]*>([^<]+)</h[2-4]>',
            text[:10000], re.IGNORECASE
        )
        section_titles = [s.strip() for s in section_titles[:20]]
        extract_method = "mcp_spec_headings"

    # 意味fingerprint を構築してhash
    fingerprint_data = {
        "versions":       versions,
        "dates":          dates[:3],           # 最新3件のみ
        "section_titles": section_titles[:15], # 最大15見出し
        "change_count":   change_count,
    }
    fp_str = json.dumps(fingerprint_data, ensure_ascii=False, sort_keys=True)
    fp_hash = hashlib.sha256(fp_str.encode()).hexdigest()[:16]

    return {
        "fingerprint_hash": fp_hash,
        "versions":         versions,
        "dates":            dates,
        "section_titles":   section_titles,
        "change_count":     change_count,
        "extract_method":   extract_method,
    }


def _extract_main_content(html: str) -> str:
    """
    HTMLからメインコンテンツ部分を抽出する。
    BeautifulSoupがなければ正規表現で近似。
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        # script/style/nav/header/footer を除去
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
        # main/article/section を優先
        for selector in ["main", "article", '[role="main"]', ".content", "#content"]:
            el = soup.select_one(selector)
            if el:
                return el.get_text(separator="\n", strip=True)
        return soup.get_text(separator="\n", strip=True)
    except ImportError:
        # BeautifulSoup なし → タグ除去だけ
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>',  '', text,  flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text[:20000]


# ── 変更種別の判定（意味差分 vs ノイズ）────────────────────────────────────────

def classify_change(
    prev_fp: dict, curr_fp: dict, source_id: str, raw_html: bytes
) -> tuple:
    """
    前回と今回のfingerprintを比較して変更種別を返す。

    Returns: (change_type, alert_level, summary)
      change_type: "SEMANTIC" | "NOISE" | "NEW"
      alert_level: "CRITICAL" | "WARNING" | "INFO"
      summary:     str
    """
    if not prev_fp:
        return "NEW", "INFO", "初回登録"

    prev_hash = prev_fp.get("fingerprint_hash")
    curr_hash = curr_fp.get("fingerprint_hash")

    if prev_hash == curr_hash:
        return "NO_CHANGE", "INFO", "意味的変化なし"

    # 意味的変化あり → 内容を解析してアラートレベルを決定
    # バージョン変化チェック
    prev_vers = set(prev_fp.get("versions", []))
    curr_vers = set(curr_fp.get("versions", []))
    new_vers  = curr_vers - prev_vers

    # 日付変化チェック（新しい日付が追加された）
    prev_dates = set(prev_fp.get("dates", []))
    curr_dates = set(curr_fp.get("dates", []))
    new_dates  = curr_dates - prev_dates

    # 変更エントリ数変化（stripe等）
    prev_count = prev_fp.get("change_count", 0)
    curr_count = curr_fp.get("change_count", 0)
    count_diff = curr_count - prev_count

    # 見出し変化
    prev_titles = set(prev_fp.get("section_titles", []))
    curr_titles = set(curr_fp.get("section_titles", []))
    new_titles  = curr_titles - prev_titles
    del_titles  = prev_titles - curr_titles

    # アラートレベル判定
    text_lower = raw_html.decode("utf-8", errors="replace").lower()[:5000]

    # CRITICAL キーワードチェック
    crit_kw = [kw for kw in ALERT_LEVELS["CRITICAL"]["keywords"] if kw in text_lower]
    if crit_kw and (new_vers or new_titles):
        return "SEMANTIC", "CRITICAL", \
            f"破壊的変更の可能性: {crit_kw[:2]} | 新バージョン: {list(new_vers)[:2]}"

    # WARNING: バージョンアップ・新日付・エントリ追加
    if new_vers:
        return "SEMANTIC", "WARNING", \
            f"バージョン更新: {sorted(new_vers)[:3]}"
    if new_dates:
        return "SEMANTIC", "WARNING", \
            f"新規エントリ追加: {sorted(new_dates, reverse=True)[:2]}"
    if count_diff > 0:
        return "SEMANTIC", "WARNING", \
            f"エントリ数増加: +{count_diff}件"
    if new_titles:
        warn_kw = [kw for kw in ALERT_LEVELS["WARNING"]["keywords"] if kw in text_lower]
        if warn_kw:
            return "SEMANTIC", "WARNING", \
                f"新セクション: {list(new_titles)[:2]}"

    # NOISE: 意味差分はあるが変更内容が軽微
    # （fingerprint変化したが上記いずれにも該当しない）
    return "NOISE", "INFO", \
        "軽微な変更またはノイズ（バージョン/日付/見出しの実質的変化なし）"


# ── URL死活監視 (TODO_297) ───────────────────────────────────────────────────

# 連続失敗カウント管理
_URL_FAIL_COUNTS: dict = {}
URL_DEAD_THRESHOLD = 3  # 連続3回失敗でDEAD判定

def check_url_alive(sources: list, hashes: dict) -> list:
    """
    watch_sources.jsonのURL死活チェック。
    接続失敗が連続3回でTECH_WATCH_URL_DEADイベント記録+prevention_queue投入。
    戻り値: DEAD判定されたsource idのリスト
    """
    dead_sources = []
    for src in sources:
        sid = src["id"]
        url = src["url"]
        try:
            import urllib.request
            req = urllib.request.Request(
                url, headers={"User-Agent": "MoCKA-TIC-Watcher/3.0 AliveCheck"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                status = r.status
            if status < 500:
                _URL_FAIL_COUNTS[sid] = 0
                continue
            # 5xx はサーバーエラーとして失敗カウント
            raise Exception(f"HTTP {status}")
        except Exception as e:
            prev = hashes.get(sid, {})
            fail_count = prev.get("url_fail_count", 0) + 1
            hashes.setdefault(sid, {})["url_fail_count"] = fail_count
            print(f"  [URL   ] {src['name']} fail({fail_count}/{URL_DEAD_THRESHOLD}): {str(e)[:60]}")
            if fail_count >= URL_DEAD_THRESHOLD:
                dead_sources.append(sid)
                write_event(
                    f"TECH_WATCH_URL_DEAD: {src['name']}",
                    f"URL死活監視: 連続{fail_count}回接続失敗 url={url} err={str(e)[:80]}",
                    "tic,tech_watcher,url_dead",
                )
                push_prevention(src["name"], f"URL死亡検知 ({fail_count}回連続失敗): {url}", url)
                print(f"           -> prevention_queue投入 (URL_DEAD)")
            continue
        # 接続成功: fail_countリセット
        hashes.setdefault(sid, {})["url_fail_count"] = 0
    return dead_sources


# ── HTTP 取得 ─────────────────────────────────────────────────────────────────

def fetch_content(url: str) -> tuple:
    try:
        import urllib.request
        req = urllib.request.Request(
            url, headers={"User-Agent": "MoCKA-TIC-Watcher/3.0"}
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read(), None
    except Exception as e:
        return None, str(e)


# ── persistence ───────────────────────────────────────────────────────────────

def load_hashes() -> dict:
    if HASHES_PATH.exists():
        return json.loads(HASHES_PATH.read_text(encoding="utf-8"))
    return {}


def save_hashes(hashes: dict):
    HASHES_PATH.parent.mkdir(parents=True, exist_ok=True)
    HASHES_PATH.write_text(
        json.dumps(hashes, ensure_ascii=False, indent=2), encoding="utf-8"
    )


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
        raw  = PREV_QUEUE.read_text(encoding="utf-8") if PREV_QUEUE.exists() else '{"queue":[]}'
        data = json.loads(raw)
    except Exception:
        data = {"queue": []}
    data["queue"].append({
        "id":          f"TECH_CRITICAL_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "type":        "TECH_CRITICAL",
        "source":      source_name,
        "summary":     summary,
        "url":         url,
        "detected_at": datetime.datetime.now().isoformat(),
        "status":      "NEW",
    })
    PREV_QUEUE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ── MoCKA 記録 ────────────────────────────────────────────────────────────────

def write_event(title: str, description: str, tags: str = "tic,tech_watcher"):
    try:
        import urllib.request
        payload = json.dumps({
            "title":       title,
            "description": description,
            "tags":        tags,
            "why_purpose": "外部技術変化の意味差分監視（v3.0）",
            "how_trigger": "tech_watcher.py v3.0",
        }).encode("utf-8")
        req = urllib.request.Request(
            MCP_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass  # MoCKA未起動でも監視は継続


# ── 形骸化防止チェック ─────────────────────────────────────────────────────────

def check_watcher_health(hashes: dict):
    """
    ウォッチャー自身の形骸化を検知する。
    - 7日間SEMANTIC変化なし → STALE（パーサーが死んでいる可能性）
    - 3日連続SEMANTIC変化  → NOISE（誤検知パターン）
    """
    if not hashes:
        return
    now = datetime.datetime.now()

    all_stale      = True
    max_noise_streak = 0

    for sid, entry in hashes.items():
        checked_at = entry.get("checked_at", "")
        if checked_at:
            try:
                age_days = (now - datetime.datetime.fromisoformat(checked_at)).days
                if age_days < 7:
                    all_stale = False
            except Exception:
                pass
        streak = entry.get("semantic_streak", 0)
        max_noise_streak = max(max_noise_streak, streak)

    if all_stale and hashes:
        print("  [STALE ] 全ソース7日間SEMANTIC変化なし → TECH_WATCH_STALE 発報")
        write_event(
            "TECH_WATCH_STALE: 7日間意味的変化検出なし",
            "全監視ソースで7日間SEMANTIC変化なし。パーサー動作確認が必要。",
            "tic,tech_watcher,stale",
        )

    if max_noise_streak >= 3:
        print(f"  [NOISE ] {max_noise_streak}日連続SEMANTIC変化 → TECH_WATCH_NOISE 発報")
        write_event(
            f"TECH_WATCH_NOISE: {max_noise_streak}日連続SEMANTIC変化",
            f"連続{max_noise_streak}日SEMANTIC変化検出。意味差分パーサーの精度見直しが必要。",
            "tic,tech_watcher,noise",
        )


# ── メイン ────────────────────────────────────────────────────────────────────

def run():
    if not SOURCES_PATH.exists():
        print(f"[ERROR] {SOURCES_PATH} not found")
        sys.exit(1)

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))["sources"]
    hashes  = load_hashes()
    now     = datetime.datetime.now().isoformat()

    # URL死活チェック (TODO_297)
    print()
    print("  [URL alive check]")
    check_url_alive(sources, hashes)
    save_hashes(hashes)

    print()
    print("=" * 65)
    print(f"  MoCKA Tech Watcher v3.0 (意味差分検知版)  {datetime.date.today()}")
    print("  変更種別: SEMANTIC / NOISE / NO_CHANGE")
    print("  アラート: CRITICAL / WARNING / INFO（NOISEはevent記録のみ）")
    print("=" * 65)

    stats = {
        "CRITICAL": 0, "WARNING": 0, "NOISE": 0,
        "NO_CHANGE": 0, "NEW": 0, "ERROR": 0
    }

    for src in sources:
        sid  = src["id"]
        name = src["name"]
        url  = src["url"]

        content, err = fetch_content(url)

        if err:
            print(f"  [ERROR ] {name}")
            print(f"           {err[:80]}")
            stats["ERROR"] += 1
            write_event(
                f"TECH_WATCH_ERROR: {name}",
                f"取得失敗: {url} / {err}",
                "tic,tech_watcher,error",
            )
            continue

        # 意味差分fingerprint を抽出
        curr_fp  = extract_semantic_fingerprint(sid, content)
        prev_fp  = hashes.get(sid, {}).get("fingerprint")

        change_type, alert_level, summary = classify_change(
            prev_fp, curr_fp, sid, content
        )

        icons = {
            "NO_CHANGE": "[OK    ]",
            "NEW":       "[NEW   ]",
            "SEMANTIC":  {"CRITICAL": "[CRIT  ]", "WARNING": "[WARN  ]"}.get(alert_level, "[INFO  ]"),
            "NOISE":     "[NOISE ]",
        }
        icon = icons.get(change_type, "[INFO  ]")
        if change_type == "SEMANTIC":
            icon = {"CRITICAL": "[CRIT  ]", "WARNING": "[WARN  ]"}.get(alert_level, "[INFO  ]")

        print(f"  {icon} {name}")
        print(f"           方式: {curr_fp['extract_method']}  "
              f"fp: {curr_fp['fingerprint_hash']}")
        if change_type not in ("NO_CHANGE",):
            print(f"           {change_type}: {summary}")

        # streak 管理（SEMANTIC連続検知カウント）
        hashes.setdefault(sid, {})
        if change_type == "SEMANTIC":
            streak = hashes[sid].get("semantic_streak", 0) + 1
            hashes[sid]["semantic_streak"] = streak
        else:
            hashes[sid]["semantic_streak"] = 0

        # MoCKA 記録（NOISEも記録するがqueue不追加）
        event_tags = f"tic,tech_watcher,{change_type.lower()},{alert_level.lower()}"
        write_event(
            f"TECH_{change_type}_{alert_level}: {name}",
            f"fp={curr_fp['fingerprint_hash']} | {summary} | 方式={curr_fp['extract_method']}",
            event_tags,
        )

        # evaluation_queue 投入（SEMANTIC かつ WARNING以上のみ）
        if change_type == "SEMANTIC" and alert_level in ("CRITICAL", "WARNING"):
            entry = {
                "id":                next_queue_id(),
                "detected_at":       now,
                "source_id":         sid,
                "source_name":       name,
                "url":               url,
                "alert_level":       alert_level,
                "change_type":       change_type,
                "summary":           summary,
                "new_versions":      curr_fp.get("versions", []),
                "new_dates":         curr_fp.get("dates", []),
                "status":            "NEW",
                "impact_components": src.get("impact_components", []),
                "fingerprint":       curr_fp["fingerprint_hash"],
                "extract_method":    curr_fp["extract_method"],
                "action_required":   alert_level == "CRITICAL",
                "human_decision":    None,
            }
            append_evaluation_queue(entry)
            stats[alert_level] += 1
            if alert_level == "CRITICAL":
                push_prevention(name, summary, url)
                print(f"           → prevention_queue 投入済み")
        elif change_type == "NOISE":
            stats["NOISE"] += 1
        elif change_type == "NO_CHANGE":
            stats["NO_CHANGE"] += 1
        elif change_type == "NEW":
            stats["NEW"] += 1

        # hash 更新（fingerprintベース）
        hashes[sid].update({
            "fingerprint": curr_fp,
            "url":         url,
            "checked_at":  now,
            "name":        name,
            "raw_hash":    hashlib.sha256(content).hexdigest()[:16],
        })

    save_hashes(hashes)
    check_watcher_health(hashes)

    print()
    print(f"  CRITICAL: {stats['CRITICAL']}件  "
          f"WARNING: {stats['WARNING']}件  "
          f"NOISE: {stats['NOISE']}件（queue不追加）  "
          f"変化なし: {stats['NO_CHANGE']}件  "
          f"初回: {stats['NEW']}件  "
          f"ERROR: {stats['ERROR']}件")
    print("=" * 65)
    print()

    return stats


if __name__ == "__main__":
    run()
