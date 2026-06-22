# MoCKA Forward Packet (FP)

id: FP-HAB-DUPLICATE-POLICY-20260622-01
date: 2026-06-22
phase: MoCKA Phase 4
module: HAB / Trust Boundary pre-design
owner: PlanningCaliber
status: draft (uncommitted snapshot)
linked_todo: HAB Duplicate Policy / window design / TODO_325 dependency
scope: functional + partial governance boundary

---

## 1. 議論背景

HABの責務設計において、「重複検知レベル」と「時間窓（window）」の関係から、
HABの状態保持とTrust Boundary構造の整合性を検討した。

## 2. 確定した機能モデル（HAB Functional Model）

### HAB基本定義

HAB = sliding short-term window filter（短命フィルタ層）

### 重複検知レベル

- **Level 0**
  - event_id一致
  - HABで検知・拒否可能
- **Level 1**
  - payload完全一致（hash一致）
  - HABのwindow内でのみ検知・拒否可能
- **Level 2以上**
  - 操作・意図・結果の重複
  - HABでは判定しない
  - H2-3 Trust Boundaryへ委譲

## 3. 時間モデル（TTL / Window）

- HABはリクエスト単位では破棄されない
- sliding short-term windowを保持する
- window内でのみLevel 1検知が成立する
- events.db全体の参照は禁止

## 4. 状態保持の性質

- HABは短期運用状態のみ保持
- セッション/TTLベースの一時キャッシュ構造
- 永続ストレージへの依存なし
- 記録責任を持たない

## 5. 未確定事項（保留）

windowサイズの決定主体

未決定。以下の論点が未解決：

- HAB設定権限の所在
- Relay / PHI-OS / HABのどこが制御するか
- Trust Boundaryとの関係

## 6. 制度的論点

windowサイズ決定は単なる技術設定ではなく：

- HABの挙動制御権限問題
- MoCKAにおけるガバナンス問題
- Trust Boundaryの外部操作可能性

を含むため、別フェーズで扱う必要がある。

## 7. 分離状態

- HAB Functional Model：確定
- HAB Governance Model：未確定（保留）

## 8. 次回論点

- windowサイズの決定主体
- HAB設定変更権限の配置
- Trust Boundaryとの権限分離設計

## 9. 取扱方針

このFPは observation log として保持される。mocka_write_event による正式記録は、
HAB / H2-3 / ACL が収束した後、または Relay 設計直前の「境界スナップショット」
として一括記録する方針（2026-06-22 PHL observation / R01 review）。
