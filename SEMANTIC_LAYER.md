# Semantic Layer (Phase 2-1)

## 目的

MoCKAに「意味を理解する能力」を追加する。Governance Layer(GL1-7)が
担う安全性・制度・実行可否・品質保証とは責務を分離し、Semantic Layerは
「利用者の意図」「文脈」「意味」のみを扱う。

判断(実行可否)・記憶(永続化)・実行は本フェーズの対象外であり、
将来のDecision Layer / Memory Layerに委ねる。

## 全体構造

```
semantic/
    semantic_registry.py     — Intentカテゴリの一元管理(Single Source of Truth)
    intent_classifier.py     — テキストをIntentへ分類(複数候補+確信度)
    context_analyzer.py      — フェーズ/Active Task/直前イベント等から意味情報を補完
    semantic_result.py        — 統一出力形式(SemanticResult / ContextSummary)
    semantic_pipeline.py      — 上記を統合する単一窓口
    semantic_integration_test.py — 統合テスト
    semantic_sample_cases.py  — テスト用サンプルケース
```

## データフロー

```
                +----------------------+
  text -------> | IntentClassifier     | --> IntentMatch[] (key, confidence)
                +----------------------+
                            |
context (dict) +----------------------+
  - phase       | ContextAnalyzer      | --> ContextSummary
  - active_task |                      |     (判断は行わない、意味情報のみ)
  - recent_events
  - conversation_flow
                            |
                            v
                +----------------------+
                | SemanticPipeline     |
                | (Registryでrecommended
                |  _action / related_topics
                |  を解決)              |
                +----------------------+
                            |
                            v
                    SemanticResult
                - intent
                - confidence
                - context_summary
                - related_topics
                - recommended_action
                - candidates (全Intent候補)
```

## Registry設計

`semantic_registry.py` の `INTENT_REGISTRY` が唯一の定義場所(Single
Source of Truth)。各 `IntentDefinition` は以下を持つ:

| フィールド | 内容 |
|---|---|
| `key` | 内部識別子(英語スネークケース) |
| `label_ja` / `label_en` | 表示名 |
| `keywords` | 単語境界マッチに使うキーワード群(日英混在) |
| `recommended_action` | このIntentでの推奨アクション(提案文字列) |
| `related_topics` | 関連トピックのヒント |

### 登録済みIntent一覧 (10種)

| key | 日本語 | English |
|---|---|---|
| `information_retrieval` | 情報取得 | Information Retrieval |
| `design` | 設計 | Design |
| `implementation` | 実装 | Implementation |
| `fix` | 修正 | Fix |
| `audit` | 監査 | Audit |
| `verification` | 検証 | Verification |
| `record` | 記録 | Record |
| `comparison` | 比較 | Comparison |
| `summary` | 要約 | Summary |
| `planning` | 計画 | Planning |

未知の入力には `UNKNOWN_INTENT`(`key="unknown"`)が割り当てられる。

### 新規Intent追加時の変更箇所

`INTENT_REGISTRY` に `IntentDefinition` を1件追加するだけでよい。
`intent_classifier.py` / `semantic_pipeline.py` / `semantic_result.py`
への変更は不要(Registryを動的に走査するため)。

## SemanticResultの構造

```python
SemanticResult(
    intent=IntentCandidate(key, label_ja, label_en, confidence),
    confidence: float,                 # 上位Intentの確信度 (0.0-1.0)
    context_summary=ContextSummary(
        phase, active_task, recent_events,
        conversation_flow, summary_text,
    ),
    related_topics: tuple,
    recommended_action: str,
    candidates: tuple[IntentCandidate],  # 全候補(確信度降順)
)
```

`to_dict()` でJSON互換のdictに変換できる。

## 将来Decision Layerとの接続方針

- Decision Layerは `SemanticPipeline.process(text, context)` の戻り値
  (`SemanticResult`)をそのまま入力として受け取る想定。
- `recommended_action` は「提案」であり、Decision LayerがGovernance
  Layer(GL1-7)の判断と合わせて最終的な実行可否を決定する。
- `candidates` (複数Intent候補+confidence) を用いることで、
  Decision Layerは曖昧な意図に対する追加確認フローを設計できる。
- Semantic LayerはGovernance Layerに依存せず、Governance Layerも
  Semantic Layerに依存しない(責務分離を維持)。Decision Layerが
  両者を統合する層となる。
- Memory Layer実装後は、`context` 引数(`recent_events` /
  `conversation_flow` 等)をMemory Layerから供給する想定。
  Context Analyzerのインターフェース(dict入力)は変更不要。
