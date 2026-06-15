# MoCKA Module Compliance Model v1

**Document ID**: MODULE_COMPLIANCE_MODEL_v1
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-06-15
**Reference**: MODULE_VALIDATION_ENGINE_v1, MODULE_POLICY_ENGINE_v1, MODULE_RULE_ENGINE_v1, MODULE_CERTIFICATION_v1, MODULE_AUDIT_PROTOCOL_v1
**Reference Event**: E20260615_074

---

## 1. Purpose

ModuleがMoCKA Governanceの要求事項へどの程度準拠しているかを評価・記録するためのCompliance Modelを定義する。

本仕様は、Validation結果・Audit結果・Certificationを統合した準拠性評価の標準モデルとする。

---

## 2. Design Principles

- Compliance is evidence-based.
- Compliance is measurable.
- Compliance is reproducible.
- Compliance is version-aware.
- Compliance preserves traceability.

---

## 3. Compliance Domains

最低限以下を評価対象とする。

| Domain | 説明 |
|--------|------|
| Governance | VERSION_POLICY・DECISION_LEDGER_SCHEMA・CHANGE_TRANSACTION_PROTOCOLへの準拠（MODULE_POLICY_ENGINEのGovernance Policy） |
| Documentation | MODULE_CATALOG Section 7 Required Documentsの整備状況 |
| Structure | MODULE_AUDIT_PROTOCOLのStructure Audit・MODULE_RULE_ENGINEのStructural Rules |
| Dependencies | MODULE_DEPENDENCY_MODELへの適合（Dependency Rules） |
| Validation | MODULE_VALIDATION_ENGINEのValidation Result |
| Security | MODULE_AUDIT_PROTOCOLのSecurity Audit・Security Rules |
| Lifecycle | MODULE_LIFECYCLEの現在状態・遷移の正当性 |
| Certification | MODULE_CERTIFICATIONのCertification Level |

---

## 4. Compliance Levels

| Level | 意味 |
|-------|------|
| NON_COMPLIANT | 1つ以上のDomainでINVALID/FAIL/BLOCKING相当の結果があり、基本要件を満たさない |
| PARTIALLY_COMPLIANT | 一部のDomainでWARNING以上の問題があるが、致命的なFAILはない |
| COMPLIANT | 全DomainでPASS/VALID相当。CERTIFIED未満のCertification Level |
| FULLY_COMPLIANT | 全DomainでPASS/VALID相当かつCertification LevelがCERTIFIED以上 |

---

## 5. Assessment Workflow

```
Module
  ↓
Evidence Collection
  ↓
Validation Review
  ↓
Policy Review
  ↓
Audit Review
  ↓
Compliance Decision
  ↓
Compliance Record
```

---

## 6. Compliance Record

保持項目：

| フィールド | 説明 |
|-----------|------|
| Compliance ID | 評価の識別子（一意） |
| Module ID | 評価対象のmodule_id（MODULE_REGISTRY_MODEL準拠） |
| Version | 評価対象のモジュールバージョン |
| Compliance Level | Section 4のいずれか |
| Assessment Date | 評価実施日（ISO8601） |
| Evidence | Validation/Policy/Audit Evidence・Registry/Event参照 |
| Findings | Domain別の評価結果・問題点 |
| Recommendations | 改善提案 |

---

## 7. Traceability

各評価は以下と関連付ける。

| フィールド | 説明 |
|-----------|------|
| Validation ID | MODULE_VALIDATION_ENGINEのValidation ID |
| Audit ID | MODULE_AUDIT_PROTOCOLの監査記録への参照 |
| Certification Level | MODULE_CERTIFICATIONの現在レベル |
| Registry Version | 評価時点のMODULE_REGISTRY_MODEL Registry Entryの状態 |
| Event Reference | 評価結果を記録したmocka_write_eventのEvent ID |

---

## 8. Non Goals

本仕様では以下を対象外とする。

- 法規制対応
- 外部認証制度
- 自動是正

---

## Appendix A: 制度仕様との関係

```
MODULE_AUDIT_PROTOCOL ─┐
MODULE_VALIDATION_ENGINE│
MODULE_POLICY_ENGINE    ├──▶ MODULE_COMPLIANCE_MODEL
MODULE_RULE_ENGINE      │
MODULE_CERTIFICATION ───┘
```

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Draft | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
