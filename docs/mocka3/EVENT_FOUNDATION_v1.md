# MoCKA Event Foundation v1

**Document ID**: EVENT_FOUNDATION_v1  
**Version**: 1.0.1  
**Status**: Active  
**Created**: 2026-06-15  
**Reference Event**: E20260615_032  

---

## Design Principles

| ID | Principle |
|----|-----------|
| P1 | Raw data is immutable. |
| P2 | Every transformation is explainable. |
| P3 | Rejected records are preserved. |
| P4 | Provenance is never discarded. |
| P5 | Normalization must be deterministic. |

これらの原則はすべての章の設計判断の根拠となる。解釈が衝突した場合、P1が最優先される。

---

## 1. Philosophy

### 1.1 Goals

MoCKA Event Foundation v1 は以下を達成することを目的とする。

1. MoCKA全モジュール（Orchestra / Relay / Memory / TIC / PHI OS）が共通の「イベント言語」で通信できる基盤を提供する
2. イベントの生成・受理・変換・保存・棄却の全過程を監査可能にする
3. 将来の拡張（Event Foundation v2）に対してスキーマバージョニングで対応できる構造にする
4. 論文（p-DERS / AIES）に対して「実運用で検証されたイベントモデル」としての証拠を提供する

### 1.2 Immutable Archive

既存の `events.db` は **歴史アーカイブ** として永久保存する。

- 一切の UPDATE / DELETE を行わない
- 新しいイベントは `events_v2.db` にのみ書き込む
- 移行（Migration）時も元データは `events.db` に残る

根拠: P1（Raw data is immutable）

### 1.3 Explainability

すべての変換（Normalization）とすべての棄却（Rejection）は記録される。

- 「なぜ NORMALIZED になったか」は `validation_result` で追跡できる
- 「なぜ REJECTED になったか」は `rejected_rows.jsonl` で追跡できる
- 数年後に「このデータはどうなったか」を答えられる状態を維持する

根拠: P2 / P3

---

## 2. Architecture

### 2.1 4-Layer Pipeline

```
┌─────────────────────────────────────────┐
│  events.db  (Immutable Archive)         │
│  ※ 既存データ。一切変更しない            │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼───────┐
         │   Importer    │
         │  (読み取り専用) │
         └───────┬───────┘
                 │
         ┌───────▼───────┐
         │   Validator   │
         └───────┬───────┘
                 │
        ┌────────┴────────┐
        │                 │
  ┌─────▼──────┐   ┌──────▼──────────────┐
  │  Accepted  │   │      Rejected       │
  └─────┬──────┘   │  rejected_rows.jsonl│
        │           └─────────────────────┘
 ┌──────▼──────┐
 │  Normalizer │
 └──────┬──────┘
        │
 ┌──────▼──────┐
 │ events_v2   │
 │  (.db)      │
 └─────────────┘
```

### 2.2 Data Flow

| 段階 | 入力 | 出力 | 変更 |
|------|------|------|------|
| Importer | events.db (read-only) | Raw Record | なし |
| Validator | Raw Record | Accept / Reject | なし |
| Normalizer | Accepted Record | Normalized Record | フィールド補正 |
| events_v2 | Normalized Record | 永続化 | 書き込みのみ |

---

## 3. Event Model

### 3.1 Event Identity

イベントは **Identity** と **Provenance** の2つの概念を持つ。

```
Event
├── Identity
│   ├── event_id       ← 永続的な識別子
│   └── schema_version ← スキーマバージョン
└── Provenance
    ├── source_db      ← 出自DB (例: "events.db")
    ├── source_table   ← 出自テーブル (例: "events")
    └── source_rowid   ← 出自行ID (例: 18391)
```

**Identity** はイベントそのものを一意に識別する。  
**Provenance** はそのイベントがどこから来たかを示す。

Provenanceは「移行されたデータが100%追跡可能であること」を保証する（P4）。

### 3.2 Event ID 仕様

```
形式: E{YYYYMMDD}_{NNN}
例:   E20260615_032

- E      : 固定プレフィックス
- YYYYMMDD : 発生日（UTC）
- NNN    : その日の通し番号（3桁ゼロ埋め）
```

Event ID以外の文字列（例: `FIREBASE_PROJECT_ID`）はValidatorで即時 REJECTED。

### 3.3 Event Schema（events_v2 テーブル定義）

```sql
CREATE TABLE events_v2 (
    -- Identity
    event_id         TEXT    NOT NULL PRIMARY KEY,
    schema_version   INTEGER NOT NULL DEFAULT 1,

    -- Core Fields
    what_type        TEXT    NOT NULL,  -- Taxonomy準拠 or "UNSPECIFIED"
    who_actor        TEXT    NOT NULL,  -- AI名・人名・システム名のみ
    when_ts          TEXT    NOT NULL,  -- ISO 8601形式のみ
    title            TEXT    NOT NULL,  -- 1行サマリー
    description      TEXT,             -- 詳細本文
    tags             TEXT,             -- カンマ区切り

    -- Validation
    validation_status TEXT   NOT NULL,  -- VALID/NORMALIZED/LEGACY/RECOVERED/REJECTED
    validation_result TEXT,             -- JSON: {"EV001":"PASS","EV002":"FIXED",...}

    -- Provenance
    source_db        TEXT    NOT NULL DEFAULT 'new',
    source_table     TEXT,
    source_rowid     INTEGER,

    -- Metadata
    metadata         TEXT,             -- JSON blob (任意の補足情報)

    -- Timestamps
    created_at       TEXT    NOT NULL  -- INSERT時のタイムスタンプ (ISO 8601)
);
```

### 3.4 NULL / UNSPECIFIED / UNKNOWN の区別

| 値 | 意味 | 使用場面 |
|----|------|----------|
| `NULL` | 項目自体が該当しない | source_rowid（新規イベントには元行IDがない）|
| `"UNSPECIFIED"` | 記録時に未指定だった | what_typeが空欄だったイベント |
| `"UNKNOWN"` | 存在するが内容が不明 | who_actorが判別不能だった場合 |

### 3.5 Schema Version

```
schema_version = 1  (本仕様)
```

将来 Event Foundation v2 に移行する際、`schema_version` フィールドで旧レコードを識別できる。すべての新規イベントは `schema_version = 1` を必須とする。

---

## 4. Validation

### 4.1 Validation Rules

| Rule ID | 対象フィールド | 検査内容 | 失敗時の扱い |
|---------|--------------|----------|-------------|
| EV001 | event_id | `E{YYYYMMDD}_{NNN}` 形式 | REJECTED |
| EV002 | when_ts | ISO 8601 形式 | FIXED（Normalizer委譲）|
| EV003 | what_type, who_actor, title | 必須フィールド存在確認 | FIXED or REJECTED |
| EV004 | 全フィールド | UTF-8 エンコーディング確認 | FIXED（BOM除去等）|
| EV005 | who_actor | パス・ハッシュ・日付でないこと | FIXED（metadataへ移動）|

### 4.2 Validation Result（Rule単位）

各Ruleの結果を `validation_result` フィールドにJSON配列形式で記録する。

```json
[
  { "rule": "EV001", "result": "PASS" },
  { "rule": "EV002", "result": "FIXED", "message": "Converted to ISO 8601" },
  { "rule": "EV003", "result": "PASS" },
  { "rule": "EV004", "result": "FIXED", "message": "BOM removed" },
  { "rule": "EV005", "result": "PASS" }
]
```

配列形式を採用する理由：将来 `reason` / `severity` / `message` フィールドを追加できる拡張性を確保するため。

| 値 | 意味 |
|----|------|
| `PASS` | 検査通過 |
| `FIXED` | 問題を検出し Normalizer が修正した |
| `FAIL` | 修正不能 → REJECTED |

### 4.3 Validation Status（イベント全体）

`validation_status` は **events_v2 に格納されたレコードの状態** を示す。

`REJECTED` は Validator の判定結果であり、events_v2 には存在しない。  
REJECTED レコードは `rejected_rows.jsonl` にのみ保存される（Section 8参照）。

| validation_status | 条件 | 格納先 |
|-------------------|------|--------|
| `VALID` | 全Rule PASS | events_v2 |
| `NORMALIZED` | 1件以上 FIXED、0件 FAIL | events_v2 |
| `LEGACY` | 旧フォーマット由来・修正して受理 | events_v2 |
| `RECOVERED` | データ欠損を補完して受理 | events_v2 |
| ~~`REJECTED`~~ | 1件以上 FAIL → **events_v2には入らない** | rejected_rows.jsonl |

> **監査上の重要事項**: `SELECT * FROM events_v2 WHERE validation_status='REJECTED'` は常に0件を返す。これが正常状態である。

---

## 5. Normalization

Normalizerは Accepted レコードに対して、以下の変換を **決定論的（Deterministic）** に行う（P5）。

| 変換対象 | 変換内容 |
|----------|----------|
| `when_ts` | 非ISO8601文字列を `metadata.original_timestamp` に移動し、推定値または `UNSPECIFIED` を設定 |
| `who_actor` | パス・ハッシュ・日付は `metadata.original_actor` に移動し、`UNKNOWN` を設定 |
| `what_type` | 空文字は `UNSPECIFIED` に変換 |
| エンコーディング | BOM除去・Shift-JIS変換等 |

**Normalizerのメタデータ記録例（名前空間付き）：**

```json
{
  "migration": {
    "source": "csv_import",
    "migrated_at": "2026-06-15T09:59:50Z"
  },
  "normalizer": {
    "version": "1.0",
    "original_actor": "interface/router.py",
    "original_timestamp": "N/A",
    "rules_applied": ["EV002", "EV005"]
  },
  "legacy": {
    "original_format": "csv_v1"
  }
}
```

名前空間（`migration` / `normalizer` / `legacy` / `tic` 等）を最初から分けることで、将来モジュールが独自フィールドを追加できる。例：TICが `"tic": { "prediction": {...} }` を追加する場合など。

---

## 6. Taxonomy

> **Note**: Event Taxonomy は本仕様から独立した仕様書 `EVENT_TAXONOMY_v1.md` で管理する。  
> Event Foundation v1 は Taxonomy を「保持する器」であり、Taxonomy の内容自体はここでは定義しない。

### 6.1 設計方針

> カテゴリがイベントを決めるのではなく、イベントからカテゴリを導く。

### 6.2 Taxonomy との関係

```
EVENT_FOUNDATION_v1.md  ← 本仕様
    └── what_type フィールド ← Taxonomy準拠の値を格納する器

EVENT_TAXONOMY_v1.md  ← 別仕様（TODO_301-D）
    └── what_type に入れてよい値の定義
```

`what_type` に入れてよい値は `EVENT_TAXONOMY_v1.md` が権威ある定義源となる。  
本仕様では `what_type` が `TEXT NOT NULL` であること、および Taxonomy 未定義時は `"UNSPECIFIED"` を使用することのみを規定する。

### 6.3 参照: Taxonomy v1 Draft カテゴリ候補

以下は `EVENT_TAXONOMY_v1.md` 策定に向けた参考情報（Draft）。確定値ではない。

| Category | 役割 |
|----------|------|
| `LIFECYCLE` | オブジェクト・セッションの生成・更新・終了 |
| `OPERATIONAL` | 通常の実行・処理・ワークフロー |
| `DECISION` | AIまたはルールによる判断・評価 |
| `AUDIT` | 検証・監査・証跡 |
| `INCIDENT` | エラー・警告・異常 |
| `SYSTEM` | 起動・停止・設定変更・内部状態 |

### 6.4 Layer と Taxonomy の分離

TICで定義された機能層（Explain / Trace / Structure / Cause / Trend / Prediction）は Taxonomy とは独立した軸として管理する。

```
TRACE_CREATED イベント
├── Layer（機能軸）: Trace
└── Taxonomy（性質軸）: LIFECYCLE
```

両軸を `tags` フィールドで表現できる：
```
tags: "layer:trace,category:LIFECYCLE"
```

---

## 7. Migration

### 7.1 Migration 対象

| 移行元 | 移行先 | 方針 |
|--------|--------|------|
| `events.db` / `events` テーブル | `events_v2.db` | Importer → Validator → Normalizer |

### 7.2 Migration Rules

1. 移行は **読み取り専用** で `events.db` にアクセスする
2. `source_db` / `source_table` / `source_rowid` を必ず記録する（P4）
3. 1件の移行失敗が他の件に影響しないようトランザクション単位を分ける
4. 移行完了後に件数検証を行う（元件数 = Accepted + Rejected）

### 7.3 将来の複数DB統合

将来 `tic_events.db` / `orchestra.db` 等が統合される場合、`source_db` の値でオリジンが区別できる。

---

## 8. Rejection Policy

### 8.1 Rejected Records の保存

REJECTEDとなったレコードは削除しない（P3）。

```
保存先: rejected_rows.jsonl (append-only)
```

### 8.2 Rejection Record 形式

```json
{
  "rejected_at": "2026-06-15T09:59:50Z",
  "reason": "EV001_FAIL",
  "failed_rule": "EV001",
  "source_db": "events.db",
  "source_table": "events",
  "source_rowid": 9982,
  "raw_event_id": "FIREBASE_PROJECT_ID",
  "validator_version": "EventValidator v1",
  "raw_snapshot": { ... }
}
```

### 8.3 既知の Rejection パターン

| パターン | 件数（調査時点） | 原因 | 対応 |
|----------|----------------|------|------|
| `what_type` 空文字 | 24件 | csv_migration由来 | REJECTED または UNSPECIFIED変換 |
| `event_id` 非形式 | 数件 | Firebase ID等が混入 | REJECTED |
| `what_type` 自然文 | 数件 | 自由記述ログが混入 | REJECTED |

---

## 9. Compatibility

### 9.1 既存コードとの共存

- 既存の `mocka_write_event()` は引き続き `events.db` に書き込む
- Event Foundation v1 が安定するまで両DBを並行運用する
- 移行完了後、新規イベントは `events_v2.db` のみへ書き込む

### 9.2 MCP Server 対応

`mocka_write_event` MCPツールは Event Foundation v1 採用後、以下の変換を行う：

1. Validation Rules (EV001〜EV005) を適用
2. `validation_status` を付与
3. `events_v2.db` に INSERT

---

## 10. Future Extensions

| 拡張項目 | 概要 | 条件 |
|----------|------|------|
| Event Foundation v2 | schema_version=2 への移行 | v1で1年以上の運用実績後 |
| Multi-DB Unified View | 複数DBの統合ビュー | 全モジュールがv1準拠後 |
| Taxonomy v2 | TIC Recommendation連携 | TODO_320完了後 |
| Event Streaming | リアルタイムイベント配信 | AI Connector Framework完了後 |

---

## 11. Invariants

本仕様の **不変条件（Invariants）** を定義する。これらは実装のいかなる段階においても破ってはならない。

| ID | Invariant |
|----|-----------|
| I1 | `events.db` is immutable. No UPDATE or DELETE is ever performed. |
| I2 | Rejected records are never deleted. They are preserved in `rejected_rows.jsonl`. |
| I3 | Every accepted event in `events_v2` has provenance (`source_db`, `source_table`, `source_rowid`). |
| I4 | Every normalized field preserves the original value in `metadata.normalizer`. |
| I5 | `schema_version` is immutable once written. |

これらは Design Principles (P1〜P5) を実装レベルで具体化したものである。実装者はコードレビュー時に I1〜I5 が守られていることを確認する。

---

## Appendix A: 用語定義

| 用語 | 定義 |
|------|------|
| Event | MoCKAシステム内で発生した記録すべき出来事の最小単位 |
| Event Identity | イベントを一意に識別するための情報 (event_id + schema_version) |
| Provenance | イベントの出自情報 (source_db + source_table + source_rowid) |
| Taxonomy | イベントをカテゴリ別に分類する体系 |
| Importer | events.dbからレコードを読み取る層（読み取り専用） |
| Validator | Event SchemaへのRule適合性を検査する層 |
| Normalizer | 受理されたレコードをスキーマ準拠に変換する層 |
| Rejected Record | Validator で FAIL となり events_v2 に取り込まれなかったレコード |

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.1 | Active | 2026-06-15 |

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| 1.0.0 | 2026-06-15 | 初版作成（E20260615_032） |
| 1.0.1 | 2026-06-15 | REJECTED を validation_status から分離・validation_result を配列形式に変更・metadata 名前空間導入・Taxonomy を EVENT_TAXONOMY_v1.md へ独立・Invariants (I1-I5) 追加 |
