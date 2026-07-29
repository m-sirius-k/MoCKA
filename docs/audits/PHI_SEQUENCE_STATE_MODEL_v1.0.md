# PHI Sequence State Model v1.0

**Status:** DESIGN(正式定義案。実装・Decision Ledger登録はまだ行わない)
**位置づけ:** PHI-OS Operational Integration Phase, **I-02**。Sequence Controllerが扱う状態遷移モデルを正式化する。
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 1. Stateとは何か

Stateは「AIの内部状態」ではない。

**Stateとは、PHI-OS全体で観測可能な制度的状態である。** すなわち、Sequence Controller単体が保持する内部変数ではなく、MoCKA(Event Ledger)・Memory・Human Gateのいずれからも参照・検証可能な、記録された状態遷移でなければならない。この定義は`PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`§5(Sequence Controllerは最終判断を行わない)と整合する — Stateが制度的に観測可能である限り、Sequence Controller単独の「思い込み」が状態として扱われることはない。

---

## 2. 推奨State Model

```
OBSERVED
    |
CLASSIFIED
    |
CONTEXT_READY
    |
VERIFICATION_PENDING
    |
VERIFIED
    |
HUMAN_GATE_REQUIRED
    |
APPROVED
    |
EXECUTING
    |
COMPLETED
    |
AUDITED
    |
MEMORIZED
```

| State | 説明 |
|---|---|
| OBSERVED | Observation Eventが記録された直後 |
| CLASSIFIED | イベント種別・対象Moduleが分類された状態 |
| CONTEXT_READY | Memory(Context Reconstruction)からの関連情報取得が完了した状態 |
| VERIFICATION_PENDING | MoCKAへ検証依頼を送出した状態 |
| VERIFIED | MoCKAの検証(Evidence確認・Gate通過判定)が完了した状態 |
| HUMAN_GATE_REQUIRED | Human Gateへの判断要求が発行された状態 |
| APPROVED | Human Decisionが確定し、Decision Ledgerへ登録された状態 |
| EXECUTING | 承認された内容を実行中の状態 |
| COMPLETED | 実行が完了した状態 |
| AUDITED | 実行結果の監査記録が生成された状態 |
| MEMORIZED | Event/Decision Memoryとして正式に記録された状態(終端) |

---

## 3. State Transition Rule

| From | To | 条件 |
|---|---|---|
| OBSERVED | CLASSIFIED | Observation Eventが存在する / Classification処理が完了している |
| CLASSIFIED | CONTEXT_READY | Memoryへの問い合わせが完了し、関連するEvent/Decision/Semantic/Procedural Memoryの取得が完了している |
| CONTEXT_READY | VERIFICATION_PENDING | 取得したContextを添えてMoCKAへ検証依頼が送出されている |
| VERIFICATION_PENDING | VERIFIED | MoCKAの検証が完了している / Evidenceが存在する |
| VERIFIED | HUMAN_GATE_REQUIRED | 検証結果がcritical/govern相当と判定され、Human Gateへのルーティングが必要と判断されている |
| HUMAN_GATE_REQUIRED | APPROVED | Human Decisionが存在する / Decision Ledgerへ登録されている |
| APPROVED | EXECUTING | 承認内容に基づく実行が開始されている |
| EXECUTING | COMPLETED | 実行処理が終了している(成功・失敗いずれの結果も含む) |
| COMPLETED | AUDITED | 実行結果の監査記録(Audit Event)が生成されている |
| AUDITED | MEMORIZED | Event/Decision MemoryへのCHANGE_DONE相当の記録が完了している |

---

## 4. 禁止遷移

以下の遷移は禁止される。いずれも中間段階(Evidence確認・Verification・Human Gate)を経由しない飛び越しであるため。

| 禁止遷移 | 理由 |
|---|---|
| `OBSERVED -> EXECUTING` | Evidence・Verification・Human Gateを経由しないため |
| `CLASSIFIED -> APPROVED` | Verification(MoCKAによるEvidence確認)を経由しないため |
| `VERIFICATION_PENDING -> APPROVED` | VERIFIEDを経由しない(検証完了前の承認は無効) |
| `HUMAN_GATE_REQUIRED -> EXECUTING` | APPROVED(Decision Ledger登録)を経由しないため |
| `APPROVED -> COMPLETED` | EXECUTING(実行そのもの)を経由しないため。「承認された」ことと「実行された」ことは別事象である |
| いずれの状態からの逆行遷移 | 状態は前進のみとする(Event Ledgerのappend-only原則、`PHI_OS_CONSTITUTION_v1.md`原則1と整合) |

---

## 5. Error / Unknown State

**UNKNOWNは消さない。** 他の11状態のいずれかに分類できない場合、状態を無理に確定させず`UNKNOWN`として保持する。

```
UNKNOWN
    |
    Evidence不足
    |
    Investigation
```

`UNKNOWN`から抜け出す条件は「新たなEvidenceの取得」のみであり、時間経過や推測による自動遷移は認めない。

**既存原則との接続(重要)**: この扱いは`DC_20260729_009`(Authority Flow、Option D「条件付きPending Resolution」)の思想と直接接続する。すなわち、「証拠が不足している状態を正しく保存する」ことは、Sequence ControllerのState Modelにおいても`UNKNOWN`という正規の状態として制度化される。`UNKNOWN`は失敗でも欠陥でもなく、Evidence-Bound Governanceが要求する誠実な状態表現である。

`UNKNOWN`は§2の11状態のいずれからも遷移し得る(Classification失敗・Context取得失敗・Verification不能等)。`UNKNOWN`からは、Evidence取得後に該当する適切な状態(多くの場合`OBSERVED`または`CLASSIFIED`)へ再遷移する。

---

## 6. Memory接続

```
COMPLETED
    |
    v
  AUDITED
    |
    v
 MEMORIZED
```

- `COMPLETED`到達時、実行結果は一旦Sequence Controller内(揮発的)に保持される
- `AUDITED`遷移時、Audit Event(監査記録)がEvent Ledgerへ書き込まれる(`phi_os/event_gate.py`経由)
- `MEMORIZED`遷移時、`PHI_MEMORY_ARCHITECTURE_v1.0.md`§2のMemory分類(Event Memory/Decision Memory)に従って正式に記録される。これをもって状態遷移は終端に達する

`HUMAN_GATE_REQUIRED -> APPROVED`の遷移自体も、Decision Ledgerへの書込(Decision Memory相当)を条件とするため、この意味で`APPROVED`は部分的にMemory接続を伴う早期の記録点である。

---

## 7. 今回決めないこと

- 自律Agent権限
- 並列Agent協調アルゴリズム
- 音声UI状態
- 外部操作状態

---

## Knowledge Lineage

**Document:** PHI_SEQUENCE_STATE_MODEL_v1.0.md
**Status:** DESIGN
**Created:** 2026-07-29
**Origin:** `PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`完了後、きむら博士よりPhase I-02(S07)として作成を指示された。
**Parent Documents:**
- docs/audits/PHI_MODULE_INTERFACE_CONTRACT_v0.1.md
- docs/audits/PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md
- docs/audits/PHI_MEMORY_ARCHITECTURE_v1.0.md
- DC_20260729_009
**Derived From:** PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0(State Transition Engineの精緻化)
**Supersedes:** なし
**Reason For Creation:** Sequence Controllerが扱う状態を、増やす前に固定するため。特にUNKNOWN状態を「消えるもの」ではなく正規状態として制度化するため。
**Affected Components:** Sequence Controller(`phios/core/*`)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。State定義(制度的観測可能性)、11状態モデル、State Transition Rule10件、禁止遷移6件、UNKNOWN State(DC_20260729_009接続)、Memory接続、今回決めないこと4件を記載。実装・Decision Ledger登録は無し。
