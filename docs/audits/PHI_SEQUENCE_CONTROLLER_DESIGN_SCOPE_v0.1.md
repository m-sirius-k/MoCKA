# PHI Sequence Controller Design Scope v0.1

**Status:** SCOPE(設計対象の定義。Architecture本体・実装・Decision Ledger登録はまだ行わない)
**位置づけ:** ジャービス化ロードマップ次工程。PHI-OSの中核となるSequence Controllerを設計対象として定義する。

```
Identity -> Authority -> Governance -> Registration -> Memory -> Sequence Controller -> Assistant Runtime
```

**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 0. 既存資産確認(Confirmed、ゼロから設計しないため)

Sequence Controller相当の機構は、既にPHI-OS Core内に前身が存在する。

- `phios/core/orchestrator.py`(RC-008、`PHIOS_ARCHITECTURE_CONSOLIDATION_REPORT_v1.md`§1.1で既確認): `InterpretedEvent -> DecisionSynthesizer -> SemanticRouter -> Executor`という**固定4段パイプライン**が既に稼働している
- `PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`§1は、この`orchestrator.py`を「Sequence Controller(現状は固定4段パイプライン。将来Planner/Sequence Engine/Workflow Engineへ拡張予定、RC-001〜003)」と明示的に位置づけ済み
- `phios/core/semantic_router.py`は`critical`/`govern`種別のイベントを`"human_gate"`という文字列ターゲットへルーティングするが、`routable=False`/`requires_human=True`を返すのみで、**実際にはどこにも接続していない**(`PHIOS_ARCHITECTURE_CONSOLIDATION_REPORT_v1.md`§2で既確認)

**本Scopeが対象とすること**: この既存の固定4段パイプラインを拡張し、正式なSequence Controllerとして再定義するための設計対象を定義する。ゼロからの新規実装ではなく、既存`orchestrator.py`の拡張・再配線を前提とする。

---

## 1. Purpose

Sequence Controllerとは何か。

- **AIモデルではない**(推論エンジンそのものではなく、推論エンジンをいつ・どの順序で呼ぶかを制御する層)
- **Plannerでもない**(計画生成そのものではなく、計画・実行・監査の各段階を接続する制御層)
- **PHI-OS全体の状態遷移制御層である**

---

## 2. Responsibility

- Module Coordination
- State Transition Control
- Execution Ordering
- Human Gate Routing
- Evidence Check Trigger

---

## 3. Module Interface

```
Sequence Controller

 +-- MoCKA
 |     Governance / Verification

 +-- Memory
 |     Context Reconstruction

 +-- Orchestra
 |     Model Selection

 +-- Relay
 |     External State Sync

 +-- Human Gate
       Final Authority
```

**既存資産との対応(Confirmed)**: 「Memory / Context Reconstruction」は`PHI_MEMORY_ARCHITECTURE_v1.0.md`§4のMemory Lifecycle(Retrieval→Reconstruction)と直接対応する。「Human Gate / Final Authority」は`semantic_router.py`が既に持つ`"human_gate"`ルーティングの意図と一致するが、§0で確認した通り現状は未接続であり、本設計が接続先を定義する対象になる。

---

## 4. State Transition Model

```
Observation
    |
    v
Classification
    |
    v
Planning
    |
    v
Verification
    |
    v
Approval
    |
    v
Execution
    |
    v
Audit
    |
    v
Memory
```

**既存資産との対応(Confirmed)**: `orchestrator.py`の`InterpretedEvent -> DecisionSynthesizer -> SemanticRouter -> Executor`は、この8段階のうち`Observation`〜`Planning`〜`Execution`に相当する部分的な実装であり、`Verification`/`Approval`/`Audit`/`Memory`は新規に接続する対象となる。

---

## 5. Human Gate Integration

Sequence Controllerは「勝手に決定する機構」ではない。

**役割:**
- 判断候補生成
- Evidence提示
- Gate要求
- 承認後実行

**既存資産との対応(Confirmed)**: 本セッション全体を通じて実施したDecision Draft提示→きむら博士確認→`mocka_decision_write`実行というパターン(`DC_20260729_008`〜`010`)が、この役割の人間主導版の実例である。Sequence Controllerの設計課題は、この人間主導フローを自動化するのではなく、**同じ構造(候補生成→Evidence提示→Gate要求→承認後実行)を維持したまま接続すること**にある。

---

## 6. Jarvis Runtime Connection(参考、本文書では未着手)

```
User Intent
    |
    v
Sequence Controller
    |
    v
Memory Retrieval
    |
    v
MoCKA Verification
    |
    v
Orchestra Execution
    |
    v
Action
```

---

## 7. 注意事項(S04では決定しない事項)

- 自律Agent権限
- 音声UI
- 常駐プロセス
- 外部デバイス制御
- 完全自動実行

これらはAssistant Runtime段階(Phase J5)の対象であり、本Scopeでは扱わない。

---

## Knowledge Lineage

**Document:** PHI_SEQUENCE_CONTROLLER_DESIGN_SCOPE_v0.1.md
**Status:** SCOPE
**Created:** 2026-07-29
**Origin:** `PHI_MEMORY_ARCHITECTURE_v1.0.md`完了後、きむら博士よりS04として作成を指示された。
**Parent Documents:**
- docs/audits/PHI_MEMORY_ARCHITECTURE_v1.0.md
- PlanningCaliber/workshop/phi-os/docs/consolidation/PHIOS_ARCHITECTURE_CONSOLIDATION_REPORT_v1.md
- PlanningCaliber/workshop/phi-os/docs/consolidation/PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md
**Derived From:** PHI_MEMORY_ARCHITECTURE_v1.0(Memory Lifecycle・MoCKA連携の継承元)
**Supersedes:** なし
**Reason For Creation:** Sequence Controllerの設計対象を定義し、既存の`orchestrator.py`固定4段パイプラインとの対応関係を明確化するため。
**Affected Components:** `phios/core/orchestrator.py`、`phios/core/semantic_router.py`、`phios/core/decision_synthesis.py`、`phios/core/executor.py`
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。既存資産確認(§0)、Purpose/Responsibility/Module Interface/State Transition Model/Human Gate Integration/Jarvis Runtime Connection/注意事項を記載。設計本体・実装・Decision Ledger登録は無し。
