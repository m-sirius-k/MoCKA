# PHI Memory Architecture v1.0

**Status:** DESIGN(正式定義案。Decision Ledger登録はまだ行わない)
**位置づけ:** `PHI_MEMORY_ARCHITECTURE_DESIGN_SCOPE_v0.1.md`承認後、ジャービス化ロードマップ Phase J1本体。PHI-OSのMemory Layerを正式定義する。
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 1. Purpose

PHI Memory Architectureは、単なる会話履歴保存の仕組みではない。

- **Institutional Memory**として機能する(個々の会話ではなく、制度・判断・事実の記録として蓄積される)
- **Evidence-Bound Governance**を支える基盤である(Confirmed/Hypothesis/Unknownの峻別、Decision Ledgerの`related_documents`/`related_events`による裏付けが、Memory層の設計と一体である)
- PHI-OS Core(`phios/`+`ise/`)における「制度的に記録された記憶」であり、単なるチャット履歴とは区別される

---

## 2. Memory Layer Model

PHI Memory Layerを以下の4分類として正式化する。

| Memory Type | 定義 |
|---|---|
| **Event Memory** | 発生した事実・観測。誰が・いつ・何をしたかの記録 |
| **Decision Memory** | 判断・承認・却下理由。alternatives/rationale/impactを伴う裁定の記録 |
| **Semantic Memory** | 概念・制度・設計知識。Constitution・設計文書・用語定義 |
| **Procedural Memory** | 手順・運用方法。CHANGE_START/CHANGE_DONEプロトコル等の運用手順そのもの |

---

## 3. Existing Asset Mapping(既存資産との対応、Confirmed)

| Memory Type | 既存機構 |
|---|---|
| Event Memory | Event Ledger(`data/mocka_events.db`、`phi_os/event_gate.py`) |
| Decision Memory | Decision Ledger(`mocka_decision_write/get/list`、本セッションで`DC_20260729_001`〜`010`運用実績あり) |
| Semantic Memory | Docs(`PHI_OS_CONSTITUTION_v1.md`等) / Constitution |
| Procedural Memory | Runbook / Operational Docs(`MoCKA/.claude/CLAUDE.md`のCHANGE_START/DONEプロトコル等) |

**この対応表が示すこと**: 4分類のうち3つ(Event/Decision/Procedural)は既に稼働中の機構に直接対応する。新規に設計を要するのは、これらを**統一的にMemoryとして扱う枠組み**(§4以降)であり、個別の記録機構そのものではない。

---

## 4. Memory Lifecycle

既存制約(§5参照)を反映した7段階のライフサイクル。

```
Creation
   |
   v
Verification        <- 既存: integrity.sign_event()によるハッシュチェーン署名(Event Memory)
   |                    既存: mocka_decision_get()によるread-back確認(Decision Memory、本セッション運用実績)
   v
Classification       <- 新規: どのMemory Typeに属するかの判定(本文書§2)
   |
   v
Retention            <- 既存制約: EVENT_DATA_LIFECYCLE_v1.md(§5参照)
   |
   v
Retrieval            <- 既存: mocka_search/mocka_read_event/mocka_decision_get
   |
   v
Reconstruction        <- 既存: Living Context(data/context_snapshots/)、Decision Ledgerのrelated_documents/related_events
   |
   v
Audit                <- 既存: 本セッションで実施したCompliance Review/Historical Integrity Investigationのパターン
```

---

## 5. Retention Policy

**既存仕様との整合が必須。** `docs/mocka3/EVENT_DATA_LIFECYCLE_v1.md`(2026-06-15、Status: Active)が既にEvent Memoryに相当する範囲の保持ポリシーを定義している。

> 「v1では全データを永久保持する。削除ポリシーはEvent Foundation v2以降で検討。」
> 「DELETEは全状態で禁止。MoCKAはデータを消さない。」

本Architectureはこれを継承し、Memory全体に対して以下の扱いを採用する。

- **DELETE禁止**(Event Memory・Decision Memory・Semantic Memory・Procedural Memoryいずれも)
- **永久保持**を原則とする
- 「忘れる」という操作は行わない。かわりに**状態管理による制御**で以下を実現する:
  - 利用対象から外す(Active→Legacy等の状態遷移。`DC_20260729_010`のLegacy Freezeが実例)
  - 参照範囲を制御する(§6 Memory Access Governance)
  - 状態を変化させる(Event Data Lifecycleの`Raw`→`Validated`→`Normalized`等の遷移と同型)
  - Evidenceとして保存する(削除ではなく、Historical Integrity Investigationのように「保存された記録を調査対象とする」)

この方式は、一般的なAI Memoryの「記憶→不要判定→削除」モデルとは異なり、Decision Ledger・Event Ledgerが既に採用している「Active/Superseded/Withdrawn」等の状態遷移思想と一致する。

---

## 6. Memory Access Governance

誰がどのMemoryを見るかを制御する層。

```
User
  |
  v
PHI-OS
  |
  v
Memory Access Control
  |
  v
Evidence Filter
  |
  v
Response
```

**現状(Confirmed)**: Decision Ledgerの`approved_by`フィールド(本セッションで一貫して「きむら博士」)が、Decision Memoryに対するAccess Governanceの萌芽的な実装として既に機能している。Event MemoryについてはMoCKA Governance Runtime(`phi_os/event_gate.py`)がGate機構として書込側のAuthorityを保証しているが、**読み取り側のAccess Control(誰が何を参照できるか)は本文書執筆時点で正式定義されていない。** これは本Architectureが新たに導入する概念であり、次工程(実装検討)の対象とする。

---

## 7. MemoryとMoCKA連携

役割分離を明示する。

| コンポーネント | 役割 |
|---|---|
| Memory | 保存・再構成 |
| MoCKA | 検証・監査(Constitution原則4・5.1、Event Gate、Decision Ledger運用) |
| Orchestra | 利用モデル調整 |
| Relay | 状態同期 |

この分離は、`PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`(DC_20260728_003)が既に確立した「PHI-OS CoreとMoCKA Governance Runtimeは別レイヤー」という整理、および`PHI-OS構想メモ`の役割分担(PHI-OS: シーケンサー / MoCKA: Runtime Governance / Memory: Institutional Memory / Orchestra: 協調制御 / Relay: 状態同期)と一致する。

---

## 8. Future Jarvis Integration(参考、本文書では未着手)

Phase J1として、以下がPHI Memory Architectureに接続される想定である(設計は別途)。

- Personal Context Engine
- Long-term Memory
- Context Reconstruction
- Intent Understanding

---

## 9. 注意事項(本Architectureでは決定しない事項)

以下は別Decision対象として扱い、本文書では確定させない。

- 自動削除機構
- 完全自律Memory更新
- 個人情報保持ルール
- 外部サービス同期仕様

---

## Knowledge Lineage

**Document:** PHI_MEMORY_ARCHITECTURE_v1.0.md
**Status:** DESIGN
**Created:** 2026-07-29
**Origin:** `PHI_MEMORY_ARCHITECTURE_DESIGN_SCOPE_v0.1.md`承認後、きむら博士よりS03としてArchitecture本体作成の指示を受けた。
**Parent Documents:**
- docs/audits/PHI_MEMORY_ARCHITECTURE_DESIGN_SCOPE_v0.1.md
- docs/mocka3/EVENT_DATA_LIFECYCLE_v1.md
- PlanningCaliber/workshop/phi-os/docs/consolidation/PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md
- DC_20260728_003、DC_20260729_010
**Derived From:** PHI_MEMORY_ARCHITECTURE_DESIGN_SCOPE_v0.1
**Supersedes:** なし
**Reason For Creation:** ジャービス化ロードマップPhase J1の中核として、PHI Memory Layerを正式定義するため。
**Affected Components:** Event Ledger、Decision Ledger、Living Context、PHI-OS Core(`ise/`)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Purpose/Memory Layer Model4分類/Existing Asset Mapping/Memory Lifecycle7段階/Retention Policy(既存仕様整合)/Memory Access Governance/MoCKA連携/Future Jarvis Integration/注意事項4件を記載。実装・Decision Ledger登録は無し。
