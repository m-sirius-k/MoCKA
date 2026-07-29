# PHI Sequence Controller Architecture v1.0

**Status:** DESIGN(正式定義案。Decision Ledger登録・実装はまだ行わない)
**位置づけ:** `PHI_SEQUENCE_CONTROLLER_DESIGN_SCOPE_v0.1.md`承認後、PHI-OSの制御中枢としてのSequence Controllerを正式定義する。
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 1. Purpose and Definition

Sequence Controllerとは何か。

- **AIモデルではない**(推論そのものを行う主体ではない)
- **Decision Makerではない**(最終判断を下す主体ではない。判断はHuman Gate、あるいはMoCKAの検証を経て確定する)
- **Module間の状態遷移制御層である**(いつ・どのModuleを・どの順序で呼ぶかを制御する)

---

## 2. Architecture Position

```
                Human Gate
                    |
         PHI-OS Sequence Controller
                    |
      +---------+---------+---------+
      |         |         |         |
    MoCKA     Memory   Orchestra   Relay
```

---

## 3. State Transition Engine

```
Observation
    |
    v
Classification
    |
    v
Context Retrieval
    |
    v
Verification
    |
    v
Planning
    |
    v
Human Gate
    |
    v
Execution
    |
    v
Audit
    |
    v
Memory Update
```

**既存資産との対応(Confirmed)**: `PHI_SEQUENCE_CONTROLLER_DESIGN_SCOPE_v0.1.md`§0・§4で確認済みの通り、`phios/core/orchestrator.py`の`InterpretedEvent -> DecisionSynthesizer -> SemanticRouter -> Executor`は、この9段階のうち`Observation`〜`Classification`〜`Planning`〜`Execution`に相当する部分実装である。`Context Retrieval`(Memory層との接続、`PHI_MEMORY_ARCHITECTURE_v1.0.md`§4のRetrieval/Reconstruction段階に対応)・`Verification`・`Human Gate`(現状`semantic_router.py`は文字列ターゲットを返すのみで未接続)・`Audit`・`Memory Update`は新規に接続する対象である。

---

## 4. Existing Implementation Mapping

| 概念 | 既存資産 |
|---|---|
| Pipeline Control | `phios/core/orchestrator.py` |
| Routing | `phios/core/semantic_router.py` |
| Governance Check | MoCKA(`phi_os/event_gate.py`、Constitution原則4・5.1) |
| Context | Memory(`PHI_MEMORY_ARCHITECTURE_v1.0.md`) |
| Model Selection | Orchestra |

---

## 5. Human Gate Control Model

Sequence Controllerの権限境界を明示する。

**許可しない:**
- 最終判断
- Authority変更(`DC_20260729_009`でPending Resolutionとされた PHI-Con/PHI-Core間のAuthority関係を、Sequence Controllerが独自に確定させることは含まれない)
- Evidenceなし実行

**実行可能:**
- 判断候補生成
- 必要Module呼出
- Gate要求

### 5.1 MoCKAとの境界(重要)

| コンポーネント | 問い |
|---|---|
| Sequence Controller | 「次に何をするか」 |
| MoCKA | 「それを許可できるか」「証拠はあるか」 |
| Memory | 「過去に何があったか」 |
| Orchestra | 「どのモデル・能力を使うか」 |
| Relay | 「外部状態を同期する」 |

**Sequence ControllerはMoCKAの代わりに判断しない。** これは`DC_20260728_003`が確立した「PHI-OS CoreとMoCKA Governance Runtimeは別レイヤー」という境界(`PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`)を、Sequence Controller設計においても維持することを意味する。Sequence ControllerからMoCKA本体`phi_os/`パッケージへの直接importという禁止事項(`DC_20260728_003`§5)は、本Architectureでも継続して適用される。

**既存実例(Confirmed)**: 本セッションで一貫して行ってきた「Decision Draft提示→きむら博士確認→`mocka_decision_write`実行→read-back確認」というフローは、まさにこの権限境界(候補生成はAI側、最終承認はHuman Gate、Evidence確認は必須)を人間主導で実演したものである。

---

## 6. Future Jarvis Runtime(参考、本文書では未着手)

```
User Intent
    |
    v
Sequence Controller
    |
    v
Memory Reconstruction
    |
    v
MoCKA Verification
    |
    v
Orchestra Execution
    |
    v
Action
    |
    v
Audit
```

---

## 7. S05で決めない項目

- 完全自律Agent権限
- 常時監視
- 音声人格
- ロボット制御
- 外部サービス全面操作

これらは後続フェーズ(Assistant Runtime)の対象であり、本Architectureでは扱わない。

---

## Knowledge Lineage

**Document:** PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md
**Status:** DESIGN
**Created:** 2026-07-29
**Origin:** `PHI_SEQUENCE_CONTROLLER_DESIGN_SCOPE_v0.1.md`承認後、きむら博士よりS05としてArchitecture本体作成の指示を受けた。
**Parent Documents:**
- docs/audits/PHI_SEQUENCE_CONTROLLER_DESIGN_SCOPE_v0.1.md
- docs/audits/PHI_MEMORY_ARCHITECTURE_v1.0.md
- PlanningCaliber/workshop/phi-os/docs/consolidation/PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md
- DC_20260728_002、DC_20260728_003、DC_20260729_009
**Derived From:** PHI_SEQUENCE_CONTROLLER_DESIGN_SCOPE_v0.1
**Supersedes:** なし
**Reason For Creation:** PHI-OSの制御中枢としてSequence Controllerを正式定義し、MoCKAとの権限境界を明確化するため。
**Affected Components:** `phios/core/orchestrator.py`、`phios/core/semantic_router.py`、`phios/core/decision_synthesis.py`、`phios/core/executor.py`
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Purpose and Definition/Architecture Position/State Transition Engine9段階/Existing Implementation Mapping/Human Gate Control Model(MoCKAとの境界含む)/Future Jarvis Runtime/S05で決めない項目を記載。実装・Decision Ledger登録は無し。
