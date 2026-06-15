# MoCKA Module Audit Protocol v1

**Document ID**: MODULE_AUDIT_PROTOCOL_v1
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-06-15
**Reference**: MODULE_CATALOG_v1, MODULE_DEPENDENCY_MODEL_v1, CHANGE_TRANSACTION_PROTOCOL_v1
**Reference Event**: E20260615_063

---

## 1. Purpose

Generation 1で整備したGovernance（VERSION_POLICY / DECISION_LEDGER_SCHEMA / MODULE_MATURITY_MODEL / MODULE_DEPENDENCY_MODEL / MODULE_CATALOG / CHANGE_TRANSACTION_PROTOCOL / EVENT_*）を運用するため、Module単位の監査プロトコルを定義する。

本仕様は「Moduleをどのように評価・監査・承認するか」を定める公式文書とする。

---

## 2. Audit Principles

- Audit is reproducible.
- Audit is deterministic.
- Audit never mutates artifacts.
- Audit records evidence.
- Audit produces verifiable results.
- Audit is traceable.

---

## 3. Audit Levels

| Level | 名称 | 説明 |
|-------|------|------|
| Level 0 | Informational | 情報収集のみ。判定を伴わない |
| Level 1 | Structural | ファイル構成・ドキュメント存在・命名規則の確認 |
| Level 2 | Dependency | MODULE_DEPENDENCY_MODELに基づく依存関係の確認 |
| Level 3 | Behavior | 実装の動作・テスト結果の確認 |
| Level 4 | Integration | 他モジュールとの連携・公開インターフェースの確認 |
| Level 5 | Release | MODULE_MATURITY_MODELの昇格条件・リリース判定 |

---

## 4. Audit Categories

| Category | 説明 |
|----------|------|
| Document Audit | 仕様書・README・変更履歴の整備状況 |
| Structure Audit | ディレクトリ構成・命名規則・配置の整合性 |
| Dependency Audit | MODULE_DEPENDENCY_MODELに対する依存関係の適合性 |
| Schema Audit | データ・イベント・設定スキーマの整合性 |
| Implementation Audit | 実装内容の構造的確認 |
| Test Audit | テストカバレッジ・自動化状況 |
| Security Audit | 権限・機密情報・脆弱性の確認 |
| Release Audit | MODULE_CATALOGのlifecycle_status・maturity_levelとの整合性、リリース可否 |

---

## 5. Audit Result

| Result | 意味 |
|--------|------|
| PASS | 監査項目を満たす |
| WARNING | 軽微な問題あり。修正推奨だが続行可 |
| FAIL | 監査項目を満たさない。修正必須 |
| BLOCKED | 前提条件未達のため監査不能 |
| NOT_APPLICABLE | 本モジュールには適用対象外 |

---

## 6. Evidence

監査結果には必ず以下を保持する。

| フィールド | 説明 |
|-----------|------|
| Module | module_id（MODULE_CATALOG準拠） |
| Version | 監査対象のドキュメント/モジュールバージョン |
| Auditor | 監査者（きむら博士 / Claude / くろこ 等） |
| Timestamp | 監査実施日時（ISO8601） |
| Evidence | 確認に使用した根拠（ファイルパス・コミットハッシュ・Event ID等） |
| Result | Section 5のいずれか |
| Notes | 補足事項・修正提案 |

---

## 7. Audit Workflow

標準フロー：

```
Module
  ↓
Pre-check
  ↓
Structural Audit
  ↓
Dependency Audit
  ↓
Behavior Audit
  ↓
Evidence Collection
  ↓
Result
  ↓
Approval
```

---

## 8. Non Goals

本仕様では以下を扱わない。

- 実装方法
- 自動監査エンジン
- CI/CD

---

## Appendix A: 制度仕様との関係

```
MODULE_CATALOG
        │
        ▼
MODULE_DEPENDENCY_MODEL
        │
        ▼
CHANGE_TRANSACTION_PROTOCOL
        │
        ▼
MODULE_AUDIT_PROTOCOL
```

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Draft | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
