# PHI Module Runtime Binding v1.0

**Status:** DESIGN(接続設計案。実装コードはまだ行わない)
**位置づけ:** Phase III、**P3-04**。`PHI_CONTROLLER_PROTOTYPE_DESIGN_v1.0.md`(P3-03)と4 Module Adapter境界(`PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md`、P2-02)を接続する。
**変更禁止事項(継続)**: S07・S08・S09・Gap-001〜003は変更しない。

---

## 1. MoCKA Runtime Binding

- Controllerは`VERIFICATION_PENDING`状態到達時にMoCKA Adapterへ検証依頼を送出する
- MoCKA Adapterは`Governance判定要求受付`(P2-02§1)のみを行い、検証結果を`VERIFIED`遷移のTriggerとしてControllerへ返却する
- MoCKA Adapter自身は`VERIFIED`への遷移を実行しない(遷移実行権はController側にある)

## 2. Memory Runtime Binding

- Controllerは`CLASSIFIED`状態到達時にMemory Adapterへ Context取得要求を送出する
- Memory Adapterは`Evidence付き記憶保存`・`Provenance取得`・`Freshness状態返却`(P2-02§2)のみを行う
- Freshness状態が「Validity Unknown」と返却された場合、Controllerはこれを`UNKNOWN`遷移のTriggerとして扱う(Gap-003の閾値自体は本文書でも未確定のまま)

## 3. Orchestra Runtime Binding

- Controllerは`APPROVED`状態到達後、`EXECUTING`遷移時にOrchestra Adapterへモデル選択・実行候補生成を要求する
- Orchestra Adapterは`Model Coordination`・`Execution候補生成`・`Result提供`(P2-02§3)のみを行い、`EXECUTING -> COMPLETED`の遷移実行権はController側にある

## 4. Relay Runtime Binding

- Controllerは外部状態同期が必要な場合にRelay Adapterへ要求する(State同期・Event搬送・Module間通信、P2-02§4)
- Relay Adapterが搬送する情報の信頼性判断はMoCKA Adapter側に委ねられ、Relay Adapter自身は判断しない(既確定の継続)

---

## 5. Module間責務境界(確認)

| 確認事項 | 状態 |
|---|---|
| ControllerがAuthorityを保持する | 確認済み。いずれのAdapterも遷移実行権・最終判断権を持たない |
| Moduleは担当領域のみ実行する | 確認済み。§1〜4の各Bindingは、P2-02で定義された責務範囲を超えない |
| ModuleによるState直接変更は禁止 | 確認済み。State(S07準拠)の書き換えはController経由でのみ発生し、Adapterが直接`event_gate.py`等を介してStateを変更することはない |

---

## 6. 含めない範囲

- 実装コード
- 本番接続
- Infrastructure
- Performance測定

---

## Knowledge Lineage

**Document:** PHI_MODULE_RUNTIME_BINDING_v1.0.md
**Status:** DESIGN
**Created:** 2026-07-29
**Origin:** `PHI_CONTROLLER_PROTOTYPE_DESIGN_v1.0.md`(P3-03)完了後、Phase III連続実行(P3-04〜P3-06)の第一工程として作成された。
**Parent Documents:** docs/audits/PHI_CONTROLLER_PROTOTYPE_DESIGN_v1.0.md、docs/audits/PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md
**Derived From:** PHI_MODULE_ADAPTER_SPECIFICATION_v1.0(4 Adapter責務の接続)
**Supersedes:** なし
**Reason For Creation:** Controller Prototype DesignとModule Adapter境界を実際のRuntime接続として具体化するため。
**Affected Components:** MoCKA Adapter、Memory Adapter、Orchestra Adapter、Relay Adapter、PHI-OS Controller
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。4 Module Runtime Binding、Module間責務境界確認3件、含めない範囲4件を記載。実装・Decision Ledger登録は無し。
