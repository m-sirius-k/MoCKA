# [採択反映レコード] Design Baseline 確立 (2026-07-15, append-only)

本レコードは append-only 追記である。以下の原本 Draft 本文(次見出し以降)は
履歴として一切改変せず保持する(本設計 Principle 3: 概念履歴の非削除に準拠)。
旧状態(Draft / 未採択 / DC 未発行)は superseded な履歴表現として残し、現行の
正式状態を本レコードで active として宣言する。

現行の正式状態 (authoritative):

- Adoption Decision: DC_20260714_005 (status: Active)
- Approved by: きむら博士 (Human Gate)
- Approved at: 2026-07-14T22:17:35Z (実行時刻)
- Document status: Design Baseline (Draft から昇格・採択済)
- Baseline 対象: 本文書 (SEMANTIC_VOCABULARY_LAYER_DESIGN_v0.2)
- 採択範囲: 責務定義 / 責務境界 / Principle 1/2/3 / Design Baseline 昇格
- 参照 Ledger: data/decisions/decision_ledger.jsonl (DC_20260714_005)
- 関連 event: E20260715_412839812a986 (CHANGE_START) /
  E20260715_457470530b547 (decision write)

注記: 下記原本の "Status: Draft / Proposal" および "DC_20260714_005 は未発行"
等の記述は、本レコード確立時点で superseded な履歴表現であり、非削除で保持する。
現行の正式状態は本レコードを正とする。
配置: 本文書は現時点 docs/internal/ に維持。docs/governance/ への配置変更は
別工程(確認後の実施候補)。

---

# Semantic Vocabulary Layer Design v0.2 (DRAFT)

Document ID: SEMANTIC_VOCABULARY_LAYER_DESIGN_v0.2
Status: Draft / Proposal
Artifact Type: Design Proposal (Human Gate 提出用 / 未採択)
Date: 2026-07-14
作成: くろこ (Claude-opus-4-8)
Authority: 未確定 (判断権限は Human Gate / きむら博士 に留保)
Adoption Decision: 未発行 (DC_20260714_005 は現時点で Decision Ledger に存在しない)
配置: docs/internal/ (GitHub 非公開領域 / 制度的決定 E20260616_094)

## 0. 本文書の位置づけと制約 (最重要)

本文書は Semantic Vocabulary Layer の設計候補を Human Gate 審査可能な状態に
整理した Draft (Proposal) である。以下を厳守する。

- 本文書は Design Baseline ではない。Design Baseline 宣言は本文書では行わない。
- DC_20260714_005 は未発行のままとする。本文書の存在は採択を意味しない。
- Decision Ledger への書込は行わない。
- Seal は行わない。
- Registry (KN-004 等) の更新は行わない。
- 既存成果物 (Contract / Registry / Decision / Naming Vocabulary) を一切変更しない。
- 採択 / 却下 / 保留の判断は Human Gate (きむら博士) に留保する。AI は判断しない。

先行 READ ONLY 監査 (2026-07-14) の確認済み事実:

- DC_20260714_005 は Decision Ledger に存在しない (最新正式 Decision は DC_20260714_004)。
- 同名の設計文書は正本環境に存在しなかった (本 Draft が初出)。
- 既存 Contract / Registry / Decision への非破壊性は維持されている。
- 直近の関連正式成果物は docs/governance/GOVERNANCE_NAMING_VOCABULARY_v1.md
  (DC_20260714_004, Active) である。

## 1. Semantic Vocabulary Layer の目的

MoCKA が「概念 (concept)」そのものを一次データとして扱うための型を定義する層。
これまで MoCKA は Artifact (ファイル / 記録 / 契約) と Decision (人間判断) を
正本として扱ってきたが、それらが指し示す「意味 (meaning)」「概念の同一性
(identity)」「概念の履歴 (naming history / lifecycle)」は制度化されていない。

本層の目的は次を制度上の一次データとして保持することにある。

- Concept identity (概念の同一性)
- Definition (定義本文)
- Meaning relation (概念間の意味関係)
- Naming history (命名履歴)
- Concept lifecycle (概念の生成 / 昇格 / 置換 / 失効)
- Provenance (由来 / どの Decision / Artifact に紐づくか)

本層が保持しないもの (責務外):

- Artifact 構造
- Git 状態
- 実ファイル配置
- Execution state (実行時状態)

目的の核心は「名前を決めること」ではなく「MoCKA が概念を扱うための型
(schema) を定義すること」である。命名工程 (Naming) は本層が扱う概念操作の
一部 (naming history) にすぎない。

## 2. Naming Vocabulary Layer との責務境界

直近成果物 GOVERNANCE_NAMING_VOCABULARY_v1 (DC_20260714_004) との関係を
明確化する。両者は別レイヤーであり、責務が異なる。

| 観点 | Naming Vocabulary Layer (既存 / DC_004) | Semantic Vocabulary Layer (本 Draft) |
|------|------------------------------------------|--------------------------------------|
| 問い | 概念を「何と呼ぶか」(name assignment) | 概念が「何であるか」(identity / definition) |
| 対象 | Governance 三層命名 (Anchor Principle / DIF / GL7) の名称固定 | 概念一般の identity / definition / relation / lifecycle |
| 方式 | addition-only / annotation-by-reference | schema 定義 + append-only concept graph |
| 範囲 | Governance 命名に限定された具体記録 | 概念モデルの型 (汎用) |

境界の原則:

- Naming Vocabulary Layer は「名称の付与記録」であり、Semantic Vocabulary
  Layer から見れば naming history の 1 インスタンス (具体レコード) に相当する。
- Semantic Vocabulary Layer は Naming Vocabulary の内容を複製しない。参照
  (reference) で結ぶことを想定する (実装は本 Draft の範囲外)。
- 既存 GOVERNANCE_NAMING_VOCABULARY_v1 は本 Draft により一切変更されない。

## 3. Concept Identity 定義 (設計候補)

各概念は安定した識別子 (concept_id) を持ち、名称変更・定義更新をまたいで
同一性を保つ。名称は identity ではない (名称は変わりうるが concept_id は不変)。

概念レコードの候補フィールド (Draft, 未確定):

- concept_id       : 不変の一意識別子
- canonical_name   : 現行の正式名称 (naming history の active 要素を指す)
- concept_layer    : 意味階層 (Philosophy / Framework / Technical / Policy 等)
- status           : lifecycle 状態 (proposed / active / superseded / obsolete)
- schema_version   : 本層スキーマのバージョン
- provenance       : 由来 (related decisions / artifacts)

注記: 上記は候補であり、フィールド追加・変更は制度変更 (Human Gate 対象) として
扱う (7 章 Principle 1 参照)。

## 4. Definition 管理方式 (設計候補)

- 定義本文 (definition body) は概念に紐づけて保持する。
- 定義の更新は上書き (overwrite) を禁止する。旧定義は superseded として残し、
  新定義を active として append する (append-only)。
- 履歴は次のように保持する (概念履歴の非削除原則, 7 章 Principle 3)。

      old definition  -> status: superseded (保持)
      new definition  -> status: active     (追加)

- 各定義バージョンは provenance (紐づく Decision / Artifact) を持つ。
- 定義本文の正本保持は本層の責務であり、KN-004 Registry には持たせない
  (6 章参照)。

## 5. Meaning Relation 管理方式 (設計候補)

概念間の意味関係を relation として保持する。関係は型 (relation_type) を持つ。

階層関係 (hierarchical) の基本方向:

      Philosophy
         |  derives
         v
      Framework
         |  derives
         v
      Technical
         |  derives
         v
      Policy

階層関係の禁止事項:

- 下位概念による上位概念の supersede を禁止する。
- 階層 relation の循環 (cycle) を禁止する。
- 自己参照 (self-reference) を禁止する。

ただし、非階層 relation (例: related-to, refines, instance-of 等) については
将来拡張余地を残す (本 Draft では型を確定しない)。

relation_type の追加、および階層方向の変更は制度変更 (Human Gate 対象) とする。

## 6. Existing Contract / Registry との接続点 (設計候補)

責務分離を次のとおり保つ (単一方向依存を原則とする)。

Semantic Vocabulary Layer が保持する:
- Concept identity / Definition / Meaning relation / Naming history /
  Concept lifecycle / Provenance

KN-004 Registry が保持する (Semantic 側に持たせない):
- Artifact 存在管理 / 構造関係 / Reference / Classification / Record lifecycle

KN-004 Registry に禁止する:
- Concept definition の格納
- 意味関係の graph 化
- Vocabulary 本文の保持

Decision Ledger が保持する:
- Human 判断 / 採択理由 / Governance decision

接続方式の候補 (Draft, 未確定):

- KN-004 の classification が Semantic Layer の concept_id (vocabulary_id) を
  参照する片方向依存とする (KN-004 -> Semantic 参照。Semantic は KN-004 に
  依存しない)。
- 具体的な参照方式 / taxonomy 統制 / 片方向依存の検証は別 Decision
  (後述 Option B) で確定する。本 Draft では接続点の存在と方向のみ提示する。

## 7. GL7 Validation との関係 (設計候補)

GL7 (Governance Layer 7) の canonical な役割は Execution Governance
(DC_20260714_003 Judgment A, 保持) であり、Artifact の実行時 / 昇格時強制を担う。
Semantic Vocabulary Layer の整合性検証はこれとは別の関心事である。

不変原則 (本 Draft が設計上の固定点として提示するもの / 採択は Human Gate):

Principle 1 (Semantic Model 変更は Human Gate 対象):
- concept_layer の追加
- relation_type の追加
- lifecycle 状態の変更
- schema_version の更新
これらは単なるデータ追加ではなく制度変更として扱う。

Principle 2 (意味階層の方向性保持):
- 基本方向 Philosophy -> Framework -> Technical -> Policy を保持する。
- 下位による上位の supersede / 循環 / 自己参照を禁止する。
- 非階層 relation は将来拡張余地を残す。

Principle 3 (概念履歴は削除しない):
- 旧定義の overwrite を禁止する。
- old (superseded) を保持しつつ new (active) を append する (append-only)。

GL7 との境界:

- GL7 = Artifact / Execution の governance (実行時強制)。
- Semantic Vocabulary Validator (将来候補, Option A) = concept graph の整合性
  検証 (schema validation / relation graph 検証 / cycle detection /
  provenance check)。
- 両者は別の validator である。GL7 と Semantic Validator の統合有無は
  別 Human Gate 判断とする。本 Draft では統合を前提としない。

## 8. Non-Goals (対象外範囲)

本 Draft の時点で、次はいずれも実施しない / 対象外とする。

- 実装開始 (storage / API / MCP tool) : NO
- KN-004 Registry への投入 : NO
- schema 変更 (KN-004 / 既存) : NO
- Validator の作成 : NO
- migration の開始 : NO
- Seal 境界の変更 : NO
- Decision Ledger への書込 : NO
- Design Baseline 宣言 : NO
- DC_20260714_005 の発行 : NO
- 既存概念の supersede : NO (append-only を維持)
- 既存 Contract / Registry / Decision / Naming Vocabulary の変更 : NO

理由: 現在の成果は「設計候補 (Draft)」であり、「設計境界の確定」でも
「実装成果」でもないため。

## 9. 将来的な Human Gate 判定項目

本 Draft を材料として、Human Gate (きむら博士) が判断しうる事項を列挙する
(いずれも本 Draft では判断しない)。

DC_20260714_005 に関する判断:
- 本 Draft を Design Baseline へ昇格するか否か。
- 昇格する場合、DC_20260714_005 を発行するか、別 ID とするか。

Principle 群の採否:
- Principle 1 (Semantic Model 変更 = Human Gate 対象) の採否。
- Principle 2 (意味階層方向 Philosophy -> Framework -> Technical -> Policy) の採否。
- Principle 3 (概念履歴 append-only / 削除禁止) の採否。

後続 Decision として切り出す候補 (それぞれ別 Human Gate 判断):

- Option A: Semantic Vocabulary Validator 設計
  (JSON Schema validation / relation graph 検証 / cycle detection /
  provenance check)。
- Option B: KN-004 classification 接続仕様
  (vocabulary_id 参照方式 / taxonomy 統制 / 片方向依存確認)。
- Option C: Semantic Vocabulary 実装計画
  (storage / API / MCP tool 境界 / migration strategy)。

配置に関する判断:
- 本 Draft を docs/internal/ (GitHub 非公開) に留めるか、docs/governance/
  (公開 / sync_watch 自動 push 対象) へ移すか。

## 10. 現状サマリ (Draft 時点)

    Semantic Vocabulary Layer
    Phase        : Draft Preparation (Human Gate 提出用)
    Authority    : 未確定 (Human Gate 留保)
    Adoption     : 未採択
    DC_20260714_005 : 未発行
    Implementation  : 未着手 (Frozen)
    Mutation        : 0 (既存正本非破壊)
    Registry (KN-004): 無変更
    Decision Ledger : 無変更
    Seal            : 未実行
    Human Gate      : 維持 (判断権限 = きむら博士)
