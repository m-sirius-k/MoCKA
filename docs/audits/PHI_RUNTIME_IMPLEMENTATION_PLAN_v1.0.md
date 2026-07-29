# PHI Runtime Implementation Plan v1.0

**Status:** PLAN(実装フェーズの作業境界固定。詳細コードはまだ書かない)
**位置づけ:** Phase IV(Runtime Implementation)、**IV-01**。
**Git基準点:** commit `540983854`(Phase I+II)、commit `e64441edb`(Phase III)
**制約(継続)**: Gap-001〜003は実装都合で解消しない。実装上必要になった時点でDecision対象として記録する。

---

## 1. 実装対象Component

`PHI_RUNTIME_IMPLEMENTATION_SPECIFICATION_v1.0.md`(P3-01)§2の実装可能性評価に基づく。

| Component | 実装対象範囲 |
|---|---|
| MoCKA Adapter | 全範囲(既存`event_gate.py`・Decision Ledger連携を土台とする) |
| Memory Adapter | 保存・Provenance取得は全範囲。Freshness判定はGap-003の閾値未確定のため、判定ロジックの枠組みのみ(具体的数値は含めない) |
| Orchestra Adapter | 全範囲(既存資産を土台とする) |
| Relay Adapter | 全範囲(既存資産を土台とする) |
| Sequence Controller(State Transition部分) | Reject経路を除く全範囲 |
| Human Gate Interface | Approve/Request More Evidence経路のみ。Reject経路はGap-001解消まで実装対象外 |

---

## 2. 実装順序

Gap-001の影響を受けないComponentを先行させる。

```
1. Event Schema基盤(P3-02準拠のEvent記録機構)
2. MoCKA Adapter
3. Memory Adapter(Freshness枠組みのみ)
4. Orchestra Adapter
5. Relay Adapter
6. Sequence Controller(State Transition、Reject経路除く)
7. Human Gate Interface(Approve/Request More Evidence経路)
```

**理由**: Event Schema基盤は他の全Componentが依存する土台であるため最初に置く。4つのAdapterは相互に独立して実装可能なため、既存資産の成熟度が高い順(MoCKA→Memory→Orchestra→Relay)とする。Sequence Controller・Human Gate Interfaceは他Componentへの依存が大きいため最後に置く。

---

## 3. Phase I〜III参照関係

| 実装対象 | 参照する設計文書 |
|---|---|
| Event Schema基盤 | `PHI_RUNTIME_EVENT_SCHEMA_v1.0.md`(P3-02) |
| MoCKA/Memory/Orchestra/Relay Adapter | `PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`(S06)、`PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md`(P2-02) |
| Sequence Controller | `PHI_SEQUENCE_STATE_MODEL_v1.0.md`(S07)、`PHI_CONTROLLER_PROTOTYPE_DESIGN_v1.0.md`(P3-03) |
| Human Gate Interface | `PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md`(S09) |

いずれの実装も、参照する設計文書の境界を変更しない。

---

## 4. Gap引継ぎ

| Gap | Phase IVでの扱い |
|---|---|
| Gap-001: REJECTED状態不足 | 実装対象外(Human Gate InterfaceのReject経路は実装しない)。実装上どうしても必要になった場合はDecision対象として記録し、本Planでは解消しない |
| Gap-002: Decision Ledgerフィールド不足 | 既存の自由記述運用(`context`欄)をそのまま実装で採用する。スキーマ拡張は行わない |
| Gap-003: Freshness閾値未確定 | 判定ロジックの枠組みのみ実装し、具体的な閾値はプレースホルダー(未確定値であることが明示された状態)とする |

---

## 5. Validation基準

`PHI_RUNTIME_INTEGRATION_TEST_PLAN_v1.0.md`(IV-04)で詳細化するが、本Planでは以下を最低基準として固定する。

- 実装がS07/S08/S09の既存境界を変更していないこと
- 実装がGap-001〜003を勝手に解消していないこと
- 実装対象外(Reject経路等)が、エラーではなく「未実装」として明示的に扱われていること(サイレントな欠落禁止)

---

## 6. 含めない範囲

- 詳細コード
- UI
- Deployment

---

## Knowledge Lineage

**Document:** PHI_RUNTIME_IMPLEMENTATION_PLAN_v1.0.md
**Status:** PLAN
**Created:** 2026-07-29
**Origin:** Phase III完了・Git Seal(`e64441edb`)後、きむら博士よりPhase IV一括進行の第一工程(IV-01)として作成された。
**Parent Documents:** Phase III全文書(P3-01〜P3-06)
**Derived From:** PHI_RUNTIME_IMPLEMENTATION_SPECIFICATION_v1.0(実装可能性評価の継承)
**Supersedes:** なし
**Reason For Creation:** 実装フェーズの作業境界(対象・順序・参照関係・Gap引継ぎ・Validation基準)を、実装着手前に固定するため。
**Affected Components:** 全Component
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。実装対象Component、実装順序7ステップ、Phase I〜III参照関係、Gap引継ぎ3件、Validation基準3件、含めない範囲3件を記載。詳細コード・Gap解消は無し。
