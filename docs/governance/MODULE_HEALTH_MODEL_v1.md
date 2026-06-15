# MoCKA Module Health Model v1

**Document ID**: MODULE_HEALTH_MODEL_v1
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-06-15
**Reference**: MODULE_AUDIT_PROTOCOL_v1, MODULE_CATALOG_v1, MODULE_MATURITY_MODEL_v1
**Reference Event**: E20260615_064

---

## 1. Purpose

Module Auditの結果を継続的な状態管理へ接続するため、Module Health Modelを定義する。

本仕様は、モジュールの「現在の健全性」を表現する唯一の標準モデルとする。

---

## 2. Design Principles

- Health is observable.
- Health is measurable.
- Health is reproducible.
- Health is continuously evaluated.
- Health never replaces audit evidence.

---

## 3. Health States

| State | 意味 |
|-------|------|
| UNKNOWN | 健全性が未評価、または評価不能 |
| HEALTHY | 全Indicatorが基準を満たす |
| WARNING | 軽微な問題が1件以上あるが運用に支障なし |
| DEGRADED | 複数または重要なIndicatorが基準未達。機能の一部に影響 |
| CRITICAL | 重大な問題があり、即時対応が必要 |
| FAILED | モジュールが機能していない、または監査でFAIL確定 |
| ARCHIVED | 運用終了。Health評価対象外 |

---

## 4. Health Indicators

最低限以下を評価対象とする。

| Indicator | 説明 |
|-----------|------|
| Documentation | MODULE_CATALOG Section 7 Required Documentsの整備状況 |
| Dependencies | MODULE_DEPENDENCY_MODELに対する依存関係の適合性・循環依存の有無 |
| Test Coverage | テスト自動化・カバレッジ状況 |
| Verification Status | CHANGE_TRANSACTION_PROTOCOLにおけるVERIFIED到達率 |
| Audit Result | MODULE_AUDIT_PROTOCOLによる直近の監査結果（PASS/WARNING/FAIL/BLOCKED） |
| Security | 権限・機密情報・脆弱性に関する既知の問題有無 |
| Maintenance Activity | 直近のイベント記録・コミット活動の有無 |

---

## 5. Health Assessment

各Indicatorは以下のいずれかの評価値を取る。

| 評価値 | 意味 |
|--------|------|
| OK | 基準を満たす |
| MINOR | 軽微な問題あり |
| MAJOR | 重要な問題あり |
| BLOCKING | 機能を停止させる問題あり |
| N/A | 評価対象外 |

### 集約ルール

Module全体のHealth Stateは、Indicator評価値の最も重大な値に基づき以下のルールで決定する。

| Indicator評価の最大値 | Health State |
|------------------------|---------------|
| すべてN/Aまたは未評価 | UNKNOWN |
| すべてOK | HEALTHY |
| MINORが1件以上、MAJOR/BLOCKINGなし | WARNING |
| MAJORが1件以上、BLOCKINGなし | DEGRADED |
| MAJORが2件以上、かつAudit ResultがFAIL | CRITICAL |
| Audit ResultがBLOCKING（FAIL確定でモジュール機能停止） | FAILED |
| lifecycle_statusがArchived（MODULE_CATALOG準拠） | ARCHIVED |

Health判定は再現可能であり、同一のIndicator評価入力に対して常に同一のHealth Stateを返す。

---

## 6. State Transition

```
UNKNOWN
  ↓
HEALTHY
  ↓
WARNING
  ↓
DEGRADED
  ↓
CRITICAL
  ↓
FAILED
  ↓
ARCHIVED
```

### 復旧遷移

問題が解消された場合、以下の復旧遷移を許可する。

| From | To | 条件 |
|------|----|------|
| FAILED | DEGRADED | Audit ResultがFAILからWARNING以下に改善 |
| CRITICAL | WARNING | MAJOR Indicatorが解消され、MINORのみ残存 |
| DEGRADED | HEALTHY | 全IndicatorがOKに改善 |
| WARNING | HEALTHY | 全IndicatorがOKに改善 |
| 任意 | UNKNOWN | 再評価が必要な状態変化（モジュール構成変更等）が発生 |

ARCHIVEDからの復旧遷移は無し（再登録は新規module_idで行う）。

---

## 7. Health Record

最低限保持する項目：

| フィールド | 説明 |
|-----------|------|
| Module | module_id（MODULE_CATALOG準拠） |
| Version | 評価対象のモジュールバージョン |
| Timestamp | 評価実施日時（ISO8601） |
| Current State | Section 3のいずれか |
| Previous State | 直前のHealth State |
| Indicators | Section 4の各Indicatorとその評価値（Section 5） |
| Evidence | 評価に使用した根拠（Audit Evidence・Event ID・コミットハッシュ等） |
| Notes | 補足事項・改善提案 |

---

## 8. Non Goals

本仕様では以下を扱わない。

- 自動監視実装
- 通知システム
- ダッシュボードUI

---

## Appendix A: 制度仕様との関係

```
MODULE_AUDIT_PROTOCOL
        │
        ▼
MODULE_HEALTH_MODEL
        │
        ▼
MODULE_CATALOG / MODULE_MATURITY_MODEL
```

---

## Appendix B: 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Draft | 2026-06-15 |

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-15 | Initial Release |
