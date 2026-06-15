# MoCKA Change Transaction Protocol v1

**Document ID**: CHANGE_TRANSACTION_PROTOCOL_v1
**Version**: 1.0.0
**Status**: Active
**Created**: 2026-06-15
**Depends On**: VERSION_POLICY_v1.md (v1.0.0), DECISION_LEDGER_SCHEMA_v1.md (v1.0.0)

---

## 1. Purpose

MoCKAにおける変更作業を制度的トランザクションとして定義する。

コード・文書・設定・データ変更は本仕様に従う。

目的：
- 作業途中の状態を可視化
- 中断・失敗・ロールバックの制度化
- 変更履歴の完全監査
- AI・人間問わず共通プロトコル化

---

## 2. Scope

対象：

- ソースコード
- ドキュメント
- 設定ファイル
- DB Migration
- Event Schema
- Module構成
- Repository構造

---

## 3. Transaction States

正常系：

```
PLANNED
  ↓
CHANGE_START
  ↓
IN_PROGRESS
  ↓
VALIDATING
  ↓
CHANGE_DONE
  ↓
COMMITTED
  ↓
VERIFIED
```

異常系：

```
IN_PROGRESS
  ↓
ABORTED
```

```
VALIDATING
  ↓
ROLLBACK
```

---

## 4. State Definitions

### PLANNED

- **意味**: 変更作業が計画され、TODOまたはDecision Ledgerに登録された状態
- **必須条件**: 変更目的・対象ファイルが明確であること
- **遷移条件**: 作業者が着手を決定した時点でCHANGE_STARTへ遷移

### CHANGE_START

- **意味**: 変更作業の着手が記録された状態
- **必須条件**: `mocka_write_event`（CHANGE_START）が記録済みであること
- **遷移条件**: 編集（Edit/Write等）が開始された時点でIN_PROGRESSへ遷移

### IN_PROGRESS

- **意味**: ファイル編集・実装作業が進行中の状態
- **必須条件**: 対象ファイルへの変更が1件以上行われていること
- **遷移条件**: 編集完了後、検証（テスト・UTF-8検証等）を開始した時点でVALIDATINGへ遷移。中断時はABORTEDへ遷移

### VALIDATING

- **意味**: 変更内容の検証（テスト・UTF-8検証・整合性確認等）を実施中の状態
- **必須条件**: 検証手順（mocka_check_utf8、テスト実行等）が定義されていること
- **遷移条件**: 全検証が成功した場合はCHANGE_DONEへ遷移。検証失敗時はROLLBACKへ遷移

### CHANGE_DONE

- **意味**: 変更が完了し、検証に成功した状態
- **必須条件**: `mocka_write_event`（CHANGE_DONE）が記録済みであること
- **遷移条件**: git commitが実行された時点でCOMMITTEDへ遷移

### COMMITTED

- **意味**: 変更がgit commitとして記録された状態
- **必須条件**: Git Commitハッシュが存在すること
- **遷移条件**: 監査（Audit Requirements確認）が完了した時点でVERIFIEDへ遷移

### VERIFIED

- **意味**: 変更がCommit・Event・Decision Ledger等を含めて完全に監査された最終状態
- **必須条件**: Section 9 Audit Requirementsの全項目を満たすこと
- **遷移条件**: 最終状態。再変更が必要な場合は新たなPLANNEDから開始する

### ABORTED（異常系）

- **意味**: IN_PROGRESS状態で作業が中断・放棄された状態
- **必須条件**: `mocka_write_event`（CHANGE_ABORTED）が記録され、中断理由が記録されていること
- **遷移条件**: 終端状態。再開する場合は新たなPLANNEDから開始する

### ROLLBACK（異常系）

- **意味**: VALIDATING状態で検証に失敗し、変更を取り消す状態
- **必須条件**: `mocka_write_event`（CHANGE_ROLLBACK）が記録され、ロールバック理由が記録されていること
- **遷移条件**: ロールバック完了後、ABORTEDへ遷移

---

## 5. Transition Rules

| From | Trigger | To |
|------|---------|-----|
| PLANNED | 作業開始 | CHANGE_START |
| CHANGE_START | 編集開始 | IN_PROGRESS |
| IN_PROGRESS | テスト開始 | VALIDATING |
| IN_PROGRESS | 作業中断 | ABORTED |
| VALIDATING | 全成功 | CHANGE_DONE |
| VALIDATING | 検証失敗 | ROLLBACK |
| CHANGE_DONE | Git Commit | COMMITTED |
| COMMITTED | 監査完了 | VERIFIED |
| ROLLBACK | 取消完了 | ABORTED |

---

## 6. Required Events

各状態で必須となる`mocka_write_event`のwhat_type：

| State | 必須イベント |
|-------|-------------|
| CHANGE_START | CHANGE_START |
| CHANGE_DONE | CHANGE_DONE |
| ABORTED | CHANGE_ABORTED |
| ROLLBACK | CHANGE_ROLLBACK |
| VERIFIED | CHANGE_VERIFIED |

---

## 7. Required Evidence

各変更には最低限以下を残す：

- Git Commit
- Decision Ledger
- Event Log
- Changed Files
- Validation Result

---

## 8. Rollback Policy

Rollback時は必ず以下を記録する：

- `ROLLBACK_STARTED`
- `ROLLBACK_COMPLETED`

Rollback理由を保存する（`mocka_write_event`のdescriptionまたはtransition_reasonに記録）。

---

## 9. Audit Requirements

監査で確認する項目：

- CHANGE_STARTが存在する
- CHANGE_DONEが存在する
- Commitが存在する
- Decision Ledgerが存在する
- Validation成功
- Event記録済み

---

## 10. Examples

### 正常例

```
PLANNED
  ↓
CHANGE_START
  ↓
IN_PROGRESS
  ↓
VALIDATING
  ↓
CHANGE_DONE
  ↓
COMMITTED
  ↓
VERIFIED
```

### 異常例

```
CHANGE_START
  ↓
IN_PROGRESS
  ↓
VALIDATING
  ↓
ROLLBACK
  ↓
ABORTED
```

---

## Appendix A: 制度仕様との関係

```
VERSION_POLICY
    ↓
DECISION_LEDGER_SCHEMA
    ↓
CHANGE_TRANSACTION_PROTOCOL
    ↓
    ├─────────────┐
    ▼             ▼
MODULE_MATURITY   MODULE_DEPENDENCY
    │
    ▼
EVENT_FOUNDATION
    │
    ▼
EVENT_DATA_LIFECYCLE
    │
    ▼
EVENT_TRANSITION_PROTOCOL
```

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Active | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
