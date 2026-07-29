# PHI Runtime Binding Architecture v1.0

**Status:** DESIGN(境界設計案。実装コード・Decision Ledger登録はまだ行わない)
**位置づけ:** Phase II(Implementation Binding)、**P2-01**。Phase I(S05〜S10)で定義した制度モデルを、実際のModule Runtimeへどう結合するかの境界を定義する。
**実装:** 本文書には一切含まない。「結合の設計」のみを扱い、実際のコード実装はP2-02以降の対象とする。
**Gap-001〜003の扱い**: 本文書はGap-001(REJECTED状態欠落)・Gap-002(Decision Ledgerスキーマ2フィールド欠落)・Gap-003(Freshness閾値未確定)のいずれも解決しない。Pending Resolutionのまま引き継ぐ。

---

## 1. Runtime Controller責務

PHI-OS Sequence Controllerが担当するもの(Phase Iで既に確定した権限境界の再確認、`PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md`§1・§5と同一):

- State Transition管理
- Permission判定(`PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`§0のState→Memory Permission Mappingの適用)
- Module呼び出し順序管理
- Evidence要求
- Human Gate呼び出し条件(`PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md`§2の`VERIFIED -> HUMAN_GATE_REQUIRED`条件)

**本文書が追加するもの**: 上記責務そのものではなく、これらの責務を**どのModuleとどう結線するか**という境界のみ(§2以降)。

---

## 2. Module Binding

```
PHI-OS
 |
 +-- MoCKA
 |     Runtime Governance
 |
 +-- Memory
 |     Institutional Memory
 |
 +-- Orchestra
 |     Multi-model Coordination
 |
 +-- Relay
       State Synchronization
```

各Moduleについて、`PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`(既確定)を実行環境への結合契約として再掲・具体化する。

| Module | Input Contract | Output Contract | Authority Boundary | Failure Handling |
|---|---|---|---|---|
| MoCKA | Event候補・Decision候補(Sequence Controllerから) | Verification結果・Gate判定・Audit記録 | Event/Knowledge/Gate/Version/Verification/Institution Authority(既確定、変更なし) | 検証失敗時は却下+理由返却。サイレント失敗禁止(既確定) |
| Memory | Event/Decision/Semantic/Procedural Memoryの書込要求 | Context Reconstruction結果・Retrieval結果 | 保存・再構成のみ、判断は行わない(既確定) | 未署名・破損データは削除せず異常記録として保持(既確定) |
| Orchestra | Model Selection要求 | 選択モデル/能力の実行結果 | モデル選択調整のみ、Authority判断は行わない(既確定) | 選択失敗時はSequence Controllerへエラー返却、勝手な代替実行禁止(既確定) |
| Relay | 外部システムの状態変化通知 | 状態同期結果 | 状態同期のみ、信頼性判断は行わない(既確定) | 同期失敗時は静かに失敗せずSequence Controllerへ通知(既確定) |

**本文書での変更点**: なし。`PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`が定義した契約を、Phase IIのRuntime結合設計の土台としてそのまま採用する。契約内容自体の見直しはPhase IIでは行わない。

---

## 3. State Runtime Mapping

S07(`PHI_SEQUENCE_STATE_MODEL_v1.0.md`)の状態を、Runtime上のイベント発生点へ対応づける。

```
Event Received
      |
      v
   OBSERVED            <- Event Ledgerへの記録(Confirmed: phi_os/event_gate.pyのprocess_event()相当)
      |
      v
Classification処理
      |
      v
   CLASSIFIED
      |
      v
Memory問い合わせ
      |
      v
 CONTEXT_READY
      |
      v
MoCKA検証依頼
      |
      v
VERIFICATION_PENDING
      |
      v
MoCKA検証完了
      |
      v
   VERIFIED
```

**用語整合の再確認(継続)**: 提示された対応例では`OBSERVED`の直後に「Evidence Collection」を経て「RECORDED」という中間状態が置かれていたが、`PHI_SEQUENCE_STATE_MODEL_v1.0.md`(S07、変更対象外)には`RECORDED`という状態は存在しない。本文書では`OBSERVED`自体をEvent Ledgerへの記録行為(`process_event()`相当)と同一視し、S07の11状態モデルを唯一の状態一覧として維持する。以降(`VERIFIED`〜`MEMORIZED`)も同様にS07をそのまま参照する。

---

## 4. Gap Handling Protocol

Phase IIでは、Phase Iで発見されたGapを勝手に修正しない。

```
Detected Gap
      |
      v
   Record
      |
      v
Impact Analysis
      |
      v
Human Decision
      |
      v
 Apply / Reject
```

**Gap-001〜003への適用**:

| Gap | 現状 | Phase IIでの扱い |
|---|---|---|
| Gap-001: REJECTED状態不足 | Pending Resolution | 新規State追加を先行実施しない。RejectをUNKNOWN、または将来のHuman Decision Ledger側の属性(例: `decision=Reject`)で表現するかは、Runtime設計の詳細検討時(P2-03 State Transition Runtime Design)で扱う候補として記録するに留める |
| Gap-002: Decision Ledgerフィールド不足 | Pending Resolution | `Previous State`/`Requested Transition`のSchema Extension候補として、P2-04(Evidence Runtime Pipeline)評価時に扱う |
| Gap-003: Freshness Threshold未確定 | Pending Resolution | Memory Runtime Policy Decisionへ移管。本文書では固定値を定めない |

いずれのGapも、本文書によって解消・確定させることはしない。

---

## 5. 本文書で決めないこと

- Runtime Controllerの実装言語・技術スタック
- Module Adapter実装(P2-02)
- State Transition Runtime詳細設計(P2-03)
- Evidence Runtime Pipeline(P2-04)
- Integration Simulation実施(P2-05)
- Gap-001〜003の最終解消

---

## Knowledge Lineage

**Document:** PHI_RUNTIME_BINDING_ARCHITECTURE_v1.0.md
**Status:** DESIGN
**Created:** 2026-07-29
**Origin:** Phase I(S05〜S10)完了(暫定)後、きむら博士よりPhase II開始(P2-01)として作成を指示された。
**Parent Documents:**
- docs/audits/PHI_RUNTIME_SIMULATION_SCOPE_v0.1.md(S10)
- docs/audits/PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md(S09)
- docs/audits/PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md(S08)
- docs/audits/PHI_SEQUENCE_STATE_MODEL_v1.0.md(S07)
- docs/audits/PHI_MODULE_INTERFACE_CONTRACT_v0.1.md(S06)
- docs/audits/PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md(S05)
**Derived From:** S05〜S10全文書(Phase I基準文書群)
**Supersedes:** なし
**Reason For Creation:** Phase IのArchitecture定義を、実際のRuntimeへ結合するための境界(実装そのものではない)を定義するため。
**Affected Components:** Sequence Controller、MoCKA、Memory、Orchestra、Relay(いずれも境界設計段階、未実装)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Runtime Controller責務(既確定の再掲)、Module Binding(既確定契約の再掲)、State Runtime Mapping(用語整合込み)、Gap Handling Protocol(Gap-001〜003をPending Resolutionのまま引き継ぎ)を記載。実装・Decision Ledger登録は無し。
