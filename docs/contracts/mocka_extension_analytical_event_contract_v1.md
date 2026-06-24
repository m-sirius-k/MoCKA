# MoCKA Extension - Analytical Event Contract v1

Status: DRAFT(裁定済み構造、スキーマ確定。実装はまだ無し)
Date: 2026-06-24
裁定者: Human Gate(きむら博士)
作成者: Claude-sonnet-4-6

## 0. 本契約の位置づけ

本契約は既存のFROZEN構造を置き換えるものではない。
既存の Event Layer 最小定義(Core Event) / Essence pipeline(既存4系統) /
Phase10-3 Signal Non-Layer Contract / Phase10-Stasis制約は、
本契約により一切変更されない。

本契約が定義する Analytical Event は、MoCKA extension という
独立追加レイヤ(index / event-analytic / meta-essence)の最小単位である。

位置づけ:
- 既存MoCKA = 制御系・監査系(変更禁止)
- MoCKA extension = 再現性・意味履歴系(本契約の対象)

## 1. Core Event と Analytical Event の関係(二重化原則)

| 項目 | Core Event(既存・不変) | Analytical Event(本契約・新規) |
|---|---|---|
| 役割 | 差分の成立判定 | 差分の意味投影 |
| 成立条件 | 差分発生/記録成功/baseline参照完了の3点のみ | core_refを通じてCore Eventを参照するだけ |
| 意味付け | 禁止(意味付け/重要性評価/因果分析/良否判断は一切行わない) | 意味構造を保持してよい(ただしCoreを書き換えない) |
| 主語 | 差分そのもの | 差分の解釈ではなく差分への参照 |
| 可変性 | immutable | immutable |

Analytical EventはCore Eventの上位版・代替版ではない。
Core Eventが成立した後にのみ、その参照として生成される別概念である。
Core Eventを経由しないAnalytical Eventは存在しない。

## 2. Analytical Event 最小スキーマ

```json
{
  "analytic_event_id": "string (一意識別子、例: AE20260624_xxxxxxxx)",
  "core_ref": "string (Core EventのEvent ID。必須。Core側へのポインタのみ、書き換え不可)",
  "timestamp": "string (ISO8601, 生成時刻)",
  "projection_type": "analytic (固定値、将来の拡張余地として保持するが本v1では変更不可)",
  "analytic_diff": {
    "who": "string (発言者/発生主体)",
    "what": "string (何が変化したか)",
    "when": "string (いつ、core_refのtimestampと整合)",
    "where": "string (どのファイル/モジュール/系統)",
    "why": "string (任意。不明な場合は null を許容)",
    "how": "string (任意。不明な場合は null を許容)"
  },
  "context_id": "string (関連する作業セッション/裁定/Phase等の識別子)",
  "trace_hash": "string (sha256。core_ref + analytic_diff の内容から算出し再現性を保証する)",
  "version": "string (スキーマバージョン、本v1では \"1.0\" 固定)"
}
```

## 3. フィールド規則

- `analytic_event_id` と `core_ref` は必須。他のフィールドが欠落していても
  この2点が無ければAnalytical Eventとして成立しない。
- `analytic_diff` の5W1H各項目はすべて任意(null許容)。ただし全項目nullの
  Analytical Eventは意味を持たないため生成しないこと。
- `trace_hash` は再現性保証のためのものであり、署名(Event Integrity
  Frameworkの signature/hash chain)とは別物である。Analytical Eventは
  Core Eventの署名・ハッシュチェーンに一切関与しない。
- `version` フィールドはスキーマ進化のために予約するが、本v1では
  "1.0" 固定とし、複数バージョン混在の解決ロジックは本契約の対象外。

## 4. 禁止事項(本契約v1の範囲)

- Analytical EventがCore Eventの内容を書き換えること(禁止)
- Analytical EventがCore Eventの代わりに成立判定を行うこと(禁止、
  成立判定は依然Core Eventの3条件のみが行う)
- Analytical Eventに重要性スコア・優先度・ランキングを付与すること
  (本v1の範囲外、将来のmeta-essence層の議論に委ねる)
- Analytical Eventを既存Essence pipeline(4系統)に直接書き込むこと
  (禁止、parallel essence layerの設計が確定するまで接続しない)
- core_refを持たないAnalytical Eventの生成(禁止)

## 5. 次の依存ステップ(本契約の対象外、予告のみ)

本契約はAnalytical Eventの最小スキーマ確定のみを範囲とする。
以下は次回以降の裁定対象であり、本契約では着手しない:

- index(全量append-onlyログ)の設計。Analytical Eventをindexへ
  どう格納するかは本契約では定義しない。
- meta-essence(再構成層)の設計。Analytical Eventの集合からどう
  意味的クラスタを生成するかは本契約では定義しない。
- 二重essenceの干渉防止設計。既存Essence pipelineとmeta-essenceの
  境界・非干渉ルールは本契約では定義しない。

## 6. 実装状態

本契約はスキーマ定義のみであり、コード・テーブル・実装は一切
着手していない。実装着手にはHuman Gateの明示指示を要する。
