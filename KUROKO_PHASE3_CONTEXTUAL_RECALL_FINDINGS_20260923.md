# Phase 3: Contextual Experience Recall - 発見報告
**2026-09-23 / 実測 3テスト実施**

---

## テスト結果

### TEST A: 既知の関連Decision
**結果: FAIL** ❌

```
Intent: "Decision Ledger adoption and formalization"
Search candidates: 58件 (DC_20260705_001, DC_20260705_002, etc.)
JARVIS returned: HG-REC-2026-PH2834-01-DP5-DECISION-20260912 (最新Active)

Verdict: JARVIS is NOT performing contextual matching
         (just returning latest, regardless of intent)
```

### TEST B: 複数の関連Decision
**結果: PASS** ✓ (ただし偶然)

```
Intent: "Authority boundary and governance framework"
Keywords searched: authority (45), governance (144), gate (191)
Total candidates: 276件
JARVIS returned: HG-REC-2026-PH2834-01-DP5-DECISION-20260912

Verdict: PASS because returned decision IS in candidates
         BUT this is luck, not contextual matching
```

### TEST C: 関連Decisionなし
**結果: PASS** ✓ (known limitation)

```
Intent: "Fictional spacetime engineering decisions"
Search result: 0件 (存在しない)
JARVIS returned: HG-REC-2026-PH2834-01-DP5-DECISION-20260912 (最新Active)

Verdict: JARVIS correctly ignores intent
         Always returns latest regardless
         This is EXPECTED behavior of Phase 2
```

---

## 重大な問題発見

### Phase 2 実装の不十分性

**Phase 2が実装したもの**:
```python
def recall_experience(self, current_intent: str = ""):
    # 1. Decision Ledger 読込
    # 2. Active filters
    # 3. 最新1件を返す
```

**問題: intentパラメータを受け取るが、使用していない**

```python
# 実装内容
def recall_experience(self, current_intent: str = "", context: Dict = None):
    # ↑ intentを受け取るが
    # ↓ 使用していない
    active_decisions.sort(key=lambda x: x.get("decision_id", ""), reverse=True)
    latest = active_decisions[0]  # ← 最新1件を返すだけ
    # intentとの関連性チェックなし
```

### 必要な改善

**Phase 3で追加すべき機能**:
1. intentをキーワードとして解析
2. Decision Ledger内で全文検索
3. intentと関連するDecisionだけを返す

---

## 既存API再利用の可能性

### Option 1: mocka_search() を活用
```python
# 既存APIで全文検索が可能
mocka_search(query=current_intent)
# → eventsと知識ベースを検索
# → Decisionも候補に含めることができるか?
```

**問題**: mocka_search() は events + knowledge_gate を検索
        → Decision Ledger全文検索は別途実装が必要?

### Option 2: Decision Ledger を直接フィルタ (Phase 2改善)
```python
def recall_experience(self, current_intent: str):
    # 1. intentをキーワード分割
    keywords = current_intent.lower().split()
    # 2. Decisionをキーワードで検索フィルタ
    matches = []
    for decision in active_decisions:
        title_text = decision.get("title", "").lower()
        context_text = decision.get("context", "").lower()
        decision_text = decision.get("decision", "").lower()
        
        if any(kw in (title_text + context_text + decision_text) for kw in keywords):
            matches.append(decision)
    # 3. マッチ結果を返す
    return matches
```

**利点**: 新APIなし、既存データのみ
**コスト**: Phase 2の+90行から+20行程度追加

---

## 実装方針の比較

| 方針 | 実装箇所 | 行数 | 新API | 説明 |
|------|--------|------|-------|------|
| **現状(Phase 2)** | engine.py | 90 | 0 | intent無視・最新返す |
| **改善案A** | engine.py | 110 | 0 | 全文検索フィルタ追加 |
| **改善案B** | mocka_mcp_server + engine.py | 150+ | 1 | mocka_decision_search新API |
| **改善案C** | engine.py + interface | 200+ | 1 | 専用検索層作成 |

---

## 推奨実装戦略

**最小性原則に従う** → **改善案A を選択**

### 実装内容
```python
def recall_experience(self, current_intent: str = ""):
    # Phase 2: 最新1件返す
    # + Phase 3: intentで検索フィルタ
    
    if not current_intent:
        # intentなし → Phase 2の動作（最新1件）
        return latest_decision
    
    # intentあり → 関連Decisionを検索
    keywords = current_intent.lower().split()
    matches = []
    for d in active_decisions:
        text = (d.get("title", "") + d.get("context", "") + d.get("decision", "")).lower()
        if any(kw in text for kw in keywords):
            matches.append(d)
    
    if matches:
        # 見つかった → 最新のマッチを返す
        return matches[0]
    else:
        # 見つからない → UNKNOWN/GAP
        return {
            "status": "empty",
            "gap": "EXPERIENCE_GAP"
        }
```

### 実装の最小性
- 新規API: **0** (mocka_decision_search不要)
- 新規DB: **0**
- Trust Score: **0**
- 推薦エンジン: **0**
- 追加行数: ~20行

---

## Phase 2 コードレビュー

### 必須部分
```python
# 1. Decision Ledger パス定義
self._decision_ledger_path = ...  # 必須

# 2. ファイル読込
with open(self._decision_ledger_path) as f:
    for line in f:
        decisions.append(json.loads(line))  # 必須

# 3. Active フィルタ
active = [d for d in decisions if d.get("status") == "Active"]  # 必須

# 4. ソート (最新優先)
active.sort(key=lambda x: x.get("decision_id", ""), reverse=True)  # 必須
```

### 補助部分 (削減可能)
```python
# ← context パラメータは未使用 (削減候補)
# ← "gap" フィールドは冗長 (削減候補)
```

### Phase 2 の+90行の必要度
- **必須**: ~50行 (読込・フィルタ・ソート・返却)
- **補助**: ~40行 (エラーハンドリング、docstring)

**最小コア実装**: 50行
**現在の実装**: 90行
**削減余地**: 40行(エラーハンドリング強化のため意図的)

---

## 次のステップ (Phase 3実装)

### 実装対象
`runtime/jarvis/core/engine.py` の `recall_experience()` メソッド改善

### 追加処理
1. intent パラメータを実際に使用
2. キーワード分割・全文検索フィルタ追加
3. マッチ件数に応じた返却処理

### テスト
- TEST A: 関連Decision取得確認
- TEST B: 複数候補の正しい処理
- TEST C: GAP検知の正確性

---

## 重要な確認事項

**Phase 2 実装でintentを受け取っているのに使用していない理由:**
→ Phase 2は「JARVIS が Decision を読める」ことの実証が目的
→ Contextual matching は Phase 3 の責務に分離した

**Phase 3 で実装する contextual matching:**
→ 既存Decision Ledgerデータだけで実現可能
→ 新API不要 (mocka_decision_search 不要)
→ 最小限の追加コード (~20行)

---

**実装状況**:
- Phase 1: ✓ Experience Source Map確認
- Phase 2: ✓ E2E接続確認(ただし context未対応)
- Phase 3: ⚠ Contextual matching 設計完了、実装待ち

**次の実装**: recall_experience() に intent フィルタを追加
