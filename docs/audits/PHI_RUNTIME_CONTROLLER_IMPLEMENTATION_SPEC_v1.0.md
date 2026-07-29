# PHI Runtime Controller Implementation Spec v1.0

**Status:** IMPLEMENTATION SPEC(実装仕様。詳細コードは含まない)
**位置づけ:** Phase IV、**IV-02**。Controller実装仕様を定義する。
**制約**: S07 State Model変更禁止。Gap-001〜003は実装都合で解消しない。

---

## 1. State管理

- Controllerは現在Stateを保持する唯一の主体とする(S07の11状態+`UNKNOWN`)
- State変更は`PHI_STATE_TRANSITION_RUNTIME_DESIGN_v1.0.md`(P2-03)§3 Transition Validationを満たした場合にのみ許可される
- Controller以外のComponent(Adapter)による直接のState書き換えは実装しない(`PHI_MODULE_RUNTIME_BINDING_v1.0.md`§5継続)

## 2. Event生成

- 各State遷移時、`PHI_RUNTIME_EVENT_SCHEMA_v1.0.md`(P3-02)§1のEvent Object(9フィールド)を生成する
- Event生成はState変更と同一トランザクション内で行う(Stateが変わったがEventが記録されない、という不整合を許さない)

## 3. Transition制御

- Controllerは`PHI_STATE_TRANSITION_RUNTIME_DESIGN_v1.0.md`§2の10 Transition Triggerを実装する
- 禁止遷移(S07§4、6件)の試行は、Stateを変更せず`REJECT`+理由記録+Audit Event生成に留める(§3の禁止遷移Handling、P2-03§4継続)
- `UNKNOWN`への遷移・`UNKNOWN`からの復帰は、新規Evidence取得というTriggerのみで発生させる。時間経過・推測による自動遷移は実装しない

## 4. Permission確認

- Memory操作の可否は`PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`(S08)§0のState→Memory Permission Mappingに従って判定する
- `APPROVED`到達前のMemory Write要求は、Controller側で拒否する(Adapter側の実装に委ねない)

## 5. Human Gate接続

- `VERIFIED`到達時、critical/govern相当と判定された場合のみHuman Gate Interfaceへ`HUMAN_GATE_REQUIRED`遷移を発行する
- Human Gate InterfaceからのApprove応答 → `APPROVED`遷移
- Human Gate InterfaceからのRequest More Evidence応答 → `UNKNOWN`遷移
- **Reject応答への対応は本仕様に含めない**(Gap-001)。Controllerは、Human Gate InterfaceがReject相当の応答を返すケースを実装対象としない。もし実装中にこのケースへの対応が避けられないと判明した場合、その時点でDecision対象として記録し、本仕様を先に書き換えない

---

## 6. 実装対象外(継続)

- 最終判断・Authority変更・Evidenceなし実行(`PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md`§5)
- Reject経路(Gap-001)
- S07への新規State追加

---

## Knowledge Lineage

**Document:** PHI_RUNTIME_CONTROLLER_IMPLEMENTATION_SPEC_v1.0.md
**Status:** IMPLEMENTATION SPEC
**Created:** 2026-07-29
**Origin:** `PHI_RUNTIME_IMPLEMENTATION_PLAN_v1.0.md`(IV-01)完了後、Phase IV一括進行の第二工程(IV-02)として作成された。
**Parent Documents:** docs/audits/PHI_RUNTIME_IMPLEMENTATION_PLAN_v1.0.md、docs/audits/PHI_CONTROLLER_PROTOTYPE_DESIGN_v1.0.md、docs/audits/PHI_STATE_TRANSITION_RUNTIME_DESIGN_v1.0.md
**Derived From:** PHI_CONTROLLER_PROTOTYPE_DESIGN_v1.0(P3-03の実装仕様化)
**Supersedes:** なし
**Reason For Creation:** Controller実装の具体的仕様(State管理・Event生成・Transition制御・Permission確認・Human Gate接続)を固定するため。
**Affected Components:** PHI-OS Controller
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。State管理・Event生成・Transition制御・Permission確認・Human Gate接続(Reject経路除外を明記)、実装対象外3件を記載。詳細コード・Gap解消は無し。
