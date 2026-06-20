# EVENT_INTEGRITY_v1.md
## Phase5-2 Event Integrity Framework 設計書

**文書番号:** PHI-OS-INTEGRITY-001
**作成日:** 2026-06-20
**フェーズ:** MoCKA Phase 5-2 — Event Integrity Framework 実装
**状態:** IMPLEMENTED v1
**上位文書:** GATE_ARCHITECTURE_v1.md / INSTITUTION_RUNTIME_v1.md

---

## 概要

Phase5-1/5-1.5は「全イベントがGateを経由し、_source列がGate Policyと一致する」
ことを保証した（誰が書いたかの制度）。Phase5-2は「記録後に改ざん・欠落・断絶が
無いことを検証できる」制度（記録後の完全性）を追加する。

4機能を一体で実装する。

1. Event Signature — 全イベントへ署名情報を付与
2. Event Hash Chain — イベントを時系列でハッシュ連結
3. Integrity Verification — Hash一致・チェーン切断・欠番・重複・不正署名・
   不正アルゴリズム・スキーマ整合性を検証
4. Recovery Support — 異常検知時に位置・影響範囲・原因候補・修復候補を診断
   （自動修復は行わない）

---

## モジュール構成

```
phi_os/
    integrity.py          — Signature/Hash Chain/Verification/Recovery/Baseline Sealのコア
    integrity_routes.py    — Verification API (Flask Blueprint)
    event_gate.py          — _write()内でintegrity.sign_event()を呼び出す（既存）
scripts/
    migrate_event_integrity.py  — 既存eventsへの遡及署名Migration
    verify_integrity.py          — Verification CLI
    seal_baseline.py             — Baseline Seal作成（JSON生成 + git tag）
data/
    integrity_baseline.json       — Baseline Seal出力先
    migrate_event_integrity_report.json — Migration実行レポート
```

外部依存: Python標準ライブラリのみ（hashlib, json, sqlite3）

---

## スキーマ — event_signatures

`events`テーブルとは1:1の別テーブル。既存32カラムのeventsを変更せず、
署名・チェーン情報のみを追加的に持つ。

| カラム | 型 | 説明 |
|---|---|---|
| event_id | TEXT PK, REFERENCES events(event_id) | 対象イベント |
| seq | INTEGER NOT NULL UNIQUE | チェーン上の連番（欠番検出の基準） |
| timestamp | TEXT NOT NULL | 署名時のwhen_tsコピー |
| previous_hash | TEXT NOT NULL | 先頭イベントは空文字 |
| current_hash | TEXT NOT NULL | このイベントのハッシュ値 |
| signature_version | TEXT NOT NULL | 署名仕様バージョン（現行: "1.0"） |
| algorithm | TEXT NOT NULL | ハッシュアルゴリズム名（現行: "sha256"） |

定義: `data/mocka_schema_v1.sql`（v1.2）

---

## Signature仕様

- `signature_version = "1.0"`（`phi_os/integrity.SIGNATURE_VERSION`）
- `algorithm`はレジストリ方式（`phi_os/integrity.ALGORITHMS = {"sha256": hashlib.sha256}`）。
  将来別アルゴリズムを追加する場合は、ALGORITHMSへ1行追加しSIGNATURE_VERSIONを
  上げるだけでよく、Verification側のロジック変更は不要。
- 署名対象フィールド（`integrity.SIGNED_FIELDS`）:
  `event_id, when_ts, who_actor, what_type, title, short_summary,
  before_state, after_state, _source, free_note`
- `canonical_payload()`がこれらを`sort_keys=True`のJSONへ正規化する。

---

## Hash Chain仕様

```
current_hash = SHA256(previous_hash + "|" + canonical_payload(event))
```

- `seq`はevent_signatures挿入順の連番。`seq`の欠番がそのまま「行削除」の
  検出条件になる（event_idの語彙順に依存しない設計）。
- 先頭イベント（genesis）の`previous_hash`は空文字。
- 署名は`events`への INSERT と同一トランザクション内で行う
  （`phi_os/event_gate.py:_write()`, `interface/db_helper.py:write_event()`）。
  Gate経由（live/buffered）・許可Direct Write（direct_allowed:*）のいずれも、
  書き込み経路に関わらず同一の署名ロジックでチェーンへ組み込まれる。

---

## Verification API

| エンドポイント | 説明 |
|---|---|
| `GET /api/integrity/verify` | `verify_chain()`の結果（ok/checked/anomalies）を返す |
| `GET /api/integrity/diagnose` | verify_chain結果 + 各anomalyへの診断（diagnose）を返す |
| `GET /api/integrity/baseline` | `data/integrity_baseline.json`の内容を返す |

CLI: `python scripts/verify_integrity.py [--diagnose]`（Flask起動不要）

### 検証項目（STEP3対応）

| 項目 | 実装 |
|---|---|
| Hash一致 | events行から再計算したhashとevent_signatures.current_hashを比較 |
| Chain切断 | 行Nのprevious_hash ≠ 行N-1のcurrent_hash |
| 欠番 | seq列の連番ギャップ |
| 重複 | seqのUNIQUE制約 + events側でevent_signatures未登録の行（unsigned_event） |
| 不正署名 | signature_versionがKNOWN_SIGNATURE_VERSIONSに無い |
| 不正アルゴリズム | algorithmがALGORITHMSレジストリに無い |
| スキーマ整合性 | `interface/schema_audit.audit_schema()`への委譲（対象DBファイルは
  検証対象のconnが実際に開いているファイルを動的に取得する。本番DB_PATHを
  固定参照すると、テスト用DBや別ファイル検証時に不要なロック待ちが発生するため） |

---

## Recovery Support（STEP4）

`integrity.diagnose(anomalies)`がanomaly種別ごとに
`{location, affected_range, candidate_cause, candidate_repair}`を返す。
自動修復は行わない（診断・提案のみ）。代表例:

| anomaly種別 | candidate_cause | candidate_repair |
|---|---|---|
| hash_mismatch | events行がGateを経由しない直接編集で変更された可能性 | 直近のバックアップ(`data/mocka_events_pre_*.db`等)から該当行を復元し再署名 |
| missing_seq | event_signatures行が削除された／署名順序の不整合 | バックアップから該当event_idを特定し再挿入後、以降のseqを再署名 |
| chain_break | previous_hashの改変、または再連結なしの挿入/削除 | バックアップと比較し分岐seqを特定、`migrate_event_integrity.py`で再構築 |
| unsigned_event | Gate/db_helper以外の書き込み経路で署名が漏れた | `migrate_event_integrity.py`で遡及署名 |

---

## Migration

`scripts/migrate_event_integrity.py`は`migrate_source_check.py`と同じ手順
（backup -> table作成 -> backfill -> verify -> JSONレポート）に従う:

1. `event_signatures`が全eventsをカバーしていれば`skipped`。
2. DBファイルをタイムスタンプ付きでバックアップ。
3. `event_signatures`テーブルを作成（未存在時）。
4. `when_ts, event_id`順（実時系列に最も近い既存順序）で未署名イベントを
   1件ずつ`sign_event()`し、チェーンを構築。
5. 直後に`verify_chain()`で検証し、異常があれば`done_with_anomalies`として
   報告する（黙って完了させない）。
6. `data/migrate_event_integrity_report.json`へレポート出力。

---

## Baseline Seal（STEP5）

`scripts/seal_baseline.py`が`data/integrity_baseline.json`を生成する。

```json
{
  "baseline_version": "1.0",
  "git_commit": "<HEAD sha>",
  "schema_version": "1.2",
  "gate_policy_version": "1.0",
  "signature_version": "1.0",
  "hash_algorithm": "sha256",
  "migration_version": "migrate_event_integrity_v1",
  "test_summary": { "passed": N, "failed": 0, "suite": "phi_os/tests/test_integrity.py" },
  "created_at": "<ISO8601 UTC>"
}
```

`--tag`オプションでgit annotated tag `mocka-baseline-v1.0-event-integrity`も
作成する（push自体はGit運用手順側で行う）。

---

## テスト（STEP6） — phi_os/tests/test_integrity.py

11ケース全PASS（既存`phi_os/tests/`全86件も regression なしで全PASS確認済み）:

- 正常チェーン検証 / チェーン切断検証 / 改ざん検証 / 欠番検証
- 重複検証（UNIQUE制約 + unsigned_event検出）
- Signature/Algorithm不正値検証
- Recovery Support診断内容検証
- Migration後整合性検証（legacy行の遡及署名 -> verify_chain OK）
- Performance確認（2,000イベントの署名+検証が10秒未満）

---

## Gate PolicyとIntegrityの対応

詳細は`GATE_ARCHITECTURE_v1.md`の対応表を参照。要点: `_source`の値
（live/buffered/direct_allowed:*のいずれであっても）に関わらず、署名・
ハッシュチェーンの適用方法は同一であり、Integrity層はGate Policy層の
分類結果に依存しない（"誰が書いたか"と"記録後に改ざんされていないか"は
独立した検証軸である）。
