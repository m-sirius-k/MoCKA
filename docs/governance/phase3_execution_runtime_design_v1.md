# MoCKA Phase3 — Execution Runtime Layer Design v1.0 [EXECUTION-ARCHIVE]

Status: EXECUTION-ARCHIVE / INACTIVE（2026-06-25、博士裁定により非アクティブ保管設計に分類変更）
**[2026-06-25 FINAL CONSOLIDATION追記]** 本文書は「保管構造（稼働しうる第二の層）」ではない。
構造ではなく**記録**であり、設計履歴の保存領域（非構造・参照停止）として位置づけ直す。
Phase3は単層であり、有効なのは`docs/governance/phase3_simulation_sealed_v1.md`（SIMULATION-SEALED）のみ。
本文書はその唯一性を損なわない、単なる過去設計案の履歴記録である。
Date: 2026-06-25（原案作成）/ 2026-06-25（ARCHIVE化）/ 2026-06-25（記録化・FINAL CONSOLIDATION）
分類: **Phase3-EXECUTION-ARCHIVE**（4層モデル、potential execution system＝「動く前提の設計」だった案の記録）。
現行採用はこちらではなく `docs/governance/phase3_simulation_sealed_v1.md`（3層モデル、SIMULATION-SEALED v1.0、Phase3の唯一の有効モデル）である。
本文書の内容（Trigger Layer/Execution Core/Safety Interceptor/State Transition Layerの4層）は、
将来Bルート（実行接続）に進む場合に参照されうる設計履歴として保存するのみであり、現時点では一切有効化しない。
4層モデルへの移行条件は永続的に未定義であり、「未定義のまま固定」自体が仕様である。
前提文書: `docs/governance/phase2_execution_governance_v1.md`、
`docs/governance/phase2_execution_governance_finalization_v1.md`（Phase2 LOCKED、commit 4512b71c1 / tag phase2-execution-governance-v1.0）
裁定者: 博士のみ。本文書はPhase3の構造案（旧案）を提示するのみで、最終確定（Finalization）は行っていない。ARCHIVE化自体もFinalizationではなく分類変更である。

---

## 0. Phase3の定義

Phase2とPhase3の違いは明確に分離する。

| Phase | 内容 |
|---|---|
| Phase2 | 実行「していいか」の統治（Governance / Control Layer） |
| Phase3 | 実行「したときどう動くか」の設計（Execution Runtime / Action Layer、設計のみ） |

Phase3 = Execution Runtime Layer：
「Execution ApprovalがAPPROVEされたときに何が起こるかを定義する層」。
ただし本文書は定義のみであり、Trigger自体は有効化しない。

---

## 1. 絶対ルール（最優先・本文書全体に適用）

### 1.1 禁止事項

* Phase2の確定範囲（Execution Approval仕様・Boundary・Safety Gate・Rollback方針）を超えて新たな判断を行わない。
* 実行そのものは設計しない（コード化・Adapter接続・Trigger実装は本文書の対象外。まだ禁止）。
* 自動実行トリガを有効化しない。

### 1.2 許可事項

* 実行の「シナリオ設計」（何が起こるかの記述）
* 状態変化（success/partial/fail等）の定義
* 安全停止条件の設計

本文書はこの範囲内でのみ記述する。

---

## 2. Phase3の構造（4層）

### 2.1 Trigger Layer（起動条件）

* APPROVE発火条件（Phase2 Execution Approval確定値がAPPROVEの場合のみ評価対象になる）
* HOLD解除条件（博士による再確認・確定値の更新を要する）
* REJECT固定条件（REJECT確定後はTrigger Layerに到達しない）

### 2.2 Execution Core（実行本体）

* コマンド変換（Approvalされた内容を実行可能な単位に変換する、という構造のみ。変換ロジック自体は本文書では実装しない）
* サブシステム呼び出し（呼び出し対象・呼び出し境界の定義のみ）
* 実行単位の分解（Level1/2/3のRollback単位と対応させる）

### 2.3 Safety Interceptor（即時停止層）

* GL7再検出（検出層としての位置づけはPhase2 Safety Gate設計と同一原則：検出と確定の分離を継承）
* runtime異常検知
* rollbackトリガ監視

### 2.4 State Transition Layer（状態遷移）

* success / partial / fail の3状態
* retry禁止 or 許可の方針（本文書では「原則retry禁止、許可は個別Human Gate判断を要する」という設計方針のみ提示）
* rollback自動発火条件（発火条件の定義のみ。自動発火そのものは未有効化）

---

## 3. Execution Flow（標準経路・設計のみ）

```
APPROVAL（Phase2確定値）
   ↓
Trigger Validation
   ↓
Execution Core Start
   ↓
Safety Interceptor Monitoring
   ↓
State Transition
   ↓
Final State Commit OR Rollback
```

本フローは経路の定義であり、各ステップの実装（コード）は本文書の対象外。

---

## 4. Rollback（Phase3の核心）

### 4.1 3段階

| Level | 単位 |
|---|---|
| Level 1 | operation rollback |
| Level 2 | commit rollback |
| Level 3 | Phase snapshot rollback（Phase1/Phase2へ） |

Phase2で確定済みのLevel1-3（File/Commit/Snapshot）と対応関係を持つが、Phase3では「実行操作（operation）」単位が追加される点が異なる。

### 4.2 トリガ条件

* GL7再検出
* runtime↔governance矛盾
* execution partial failure
* safety interceptor trigger

これらはPhase2 Rollback設計（3.2節）のトリガ条件を継承し、Phase3固有の条件（execution partial failure、safety interceptor trigger）を追加するものである。

---

## 5. Safety Interceptor設計（常時監視・設計のみ）

監視対象：

* execution anomaly
* state drift
* unauthorized trigger
* submodule mutation impact

即時動作（定義のみ、実装は対象外）：

* STOP
* FREEZE
* ROLLBACK
* HOLD fallback

---

## 6. Phase3終了条件（実行結果としての終了、本文書設計とは別概念）

### 6.1 成功

* Execution complete
* State consistent
* No safety trigger fired

### 6.2 失敗

* rollback to Phase2 or Phase1
* system freeze
* HOLD state re-entry

注：本節は「実行が行われた場合の終了条件」を定義するものであり、本文書（DRAFT設計）自体の終了条件ではない。本文書自体の終了条件は第8節を参照。

---

## 7. Phase2との分離原則

Phase2が「実行を止める層」、Phase3が「実行を起こす層」であり、両者は完全に分離されている。
Phase3の設計はPhase2のLOCKED状態（commit 4512b71c1 / tag phase2-execution-governance-v1.0）を変更しない。
Phase3 Trigger Layerの起動条件（2.1節）は常にPhase2 Execution Approval確定値を前提とし、Phase3側で独自にAPPROVE/HOLD/REJECTを生成しない。

---

## 8. 本文書（DRAFT設計）自体の終了条件

Phase3設計のFinalization（確定）には、以下が博士により確認されることを要する。

| 条件 | 状態 |
|---|---|
| Trigger Layer起動条件確定 | 構造案提示済み（博士確定待ち） |
| Execution Core境界確定 | 構造案提示済み（博士確定待ち） |
| Safety Interceptor設計確定 | 構造案提示済み（博士確定待ち） |
| State Transition Layer確定 | 構造案提示済み（博士確定待ち） |
| Rollback 3段階確定 | 構造案提示済み（博士確定待ち） |

**現時点のStatusはDRAFTのまま。** 本文書はPhase3の「実行の安全構造設計」を提示するものであり、Execution実装・Trigger有効化・自動実行は一切含まない。
Phase3 Finalizationが確定しても、それは実行可能化を意味しない——Phase2のFinalizationと同様、Finalization自体は「設計の確定」であり「実行許可」ではない。実行可能化にはさらに別個の新規判断（Trigger Layer有効化の明示的着手判断）を要する。

## 関連文書

- `docs/governance/phase2_execution_governance_v1.md`
- `docs/governance/phase2_execution_governance_finalization_v1.md`
