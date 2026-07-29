# PHI State Transition Runtime Design v1.0

**Status:** DESIGN(Runtime接続設計案。実装コード・Decision Ledger登録はまだ行わない)
**位置づけ:** Phase II、**P2-03**。`PHI_SEQUENCE_STATE_MODEL_v1.0.md`(S07、変更対象外)をRuntime Controllerへ接続する。
**方針(継続適用)**: S07を書き換えない/Gapは勝手に解消しない/新規概念はDecision対象として記録する。

---

## 1. State Event

S07の11状態それぞれについて、状態への到達がRuntime上で「Event」として観測可能でなければならない。

- 各State遷移は、Event Ledger(`phi_os/event_gate.py`)への書込を伴う、または伴う設計を前提とする
- State Event自体は`PHI_SEQUENCE_STATE_MODEL_v1.0.md`§1「Stateとは制度的に観測可能な状態」の要件を満たす形で実装される

---

## 2. Transition Trigger

各遷移(S07§3 State Transition Rule、10件)を発火させる契機を定義する。

| 遷移 | Trigger |
|---|---|
| `OBSERVED -> CLASSIFIED` | Observation Event記録完了 + Classification処理完了 |
| `CLASSIFIED -> CONTEXT_READY` | Memory Adapter(P2-02)からのContext取得完了 |
| `CONTEXT_READY -> VERIFICATION_PENDING` | MoCKA Adapterへの検証依頼送出 |
| `VERIFICATION_PENDING -> VERIFIED` | MoCKA Adapterからの検証完了応答 |
| `VERIFIED -> HUMAN_GATE_REQUIRED` | critical/govern相当と判定 |
| `HUMAN_GATE_REQUIRED -> APPROVED` | Human Decision確定 + Decision Ledger登録 |
| `APPROVED -> EXECUTING` | 実行開始 |
| `EXECUTING -> COMPLETED` | 実行処理終了 |
| `COMPLETED -> AUDITED` | Audit Event生成 |
| `AUDITED -> MEMORIZED` | Memory Adapterへの正式記録完了 |

---

## 3. Transition Validation

各Triggerが成立したとみなす前に、Runtime Controllerが確認すべき検証項目。

- 遷移元Stateが直前の正規Stateであること(S07の遷移順序と一致)
- 当該遷移がS07§4の禁止遷移一覧に該当しないこと
- Evidence Requirement(`PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`各契約)が満たされていること

---

## 4. Forbidden Transition Handling

S07§4の禁止遷移6件が発生した場合の扱い(`PHI_RUNTIME_SIMULATION_SCOPE_v0.1.md`§3で定義済みの期待結果を、Runtime接続設計として再確認する)。

```
禁止遷移検知
      |
      v
   REJECT
      |
      v
理由記録(Event Ledger)
      |
      v
Audit Event生成
```

サイレントな無視は許されない。禁止遷移の試行自体が、Event Ledgerへ記録される対象である。

---

## 5. UNKNOWN Handling

S07§5(UNKNOWNは消さない)をRuntime接続として具体化する。

- いずれの状態からも、Classification/Context取得/Verificationが失敗した場合`UNKNOWN`へ遷移可能とする
- `UNKNOWN`からの脱出は、新規Evidence取得のトリガーによってのみ発生する。タイマー等の時間経過のみによる自動遷移は実装しない
- `UNKNOWN`状態もState Eventとして記録される(§1の要件と一致)

---

## 6. Gap-001の扱い(解決しない)

`PHI_RUNTIME_SIMULATION_SCOPE_v0.1.md`§4 Case Bで発見されたGap(Human Gate Reject時の受け皿状態がS07に存在しない)について、本設計では以下の扱いに留める。

```
Observed Gap
      |
      v
Runtime Behavior Requirement
      |
      v
Decision Pending
```

**明記**: 本文書はS07に`REJECTED`状態を新設しない。Human GateがRejectを選択した場合のRuntime挙動(`UNKNOWN`へ戻す、または将来のDecision Ledger属性で表現する等)は、Gap-001がHuman Decisionによって解消されるまで**未定義のまま**とする。この未定義状態自体を隠さず、Runtime設計上の既知の制約として記録する。

---

## 7. 本設計で決めないこと

- State EventのRuntime実装形式(メッセージキュー・DB Trigger等の技術選定)
- Gap-001の最終解消方法
- Evidence Runtime Pipeline詳細(P2-04で扱う)

---

## Knowledge Lineage

**Document:** PHI_STATE_TRANSITION_RUNTIME_DESIGN_v1.0.md
**Status:** DESIGN
**Created:** 2026-07-29
**Origin:** `PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md`(P2-02)完了後、Phase II一括実行の第二工程(P2-03)として作成された。
**Parent Documents:** docs/audits/PHI_SEQUENCE_STATE_MODEL_v1.0.md、docs/audits/PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md、docs/audits/PHI_RUNTIME_SIMULATION_SCOPE_v0.1.md
**Derived From:** PHI_SEQUENCE_STATE_MODEL_v1.0(S07を変更せず接続のみ設計)
**Supersedes:** なし
**Reason For Creation:** S07 State ModelをRuntime Controllerへ接続するための設計を固定するため。
**Affected Components:** Sequence Controller Runtime
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。State Event/Transition Trigger10件/Transition Validation/Forbidden Transition Handling/UNKNOWN Handling/Gap-001の扱い(未解決のまま保持)を記載。実装・Decision Ledger登録は無し。
