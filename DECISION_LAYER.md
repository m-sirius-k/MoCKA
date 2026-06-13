# Decision Layer (Phase 2-2)

## 目的

MoCKAにおいて初めて「判断(中間意思決定)」を担う層を実装する。
Semantic Layerが生成した `SemanticResult`(意味)を入力として、
「選択・優先・リスク評価・実行候補」を構造化した `DecisionResult` を出力する。

Decision Layerは**実行しない**(非破壊)。最終的な実行可否は常に
Governance Layer(GL1-7)に委ね、`required_governance_check=True` を
全DecisionResultに付与する。

## アーキテクチャ

```
decision/
    decision_registry.py     — Intentごとのデフォルト行動マッピング・評価重み
    priority_scorer.py        — 優先度スコア(0-1)算出
    risk_analyzer.py          — リスクスコア(0-1)・risk_factors算出
    decision_model.py         — 統一出力形式(DecisionResult / Alternative)
    decision_engine.py        — 候補生成・スコアリング統合(コア)
    decision_pipeline.py       — Semantic Layer + Decision Engine の単一窓口
    decision_integration_test.py — 統合テスト
    decision_sample_cases.py   — テスト用サンプルケース
```

### データフロー

```
text/context
   |
   v
SemanticPipeline (semantic/)
   |
   v
SemanticResult (intent, confidence, context_summary, candidates)
   |
   v
DecisionEngine.decide()
   |-- decision_registry.get_decision_profile(intent.key)
   |-- PriorityScorer.score()   -> priority_score (0-1)
   |-- RiskAnalyzer.analyze()   -> risk_score (0-1), risk_factors[]
   |
   v
DecisionResult
   - selected_action
   - alternatives[]
   - priority_score
   - risk_score
   - confidence
   - rationale
   - required_governance_check = True
```

## Semanticとの違い

| | Semantic Layer | Decision Layer |
|---|---|---|
| 入力 | text + context | SemanticResult |
| 出力 | 意味(Intent/Context) | 判断(選択/優先/リスク) |
| 判断を行うか | 行わない | 行う(中間意思決定のみ) |
| 実行するか | しない | しない(非破壊) |
| Governanceとの関係 | 関与しない | 必ずGovernanceへ引き渡す前提 |

Semantic Layerは「これは何を意味するか」を答える層であり、
Decision Layerは「(その意味を受けて)何をすべきか・どの優先度か・
どの程度のリスクか」を答える層である。いずれも最終実行は行わない。

## Governanceとの関係

- Decision Layerは**最終判断を行わない**。`DecisionResult` は常に
  `required_governance_check=True` を持ち、Governance Layer(GL1-7)に
  渡されることを前提とする。
- `risk_score` / `risk_factors` はGL7(Execution Governance)の
  Dry Run / Default Deny判断の参考材料として渡せるよう設計している
  (action_profile="write_heavy"は`READ_ONLY_TOOLS`に含まれないtoolの
  Dry Run対象であることを risk_factors に明記している)。
- Decision Layer自身はGovernance Layerのモジュールをimportせず、
  GL1-7のロジック・判定アルゴリズムには一切変更を加えない。

## スコアリング設計

### Priority Score (`priority_scorer.py`)

5軸の重み付き合計(合計重み=1.0):

| 軸 | 重み | 内容 |
|---|---|---|
| Intent重要度 | 0.30 | `DecisionProfile.priority_weight`(Registry定義) |
| コンテキスト強度 | 0.20 | ContextSummaryのphase/active_task/recent_events/conversation_flowの充足率 |
| 依存関係 | 0.15 | action_profile別の「先行作業への依存の小ささ」 |
| 緊急度(推定) | 0.15 | action_profile別の推定緊急度(write_heavy/fixが高め) |
| ユーザー意図明確度 | 0.20 | SemanticResult.confidence + 候補間スコア差 |

### Risk Score (`risk_analyzer.py`)

4軸の重み付き合計(合計重み=1.0):

| 軸 | 重み | 内容 |
|---|---|---|
| 副作用リスク | 0.40 | `DecisionProfile.base_risk`(Registry定義) |
| Governance違反可能性 | 0.20 | action_profile別(write_heavy=0.8 など、GL7 Default Denyを反映) |
| 未知動作可能性 | 0.20 | Intent="unknown"、または候補confidenceの近接度 |
| Context不確実性 | 0.20 | ContextSummaryの空き具合 |

`risk_factors` は `DecisionProfile.risk_factors`(Registry定義の既定要因)
に、実行時に検出した追加要因(曖昧なIntent、不足したContext等)を
合成したリストとして返す。

## Decision Registry設計

`decision_registry.py` の `DECISION_REGISTRY` が唯一の定義場所。
Semantic Registry(`semantic/semantic_registry.py`)の10 Intentキーに
対応する `DecisionProfile` を1件ずつ保持する。

| intent_key | action_profile | priority_weight | base_risk |
|---|---|---|---|
| information_retrieval | read_heavy | 0.50 | 0.10 |
| design | analysis_heavy | 0.60 | 0.20 |
| implementation | write_heavy | 0.80 | 0.70 |
| fix | write_heavy | 0.85 | 0.65 |
| audit | verification_first | 0.70 | 0.30 |
| verification | verification_first | 0.65 | 0.25 |
| record | write_heavy | 0.40 | 0.35 |
| comparison | analysis_heavy | 0.50 | 0.15 |
| summary | read_heavy | 0.45 | 0.10 |
| planning | analysis_heavy | 0.55 | 0.20 |
| (unknown) | verification_first | 0.30 | 0.30 |

新しいIntentに対応する場合は `DECISION_REGISTRY` に1エントリを
追加するだけでよい(`priority_scorer.py`/`risk_analyzer.py`/
`decision_engine.py`への変更は不要)。

## DecisionResultの構造

```python
DecisionResult(
    selected_action: str,
    alternatives: tuple[Alternative],   # action, priority_score, risk_score
    priority_score: float,              # 0.0 - 1.0
    risk_score: float,                  # 0.0 - 1.0
    confidence: float,                  # SemanticResult.confidenceを継承
    rationale: str,
    required_governance_check: bool = True,
    risk_factors: tuple[str],
)
```

`to_dict()` でJSON互換のdictに変換できる。

## 今後Memoryとの統合方針

- Memory Layer実装後、`DecisionEngine.decide()` が参照する
  `SemanticResult.context_summary` の供給元(`recent_events` /
  `conversation_flow`)をMemory Layerに切り替えるのみでよい。
  Decision Layer側のインターフェース変更は不要。
- `DecisionResult` はそのままMemory Layerへの記録対象となり得る
  (`to_dict()` でシリアライズ可能)。将来的に「過去のDecisionResultの
  履歴」をPriority/Riskスコアリングの追加入力(過去の選択傾向)として
  利用することも、Registryへのエントリ追加のみで拡張可能な設計としている。
- Decision LayerはMemory Layerの有無に関わらず、`context=None`
  (情報量ゼロのContextSummary)でも動作する(フォールバック済み)。
