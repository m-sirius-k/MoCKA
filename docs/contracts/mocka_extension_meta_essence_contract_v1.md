# MoCKA Extension - Meta-Essence Contract v1 (Semantic Compression Layer)

Status: DRAFT(裁定済み構造、スキーマ確定。実装はまだ無し)
Date: 2026-06-24
裁定者: Human Gate(きむら博士)
作成者: Claude-sonnet-4-6

## 0. 本契約の位置づけ

本契約は既存のFROZEN構造を置き換えるものではない。
既存の Event Layer 最小定義(Core Event) / Essence pipeline(既存4系統) /
Phase10-3 Signal Non-Layer Contract / Phase10-Stasis制約は、
本契約により一切変更されない。

既存Essence pipeline(Drift Monitor / tech_watcher / Essence pipeline /
Advisorの4系統の一つ)と本契約のmeta-essenceは別系統であり、
"parallel essence layer"として競合させない。統合・置換は禁止。

本契約はMoCKA extension(index / event-analytic / meta-essence)の
第3要素である meta-essence を定義する。

## 1. 基本定義

meta-essence は次のように定義される。

「indexグラフ上のAnalytical Event群を入力とし、非破壊的に意味構造を
再圧縮した派生レイヤ」

重要な制約:

- Core Event には一切戻らない。
- Analytical Event の「関係構造のみ」を対象とする。
- index は入力、meta-essence は出力。

全体構造(最終形):

```
Core Event
   |
   v
Analytical Event
   |
   v
index (trace graph)
   |
   v
meta-essence (semantic compression layer)
```

## 2. 入力対象

meta-essence が扱うのは以下のみ。

- index_entry graph
  ([mocka_extension_index_contract_v1.md](mocka_extension_index_contract_v1.md)
  で定義したグラフ構造)
- Analytical Event set
  ([mocka_extension_analytical_event_contract_v1.md](mocka_extension_analytical_event_contract_v1.md)
  で定義したエンティティ)

禁止:

- Core Event の直接参照
- raw event の再評価
- 新規事実生成

## 3. 出力構造(最小スキーマ)

```json
{
  "meta_id": "string",
  "source_range": {
    "from_index_id": "string",
    "to_index_id": "string"
  },
  "compression_type": "semantic_cluster | drift_summary | causal_fold",
  "derived_nodes": [
    {
      "meta_node_id": "string",
      "meaning_vector": "string",
      "weight": "float",
      "source_refs": ["analytic_event_id"]
    }
  ],
  "relations": [
    {
      "type": "compression_link | abstraction_link",
      "from": "string",
      "to": "string"
    }
  ],
  "trace_signature": "string"
}
```

## 4. 再構成ルール(核心)

### 4.1 圧縮のみ許可

- 新しい事実の生成は禁止する。
- 意味の「再配置」のみ許可する。

### 4.2 クラスタ単位生成

meta-essence は必ず以下のいずれかを入力単位とする。

- index の連続区間
- 意味的クラスタ

### 4.3 多重解釈禁止

- 1つの meta_node は1つの意味圧縮結果のみを表す。
- 曖昧な多義構造は禁止する。
- 分岐が必要な場合は relations で表現する(meta_nodeを多義化しない)。

## 5. compression_type 定義

- `semantic_cluster`: 意味的まとまりの抽出
- `drift_summary`: 時系列変化の要約
- `causal_fold`: 因果構造の折り畳み

## 6. trace_signature(整合性保証)

```
trace_signature = hash(
  index_range +
  analytic_event_ids +
  compression_type
)
```

この trace_signature は index の trace_hash、Analytical Event の
trace_hash とは別物であり、それぞれの層で独立に検証する。

## 7. indexとの関係

- index = 構造(graph)
- meta-essence = 意味圧縮(projection)
- index は「全部保持」する。
- meta-essence は「再構成」する。

## 8. 禁止事項(FROZEN保護)

- Core再評価の禁止
- Event再生成の禁止
- index改変の禁止(meta-essenceはindexを読むだけで、書き換えない)
- meta-essence から index への逆書き込みの禁止
- 既存Essence pipeline(4系統)との統合・再分類の禁止

## 9. 実装状態

本契約は再構成レイヤの構造定義のみであり、コード・テーブル・
アルゴリズム実装は一切着手していない。実装着手にはHuman Gateの
明示指示を要する。
