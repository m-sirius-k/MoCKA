# INTENT_GRAPH v1.0

## 0. ステータスと位置づけ

本書は [ARCHITECTURE_MOCKA_2_0_v1.md](ARCHITECTURE_MOCKA_2_0_v1.md)（①固定）および [INTENT_SCHEMA_v1.md](INTENT_SCHEMA_v1.md)（②固定）を前提とする、実装順序Step 2（Intent Graph構築）の基準仕様である。

- Step 1（INTENT_SCHEMA v1）= Intentという単位の**存在定義**（静的定義）
- Step 2（本書）= Intent同士の関係性の**構造化**（動的構造）

MoCKAは「Intent単体の集合」から「意味ネットワーク」へ進化する。

## 1. Graphの本質

Intent Graphとは、Intentをノードとし、意味・依存・競合・時間関係をエッジで表現した構造体である。

## 2. Node

Nodeは [INTENT_SCHEMA_v1.md](INTENT_SCHEMA_v1.md) §1で定義されたIntentオブジェクトそのものである。Step 2はIntentオブジェクトの構造を変更しない。Nodeのidは`intent_id`を用いる。

## 3. Edge types

Intent Graphは単純な依存グラフではなく、4種類のエッジを持つ。

### ① dependency（依存）

```
Intent_A --depends_on--> Intent_B
```

- 実行順序制約。AはBに依存する。
- INTENT_SCHEMA §2.7 `dependencies.depends_on` / `dependencies.required_by`（逆参照）に対応する。

### ② conflict（競合）

```
Intent_A <--conflicts_with--> Intent_B
```

- 同時成立できない意図同士の関係。無向エッジ。
- INTENT_SCHEMA §2.6 `conflict.conflicts_with` / `resolution_state` / `resolution_intent_id` に対応する。

### ③ refinement（詳細化）

```
Intent_A --refines--> Intent_B
```

- 抽象→具体の関係。AはBをより具体化したIntentである。
- INTENT_SCHEMA v1には対応フィールドが存在しないため、新規拡張フィールド `relations.refines` / `relations.refined_by`（逆参照）をIntentオブジェクトに追加する（§6参照）。

### ④ temporal（時間関係）

```
Intent_A --precedes--> Intent_B
```

- 発生順序・履歴。AはBより先に生成された、またはBの前提条件として先行する。
- `created_at`（INTENT_SCHEMA §2.9）から導出可能だが、明示的な先行関係（時系列上の単純な前後関係ではない、意味的な「先行」）を表す場合は新規拡張フィールド `relations.precedes` / `relations.preceded_by` を用いる（§6参照）。

## 4. Graphの3層構造

Intent Graphは単一ネットワークではなく3層に分かれる。

### Layer G0: Local Intent Graph

- 単一コンテキスト内のIntent関係。
- 例: 1つのTODO・1つの変更セッション内で生成されたIntent群とその4種エッジ。

### Layer G1: System Intent Graph

- システム全体のIntent相関。
- G0群を統合した、MoCKA全体のIntentネットワーク。dependency/conflict/refinementエッジが層を越えて接続される。

### Layer G2: Evolution Graph

- 時間軸上のIntent変化。temporalエッジ、およびlifecycle_state遷移（draft→active→resolved/deprecated）の履歴を保持する層。
- ARCHITECTURE_MOCKA_2_0_v1.md Layer 2のDrift Semantics Engineとの統合層であり、Step 3（Semantic Drift Engine）はG2を主たる入力とする。

G0→G1→G2の関係は包含ではなく射影である。G0/G1は「今のネットワーク」を表し、G2はその時系列での変化を表す。

## 5. 設計ルール（R1〜R4）

### R1: Eventは禁止ではなく従属

Eventは Intent Graphのノードではなく、**Trace**として扱う。EventはINTENT_SCHEMA §2.2 `source.originating_event_ids` を通じてIntentに従属する。Graph上の演算（依存解析・競合検出・正規化）はEventを対象としない。

### R2: Conflictは削除しない

`conflicts_with`エッジは「解決対象」として消去するものではなく、**構造情報として保持**する。競合が解消された場合もエッジ自体は残し、INTENT_SCHEMA §2.6 `resolution_state: resolved` および `resolution_intent_id` によって解決済みであることを示す。Graphの履歴的整合性（G2）はこの保持を前提とする。

### R3: Graphは常に非同期進化

Graphはバッチ一括再構築を前提としない。Intentの生成・更新・lifecycle_state遷移ごとに、Graphへの増分反映（インクリメンタル更新）を行う。リアルタイム更新が前提である。

### R4: Intentは必ず多関係を持つ

単一エッジ（孤立ノードに近い状態）は禁止する。新規Intentが生成された時点で、Edge inference（§6 Phase 2-2）により最低限のエッジ（少なくとも`source.originating_event_ids`に基づくtemporalエッジ、または明示された`depends_on`/`refines`のいずれか）を持たない場合、当該Intentは`lifecycle_state: draft`のまま保留され、Layer 1検証（ARCHITECTURE §3 P4）に進めない。

## 6. INTENT_SCHEMA v1への拡張

Step 2に伴い、INTENT_SCHEMA v1のIntentオブジェクトに以下のフィールドを追加する（既存フィールドの変更は行わない、追加のみ）。

```json
{
  "relations": {
    "refines": ["string"],
    "refined_by": ["string"],
    "precedes": ["string"],
    "preceded_by": ["string"]
  }
}
```

- `dependency`（depends_on/required_by）と`conflict`（conflicts_with）はINTENT_SCHEMA v1で定義済みのフィールドをそのまま使用する。
- `refinement`と`temporal`の明示的エッジのみ、本拡張で新設する`relations`に格納する。

## 7. Graph生成パイプライン

### Phase 2-1: Intent ingestion

- INTENT_SCHEMAに準拠するIntentオブジェクトを入力としてNodeを生成する。
- 既存Intent（更新の場合）はNodeの差分更新として扱う。

### Phase 2-2: Edge inference

- `dependencies` / `conflict` / `relations.refines` / `relations.precedes` の各フィールドから4種エッジを生成する。
- R4に基づき、最低限のエッジを持たないIntentは`draft`のまま保留する。

### Phase 2-3: Graph normalization

- 重複Intentの統合: 同一`source.origin`・同一`originating_event_ids`から生成された実質同一のIntentを検出し、`lifecycle_state: deprecated`への遷移と`resolution_intent_id`相当の統合先参照を設定する（統合自体はLayer 3 Semantic Compressionの責務、本フェーズはその入力となるGraph上の重複候補検出のみを担う）。
- ループ検出: `depends_on`エッジによる循環依存を検出する。検出された場合はLayer 1検証を通過させない（draft保留）。

### Phase 2-4: Graph persistence

- versioned graph storage: GraphはG0/G1/G2それぞれをバージョン付きで永続化する。各バージョンはINTENT_SCHEMA §2.9 `updated_at`およびLayer 2 Decision Reason Graphの該当ノードと紐づけ可能であること（traceability hooksとの整合）。

## 8. 次ステップへの接続

Step 2完了後はStep 3（Semantic Drift Engine：意味変化検出）に移行する。Step 3はG2（Evolution Graph）を主たる入力とし、REQとの差分ではなく「意図差分」を検出する。ここで初めてシステムに「進化」が組み込まれる。

## 9. 状態整理

- ARCHITECTURE v1 → 固定済み
- INTENT_SCHEMA v1 → 固定済み（本書§6で追加フィールドのみ拡張）
- INTENT_GRAPH v1（本書） → Step 2 構造定義として確定
