# PHI Controller Prototype Design v1.0

**Status:** PROTOTYPE DESIGN(責務・制御境界の定義。実装コードは含まない)
**位置づけ:** Phase III、**P3-03**。PHI-OS Runtime Controllerの責務と制御境界を定義する。プロトタイプ「設計」のみであり、実装は対象外。
**変更禁止事項(継続)**: S07 State Model・S08 Memory Permission・S09 Human Gate Authority・Gap-001〜003のPending状態はいずれも変更しない。

---

## 1. Controller責務

PHI-OS Runtime Controllerが担当するもの。

- State Transition制御
- Event生成(`PHI_RUNTIME_EVENT_SCHEMA_v1.0.md`§1のEvent Objectを生成する主体)
- Module呼び出し制御
- Permission確認(`PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`§0のState→Memory Permission Mappingの適用)
- Human Gate接続判断(`VERIFIED -> HUMAN_GATE_REQUIRED`の判定、S09準拠)

**担当しないもの(既確定の再確認)**: 最終判断・Authority変更・Evidenceなし実行(`PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md`§5)。本文書はこの境界を変更しない。

---

## 2. ControllerとModuleの境界

```
PHI-OS Controller
        |
        +-- MoCKA Adapter
        +-- Memory Adapter
        +-- Orchestra Adapter
        +-- Relay Adapter
```

| 項目 | 定義 |
|---|---|
| 呼び出し方向 | ControllerからAdapterへの一方向。AdapterからControllerへは応答(結果返却)のみで、Adapter間の直接呼び出しは行わない(`PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md`§5 Cross-Adapter原則の継続適用) |
| 入出力境界 | 各Adapterの`PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md`(P2-02)で定義済みの責務・禁止事項をそのまま採用。本文書では変更しない |
| Authority境界 | ControllerはいずれのAdapterのAuthorityも代行しない。MoCKA Adapterの検証結果・Human Gateの承認結果を、Controllerが上書き・無視することは禁止される |

---

## 3. State制御

S07(`PHI_SEQUENCE_STATE_MODEL_v1.0.md`)を参照する。

**含める:**
- Transition要求受付(`PHI_STATE_TRANSITION_RUNTIME_DESIGN_v1.0.md`§2 Transition Triggerの受付)
- Transition条件確認(同§3 Transition Validationの適用)
- Event記録(`PHI_RUNTIME_EVENT_SCHEMA_v1.0.md`§2 State Transition Eventとしての記録)

**含めない:**
- 新規State追加(S07の11状態+`UNKNOWN`のまま)
- Gap-001解消(REJECTED状態の要否判断は本文書では行わない)

---

## 4. Human Gate接続

S09(`PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md`)準拠。

| 項目 | 内容 |
|---|---|
| Gate要求発行条件 | `VERIFIED`状態到達 + critical/govern相当と判定された場合(S09§2) |
| Decision結果受領 | Approve → `APPROVED`、Request More Evidence → `UNKNOWN` |
| Event記録 | `PHI_RUNTIME_EVENT_SCHEMA_v1.0.md`§4 Human Decision Eventとして記録(Authority reference・Decision rationaleを含む) |

**Reject経路の扱い:**

```
Gap-001 Pending
```

Human GateがRejectを選択した場合のController側の挙動は、Gap-001が解消されるまで定義しない。本文書はこの未定義を新たに埋めることをせず、既存のPending状態をそのまま引き継ぐ。

---

## 5. 含めない範囲(本文書全体)

- 実装コード
- API設計
- DB実装
- UI
- Performance
- Deployment

---

## Knowledge Lineage

**Document:** PHI_CONTROLLER_PROTOTYPE_DESIGN_v1.0.md
**Status:** PROTOTYPE DESIGN
**Created:** 2026-07-29
**Origin:** `PHI_RUNTIME_EVENT_SCHEMA_v1.0.md`(P3-02)完了後、きむら博士よりPhase III第三工程(P3-03)として作成を指示された。
**Parent Documents:** docs/audits/PHI_RUNTIME_EVENT_SCHEMA_v1.0.md、docs/audits/PHI_STATE_TRANSITION_RUNTIME_DESIGN_v1.0.md、docs/audits/PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md、docs/audits/PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md
**Derived From:** PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0(Controller責務の継承元)
**Supersedes:** なし
**Reason For Creation:** PHI-OS Runtime Controllerの責務と制御境界を、実装着手前に固定するため。
**Affected Components:** PHI-OS Controller
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Controller責務5項目、ControllerとModuleの境界(呼び出し方向・入出力境界・Authority境界)、State制御(含める/含めない)、Human Gate接続(Reject経路はGap-001 Pendingのまま)、含めない範囲6件を記載。実装・Decision Ledger登録は無し。
