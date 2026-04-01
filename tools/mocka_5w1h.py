import csv
import os
import re
import datetime

EVENTS = r"C:\Users\sirok\MoCKA\data\events.csv"
INCIDENTS_DIR = r"C:\Users\sirok\MoCKA\docs\incidents"

# 失敗パターン定義（Why/How分類）
FAILURE_PATTERNS = [
    {
        "id": "P001",
        "pattern": ["429","RESOURCE_EXHAUSTED","quota","exceeded"],
        "why": "外部API無料枠の上限超過",
        "how": "orchestra経由（Playwright）に切替。APIキー依存を排除する",
        "article": "第6条（入口統合原則）"
    },
    {
        "id": "P002",
        "pattern": ["gemini_state","state.json","OAuth","token","credential"],
        "why": ".gitignore未設定のままgit管理対象にした",
        "how": "生成前に必ず.gitignoreへ追加。secrets/フォルダ運用を徹底する",
        "article": "第2条（秘密情報原則）"
    },
    {
        "id": "P003",
        "pattern": ["router.py","無断変更","rewrite","replaced"],
        "why": "GPT指示書にコアファイル変更禁止が明記されていなかった",
        "how": "GPT_RESTRICTIONS.mdを指示書冒頭に必ず参照させる",
        "article": "第6条（入口統合原則）・第7条（多重監査原則）"
    },
    {
        "id": "P004",
        "pattern": ["format","フォーマット","3列","corrupted"],
        "why": "GPTが独自フォーマットで実装した",
        "how": "events.csvの書き込みはrouter.py経由のみ許可",
        "article": "第6条（入口統合原則）"
    },
    {
        "id": "P005",
        "pattern": ["FAIL","failed","失敗","not found","FileNotFound"],
        "why": "ファイル・パスの存在確認不足",
        "how": "実装前チェックリストでTest-Path確認を義務化",
        "article": "第3条（実装前チェックリスト）"
    }
]

def classify_5w1h(row, reasons):
    """5W1H自動分類"""
    all_text = " ".join(str(v) for v in row.values())
    
    # Who
    who = row.get("who_actor", "不明")
    
    # What
    what = row.get("what_type", "不明")
    
    # When
    when = row.get("when", "不明")
    
    # Where
    where = f"{row.get('where_component','不明')} / {row.get('where_path','不明')}"
    
    # Why・How（パターンマッチ）
    why = "原因不明"
    how = "要手動分析"
    article = "（要確認）"
    pattern_id = "P000"
    
    for p in FAILURE_PATTERNS:
        if any(kw.lower() in all_text.lower() for kw in p["pattern"]):
            why = p["why"]
            how = p["how"]
            article = p["article"]
            pattern_id = p["id"]
            break
    
    return {
        "who": who,
        "what": what,
        "when": when,
        "where": where,
        "why": why,
        "how": how,
        "article": article,
        "pattern_id": pattern_id
    }

def update_incidents_with_5w1h():
    """既存INCファイルに5W1Hを追記"""
    updated = 0
    
    # events.csvからCRITICAL/HIGH行を取得
    critical_rows = {}
    with open(EVENTS, encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            if row.get("risk_level") in ("CRITICAL","HIGH"):
                inc_id = row.get("related_event_id","")
                if inc_id.startswith("INC-"):
                    critical_rows[inc_id] = row

    # INCファイルを更新
    for inc_id, row in critical_rows.items():
        path = os.path.join(INCIDENTS_DIR, f"{inc_id}.md")
        if not os.path.exists(path):
            continue
        
        with open(path, encoding="utf-8") as f:
            content = f.read()
        
        # 既に5W1H追記済みならスキップ
        if "## 5W1H分析" in content:
            continue
        
        w5h1 = classify_5w1h(row, [])
        
        analysis = "\n".join([
            "",
            "## 5W1H分析（自動生成）",
            f"- **Who（誰が）**: {w5h1['who']}",
            f"- **What（何を）**: {w5h1['what']}",
            f"- **When（いつ）**: {w5h1['when']}",
            f"- **Where（どこで）**: {w5h1['where']}",
            f"- **Why（なぜ）**: {w5h1['why']}",
            f"- **How（どう防ぐ）**: {w5h1['how']}",
            "",
            f"## パターン分類",
            f"- ID: {w5h1['pattern_id']}",
            f"- 憲章違反条項: {w5h1['article']}",
            "",
            f"## 自動分析日時",
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ])
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content + analysis)
        
        print(f"[5W1H追記] {inc_id} → {w5h1['pattern_id']}: {w5h1['why'][:40]}")
        updated += 1
    
    print(f"[完了] {updated}件のINCに5W1H追記")

if __name__ == "__main__":
    print("=" * 50)
    print("MoCKA 5W1H自動分類エンジン")
    print(f"実行時刻: {datetime.datetime.now()}")
    print("=" * 50)
    update_incidents_with_5w1h()
    print("=" * 50)
