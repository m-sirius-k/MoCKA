# MoCKA Module Discovery Model v1

**Document ID**: MODULE_DISCOVERY_MODEL_v1
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-06-15
**Reference**: MODULE_REGISTRY_MODEL_v1, MODULE_INDEX_SPEC_v1, MODULE_QUERY_PROTOCOL_v1, MODULE_CERTIFICATION_v1
**Reference Event**: E20260615_070

---

## 1. Purpose

MoCKA内のModuleを、属性・状態・依存関係・品質・役割など複数の条件から発見・探索するためのDiscovery Modelを定義する。

本仕様は、Registry・Index・Queryの上位概念として機能し、知識探索の標準モデルとする。

---

## 2. Design Principles

- Discovery is deterministic.
- Discovery never modifies Registry data.
- Discovery combines multiple query dimensions.
- Discovery supports reproducible exploration.
- Discovery is explainable.

---

## 3. Discovery Dimensions

| Dimension | 説明 | 対応Index（MODULE_INDEX_SPEC） |
|-----------|------|-----------------------------------|
| Module Category | 役割分類・Dependency Level | Category Index |
| Functional Role | モジュールが果たす機能的役割 | Module Name Index / Category Index |
| Dependency Relationship | 依存・被依存関係 | Dependency Index |
| Lifecycle State | MODULE_LIFECYCLEの現在状態 | Lifecycle Index |
| Health State | MODULE_HEALTH_MODELの現在状態 | Health Index |
| Certification Level | MODULE_CERTIFICATIONの現在レベル | Certification Index |
| Maturity Level | MODULE_MATURITY_MODELのLevel | Category Index |
| Version | バージョン履歴・現行バージョン | Version Index |
| Event History | 関連するmocka_write_eventの履歴 | Event Index |

---

## 4. Discovery Modes

| Mode | 説明 |
|------|------|
| Exact Match | Module IDまたはModule Nameによる一致検索（MODULE_QUERY_PROTOCOLのQuery by Module ID/Nameを利用） |
| Attribute Search | Category・Lifecycle・Health・Certification・Maturity等の属性条件による検索 |
| Dependency Search | 指定Moduleに依存する/依存される全Moduleの探索（Dependency Index利用） |
| Relationship Search | MODULE_DEPENDENCY_MODELのDependency Levelに基づく上位/下位層のModule探索 |
| Version Search | 指定module_idの全バージョン履歴、または特定バージョン条件に合致するModuleの探索 |
| Similar Module Discovery | 同一Category・同一Dependency Level・同様のCertification Levelを持つModuleの探索 |
| Governance-Based Discovery | MODULE_AUDIT_PROTOCOL/MODULE_CERTIFICATIONの結果に基づく条件（例: CERTIFIED以上、HEALTHY等）での探索 |

---

## 5. Discovery Result

返却項目：

| フィールド | 説明 |
|-----------|------|
| Module ID | module_id |
| Module Name | モジュール名 |
| Match Reason | 検索条件に一致した理由（どのDimension・Modeで一致したか） |
| Relevance Criteria | 一致度判定に用いた基準（Section 6 Ranking Principles参照） |
| Current State | Lifecycle / Health の現在状態 |
| Dependencies | 依存モジュール一覧 |
| Certification | MODULE_CERTIFICATIONの現在レベル |
| Registry Reference | MODULE_REGISTRY_MODELのRegistry Entryへの参照 |

---

## 6. Ranking Principles

結果の優先順位付けは以下の順序で適用する。

1. Exact Match
2. Certified Modules（CERTIFIED以上のCertification Level）
3. Stable Modules（MODULE_LIFECYCLEがSTABLE以上）
4. Newest Version
5. Lowest Dependency Depth（MODULE_DEPENDENCY_MODELのDependency Levelが低い、すなわちCore Platformに近いものを優先）

上位の基準で同順位の場合のみ、次の基準で比較する。

---

## 7. Traceability

Discovery結果には以下を保持する。

| フィールド | 説明 |
|-----------|------|
| Query ID | MODULE_QUERY_PROTOCOLのQuery IDとの対応 |
| Evaluation Criteria | 適用したDiscovery Mode・Dimension・Ranking Principles |
| Timestamp | Discovery実施日時（ISO8601） |
| Registry Version | 探索時点のRegistry状態を示すバージョン/参照 |

---

## 8. Non Goals

本仕様では以下を対象外とする。

- AI推論
- 推薦アルゴリズム
- 機械学習ランキング

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
MODULE_DISCOVERY_MODEL
        │
        ▼
MODULE_CERTIFICATION_v1
```

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Draft | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
