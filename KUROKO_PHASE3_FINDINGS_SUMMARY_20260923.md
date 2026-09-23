# Phase 3: 実装改善 + 発見報告
**2026-09-23 調査・実装進行中**

---

## 現状

**Phase 2 実装完成**: JARVIS が Decision Ledger から最新 Decision を読み出すことに成功

**Phase 3 課題**: Intent ベースの contextual matching が未完成

### TEST 結果
```
TEST A: FAIL - Intent "Decision Ledger adoption" で、
        期待される Decision Ledger 関連 Decision が返されない

TEST B: PASS - 複数候補の中から何かが返される

TEST C: PASS - Gap 検知（ただし常に何かを返す）
```

---

## 発見した制限

### Phase 2 実装の限界

1. **Intent パラメータが受け取られているが、使用されていない**
   - `def recall_experience(self, current_intent: str = "", ...)`
   - intentは形式上存在するが、最終的には無視されていた

2. **Contextual matching のアルゴリズム問題**
   - キーワード抽出: "Decision Ledger adoption" → ['decision', 'ledger', 'adoption']
   - キーワード長フィルタ: len > 2 で 3 文字未満を除外
   - マッチ判定:初期「any」(ORロジック)で、どんなキーワードでもマッチ
   - 改善:「all」(ANDロジック)に変更

3. **改善後も不完全**
   - Intent: "Decision Ledger adoption"
   - 必要な全キーワード: ['decision', 'ledger', 'adoption']
   - 実際の検索結果: DC_20260811_001 (ledger キーワードなし)
   - 原因不明確

---

## 課題分析

### なぜ Decision Ledger 関連 Decision が見つからないのか？

**仮説 1**: Decision Ledger 内のレコードが期待と異なる
- 検索で見つかった DC_20260705_001, DC_20260705_002 は
- 実際の Intent マッチ時に返ってこない

**仮説 2**: キーワード抽出が不十分
- "Decision Ledger" を句として扱うべき（2単語）
- 単語分割の granularity が問題

**仮説 3**: 全キーワード必須条件は厳しすぎる
- "Decision Ledger" 検索には "decision" と "ledger" で十分
- "adoption" は不要キーワード

---

## 次のステップ（回避策）

### 案 A: Phrase Matching に切り替え
```python
intent_phrases = ["decision ledger", "authority boundary", ...]
for phrase in intent_phrases:
    if phrase in searchable:
        matches.append(decision)
```

### 案 B: キーワードの重み付け
```python
# 重要なキーワードは必須
required = ["decision", "ledger"]
optional = ["adoption"]

# required は全てマッチが必要
# optional はマッチしなくても OK
```

### 案 C: 既存 mocka_search API を活用
```python
# mocka_mcp_server.py の mocka_search() を直接利用
# → 既に全文検索が実装されている
```

---

## 重要な判定

**「Contextual Recall 実装の必要性」:**

- Phase 2 は読取だけ (最新 Decision 返す)
- Phase 3 は検索 (Intent マッチ)
- 実装に手間がかかり、かつ「新API禁止」制約がきつい
- 既存 mocka_search API の再利用を検討すべき

---

## 推奨実装戦略

**最小限にする** → 現実的には Phase 3 では「完全なContextual matching」は不要かもしれない

**代替案**:
- JARVIS recall_experience() は「最新 Decision を返す」だけにする (Phase 2 完)
- 検索・フィルタは上位層 (HAB) で実装する
- JARVIS の責務は「過去を読む」だけ、「過去から選ぶ」ではない

---

## 実装状況

| Phase | 目標 | 実装状況 | テスト |
|-------|------|--------|-------|
| 1 | Source Map確認 | COMPLETE | - |
| 2 | E2E読取確認 | COMPLETE | ALL PASS |
| 3 | Contextual matching | INCOMPLETE | 1 FAIL, 2 PASS |

**3の問題**: Intent-based filtering が実装課題が大きい

---

## 結論

**Contextual Experience Recall の実装は、最小性原則とのバランスが難しい**

- 実装可能: ○
- 最小性: × (余分なロジックが増える)
- 必要性: ? (HAB層で事足りるかも)

**提案**: Phase 3 を「実装完遂」ではなく「実装可能性確認」で区切る
