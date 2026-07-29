# PHI-OS / MoCKA Integration Human Gate Decision Record v0.1

**Status:** DECISION INPUT TEMPLATE(未記入。判断そのものは含まない。Decision Ledger登録はまだ行わない)
**位置づけ:** `PHI_MOCKA_INTEGRATION_HUMAN_GATE_REVIEW_v0.1.md`(commit `8b927ff14`)後続、Human Gate Decision Input Preparation(Phase 3-A)。
**目的:** Human Gateを代行しない。博士の判断結果を、そのまま`mocka_decision_write`でDecision Ledgerへ記録できる形式に整えるための入力フォームである。
**分類:** Decision Preparation → Human Decision(本文書の役割はここまで) → Decision Seal(次工程、博士記入後)

---

## 1. Decision Metadata

```
Decision ID:          (承認時にDC_YYYYMMDD_NNN形式で付番。本文書では未定)
対象:                  PHI-OS Module Integration — Integration Adapter Architecture

Evidence:              commit d69121b9e (PHI_RUNTIME_ARCHITECTURE_VALIDATION_v1.0.md,
                        PHI_MODULE_INTEGRATION_STRATEGY_PROPOSAL_v0.1.md,
                        PHI_RUNTIME_IMPLEMENTATION_EXECUTION_PLAN_v1.0.md)
Scope:                 commit 224a7bfe3 (PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md)
Architecture Package:  commit 51dcbe920 (PHI_MOCKA_INTEGRATION_ARCHITECTURE_DECISION_PACKAGE_v0.1.md)
Review:                commit 8b927ff14 (PHI_MOCKA_INTEGRATION_HUMAN_GATE_REVIEW_v0.1.md)
```

---

## 2. Decision Items(未記入、博士記入欄)

### D-01: Integration Pattern

```
選択:
[x] Candidate A — PHI-OS Adapter Pattern
[ ] Candidate B — Relay-mediated Pattern
[ ] Candidate C — Event Bridge Pattern
[ ] Reject / Redesign(理由: ______________________)
```

### D-02: Adapter Responsibility Boundary

```
記述:
Adapter = Translation Boundary(翻訳境界)。

Allowed(Adapterに許可される責務):
- Interface transformation(インターフェース変換)
- Request/Response transformation(要求/応答の変換)
- Context transfer(コンテキスト伝達)
- Evidence reference linking(証跡参照の紐付け)
- Runtime connection management(Runtime接続管理)

Forbidden(Adapterに禁止される責務):
- Decision generation(意思決定の生成)
- Policy modification(ポリシー変更)
- Authority judgment(権限判断)
- Human Gate replacement(Human Gateの代替)
- Evidence modification(証跡の改変)

Adapterは変換・伝達・接続管理のみを担い、判断・裁定・証跡改変のいずれも行わない。
```

### D-03: Authority Ownership

```
記述:
PHI-OS:
- Runtime Coordination(Runtime調整)
- Execution Control(実行制御)
- Human Gate Routing(Human Gateへの経路制御)

MoCKA:
- Evidence Management(証跡管理)
- Decision Evidence(意思決定証跡)
- Audit Intelligence(監査インテリジェンス)
- Governance Analysis(ガバナンス分析)

Human:
- Architecture Authority(アーキテクチャ権限)
- Policy Change Approval(ポリシー変更承認)
- Irreversible Decision(不可逆判断)

Adapter(D-02のTranslation Boundary)はこの3者いずれの権限も保有しない。PHI-OS/MoCKA/Human間の
既存の権限配分そのものは変更せず、Adapterはその配分の間を仲介するのみ。
```

### D-04: Implementation Authorization

```
選択:
[ ] Approved
[x] Approved with Conditions
[ ] Revise(差し戻し理由: ______________________)
[ ] Reject(理由: ______________________)

条件:
D-02(Adapter = Translation BoundaryのAllowed/Forbidden境界)およびD-03(Authority
Ownershipの3者配分)を実装の拘束条件とする。実装がこの境界・配分を逸脱する場合は、
本Decisionの範囲外として再度Human Gateへ差し戻す。

[記録上の注記: 本欄の条件テキストは、博士提示のD-02/D-03の内容がD-04の実質的な
承認条件であるとClaude側で解釈し明文化したものである。博士自身が別途「条件」として
明示した独立の文言ではない。この解釈に相違があれば訂正されたい。]
```

---

## 3. Existing Constraints(自動記録、確定済み・変更対象外)

いずれのDecision Itemsを選んでも、以下は本判断によって変更されない。

```
保持条件:

- Runtime Foundation変更禁止(controller_core.py / event_runtime.py /
  adapter_runtime.py / memory_boundary.py、DC_20260729_011)
- MoCKA本体変更禁止(C:/Users/sirok/MoCKA/のうちPlanningCaliber/を除く部分)
- Evidence Lineage維持(d69121b9e → 224a7bfe3 → 51dcbe920 → 8b927ff14 の参照関係)
- Human Gate必須(責務・権限に関わる変更はHuman Gateを経ずに確定しない)
- Gap Pending維持(Gap-001 REJECTED状態不足 / Gap-002 Decision Ledgerフィールド不足 /
  Gap-003 Freshness閾値未確定は本判断で暗黙に解消しない)
```

---

## 4. Decision Ledger Entry Template(記入完了後、この形式で`mocka_decision_write`へ変換)

```
title:          [HG-MI-MoCKA-ADAPTER] Integration Adapter Architecture Decision
context:        (§1 Decision Metadata + §2 D-01〜D-04の記入内容を要約)
alternatives:   (§2 D-01で不採用としたCandidate/選択肢を、rejected_reasonとともに列挙。
                 却下案が無い場合はoption:N/Aの1件を入れる)
decision:       (§2 D-01〜D-04の記入結果をそのまま転記)
rationale:      (§2 D-02〜D-03の記述、および§4評価基準への言及があれば転記)
impact:         (§3 Existing Constraintsを「本Decisionで変更されないもの」として転記。
                 加えて次工程=Implementation Planへの移行条件を記載)
approved_by:    きむら博士
related_documents: [
  "docs/audits/PHI_RUNTIME_ARCHITECTURE_VALIDATION_v1.0.md",
  "docs/audits/PHI_MODULE_INTEGRATION_STRATEGY_PROPOSAL_v0.1.md",
  "docs/audits/PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md",
  "docs/audits/PHI_MOCKA_INTEGRATION_ARCHITECTURE_DECISION_PACKAGE_v0.1.md",
  "docs/audits/PHI_MOCKA_INTEGRATION_HUMAN_GATE_REVIEW_v0.1.md",
  "docs/audits/PHI_MOCKA_INTEGRATION_HUMAN_GATE_DECISION_RECORD_v0.1.md"
]
```

**Result:**
```
Decision:       (D-01〜D-04の結論を1行で要約)
Evidence:       d69121b9e / 224a7bfe3 / 51dcbe920 / 8b927ff14(いずれもSeal済み)
Verification:   UTF-8検証OK、git seal済み、Core System File除外0件(全4文書共通)
Authority:      Human Gate(きむら博士)
Next Phase:     Implementation Plan(D-04がApproved/Approved with Conditionsの場合のみ)
```

---

## 停止点(更新済み)

```
Phase 3-A: Human Gate Decision Input Preparation
COMPLETE

Human Gate Decision:
RECORDED(D-01: Candidate A / D-02: Translation Boundary / D-03: Authority Ownership 3者配分 / D-04: Approved with Conditions)

Decision Ledger:
DC_20260729_013(approved_by=きむら博士, approved_at=2026-07-29T07:17:06Z、読み戻し確認済み)

Next Phase:
Implementation Plan(D-02/D-03を拘束条件として)
```

D-01〜D-04はきむら博士により記入された(2026-07-29)。本文書作成者(Claude)はCandidate採択・Architecture確定のいずれも行っていない(判断はD-01〜D-04として博士から提示された内容をそのまま転記)。

---

## Knowledge Lineage

**Document:** PHI_MOCKA_INTEGRATION_HUMAN_GATE_DECISION_RECORD_v0.1.md
**Status:** DECISION INPUT TEMPLATE
**Created:** 2026-07-29
**Origin:** きむら博士指示「Phase 3-A: Human Gate Decision Input Preparation 開始。Decision項目のみ整理し、Candidate採択・Architecture確定は禁止」を受けて作成。
**Parent Documents:** `docs/audits/PHI_MOCKA_INTEGRATION_HUMAN_GATE_REVIEW_v0.1.md`(commit `8b927ff14`), `docs/audits/PHI_MOCKA_INTEGRATION_ARCHITECTURE_DECISION_PACKAGE_v0.1.md`(commit `51dcbe920`), `docs/audits/PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md`(commit `224a7bfe3`), `DC_20260729_011`, `DC_20260729_012`
**Derived From:** `HUMAN_GATE_REVIEW_v0.1.md`§2(Decision Required Items)を、Decision Ledger登録可能な入力フォーム形式へ変換
**Supersedes:** なし
**Reason For Creation:** 博士の判断結果を、追加の解釈・変換作業なしにそのままDecision Ledgerへ記録できる形式に整えるため。
