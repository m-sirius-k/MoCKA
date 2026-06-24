# MoCKA Lineage Governance — Finalization v1.0

**Status:** DECIDED — 4論点裁定済み
**基準文書:** [[MOCKA_LINEAGE_GOVERNANCE_AUDIT_v1]]
**裁定者:** 博士
**裁定日:** 2026-06-24

---

## 論点1：適用方針

裁定：**採用**

理由：監査（MOCKA_LINEAGE_GOVERNANCE_AUDIT_v1 第1部）でLineage欠落による実害（app.py `.bak`系列7種の出自不明化、PHI-OS同名別実体問題、Human Gate文書過多・コード過少の非対称構造）が確認されたため、Knowledge LineageをMoCKA標準として正式採用する。

## 論点2：遡及範囲

裁定：**段階適用**（一括遡及は避ける）

優先順位：

| Level | 対象 |
|---|---|
| Level 1 | Human Gate Finalization / Decision Draft / Readiness Review |
| Level 2 | Phase D文書群 |
| Level 3 | Phase C文書群 |
| Level 4 | Event Integrity Framework関連 |
| Level 5 | app.py台帳 |

## 論点3：制定形態

裁定：**Governance Standard**

扱い：`docs/governance/` 配下の正式標準とする。単なる運用メモではなく制度文書として位置づける（[[mocka_knowledge_lineage_standard_v1]]はこの裁定により正式標準として確定する）。

## 論点4：app.py等への適用方式

裁定：**直接埋め込みではなく外部台帳方式**

形式：

```
docs/lineage/
  app_py_lineage.md
  human_gate_lineage.md
  phi_os_lineage.md
```

理由：app.pyは今後Code Binding対象であり、コードへの大量のLineageヘッダ埋め込みはコードレビュー・差分監査・将来のリファクタを重くする。外部台帳方式により、コア資産そのものへの変更（書込ポリシー上Human Gate承認が必要な領域）を経ずにLineage記録を進められる。

---

## 推奨裁定（確定）

```
適用方針:       採用
遡及範囲:       段階適用
制定形態:       Governance Standard
app.py適用:     外部Lineage台帳方式
```

---

## 次の監査テーマの指定

**PHI-OS Identity Audit（PHI-OS A / PHI-OS B 同名別実体問題の整理）を最優先とする。**

理由（博士提示）：
- `.bak`問題は過去の整理（archive-cleanupブランチ等）で対応済みであり、過去の問題に留まる。
- 一方、PHI-OS A（MoCKA本体 `phi_os/`）とPHI-OS B（`PlanningCaliber/workshop/phi-os/`）の同名別実体問題は、今後の設計そのものに影響する未解決の現在進行中の問題である。
- よってCode Bindingより先に、PHI-OS Identity Auditを実施する優先順位とする。

**本文書では PHI-OS Identity Audit そのものは未着手。** 着手の指示は別途必要。

---

## Knowledge Lineage

Document:
MOCKA_LINEAGE_GOVERNANCE_FINALIZATION_v1.md

Status:
Frozen

Created:
2026-06-24

Last Reviewed:
2026-06-24

Origin:
MOCKA_LINEAGE_GOVERNANCE_AUDIT_v1が提示した4論点に対する博士裁定を記録するために作成。

Parent Documents:

* MOCKA_LINEAGE_GOVERNANCE_AUDIT_v1.md
* mocka_knowledge_lineage_standard_v1.md

Derived From:
MOCKA_LINEAGE_GOVERNANCE_AUDIT_v1 第6部（最終提言・博士が裁定すべき4論点）

Supersedes:
（無し）

Reason For Creation:
4論点（適用方針/遡及範囲/制定形態/app.py適用方式）への博士裁定、および次監査テーマ（PHI-OS Identity Audit）の指定を制度的に記録するため。

Affected Components:

* mocka_knowledge_lineage_standard_v1（正式標準として確定）
* docs/lineage/（新設予定、外部台帳格納先）
* app.py
* phi_os（PHI-OS A/B同名別実体問題、次監査対象）

Related Documents:

* MOCKA_LINEAGE_GOVERNANCE_AUDIT_v1.md
* mocka_knowledge_lineage_standard_v1.md
* MOCKA_CODE_BINDING_FINAL_REVIEW_v1.md

Revision History:

Revision:
R1

Date:
2026-06-24

Reason:
新規作成

Change:
博士による4論点裁定の記録、次監査テーマ(PHI-OS Identity Audit)の指定

Impact:
Knowledge Lineage StandardがMoCKA正式Governance Standardとして確定。遡及適用はLevel1から段階的に実施可能な状態になった（実施自体は別途指示が必要）。PHI-OS Identity Auditが次の優先監査として確定したが未着手。
