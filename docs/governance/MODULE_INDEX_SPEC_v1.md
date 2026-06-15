# MoCKA Module Index Spec v1

**Document ID**: MODULE_INDEX_SPEC_v1
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-06-15
**Reference**: MODULE_REGISTRY_MODEL_v1, MODULE_CATALOG_v1, MODULE_CERTIFICATION_v1
**Reference Event**: E20260615_068

---

## 1. Purpose

Registry内のModuleを高速かつ一貫性を保って検索・参照するための標準Index仕様を定義する。

本仕様はRegistryの論理インデックス構造を規定し、Query ProtocolおよびDiscovery Modelの基盤となる。

---

## 2. Design Principles

- Indexes are deterministic.
- Every index entry references exactly one Module ID.
- Indexes support historical versions.
- Indexes are append-friendly.
- Indexes are independently verifiable.

---

## 3. Required Indexes

| Index | 説明 |
|-------|------|
| Module ID Index | module_idによる一次キー索引。Registryエントリへの直接参照 |
| Module Name Index | Module Nameからmodule_idを引くための索引 |
| Category Index | MODULE_DEPENDENCY_MODELの役割分類・Dependency Levelによる索引 |
| Dependency Index | 依存関係グラフ（どのModuleがどのModuleに依存しているか）の索引 |
| Lifecycle Index | MODULE_LIFECYCLEの現在状態（PLANNED〜ARCHIVED）による索引 |
| Health Index | MODULE_HEALTH_MODELの現在状態（HEALTHY〜FAILED等）による索引 |
| Certification Index | MODULE_CERTIFICATIONの現在レベルによる索引 |
| Version Index | module_idごとのバージョン履歴索引 |
| Event Index | Moduleに関連するmocka_write_eventのEvent ID索引 |

---

## 4. Index Entry

各インデックス項目は最低限以下を保持する。

| フィールド | 説明 |
|-----------|------|
| Index Key | 索引の検索キー（例: module_id, category名, lifecycle state名等） |
| Module ID | 参照先のmodule_id |
| Version | 索引作成時点のモジュールバージョン |
| Registry Reference | MODULE_REGISTRY_MODELのRegistry Entryへの参照 |
| Last Updated | 索引エントリの最終更新日時（ISO8601） |
| Status | 索引エントリの状態（Active / Superseded / Archived） |

---

## 5. Integrity Rules

- Index Keyの一意性: 同一Index内でIndex Keyは一意であること（Version Index・Event Indexは複合キーで一意性を確保する）
- Registryとの整合性: 各索引エントリはMODULE_REGISTRY_MODELの該当Registry Entryと整合していること
- Version追跡: Version IndexはModule IDごとに全バージョン履歴を保持し、現行バージョンを明示すること
- Eventとの対応: Event Indexは関連するmocka_write_eventのEvent IDと1対多で対応すること
- Historical consistency: 索引エントリはStatus変更時も過去のエントリを保持し、上書き・削除しないこと

---

## 6. Query Support

各インデックスが対応すべき検索例：

| 検索条件 | 対応するIndex |
|----------|----------------|
| Module ID | Module ID Index |
| Module Name | Module Name Index |
| Category | Category Index |
| State（Lifecycle / Health） | Lifecycle Index / Health Index |
| Certification | Certification Index |
| Dependency | Dependency Index |
| Version | Version Index |

---

## 7. Non Goals

本仕様では以下を対象外とする。

- データベース実装
- 検索アルゴリズム
- API設計

---

## Appendix A: 制度仕様との関係

```
MODULE_REGISTRY_MODEL
        │
        ▼
MODULE_INDEX_SPEC
        │
        ▼
MODULE_CATALOG / MODULE_CERTIFICATION
```

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Draft | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
