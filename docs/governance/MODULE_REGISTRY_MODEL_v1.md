# MoCKA Module Registry Model v1

**Document ID**: MODULE_REGISTRY_MODEL_v1
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-06-15
**Reference**: MODULE_CATALOG_v1, MODULE_AUDIT_PROTOCOL_v1, MODULE_HEALTH_MODEL_v1, MODULE_LIFECYCLE_v1, MODULE_CERTIFICATION_v1
**Reference Event**: E20260615_067

---

## 1. Purpose

MoCKA内のすべてのModuleを一元管理するRegistryモデルを定義する。

RegistryはModuleの唯一の公式情報源（Single Source of Truth）とし、Audit・Health・Lifecycle・Certificationとの連携基盤となる。

---

## 2. Design Principles

- Registry is the authoritative source.
- Every Module has exactly one registry entry.
- Registry records are version-aware.
- Registry preserves historical records.
- Registry integrates governance metadata.

---

## 3. Registry Entry

各Moduleについて最低限保持する。

| フィールド | 説明 |
|-----------|------|
| Module ID | module_id（MODULE_CATALOG準拠・一意） |
| Module Name | モジュール名 |
| Version | 現行バージョン（vX.Y.Z） |
| Owner | 所有者（きむら博士 / Claude / くろこ 等） |
| Category | MODULE_DEPENDENCY_MODELのDependency Level / 役割分類 |
| Dependencies | MODULE_DEPENDENCY_MODELに基づく依存モジュール一覧 |
| Maturity Level | MODULE_MATURITY_MODELのLevel（M0〜M5） |
| Health State | MODULE_HEALTH_MODELの現在状態 |
| Lifecycle State | MODULE_LIFECYCLEの現在状態 |
| Certification Level | MODULE_CERTIFICATIONの現在レベル |
| Current Status | Registry Operations上の状態（Active / Deprecated / Archived） |
| Last Audit | 直近のMODULE_AUDIT_PROTOCOL実施日とResult |
| Last Updated | 最終更新日時（ISO8601） |

---

## 4. Registry Operations

| Operation | 説明 |
|-----------|------|
| Register | 新規ModuleをRegistryに登録する。Module IDを発行し、初期エントリを作成する |
| Update | 既存エントリのフィールドを更新する。更新前の状態は履歴として保持する |
| Deprecate | Current StatusをDeprecatedへ変更する。MODULE_LIFECYCLEのDEPRECATED遷移と連動する |
| Archive | Current StatusをArchivedへ変更する。MODULE_LIFECYCLEのARCHIVED遷移と連動する |
| Query | Module ID・Category・Status等を条件にエントリを検索・参照する（読み取り専用） |
| Verify | Registryエントリの内容がAudit・Health・Lifecycle・Certificationの最新記録と整合しているか確認する |

---

## 5. Integrity Rules

- Module IDは一意であること。
- Version履歴は保持すること。
- Registry更新はイベントとして記録すること。
- 削除ではなく履歴管理を基本とすること。

---

## 6. Relationships

| 連携先 | 連携内容 |
|--------|----------|
| Module Catalog | RegistryはMODULE_CATALOGの登録情報（module_id・owner・public_interfaces等）を正本として参照する |
| Audit | RegistryのLast Audit / Certification Levelは MODULE_AUDIT_PROTOCOL の監査結果（Evidence・Result）を反映する |
| Health | RegistryのHealth StateはMODULE_HEALTH_MODELのHealth Recordから更新される |
| Lifecycle | RegistryのLifecycle State・Current StatusはMODULE_LIFECYCLEの状態遷移と同期する |
| Certification | RegistryのCertification LevelはMODULE_CERTIFICATIONのCertification Recordから更新される |
| Event Foundation | Registry Operations（Register/Update/Deprecate/Archive）は全てmocka_write_eventで記録され、EVENT_FOUNDATIONの不変条件に従う |

---

## 7. Non Goals

本仕様では以下を対象外とする。

- データベース実装
- API実装
- UI実装

---

## Appendix A: 制度仕様との関係

```
MODULE_CATALOG
        │
        ▼
MODULE_AUDIT_PROTOCOL ─┐
MODULE_HEALTH_MODEL    ├──▶ MODULE_REGISTRY_MODEL
MODULE_LIFECYCLE       │
MODULE_CERTIFICATION ──┘
        │
        ▼
EVENT_FOUNDATION
```

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Draft | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
