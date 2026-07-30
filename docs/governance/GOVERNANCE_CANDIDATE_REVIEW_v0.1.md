# Governance Candidate Review v0.1

Status: 分類レビューのみ（制度化そのものは行わない。昇格判断はHuman Gate）
Date: 2026-07-30
記録者: 執行官Claude（くろこ、Cloud session）
関連: DC_20260728_006 / DC_20260729_001 / DC_20260730_009 / DC_20260730_010

本文書は、本セッション（Cloud session、branch claude/genesis-phase-integration-policy-ftib7s）で
作成した文書群をレビューし、恒久制度化すべきもの・プロジェクト固有の一時文書・今回限りのインシデント
対応の3分類に整理する。分類は提案であり、実際の制度昇格はHuman Gate（きむら博士）の裁定による。

---

## 1. レビュー対象

本セッションで作成した10文書。作成順に列挙する。

```
G1. docs/governance/GENESIS_PHASE_INVESTIGATION_POLICY_v1.0.md
G2. docs/governance/GENESIS_PHASE_INVESTIGATION_v0.1.md
A1. docs/audits/OPTION_C_EVIDENCE_AVAILABILITY_AUDIT_v0.1.md
A2. docs/audits/OPTION_C_REQUIRED_EVIDENCE_MANIFEST_v0.1.md
A3. docs/audits/REPOSITORY_DIVERGENCE_REPORT_v0.1.md
A4. docs/audits/OPTION_C_AUDIT_RESUMPTION_PLAN_v0.1.md
B1. docs/audits/EVIDENCE_SYNCHRONIZATION_STRATEGY_v0.1.md
B2. docs/audits/EVIDENCE_SOURCE_PRIORITY_POLICY_v0.1.md
B3. docs/audits/REPOSITORY_DIVERGENCE_DETECTION_PROCEDURE_v0.1.md
B4. docs/audits/AUDIT_CAPABILITY_MATRIX_v0.1.md
```

## 2. 分類の定義

本レビューで用いる3分類を、判定基準とともに定義する。

- **恒久制度化候補（Permanent Institution Candidate）**: 対象が本件（Option C監査・Genesis Phase調査）
  に限定されず、将来の別案件でも同じ形で適用できるもの。適用が義務的になるため、Human Gate承認と
  Decision Ledger登録を要する。
- **プロジェクト固有の一時文書（Project-Scoped Working Document）**: 特定の案件・調査に紐づき、その
  案件が完了すれば役割を終えるもの。記録としては保持するが、制度としての義務は生じない。
- **今回限りのインシデント対応（One-Time Incident Response）**: 特定の事象（今回はCloud/Local乖離の
  発覚）を記録するためのもので、事象そのものが解消すれば内容が陳腐化するもの。

## 3. 分類結果

### 3.1 恒久制度化候補

| 文書 | 判定理由 | 昇格に必要な手続き |
|---|---|---|
| G1. GENESIS_PHASE_INVESTIGATION_POLICY_v1.0.md | Statement単位Classification（Confirmed/Source/Founder Narrative/Hypothesis/Unknown/Rejected）は、Genesis Phase調査に限らず、歴史的再構成を伴うあらゆる調査に適用できる。禁止事項（逆算による一本道の歴史生成、後知恵のConfirmed扱い、Unknownの穴埋め）も同様に一般性がある | 既にDC_20260728_006として登録済み。ただしDecision本文は（Genesis Phase調査の統合方針）としてスコープされており、Classification Ruleを他調査へ一般化して適用するには、スコープ拡張の追加Decisionを要する |
| B3. REPOSITORY_DIVERGENCE_DETECTION_PROCEDURE_v0.1.md | 5段階の確認手順は、Option C監査に限らず、継続作業を装った指示を受けたすべての場面で適用できる。DC_20260730_009（未検証文脈の隔離ルール）が定めた確認順序を、実行可能なコマンドレベルへ具体化したものであり、既存制度の実装に相当する | Human Gate承認 + Decision Ledger登録。DC_20260730_009との関係（具体化・実装である旨）を明記すること |
| B2. EVIDENCE_SOURCE_PRIORITY_POLICY_v0.1.md | 証拠源の優先順位は、あらゆる監査・裁定の基礎となる。ただし現状は提案段階であり、既存DC_20260730_009との統合方法が未確定 | **本セッションでは登録しない（きむら博士明示指示）。** DC_PROPOSAL_EVIDENCE_SOURCE_POLICY_v0.1.mdとして提案書化し、Human Gate審査を経た場合のみ昇格 |

### 3.2 プロジェクト固有の一時文書

| 文書 | 判定理由 | 扱い |
|---|---|---|
| G2. GENESIS_PHASE_INVESTIGATION_v0.1.md | Genesis Phase調査そのものの成果物（Evidence/Timeline/Decisions/Unknown/Interpretation Boundaryの5区分）。調査が進むにつれ内容が更新される作業文書であり、制度ではない | 調査進行に伴い改訂。TODO化して継続（本セッションではTODO_457相当の登録がMCP側502により未完了、後述） |
| A2. OPTION_C_REQUIRED_EVIDENCE_MANIFEST_v0.1.md | Option C監査Task 1-4に必要な23文書の一覧。当該監査が完了すれば役割を終える | Task 1-4完了時にCLOSED扱いとする |
| A4. OPTION_C_AUDIT_RESUMPTION_PLAN_v0.1.md | Option C監査の再開順序・完了条件。同上 | 同上 |
| B1. EVIDENCE_SYNCHRONIZATION_STRATEGY_v0.1.md | 同期戦略そのものは一般性を持つが、現状の記述はCloud/Local/MCPという本件固有の3環境構成を前提としている。他プロジェクトへの適用には抽象化が必要（REUSABLE_GOVERNANCE_PATTERNS_v0.1.md参照） | 当面はプロジェクト固有として保持。抽象化後に恒久制度化を再検討 |

### 3.3 今回限りのインシデント対応

| 文書 | 判定理由 | 扱い |
|---|---|---|
| A1. OPTION_C_EVIDENCE_AVAILABILITY_AUDIT_v0.1.md | 2026-07-30時点でCloud checkoutに23文書が不在という、特定時点の観測結果の記録。同期が完了すれば記述内容は陳腐化する | 記録として永久保持（MoCKAは全データ永久保持・DELETE禁止）。ただし将来参照時は（2026-07-30時点の観測）である旨に注意 |
| A3. REPOSITORY_DIVERGENCE_REPORT_v0.1.md | 同上。3環境の差異という特定時点のスナップショット | 同上 |
| B4. AUDIT_CAPABILITY_MATRIX_v0.1.md | 環境ごとの監査可否は、環境構成が変われば変化する（実際、本セッション中にpush権限が403から可へ変化した）。恒久的な制度というより、現時点の能力記録 | 環境変更時に更新。ただしマトリクスという**形式**自体は再利用可能（3.4参照） |

### 3.4 分類が単純でないもの

以下の2件は、内容と形式で分類が分かれるため、注記する。

- **B4. AUDIT_CAPABILITY_MATRIX_v0.1.md**: 記載内容（どの環境で何ができるか）は時点依存でインシデント
  対応に近い。しかし、監査項目 x 環境のマトリクスで能力を可視化するという**形式**は、他プロジェクトでも
  そのまま使える。したがって、内容は3.3、形式はREUSABLE_GOVERNANCE_PATTERNS_v0.1.mdでパターンとして
  抽出する。
- **B1. EVIDENCE_SYNCHRONIZATION_STRATEGY_v0.1.md**: 同期完了判定・失敗時対応の考え方は一般性を持つが、
  現記述は3環境構成に密結合している。抽象化してから恒久制度化を検討するのが安全と判断した。

## 4. 未完了事項

本セッション中、以下がMCPサーバー側の一時的な障害（502 Bad Gateway、複数分にわたり継続）により
未完了のまま残っている。

- TODO_457（Genesis Phase Investigation 実データ収集）の登録。`mocka_add_todo`が502で失敗した。
  Genesis Phase調査（G2）を継続するには、このTODO登録が必要である。

上記は本レビューの対象外だが、G2をプロジェクト固有の一時文書として継続する前提が未成立であることを
明示するために記載する。

## 5. Human Gateへの確認事項

1. 3.1の恒久制度化候補3件のうち、B3（Divergence Detection Procedure）をDecision Ledgerへ登録するか。
2. G1（Genesis Phase Classification Rule）のスコープを、Genesis Phase調査以外の歴史的再構成調査へ
   拡張するか。
3. B2（Evidence Source Priority Policy）については、本セッションでは登録しないという指示を受領済み。
   提案書（DC_PROPOSAL_EVIDENCE_SOURCE_POLICY_v0.1.md）の内容で審査を進めてよいか。

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-07-30 | 0.1 | 初版。監査基盤整備完了後の制度化候補整理指示に基づき作成。 |
