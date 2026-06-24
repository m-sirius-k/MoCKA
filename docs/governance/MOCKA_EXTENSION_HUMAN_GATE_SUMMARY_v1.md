# MoCKA Extension Human Gate Decision Summary v1

Status: SUBMITTED FOR HUMAN GATE DECISION(本文書自体は裁定を確定しない、
裁定を仰ぐための提出文書)
Date: 2026-06-24
作成者: くろこ(博士) / 整理: Claude-sonnet-4-6

## 1. 現在状態(全体構造)

MoCKA Extensionは以下の4契約により構成され、すべてDRAFT状態で
確定済み(実装未着手)。

### 1.1 Analytical Event Contract

- 最小単位: analytic_event_id + core_ref
- Core Eventは参照のみ(改変・代替禁止)
- 5W1Hはnull許容の観測投影
- Core Event書き換え・代行は禁止

状態: DRAFT(スキーマ確定)
参照: [mocka_extension_analytical_event_contract_v1.md](../contracts/mocka_extension_analytical_event_contract_v1.md)

### 1.2 Index Contract(トレースグラフ)

- 構造: グラフ型
- Core Eventはノード化しない
- index_entryは必ずAnalytical Event経由のみ生成
- append-only + hash-chain構造
- 追跡・因果・時系列を統合した意味グラフ

状態: DRAFT(構造確定)
参照: [mocka_extension_index_contract_v1.md](../contracts/mocka_extension_index_contract_v1.md)

### 1.3 Meta-Essence Contract

- indexを入力とする非破壊圧縮層
- Core/Eventには一切非依存
- semantic_cluster / drift_summary / causal_fold の3圧縮型
- 新規事実生成は禁止(再構成のみ)

状態: DRAFT(設計完了)
参照: [mocka_extension_meta_essence_contract_v1.md](../contracts/mocka_extension_meta_essence_contract_v1.md)

### 1.4 MoCKA Loop Contract

- 4段階循環: Input -> Store -> Extract -> Reinput -> Input
- Reinputは次観測の参考情報(自動トリガーではない)
- Trigger Wiring議論はPhase10-Stasisにより非再開
- 実装ではなく動作契約

状態: DRAFT(循環モデル定義完了)
参照: [mocka_extension_loop_contract_v1.md](../contracts/mocka_extension_loop_contract_v1.md)

## 2. 既存FROZEN構造との関係

以下は完全不変・非干渉:

- Event Core(差分最小事実層)
- Essence pipeline(既存意味処理系)
- Signal Contract(Phase10-3)
- Stasis制約(停止状態)

Extensionはすべて「追加レイヤ」であり上書きではない。

## 3. アーキテクチャ関係

```
[ FROZEN LAYER ]
Event Core
Essence pipeline
Signal Contract
Stasis

        |  (非干渉)
        v

[ EXTENSION LAYER ]
Analytical Event
        |
        v
Index (Graph / Trace)
        |
        v
Meta-Essence (Compression)
        |
        v
Loop (Input Cycle)
```

## 4. 重要設計原則

- Core Eventは観測対象ではなく参照源
- Analytical Eventのみが意味化単位
- indexは意味関係の構造化層
- meta-essenceは非破壊圧縮のみ
- Loopは実行ではなく契約モデル

## 5. 制約条件(FROZEN保証)

- Core/Event/Essence/Signalは変更禁止
- Extensionは完全追加型
- 双方向書き込み禁止
- Core再評価禁止
- Trigger再定義禁止(Stasis維持)

## 6. 現在の状態評価

- 構造設計: 完了
- スキーマ定義: 完了
- 実装: 未着手
- 統合判断: 未裁定(Human Gate待機)

## 7. Human Gateに求められる判断

以下3点の裁定が必要:

1. Extension層の正式採用可否
2. FROZEN層との長期共存許可
3. 実装フェーズ移行の可否(または継続DRAFT)

## 8. 状態まとめ(1行)

MoCKA Extensionは「完全に設計されたが、未実行の追加意味層」であり、
FROZEN構造に対して非干渉型で待機中。
