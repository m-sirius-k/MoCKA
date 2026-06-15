# MoCKA Module Catalog v1

**Document ID**: MODULE_CATALOG_v1
**Version**: 1.0.0
**Status**: Active
**Created**: 2026-06-15
**Depends On**: VERSION_POLICY_v1.md (v1.0.0), DECISION_LEDGER_SCHEMA_v1.md (v1.0.0), MODULE_MATURITY_MODEL_v1.md (v1.0.0), MODULE_DEPENDENCY_MODEL_v1.md (v1.0.0)

---

## 1. Purpose

MoCKA制度OSを構成する全モジュールを制度的に登録・管理する。

MODULE_MATURITY_MODELおよびMODULE_DEPENDENCY_MODELと連携し、モジュール管理の唯一の公式台帳とする。

---

## 2. Scope

対象：

- PHI-OS
- Orchestra
- Relay
- Memory
- Prism
- Caliber
- TIC
- mini-MoCKA
- vasAI
- 将来追加される全モジュール

---

## 3. Module Registration Rules

各モジュールは以下を必須とする。

| フィールド | 説明 |
|-----------|------|
| module_id | 一意の識別子（例: MOD_PHI_OS） |
| module_name | モジュール名 |
| summary | 役割の一行要約 |
| owner | 所有者（きむら博士 / Claude / くろこ 等） |
| repository | リポジトリパスまたはURL |
| maturity_level | MODULE_MATURITY_MODELのLevel（M0〜M5） |
| dependency_level | MODULE_DEPENDENCY_MODELのLevel（0〜3） |
| lifecycle_status | Section 4のStatus |
| public_interfaces | 公開API・公開関数・公開エンドポイント一覧 |
| related_documents | 関連仕様書一覧 |
| related_decisions | 関連Decision ID一覧（DC_YYYYMMDD_NNN） |
| created_at | 登録日（ISO8601） |
| last_updated | 最終更新日（ISO8601） |

`module_id` は一意であること。

---

## 4. Lifecycle Status

| Status | 意味 | 遷移条件 |
|--------|------|----------|
| Proposed | 提案段階。設計概要のみ存在 | Decision Ledger登録によりDevelopingへ遷移 |
| Developing | 実装中 | 基本動作確認完了によりTestingへ遷移 |
| Testing | テスト・検証中 | テスト自動化・mocka_write_event連携完了によりActiveへ遷移 |
| Active | 本番運用中 | 廃止決定（Decision Ledger登録）によりDeprecatedへ遷移 |
| Deprecated | 廃止予定 | 後継モジュールへの移行完了によりArchivedへ遷移 |
| Archived | 保守終了 | 終端状態 |

---

## 5. Maturity Integration

MODULE_MATURITY_MODELとの対応：

| Maturity Level | Lifecycle Status |
|-----------------|-------------------|
| M0〜M1 | Proposed |
| M2 | Developing |
| M3 | Testing |
| M4 | Active |
| M5 | Active（Institutional区分） |

---

## 6. Dependency Integration

MODULE_DEPENDENCY_MODELとの対応として、各モジュールは以下を登録する。

| フィールド | 説明 |
|-----------|------|
| Dependency Level | MODULE_DEPENDENCY_MODEL Section 4のLevel（0〜3） |
| Allowed Dependencies | MODULE_DEPENDENCY_MODEL Section 5に従い依存可能なモジュール一覧 |
| Required Dependencies | 実際に依存しているモジュール一覧（Allowed Dependenciesの部分集合） |

---

## 7. Required Documents

各モジュールは最低限以下への参照を持つこと。

- README
- VERSION_POLICY
- MODULE_MATURITY_MODEL
- MODULE_DEPENDENCY_MODEL
- DECISION_LEDGER
- CHANGE_TRANSACTION_PROTOCOL

必要に応じてイベント仕様（EVENT_FOUNDATION / EVENT_DATA_LIFECYCLE / EVENT_TRANSITION_PROTOCOL）も追加する。

---

## 8. Audit Requirements

監査項目：

- module_id が一意
- 所有者が定義されている
- 成熟度が設定されている
- 依存関係が登録されている
- Decision Ledgerと関連付け済み
- 公開インターフェースが明記されている

---

## 9. Initial Catalog

| module_id | Module | Role | maturity_level | dependency_level | lifecycle_status |
|-----------|--------|------|-----------------|-------------------|-------------------|
| MOD_PHI_OS | PHI-OS | 共通基盤 | M3 | 0 | Testing |
| MOD_ORCHESTRA | Orchestra | 会話・オーケストレーション | M4 | 2 | Active |
| MOD_RELAY | Relay | セッション継続・受け渡し | M3 | 1 | Testing |
| MOD_MEMORY | Memory | 長期知識管理 | M3 | 1 | Testing |
| MOD_PRISM | Prism | 認知・解析層 | M0 | 2 | Proposed |
| MOD_CALIBER | Caliber | 計画・運用支援 | M3 | 2 | Testing |
| MOD_TIC | TIC | タグ・インデックス・分類 | M3 | 2 | Testing |
| MOD_MINI_MOCKA | mini-MoCKA | 軽量アプリケーション | M0 | 3 | Proposed |
| MOD_VASAI | vasAI | 公開API利用アプリケーション | M4 | 3 | Active |

> 上記は初期登録例であり、各モジュールの詳細レコード（owner / repository / public_interfaces / related_documents / related_decisions / created_at / last_updated）は今後個別に追記する。

---

## Appendix A: 制度仕様との関係

```
VERSION_POLICY
        │
        ▼
CHANGE_TRANSACTION_PROTOCOL
        │
        ▼
DECISION_LEDGER_SCHEMA
        │
        ▼
MODULE_MATURITY_MODEL
        │
        ▼
MODULE_DEPENDENCY_MODEL
        │
        ▼
MODULE_CATALOG
        │
        ▼
各モジュール仕様
```

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Active | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
