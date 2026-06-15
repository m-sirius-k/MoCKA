# PRE_CONSTRAINT_ARCHITECTURE_v1.md
# Pre-Constraint Architecture（初期制約固定アーキテクチャ）

Document ID: PRE_CONSTRAINT_ARCHITECTURE_v1
Version: 1.0.0（固定・上書き禁止。変更は新バージョンとして分岐）
Status: 正本仕様（governance/architecture）
作成日: 2026-06-15
記録元: きむら博士「保存・統合指示」（MoCKA正式構造更新イベント）

---

## 1. 目的

- 初期設計の重さを正当化し、後工程コストを削減するための構造固定。
- 実験(PlanningCaliber)と本番(MoCKA)の境界を制度として明確化する。
- 仕様揺れの発生源を初期で封じる。

## 2. レイヤ構成

```
Pre-Constraint Layer   （変更禁止の初期固定仕様）
        ↓ 従属
Execution Layer        （Pre-Constraint Layerに必ず従属）
        ↓ 後工程
Compression Layer      （後工程専用の削減処理のみ）
```

### 2.1 Pre-Constraint Layer
- 「変更禁止の初期固定仕様」として扱う。
- ここで固定された制約は、Execution Layer以下のあらゆる実行・生成の前提条件となる。
- 仕様変更が必要な場合は、本ファイルを上書きせず **新バージョン（v2, v3, ...）として分岐** する。
  既存バージョンは履歴として保持される。

### 2.2 Execution Layer
- Pre-Constraint Layerに定義された制約に必ず従属する。
- 制約を満たさない実行はEvent Logに記録のうえ拒否される。

### 2.3 Compression Layer
- 後工程専用の削減処理（要約・圧縮・統合）としてのみ実装する。
- Pre-Constraint Layerの内容を変更・上書きする処理を含んではならない。

## 3. 統合ルール（固定・上書き禁止）

1. Pre-Constraint Layerは「変更禁止の初期固定仕様」として扱う。
2. Execution Layerは必ずこの制約に従属する。
3. Compression Layerは後工程専用の削減処理として実装する。
4. 仕様変更が必要な場合は「新バージョン」として分岐する（上書き禁止）。

## 4. 既存構造との整合（必須連携）

本アーキテクチャは以下の既存構造と矛盾しないことを確認済み：

- **Shadow Execution Layer**: shadow_Movement（縮退運用・75%機能維持）はExecution Layer内の運用モードであり、Pre-Constraint Layerへの従属関係は変わらない。
- **Audit / Verification Layer**: `governance/verify_*.py` 群によるALL CHECKS PASSED検証は、Pre-Constraint Layerの制約適合性チェックの一部として機能する。
- **PlanningCaliber実験ループ**: 実験は本アーキテクチャの「実験側」境界に位置し、Pre-Constraint Layerで固定された制約のもとで自由に試行できる。実験結果のMoCKA本体への昇格は第5節のP0-P4モデルに従う。
- **MoCKA昇格モデル（P0〜P4）**: 実験(PlanningCaliber)からMoCKA本番への昇格段階。Pre-Constraint Layerの制約は各段階を通じて不変。

## 5. 保存位置（三層反映）

| 層 | パス | 役割 |
|---|---|---|
| 正本仕様 | `docs/architecture/PRE_CONSTRAINT_ARCHITECTURE_v1.md`（本ファイル） | バージョン管理対象・正本(v1固定) |
| 実行時強制ルール | `runtime/constraints/pre_constraint_layer_v1.json` | Pre-Constraint Layerを機械的に適用可能にする展開形 |
| 設計思想ドキュメント | `docs/lifecycle/PRE_CONSTRAINT_ARCHITECTURE_LIFECYCLE_v1.md` | PlanningCaliber〜MoCKA移行の基準文書 |

## 6. バージョニング

- 本ファイルはv1として固定。
- 仕様変更時は `PRE_CONSTRAINT_ARCHITECTURE_v2.md` 等として新規作成し、本ファイルは履歴として保持する。
- `runtime/constraints/` 側も `pre_constraint_layer_v2.json` のように同期してバージョン分岐する。
