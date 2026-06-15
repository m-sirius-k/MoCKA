# MoCKA Module Lifecycle v1

**Document ID**: MODULE_LIFECYCLE_v1
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-06-15
**Reference**: MODULE_HEALTH_MODEL_v1, MODULE_AUDIT_PROTOCOL_v1, MODULE_MATURITY_MODEL_v1
**Reference Event**: E20260615_065

---

## 1. Purpose

Moduleの誕生から廃止までの状態遷移を統一的に定義する。

本仕様は、すべてのModuleが従う標準ライフサイクルモデルとする。

---

## 2. Design Principles

- Lifecycle is deterministic.
- Lifecycle is observable.
- Lifecycle is version-aware.
- Lifecycle preserves traceability.
- Lifecycle transitions require evidence.

---

## 3. Lifecycle States

| State | 意味 |
|-------|------|
| PLANNED | 設計構想段階。Decision Ledgerに登録された提案 |
| DRAFT | 仕様・設計書を作成中 |
| EXPERIMENTAL | 実装中。動作不安定 |
| BETA | 機能完成。検証・テスト中 |
| STABLE | 安定運用中。本番利用可能 |
| MAINTENANCE | 新機能追加なし。バグ修正のみ継続 |
| DEPRECATED | 廃止予定。後継モジュールへの移行期間 |
| ARCHIVED | 運用終了。保守終了 |

---

## 4. Transition Rules

| From | To | 必要な監査 | 必要な証跡 | 必要な承認 | 巻き戻し条件 |
|------|----|-----------|-----------|-----------|---------------|
| PLANNED | DRAFT | Level 0 (Informational) | Decision Ledger登録（DC_YYYYMMDD_NNN） | くろこ | 設計が破棄された場合、PLANNEDへ戻る |
| DRAFT | EXPERIMENTAL | Level 1 (Structural) | 仕様書・README初版コミット | くろこ | 仕様不備が判明した場合、DRAFTへ戻る |
| EXPERIMENTAL | BETA | Level 2 (Dependency) | mocka_write_event連携・基本テスト結果 | くろこ | 重大な設計変更が必要な場合、DRAFTへ戻る |
| BETA | STABLE | Level 3 (Behavior) + Level 4 (Integration) | テスト自動化完了・MODULE_HEALTH_MODELでHEALTHY | きむら博士 | 重大障害発生時、BETAへ戻る |
| STABLE | MAINTENANCE | Level 5 (Release) | 新機能追加終了のDecision Ledger登録 | きむら博士 | 新機能要求が承認された場合、STABLEへ戻る |
| MAINTENANCE | DEPRECATED | Level 0 (Informational) | 後継モジュールのDecision Ledger登録 | きむら博士 | 後継モジュールが撤回された場合、MAINTENANCEへ戻る |
| DEPRECATED | ARCHIVED | Level 5 (Release) | 移行完了の証跡（依存モジュールの参照解消確認） | きむら博士 | 巻き戻し不可（再登録は新規module_idで行う） |

各遷移はCHANGE_TRANSACTION_PROTOCOL_v1のトランザクションとして実行し、CHANGE_START / CHANGE_DONE / CHANGE_VERIFIEDイベントを記録する。

---

## 5. Entry Criteria

各状態へ遷移するための条件：

| State | Entry Criteria |
|-------|-----------------|
| DRAFT | Decision Ledger登録済み・設計概要が存在する |
| EXPERIMENTAL | Documentation complete（README初版）・仕様書が存在する |
| BETA | Required dependency verification complete（MODULE_DEPENDENCY_MODEL適合確認） |
| STABLE | Required audits passed（Level 1〜4）・Required tests passed・MODULE_HEALTH_MODELでHEALTHYまたはWARNING以下 |
| MAINTENANCE | STABLE状態を一定期間維持・新機能追加停止のDecision Ledger登録 |
| DEPRECATED | 後継モジュールまたは代替手段の存在確認 |
| ARCHIVED | DEPRECATED期間中の移行完了確認 |

---

## 6. Exit Criteria

各状態を終了する条件：

| State | Exit Criteria |
|-------|-----------------|
| PLANNED | Successor state（DRAFT）が承認され、Decision Ledgerに記録済み |
| DRAFT | 仕様レビュー完了・Evidence recorded（コミット）・Lifecycle event logged |
| EXPERIMENTAL | 基本動作確認完了・Audit Level 2 PASS |
| BETA | Audit Level 3〜4 PASS・MODULE_HEALTH_MODEL評価記録済み |
| STABLE | MAINTENANCE移行のDecision Ledger登録・Lifecycle event logged |
| MAINTENANCE | DEPRECATED移行のDecision Ledger登録・後継モジュール登録済み |
| DEPRECATED | 依存モジュールの参照解消・Evidence recorded |
| ARCHIVED | 終端状態。Exit Criteriaなし |

---

## 7. Lifecycle Record

最低限保持する項目：

| フィールド | 説明 |
|-----------|------|
| Module | module_id（MODULE_CATALOG準拠） |
| Version | 遷移時点のモジュールバージョン |
| Previous State | 遷移前のLifecycle State |
| Current State | 遷移後のLifecycle State |
| Transition Date | 遷移日（ISO8601） |
| Approval | 承認者（くろこ / きむら博士） |
| Evidence | Decision Ledger ID・Event ID・コミットハッシュ・Audit結果 |
| Notes | 補足事項 |

---

## 8. State Transition Matrix

| From \ To | PLANNED | DRAFT | EXPERIMENTAL | BETA | STABLE | MAINTENANCE | DEPRECATED | ARCHIVED |
|-----------|---------|-------|--------------|------|--------|--------------|------------|----------|
| PLANNED | - | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| DRAFT | ✅(巻き戻し) | - | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| EXPERIMENTAL | ❌ | ✅(巻き戻し) | - | ✅ | ❌ | ❌ | ❌ | ❌ |
| BETA | ❌ | ✅(巻き戻し) | ✅(巻き戻し) | - | ✅ | ❌ | ❌ | ❌ |
| STABLE | ❌ | ❌ | ❌ | ✅(巻き戻し) | - | ✅ | ❌ | ❌ |
| MAINTENANCE | ❌ | ❌ | ❌ | ❌ | ✅(巻き戻し) | - | ✅ | ❌ |
| DEPRECATED | ❌ | ❌ | ❌ | ❌ | ❌ | ✅(巻き戻し) | - | ✅ |
| ARCHIVED | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | - |

- ✅: 許可される遷移（隣接する前進または巻き戻しのみ）
- ❌: 禁止される遷移（状態のスキップ・逆順への飛び越しは禁止）
- ARCHIVEDは終端状態であり、いかなる遷移も許可しない

---

## 9. Non Goals

本仕様では以下を対象外とする。

- リリース自動化
- CI/CD
- パッケージ配布

---

## Appendix A: 制度仕様との関係

```
MODULE_AUDIT_PROTOCOL
        │
        ▼
MODULE_HEALTH_MODEL
        │
        ▼
MODULE_LIFECYCLE
        │
        ▼
MODULE_MATURITY_MODEL / MODULE_CATALOG
```

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Draft | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
