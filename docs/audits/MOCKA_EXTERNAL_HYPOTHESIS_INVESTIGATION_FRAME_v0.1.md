# MOCKA JARVIS停止仮説 — 外部証拠調査フレーム v0.1

**文書番号:** MOCKA-EXT-HYP-001
**作成日:** 2026-08-19
**著者:** くろこ(WEB調査部門)
**状態:** INVESTIGATION FRAME(証拠収集に先立つ調査戦略文書)
**分類:** READ-ONLY Investigation(PC内部データは使用しない)

---

## 0. 本文書の目的と制約

### 0.1 制度上の位置づけ

本文書はユーザー指示「くろこWEB指示書」(2026-08-19)に基づき、以下の中心仮説を検証するための外部証拠調査戦略を提示する。

**中心仮説:**
```
MoCKA内部で以前から存在していた
「条件・境界・権限の未確定」
    ↓
JARVIS実装前に問題が顕在化
    ↓
実装を進めるのではなく停止
    ↓
Boundary / Governance整理
```

### 0.2 調査スコープの厳格な制限

**使用可能な証拠:**
- 公開GitHub(m-sirius-k/MoCKA commit履歴、タグ)
- 公開ドキュメント(docs/配下のmarkdown、pdf等)
- 公開Zenodo/arXiv等の学術記録
- 外部で公開されている研究論文・技術文書
- 企業公開声明(Microsoft等)

**使用禁止:**
- MoCKA内部のEvent Ledger
- Decision Ledger
- 非公開メモ
- PC内部計測データ

本調査は「外部からMoCKAを観察したら何が見えるか」という観点のみを取る。

### 0.3 検証形式

| 形式 | 定義 |
|---|---|
| **EXTERNAL FACT** | 公開記録で直接確認できる事実(commit日時、公開ドキュメント内容、論文出版日等) |
| **TEMPORAL ALIGNMENT** | MOCKA内部時系列とExternal Factの時間的一致 |
| **CONCEPTUAL CONVERGENCE** | 概念上の収束(同じ問題を両者が言及しているか) |
| **DIRECT LINK** | MoCKAまたは博士との直接的言及・引用・関係 |
| **CAUSALITY** | 外部情報がJARVIS停止を引き起こした証拠 |

**重要:** 本調査ではCAUSALITYを追求しない。あるのはTEMPORAL ALIGNMENTとCONCEPTUAL CONVERGENCEのみ。

---

## 1. 調査対象と時間軸

### 1.1 調査対象概念

以下の10個の概念について、外部でいつ・どのように形成されたかを調査する。

| # | 概念 | MoCKA側での言及文書 |
|---|---|---|
| 1 | AI authority boundary | JARVIS_CONSTITUTION_DRAFT.md §3、PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md §5 |
| 2 | AI governance boundary | 同上 |
| 3 | human authority | JARVIS_CONSTITUTION_DRAFT.md §2.2 |
| 4 | human-in-the-loop | PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md §5(Human Gate) |
| 5 | authorization boundary | PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md §5.2 |
| 6 | governed capability | PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md §5 / JARVIS_CONSTITUTION_DRAFT.md §3.1-3.2 |
| 7 | admissibility | PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md §5.1(Verification段階) |
| 8 | approval conditions | PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md §5(Human Gate段階) |
| 9 | agent permissions | JARVIS_CONSTITUTION_DRAFT.md §3 |
| 10 | governance before execution | PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md §3(Verification→Human Gate→Execution) |

### 1.2 時間軸

**MoCKA内部での主要イベント（公開記録に基づく）:**

| 日時 | イベント | 公開証拠 |
|---|---|---|
| 2026-06-01 | PHI-OS Milestone計画段階 | MOCKA_OVERVIEW.json session_history |
| 2026-07-25 | PHI-OS Constitution v1(RATIFIED) | PHI_OS_CONSTITUTION_v1.md 推定 |
| 2026-07-29 | DC_20260729_008承認(HAB-D Active) | JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md §3.2 |
| 2026-08-04 | JARVIS Constitution Draft作成 | JARVIS_CONSTITUTION_DRAFT.md |
| 2026-08-04 | JARVIS Human Gate Decision Package作成 | JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md |
| 2026-08-18 | HG-J03 Evidence Complete / Governance Asset Revaluation | essence CHANGE_DONE記録 |
| 2026-08-19 | WEB Investigation Order | 本文書 |

**外部での主要イベント（既知）:**

| 日時 | イベント | 出典 |
|---|---|---|
| 2026-03 | arXiv:2603.14805 投稿(推定) | ユーザー指示により既知 |
| 2026-04 | arXiv:2604.08059 投稿(推定) | ユーザー指示により既知 |
| 2026-06 | Microsoft Build 2026 | ユーザー指示により既知 |
| 2026-06 | Ravi Shankar NRK関連資料 | ユーザー指示により既知 |

**調査対象期間:** 2026-03 〜 2026-08（MoCKA内部の「制度整備」とExternal事象の時間的対応を調査）

---

## 2. 重要な問い

### 2.1 主要問い

**「2026年3月から8月にかけて、AI capabilityの実装可能性と、authority/governanceの許可可能性を分離して考える動きが外部でも形成されていたか」**

この問いに答えるため、以下の部分問いを立てる。

### 2.2 部分問い

| ID | 問い | 調査対象 |
|---|---|---|
| Q1 | 「何ができるか」(capability)と「何をさせてよいか」(authority)を分離する考え方は、いつ頃から外部で明示化されたか | academic論文、業界文書 |
| Q2 | "Governance before Execution"という考え方は、MoCKA外で同時期に出現しているか | 同上 |
| Q3 | "Human-in-the-loop"の概念のうち「最終判断は人間が下す」という部分は、いつ頃からacademicに扱われ始めたか | 同上 |
| Q4 | "Authority Boundary"という明示的な概念は、何時から出現しているか | 同上 |
| Q5 | arXiv:2603.14805 / 2604.08059 / 2606.22528の内容は、「capability vs authority」の分離に言及しているか | 指定論文の内容検査 |
| Q6 | Microsoft Build 2026で「AI Governance」「AI Authority」というキーワードが扱われた時期は何月か | MS Build記録 |
| Q7 | Ravi Shankar氏のNRK関連資料で「Four Kinds of Decay」と「Proof Does Not Decay With Time」という概念が出現した時期は | 同上 |
| Q8 | MoCKA内部で「権限・境界・許可条件」が「未確定」として顕在化した時期は | 公開ドキュメント・commit履歴 |

---

## 3. 調査戦略

### 3.1 Phase A: MoCKA公開記録の時系列整理

**目標:** MoCKAの公開記録から「governance boundary」と「capability boundary」の分離思想が明示化された順序と時期を特定する。

**調査対象:**
- PHI_SEQUENCE_CONTROLLER_*.md(全バージョン)の作成日と内容
- JARVIS_CONSTITUTION_DRAFT.md の第2章(継承規範)の出典文書の作成日
- commit履歴から「governance」「authority」「boundary」「permission」が出現した時期
- Decision Ledgerで`DC_20260728_002` `DC_20260729_009`等が確定された時期

**成果:** MoCKA内部での「制度先行・実装後行」の時間軸を確立

### 3.2 Phase B: 既知外部資料の内容確認

**目標:** ユーザーが指示した既知資料(arXiv 3件、MS Build、Ravi Shankar)で、実際にどのような「governance/capability」概念が扱われたかを記録する。

**調査対象:**
- arXiv:2603.14805 (タイトル・要旨・キーワード)
- arXiv:2604.08059 (同上)
- arXiv:2606.22528 (同上)
- Microsoft Build 2026のAI Governanceセッション記録
- Ravi Shankar著「Governance Theatre Series Part 4 — Four Kinds of Decay」

**制約:** 「内容を探索する」のではなく、**既存資料の確認のみ**。新規論文検索・外部Webサイト巡回は行わない。

**成果:** 既知資料がどのような概念を扱っていたかの精密記録

### 3.3 Phase C: 時間的対応と概念的収束の記録

**目標:** Phase A + Phase B の結果から、以下を記録する。

1. **TEMPORAL ALIGNMENT:** 同一の概念が外部と内部で同時期に出現しているか
2. **CONCEPTUAL CONVERGENCE:** 同じ問題を独立に両者が論じているか
3. **DIRECT LINK:** 引用・言及・交流の有無

**成果:** 「外部でも同時期に同じ問題が認識されていた」という主張が成立するかの判定

### 3.4 Phase D: 因果関係の厳格な保留

**決定:** 本調査ではCAUSALITYを追求しない。

以下の表現は使用しない：
- 「外部研究がMoCKAに影響を与えた」
- 「JARVISの停止は外部動向による」
- 「MoCKAが外部の流れに同期した」

使用する表現：
- 「両者で同じ時期に同じ概念が出現した」
- 「外部でも同様の問題が認識されていた」
- 「関連する研究・文書が並行して形成されていた」

---

## 4. 現在までの暫定観測

### 4.1 MoCKA側の公開記録から見えるもの

**"governance before execution"の明示化:**

| 文書 | 日時 | 内容 |
|---|---|---|
| PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md | Status=DESIGN(日時不明) | State Transition Engineに「Verification → Human Gate → Execution」の順序を明記 |
| JARVIS_CONSTITUTION_DRAFT.md | 2026-08-04 | 第2章で「原則3: Gate のみが制度変更を承認できる / 原則7: Institution が責任主体」を継承として記載。つまり、より古い Decision に基づいている |
| JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md | 2026-08-04 | HG-J02が「Authority 位置は未確定」と明記。**これが JARVIS実装を止めている根本原因** |

**観測:** MoCKA側では「governance」と「capability」の分離は**少なくとも2026-07-29より前**(DC_20260729_008の上流)に決定されていた。

### 4.2 未検証の点

- PHI-OS Constitution v1の正確な作成日(推定2026-07-25)
- PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.mdの作成日
- 「Authority Flow」(DC_20260729_009)がPending Resolutionになった理由
- 外部資料との直接的関連性

---

## 5. 次ステップ

### 5.1 調査ワークフロー

1. **(本文書)** 調査戦略フレームの確定
2. **(Phase A)** MoCKA公開記録の詳細時系列化
3. **(Phase B)** 既知外部資料の内容確認
4. **(Phase C)** 時間的対応・概念的収束の記録
5. **(Phase D)** 最終報告：「外部でも同時期に同じ問題が認識されていた」という判定の成立可否

### 5.2 納期

調査完了予定: 2026-08-25

---

## Knowledge Lineage

**Document:** MOCKA_EXTERNAL_HYPOTHESIS_INVESTIGATION_FRAME_v0.1.md
**Created:** 2026-08-19
**Purpose:** JARVIS停止仮説の外部証拠調査戦略の確立
**Instruction Origin:** ユーザー指示「くろこWEB指示書」(2026-08-19)
**Constraint:** READ-ONLY Investigation(PC内部データ不使用)
**Status:** FRAME(本体調査に先立つ戦略文書。新しい主張を含まない)
