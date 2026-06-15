# MoCKA Module Certification v1

**Document ID**: MODULE_CERTIFICATION_v1
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-06-15
**Reference**: MODULE_AUDIT_PROTOCOL_v1, MODULE_HEALTH_MODEL_v1, MODULE_LIFECYCLE_v1, MODULE_MATURITY_MODEL_v1
**Reference Event**: E20260615_066

---

## 1. Purpose

Moduleの品質・成熟度・運用実績を総合的に評価し、公式な認証レベルを定義する。

本仕様は、MoCKAにおけるModule認証の唯一の標準とする。

---

## 2. Design Principles

- Certification is evidence-based.
- Certification is reproducible.
- Certification is version-specific.
- Certification is auditable.
- Certification requires traceable approval.

---

## 3. Certification Levels

| Level | 意味 |
|-------|------|
| UNVERIFIED | 認証評価未実施。デフォルト状態 |
| VERIFIED | 基本構造・依存関係の検証完了 |
| CERTIFIED | 全監査レベルをPASSし、健全性・成熟度基準を満たす |
| ENTERPRISE_READY | 長期運用・セキュリティ・統合要件を満たし、組織利用に適する |
| COMMERCIAL_READY | 外部公開・収益化に適する品質・運用体制を備える |
| LONG_TERM_STABLE | 6ヶ月以上の安定運用実績があり、長期保証対象となる |

---

## 4. Certification Requirements

| Level | Required Audit Results | Required Health State | Required Lifecycle State | Required Documentation | Required Test Evidence | Required Approval |
|-------|--------------------------|--------------------------|-----------------------------|---------------------------|---------------------------|---------------------|
| UNVERIFIED | N/A | UNKNOWN以上 | PLANNED以上 | なし | なし | なし |
| VERIFIED | Level 1〜2 PASS | UNKNOWN〜WARNING | DRAFT以上 | README・仕様書初版 | なし | くろこ |
| CERTIFIED | Level 1〜4 全てPASS | HEALTHY〜WARNING | BETA以上 | MODULE_CATALOG Section 7全項目整備 | テスト自動化・実行結果記録 | くろこ |
| ENTERPRISE_READY | Level 1〜5 全てPASS | HEALTHY | STABLE以上 | 外部公開ドキュメント整備済み・Security Audit PASS | テストカバレッジ基準達成・統合テスト結果記録 | きむら博士 |
| COMMERCIAL_READY | ENTERPRISE_READY要件 + Release Audit PASS | HEALTHY | STABLE以上（M4相当） | 公開API仕様・利用規約等の整備 | 負荷・運用実績の証跡 | きむら博士 |
| LONG_TERM_STABLE | ENTERPRISE_READY要件を6ヶ月以上維持 | HEALTHY（過去6ヶ月WARNING以下） | MAINTENANCE以上（M5相当含む） | Decision Ledgerによる長期保証記録 | 6ヶ月以上の障害・降格記録なし | きむら博士 |

---

## 5. Certification Workflow

標準フロー：

```
Module
  ↓
Evidence Collection
  ↓
Audit Review
  ↓
Health Verification
  ↓
Lifecycle Verification
  ↓
Certification Decision
  ↓
Approval
  ↓
Certification Record
```

---

## 6. Certification Record

最低限保持する項目：

| フィールド | 説明 |
|-----------|------|
| Module | module_id（MODULE_CATALOG準拠） |
| Version | 認証対象のモジュールバージョン |
| Certification Level | Section 3のいずれか |
| Effective Date | 認証発効日（ISO8601） |
| Expiration Policy | 必要な場合のみ。再評価周期等（例: LONG_TERM_STABLEは6ヶ月毎に再評価） |
| Evidence | Audit Evidence・Health Record・Lifecycle Record・Decision ID |
| Approver | 承認者（くろこ / きむら博士） |
| Notes | 補足事項 |

---

## 7. Revocation

以下の条件に該当する場合、認証は取り消される。

| 取消条件 | 説明 |
|----------|------|
| Audit Failure | MODULE_AUDIT_PROTOCOLによる監査でFAILが確定した場合 |
| Critical Security Issue | Security AuditでBLOCKING相当の脆弱性が検出された場合 |
| Unsupported Dependencies | MODULE_DEPENDENCY_MODELに違反する依存関係が発生した場合 |
| Integrity Violation | データ・記録の不変条件（I1〜I5等）への違反が確認された場合 |

取消時は認証レベルをUNVERIFIEDへ戻し、Decision Ledger登録およびmocka_write_event（what_type: CERTIFICATION_REVOKED）を必須とする。

---

## 8. Non Goals

本仕様では以下を対象外とする。

- 外部認証制度
- 法的認証
- ソフトウェアライセンス

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
MODULE_CERTIFICATION
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
