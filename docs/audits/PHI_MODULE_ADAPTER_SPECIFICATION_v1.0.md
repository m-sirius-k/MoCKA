# PHI Module Adapter Specification v1.0

**Status:** DESIGN(実装接続境界の固定案。実装コード・Decision Ledger登録はまだ行わない)
**位置づけ:** Phase II、**P2-02**。PHI-OSと各Module間の実装接続境界を固定する。
**方針(継続適用)**: 既存State Model(S07)を書き換えない/Gapは勝手に解消しない/新規概念はDecision対象として記録する/実装詳細は本工程の責務範囲(接続境界の定義)内に限定する。

---

## 1. MoCKA Adapter

**責務:**
- Governance判定要求受付
- Evidence Validation結果返却
- Decision Ledger連携

**禁止:**
- Sequence Controller代替(Adapterが独自に次の遷移を決定してはならない)
- Human Gate代替(AdapterがApprove/Reject相当の判断を行ってはならない)

**既存契約との対応**: `PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`§1のMoCKA Interface Contract(Input/Output/Authority Boundary)をそのまま実装接続点として採用する。契約内容自体は変更しない。

---

## 2. Memory Adapter

**責務:**
- Evidence付き記憶保存
- Provenance取得
- Freshness状態返却

**禁止:**
- 自動Verified化(`PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`§3 Memory Freshness Contractの継続適用。時間経過のみでのVerified復帰は禁止)
- Evidence欠落保存(`PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`§4 Forbidden Memory Operations「Provenance欠落Memoryの昇格」禁止と整合)

---

## 3. Orchestra Adapter

**責務:**
- Model Coordination
- Execution候補生成
- Result提供

**禁止:**
- Authority判断(`PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`§3「OrchestraをAuthority Layerにしない」の継続適用)
- State直接変更(Orchestraが`PHI_SEQUENCE_STATE_MODEL_v1.0.md`の状態を直接書き換えることは禁止。状態遷移はSequence Controllerのみが行う)

---

## 4. Relay Adapter

**責務:**
- State同期
- Event搬送
- Module間通信

**禁止:**
- 内容解釈によるDecision生成(`PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`§4「RelayをTrust Layerにしない」の継続適用。搬送する情報の意味解釈・信頼性判断・Decision生成は行わない)

---

## 5. Cross-Adapter原則

- いずれのAdapterも、Sequence Controllerを介さずに他Adapter・他Moduleへ直接指示を出してはならない
- いずれのAdapterも、Human Gateの承認を経ずに`APPROVED`相当の状態へ進めることはできない
- 本仕様は接続**境界**の固定であり、Adapter内部の実装(通信プロトコル・言語・ライブラリ選定等)は対象外とする

---

## 6. 本仕様で決めないこと

- Adapter内部実装
- State Transition Runtime詳細(P2-03で扱う)
- Evidence Runtime Pipeline(P2-04で扱う)
- Gap-001〜003の解消

---

## Knowledge Lineage

**Document:** PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md
**Status:** DESIGN
**Created:** 2026-07-29
**Origin:** `PHI_RUNTIME_BINDING_ARCHITECTURE_v1.0.md`(P2-01)完了後、きむら博士よりPhase II一括実行の第一工程(P2-02)として作成を指示された。
**Parent Documents:** docs/audits/PHI_RUNTIME_BINDING_ARCHITECTURE_v1.0.md、docs/audits/PHI_MODULE_INTERFACE_CONTRACT_v0.1.md
**Derived From:** PHI_MODULE_INTERFACE_CONTRACT_v0.1(既確定契約の実装接続境界への具体化)
**Supersedes:** なし
**Reason For Creation:** PHI-OSと各Module間の実装接続境界を固定するため。
**Affected Components:** MoCKA Adapter、Memory Adapter、Orchestra Adapter、Relay Adapter(いずれも設計段階、未実装)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。4Adapterの責務・禁止事項、Cross-Adapter原則、本仕様で決めないことを記載。実装・Decision Ledger登録は無し。
