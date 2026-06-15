# MoCKA Module Rule Engine v1

**Document ID**: MODULE_RULE_ENGINE_v1
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-06-15
**Reference**: MODULE_POLICY_ENGINE_v1, MODULE_AUDIT_PROTOCOL_v1, MODULE_CERTIFICATION_v1, MODULE_REGISTRY_MODEL_v1
**Reference Event**: E20260615_072

---

## 1. Purpose

Policy Engineで評価される各種ルールの適用モデルを定義する。

Rule Engineは、Moduleに対して適用されるガバナンスルールの管理・評価・適用順序を規定する標準仕様とする。

---

## 2. Design Principles

- Rules are deterministic.
- Rules are version-aware.
- Rule execution is reproducible.
- Rule precedence is explicitly defined.
- Rule application is traceable.

---

## 3. Rule Categories

| Category | 説明 |
|----------|------|
| Governance Rules | MODULE_POLICY_ENGINEのGovernance Policyに対応するルール群（VERSION_POLICY等への準拠） |
| Security Rules | MODULE_POLICY_ENGINEのSecurity Policyに対応するルール群 |
| Dependency Rules | MODULE_DEPENDENCY_MODELのAllowed Dependencies・循環依存禁止に対応するルール群 |
| Lifecycle Rules | MODULE_LIFECYCLEのState Transition Matrixに対応するルール群 |
| Documentation Rules | MODULE_CATALOG Section 7 Required Documentsに対応するルール群 |
| Certification Rules | MODULE_CERTIFICATIONのCertification Requirementsに対応するルール群 |
| Validation Rules | MODULE_AUDIT_PROTOCOLの各Audit Categoryに対応する構造的検証ルール群 |

---

## 4. Rule Definition

各ルールについて保持する項目：

| フィールド | 説明 |
|-----------|------|
| Rule ID | ルールの識別子（一意） |
| Rule Name | ルール名 |
| Description | ルールの内容・目的 |
| Scope | 適用対象（Module全体 / 特定Category / 特定Dependency Level等） |
| Preconditions | ルール評価の前提条件 |
| Evaluation Logic | 判定基準（参照元仕様の該当条項） |
| Expected Result | 期待される評価結果（Section 7） |
| Version | ルール定義のバージョン |

---

## 5. Rule Execution Order

ルールは以下の順序で適用する。

1. Structural Rules（Validation Rulesのうち構造検証に関するもの）
2. Dependency Rules
3. Governance Rules
4. Health Rules（Validation Rulesのうち健全性に関するもの）
5. Lifecycle Rules
6. Certification Rules

Documentation RulesおよびSecurity Rulesは上記各段階の評価対象となるルール群と並行して適用される横断的ルールとする。

---

## 6. Conflict Resolution

ルールが競合した場合の優先順位：

| 要素 | 内容 |
|------|------|
| Priority | Section 5のExecution Orderにおいて、より前段のCategoryのルールが優先される。同一Category内ではRule IDの昇順を優先順位とする |
| Override Conditions | 上位のRule（Security Rules・Governance Rules）がFAILと判定した場合、下位のRuleの評価結果がPASSであっても全体結果はFAILとする。Overrideはきむら博士の承認・Decision Ledger登録がある場合のみ無効化できる |
| Conflict Recording | ルール競合が発生した場合、競合したRule ID・優先順位適用結果・Override有無をEvidenceとして記録する |

---

## 7. Rule Result

| Result | 意味 |
|--------|------|
| PASS | ルール基準を満たす |
| WARNING | 軽微な逸脱あり |
| FAIL | ルール基準を満たさない |
| SKIPPED | Preconditionsを満たさないため評価をスキップした |
| NOT_APPLICABLE | 対象Moduleには本ルールが適用されない |

---

## 8. Traceability

各ルール適用結果は以下と関連付ける。

| フィールド | 説明 |
|-----------|------|
| Module ID | 評価対象のmodule_id |
| Rule Version | 適用したRule Definitionのバージョン |
| Policy Version | MODULE_POLICY_ENGINEにおける対応Policyのバージョン |
| Event Reference | 評価結果を記録したmocka_write_eventのEvent ID |
| Timestamp | 評価実施日時（ISO8601） |

---

## 9. Non Goals

本仕様では以下を対象外とする。

- スクリプト実装
- 実行エンジン
- 自動修復

---

## Appendix A: 制度仕様との関係

```
MODULE_AUDIT_PROTOCOL ─┐
MODULE_CERTIFICATION   ├──▶ MODULE_POLICY_ENGINE ──▶ MODULE_RULE_ENGINE
MODULE_REGISTRY_MODEL ─┘
```

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Draft | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
