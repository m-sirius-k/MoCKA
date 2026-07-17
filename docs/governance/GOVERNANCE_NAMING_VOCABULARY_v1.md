# MoCKA Governance Naming Vocabulary v1

Document ID: GOVERNANCE_NAMING_VOCABULARY_v1
Status: Active
Artifact Type: Vocabulary Definition (addition-only / annotation-by-reference)
Date: 2026-07-14
作成: くろこ(Claude-opus-4-8)
Authority: Human Gate Approved (きむら博士 / 命名体系の正式採用)
Adoption Decision: DC_20260714_004(Decision Ledger, Active)

## 0. 位置づけ

本文書は、MoCKA 内で再利用可能な正式概念語彙として三層命名体系を固定する
定義文書である。目的は「名称を付けること」ではなく「再利用可能な正式概念
語彙として固定すること」にある。

本文書は追加(addition)であり、既存の Decision / Contract / Evidence /
設計記録を一切改変しない。既存記録との結び付けは annotation(参照)方式で
行う(過去記録の改変は禁止)。

## 1. 三層命名体系(正式採択語彙)

| 層 | 正式名称 | 略称 |
|----|----------|------|
| 思想層 | Governance Anchor Principle | - |
| 制度層 | Decision Integrity Framework | DIF |
| 技術層 | Governance Layer 7 | GL7 |

## 2. 各層の定義

### 2.1 思想層 — Governance Anchor Principle

MoCKA の統治を支える最上位の思想的アンカー。統治判断を人間の意思決定・
記録・検証に錨づける原理を指す。個別の制度・機構はこの原理から導出される。

### 2.2 制度層 — Decision Integrity Framework (DIF)

思想層を制度として具現する枠組み。Decision Ledger・Human Gate・Contract・
Integrity 記録など、意思決定の完全性(decision integrity)を保証する制度群の
総称。DIF は「なぜ・誰が・どの代替案の上で決めたか」を継承可能な形で保持する
制度層を指す。

### 2.3 技術層 — GL7 (Governance Layer 7)

制度を実行時に強制する技術層コンポーネント。名称 GL7 は "Governance Layer 7"
の略である。

重要(参照整合): GL7 の名称(Governance Layer 7)と、GL7 の canonical な
governance 定義・役割は別軸である。GL7 の canonical definition / 役割は
Execution Governance であり、これは DC_20260714_003(Judgment A)で確定済みの
まま保持される。本語彙は「名称 = Governance Layer 7」を追加するものであって、
GL7 の canonical definition(Execution Governance)を置換・改変しない。

## 3. 三層の関係

    思想層  Governance Anchor Principle   (原理)
       |  derives
       v
    制度層  Decision Integrity Framework  (制度: Decision Ledger / Human Gate / Contract)
       |  enforced by
       v
    技術層  GL7 (Governance Layer 7)      (実行時強制。role = Execution Governance)

上位層が下位層の存在理由を与え、下位層が上位層を実行時に担保する。GL7 は
DIF を実行時に強制する技術層であり、その役割は Execution Governance である。

## 4. 既存記録との参照整合(annotation / 非改変)

本語彙は以下の既存正本を参照(annotation)する。いずれも本文書により
改変されない。

- DC_20260714_003(Active): GL7 canonical definition = Execution Governance /
  "GL7 Core Integrity Layer" = Policy View / Promotion Gate 命名 /
  ValidationRecord = 入力証跡。→ 本語彙の技術層 GL7 の役割定義と整合。
- CONT-GL7-PROMOTION-GATE-v1.0(Canonical): Promotion Gate 境界制御契約。
  → 制度層 DIF の一要素(Contract)として参照。
- MAP_LAB_GL7_BOUNDARY_DESIGN v0.1 / v0.2(NON-CANONICAL 設計記録): GL7 と
  MAP-LAB の責務境界。→ 技術層 GL7 の境界設計として参照。
- GL7_ENCODING_REMEDIATION_EVIDENCE_20260714.md: GL7 encoding blocker 解消証跡。
  → 技術層 GL7 の実測証跡として参照。

参照整合の確認結果: 本語彙は既存の GL7 canonical definition(Execution
Governance)と矛盾しない。GL7 の名称付与は追加であり、機能定義は不変。

## 5. 採択理由

本命名体系は、実装・検証・意思決定の積み上げ後に付与された概念であり、
名称による権威化を避けた状態で正式語彙として固定する。名称先行による
概念の権威化を避けることが採択の核心である。

## 6. 適用範囲・非適用

- 適用: 本語彙は MoCKA 内の以後の記述で、三層概念を指す正式語彙として
  再利用してよい。
- 非適用(本文書では実施しない): KN-004 Registry(六層識別グラフ)への
  レコード追加は本文書・DC_20260714_004 の範囲外(別 Human Gate 判断へ留保)。
  Seal 実行・commit・push は本文書の範囲外(別 Human Gate 判断)。

## 7. 未実施事項(本文書時点)

- 既存 Contract / Decision / Evidence の改変: なし(参照のみ)
- KN-004 Registry レコード追加: なし(別判断へ留保)
- Seal 実行: なし(準備確認のみ)
- commit / push: なし(commit境界維持・push未承認)
- F-A Event Write 再開: なし(Pending 0/3 維持)
