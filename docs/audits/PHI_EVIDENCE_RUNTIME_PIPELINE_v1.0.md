# PHI Evidence Runtime Pipeline v1.0

**Status:** DESIGN(Evidence流通経路の設計案。実装コード・Decision Ledger登録はまだ行わない)
**位置づけ:** Phase II、**P2-04**。EvidenceがRuntime上でどう流れるかを定義する。
**方針(継続適用)**: 既存State Model(S07)・既存契約(S06)を書き換えない/Gapは勝手に解消しない。

---

## 1. Evidence Pipeline

```
Input
  |
  v
Observation
  |
  v
Evidence Capture
  |
  v
Validation
  |
  v
Governance Check
  |
  v
Human Gate
  |
  v
Decision Record
  |
  v
Memory
```

**S07との対応**: `Observation`は`OBSERVED`、`Evidence Capture`〜`Validation`は`CLASSIFIED`〜`CONTEXT_READY`〜`VERIFICATION_PENDING`、`Governance Check`は`VERIFIED`、`Human Gate`は`HUMAN_GATE_REQUIRED`〜`APPROVED`、`Decision Record`は`APPROVED`(Decision Ledger登録)、`Memory`は`MEMORIZED`にそれぞれ対応する。新規のPipeline名称であり、S07の状態名自体は変更しない。

---

## 2. Evidence Object

Evidenceは以下の要素を持つオブジェクトとして扱う。

- `source`: 一次資料の所在(ファイルパス・event_id・decision_id等)
- `content`: Evidence本体(観測内容・検証結果等)
- `captured_at`: 取得時刻
- `provenance`: §3参照

---

## 3. Provenance

すべてのEvidenceは出典(Provenance)を持たなければならない。

- `PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`§4「Provenance欠落Memoryの昇格」禁止と直接対応する
- Provenance欠落のEvidenceは`Validation`段階を通過できない(§4参照)

---

## 4. Validation Point

Evidenceが検証される地点を固定する。

| Validation Point | 内容 |
|---|---|
| Capture後 | Provenance存在確認(欠落Evidenceの除外) |
| Governance Check | MoCKAによるConstitution原則4・5.1適合確認 |
| Human Gate提示前 | Evidence Packageとしての完全性確認(`PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md`§2「VERIFIED Evidence Package」相当) |

---

## 5. Storage Point

Evidenceが永続化される地点。

| Storage Point | 対応するMemory種別 |
|---|---|
| Decision Record後 | Decision Memory(`PHI_MEMORY_ARCHITECTURE_v1.0.md`§2) |
| Memory到達後(MEMORIZED) | Event Memory / Semantic Memory / Procedural Memory(内容に応じて分類) |

---

## 6. Audit Reference

各Storage Pointでの書込は、`event_id`または`decision_id`をAudit Referenceとして記録する。これにより`PHI_RUNTIME_SIMULATION_SCOPE_v0.1.md`§6のSimulation Evidence形式(`Audit Reference`欄)と接続する。

---

## 7. Gap-002 影響分析(解決しない)

`PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md`§3で発見されたGap-002(Decision Ledgerスキーマに`Previous State`/`Requested Transition`の専用フィールドが存在しない)について、本Pipelineにおける影響を分析する。

**影響**: `Decision Record`段階(§1)で、Evidence Pipelineが`Requested Transition`(例: `HUMAN_GATE_REQUIRED -> APPROVED`)の情報を保持していても、Decision Ledgerの`decision`/`context`欄への自由記述としてしか記録できない。構造化されたクエリ(例: 「特定の遷移に関する過去のDecisionのみを抽出する」)を将来必要とする場合、この構造化不足が制約になり得る。

**本文書での扱い**: 影響を記録するに留め、スキーマ拡張の要否・実施はここでは決定しない。Gap-002はPending Resolutionのまま持ち越す。

---

## 8. 本設計で決めないこと

- Evidence Objectの技術的シリアライズ形式
- Gap-002のスキーマ拡張実施
- Integration Simulation実施(P2-05で扱う)

---

## Knowledge Lineage

**Document:** PHI_EVIDENCE_RUNTIME_PIPELINE_v1.0.md
**Status:** DESIGN
**Created:** 2026-07-29
**Origin:** `PHI_STATE_TRANSITION_RUNTIME_DESIGN_v1.0.md`(P2-03)完了後、Phase II一括実行の第三工程(P2-04)として作成された。
**Parent Documents:** docs/audits/PHI_STATE_TRANSITION_RUNTIME_DESIGN_v1.0.md、docs/audits/PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md、docs/audits/PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md
**Derived From:** PHI_MEMORY_ARCHITECTURE_v1.0(Memory分類との対応)
**Supersedes:** なし
**Reason For Creation:** EvidenceのRuntime上の流通経路を固定し、Gap-002の影響範囲を分析するため。
**Affected Components:** Evidence Pipeline、Decision Ledger
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Evidence Pipeline(S07対応込み)、Evidence Object、Provenance、Validation Point、Storage Point、Audit Reference、Gap-002影響分析(未解決のまま保持)を記載。実装・Decision Ledger登録は無し。
