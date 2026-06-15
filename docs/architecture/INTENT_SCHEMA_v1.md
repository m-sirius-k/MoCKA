# INTENT_SCHEMA v1.0

## 0. ステータスと位置づけ

本書は [ARCHITECTURE_MOCKA_2_0_v1.md](ARCHITECTURE_MOCKA_2_0_v1.md) を前提として、Layer 3（Cognitive Governance Layer）が扱う最小データ構造「Intent」を定義する。

- ①（ARCHITECTURE_DOC v1.0）= 固定
- ②（本書 INTENT_SCHEMA v1.0）= 構造生成
- 以降すべての設計はこの2つを基準とする。

MoCKA 2.0において、EventはIntentに従属するデータとなる（P1：意図はすべての上位構造である）。本スキーマはEventではなくIntentを中心データとして機能させるための最小カーネルである。

## 1. Intent オブジェクト構造

```json
{
  "intent_id": "string",
  "source": {
    "origin": "string",
    "originating_event_ids": ["string"]
  },
  "priority": "string",
  "stability": "string",
  "lifecycle_state": "draft | active | resolved | deprecated",
  "conflict": {
    "conflicts_with": ["string"],
    "resolution_state": "none | open | resolved",
    "resolution_intent_id": "string | null"
  },
  "dependencies": {
    "depends_on": ["string"],
    "required_by": ["string"]
  },
  "traceability": {
    "reason_graph_node_id": "string",
    "constraint_check_id": "string | null",
    "related_req_ids": ["string"]
  },
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

## 2. フィールド定義

### 2.1 intent_id

- 一意識別子。形式: `INT_{YYYYMMDD}_{NNN}`（既存event_id採番規則 `E{YYYYMMDD}_{NNN}` に準拠した命名）。
- 不変。生成後の変更は不可。

### 2.2 source（origin）

- `origin`: このIntentがどこから生成されたかを示す。値の例: `layer3.synthesis`（Intent Synthesisによる自動生成）、`human_gate`（人間による直接指定）、`drift_projection`（Design Drift Projectionによる提案）。
- `originating_event_ids`: このIntentの起点となったLayer 0のevent_id群（任意・空配列可）。MoCKA 1.0のevents.dbとの接続点となる。

### 2.3 priority

- 値: `critical | high | normal | low`
- Intent間の競合解消（§2.4）における優先順位判定に使用する。
- 優先度の決定ロジック自体はLayer 3の実装フェーズで定義し、本スキーマでは値域のみを定義する。

### 2.4 stability

- 値: `experimental | provisional | stable`
- Intentがどの程度「確定的」かを示す。
  - `experimental`: Intent Synthesisによる生成直後。Layer 1検証前。
  - `provisional`: Layer 1検証を通過したが、運用実績が浅い。
  - `stable`: 運用実績があり、Design Drift Projectionの基準点として参照可能。
- stabilityの遷移は、Layer 1の検証結果とLayer 2のDrift Semantics Engineの観測に基づく（遷移条件はLayer 1/2実装時に定義）。

### 2.5 lifecycle_state

- 値: `draft | active | resolved | deprecated`
  - `draft`: Intent Synthesisにより生成されたが、Layer 1検証未通過。
  - `active`: Layer 1検証を通過し、Execution（Layer 0）への影響を持ちうる状態。
  - `resolved`: 目的を達成し終了した、または別Intentに統合された。
  - `deprecated`: 意味的に無効化された（Semantic Compressionにより圧縮・吸収された場合も含む）。
- `draft → active` の遷移は必ずLayer 1のConstraint検証を経る（ARCHITECTURE §3 P4）。

### 2.6 conflict（conflict representation）

- `conflicts_with`: 競合関係にある他のintent_idのリスト。
- `resolution_state`: `none | open | resolved`
- `resolution_intent_id`: 競合解消の結果として生成されたIntent（Intent Conflict Resolutionの出力）のid。未解消の場合は`null`。
- 競合の検出自体はLayer 3（Intent Conflict Resolution）が行い、本フィールドはその結果の記録のみを担う。

### 2.7 dependency links

- `depends_on`: このIntentが前提とする他Intentのid群。
- `required_by`: このIntentに依存する他Intentのid群（`depends_on`の逆参照。整合性はLayer 2のIntent Graph構築時に保証する）。

### 2.8 traceability hooks

- `reason_graph_node_id`: Layer 2のDecision Reason Graph上で、このIntentに対応するノードのid。「なぜこのIntentが生成されたか」を遡るためのフック。
- `constraint_check_id`: Layer 1のValidation Engineによる検証結果のid。`lifecycle_state`が`draft`の間は`null`。
- `related_req_ids`: 1.0のREQ Change History（Layer 2）と紐づくREQ識別子群。MoCKA 2.0は「REQとの差分」ではなく「意図差分」を扱うが、既存REQとの接続点として保持する。

### 2.9 created_at / updated_at

- ISO8601形式のタイムスタンプ。`updated_at`はlifecycle_state・conflict・dependenciesのいずれかが変更された際に更新する。

## 3. Event → Intent との関係（最小定義）

- 1つのEvent（events.db）は0個以上のIntentの`originating_event_ids`に登場しうる（1.0との後方互換）。
- 1つのIntentは0個以上のEventを起点として持つ。Intentの存在はEventの存在を前提としない（`origin: "human_gate"` や `"drift_projection"` のように、Eventなしで生成されるIntentを許容する）。
- Decision back-propagation（Event → Intentへの逆参照付与）は、Intent Graph構築（実装順序Step 2）で扱う。本書はそのためのフィールド（`source.originating_event_ids`, `traceability.reason_graph_node_id`）のみを定義する。

## 4. 本書の範囲外

以下はLayer 3 prototype以降の実装フェーズで定義し、本書では扱わない：

- priority / stabilityの自動算出ロジック
- Intent Conflict Resolutionの具体的アルゴリズム
- Semantic Compressionによるintentの統合・圧縮ルール
- Design Drift Projectionの出力形式

## 5. 次フェーズへの接続

本スキーマ確定後、実装順序Step 2（Intent Graph構築：Event → Intent mapping / Decision back-propagation）に移行する。
