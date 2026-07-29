# PHI Authority Decision Draft v0.1

**Status:** DRAFT([DC-PHI-ID-002] PHI Authority Flow Model Selection Policyの候補比較資料。Decision Ledger登録前段階)
**位置づけ:** `PHI_AUTHORITY_MODEL_PROPOSAL_v0.1.md`を基礎とし、DC-PHI-ID-002の裁定に向けて4選択肢を比較する。Decision化(mocka_decision_write実行)はまだ行わない。
**実装・リネーム:** 一切含まない。

**既存Decision不変更の前提**: 以下のOption A〜Dのいずれを選択した場合でも、次のDecisionは変更・撤回されない。
- `DC_20260728_002`(Canonical PHI-OS Core確定: phios/+ise/+phi_os_core.py)
- `DC_20260728_003`(PHI-OS/MoCKA Boundary確定: 判定区分E)
- `DC_20260729_008`(DC-PHI-ID-001、Responsibility Classification Alias採用)

---

## 1. 4 Option比較表

| Option | 内容 | Evidence | Risk | 変更範囲 |
|---|---|---|---|---|
| **A** | Constitution Authority Modelを正式Authorityモデルとする(PHI-Con → MoCKA全体) | `PHI_OS_CONSTITUTION_v1.md`第1章1.1、RATIFIED v1(制度上唯一の上位文書) | `DC_20260728_003`(MoCKA Governance RuntimeをPHI-Coreの外部保証層とする整理)と正面から向きが逆になる可能性がある。DC_003を撤回せずOption Aを採用する方法(適用範囲の限定等)が別途必要になる | Constitution本文自体の変更は不要(既にRATIFIED)。ただしDC_20260728_003の解釈・適用範囲の再整理を要する可能性がある |
| **B** | Runtime Governance Modelを正式Authorityモデルとする(MoCKA Governance Runtime → PHI-Core) | `PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`、`PHIOS_CORE_CANONICAL_DESIGN_v1.md`、`DC_20260728_003` | 根拠がRATIFIED Constitutionではなく非公式`PHI-OS構想メモ`に依拠していることが確認済み(`PHI_AUTHORITY_FLOW_ANALYSIS_v0.1.md`§2)。Constitution第1章1.1との関係を未整理のまま正式化するリスクがある | 実質的にDC_20260728_003の現状追認に近く、新規の変更は小さい。ただしConstitution本文とModel Bの関係整理が将来的に必要になる可能性が残る |
| **C** | PHI-Con/Core/HAB階層モデル(Model C)を正式Authorityモデルとして採用する | `DC-PHI-ID-001`(`DC_20260729_008`)からの構造的類推のみ。PHI-Con→PHI-Coreの統治関係を直接記す一次資料は存在しない(`PHI_AUTHORITY_MODEL_PROPOSAL_v0.1.md`§2で既報告) | 一次資料の裏付けを欠く設計仮説を正式Authorityモデルとして確定させることになり、4選択肢中Evidence-Bound原則との整合性が最も低い。将来の検証で前提が崩れた場合の手戻りリスクが最大 | 「PHI-Con→PHI-Core→PHI-HAB」という統治構造を制度上初めて確定させることになり、4選択肢中もっとも影響範囲が広い |
| **D** | Authority関係を未確定(Pending Resolution)のまま維持する | 既存資料はいずれもPending Resolutionを覆すだけの直接証拠を持たない(`PHI_AUTHORITY_FLOW_ANALYSIS_v0.1.md`§4、`PHI_AUTHORITY_MODEL_PROPOSAL_v0.1.md`§4) | 意思決定の先送りにより、将来Planner/Sequence Engine等の実装時にAuthority判断が必要になった場合、都度個別判断を要する運用負荷が残る | 変更範囲なし(現状追認)。ただし「決めないと決めた」こと自体をDecisionとして記録する必要がある |

---

## 2. 各Optionの補足

### Option A
Constitution第1章1.1の文言をそのまま制度上のAuthorityモデルとして確定させる案。RATIFIED文書を根拠にする点で4案中最も制度的な正当性が高いが、`DC_20260728_003`が既にActiveとして存在するため、両者の関係(DC_003を限定解釈するか、事実上上書きするか)を別途整理しない限り、単純な採用では新たな矛盾を残す。

### Option B
`DC_20260728_003`の枠組みをそのまま正式Authorityモデルとする案。既にHuman Gate承認済み(きむら博士、2026-07-28)であるため制度的な追認コストは低いが、その根拠が非公式資料である点はConstitution(制度上位文書)との整合性の観点で残存課題となる。

### Option C
Model Cは前回`PHI_AUTHORITY_MODEL_PROPOSAL_v0.1.md`で「Model A・Model Bいずれの直接合成でもない設計仮説」と明記した通り、一次資料による裏付けを持たない。4案の中で唯一、根拠文書欄に既存の確定Decisionを直接引用できない案である。

### Option D
「決めない」こと自体を制度上の記録として残す案。Evidence量(未解決点の多さ)から見て、現時点でもっとも一次資料と整合する選択肢である一方、実務上の判断保留が長期化するリスクを伴う。

---

## 3. 既存Decisionへの影響確認(Confirmed)

Option A〜Dのいずれを選択しても、以下は本Draftの対象外であり変更されない。
- `DC_20260728_002`(Canonical PHI-OS Core確定)
- `DC_20260728_003`(PHI-OS/MoCKA Boundary確定)
- `DC_20260729_008`(DC-PHI-ID-001、Responsibility Classification Alias採用)

Option A・Bはこれら既存Decisionの「解釈・適用範囲」に触れる可能性があるが、「変更・撤回」ではない(既存Decisionはstatus: Activeのまま維持される)。

---

## 4. Decision対象外(継続、変更なし)

- `PHI_OS_CONSTITUTION_v1.md`本文の改定
- PHI-REG-04(`phi_os_bridge.py`)のConstitution Compliance Review(別トラック、DC-PHI-ID-003候補として分離済み)
- PHI-REG-02(c)(Hub系)の最終分類

---

## Knowledge Lineage

**Document:** PHI_AUTHORITY_DECISION_DRAFT_v0.1.md
**Status:** DRAFT
**Created:** 2026-07-29
**Origin:** PHI_AUTHORITY_MODEL_PROPOSAL_v0.1.md確認後、きむら博士よりDC-PHI-ID-002 Draft(4選択肢比較)作成の指示を受け作成。
**Parent Documents:**
- PHI_AUTHORITY_MODEL_PROPOSAL_v0.1.md
- PHI_AUTHORITY_FLOW_ANALYSIS_v0.1.md
- PHI_OS_CONSTITUTION_v1.md
- DC_20260728_002、DC_20260728_003、DC_20260729_008
**Derived From:** PHI_AUTHORITY_MODEL_PROPOSAL_v0.1(Model A/B/C定義の継承元)
**Supersedes:** なし
**Reason For Creation:** DC-PHI-ID-002を裁定Decisionとして記録する前に、4選択肢(Model A/B/C/Pending Resolution)のEvidence・Risk・変更範囲を比較し、Human Gate判断の材料とするため。
**Affected Components:** PHI-REG-01、PHI-REG-02(a)(b)、DC_20260728_002、DC_20260728_003、DC_20260729_008
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。4 Option比較表・補足・既存Decision影響確認・Decision対象外を記載。Decision化・実装・リネームは無し。
