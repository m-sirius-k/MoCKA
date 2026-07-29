# PHI Human Gate Integration Model v1.0

**Status:** DESIGN(正式定義案。実装・Decision Ledger登録はまだ行わない)
**位置づけ:** PHI-OS Operational Integration Phase, **I-04**。Phase Iの中で最重要境界。「AI内部状態 → Human Decision Authority → External Action」の接続点を定義する。
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 1. Human Gateの責任境界

Human Gateは以下ではない。

- **AIの補助者ではない**(AIの判断を追認する役割ではない)
- **最終承認ボタンではない**(形式的なクリック操作ではなく、Evidence確認を伴う制度的行為である)

Human Gateは、**状態遷移機械(Sequence Controller)の外部Authorityである。** これは`PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md`§5(Sequence Controllerは最終判断・Authority変更・Evidenceなし実行を行わない)の直接の裏返しであり、Sequence Controllerが持たない権限は、すべてHuman Gateに帰属する。

---

## 2. Gate対象状態(S07との整合)

`PHI_SEQUENCE_STATE_MODEL_v1.0.md`(既に確定済み・変更対象外)が定めるGate接続点は以下である。

```
VERIFIED
    |
    v
HUMAN_GATE_REQUIRED
    |
    v
APPROVED
    |
    v
EXECUTING
```

**用語の整合確認(重要)**: 本文書はS07が既に固定した状態名(`VERIFIED`/`HUMAN_GATE_REQUIRED`/`APPROVED`)をそのまま使用する。S07の`APPROVED`は「Human Decisionが確定し、Decision Ledgerへ登録された状態」と定義済みであり、本文書における「AUTHORIZED」相当の概念は、この`APPROVED`に一致するものとして扱う。S07では`AUDITED`は`COMPLETED`の**後**(実行後の監査記録)に位置しており、Human Gateより**前**には来ない。S07を変更せず、Gate接続点は`VERIFIED -> HUMAN_GATE_REQUIRED -> APPROVED -> EXECUTING`の一系統のみとする。

---

## 3. Human Decisionの記録方式

必須項目8点と、既存Decision Ledgerスキーマ(`mocka_decision_write`)との対応を確認する。

| 必須項目 | 既存Decision Ledgerスキーマとの対応 |
|---|---|
| Decision ID | `decision_id`(既存、自動採番または明示指定) |
| Input Evidence Reference | `related_documents`/`related_events`(既存) |
| Previous State | **既存スキーマに専用フィールドなし**(現状は`context`欄への自由記述で代替可能) |
| Requested Transition | **既存スキーマに専用フィールドなし**(現状は`context`/`decision`欄への自由記述で代替可能) |
| Human Decision | `decision`(既存) |
| Timestamp | `approved_at`(既存、自動記録) |
| Authority Identity | `approved_by`(既存。本セッションでは一貫して「きむら博士」) |
| Reason | `rationale`(既存) |

**確認結果**: 8項目中6項目は既存Decision Ledgerスキーマで既にConfirmed対応済みである(本セッションで`DC_20260729_001`〜`010`として運用実績あり)。残り2項目(Previous State/Requested Transition)は専用フィールドが存在しないため、当面は`context`欄内の自由記述で運用し、スキーマ自体の拡張要否は別途判断とする(本文書では決定しない)。

---

## 4. 禁止事項

- **AIによるHuman Gate代替禁止**: Sequence Controller・MoCKA・その他いずれのModuleも、`HUMAN_GATE_REQUIRED -> APPROVED`の遷移を人間の判断なしに自動実行してはならない
- **Human GateなしのAPPROVED遷移禁止**: `approved_by`が実在する人間の識別子を持たない`APPROVED`状態は無効とする
- **Decision理由なしの承認禁止**: `rationale`を伴わない承認は記録として成立しない(既存Decision Ledgerスキーマが`rationale`を必須パラメータとしていることと一致)
- **承認後Evidence変更時の再承認要求**: `APPROVED`確定後に、その根拠となった`related_documents`/`related_events`の内容が変更された(Supersede等)場合、当該Decisionは自動的に有効なまま維持されず、再承認(新規Decision、または既存Decisionの`Superseded`状態への遷移)を要求する。これは`PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`§3(Memory Freshness Contract、自動Verified復帰禁止)と同型の原則である

---

## 5. 本Modelで決めないこと

- Decision Ledgerスキーマへの`Previous State`/`Requested Transition`専用フィールド追加の要否
- Human Gate承認の技術的インターフェース(UI・通知方式等)
- 複数人間による承認(Multi-Approver)の要否
- Runtime Simulation(Phase I-05で扱う)

---

## Knowledge Lineage

**Document:** PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md
**Status:** DESIGN
**Created:** 2026-07-29
**Origin:** `PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`完了後、きむら博士よりPhase I-04(S09)として作成を指示された。
**Parent Documents:**
- docs/audits/PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md
- docs/audits/PHI_SEQUENCE_STATE_MODEL_v1.0.md
- docs/audits/PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md
**Derived From:** PHI_SEQUENCE_STATE_MODEL_v1.0(Gate対象状態はS07を変更せず継承)
**Supersedes:** なし
**Reason For Creation:** 「AI内部状態→Human Decision Authority→External Action」の接続点を制度として定義するため。
**Affected Components:** Sequence Controller、Decision Ledger
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Human Gateの責任境界、Gate対象状態(S07用語整合確認込み)、Human Decision記録方式(既存スキーマ対応表)、禁止事項4件、本Modelで決めないこと4件を記載。実装・Decision Ledger登録は無し。
