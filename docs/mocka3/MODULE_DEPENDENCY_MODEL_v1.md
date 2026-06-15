# MoCKA Module Dependency Model v1

**Document ID**: MODULE_DEPENDENCY_MODEL_v1
**Version**: 1.0.0
**Status**: Active
**Created**: 2026-06-15
**Depends On**: VERSION_POLICY_v1.md (v1.0.0), DECISION_LEDGER_SCHEMA_v1.md (v1.0.0), MODULE_MATURITY_MODEL_v1.md (v1.0.0)

---

## 1. Purpose

モジュール間依存関係を制度として定義する。全モジュールは本仕様に従って依存関係を構築する。

目的：
- 循環依存の防止
- アーキテクチャの長期維持
- 将来モジュール追加時の設計基準
- PHI-OSを中心とした制度OS全体の一貫性確保

---

## 2. Scope

対象モジュール：

- PHI-OS
- Orchestra
- Relay
- Memory
- Prism
- Caliber
- TIC
- 今後追加される全モジュール

---

## 3. Dependency Principles

- 循環依存禁止
- 上位層から下位層への依存のみ許可
- 共通機能はPHI-OSへ集約
- モジュール間通信は公開インターフェース経由
- 内部実装への直接依存禁止

---

## 4. Dependency Levels

```
Level 0: Core Platform
    PHI-OS

Level 1: Infrastructure
    Memory
    Relay

Level 2: Knowledge Services
    Orchestra
    Prism
    TIC

Level 3: Applications
    mini-MoCKA
    vasAI
    その他アプリケーション
```

依存方向：

```
Level 3 (Applications)
    │
    ▼ depends on
Level 2 (Knowledge Services)
    │
    ▼ depends on
Level 1 (Infrastructure)
    │
    ▼ depends on
Level 0 (Core Platform)
```

下位レベルから上位レベルへの依存（逆方向依存）は禁止。

---

## 5. Allowed Dependencies

| モジュール | 依存可能先 |
|-----------|-----------|
| PHI-OS | なし |
| Relay | PHI-OS |
| Memory | PHI-OS |
| Orchestra | PHI-OS・Relay・Memory |
| Prism | PHI-OS・Memory |
| mini-MoCKA | Orchestra・Relay・Memory |
| vasAI | 全公開API |

### 依存禁止例

| 禁止依存 | 理由 |
|----------|------|
| PHI-OS → Relay / Memory / Orchestra 等 | Level 0は下位層を持たず、上位層への依存は禁止（逆方向依存） |
| Relay → Orchestra | Level 1がLevel 2へ依存することは逆方向依存 |
| Memory → Prism | Level 1がLevel 2へ依存することは逆方向依存 |
| Orchestra → mini-MoCKA | Level 2がLevel 3へ依存することは逆方向依存 |
| モジュールの内部実装（非公開関数・内部DB等）への直接依存 | 公開インターフェース経由でない依存は禁止 |

---

## 6. Circular Dependency Policy

循環依存は禁止。

検出時は **Critical** として扱う。Decision Ledgerへ記録対象とする。

---

## 7. Dependency Change Process

依存追加時：

1. Decision Ledger登録
2. 影響評価
3. レビュー
4. 承認
5. 実装

---

## 8. Audit Requirements

監査で確認する内容：

- 循環依存が存在しない
- 公開APIのみ利用
- Maturity要件を満たす
- Decision Ledger登録済み

---

## 9. Examples

### 正常例

```
PHI-OS
  ↓
Relay
  ↓
Orchestra
  ↓
mini-MoCKA
```

### 異常例（循環依存）

```
Relay
  ↓
Orchestra
  ↓
Relay
```

---

## Appendix A: 他仕様との関係

```
VERSION_POLICY
    ↓
DECISION_LEDGER_SCHEMA
    ↓
MODULE_MATURITY_MODEL
    ↓
MODULE_DEPENDENCY_MODEL
    ↓
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
