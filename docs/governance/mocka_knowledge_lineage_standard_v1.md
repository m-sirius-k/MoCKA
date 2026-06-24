# MoCKA Knowledge Lineage Standard v1.0

## 第1章 目的

本標準は、MoCKA内の重要文書について、作成経緯・依存関係・影響範囲・改訂理由を追跡可能にすることを目的とする。

Git履歴は技術的変更履歴を保持するが、本標準は制度的・知識的履歴を保持する。

すべての重要文書は、本文とは独立した「Knowledge Lineage」セクションを持つことが望ましい。

---

## 第2章 適用対象

必須対象：

* docs/spec/
* docs/governance/
* docs/audits/

推奨対象：

* docs/experimental/
* 長期運用対象文書

除外：

* 一時メモ
* 作業途中の草案
* 個人メモ

---

## 第3章 Knowledge Lineage セクション

文書末尾に以下を配置する。

### Knowledge Lineage

Document:
<現在の文書名>

Status:
Draft / Review / Frozen / Superseded

Created:
YYYY-MM-DD

Last Reviewed:
YYYY-MM-DD

---

## 第4章 系譜情報

Origin:

この文書が最初に生まれた背景。

例：

Origin:
Phase D Execution Architecture検討

---

Parent Documents:

直接参照した上位文書。

例：

Parent Documents:

* moCKA_spec_v1.0.2-rc.md
* mocka_human_gate_v1.md

---

Derived From:

派生元となる文書または決定。

例：

Derived From:
mocka-phaseC-design-v1

---

Supersedes:

置換対象が存在する場合のみ記載。

例：

Supersedes:
mocka_execution_contract_v0.9

---

## 第5章 作成理由

Reason For Creation:

なぜこの文書が必要になったか。

例：

Reason For Creation:
Execution責務を明確化するため。

---

## 第6章 影響範囲

Affected Components:

影響対象を列挙する。

例：

Affected Components:

* IR Layer
* Human Gate
* Execution Layer

---

Related Documents:

関連文書を列挙する。

例：

Related Documents:

* MOCKA_PHASE_D_EXECUTION_FLOW_v1.md
* MOCKA_PHASE_D_EXECUTION_CORE_v1.md

---

## 第7章 改訂履歴

Revision History:

Revision:
R1

Date:
YYYY-MM-DD

Reason:
変更理由

Change:
変更内容

Impact:
影響範囲

---

Revision:
R2

Date:
YYYY-MM-DD

Reason:
変更理由

Change:
変更内容

Impact:
影響範囲

---

## 第8章 運用原則

Knowledge Lineageは単なる履歴ではない。

以下を追跡できることを目的とする。

* どこから来たか
* なぜ作られたか
* 何を変えたか
* 何へ影響するか
* どこと関係するか

文書単体を読んでも、その制度的位置付けと知識系譜が理解できる状態を維持する。
