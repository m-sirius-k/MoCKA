# REGISTRY_SEMANTICS_v1.0

KN-005: Registry Semantics(意味論)

## 1. Scope

本文書はRegistryが管理対象として扱うCategoryおよびSeriesの意味を
定義する。Registry自身の構造・用語(Record、Artifact、Reference等)
はTERM-001の管轄とし、本書では再定義しない。また、Category・Series
間の関係性およびTopologyはAtlas Seriesの管轄とし、本書の対象外とする。

対象:
- Categoryの意味(DP/GV/IA/OA/KN/KA各々が何を表すか)
- Categoryの境界条件
- Seriesの意味(KN-004 classification.series/series_numberが指す系列構造)
- classification.artifact_type の意味的な分類軸

対象外:
- JSON Schema(KN-004の範囲)
- Validation(KN-007の範囲・予定)
- State遷移(KN-006の範囲・予定)
- Category/Series間の関係図・Topology(Atlas Seriesの範囲)
- Registry自身の用語定義(TERM-001の範囲)

## 2. Semantic Principles(意味論の原則)

- 意味定義は「何を表すか」を書くものであり、「どう運用するか」
  (個別番号の列挙・運用例)は含めない。
- 定義は制度の意味であり、運用例に引っ張られない形で記述する
  (例: 「DP-001」等の個別Artifactの列挙はしない)。
- 各Categoryの定義は、対になる「何ではないか」(Boundary Rules)
  を伴ってはじめて完成する。

## 3. Category Definitions

| Formal Name | Code | Meaning |
|---|---|---|
| Decision | DP | 意思決定制度に関するカテゴリ。判断・優先順位・競合解決の裁定を扱う |
| Governance | GV | 制度運用・監査に関するカテゴリ。成果物管理・監査運用・検証プロセスを扱う |
| Impact | IA | 制度変更が他レイヤーへ与える影響評価に関するカテゴリ |
| Operational Assurance | OA | 運用保証に関するカテゴリ(Canary Test・CI実効保証等) |
| Knowledge Navigation | KN | 知識の「探索」に関するカテゴリ。Passive。"Where?"に答える |
| Knowledge Activation | KA | 知識の「活用」に関するカテゴリ。Active。"Why?/When?/How?"に答える |

## 4. Boundary(境界)

### 4.1 Category Boundary(何ではないか)

- DPは実行しない・保存しない・Approvalを持たない。
  本境界はDECISION_POLICYシリーズの制度原則を継承する。
- GVは意思決定を行わない。GVは「その成果物が正しく証明・検証されたか」
  のみを扱う。本境界はGovernance Audit Seriesの制度原則を継承する。
- KNは「使う」判断をしない。KNが答えるのは存在の有無・所在のみであり、
  「今どれが必要か」はKAの責務。本境界はGM2_ROADMAPのNavigation/
  Activation責務分離を継承する。
- KAは「探す」機構を持たない。KAはKNが既に存在を確認した知識を前提として
  参照・活用する。
- IA/OAは制度そのものを設計しない。既存制度が正しく機能しているかを
  確認・保証する立場に留まる。本境界はImpact Audit Series/Operational
  Assurance Seriesの制度原則を継承する。

### 4.2 TERM-001 Boundary

本文書はCategoryの意味論のみを扱い、Registryの構造用語
(Record/Entry/Artifact/Reference/Identifier等)の定義には立ち入らない。
それらの用語の意味はTERM-001_REGISTRY_TERMINOLOGY.mdを正本として参照する。

### 4.3 Atlas Boundary

本文書は各Categoryの意味を定義するものであり、Category間・Series間の
関係・依存・接続・経路(Topology)はAtlas Series(GM2_ROADMAP)の管轄
とし、本書の対象外とする。

## 5. Extension Policy(将来拡張)

- 新Category追加は、CATEGORY_REGISTRY_V1の原則(既存シリーズの追加で
  解決できないことを筆頭条件とする＝新カテゴリは最後の手段)を継承する。
- 既存Categoryの意味を変更する場合は、本文書の改訂として扱い、
  KN-004(Schema)・KN-002(分類体系)への影響を都度確認する。
