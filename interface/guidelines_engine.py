"""
MoCKA Guidelines Engine v1.0
============================
蓄積データ → 行動指針 への変換パイプライン

処理フロー:
  events.db (user_voice / INCIDENT / MATAKA)
    ↓ [Phase 1] 収集フィルタ: 思想・判断文のみ選別
    ↓ [Phase 2] 5W1H因果抽出
    ↓ [Phase 3] 否定5W1H生成（防止策）
    ↓ [Phase 4] guidelines.json へAND蓄積
    ↓ [Phase 5] lever_essence.json PHILOSOPHY軸へ注入

配置先: C:\\Users\\sirok\\MoCKA\\interface\\guidelines_engine.py
実行: python interface/guidelines_engine.py
"""

import sqlite3
import json
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# 設定
# ============================================================
MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
DB_PATH    = MOCKA_ROOT / "mocka_events.db"
GUIDELINES = MOCKA_ROOT / "data" / "guidelines.json"
ESSENCE    = MOCKA_ROOT / "data" / "lever_essence.json"
PROCESSED  = MOCKA_ROOT / "data" / "guidelines_processed.json"

# ============================================================
# Phase 1: 収集フィルタ
# 「きむら博士の思想・判断文」を選別するルール
# ============================================================

# 除外パターン（ノイズ）
NOISE_PATTERNS = [
    r"^PS C:\\",                          # PowerShellプロンプト
    r"^StatusCode\s*:",                   # HTTP応答
    r"background\.js:\d+",               # JSエラー
    r"^\d+$",                             # 数字のみ
    r"^https?://",                        # URL
    r"Access-Control-Allow-Origin",       # CORSエラー
    r"net::ERR_",                         # ネットワークエラー
    r"Enumerating objects",               # git出力
    r"Writing objects",                   # git出力
    r"document\.querySelector",          # JSコード
    r"^\{\"event_id\"",                   # JSONレスポンス
    r"^StatusDescription",               # HTTP
    r"RawContent\s*:",                    # HTTP
    r"Content-Type:",                     # HTTPヘッダ
    r"VM\d+:\d+",                         # Chrome内部
    r"DIV font-sans",                     # DOM要素
    r"impamkj",                           # 拡張ID
    r"cloudflareaccess\.com",            # Cloudflare
]

# 採用パターン（きむら博士の思想・判断シグナル）
THOUGHT_SIGNALS = [
    # 疑問・探求
    r"なぜ|どうして|なんで|なんで|どうやって|どういう",
    r"これって|どう思|どう考",
    r"問題|課題|懸念|疑問",
    # 判断・指示
    r"こうしよう|やろう|改善|変更|修正",
    r"違う|ちがう|そうじゃない|そこはない",
    r"これで|これが|これは",
    # 発見・気づき
    r"わかった|気づ|発見|なるほど",
    r"そうか|そういう|そういうこと",
    # 評価・感情
    r"いいね|グレート|ヒント|うまい",
    r"ダメ|だめ|おかしい|間違",
    r"また|再発|繰り返|何度も",
    # 構想・設計
    r"設計|構想|考え|思想|方針|指針",
    r"mocka|MoCKA|caliber|essence|PHL|SPP",
    # 確認・要求
    r"確認|見て|調べて|教えて",
    r"どこ|いつ|誰が|何が|なぜ",
]

NOISE_RE  = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]
SIGNAL_RE = [re.compile(p, re.IGNORECASE) for p in THOUGHT_SIGNALS]

# 5W1H インシデント分類キーワード
INCIDENT_KEYWORDS = {
    "INCIDENT":  ["インシデント", "エラー", "失敗", "問題", "バグ", "壊れ", "動かない",
                  "文字化け", "UTF", "cp932", "Shift-JIS", "403", "500", "CRITICAL"],
    "MATAKA":    ["またか", "また同じ", "再発", "繰り返", "何度も", "また間違", "また忘れ"],
    "DECISION":  ["決定", "採択", "承認", "方針", "確定", "これで行く", "こうする"],
    "INSIGHT":   ["わかった", "気づ", "発見", "なるほど", "そういうことか", "ヒント", "グレート"],
    "CHALLENGE": ["違う", "そうじゃない", "おかしい", "ダメ", "問題がある", "なぜ"],
}

def is_noise(text: str) -> bool:
    """ノイズ（ターミナル出力・エラーログ等）を検出"""
    if not text or len(text.strip()) < 4:
        return True
    for p in NOISE_RE:
        if p.search(text):
            return True
    return False

def has_thought_signal(text: str) -> bool:
    """きむら博士の思想・判断シグナルを検出"""
    for p in SIGNAL_RE:
        if p.search(text):
            return True
    return False

def classify_event(text: str) -> str:
    """イベントを5W1H分類に振り分け"""
    for category, keywords in INCIDENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return category
    return "GENERAL"

def score_voice(text: str) -> float:
    """思想スコア算出 (0.0-1.0)"""
    if is_noise(text):
        return 0.0
    score = 0.0
    signal_count = sum(1 for p in SIGNAL_RE if p.search(text))
    score += min(signal_count * 0.15, 0.6)
    # 長さボーナス（適切な長さの発言を優遇）
    l = len(text)
    if 10 <= l <= 200:
        score += 0.2
    elif 200 < l <= 500:
        score += 0.1
    # インシデント分類ボーナス
    cat = classify_event(text)
    if cat in ("INCIDENT", "MATAKA"):
        score += 0.3
    elif cat in ("DECISION", "INSIGHT", "CHALLENGE"):
        score += 0.2
    return min(score, 1.0)

# ============================================================
# Phase 2: events.db からデータ取得
# ============================================================

def fetch_events(db_path: Path, limit: int = 2000) -> list[dict]:
    """events.db から全イベントを取得"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # user_voice + INCIDENT系 + MATAKAを取得
    cur.execute("""
        SELECT event_id, when_ts, who_actor, what_type,
               title, short_summary, free_note,
               why_purpose, how_trigger, risk_level,
               recurrence_flag
        FROM events
        WHERE what_type IN ('user_voice','incident','mataka','claim','record','decision')
           OR recurrence_flag = 1
           OR risk_level IN ('WARNING','CRITICAL','DANGER')
        ORDER BY when_ts DESC
        LIMIT ?
    """, (limit,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def load_processed(path: Path) -> set:
    """処理済みイベントIDをロード（重複スキップ用）"""
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return set(data.get("processed_ids", []))
    return set()

def save_processed(path: Path, ids: set):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"processed_ids": list(ids), "updated": datetime.now(timezone.utc).isoformat()},
                   ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

# ============================================================
# Phase 3: 5W1H 因果抽出 + 否定5W1H（防止策）生成
# ============================================================

def extract_5w1h(text: str, event: dict) -> dict:
    """テキストから5W1H構造を抽出"""
    category = classify_event(text)

    # WHO: actor判定
    who = event.get("who_actor", "kimura")
    if "Claude" in text or "claude" in text:
        who = "Claude"
    elif "Gemini" in text or "gemini" in text:
        who = "Gemini"

    # WHAT: カテゴリから推定
    what_map = {
        "INCIDENT":  "問題・障害の発生",
        "MATAKA":    "同一パターンの再発",
        "DECISION":  "方針・判断の確定",
        "INSIGHT":   "新たな気づき・発見",
        "CHALLENGE": "現状への疑問・異議",
        "GENERAL":   "発言・記録",
    }
    what = what_map.get(category, "記録")

    # WHEN: タイムスタンプ
    when = event.get("when_ts", "")[:10]

    # WHERE: コンポーネント
    where = event.get("where_component") or "claude.ai"

    # WHY: テキストから疑問・原因を抽出
    why_patterns = [
        r"なぜ(.{0,50})[？?。\n]",
        r"なんで(.{0,50})[？?。\n]",
        r"問題は(.{0,50})[。\n]",
        r"原因は(.{0,50})[。\n]",
    ]
    why = "不明"
    for p in why_patterns:
        m = re.search(p, text)
        if m:
            why = m.group(1).strip()
            break

    # HOW: トリガー
    how = event.get("how_trigger") or "manual"

    return {
        "who": who,
        "what": what,
        "when": when,
        "where": where,
        "why": why,
        "how": how,
        "category": category,
        "source_text": text[:200],
    }

def generate_prevention(w5h1: dict, text: str) -> dict:
    """否定の5W1H（防止策）を生成"""
    cat = w5h1["category"]

    # カテゴリ別の防止策テンプレート
    prevention_templates = {
        "INCIDENT": {
            "who":   "Claude（執行官）+ きむら博士（確認）",
            "what":  "同一インシデントの再発を防止する",
            "when":  "次回同一状況に遭遇した時点で即時",
            "where": "発生コンポーネントの上流で検知",
            "why":   "「{why}」という状況が再現しないよう制度化する",
            "how":   "prevention_queueに登録 → Human Gate承認 → essence INCIDENT軸に記録",
        },
        "MATAKA": {
            "who":   "Claudeが自律的に",
            "what":  "再発パターンをdanger_patterns.jsonに追記し自動検知",
            "when":  "同一パターン検知時に即座に",
            "where": "language_detector / morphology_engine",
            "why":   "「{why}」の繰り返しをシステムレベルで封じる",
            "how":   "mataka_count ≥ 3 → auto_escalate → COMMAND CENTER警告",
        },
        "DECISION": {
            "who":   "MoCKAシステム全体",
            "what":  "この判断を行動指針として記録・継承する",
            "when":  "類似状況が発生した時に自動参照",
            "where": "guidelines.json + essence PHILOSOPHY軸",
            "why":   "「{why}」という判断の根拠を未来のAIに継承する",
            "how":   "guidelines.jsonにAND追加 → PHL注入で次セッションから有効",
        },
        "INSIGHT": {
            "who":   "Claude（次セッション以降）",
            "what":  "この気づきを知識として活用する",
            "when":  "関連状況で常に",
            "where": "essence PHILOSOPHY軸",
            "why":   "「{why}」という洞察をMoCKAの知的資産にする",
            "how":   "guidelines.jsonに追記 → essence PHILOSOPHY更新",
        },
        "CHALLENGE": {
            "who":   "Claude（執行官）",
            "what":  "この異議・指摘を反映した動作に修正する",
            "when":  "次回同一タスク実行時",
            "where": "実行経路の上流",
            "why":   "「{why}」という問題を繰り返さない",
            "how":   "action_guidelineとして登録 → セッション開始時に読み込む",
        },
        "GENERAL": {
            "who":   "Claude",
            "what":  "この記録を参照可能な状態に維持する",
            "when":  "必要時",
            "where": "guidelines.json",
            "why":   "蓄積した経験を活用するため",
            "how":   "AND追記",
        },
    }

    tmpl = prevention_templates.get(cat, prevention_templates["GENERAL"])
    result = {}
    for k, v in tmpl.items():
        result[k] = v.format(why=w5h1.get("why", "不明"))
    return result

# ============================================================
# Phase 4: guidelines.json への AND蓄積
# ============================================================

def load_guidelines(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "meta": {
            "version": "1.0",
            "description": "MoCKA行動指針 — 蓄積データから生成された知識ベース",
            "philosophy": "失敗は資産になる / ここに至る経緯を理解せよ",
            "created": datetime.now(timezone.utc).isoformat(),
        },
        "guidelines": [],
        "summary": {
            "total": 0,
            "by_category": {},
            "last_updated": "",
        }
    }

def save_guidelines(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    # サマリ更新
    cats = {}
    for g in data["guidelines"]:
        c = g.get("category", "GENERAL")
        cats[c] = cats.get(c, 0) + 1
    data["summary"]["total"] = len(data["guidelines"])
    data["summary"]["by_category"] = cats
    data["summary"]["last_updated"] = datetime.now(timezone.utc).isoformat()

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def guideline_exists(guidelines: list, fingerprint: str) -> bool:
    """フィンガープリントで重複チェック"""
    return any(g.get("fingerprint") == fingerprint for g in guidelines)

def add_guideline(guidelines_data: dict, w5h1: dict, prevention: dict,
                  source_event_id: str, score: float) -> bool:
    """行動指針をAND追加"""
    # フィンガープリント生成（重複防止）
    fp_src = f"{w5h1['category']}:{w5h1['source_text'][:80]}"
    fingerprint = hashlib.md5(fp_src.encode()).hexdigest()[:12]

    if guideline_exists(guidelines_data["guidelines"], fingerprint):
        return False  # 重複スキップ

    entry = {
        "id": f"GL_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{fingerprint}",
        "fingerprint": fingerprint,
        "category": w5h1["category"],
        "score": round(score, 3),
        "source_event_id": source_event_id,
        "created": datetime.now(timezone.utc).isoformat(),
        "verified": False,
        "trust_score": score,
        # 因果5W1H（何が起きたか）
        "cause_5w1h": w5h1,
        # 防止5W1H（どう防ぐか）
        "prevention_5w1h": prevention,
        # 行動指針（1行サマリ）
        "action_directive": _make_directive(w5h1, prevention),
    }

    guidelines_data["guidelines"].append(entry)
    return True

def _make_directive(w5h1: dict, prevention: dict) -> str:
    """行動指針を1行で表現"""
    cat = w5h1["category"]
    directives = {
        "INCIDENT":  f"【防止】{w5h1['where']}で発生した問題: {w5h1['source_text'][:60]}… → {prevention['how']}",
        "MATAKA":    f"【再発警告】{w5h1['source_text'][:60]}… は繰り返しパターン → 自動検知を強化せよ",
        "DECISION":  f"【継承】判断: {w5h1['source_text'][:60]}… → {prevention['how']}",
        "INSIGHT":   f"【知恵】{w5h1['source_text'][:60]}… → essence PHILOSOPHYに記録",
        "CHALLENGE": f"【是正】{w5h1['source_text'][:60]}… → {prevention['how']}",
        "GENERAL":   f"【記録】{w5h1['source_text'][:80]}",
    }
    return directives.get(cat, directives["GENERAL"])

# ============================================================
# Phase 5: lever_essence.json PHILOSOPHY軸へ注入
# ============================================================

def inject_to_essence(essence_path: Path, guidelines_data: dict):
    """guidelines の上位指針を essence PHILOSOPHY 軸に注入"""
    if not essence_path.exists():
        print(f"[WARN] essence not found: {essence_path}")
        return

    essence = json.loads(essence_path.read_text(encoding="utf-8"))

    # スコア上位5件の行動指針を抽出
    top5 = sorted(
        guidelines_data["guidelines"],
        key=lambda g: g.get("score", 0),
        reverse=True
    )[:5]

    if not top5:
        return

    # PHILOSOPHY軸に追記
    inject_lines = []
    for g in top5:
        inject_lines.append(f"[GL:{g['category']}] {g['action_directive'][:100]}")

    inject_text = "\n".join(inject_lines)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    current_phil = essence.get("PHILOSOPHY", "")
    # 既存のGL注入を除去して新しいものを追加
    lines = [l for l in current_phil.split("\n") if not l.startswith("[GL:")]
    lines.append(f"[{now}] Guidelines Engine v1.0 — 行動指針TOP5:")
    lines.extend(inject_lines)

    # 最大20行に抑える
    essence["PHILOSOPHY"] = "\n".join(lines[-20:])
    essence_path.write_text(
        json.dumps(essence, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"[OK] essence PHILOSOPHY更新: {len(top5)}件注入")

# ============================================================
# メイン実行
# ============================================================

def run(score_threshold: float = 0.35, max_new: int = 200):
    print("=" * 60)
    print("MoCKA Guidelines Engine v1.0")
    print("=" * 60)

    # DB確認
    if not DB_PATH.exists():
        print(f"[ERROR] DB not found: {DB_PATH}")
        return

    # 処理済みIDロード
    processed_ids = load_processed(PROCESSED)
    print(f"[INFO] 処理済みイベント: {len(processed_ids)}件")

    # events.db から取得
    events = fetch_events(DB_PATH)
    print(f"[INFO] 取得イベント数: {len(events)}件")

    # guidelines.json ロード
    guidelines_data = load_guidelines(GUIDELINES)
    existing = len(guidelines_data["guidelines"])
    print(f"[INFO] 既存行動指針: {existing}件")

    new_count = 0
    skip_noise = 0
    skip_low   = 0
    skip_dup   = 0

    for ev in events:
        if new_count >= max_new:
            break

        eid = ev.get("event_id", "")
        if eid in processed_ids:
            skip_dup += 1
            continue

        # テキスト抽出（title > free_note > short_summary の優先順）
        text = (ev.get("title") or ev.get("free_note") or ev.get("short_summary") or "").strip()

        if not text:
            processed_ids.add(eid)
            continue

        # Phase 1: フィルタ
        if is_noise(text):
            skip_noise += 1
            processed_ids.add(eid)
            continue

        # スコアリング
        score = score_voice(text)
        if score < score_threshold:
            skip_low += 1
            processed_ids.add(eid)
            continue

        # Phase 2: 5W1H抽出
        w5h1 = extract_5w1h(text, ev)

        # Phase 3: 防止策生成
        prevention = generate_prevention(w5h1, text)

        # Phase 4: AND追加
        added = add_guideline(guidelines_data, w5h1, prevention, eid, score)
        if added:
            new_count += 1
            print(f"  [+] {w5h1['category']:10s} score={score:.2f} | {text[:50]}…")

        processed_ids.add(eid)

    # 保存
    save_guidelines(GUIDELINES, guidelines_data)
    save_processed(PROCESSED, processed_ids)

    # Phase 5: essence注入
    inject_to_essence(ESSENCE, guidelines_data)

    # レポート
    print()
    print("=" * 60)
    print(f"  新規追加行動指針 : {new_count}件")
    print(f"  ノイズ除外       : {skip_noise}件")
    print(f"  低スコア除外     : {skip_low}件")
    print(f"  重複スキップ     : {skip_dup}件")
    print(f"  合計行動指針数   : {len(guidelines_data['guidelines'])}件")
    print()
    print("  カテゴリ別:")
    for cat, cnt in guidelines_data["summary"]["by_category"].items():
        print(f"    {cat:12s}: {cnt}件")
    print("=" * 60)
    print(f"[OK] guidelines.json → {GUIDELINES}")
    print(f"[OK] essence PHILOSOPHY → {ESSENCE}")


if __name__ == "__main__":
    run()
