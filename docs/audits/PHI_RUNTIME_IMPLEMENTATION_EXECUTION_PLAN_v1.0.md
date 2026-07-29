# PHI Runtime Implementation Execution Plan v1.0

**Status:** EXECUTION PLAN(実コード実装着手前の境界固定。本文書自体はコードを書かない)
**位置づけ:** Phase IVは「Runtime Implementation Design / Preparation」として完了(Git Seal `00438e15a`)。本文書はPhase V(Runtime Code Implementation & Execution Validation)の入口として、実行境界を固定する。
**Git基準点:** `540983854`(Phase II)→`e64441edb`(Phase III)→`00438e15a`(Phase IV)

---

## 1. Implementation対象

- Runtime Controller
- Event Handler
- Module Adapter Runtime
- Evidence Pipeline接続

---

## 2. 実装順序

```
Controller Core
      |
      v
Event Runtime
      |
      v
Adapter Runtime
      |
      v
Evidence Flow
      |
      v
Integration Execution
```

**理由**: Controller Coreが他の全要素の土台(State保持・遷移制御)であるため最初に置く。Event Runtimeは各遷移の記録機構であり、Controller Coreの直後に必要になる。Adapter Runtimeは4 Adapterの実装(`PHI_MODULE_ADAPTER_IMPLEMENTATION_SPEC_v1.0.md`、IV-03準拠)。Evidence Flowはこれらが揃って初めて実際に流通させられる(`PHI_EVIDENCE_RUNTIME_PIPELINE_v1.0.md`、P2-04準拠)。Integration Executionは全体を接続した実行確認であり最後に置く。

---

## 3. Phase IV成果物との接続

| 実装対象 | 参照する仕様 |
|---|---|
| Controller Core | `PHI_RUNTIME_CONTROLLER_IMPLEMENTATION_SPEC_v1.0.md`(IV-02) |
| Event Runtime | `PHI_RUNTIME_EVENT_SCHEMA_v1.0.md`(P3-02) |
| Adapter Runtime | `PHI_MODULE_ADAPTER_IMPLEMENTATION_SPEC_v1.0.md`(IV-03) |
| Integration Execution | `PHI_RUNTIME_INTEGRATION_TEST_PLAN_v1.0.md`(IV-04) |

いずれの実装も、参照する仕様の境界(Input/Output/Error境界/Authority境界)を変更しない。

---

## 4. Gap引継ぎ(変更禁止)

| Gap | 内容 | 扱い |
|---|---|---|
| Gap-001 | REJECTED状態不足 | Implementation Constraintとして保持。Reject経路は実装対象外のまま |
| Gap-002 | Decision Ledger Schema(Previous State/Requested Transition不足) | Implementation Constraintとして保持。自由記述運用を継続 |
| Gap-003 | Freshness Threshold未確定 | Implementation Constraintとして保持。プレースホルダー実装に留める |

**明記**: 実装中にこれらのGapへの対応が避けられないと判明した場合でも、実装者(くろこ)が独断で仕様変更・State追加・Schema変更を行わない。その時点で作業を止め、Decision対象としてきむら博士へ報告する。

---

## 5. 実装開始条件

**含む:**
- Runtime Code
- Unit Test
- Integration Test

**含まない:**
- Production Deployment
- Public Release
- Policy変更

---

## 6. 本Execution Planで決めないこと

- 実際のRuntime Code(次工程、Controller Core実装で着手)
- Deployment・Release判断
- Gap-001〜003の最終解消

---

## Knowledge Lineage

**Document:** PHI_RUNTIME_IMPLEMENTATION_EXECUTION_PLAN_v1.0.md
**Status:** EXECUTION PLAN
**Created:** 2026-07-29
**Origin:** Phase IV(Git Seal `00438e15a`)完了後、きむら博士よりPhase V入口の境界固定として作成を指示された。
**Parent Documents:** Phase IV全文書(IV-01〜IV-05)
**Derived From:** PHI_RUNTIME_IMPLEMENTATION_PLAN_v1.0(IV-01の実装順序を実行計画として具体化)
**Supersedes:** なし
**Reason For Creation:** 実コード実装着手前に、対象・順序・参照仕様・Gap引継ぎ・実装開始条件を固定するため。
**Affected Components:** Runtime Controller、Event Handler、Module Adapter Runtime、Evidence Pipeline
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Implementation対象4件、実装順序5ステップ、Phase IV成果物との接続、Gap引継ぎ3件(独断変更禁止の明記込み)、実装開始条件(含む/含まない)を記載。実コードは無し。
