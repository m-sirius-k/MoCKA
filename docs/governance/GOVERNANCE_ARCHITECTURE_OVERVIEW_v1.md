# MoCKA Governance Architecture Overview v1

**Document ID**: GOVERNANCE_ARCHITECTURE_OVERVIEW_v1
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-06-15
**Reference Event**: E20260615_076

---

## 1. Purpose

Generation 1〜4で策定したGovernance仕様全体を体系化し、MoCKA Governance Architectureの公式概要文書を作成する。

本仕様は、新規開発者・監査担当・AIエージェントが短時間で全体像を理解できるための入口となる。

---

## 2. Scope

本書はGeneration 1〜4を対象とする。

- Generation 1（docs/mocka3/）: VERSION_POLICY / DECISION_LEDGER_SCHEMA / MODULE_MATURITY_MODEL / MODULE_DEPENDENCY_MODEL / EVENT_FOUNDATION / EVENT_DATA_LIFECYCLE / EVENT_TRANSITION_PROTOCOL / CHANGE_TRANSACTION_PROTOCOL / MODULE_CATALOG
- Generation 2〜4（docs/governance/）: MODULE_AUDIT_PROTOCOL / MODULE_HEALTH_MODEL / MODULE_LIFECYCLE / MODULE_CERTIFICATION / MODULE_REGISTRY_MODEL / MODULE_INDEX_SPEC / MODULE_QUERY_PROTOCOL / MODULE_DISCOVERY_MODEL / MODULE_POLICY_ENGINE / MODULE_RULE_ENGINE / MODULE_VALIDATION_ENGINE / MODULE_COMPLIANCE_MODEL / MODULE_GOVERNANCE_RUNTIME

---

## 3. Governance Layers

Generationごとの役割：

| Generation | 役割 | 概要 |
|------------|------|------|
| Generation 1 | Definition | Moduleとイベントデータの「定義」層。バージョン管理・意思決定記録・成熟度・依存関係・イベントのState/Transition・変更トランザクション・Module台帳を定義する |
| Generation 2 | Evaluation | Moduleの「評価」層。監査プロトコル・健全性モデル・ライフサイクル・認証レベルを定義する |
| Generation 3 | Discovery | Moduleの「発見」層。Registry・Index・Query・Discoveryを定義し、Module情報のSingle Source of Truthと探索手段を提供する |
| Generation 4 | Runtime | Governanceの「実行」層。Policy/Rule/Validation/ComplianceのEngineを定義し、全体をGovernance Runtimeとして統合する |

---

## 4. Document Map

| Document ID | Purpose | Primary Responsibility | Dependencies | Related Documents |
|-------------|---------|--------------------------|---------------|----------------------|
| VERSION_POLICY_v1 | バージョン・Status管理ルール定義 | Versioning Scheme・Document Status Lifecycle・Impact Assessment | なし | DECISION_LEDGER_SCHEMA |
| DECISION_LEDGER_SCHEMA_v1 | 制度的意思決定の記録スキーマ | Decision Record・DC採番・supersedes連鎖 | VERSION_POLICY, EVENT_FOUNDATION | MODULE_MATURITY_MODEL, MODULE_DEPENDENCY_MODEL |
| MODULE_MATURITY_MODEL_v1 | Moduleの成熟度モデル | M0〜M5定義・7軸評価・昇格/降格条件 | VERSION_POLICY, DECISION_LEDGER_SCHEMA, EVENT_FOUNDATION | MODULE_DEPENDENCY_MODEL, MODULE_CATALOG |
| MODULE_DEPENDENCY_MODEL_v1 | Module依存関係アーキテクチャ | Dependency Levels・Allowed Dependencies・循環依存禁止 | VERSION_POLICY, DECISION_LEDGER_SCHEMA, MODULE_MATURITY_MODEL | MODULE_CATALOG |
| EVENT_FOUNDATION_v1 | イベントの定義・不変条件 | Design Principles・Invariants(I1-I5)・Event Schema | なし | EVENT_DATA_LIFECYCLE, EVENT_TRANSITION_PROTOCOL |
| EVENT_DATA_LIFECYCLE_v1 | イベントデータのライフサイクル | Logical States・Storage Mapping・State Transition・Lifecycle Metadata | EVENT_FOUNDATION | EVENT_TRANSITION_PROTOCOL |
| EVENT_TRANSITION_PROTOCOL_v1 | イベント遷移の実行プロトコル | 遷移実行手順・Actor責務・エラー処理・冪等性 | EVENT_FOUNDATION, EVENT_DATA_LIFECYCLE | - |
| CHANGE_TRANSACTION_PROTOCOL_v1 | 変更作業のトランザクション化 | Transaction States・Transition Rules・Rollback Policy | VERSION_POLICY, DECISION_LEDGER_SCHEMA | MODULE_AUDIT_PROTOCOL |
| MODULE_CATALOG_v1 | Module公式登録台帳 | Module Registration・Lifecycle Status・Initial Catalog | VERSION_POLICY, DECISION_LEDGER_SCHEMA, MODULE_MATURITY_MODEL, MODULE_DEPENDENCY_MODEL | MODULE_REGISTRY_MODEL |
| MODULE_AUDIT_PROTOCOL_v1 | Module監査プロトコル | Audit Levels(0-5)・Categories・Result・Evidence・Workflow | MODULE_CATALOG, MODULE_DEPENDENCY_MODEL, CHANGE_TRANSACTION_PROTOCOL | MODULE_HEALTH_MODEL |
| MODULE_HEALTH_MODEL_v1 | Module健全性モデル | Health States(7段階)・Indicators・Assessment・Transition | MODULE_AUDIT_PROTOCOL, MODULE_CATALOG, MODULE_MATURITY_MODEL | MODULE_LIFECYCLE |
| MODULE_LIFECYCLE_v1 | Module標準ライフサイクル | Lifecycle States(8段階)・Transition Rules・Matrix | MODULE_HEALTH_MODEL, MODULE_AUDIT_PROTOCOL, MODULE_MATURITY_MODEL | MODULE_CERTIFICATION |
| MODULE_CERTIFICATION_v1 | Module認証レベル | Certification Levels(6段階)・Requirements・Revocation | MODULE_AUDIT_PROTOCOL, MODULE_HEALTH_MODEL, MODULE_LIFECYCLE, MODULE_MATURITY_MODEL | MODULE_REGISTRY_MODEL |
| MODULE_REGISTRY_MODEL_v1 | Module一元管理Registry | Registry Entry・Operations・Integrity Rules | MODULE_CATALOG, MODULE_AUDIT_PROTOCOL, MODULE_HEALTH_MODEL, MODULE_LIFECYCLE, MODULE_CERTIFICATION | MODULE_INDEX_SPEC |
| MODULE_INDEX_SPEC_v1 | Registry論理インデックス | Required Indexes(9種)・Index Entry・Query Support | MODULE_REGISTRY_MODEL, MODULE_CATALOG, MODULE_CERTIFICATION | MODULE_QUERY_PROTOCOL |
| MODULE_QUERY_PROTOCOL_v1 | Registry/Index問い合わせ標準 | Query Types(9種)・Request/Response・Error Handling | MODULE_REGISTRY_MODEL, MODULE_INDEX_SPEC, MODULE_CATALOG | MODULE_DISCOVERY_MODEL |
| MODULE_DISCOVERY_MODEL_v1 | Module発見・探索モデル | Discovery Dimensions・Modes・Ranking | MODULE_REGISTRY_MODEL, MODULE_INDEX_SPEC, MODULE_QUERY_PROTOCOL, MODULE_CERTIFICATION | MODULE_POLICY_ENGINE |
| MODULE_POLICY_ENGINE_v1 | ガバナンスポリシー評価 | Policy Categories(7種)・Evaluation・Results | MODULE_AUDIT_PROTOCOL, MODULE_HEALTH_MODEL, MODULE_LIFECYCLE, MODULE_CERTIFICATION, MODULE_REGISTRY_MODEL, MODULE_QUERY_PROTOCOL | MODULE_RULE_ENGINE |
| MODULE_RULE_ENGINE_v1 | ルール適用モデル | Rule Categories(7種)・Execution Order・Conflict Resolution | MODULE_POLICY_ENGINE, MODULE_AUDIT_PROTOCOL, MODULE_CERTIFICATION, MODULE_REGISTRY_MODEL | MODULE_VALIDATION_ENGINE |
| MODULE_VALIDATION_ENGINE_v1 | 検証エンジン | Validation Scope(8項目)・Workflow・Results | MODULE_POLICY_ENGINE, MODULE_RULE_ENGINE, MODULE_AUDIT_PROTOCOL, MODULE_CERTIFICATION | MODULE_COMPLIANCE_MODEL |
| MODULE_COMPLIANCE_MODEL_v1 | 準拠性評価モデル | Compliance Domains(8種)・Levels(4段階)・Workflow | MODULE_VALIDATION_ENGINE, MODULE_POLICY_ENGINE, MODULE_RULE_ENGINE, MODULE_CERTIFICATION, MODULE_AUDIT_PROTOCOL | MODULE_GOVERNANCE_RUNTIME |
| MODULE_GOVERNANCE_RUNTIME_v1 | Governance実行統合モデル | Runtime Components(12種)・Workflow・Interfaces | 全Generation 1-4文書 | - |

---

## 5. Layer Relationships

Generation間の依存関係とデータフロー：

```
[Generation 1: Definition]
VERSION_POLICY
    │
    ▼
DECISION_LEDGER_SCHEMA ── CHANGE_TRANSACTION_PROTOCOL
    │
    ▼
MODULE_MATURITY_MODEL ── MODULE_DEPENDENCY_MODEL
    │
    ▼
MODULE_CATALOG
    │
    │   EVENT_FOUNDATION ── EVENT_DATA_LIFECYCLE ── EVENT_TRANSITION_PROTOCOL
    │
    ▼
[Generation 2: Evaluation]
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
[Generation 3: Discovery]
MODULE_REGISTRY_MODEL
    │
    ▼
MODULE_INDEX_SPEC
    │
    ▼
MODULE_QUERY_PROTOCOL
    │
    ▼
MODULE_DISCOVERY_MODEL
    │
    ▼
[Generation 4: Runtime]
MODULE_POLICY_ENGINE
    │
    ▼
MODULE_RULE_ENGINE
    │
    ▼
MODULE_VALIDATION_ENGINE
    │
    ▼
MODULE_COMPLIANCE_MODEL
    │
    ▼
MODULE_GOVERNANCE_RUNTIME
```

データは下流（Generation 1 → 4）に向かって「定義 → 評価 → 発見 → 実行」の順で利用される。一方、評価結果（Health/Lifecycle/Certification/Compliance）はRegistry（Generation 3）を介して上流の定義（Catalog/Maturity）にフィードバックされる。

---

## 6. Runtime Architecture

Registry、Policy、Rule、Validation、Compliance、Audit、Certificationの相互関係：

- **Registry**（MODULE_REGISTRY_MODEL）は全Moduleの単一公式情報源であり、Audit/Health/Lifecycle/Certificationの結果を集約する。
- **Audit**（MODULE_AUDIT_PROTOCOL）はModuleの構造・依存・実装・テスト・セキュリティ・リリースを検証し、Evidenceを生成する。
- **Health**（MODULE_HEALTH_MODEL）はAudit結果を継続的な健全性指標へ変換する。
- **Lifecycle**（MODULE_LIFECYCLE）はModuleの誕生から廃止までの状態を管理し、Health/Auditの結果を遷移条件として利用する。
- **Certification**（MODULE_CERTIFICATION）はAudit/Health/Lifecycle/Maturityを総合し、公式な認証レベルを付与する。
- **Policy Engine**（MODULE_POLICY_ENGINE）はGovernance全体のポリシーをRegistry・Audit・Health・Lifecycle・Certificationの情報に基づき評価する。
- **Rule Engine**（MODULE_RULE_ENGINE）はPolicy Engineが参照する個別ルールの定義・適用順序・競合解決を管理する。
- **Validation Engine**（MODULE_VALIDATION_ENGINE）はRule/Policy Engineの評価結果を集約し、Module全体の検証結果（VALID/WARNING/INVALID）を生成する。
- **Compliance Model**（MODULE_COMPLIANCE_MODEL）はValidation・Audit・Certificationを統合し、Module全体の準拠レベルを決定する。

これら全体は**Governance Runtime**（MODULE_GOVERNANCE_RUNTIME）として統合され、Module Registration → Evaluation → Certification → Registry Updateの標準フローを構成する。

---

## 7. Governance Principles

Generation全体を貫く共通原則：

- **Deterministic**: 同一入力に対して常に同一の評価結果を返す
- **Reproducible**: 評価・監査・検証は再現可能である
- **Traceable**: すべての判断・遷移・記録はEvent/Decision Ledgerと関連付けられる
- **Evidence-based**: 結果は必ず根拠（Evidence）を伴う
- **Version-aware**: すべての記録・評価はバージョンに紐づく

---

## 8. Future Roadmap

Generation 5以降で想定する拡張候補：

- Governance Services
- Runtime Automation
- PHI-OS Integration
- Orchestra Integration
- Prism Integration
- Memory Integration

---

## 9. Non Goals

本書では新しいガバナンス規則は定義しない。既存仕様の整理・体系化のみを目的とする。

---

## Appendix: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Draft | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
