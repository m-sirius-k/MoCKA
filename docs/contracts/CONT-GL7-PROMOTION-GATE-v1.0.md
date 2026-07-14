# GL7 Promotion Gate Contract v1.0

Document ID: CONT-GL7-PROMOTION-GATE-v1.0
Status: Canonical
Artifact Stage: Canonical (Canonicalized 2026-07-14 under Human Gate GO)
Date: 2026-07-14
作成: くろこ(Claude-opus-4-8)
Authority: Human Gate Approved (Canonical 化 GO / きむら博士)

本文書は Human Gate GO により Canonical 化された Contract である。正式化の根拠
Decision は DC_20260714_003(Decision Ledger, Active)。Seal・Commit/Push は Human
Gate 再確認後に別途実施する(本工程では未実施)。

---

## 1. Contract Identity

- Document ID: CONT-GL7-PROMOTION-GATE-v1.0
- Status: Canonical
- Contract Name: GL7 Promotion Gate Contract
- Supersedes: なし(新規)
- Related Design Record: docs/architecture/MAP_LAB_GL7_BOUNDARY_DESIGN_v0.2.md
  (NON-CANONICAL 設計記録。本 Contract はその Validation Gate Policy / Default
  Deny Policy を正式契約として固定する上位工程)

## 2. Purpose

MAP-LAB 領域から GL7 Core / Root へ成果物を昇格(promotion)する際の認可基準・
検証基準を固定する。昇格の可否を制御する境界(Promotion Gate)の要件を契約として
明文化し、無断書込・検証未通過昇格・境界迂回を制度的に排除することを目的とする。

## 3. Responsibility Boundary

- Canonical GL7 definition: GL7 = Execution Governance(正本定義)。
- "GL7 Core Integrity Layer" は正本定義ではなく Policy View として扱う。GL7 scope を
  参照する政策的視点であり、GL7 の canonical definition を置換しない。
- Promotion Gate は GL7 保護のための昇格境界制御層(admission / promotion control)。
  Module 品質保証(Module Validation)とは責務軸が異なる独立層である。
- 対象オブジェクトの区別:
  - Promotion Gate の対象 = MAP-LAB 動的成果物(observation / generation /
    regenerable output)。
  - Module Validation の対象 = Module(module_id / version)。
  両者を同一責務として混同しない。

## 4. Evidence Input

- 既存 ValidationRecord(MODULE_VALIDATION_ENGINE_v1 Section 6 /
  core_kernel/governance/contracts/validation_contract.py)を Promotion Gate の
  入力証跡(evidence input)として参照する。
- ValidationRecord は証拠(evidence)であり、昇格承認(promotion approval)そのもの
  ではない。VALID な ValidationRecord の存在は Promotion Gate の Approve を自動的に
  意味しない。
- 参照関係の性質: Promotion Gate が ValidationRecord を入力として消費する consumer
  関係であり、Promotion Gate が Module Validation Engine の拡張(identity)である
  ことを意味しない。

## 5. Prohibited Operations

- MAP-LAB からの無断 Core 書込禁止(uncontrolled write to GL7 Core / Root)。
- Validation を経由しない昇格禁止(promotion without ValidationRecord evidence)。
- Promotion Gate を経由しない GL7 Root 操作禁止(bypass of the Promotion Gate)。
- 上記のいずれかに該当する昇格・反映・書込はすべて拒否される(Default Deny)。

## 6. Canonicalization Conditions

成果物の GL7 Core / Root への昇格・正本化は、以下をすべて充足する場合に限り成立する。

- Promotion Gate 基準充足(Promotion Gate Approve)。
- Human Gate 明示承認(explicit human approval。暗黙・自動フローによる承認を認めない)。
- 必要な登録判断完了(Contract 登録判断等、当該工程に必要な判断の完了)。

いずれかを欠く昇格・正本化は成立しない。

## 7. Human Gate Connection

Promotion Gate の判定および後続工程は、以下の Human Gate 判断点に接続する。

- Approve / Revise(Promotion Gate 判定。Approve のみ Core 反映可、Revise は
  MAP-LAB 側で再精製し再提出)。
- Contract 登録判断(本 Contract の登録要否・正本化の可否)。
- Commit 判断(制度的 git 記録の実施可否)。
- Push 判断(遠隔反映の実施可否)。
- Canonical 化判断(Status の Proposed から Canonical への遷移可否)。

これらはいずれも人間専権の判断点であり、AI(くろこ)が自動で成立させない。

## 8. Decision References

本 Contract の根拠 Decision は **DC_20260714_003**(Decision Ledger, status: Active,
approved_by: きむら博士 Human Gate)。同 Decision は以下3判断を単一レコードに包含する。

- Judgment A(DC_20260714_003): GL7 canonical definition = Execution Governance を維持。
  "GL7 Core Integrity Layer" は Policy View として保持。
- Judgment B-1:A(DC_20260714_003): "Validation Gate Policy" を "Promotion Gate Policy"
  へ名称整理。MAP-LAB 成果物の Core 昇格は Promotion Gate 通過必須。新規責務であり
  Module Validation の拡張ではない。
- Judgment B-2:A(DC_20260714_003): ValidationRecord は Promotion Gate の入力証跡として
  参照。証拠であり昇格承認そのものではない。

関連 Event: E20260714_42167102612ba(DECISION_MADE)/ E20260714_463550098ea9e
(decision_write)。前提の GL7 encoding blocker 解消証跡: E20260714_4006395644544 /
docs/audits/GL7_ENCODING_REMEDIATION_EVIDENCE_20260714.md。
