# MoCKA 1.0 Audit Baseline v1.0

**Status**: Audit Baseline(Frozen)
**Date**: 2026-07-24
**Scope**: MoCKA Caliber統合監査(Orchestra / Relay / Memory / PHI-OS)、Step1〜Step8
**根拠**: Step1〜Step6-B(読み取り専用調査)、Step6-C Canonical Context Architecture v1.0 Audit Freeze Report、Step7 Governance Consolidation Report v1.0、Step8 MoCKA 1.0 Product Readiness Assessment(訂正版)
**制約**: 本監査全体を通じ、コード変更・実装・Decision Ledger追加は一切行っていない(読み取り専用のEvidence Captureのみ)。

本文書はMoCKA 1.0監査フェーズ(Step1〜Step8)の最終成果物であり、以後の設計・実装作業はここに固定されたConfirmed事項を基準として進めることができる。本文書の完成をもって監査フェーズは完了とする。

---

## 1. Canonical Context Architecture(構造の確定)

### 1.1 5層構造

| 層 | 責務 | Canonical Source | PHI-OS管理 |
|---|---|---|---|
| Canonical Ledger | 一次データの永続保持 | `mocka_events.db`・`decision_ledger.jsonl`・`integrity_classification.jsonl`・`MOCKA_TODO_ACTIVE.json` | Event Ledgerのみ Yes |
| Canonical Context | Event Ledgerから再構成された現在状態 | なし(派生)。essenceテーブルがLedgerに最近接 | Working ContextのみYes |
| Projection Layer | Canonical情報のファイル書き出し | なし(全て派生)。`interface/lever_essence.json`がProjection内正本 | Context SnapshotのみYes |
| View Layer | エンドユーザー向け表示合成 | なし(都度合成) | No |
| Runtime Layer | 実行主体(6稼働プロセス+sync_watch.py) | N/A | 部分的 |

### 1.2 Architecture Boundary

- **A. Runtime Boundary**: 確認された6稼働プロセス(app.py×2 / mocka_mcp_server.py / gateway.py / mocka_caliber_server.py / living_room/hub.py)+sync_watch.py(常駐daemon)
- **B. Governance Boundary**: `phi_os/event_gate.py`が実際に検証・制御する範囲。Event Ledgerのみ完全収束、Decision Ledgerはcompanion eventのみ部分収束、Integrity Classification・TODOは境界外
- **C. Projection Boundary**: `essence_auto_updater.py` / `ping_generator.py` / `export_for_cloudflare.py`が構成。Canonical側の更新頻度と非同期(一発起動+10分毎コピー)
- **D. Presentation Boundary**: `handshake.py`系(Living Contextウィジェット)。Projection Boundary(ESSENCE系)とは非接続

### 1.3 確定した構造図

```
Runtime → Governance(Event Ledgerのみ完全収束) → Projection(Canonical側と非同期) → Presentation(Projectionと非接続、別経路で独立合成)
```

### 1.4 境界を越える確認済み経路

- `mocka_write_event`(Runtime)→`event_gate.py`(Governance)
- `mocka_decision_write`のcompanion event(Runtime)→`event_gate.py`(Governance、部分)
- `gateway.py /api/v1/event`(Runtime)→`event_buffer.py`→`event_gate.py`(Governance)
- `mocka_events.db`内essenceテーブル(Governance)→`essence_auto_updater.py`→`interface/lever_essence.json`(Projection)
- `interface/lever_essence.json`(Projection)→`mocka_get_essence`(Runtime、消費)
- `data/lever_essence.json`(Projection)→`gateway/context_builder.py`・`gateway.py`(Runtime、消費)→**External AI**
- `MOCKA_TODO.json`(root)+`recurrence_registry.csv`→`handshake.py`(Presentation)

---

## 2. Governance構造の確定

| Governance | Canonical Source | Authority | Boundary | Status |
|---|---|---|---|---|
| Event Governance | `mocka_events.db` | `phi_os/event_gate.py` | Governance Boundary内 | **PASS** |
| Decision Governance | `decision_ledger.jsonl` | mocka_mcp_server.py自前検証+companion event | 部分的にGovernance Boundary内 | **PARTIAL** |
| Integrity Governance | `integrity_classification.jsonl` | mocka_mcp_server.py自前検証のみ | Governance Boundary外 | **BYPASS** |
| Context Governance | essenceテーブル/`interface/lever_essence.json` | `essence_auto_updater.py`(一発起動)、`WorkingContext.live_update()` | Projection Boundaryに帰属 | **STALE**(essence系)/**DORMANT**(Working Context・Context Snapshot) |
| Process Governance | なし | `phi_os/process_manager.py`(importerゼロ) | Runtime Boundaryのみ | **DORMANT** |
| Human Governance | `mocka_events.db`(設計上) | `phi_os/human_gate.py`(app.py未mount) | 実質境界外 | **DORMANT** |

**確定事実(Governance)**: MoCKAは単一Gateではなく、Event Ledger向けGate(完全収束)と、Decision / Integrity / TODOそれぞれ独自の検証経路が併存する構造である。Decision Ledgerのみcompanion eventによる部分的なGovernance Boundaryへの接続を持つ。

---

## 3. 統合Issue分類

| Status | 該当項目 | Business Impact |
|---|---|---|
| **PASS** | Event Ledger書込み経路、gateway.py書込み経路(`/api/v1/event`) | Low(正常機能) |
| **PARTIAL** | Decision Ledger(companion eventのみGate経由)、living_room/hub.py(DRY_RUN固定)、Orchestra稼働正本(Legacy Write Pattern併存) | Medium |
| **BYPASS** | Integrity Classification、TODO(ACTIVE、自前hash監査あり)、Relay R2(`relay_kernel.py`、別DB`data/relay/event_log.db`) | Integrity/TODO=Medium、Relay R2=Low |
| **STALE** | ESSENCE(essenceテーブル・`lever_essence.json`、External AI配信あり) | **Critical**(ただしKnown Limitation、非Blocker) |
| **STALE** | `ping_latest.json`、Relay R2 event_log.db(約1ヶ月更新なし)、第3のlever_essence.json(planningcaliber別リポジトリ) | Low(内部限定) |
| **DORMANT** | `phi_os/human_gate.py` | High(Known Limitation、非Blocker) |
| **DORMANT** | `phi_os/process_manager.py`、Context Snapshot/Working Context(消費者不明)、`core_kernel/`全体、root`memory/`、Orchestra乖離コピー(B') | Low(稼働runtime非接続) |
| **UNKNOWN** | Recurrence Registry更新主体、TODO(root)同期詳細、Working Context消費者、Context Snapshot呼出元 | Medium(未検証だが機能不全は未Confirmed) |

---

## 4. Product Readiness

### 4.1 必須機能分類

- **Must Have**: Event Ledger(PASS)、Decision Ledgerの永続化(PARTIAL、記録自体は成立)
- **Should Have**: Governance統一(Integrity/Decision)、ESSENCE鮮度、Human Gate実行時接続
- **Nice to Have**: Process Governance自動化、Context Snapshot消費経路、並行実装群の整理

### 4.2 Release Readiness Matrix

| Component | Status | Business Impact | Release Blocker | Notes |
|---|---|---|---|---|
| Event Ledger | PASS | Low | No | — |
| Decision Ledger | PARTIAL | Medium | No | 記録は成立、Gate非経由は内部統制課題 |
| Integrity Classification | BYPASS | Medium | No | 自前検証で記録成立 |
| TODO(ACTIVE) | BYPASS | Medium | No | 独自hash監査で信頼性担保 |
| ESSENCE / Context Projection | STALE | Critical | **No** | Known limitation: 鮮度は一発起動更新に依存。データ破損・誤動作なし、境界明確、開示可能 |
| ESSENCE内部生成物 | STALE | Low | No | 内部限定 |
| Human Governance | DORMANT | High | No | 専用機構は不在だが、承認事実はDecision Ledgerの`approved_by`で記録・参照可能。Known limitation |
| Process Governance | DORMANT | Low | No | 手動運用で機能代替中 |
| Context Snapshot / Working Context | DORMANT | Low | No | 消費者未確認、利用者影響なし |
| Relay R2 | BYPASS/STALE | Low | No | 利用実績未確認 |
| core_kernel/全体等 | DORMANT | Low | No | 稼働runtime接続なし |
| Recurrence Registry等 | UNKNOWN | Medium | No | 未検証だが機能不全は未Confirmed |

**Release Blocker = Yesの項目: 0件**

---

## 5. Release ReadinessとKnown Limitations

### 5.1 Release Readiness判定

# READY WITH LIMITATIONS

判定基準: NOT READY基準(データ破損/記録不能/セキュリティ問題/ガバナンス不成立/主機能不成立)に該当する項目は**0件**。Event Ledger・Decision Ledger・Integrity Classificationはいずれも記録として成立している(Confirmed)。Release Blocker = Yesの項目も**0件**。

### 5.2 Known Limitations(既知の制限事項、開示可能)

1. **ESSENCE / Context Projectionの鮮度制限**
   `interface/lever_essence.json`(正本)はMoCKA起動時の一発生成のみで更新され、常駐更新機構は存在しない。`data/lever_essence.json`は10分毎の機械的コピーだが内容自体は更新されない。この情報はGateway経由でExternal AIへ配信される。データ破損・誤動作は伴わないが、配信内容が起動時点で凍結されている可能性がある。

2. **Human Governance専用機構の未接続**
   `phi_os/human_gate.py`は「Human Gate状態管理の唯一の真実」として設計されているが、確認された6稼働プロセスのいずれからも呼び出されていない。ただし、人間承認の事実自体はDecision Ledgerの`approved_by` / `approved_at`フィールドを通じて別経路で記録・参照可能であり、承認プロセスの記録機能そのものは失われていない。

3. **統治経路の非統一(参考情報)**
   Decision Ledger・Integrity Classification・TODOはPHI-OS Gateを経由しない独自検証経路を持つ。いずれも記録自体は確実に成立しており(Confirmed)、機能不全ではないが、単一Gateへの統一はされていない。

### 5.3 監査Baselineとして固定される事項

- Canonical Ledgerは4種(Event / Decision / Integrity / TODO)存在し、いずれも記録として機能している
- PHI-OS Gateが完全収束しているのはEvent Ledgerのみ
- ESSENCE系は正本(`interface/`)とコピー(`data/`)の1対の関係であり、両者に内容の乖離はない
- Living Contextウィジェット(Presentation層)はESSENCE系と非接続の別経路である
- 稼働runtimeに接続されていないコンポーネント(`core_kernel/`全体、root`memory/`、`phi_os/human_gate.py`、`phi_os/process_manager.py`、Orchestra乖離コピー、一部のRelay系)は、利用者への影響がConfirmedされていない

---

## Audit Baseline宣言

本文書「MoCKA 1.0 Audit Baseline v1.0」を、MoCKA 1.0監査フェーズ(Step1〜Step8)の最終成果物(Audit Baseline)として確定する。以後の設計・実装作業は、本文書に記載されたConfirmed事項を基準として進めることができる。

改善案・実装案・設計変更案は含まれていない。新規調査・新規推測は行っていない。

**監査フェーズ完了。**
