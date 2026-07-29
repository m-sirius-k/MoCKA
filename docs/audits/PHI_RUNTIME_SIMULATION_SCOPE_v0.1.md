# PHI Runtime Simulation Scope v0.1

**Status:** SCOPE + PAPER SIMULATION(Phase I統合検証文書)
**位置づけ:** Phase Iの最終工程(S10)。「PHI-OSの設計思想が、実際の状態遷移として破綻しないこと」を確認する。
**実装・Decision Ledger登録:** 本文書には一切含まない。

**重要な前提**: Sequence Controller/Memory Access Control/Human Gate Integrationは、S01〜S09のいずれも**設計文書**であり、実行可能なコードとしては実装されていない。したがって本文書のSimulationは、実行環境上のテストではなく、既存の確定ルール(S06〜S09)に対する**机上トレース(paper simulation)**である。真の意味でのRuntime検証は、実装が存在するPhase II以降に持ち越される。

---

## 0. 用語整合の確認

ご提示の正常系(`OBSERVED→RECORDED→CLASSIFIED→EVALUATED→VERIFIED→...`)は、`PHI_SEQUENCE_STATE_MODEL_v1.0.md`(S07、既に確定済み・変更対象外)の11状態(`OBSERVED→CLASSIFIED→CONTEXT_READY→VERIFICATION_PENDING→VERIFIED→...`)とは異なる中間状態名(`RECORDED`/`EVALUATED`)を含んでいる。S07を変更せず単一の状態モデルとして維持するため、本文書ではS07の既存状態名をそのまま使用する。

| 提示された概念 | S07既存状態との対応 |
|---|---|
| RECORDED | `OBSERVED`(Event Ledgerへの記録を伴う観測) |
| EVALUATED | `CLASSIFIED`〜`CONTEXT_READY`〜`VERIFICATION_PENDING`の範囲 |

---

## 1. Simulation対象(正常系)

**SIM-001: 正常系フルパス**

```
OBSERVED -> CLASSIFIED -> CONTEXT_READY -> VERIFICATION_PENDING
   -> VERIFIED -> HUMAN_GATE_REQUIRED -> APPROVED -> EXECUTING
   -> COMPLETED -> AUDITED -> MEMORIZED
```

| 段階 | 確認対象 | 判定基準 |
|---|---|---|
| State transition | S07§3のState Transition Rule10件すべてを順に満たすこと | S07既確定 |
| Evidence requirement | 各遷移の条件(Observation Event存在/Classification完了/MoCKA検証完了等)を満たすこと | S07§3 |
| Memory permission | S08§0のState→Memory Permission Mappingに従いRead/Writeが許可されること(`APPROVED`以前はRead限定、`APPROVED`以降でWrite許可) | S08既確定 |
| Human Gate invocation | `HUMAN_GATE_REQUIRED`到達時にHuman Gateへの提示が発行されること(S09§1・§2) | S09既確定 |
| Audit trail生成 | `AUDITED`遷移時にAudit Eventが`phi_os/event_gate.py`経由でEvent Ledgerへ記録されること(S07§6) | S07既確定 |

**Simulation Evidence(§6形式による記録例)**:

| 項目 | 内容 |
|---|---|
| Simulation ID | SIM-001 |
| Initial State | (Pre-OBSERVED) |
| Input Evidence | 仮のObservation Event |
| Expected Transition | 上記フルパス(11状態) |
| Actual Transition | (机上トレースにつき期待通りと仮定) |
| Decision | Human Gate: Approve(仮定) |
| Audit Reference | (仮のevent_id、実装後に実値を記録) |
| Final State | MEMORIZED |

---

## 2. UNKNOWN経路Simulation

**SIM-002: UNKNOWN経路**

```
CLASSIFIED -> (Context取得失敗) -> UNKNOWN -> (新Evidence取得) -> CONTEXT_READY
```

**確認事項(いずれもConfirmed済みルールとの整合確認)**:
- UNKNOWNからの推測による脱出は禁止(S07§5「時間経過や推測による自動遷移は認めない」)
- EvidenceなしのAPPROVEDは禁止(S09§4「Human GateなしのAPPROVED遷移禁止」および「Decision理由なしの承認禁止」)
- 時間経過だけではVerified化しない(S08§3 Memory Freshness Contract「自動的にVerified扱いへ戻さない」)

| 項目 | 内容 |
|---|---|
| Simulation ID | SIM-002 |
| Initial State | CLASSIFIED |
| Input Evidence | Context取得失敗(不十分な情報) |
| Expected Transition | CLASSIFIED -> UNKNOWN -> (新Evidence) -> CONTEXT_READY |
| Actual Transition | (机上トレースにつき期待通りと仮定) |
| Decision | N/A(Human Gate未到達) |
| Audit Reference | UNKNOWN遷移自体の記録(要Event Ledger化) |
| Final State | CONTEXT_READY(復帰) |

---

## 3. 禁止遷移Simulation

S07§4が定める6件の禁止遷移すべてを検証対象とする。

| 禁止遷移 | 期待結果 |
|---|---|
| `OBSERVED -> EXECUTING` | REJECTED + 理由「Evidence・Verification・Human Gate未経由」+ Audit Event生成 |
| `CLASSIFIED -> APPROVED` | REJECTED + 理由「Verification未経由」+ Audit Event生成 |
| `VERIFICATION_PENDING -> APPROVED` | REJECTED + 理由「VERIFIED未経由」+ Audit Event生成 |
| `HUMAN_GATE_REQUIRED -> EXECUTING` | REJECTED + 理由「APPROVED未経由」+ Audit Event生成 |
| `APPROVED -> COMPLETED` | REJECTED + 理由「EXECUTING未経由」+ Audit Event生成 |
| 任意状態からの逆行遷移(例: `MEMORIZED -> EXECUTING`) | REJECTED + 理由「Event Ledger append-only原則違反」+ Audit Event生成 |

**共通の期待結果**: `REJECTED` + 理由記録 + Audit Event生成。いずれの禁止遷移も、単に無視されるのではなく、**拒否されたこと自体が記録される**必要がある(沈黙の禁止、`PHI_OS_CONSTITUTION_v1.md`第1章1.2「沈黙の禁止」原則と整合)。

---

## 4. Human Gate Simulation

入力: `VERIFIED` Evidence Package → Human Gate

### Case A: Approve

```
VERIFIED -> HUMAN_GATE_REQUIRED -> APPROVED -> EXECUTING
```

S07・S09が既に確定済みの経路と一致する。本セッションの`DC_20260729_008`〜`010`が、この人間主導版の既存実例である。

### Case B: Reject

```
VERIFIED -> HUMAN_GATE_REQUIRED -> REJECTED
```

**重要な発見(Gap)**: S07が定める既存11状態には、`REJECTED`という状態が定義されていない。本Simulation Scopeの作成過程で、Human GateがRejectする場合の受け皿状態がS07に存在しないことが判明した。これは新たに発見されたGapであり、本文書では追加を提案せず、**Unknown/要確認事項**として記録するに留める(S07への状態追加が必要かどうかはHuman Gate判断対象、§8参照)。

### Case C: Request More Evidence

```
VERIFIED -> HUMAN_GATE_REQUIRED -> UNKNOWN
```

これはS07の既存`UNKNOWN`状態(§2参照)を用いて表現可能であり、Case Bのような新規状態は不要である。Human Gateが「Evidence不足」と判断した場合、`HUMAN_GATE_REQUIRED`から`UNKNOWN`へ遷移し、新規Evidence取得を待つ。

---

## 5. Memory Integration Simulation(S08との接続確認)

| 検証項目 | 期待結果 | 根拠 |
|---|---|---|
| APPROVED以前のWrite拒否 | `OBSERVED`〜`VERIFICATION_PENDING`の間のMemory Write要求はREJECTED | S08§0 State→Memory Permission Mapping |
| ProvenanceなしMemory拒否 | `event_id`/`decision_id`等の出典を持たないMemoryの昇格・利用はREJECTED | S08§4 Forbidden Memory Operations |
| Freshness失効MemoryはUNKNOWN化 | 時間経過したMemoryは自動的にVerified扱いへ戻らず、再利用時はUNKNOWN扱いとして再検証を要求 | S08§3 Memory Freshness Contract |
| Delete不可 | いかなるActor・いかなる状態からのDelete要求もREJECTED | S08§2 Access Control Matrix(全Actor×)、`EVENT_DATA_LIFECYCLE_v1.md` |

---

## 6. Simulation Evidence形式(テンプレート定義)

以降のSimulation記録は、以下の8項目形式で残す。

```
Simulation ID
Initial State
Input Evidence
Expected Transition
Actual Transition
Decision
Audit Reference
Final State
```

本文書内のSIM-001/SIM-002は、この形式に基づく机上トレース例である。実装後は、`Actual Transition`欄に実際のRuntime挙動を記録し、`Expected`との差異を検出する。

---

## 7. Phase I完了条件チェック

| 条件 | 状態 |
|---|---|
| Sequence exists | 満たす(`PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md`、`PHI_SEQUENCE_STATE_MODEL_v1.0.md`) |
| Modules connect | 満たす(`PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`) |
| Memory protected | 満たす(`PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`) |
| Human authority integrated | 満たす(`PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md`) |
| Runtime behavior verified | **部分的に満たす**。本文書の机上トレースにより設計の内部整合性は確認したが、実装が存在しない段階のため、真の意味でのRuntime検証はPhase II(実装Binding後)に持ち越される |

---

## 8. 発見されたGap一覧(Unknown、本文書では解消しない)

1. **REJECTED状態の欠落**(§4 Case B): S07にHuman Gate拒否時の受け皿状態が未定義
2. **Decision Ledgerスキーマの2フィールド欠落**(S09§3で既報告、継続): `Previous State`/`Requested Transition`の専用フィールドなし
3. **Freshness閾値の数値未確定**(S08§3で既報告、継続): 再検証を要求する具体的な経過時間が未定義

---

## 9. 本Scopeで決めないこと

- 上記Gap(§8)の解消方法・要否の最終判断(Human Gate対象)
- Phase II(実装Binding、Runtime Controller、Module実接続、Production Validation)の詳細設計
- 実際のコード実装

---

## Knowledge Lineage

**Document:** PHI_RUNTIME_SIMULATION_SCOPE_v0.1.md
**Status:** SCOPE + PAPER SIMULATION
**Created:** 2026-07-29
**Origin:** `PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md`完了後、きむら博士よりPhase I最終工程(S10)として作成を指示された。
**Parent Documents:**
- docs/audits/PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md
- docs/audits/PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md
- docs/audits/PHI_SEQUENCE_STATE_MODEL_v1.0.md
- docs/audits/PHI_MODULE_INTERFACE_CONTRACT_v0.1.md
**Derived From:** S06〜S09全文書
**Supersedes:** なし
**Reason For Creation:** Phase I(S06〜S09)の統合検証を行い、設計思想が状態遷移として破綻しないことを机上で確認し、Phase I完了条件を評価するため。
**Affected Components:** Sequence Controller、Memory、MoCKA、Human Gate(いずれも設計段階、未実装)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。用語整合確認、正常系Simulation(SIM-001)、UNKNOWN経路Simulation(SIM-002)、禁止遷移6件、Human Gate3ケース(REJECTED状態欠落Gapを発見)、Memory Integration検証、Simulation Evidence形式、Phase I完了条件チェック、発見されたGap一覧3件を記載。実装・Decision Ledger登録は無し。
