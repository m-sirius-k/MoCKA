# Feedback Loop & Adaptive Decision (Phase 3-2)

## 目的

Self-Audit Layer(Phase 3-1)が生成する`AuditReport`を入力として、
Decision / Memory / Semantic(軽微)に対する「重み調整案・改善提案」を
生成する。MoCKAを「評価するシステム」から「改善するシステム」へ
進化させる層である。

ただし、本層は以下を絶対に行わない:

- 自動コード修正
- Governance変更
- 実行ロジック変更
- 即時反映(自動適用)
- Memory削除

許可されるのは「分析・提案・重み調整案・影響評価」のみであり、
すべての提案は`requires_governance_check = True`を保持し、最終的な
適用判断は人間または上位プロセス + Governance Layerに委ねられる。

## Feedback Loop構造

```
Semantic / Decision / Memory / Governance
        |
        v
  Self-Audit Layer (AuditPipeline.run_full_audit())
        |
        v
  AuditReport (issue_list)
        |
        v
  Feedback Engine (Target Classifier)
        |
        v
  Weight Optimizer / Decision Tuner / Memory Reinforcer / Semantic Adjuster
        |
        v
  FeedbackProposal
        |
        v
  Governance Validation (GOVERNANCE_REGRESSION_SUMMARY.md読み取り)
        |
        v
  pending_governance_review / blocked
```

```
feedback/
    feedback_registry.py        — feedback_type/target_layer分類/
                                   confidence・priorityルール/安全制約
    feedback_model.py            — FeedbackProposal / FeedbackBatch
    weight_optimizer.py           — Decision/Memory/Semanticの重み調整案
    decision_tuner.py             — Decision Layerへの改善提案
    memory_reinforcer.py          — Memoryの強化・減衰提案
    semantic_adjuster.py          — Semanticへの改善提案(提案のみ)
    feedback_engine.py            — AuditReport -> FeedbackProposal
    feedback_pipeline.py          — Self-Audit -> Feedback -> Governance検証
    feedback_integration_test.py
    feedback_weight_test.py
    feedback_safety_test.py
```

## 各Layerへの影響(提案内容)

### Decision Layer

| Audit check | feedback_type | 提案内容 |
|---|---|---|
| `priority妥当性` | `weight_adjustment` | `priority_scorer.py`の`intent_clarity`重みの増減案 + priority再配分提案(`decision_tuner`) |
| `risk整合性` | `weight_adjustment` | `risk_analyzer.py`の`governance_violation`重みの増減案 + risk scoring補正提案(`decision_tuner`) |
| `rationale一貫性` | `rationale_improvement` | `decision_engine.py`のrationaleテンプレート改善提案 |

### Memory Layer

| Audit check | feedback_type | 提案内容 |
|---|---|---|
| `一貫性` | `memory_reinforcement` | 成功パターン(risk_score<0.4)を`memory_type=skill`として再記録し優先度を高める提案 |
| `ノイズ率` | `memory_decay` | `memory_retriever.py`の`recency`重みを下げ、重複・低価値記憶を減衰させる提案(削除ではない) |
| `再利用性` | `reuse_weight_adjustment` | `memory_retriever.py`の`intent_match`重みを上げ、再利用可能な記憶を優先する提案 |

### Semantic Layer(軽微・提案のみ)

| Audit check | feedback_type | 提案内容 |
|---|---|---|
| `意図分類精度` | `intent_threshold_adjustment` | `intent_classifier.py`の`confidence_threshold`引き下げ案 + `semantic_registry`のkeywords追加候補(`registry_candidate`) |
| `context補完妥当性` | `context_improvement` | `context_analyzer.py`のsummary_text生成ロジック見直し提案 |

### Governance Layer

Governance Layerの`AuditReport`(target_type=`governance`)は
`feedback_registry.is_feedback_target()`により**Feedback対象外**である。
`FeedbackEngine.generate()`は当該AuditReportに対し常に空のtupleを返す
(逆流禁止)。

## Weight調整原理

`weight_optimizer.WeightOptimizer`は、issueの`severity`に応じた
調整幅(`_DELTA_BY_SEVERITY`: critical=0.10 〜 info=0.01)を用いて、
対象パラメータの`suggested_delta`と`direction`(increase/decrease)を
算出する。あくまで「現在値に対する増減の提案」であり、Registry/Pipeline
の実値は変更しない。

`feedback_registry.confidence_for_severity(severity)`は
severityが高いほど高いconfidence(critical=0.95 〜 info=0.3)を返す
(「問題が明確であるほど、改善提案の確信度も高い」という設計)。

`expected_impact`は `confidence × priority_for_feedback_type(feedback_type) × 1.4`
(0-1にクリップ)で算出する。`priority_for_feedback_type`は
`feedback_registry.PRIORITY_RULES`に定義される。

## Governance連携

すべての`FeedbackProposal`は`requires_governance_check = True`を
コンストラクタのデフォルト値として保持し、`feedback_pipeline`内でも
変更しない。

`FeedbackPipeline._governance_validation()`は
`structural/GOVERNANCE_REGRESSION_SUMMARY.md`を読み取り専用で確認し、
"Overall PASS"の記載があれば`governance_status="PASS"`、なければ
`"FAIL"`を返す。

- `governance_status == "PASS"` → 各`FeedbackProposal.status`は
  `"pending_governance_review"`(人間・上位プロセスのレビュー待ち。
  自動適用はしない)
- `governance_status != "PASS"` → 各`FeedbackProposal.status`は
  `"blocked"`(Governance Regressionが健全でないため、適用検討自体を保留)

```
Feedback Proposal
   ↓
Governance Validation
   ↓
Apply / Reject   (※本フェーズではApply/Rejectの実行自体は対象外。
                   pending_governance_review / blocked のラベル付けのみ)
```

## 将来のSelf-Learning構想

現状の`status`は`pending_governance_review`/`blocked`の2値であり、
実際の適用(Apply)・棄却(Reject)は人間または別フェーズのプロセスが
行う。将来的には:

1. レビュー済みProposalのうち承認されたものを記録する
   `feedback_decision_log`(Memory Layerのepisodic記憶として記録)
2. 承認パターンの蓄積から、Feedback自体の`confidence`/`priority`を
   `Improvement Scorer`(Self-Audit Layer)同様の手法で再調整する
3. 最終的に、承認された重み調整のみをDecision/Memory Registryへ
   反映する別モジュール(`self_healing/`等)を、Governance Layerの
   明示的なゲートを通じて新設する

という段階を想定する。いずれの段階でもSelf-Audit/Feedback Loop自身が
直接Registry/コードを書き換えることはなく、「提案 → レビュー → 承認 →
(別モジュールによる)適用」という非破壊的な多段構成を維持する。
