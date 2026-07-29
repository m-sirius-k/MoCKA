# PHI Runtime Implementation Specification v1.0

**Status:** SPECIFICATION(実装可能性確認のための境界定義。実装コードは含まない)
**位置づけ:** Phase III(Implementation & Operational Validation)、**P3-01**。Phase I/IIの目的(制度設計)から、Phase IIIの目的(実装可能性確認)への移行第一工程。
**Git基準点:** commit `540983854`、tag `phi-phase2-complete-20260729`

**変更禁止事項(継続適用、本文書では一切変更しない)**:
- S07 State Model(`PHI_SEQUENCE_STATE_MODEL_v1.0.md`)
- S08 Memory Permission(`PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`)
- S09 Human Gate Authority(`PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md`)
- Gap-001〜003のPending Resolution状態

---

## 1. Runtime Component構造

Phase II(P2-01〜P2-02)で定義した境界を、実装可能性確認の対象として再整理する(新規定義ではなく既存境界の実装可能性観点での棚卸し)。

```
Sequence Controller Runtime
      |
      +-- MoCKA Adapter
      +-- Memory Adapter
      +-- Orchestra Adapter
      +-- Relay Adapter
      +-- Human Gate Interface
```

---

## 2. Component責務(既存契約の実装可能性確認)

| Component | 責務(P2-02から継承、変更なし) | 実装可能性 |
|---|---|---|
| MoCKA Adapter | Governance判定要求受付・Evidence Validation結果返却・Decision Ledger連携 | 実装可能(既存の`mocka_decision_write/get`・`event_gate.py`が実体として既に存在するため) |
| Memory Adapter | Evidence付き記憶保存・Provenance取得・Freshness状態返却 | 部分的に実装可能(保存・Provenance取得は既存Event/Decision Ledgerで実装可能。Freshness状態返却はGap-003(閾値未確定)により具体的な判定ロジックが未確定) |
| Orchestra Adapter | Model Coordination・Execution候補生成・Result提供 | 実装可能(既存`orchestra_core`相当の資産を土台にできる。ただし本文書では既存資産の詳細検証は行わない) |
| Relay Adapter | State同期・Event搬送・Module間通信 | 実装可能(既存Relay資産を土台にできる) |
| Human Gate Interface | 判断候補生成・Evidence提示・Gate要求 | **部分的に実装可能**。Approve/Request More Evidenceの2経路は実装可能だが、Reject経路はGap-001(REJECTED状態不足)により未定義のまま |

---

## 3. Eventモデル境界

Runtime実装が扱うEventの範囲を、S07・P2-03(State Event/Transition Trigger)の既存定義に限定する。

- Event境界は`PHI_SEQUENCE_STATE_MODEL_v1.0.md`の11状態(`OBSERVED`〜`MEMORIZED`)+`UNKNOWN`に限定される
- 本仕様は、この境界を**拡張しない**(新規State追加は行わない、Gap-001も本文書では解消しない)
- Eventの発生源(Observation/Human Decision/実行結果等)は、`PHI_EVIDENCE_RUNTIME_PIPELINE_v1.0.md`(P2-04)のPipelineに限定される

---

## 4. Interface境界

`PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`(S06)・`PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md`(P2-02)が定義したInput/Output境界を、実装対象の確定範囲として採用する。

- 各Adapterは、S06/P2-02で定義された契約のInput/Output以外を扱わない
- Adapter間の直接通信(Sequence Controllerを介さない通信)は、実装対象に含めない(`PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md`§5 Cross-Adapter原則の継続適用)

---

## 5. Validation Point

`PHI_EVIDENCE_RUNTIME_PIPELINE_v1.0.md`§4のValidation Point(Capture後/Governance Check/Human Gate提示前)を、実装が満たすべき最小要件として採用する。

- 実装は、上記3地点でのEvidence検証を省略してはならない
- 新たなValidation Pointの追加は本文書では行わない

---

## 6. 変更禁止事項の確認

| 項目 | 状態 |
|---|---|
| S07 State Model | 未変更(§3のEvent境界は11状態+UNKNOWNのまま) |
| S08 Memory Permission | 未変更(§2のFreshness判定はGap-003未解決のまま) |
| S09 Human Gate Authority | 未変更(§2のHuman Gate Interfaceの権限境界はそのまま) |
| Gap-001〜003 | いずれもPending Resolutionのまま。本文書は§2でGap-001がHuman Gate Interfaceの実装可能性に与える影響を評価したのみで、解消はしていない |

---

## 7. 実装可能性評価(P3-01の主目的)

| Component | 評価 |
|---|---|
| MoCKA Adapter | 実装可能(既存資産あり) |
| Memory Adapter | 実装可能(Freshness閾値は暫定値または未実装のまま進行可能。Gap-003解消は別途) |
| Orchestra Adapter | 実装可能(既存資産あり) |
| Relay Adapter | 実装可能(既存資産あり) |
| Human Gate Interface | **Approve/Request More Evidence経路のみ実装可能。Reject経路はGap-001解消まで実装保留** |
| Sequence Controller Runtime(State Transition部分) | Reject経路を除き実装可能 |

**結論**: 5 Component中4つは現行の制度設計のまま実装着手が可能である。Human Gate Interface(および連動するSequence Controller Runtime)のみ、Reject経路がGap-001により未定義であるため、その部分に限定して実装を保留する必要がある。これは「Phase III全体を止める」ものではなく、「特定の1経路のみ実装対象から除外して進める」という限定的な保留である。

---

## 8. 本仕様で決めないこと

- 実装コード
- デプロイ設計
- 性能最適化
- 運用インフラ
- Gap-001〜003の最終解消

---

## Knowledge Lineage

**Document:** PHI_RUNTIME_IMPLEMENTATION_SPECIFICATION_v1.0.md
**Status:** SPECIFICATION
**Created:** 2026-07-29
**Origin:** Git Seal(commit `540983854`)後、きむら博士よりPhase III第一工程(P3-01)として作成を指示された。
**Parent Documents:** Phase I全文書(S05〜S10)、Phase II全文書(P2-01〜P2-06)
**Derived From:** PHI_MODULE_ADAPTER_SPECIFICATION_v1.0、PHI_EVIDENCE_RUNTIME_PIPELINE_v1.0
**Supersedes:** なし
**Reason For Creation:** 制度設計から実装可能性確認への移行として、Runtime Component構造・責務・Event/Interface境界・Validation Pointを実装対象として確定し、Gap-001が特定Componentの実装可能性に与える影響を評価するため。
**Affected Components:** MoCKA Adapter、Memory Adapter、Orchestra Adapter、Relay Adapter、Human Gate Interface、Sequence Controller Runtime
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Runtime Component構造、Component責務(実装可能性込み)、Eventモデル境界、Interface境界、Validation Point、変更禁止事項確認、実装可能性評価(5 Component中4つ実装可能、Human Gate InterfaceのみReject経路保留)、本仕様で決めないことを記載。実装コード・デプロイ設計・性能最適化・運用インフラ・Gap解消は無し。
