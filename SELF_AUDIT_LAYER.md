# Self-Audit Layer (Phase 3-1)

## 目的

Semantic / Decision / Memory / Governanceの4層が生成する出力を評価し、
「改善提案」として非実行のフィードバックを生成する。

Self-Audit Layerは以下3原則のもとで動作する:

1. **非実行原則**: 評価・分析・改善提案の生成のみを行い、いかなる実行も行わない。
2. **層分離維持**: 各層の責務を侵さない。
   - Semantic = 意味生成
   - Decision = 意思決定
   - Memory = 記録・再利用
   - Governance = 実行制御
   - Self-Audit = 評価・改善
3. **逆流禁止**: Self-AuditはDecision/Governanceを直接変更しない。
   出力は常に「改善提案(improvement_suggestions / prioritized_actions)」
   のみであり、各層への書き込みは一切行わない。

## アーキテクチャ

```
self_audit/
    audit_registry.py    — 評価ルール/スコア閾値/severity定義/層別チェック項目
    audit_model.py        — Issue / AuditReport / ImprovementSuggestion / PrioritizedAction
    audit_analyzer.py      — 各層の出力を読み取り評価軸ごとにスコア化
    improvement_scorer.py  — improvement_suggestionsに0-1スコアを付与
    feedback_generator.py  — improvement_suggestions / prioritized_actionsを生成
    audit_engine.py        — Analyzer + FeedbackGeneratorを統合しAuditReportを生成
    audit_pipeline.py       — 4層を統合的に評価する単一窓口
    audit_integration_test.py
    audit_consistency_test.py
    audit_feedback_test.py
```

## データフロー

```
Semantic（意味）
   ↓
Decision（判断）
   ↓
Memory（継続）
   ↓
Self-Audit（評価）
   ↓
Governance（制御）
```

```
SemanticPipeline / DecisionPipeline / MemoryStore / (Governance各ファイル)
        |
        v
  AuditAnalyzer (評価軸ごとにscore/issues/strengthsを算出)
        |
        v
  AuditEngine (AuditReport生成)
        |
        v
  FeedbackGenerator (improvement_suggestions)
        |
        v
  ImprovementScorer (improvement_score付与)
        |
        v
  prioritized_actions
```

## Auditモデル設計

`audit_model.AuditReport`:

| フィールド | 内容 |
|---|---|
| `audit_id` | 監査ID (`AUDIT_<target_type>_<seq>`) |
| `target_type` | `semantic` / `decision` / `memory` / `governance` |
| `target_id` | 評価対象の識別子 |
| `evaluation_score` | 0.0-1.0の総合評価スコア |
| `issue_list` | `Issue`(check/description/severity)のtuple |
| `strength_list` | 良好点の説明文字列のtuple |
| `improvement_suggestions` | `ImprovementSuggestion`のtuple |
| `severity_level` | `info`/`low`/`medium`/`high`/`critical` |

`audit_model.ImprovementSuggestion`:
`suggestion_id` / `target_type` / `target_id` / `description` /
`related_check` / `improvement_score`

`audit_model.PrioritizedAction`:
`suggestion` / `improvement_score` / `rationale`

## 評価軸設計 (audit_registry.LAYER_CHECKS)

| 層 | 評価軸 |
|---|---|
| Decision | priority妥当性 / risk整合性 / rationale一貫性 |
| Memory | 再利用性 / 一貫性 / ノイズ率 |
| Semantic | 意図分類精度 / context補完妥当性 |
| Governance | Fail Closed維持 / bypass検出 / 異常ログ |

`audit_registry.SCORE_THRESHOLDS` により `evaluation_score(0-1)` を
`severity_level` (`info`/`low`/`medium`/`high`/`critical`) に変換する。
issue_list内に算出スコアより重いseverityが存在する場合は、そのseverityを
`AuditReport.severity_level`として採用する(重大issueの過小評価を防ぐ)。

### 各層のAnalyzer実装概要

- **Decision**: `DecisionResult.priority_score`/`risk_score`が0-1範囲か、
  `selected_action`がDecision Registryの候補に含まれるか、
  `risk_score>=0.6`の場合に`risk_factors`が記録されているか、
  `required_governance_check`が`True`のままか、`rationale`に
  `selected_action`が明記されているかを検証する。
- **Memory**: `MemoryStore.all()`から取得した全`MemoryEntry`について、
  必須フィールド(`memory_id`/`timestamp`/`memory_type`、episodicは
  `metadata.intent_key`)の有無(一貫性)、`memory_type=skill`の比率
  (再利用性)、`content`内テキストの重複率(ノイズ率)を評価する。
- **Semantic**: `semantic_sample_cases.SAMPLE_CASES`を`SemanticPipeline`で
  処理し、`expected_intent`との一致率(意図分類精度)、contextが与えられた
  場合の`ContextSummary.summary_text`の非空率(context補完妥当性)を評価する。
- **Governance**: `mocka_mcp_server.py`内の`GL_FAIL_CLOSED`/
  `READ_ONLY_TOOLS`記述の有無(Fail Closed維持)、
  `structural/dogfood_result.json`の`bypassed`/`fatal_errors`(bypass検出)、
  `write_aborted`/`checklist_fail_count`(異常ログ)、
  `structural/GOVERNANCE_REGRESSION_SUMMARY.md`の`Overall PASS`記載を
  読み取り専用で確認する。

## Feedback設計

`feedback_generator.FeedbackGenerator.generate_suggestions(target_type, target_id, issue_list)`は
各issueから`ImprovementSuggestion`を生成する。説明文は
「[check] description について、原因を分析し改善案を検討することを推奨する
(本提案は自動修正を伴わない)。」の形式に統一し、自動修正・自動実行・
自動コード変更を一切claimしない。

`generate_prioritized_actions(suggestions)`は`improvement_score`降順に
ソートした`PrioritizedAction`のtupleを返す。各`rationale`には
対象`check`と`improvement_score`を明記する。

## Improvement Scoring設計

`improvement_scorer.ImprovementScorer.score(severity_level, target_type, occurrence_count, max_occurrence)`は
以下4軸の重み付き合計(0-1)で`improvement_score`を算出する:

| 軸 | 重み | 算出方法 |
|---|---|---|
| 影響度 (impact) | 0.35 | severity_levelから決定(`critical`=1.0 〜 `info`=0.1) |
| リスク低減効果 (risk_reduction) | 0.30 | severity_levelから決定(影響度と同基準) |
| 頻度 (frequency) | 0.15 | 同checkの出現回数 / 今回監査における最大出現回数 |
| システム全体への波及性 (ripple) | 0.20 | target_typeから決定(`governance`=1.0 > `decision`=0.7 > `memory`/`semantic`=0.5) |

## Integration Test結果

- `audit_integration_test.py`: 23/23 PASS
  - 全層(Semantic/Decision/Memory/Governance)のAudit可能性
  - AuditReportの基本フィールド・to_dict()
  - prioritized_actionsの生成・スコア範囲・ソート順
- `audit_consistency_test.py`: 16/16 PASS
  - audit_registryのスコア閾値/severity/LAYER_CHECKS整合性
  - AnalyzerがDecisionResultを変更しないこと(層分離維持)
  - Governance違反検出ロジックの整合性
- `audit_feedback_test.py`: 20/20 PASS
  - ImprovementScorerのスコア範囲・severity/頻度反映
  - improvement_suggestionsが自動修正/自動実行を主張しないこと
  - prioritized_actionsのソート順・to_dict()

## Governance Regression結果

`python structural/governance_regression.py` を実行し、
Integration / Dogfood / Audit すべてPASS、`Overall PASS`を維持。
Governance Layer v1.1 Baseline (Commit `e35724b97b7abcdc68ce5df5574537581faf0dfb`,
Event `E20260613_067`) は変更されていない。

## 他層との連携方法

- **Memory Layer**: `memory_store.MemoryStore().all()` を読み取り専用で
  呼び出し、過去のDecision履歴(`memory_type=episodic`)・成功/失敗パターン
  (`memory_type=skill`)を一貫性・再利用性・ノイズ率の観点で評価する。
- **Decision Layer**: `decision_pipeline.DecisionPipeline` と
  `semantic_pipeline.SemanticPipeline` を用いて`decision_sample_cases`を
  再評価し、`DecisionResult`のrationale・risk整合性・Governance確認要求
  (`required_governance_check`)を検証する。
- **Governance Layer**: `structural/dogfood_result.json` /
  `structural/GOVERNANCE_REGRESSION_SUMMARY.md` / `mocka_mcp_server.py`を
  ファイル読み取りのみで分析し、Fail Closed維持・bypass検出・異常ログを
  確認する。

## 将来のSelf-Healing構想

現状のSelf-Audit Layerは「評価・改善提案」のみを行う。将来的には
`prioritized_actions`を人間または上位の意思決定プロセスがレビューし、
承認されたものだけをDecision/Governance Registryへの変更案として
別フェーズで適用する「Self-Healing」段階への拡張が考えられる。
その場合も、Self-Audit自身が直接Registryやコードを書き換えることは
逆流禁止原則により行わず、承認ステップを経た別モジュール
(将来の `self_healing/` 等)が実行を担う構成を想定する。
