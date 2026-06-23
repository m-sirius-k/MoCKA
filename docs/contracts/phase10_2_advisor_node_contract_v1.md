# Phase10-2: Advisor Node Contract v1

Status: DRAFT (Phase10-2。契約のみ。コード禁止・テスト禁止。
実装は本契約では行わない・要承認)
Date: 2026-06-23

本文書はPhase10-0（Cognitive Integration Concept Contract）の
Node Definition第1章Category 1「Advisor Node」を制度化する。
Phase7（Semantic OS Core）、Phase8（HAB Runtime Integration
Layer）、Human Gate（Phase7-B6/B7）、Phase9-1〜9-3A（Projection
Layer全契約）、Phase10-0、Phase10-1（Observer Node Contract）の
いずれのクラス・メソッド署名・絶対禁止・凍結状態も本文書では
変更しない。

```
本文書で行わないこと（確定）:
    コード追加
    テスト追加
    Runtime変更（Phase8）
    Core変更（Phase7）
    Human Gate変更
    Projection Layer変更（Phase9全体）
    Phase9-3B（Intent Projection）の凍結解除・開始
```

## 0. 位置づけ

```
Phase10-0: Node体系全体の概念契約
              （Advisor Node / Observer Node / Reasoning Node）
Phase10-1: Observer Node（見る・説明する）の制度化（完了済み）
Phase10-2: Advisor Node（見る・説明する・提案する）の制度化（本文書）
Phase10-3: Reasoning Node（候補を生成する）の制度化（未着手）
```

Phase10権限階層はPhase10-1で「最も弱い権限」を固定し、本契約で
一段階上の権限（提案）を固定する。提案権限の追加が採択権限の
追加を意味しないことが、本契約全体を通じて最も重要な境界となる。

## 1. Advisor Node Definition（確定）

```
Advisor Node とは:
    Observer Nodeの観測結果に基づき、助言・説明・代替案提示・
    矛盾点指摘を行うNode。
```

役割は以下の4点に限定する。

```
役割1: 観測結果に対する助言
    Observer Nodeが観測した状態（trace_view/cluster_view/
    collision_view/ruling_view）に基づき、助言を生成する。

役割2: 候補の説明
    Projection結果（EventCandidate/NLCandidate）について、
    各候補がなぜ存在するか（why_generated、Phase9-3A第5章）を
    踏まえた説明を行う。

役割3: 代替案の提示
    単一の推奨だけでなく、複数の選択肢を並列に提示する。

役割4: 矛盾点の指摘
    候補間・観測結果間の矛盾（collision_viewが示す衝突等）を
    指摘する。指摘は「ここに矛盾がある」という記述であり、
    矛盾の解消ではない。
```

```
Observerとの違い:
    Observer = 状態説明のみ（「今こうなっている」）
    Advisor  = 提案可能（「こうしてはどうか」「他にこういう
               可能性もある」）
    ただし採択権なし。提案が採用されるかどうかはHuman Gateのみが
    決定する。
```

Advisor NodeはPhase10-0第1章で定義したNodeの一般的性質
（読み取り専用参照、出力はHuman GateまたはAudit Logにのみ記録、
PHI-OS Core/Runtimeへの直接書き込み権限なし）、およびPhase5
Step4-A〜C・Step5・Step6で確立済みのAdvisor Adapter Governance
（GPT=Model B固定、提案のみ・実行不可）をすべて継承する。

## 2. Advisor Permissions（最重要・確定）

```
許可:
    候補比較（compare candidates）
    代替候補提示（present alternatives）
    説明生成（describe / explain）
    推論補助（reasoning assistance）

禁止:
    採択（adopt）
    実行（execute）
    candidate削除（delete candidate）
    candidate統合（merge candidate）
    collision解消（resolve collision）
    ranking改変（modify ranking）
```

許可される4操作の境界を明確化する。

```
候補比較: 複数候補の差異・共通点を並べて示す。比較の結果として
    1件を選ぶ操作は含まない。
代替候補提示: 既存候補群に対し、別の見方・別の候補群を並列に
    提示する。これは新規candidateの生成（Phase9
    SemanticProjectionLayerの責務）ではなく、既存candidate群の
    再提示・再構成（提示の仕方の工夫）に限定される。
説明生成: Observer Nodeの「状態説明」よりも踏み込み、候補間の
    関係性や背景についての解釈を含めてよい。ただし解釈の提示は
    「助言」であり「結論」ではない。
推論補助: Human Gateが判断する際の参考情報（リスク・トレード
    オフ等）を提示する。判断そのものは行わない。
```

禁止される6操作はPhase9-3A（Ranking Policy）・Phase7-B5
（Collision Governance）・Phase10-0第4章（Reasoning Ownership
Rule）・Phase10-1（Observer Permissions）の既存禁止事項を
Advisor Nodeに対してそのまま適用・拡張したものであり、提案権限
の追加によって緩和されるものではない。

## 3. Advisor Output Policy（最重要・確定）

```
出力形式:
    Recommendation（推奨）
    Alternative（代替案）
    Risk（リスク）
    Observation（観測事実）
```

```
Advisorは常に複数候補を保持する。
```

出力形式4種の関係を明確化する。

```
Recommendation: 「これを検討してはどうか」という助言。
    複数のRecommendationが同時に存在してよい
    （唯一のRecommendationに限定しない）。
Alternative: Recommendationに対する代替の選択肢。
    Recommendationと同じ重みで並列に保持される
    （Alternativeが劣後扱いされることはない）。
Risk: 各Recommendation/Alternativeに付随する懸念点。
Observation: Observer Nodeから引き継いだ観測事実（状態の記述）。
    Advisor自身の解釈と区別して保持する。
```

```
以下を禁止:
    唯一解提示（presenting a single solution as "the" answer）
    winner宣言（declaring any candidate as winner）
    top-1確定（finalizing a top-1 selection）
```

これはPhase9-1の核心原則「単一解を作らず、複数候補を保持した
まま流す」、Phase7-B5「衝突は解消しない」の直接継承であり、
Advisor Nodeの出力構造そのものに恒久的に適用される。

## 4. Advisor Governance（確定）

```
Advisorは Human Gateを代行しない。
Advisorは Orchestratorを代行しない。
Advisorは Projectionを変更しない。
```

```
Human Gate代行禁止:
    Advisor Nodeの助言・推奨が、いかなる形であっても
    「採択された」「承認された」という効力を持つことはない。
    採択権は常にHuman Gateのみが持つ（Phase10-0第4章Reasoning
    Ownership Ruleの継承）。

Orchestrator代行禁止:
    Advisor NodeはPhase8-3 Execution Orchestratorの処理順序
    （MeaningCycleExecutor -> OrderNormalizer -> CollisionGovernor）
    を呼び出さない、変更しない、迂回しない。

Projection変更禁止:
    Advisor NodeはPhase9 SemanticProjectionLayerの内部メソッドへ
    候補生成・削除・並び替えの指示を送らない（Phase10-0第3章
    Projection Connection Ruleの継承）。「代替候補提示」（第2章）
    は既存candidate群の再提示に限定され、Projection層そのものへ
    の介入ではない。
```

Phase10-0第2章Node Governance全般規則（Node間直接通信禁止/
Nodeはcollisionを解消しない/Node追加削除は人間ゲート承認必須）
もAdvisor Nodeにそのまま適用される。

## 5. Advisor / Observer Boundary（確定）

Phase10権限階層における三者の役割を明確に分離する。

```
Observer Node:
    見る
    説明する

Advisor Node:
    見る
    説明する
    提案する

Reasoning Node（Phase10-3で制度化予定・本契約では定義しない）:
    候補を生成する
```

```
三者の境界が崩れてはならない理由:
    Observer -> Advisor の境界（「説明」から「提案」への一段階）
        は権限の追加だが、採択権の追加ではない。
    Advisor -> Reasoning の境界（「提案」から「候補生成」への
        一段階）は、Phase9 Projection層の責務（候補生成）に
        踏み込む境界であり、Reasoning Nodeの制度化（Phase10-3）
        を経ない限りAdvisor Nodeがこれを行うことはできない。
    いずれの段階においても「採択（Adoption）」はHuman Gateのみ
        が持ち、「実行（Execution）」はExecution Orchestratorの
        みが持つ（Phase10-0第4章Reasoning Ownership Ruleの三分離
        を全段階で維持する）。
```

## 6. Future Integration（確定）

```
将来のGPT/Claude/Geminiは、Observer Nodeから始まり、必要に応じて
Advisor Nodeへ昇格する制度を記録する。ただし昇格にはHuman Gate
承認を必須とする。
```

- Phase10-1第5章Future Integrationで「外部AIは最初Observer
  Nodeとして接続することを推奨」と記録済み。本契約はその継続
  として、Observer Nodeとして稼働した後にAdvisor Nodeへ昇格する
  経路を記録する。
- 昇格条件（確定）:
  ```
  昇格にはHuman Gate承認を必須とする。
  自動昇格・条件満了による自動昇格は存在しない。
  ```
- 既存のAdvisor Adapter Governance（Phase5 Step4-A〜C, Step5,
  Step6）はGPTを「Model B (Advisor)」に固定し、提案のみ・実行
  不可と定義している。本契約のAdvisor Node Permissions/Output
  Policy/GovernanceはPhase5の既存Advisor Adapter契約と整合し、
  これを置き換えるものではない。
- これは設計判断・昇格経路の記録であり、接続実装・昇格実行の
  承認ではない。実際の外部AI接続（SDK導入・API Key設定等）は
  PHASE5_STEP3_SEALの禁止事項（GPT Adapter実装/MCP Adapter
  実装/外部接続等の禁止）に従い、依然未着手・凍結のままである。
  本契約はこの凍結状態を解除しない。

## 7. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、
ユーザーの明示的承認を要する。第3章（Advisor Output Policy）の
「常に複数候補を保持する」原則、および第5章の三者境界（Observer/
Advisor/Reasoning）は、他のいかなる変更からも独立して維持される。

本契約はPhase9-3B（Intent Projection）の凍結状態に影響しない。
Phase9-3Bの着手条件（`docs/audits/phase9_artifacts_audit_v1.md`
第3章）は本契約と独立して維持される。
