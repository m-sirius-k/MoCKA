# MoCKA Event Data Lifecycle v1

**Document ID**: EVENT_DATA_LIFECYCLE_v1  
**Version**: 1.0.0  
**Status**: Active  
**Created**: 2026-06-15  
**Depends On**: EVENT_FOUNDATION_v1.md (v1.0.1)  
**Reference Event**: E20260615_032  

---

## 1. Purpose

本仕様は、MoCKAシステム内でイベントデータが生まれてから役目を終えるまでの **ライフサイクル** を定義する。

EVENT_FOUNDATION_v1 が「イベントとは何か」を定義するのに対し、本仕様は「イベントデータがどのように生き、どのように保たれ、どのように終わるか」を定義する。

**本仕様が答える問い：**
- あるイベントデータは今どの状態にあるか
- その状態から次の状態へ移行する条件は何か
- 各状態で何の操作が許可され、何が禁止されるか
- 監査時にデータの来歴をどこまで再構築できるか

---

## 2. Scope

**対象：**
- `events.db` に存在する全レコード（Historical Archive）
- `events_v2.db` に存在する全レコード（Canonical Store）
- `rejected_rows.jsonl` に存在する全レコード（Rejection Archive）

**対象外：**
- MoCKAモジュール内部のメモリ上データ（永続化前）
- Caliber / TIC 等が持つモジュール固有の一時データ

---

## 3. Lifecycle States

イベントデータは以下の6状態を経る。

```
┌─────────────┐
│     Raw     │  events.db に存在する未処理の原データ
└──────┬──────┘
       │ Importer が読み取る
       ▼
┌─────────────┐
│  Validated  │  Validator が Rule を適用した状態
└──────┬──────┘
       │
    ┌──┴──────────────────────────────┐
    │                                 │
    ▼                                 ▼
┌────────────┐                ┌──────────────┐
│  Rejected  │                │  Normalized  │
│(rejected_  │                │(events_v2.db)│
│ rows.jsonl)│                └──────┬───────┘
└────────────┘                       │ 将来拡張
       ※永久保存                      ▼
                              ┌──────────────┐
                              │   Enriched   │  (将来: TIC等が付加情報を追加)
                              └──────┬───────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │   Indexed    │  (将来: 検索インデックス構築)
                              └──────┬───────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │   Archived   │  (長期保管・低アクセス領域)
                              └──────────────┘
```

### 3.1 Logical States

| State | 説明 |
|-------|------|
| `Raw` | 原データ。一切変更しない |
| `Validated` | Validator がRuleを適用した直後 |
| `Rejected` | Validator で FAIL となったレコード |
| `Normalized` | Normalizer が修正・補完したレコード |
| `Enriched` | 付加情報が追加されたレコード（将来） |
| `Indexed` | 全文検索等のインデックスが構築された状態（将来） |
| `Archived` | 長期保管状態（将来） |

> ⚠️ **Enriched / Indexed / Archived は Reserved for future versions. Not implemented in v1.**
> Implementation target: v2.0 or later.

### 3.2 Storage Mapping（実装依存・別セクション）

| State | v1 Storage | Future Options |
|-------|-----------|-----------------|
| Raw | `events.db` | SQLite / Parquet |
| Validated | メモリ上 | SQLite / Parquet |
| Rejected | `rejected_rows.jsonl` | SQLite / Object Storage |
| Normalized | `events_v2.db` | SQLite / Parquet |
| Enriched | `events_v2.db`（将来） | SQLite / Parquet |
| Indexed | 検索インデックス（将来） | Elasticsearch / 他 |
| Archived | アーカイブ領域（将来） | Object Storage / Cold Storage |

> Logical State と Storage は分離して管理する。Storage 実装は将来変更されうるが、Logical State の定義・遷移条件は変更されない。

---

## 4. State Transition Rules

### 4.1 遷移表

| From | Trigger | To | Actor |
|------|---------|----|-------|
| Raw | IMPORT_COMPLETED | Validated | Importer |
| Validated | VALIDATION_PASSED | Normalized | Validator |
| Validated | VALIDATION_FAILED | Rejected | Validator |
| Normalized | ENRICHMENT_COMPLETED | Enriched | Enricher（将来） |
| Enriched | INDEX_COMPLETED | Indexed | Indexer（将来） |
| Indexed | ARCHIVE_TRIGGERED | Archived | ArchiveAgent（将来） |

### 4.2 不可逆遷移

以下の遷移は **不可逆** である。一度この状態に移行したデータは前の状態に戻せない。

| 不可逆遷移 | 根拠 |
|-----------|------|
| Raw → （任意） | P1: Raw data is immutable |
| Validated → Rejected | P3: Rejected records are preserved |

### 4.3 禁止遷移

| 禁止遷移 | 理由 |
|----------|------|
| Raw への書き戻し | I1 違反 |
| Rejected の削除 | I2 違反 |
| Normalized の上書き | P2 違反（変換履歴が失われる）|

### 4.4 Lifecycle Metadata

各イベントレコードは、状態遷移ごとに以下のメタデータフィールドを保持する。

```yaml
lifecycle_metadata:
  entered_at: ISO8601
  entered_by: Actor名（Importer / Validator / Normalizer 等）
  previous_state: 直前の状態
  transition_id: TR_YYYYMMDD_NNN形式
  transition_reason: 自由記述（VALIDATION_FAILED時は必須）
```

---

## 5. Allowed Operations

各状態で許可・禁止される操作を定義する。

| Operation | Raw | Validated | Rejected | Normalized | Enriched | Archived |
|-----------|-----|-----------|----------|------------|----------|----------|
| READ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CREATE | ❌ | ✅ (メモリ) | ✅ (jsonl追記) | ✅ (INSERT) | ✅ (UPDATE) | ❌ |
| UPDATE | ❌ | ❌ | ❌ | ❌ | ⚠️ (付加情報のみ) | ❌ |
| DELETE | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| EXPORT | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

> ⚠️ Enriched状態のUPDATEは `metadata` の特定名前空間への追記のみ許可。既存フィールドの変更は禁止。

**DELETE は全状態で禁止。** MoCKAはデータを消さない。

---

## 6. Immutability Rules

EVENT_FOUNDATION_v1 の Invariants (I1〜I5) をライフサイクル視点で具体化する。

| Rule | 対象状態 | 内容 |
|------|----------|------|
| LR1 | Raw | `events.db` は読み取り専用。書き込みAPIを提供しない |
| LR2 | Rejected | `rejected_rows.jsonl` は append-only。既存行の変更・削除不可 |
| LR3 | Normalized | `events_v2.db` への INSERT 後、`event_id` / `schema_version` / `source_*` フィールドは変更不可 |
| LR4 | Normalized〜Enriched | `metadata.normalizer` 名前空間は書き込み後に変更不可 |
| LR5 | 全状態 | `schema_version` は一度書き込まれたら変更不可（I5） |

---

## 7. Retention Policy

### 7.1 現行ポリシー（v1）

| 格納先 | 保持期間 | 根拠 |
|--------|----------|------|
| `events.db` (Raw) | 永久 | 歴史アーカイブ・不可変（P1） |
| `rejected_rows.jsonl` | 永久 | 監査証跡（P3） |
| `events_v2.db` (Normalized) | 永久 | カノニカルストア |

**v1では全データを永久保持する。** 削除ポリシーは Event Foundation v2 以降で検討。

### 7.2 将来の保持ポリシー候補

| 対象 | 候補ポリシー | 導入条件 |
|------|-------------|----------|
| Archived データ | 5年後に cold storage 移行 | ストレージ容量が問題になった時点 |
| Rejected データ | 10年後に統計情報のみ保持 | 法的要件の確認後 |

---

## 8. Recovery

### 8.1 復元可能な状態

| 失われたもの | 復元方法 | 可否 |
|-------------|----------|------|
| `events_v2.db` | `events.db` + Migration Pipeline を再実行 | ✅ 可能 |
| `rejected_rows.jsonl` | `events.db` + Validator を再実行 | ✅ 可能 |
| `events.db` (Raw) | バックアップから復元のみ | ⚠️ バックアップ依存 |

### 8.2 Recovery の決定論的保証

Normalizer は P5（Normalization must be deterministic）に従うため、同じ入力（`events.db`）に対して Migration Pipeline を再実行すると、同じ `events_v2.db` が生成される。

これにより `events_v2.db` の消失は **完全復元可能** である。

### 8.3 Replay 可能な監査証跡

以下のデータがあれば、任意の時点のシステム状態を再構築できる。

```
events.db
    + EVENT_FOUNDATION_v1.md (v1.0.1)
    + rejected_rows.jsonl
→ events_v2.db を完全再生成可能
```

---

## 9. Audit Requirements

### 9.1 監査で答えられること

本ライフサイクルに従うことで、以下の問いに答えられる。

| 問い | 答えの根拠 |
|------|-----------|
| このイベントはいつ作られたか | `when_ts` + `created_at` |
| 誰が作ったか | `who_actor` |
| どこから来たか | `source_db` / `source_table` / `source_rowid` |
| なぜ NORMALIZED になったか | `validation_result` の FIXED エントリ |
| なぜ REJECTED になったか | `rejected_rows.jsonl` の `reason` / `failed_rule` |
| 元の値は何だったか | `metadata.normalizer.original_*` |
| このデータは改ざんされていないか | `events.db` が不変であることの確認 |

### 9.2 Foundation Invariants との対応

| Invariant | ライフサイクルでの保証方法 |
|-----------|----------------------|
| I1: events.db is immutable | LR1: 書き込みAPIを提供しない |
| I2: Rejected records are never deleted | LR2: append-only ファイル |
| I3: Every accepted event has provenance | LR3: source_* フィールドを必須化 |
| I4: Every normalized field preserves original | LR4: metadata.normalizer 名前空間 |
| I5: schema_version is immutable | LR5: 書き込み後の変更禁止 |

---

## 10. Examples

### 10.1 正常フロー（既存イベントの移行）

```
[Raw] events.db / rowid=18391
  event_id: E20260601_011
  what_type: SESSION_START
  who_actor: Claude
  when_ts: 2026-06-01T07:35:46Z
  ↓ Importer (read-only)
[Validated]
  EV001: PASS (E形式確認)
  EV002: PASS (ISO8601確認)
  EV003: PASS (必須フィールド確認)
  EV004: PASS (UTF-8確認)
  EV005: PASS (who_actor確認)
  ↓ Normalizer
[Normalized] events_v2.db
  validation_status: VALID
  validation_result: [{rule:EV001,result:PASS}, ...]
  source_db: events.db
  source_table: events
  source_rowid: 18391
```

### 10.2 NORMALIZED フロー（who_actor が異常）

```
[Raw] events.db / rowid=9500
  event_id: E20260501_030
  what_type: PIPELINE_RUN
  who_actor: interface/router.py    ← パスが混入
  when_ts: 2026-05-01T10:00:00Z
  ↓ Validator
  EV005: FIXED (who_actorにパスが混入 → Normalizerへ委譲)
  ↓ Normalizer
[Normalized] events_v2.db
  who_actor: UNKNOWN
  validation_status: NORMALIZED
  metadata: {
    "normalizer": {
      "original_actor": "interface/router.py",
      "rules_applied": ["EV005"]
    }
  }
```

### 10.3 REJECTED フロー（Event ID が非形式）

```
[Raw] events.db / rowid=9982
  event_id: FIREBASE_PROJECT_ID    ← 非形式
  what_type: ...
  ↓ Validator
  EV001: FAIL
  ↓ → rejected_rows.jsonl
{
  "rejected_at": "2026-06-15T10:00:00Z",
  "reason": "EV001_FAIL",
  "failed_rule": "EV001",
  "source_db": "events.db",
  "source_table": "events",
  "source_rowid": 9982,
  "raw_event_id": "FIREBASE_PROJECT_ID",
  "validator_version": "EventValidator v1"
}
```

---

## Appendix A: Foundation との依存関係

```
EVENT_FOUNDATION_v1.md
    ├── Design Principles (P1〜P5)  →  本仕様の全Ruleの根拠
    ├── Invariants (I1〜I5)         →  Section 6 LR1〜LR5 で具体化
    ├── Event Schema                →  Section 3 の状態定義の前提
    ├── Validation (EV001〜EV005)   →  Section 4 の遷移条件
    └── Rejection Policy            →  Section 8 の復元可能性の前提

EVENT_DATA_LIFECYCLE_v1.md（本仕様）
    └── 上記を「時間軸」で再定義
```

---

## Appendix B: 変更履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Active | 2026-06-15 |

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| 1.0.0 | 2026-06-15 | 初版作成 |
| 1.0.0 (確定) | 2026-06-15 | 承認条件4点反映: State/Storage分離、Trigger追加、Lifecycle Metadata追加、Reserved States明記 |
