# Personal Lexicon v1

> 「正しさ」ではなく「納得」を保存する辞書

---

## これは何か

きむら博士個人の意味安定辞書。  
PHI-OSでもMoCKAでもない。**思考補助装置**である。

システムに最適化された定義ではなく、  
**自分が今この瞬間に納得している意味**を固定する場所。

---

## 設計原則

| 原則 | 理由 |
|------|------|
| 意味は1つに固定（多義禁止） | 揺れがあれば別の用語を作る |
| バージョン管理なし | 常に最新理解だけが有効 |
| 上書き型 | 理解が変わったら即更新 |
| 外部依存なし | sqlite3標準のみ。どこでも動く |
| PHI-OS・MoCKAとの連携なし | 人間の意味空間はシステムから独立する |

---

## ファイル構成

```
personal_lexicon/
    personal_lexicon.py   — 本体
    personal_lexicon.db   — SQLite（初回起動時に自動生成）
    README.md             — 本ファイル
```

---

## 使い方

### Pythonモジュールとして

```python
from personal_lexicon import PersonalLexicon

db = PersonalLexicon()

# 登録（上書き型）
db.add_term("Semantic Gravity", "意味が安定している度合い。高いほど揺れにくい")
db.add_term("Drift",            "意味が元の定義から離れていく現象",
            note="Driftedステータスのトリガー", category="PHI-OS")

# 取得
entry = db.get("Drift")
print(entry["meaning"])

# 一覧
db.show_all()                    # 全件
db.show_all(category="PHI-OS")  # カテゴリ絞り込み

# 削除
db.delete_term("Drift")

db.close()
```

### CLIとして

```bash
# 登録
python personal_lexicon.py add "Event" "状態変化の記録単位" "5W1Hを保存する" "MoCKA"

# 取得
python personal_lexicon.py get "Event"

# 一覧
python personal_lexicon.py list
python personal_lexicon.py list MoCKA   # カテゴリ絞り込み

# 削除
python personal_lexicon.py delete "Event"
```

---

## DBスキーマ

```sql
CREATE TABLE personal_terms (
    term       TEXT PRIMARY KEY,
    meaning    TEXT NOT NULL,
    note       TEXT,
    category   TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

---

## 運用ルール

1. **思いついたら即登録** — 「あとで整理」はしない
2. **意味が変わったら即上書き** — 旧定義は残さない
3. **迷ったら削除** — 納得できない語彙は辞書に置かない
4. **カテゴリは任意** — MoCKA / PHI-OS / 日常 / 研究 など自由に
5. **補足（note）は使い方の文脈を書く** — 定義の延長ではなく「どう使うか」
6. **PHI-OS辞書と混同しない** — あちらはシステムの辞書。こちらは人間の辞書

---

## このファイルが属する場所

```
MoCKA/               — 制度核（システム）
PHI-OS/              — 語彙コア（システム）
personal_lexicon/    — 思考補助装置（人間）← ここ
```

*記録: E20260616_092 / 2026-06-16*
