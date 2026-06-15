# MoCKA Event Transition Protocol v1

**Document ID**: EVENT_TRANSITION_PROTOCOL_v1
**Version**: 1.0.0
**Status**: Approved
**Created**: 2026-06-15
**Depends On**: EVENT_FOUNDATION_v1.md (v1.0.1), EVENT_DATA_LIFECYCLE_v1.md (v1.0.0)

---

## 1. Purpose

EVENT_FOUNDATION_v1 と EVENT_DATA_LIFECYCLE_v1 で定義した状態・遷移条件を、**どのように実行するか** を規定する。

実行手順・Actorの責務・トランザクション境界・エラー処理・リトライ・冪等性を定義し、実装者が迷わない仕様とする。

---

## 2. Actors と責務

| Actor | 責務 |
|-------|------|
| Importer | Raw取込・IMPORT_COMPLETED発火 |
| Validator | バリデーション実行・PASSED/FAILED発火 |
| Normalizer | 正規化実行・NORMALIZATION_COMPLETED発火 |
| Enricher | エンリッチ実行（Reserved/v2以降） |
| Indexer | インデックス実行（Reserved/v2以降） |
| ArchiveAgent | アーカイブ実行（Reserved/v2以降） |

---

## 3. 遷移実行手順（v1スコープ）

### 3.1 Raw → Validated

1. Importerが`events.db`から行を取得
2. transition_idを `TR_YYYYMMDD_NNN` 形式で採番
3. Lifecycle Metadataを付与（`entered_at` / `entered_by` / `previous_state` / `transition_id` / `transition_reason`）
4. `events_v2.db`にINSERT
5. `IMPORT_COMPLETED` イベントを発火

### 3.2 Validated → Rejected

1. ValidatorがEV001〜EV005ルール適用
2. FAILルールを `transition_reason` に記録（必須）
3. `rejected_rows.jsonl`にAPPEND（append-only）
4. `VALIDATION_FAILED` イベント発火

### 3.3 Validated → Normalized

1. ValidatorがEV005（FIXED）を検知
2. Normalizerが正規化適用
3. `events_v2.db`のレコードを更新（`validation_status=NORMALIZED`）
4. `NORMALIZATION_COMPLETED` イベント発火

---

## 4. トランザクション境界

- 各遷移は単一トランザクション内で完結すること
- トランザクション失敗時は元の状態を保持（ロールバック）
- 部分書き込み禁止（all-or-nothing）

---

## 5. エラー処理

| エラー種別 | 処置 |
|------------|------|
| DB接続エラー | リトライ3回→ALERT発火→処理停止 |
| バリデーションエラー | Rejected遷移→処理継続 |
| 採番エラー | 処理停止→インシデント記録 |
| 重複transition_id | 処理停止→インシデント記録 |

---

## 6. リトライポリシー

- 対象: DB接続エラーのみ
- 回数: 最大3回
- 間隔: 指数バックオフ（1s / 2s / 4s）
- 上限超過: ALERT → 処理停止 → mocka_write_event記録

---

## 7. 冪等性（Idempotency）

- 同一イベントを2回インポートしても重複しないこと
- 判定キー: `event_id`
- 実装: `INSERT OR IGNORE`（SQLite）またはUPSERT
- `rejected_rows.jsonl`への重複APPEND禁止（`transition_id`で判定）

---

## 8. Reserved遷移（v2以降）

以下の遷移はv1では未実装。仕様のみ定義。

- Normalized → Enriched（ENRICHMENT_COMPLETED）
- Enriched → Indexed（INDEX_COMPLETED）
- Indexed → Archived（ARCHIVE_TRIGGERED）

> ⚠️ Reserved for future versions. Not implemented in v1.

---

## 9. Appendix: Foundation/Lifecycleとの依存関係

```
EVENT_FOUNDATION_v1.md
    └── Validation Rules (EV001〜EV005) → Section 3 遷移条件の根拠
EVENT_DATA_LIFECYCLE_v1.md
    └── State定義・Storage Mapping → Section 3 遷移先の根拠
EVENT_TRANSITION_PROTOCOL_v1.md（本仕様）
    └── 実行手順・責務・エラー処理・冪等性
```

---

## 10. 変更履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| 1.0.0 | 2026-06-15 | 初版作成 |
