# PHI Runtime Event Schema v1.0

**Status:** SCHEMA(記録境界の定義。コード化はまだ行わない)
**位置づけ:** Phase III、**P3-02**。Runtime上で発生する全イベントの記録境界を定義する。
**変更禁止事項(継続)**: S07 State Model・S08 Memory Permission・S09 Human Gate Authority・Gap-001〜003のPending状態はいずれも変更しない。

---

## 1. Event Object基本構造

すべてのRuntime Eventが最低限持つべきフィールド。

| フィールド | 内容 |
|---|---|
| Event ID | 一意識別子 |
| Timestamp | 発生時刻 |
| Actor | 発生させた主体(Sequence Controller/MoCKA/Memory/Orchestra/Relay/Human) |
| Source Component | 発生元Component(P3-01§1のRuntime Component構造上の位置) |
| Previous State | 遷移前のState(S07準拠) |
| Current State | 遷移後のState(S07準拠) |
| Evidence Reference | 根拠となるEvidence Object(P2-04 Evidence Runtime Pipelineとの接続) |
| Decision Reference | 関連するDecision Ledgerエントリ(存在する場合) |
| Audit Reference | 対応するAudit Event |

**Gap-002との関係(重要)**: `Previous State`/`Current State`フィールドは、`PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md`§3(Gap-002、Decision Ledgerに`Previous State`/`Requested Transition`の専用フィールドが無い)で指摘された不足を、**Event層で先に満たす**ものである。ただし、これはDecision Ledgerのスキーマ自体を変更するものではない。Gap-002はDecision Ledger側の課題として引き続きPending Resolutionのまま残る。Event SchemaがこのフィールドをRuntime記録として持つことと、Decision Ledgerのスキーマ拡張は別の問題である。

---

## 2. State Transition Event

S07との接続。

```
State Before
    |
    v
Transition Request
    |
    v
Validation
    |
    v
State After
```

- `State Before`/`State After`はいずれもS07の11状態(`OBSERVED`〜`MEMORIZED`)+`UNKNOWN`のいずれかでなければならない(新規State追加不可)
- `Validation`は`PHI_STATE_TRANSITION_RUNTIME_DESIGN_v1.0.md`(P2-03)§3 Transition Validationの基準をそのまま適用する

---

## 3. Evidence Event

S08/S09との接続。

- **Evidence取得**: `Evidence Reference`が新規に紐づけられる
- **Evidence検証**: MoCKA Adapterによる検証結果(Pass/Fail)が記録される
- **Evidence不足**: `State After`が`UNKNOWN`になる場合の記録(S07§5、時間経過や推測による解消は認めない)
- **Evidence更新**: 既存Evidenceが新しいEvidenceで置き換えられる場合(`PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`§3 Freshness Contract、自動Verified復帰は禁止のまま)

---

## 4. Human Decision Event

S09との接続。

| 項目 | 内容 |
|---|---|
| Human Gate invocation | `HUMAN_GATE_REQUIRED`到達時の記録 |
| Decision result | Approve / Request More Evidence / Reject(Rejectは§5参照、Gap-001によりCurrent Stateが未定義) |
| Authority reference | `approved_by`相当(既存Decision Ledgerスキーマと同一の概念) |
| Decision rationale | `rationale`相当(既存Decision Ledgerスキーマと同一の概念) |

**Gap-002との関係の記録**: Human Decision Eventの`Previous State`/`Current State`(§1)は、対応するDecision Ledgerエントリの`context`欄に自由記述として反映される(既存の運用、`PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md`§3で確認済み)。本Eventスキーマは、この対応関係を明示するのみで、Decision Ledger側のフィールド追加は行わない。

---

## 5. Failure / Unknown Event

**重要な区別**: Runtime FailureとGovernance Unknownは、明確に別のEvent種別として扱う。

| 種別 | 定義 | 対応 |
|---|---|---|
| System Failure | Runtime実行環境の技術的な異常(通信断・プロセス異常終了・タイムアウト等) | 技術的な復旧対象。Stateを`UNKNOWN`にはしない(制度的な証拠不足ではなく、単なる実行環境の障害であるため) |
| Evidence Unknown(Governance Unknown) | S07の`UNKNOWN`状態そのもの。Evidence不足による制度的な判断保留 | 新規Evidence取得によってのみ解消。技術的な復旧処置とは無関係 |

**両者を混同してはならない理由**: System FailureをEvidence Unknownとして記録すると、「技術障害」が「証拠不足によるPending Resolution」であるかのように見えてしまい、`DC_20260729_009`(Option D)が確立した「証拠不足を正しく保存する」という意味が、単なる技術的トラブルによって希釈される。逆にEvidence UnknownをSystem Failureとして扱うと、技術的な再試行(リトライ)によって誤って状態が「解消」されたように見えるリスクがある。

---

## 6. 永続化境界

**含む:**
- Event schema(本文書§1〜5の構造)
- Provenance(Evidence Referenceの出典情報)
- Audit reference

**含まない:**
- DB実装
- Storage engine選択
- Performance tuning

---

## 7. 本仕様で決めないこと

- Event ObjectのDB実装・テーブル設計
- Storage engine(SQLite継続か別技術かを含む)の選定
- Performance tuning
- Gap-001〜003の最終解消

---

## Knowledge Lineage

**Document:** PHI_RUNTIME_EVENT_SCHEMA_v1.0.md
**Status:** SCHEMA
**Created:** 2026-07-29
**Origin:** `PHI_RUNTIME_IMPLEMENTATION_SPECIFICATION_v1.0.md`(P3-01)完了後、きむら博士よりPhase III第二工程(P3-02)として作成を指示された。
**Parent Documents:** docs/audits/PHI_RUNTIME_IMPLEMENTATION_SPECIFICATION_v1.0.md、docs/audits/PHI_SEQUENCE_STATE_MODEL_v1.0.md、docs/audits/PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md、docs/audits/PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md
**Derived From:** PHI_STATE_TRANSITION_RUNTIME_DESIGN_v1.0、PHI_EVIDENCE_RUNTIME_PIPELINE_v1.0
**Supersedes:** なし
**Reason For Creation:** Runtime上で発生する全イベントの記録境界を、コード化前に固定するため。
**Affected Components:** Event記録層(全Component共通)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Event Object基本構造(9フィールド、Gap-002との関係明記)、State Transition Event、Evidence Event、Human Decision Event(Gap-002関係)、Failure/Unknown Event(System FailureとEvidence Unknownの分離)、永続化境界、本仕様で決めないことを記載。コード化・DB実装・Gap解消は無し。
