# MoCKA Module Query Protocol v1

**Document ID**: MODULE_QUERY_PROTOCOL_v1
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-06-15
**Reference**: MODULE_REGISTRY_MODEL_v1, MODULE_INDEX_SPEC_v1, MODULE_CATALOG_v1
**Reference Event**: E20260615_069

---

## 1. Purpose

Module RegistryおよびIndexに対する標準的な問い合わせ仕様（Query Protocol）を定義する。

本仕様は、すべてのMoCKAコンポーネントが共通の方法でModule情報を取得・検索・参照するための標準プロトコルとする。

---

## 2. Design Principles

- Queries are deterministic.
- Queries are read-only.
- Queries are reproducible.
- Query results are version-aware.
- Every query is traceable.

---

## 3. Supported Query Types

| Query Type | 説明 | 利用Index |
|------------|------|-----------|
| Query by Module ID | module_idを指定して単一Moduleを取得する | Module ID Index |
| Query by Module Name | Module Nameからmodule_idを引き、Moduleを取得する | Module Name Index |
| Query by Category | 役割分類・Dependency Levelでフィルタする | Category Index |
| Query by Dependency | 指定Moduleに依存する/依存される全Moduleを取得する | Dependency Index |
| Query by Version | 指定module_idの特定バージョンまたは全履歴を取得する | Version Index |
| Query by Lifecycle State | MODULE_LIFECYCLEの状態でフィルタする | Lifecycle Index |
| Query by Health State | MODULE_HEALTH_MODELの状態でフィルタする | Health Index |
| Query by Certification Level | MODULE_CERTIFICATIONのレベルでフィルタする | Certification Index |
| Query by Event Reference | 指定Event IDに関連するModuleを取得する | Event Index |

---

## 4. Query Request

問い合わせ時に保持する項目：

| フィールド | 説明 |
|-----------|------|
| Query ID | 問い合わせ識別子（一意） |
| Request Timestamp | 問い合わせ実施日時（ISO8601） |
| Query Type | Section 3のいずれか |
| Query Parameters | 検索条件（module_id・category名・state名等） |
| Requested Version | 取得対象のバージョン指定（省略時は現行バージョン） |
| Request Source | 問い合わせ元（モジュール名・くろこ・きむら博士等） |

---

## 5. Query Response

返却項目：

| フィールド | 説明 |
|-----------|------|
| Module ID | module_id |
| Version | 返却対象のモジュールバージョン |
| Registry Reference | MODULE_REGISTRY_MODELのRegistry Entryへの参照 |
| Current State | Registry OperationsのCurrent Status（Active/Deprecated/Archived） |
| Health | MODULE_HEALTH_MODELの現在状態 |
| Lifecycle | MODULE_LIFECYCLEの現在状態 |
| Certification | MODULE_CERTIFICATIONの現在レベル |
| Dependencies | MODULE_DEPENDENCY_MODELに基づく依存モジュール一覧 |
| Last Audit | 直近のMODULE_AUDIT_PROTOCOL実施日とResult |
| Last Updated | Registry Entryの最終更新日時（ISO8601） |

---

## 6. Consistency Rules

- 同一条件では同一結果を返すこと
- Registryとの整合性を維持すること
- Historical Versionを指定可能とすること
- Queryは状態を変更しないこと

---

## 7. Error Handling

| エラー種別 | 説明 |
|------------|------|
| Module Not Found | 指定されたmodule_idまたはModule Nameに対応するエントリがRegistryに存在しない |
| Version Not Found | 指定module_idは存在するが、Requested VersionがVersion Indexに存在しない |
| Invalid Query | Query ParametersがQuery Typeに対して不正・不足している |
| Unsupported Query | Section 3に定義されていないQuery Typeが指定された |
| Registry Unavailable | Registry自体が参照不能（一時的な障害等） |

---

## 8. Non Goals

本仕様では以下を対象外とする。

- API通信
- 認証・認可
- UI検索画面

---

## Appendix A: 制度仕様との関係

```
MODULE_REGISTRY_MODEL
        │
        ▼
MODULE_INDEX_SPEC
        │
        ▼
MODULE_QUERY_PROTOCOL
        │
        ▼
MODULE_CATALOG
```

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Draft | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
