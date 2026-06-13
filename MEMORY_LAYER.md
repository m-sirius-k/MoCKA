# Memory Layer (Phase 2-3)

## 目的

Decision Layerが生成する判断(`DecisionResult`)を持続させ、MoCKAに
「一貫性」と「継続性」を与える。単発の判断ではなく、過去の記憶を
踏まえた判断ができる「継続知能」への進化を目的とする。

Memory Layerは記録・検索・コンテキスト生成のみを行う。
Governance Layer(GL1-7)・Semantic Layer・Decision Layerのロジックには
変更を加えない(これらの出力結果を読み取るのみ)。

## 4種記憶の定義

| memory_type | 名称 | 内容 | 例 |
|---|---|---|---|
| `episodic` | エピソード記憶 | 過去の意思決定・実行履歴・会話/イベント履歴 | `DecisionResult`、EventLog |
| `semantic` | 意味記憶 | 概念・定義・Registry情報・固定知識 | `decision_registry`の`action_profile`定義 |
| `procedural` | 手続き記憶 | 実行フロー・Pipeline構造・Decisionルール | Pipeline実行ログ、フロー定義 |
| `skill` | 技能記憶 | 最適化された処理パターン・成功パターン・再利用可能な構造 | 低リスクで完了したDecisionパターン |

各memory_typeは `memory_registry.RETENTION_POLICIES` で
`max_entries`(保存上限)・`default_priority`・`default_tags` を定義する。

## アーキテクチャ

```
memory/
    memory_registry.py         — memory_type/タグ体系/優先度ルール/保存ポリシー
    memory_model.py             — MemoryEntry / ScoredMemory / EnrichedContext
    memory_store.py             — 中核ストレージ(JSON、保存ポリシー適用)
    memory_index.py             — intent/tag/time/similarity インデックス構築
    memory_writer.py            — DecisionResult/EventLog -> MemoryEntry
    memory_retriever.py         — 検索条件 -> ranked ScoredMemory list
    memory_context_builder.py   — 過去記憶 -> EnrichedContext
    memory_pipeline.py          — 上記を統合する単一窓口
    memory_integration_test.py
    memory_retrieval_test.py
    memory_consistency_test.py
    data/memory_store.json      — 永続化先(JSON配列)
```

## データフロー

```
Event / DecisionResult
        |
        v
  MemoryWriter ----------------------+
        |                            |
        v                            |
  MemoryStore (data/memory_store.json)
        |
        v
  MemoryIndex (intent/tag/time/similarity)
        |
        v
  MemoryRetriever --------------------+
        |                             |
        v                             v
  MemoryContextBuilder         retrieve(intent/tags/query)
        |
        v
  EnrichedContext
        |
        +--> to_context_dict() --> Semantic Layer (ContextAnalyzer入力)
        +--> to_dict()          --> Decision Layer / 将来Self-Audit
```

## Decisionとの連携

`memory_pipeline.MemoryPipeline.process(text, context)` が
Semantic Layer / Decision Layerと連携する単一窓口:

1. `SemanticPipeline.process()` で一次Intent推定(`preliminary`)
2. `MemoryContextBuilder.build(preliminary.intent.key, query=text)` で
   同Intentの過去Decision履歴から `EnrichedContext` を構築
3. `EnrichedContext.to_context_dict()` を元の `context` に合成し、
   `SemanticPipeline.process()` を再実行(`semantic_result`)
4. `DecisionPipeline.decide_from_semantic(semantic_result)` で
   `DecisionResult` を生成
5. `MemoryWriter.write_decision(decision_result, semantic_result)` で
   `DecisionResult` をepisodic memoryとして記録

```python
from memory_pipeline import MemoryPipeline

pipeline = MemoryPipeline()
decision_result, enriched_context = pipeline.process(
    "Decision Engineを実装して新しいモジュールを追加して",
    {"phase": "phase2-3", "active_task": "TODO_implement_memory"},
)
```

`enriched_context.to_dict()` には以下が含まれる:
- `past_decisions`   — 同Intentの過去`DecisionResult`(ScoredMemory)
- `success_patterns` — `risk_score < 0.4` の過去Decision
- `failure_patterns` — `risk_score >= 0.6` の過去Decision
- `related_topics`   — `semantic_registry`の`IntentDefinition.related_topics`
- `summary_text`     — 上記の要約文

## Index設計

`memory_index.MemoryIndex` はMemory Storeのスナップショットから
4種のインデックスを構築する(都度再構築する簡易設計):

| index | キー | 値 |
|---|---|---|
| `intent_index` | `metadata["intent_key"]` | memory_idのタプル |
| `tag_index` | tag文字列 | memory_idのタプル |
| `time_index` | — | timestamp昇順のmemory_idタプル |
| `similarity_index` | トークン(キーワード) | memory_idのタプル |

`similarity_index` は `rationale`/`selected_action`/`summary_text`/
タグ等のテキストを正規表現でトークン化した簡易キーワード一致である
(埋め込みベクトル等は使用しない=「簡易で可」要件)。

## Retrievalロジック

`memory_retriever.MemoryRetriever.retrieve()` は以下を受け付ける:

- `intent_key`  — 指定時はハードフィルタ(metadata一致のみ)
- `tags`        — タグ重複率をスコアに反映(フィルタではない)
- `query`       — `similarity_index`によるトークン一致数をスコアに反映
- `memory_type` — 指定時はハードフィルタ
- `top_k`       — 返却件数の上限

`relevance_score`(0-1)は以下の重み付き合計:

| 軸 | 重み |
|---|---|
| intent_match | 0.40 |
| tag_overlap | 0.25 |
| similarity | 0.20 |
| recency | 0.15 |

検索条件が一切指定されない場合は `recency` のみで新しい順に並べる。

## 将来Self-Audit接続設計

- `memory_store.MemoryStore` は `data/memory_store.json` に
  追記型で記録されるため、Self-Auditは過去のDecision履歴
  (`memory_type=episodic`)を時系列で全件検査できる。
- `EnrichedContext.success_patterns` / `failure_patterns` は
  risk_scoreベースの簡易分類だが、将来Self-Auditが「実際の実行結果
  (成功/失敗)」を `memory_writer.write_event()` で記録することで、
  分類基準を「推定リスク」から「実績」に置き換え可能(Registry/Writer
  への追加のみで対応でき、Retriever/ContextBuilderのインターフェースは
  変更不要)。
- `memory_type=skill`(技能記憶)に蓄積される再利用可能パターンは、
  Self-Auditが「同じIntentで繰り返し低リスクだった判断」を抽出し、
  Decision Registryの重み調整(将来フェーズ)の参考データとして
  利用できる。
- Memory LayerはGovernance Layerをimportしないため、Self-Audit自身は
  Governance Layer側(GL6 Reasoning Governance等)に実装し、
  Memory Layerが提供する `retrieve()` / `get_enriched_context()` を
  読み取り専用で利用する構成を想定する。
