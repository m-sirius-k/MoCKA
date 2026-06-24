# MoCKA Extension - Index Contract v1 (Trace Graph Type)

Status: DRAFT(裁定済み構造、スキーマ確定。実装はまだ無し)
Date: 2026-06-24
裁定者: Human Gate(きむら博士)
作成者: Claude-sonnet-4-6

## 0. 本契約の位置づけ

本契約は既存のFROZEN構造を置き換えるものではない。
既存の Event Layer 最小定義(Core Event) / Essence pipeline(既存4系統) /
Phase10-3 Signal Non-Layer Contract / Phase10-Stasis制約は、
本契約により一切変更されない。

本契約はMoCKA extension(index / event-analytic / meta-essence)の
第2要素である index を定義する。index は
[mocka_extension_analytical_event_contract_v1.md](mocka_extension_analytical_event_contract_v1.md)
で確定したAnalytical Eventを唯一のノード種別とするトレースグラフである。

## 1. 基本定義

index は次の三層グラフとして定義される。

- Node(頂点): Analytical Event のみ
- Edge(辺):
  - core_ref(Analytical Eventが内部に保持する、Core Eventへの参照。
    グラフのエッジとしては表現しない。参照のみ)
  - temporal_link(時間順接続)
  - derivation_link(派生関係、meta-essence層との接続用)

### 1.1 Core Eventのノード化禁止(確定裁定)

Core Event は index に単独ノードとして登場しない。
すべての index_entry は必ず1つの Analytical Event に紐づく。
Core Event は常に「参照先としてのみ存在」し、グラフ構造には入らない。

構造図(確定形):

```
Core Event (FROZEN, immutable source)
        |
        v  reference only
Analytical Event (observational node)
        |
        v
index_entry (graph node)
        |
        v
graph structure (trace / sequence / derivation)
```

設計原理: 「事実はグラフに入らない、観測だけが構造化される」。

## 2. データ構造(最小スキーマ)

```json
{
  "index_id": "string",
  "analytic_event_id": "string (必須。Analytical Eventへの参照)",
  "core_ref": "string (必須。ただし参照のみ、グラフのノード化はしない)",
  "timestamp": "int",
  "prev_index_id": "string | null",
  "trace_hash": "string",
  "layer": "analytical (固定値。'core'は廃止・非推奨)",
  "relation": {
    "type": "ref | sequence | derivation",
    "target_id": "string"
  },
  "meta": {
    "inserted_at": "int",
    "version": "string"
  }
}
```

`layer`フィールドは将来の互換性のために残すが、本v1では
`"analytical"`固定とする。`"core"`値は廃止・非推奨であり、
新規index_entryに使用してはならない。

## 3. グラフ構造ルール

### 3.1 Core -> Analytical(固定参照、エッジ化しない)

- Analytical Event は必ず1つの core_ref を持つ。
- 多対1は許容される(Core 1 -> Analytical N)。
- この関係は index のグラフエッジとしては表現しない
  (Core Eventがノードではないため)。

### 3.2 時系列リンク(sequence)

- `prev_index_id` で連結する。
- append-only を保証する。
- 分岐は許可しない(線形ストリーム)。

### 3.3 派生リンク(derivation)

- meta-essence はこの層でのみ index に接続できる。
- Core Event / Analytical Event の実体に対する直接接続は禁止。

## 4. 不変性ルール(重要)

- index_entry は完全append-onlyである。
- 既存entryの書き換えを禁止する。
- 削除を禁止する(論理無効化も禁止)。
- すべて trace_hash で検証可能でなければならない。

## 5. trace_hash仕様

```
trace_hash = hash(
  core_ref +
  analytic_event_id +
  prev_index_id +
  timestamp +
  relation.type +
  relation.target_id
)
```

この trace_hash は
[mocka_extension_analytical_event_contract_v1.md](mocka_extension_analytical_event_contract_v1.md)
で定義した Analytical Event 自身の trace_hash とは別物である。
両者を混同しないこと。

## 6. 役割分離(FROZEN構造保護)

| 層 | 役割 | 変更可否 |
|---|---|---|
| Event Core | 事実生成 | 固定(変更禁止) |
| Analytical Event | 投影生成 | 固定(本契約上位、変更には別契約の再裁定を要する) |
| index | 接続・追跡 | 追加のみ(append-only) |
| meta-essence | 再構成 | 後段(別契約で定義) |

Core / 既存Essence pipeline には一切干渉しない設計とする。

## 7. 構造的意味

このindexは単なる保存ではなく、以下として機能する。

- 「意味の移動経路」
- 「観測履歴」
- 「再構成可能な因果グラフ」

ただし、これは「事実のネットワーク」ではなく「観測(Analytical Event)
同士の意味のネットワーク」である点に注意する。Core Eventという
事実そのものはグラフの外に常に存在する。

## 8. 実装状態

本契約はグラフ構造定義のみであり、コード・テーブル・実装は一切
着手していない。実装着手にはHuman Gateの明示指示を要する。
