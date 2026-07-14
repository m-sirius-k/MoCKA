# MAP-LAB / GL7 Boundary Design v0.2

Status: DESIGN RECORD / NON-CANONICAL / NOT IMPLEMENTED
Artifact Type: Boundary Design Record
Version: v0.2
Supersedes: v0.1 (docs/architecture/MAP_LAB_GL7_BOUNDARY_DESIGN_v0.1.md — 保持・削除しない)
Date: 2026-07-14
作成: くろこ(Claude-opus-4-8)

Authority: Human Gate Approved
Decision: v0.1 を保持し、v0.2 を新規設計記録として作成する
Mutation: file creation only

## Revision Note (v0.1 -> v0.2)

- v0.1 の境界設計思想は保持する(削除・改変しない)。
- 運用ポリシーを独立章として明示分離した:
  - Validation Gate Policy(章 3)
  - Storage Boundary Policy(章 4)
  - Default Deny Policy(章 5)
- v0.1 の「依存方向」章の図と原則は Validation Gate Policy(章 3)へ吸収・拡張した
  (内容は保存、明示見出し化)。
- v0.1 は併存させ、本 v0.2 が設計記録の最新版となる(v0.1 は履歴として残置)。

---

## 0. 位置づけ

本記録は、GL7 Core Integrity と MAP-LAB Observation の責務境界について
Human Gate で決定された方針を、設計判断として固定するものである。
実装・ファイル配置・GL7設定変更・encoding変換・F-A Event Write 再実行は
本記録の範囲外であり、次の Human Gate 承認後に別途行う。

本記録は正本ではない(NON-CANONICAL)。制度承認・正本化・Decision Ledger 登録・
実装のいずれも含まない。

---

## 1. 背景

- 2026-07-14、Observation Constitutional Finding F-A の Event Write が
  GL7_EXECUTION_BLOCKED により停止した(0/3、未書込保留)。
- 原因は MAP-LAB 生成物 12件が UTF-16LE(BOM FF FE)で書き出されており、
  MoCKA の UTF-8 整合前提に反したこと。cp932 ではなく UTF-16LE が実体。
- Event Ledger に Mutation は発生していない(chain tip 不変・部分書込ゼロ)。
- GL7 の停止動作は、整合違反時に write を全 abort する安全機構として
  設計どおり機能した(不具合ではない)。
- 対象12件は MAP-LAB-001 First Blood(Evidence-001)の surface-map 生成物で、
  全て git 未追跡・root 直下・同一バッチ生成(11:08-11:17 JST)。

## 2. 境界設計原則

### GL7 Core Integrity Layer

注記(2026-07-14, DC_20260714_003 / Judgment A): 本見出しの "GL7 Core Integrity Layer"
は GL7 の canonical definition ではなく Policy View として機能する。GL7 の正本定義は
Execution Governance であり、本節は GL7 scope を参照する政策的視点を記述する。

責務:
- canonical data の保護
- 確定済みデータの検証
- 不変条件(integrity invariant)の保証

対象:
- tracked data(git 追跡下の資産)
- 正本データ(data/ 正本)
- 検証済み成果物

### MAP-LAB Observation Layer

責務:
- 観測(observation)
- 実験(experiment)
- 生成(generation)
- 分析用成果物の作成

対象:
- dynamic artifact(動的生成物)
- regenerable output(再生成可能な出力)
- 未確定データ

原則: 両層は責務が排他的である。観測・生成の途中成果物を
Core Integrity と同一の不変条件で扱わない。

## 3. Validation Gate Policy

MAP-LAB 成果物は GL7 Core へ直接到達しない。Core への反映は
Validation Gate を経由した昇格(promotion)によってのみ成立する。

    MAP-LAB
        |
        v
    Validation Gate  --(Revise)-->  MAP-LAB 側で再精製
        |
      (Approve)
        |
        v
    GL7 Core

- 直接到達禁止: MAP-LAB 成果物の GL7 Core への直接反映は認めない。
- 昇格必須: Core 反映には Validation Gate 通過を必須とする。
- Approve 時のみ反映: Validation Gate が Approve を返した成果物のみ Core へ反映可能。
- Revise 時は差戻し: Validation Gate が Revise の場合、MAP-LAB 側で再精製し
  再度 Gate に提出する(Core 側は変更しない)。
- 未検証成果物は対象外: Gate 未通過の成果物は GL7 Core 整合の対象に含めない。

## 4. Storage Boundary Policy

GL7 Core と MAP-LAB を、物理配置・論理責務・書込権限の3軸で分離する。

GL7 Core:
- canonical(正本)
- baseline(基準)
- invariant(不変条件)
- 管理された反映のみ許可(uncontrolled write を認めない)

MAP-LAB:
- dynamic artifact(動的生成物)
- experiment data(実験データ)
- regenerable output(再生成可能な出力)
- 未確定データ

分離軸:
- 物理配置: Core 資産と MAP-LAB 生成物の格納場所を分ける
  (MAP-LAB 生成物を Core/root の整合空間へ混在させない)。
- 論理責務: 保護・検証・不変保証(Core)と 観測・実験・生成(MAP-LAB)を混同しない。
- 書込権限: Core への書込は管理経路のみ。MAP-LAB からの直接書込権限を持たせない。

## 5. Default Deny Policy

原則: MAP-LAB から GL7 Root / Core への自動書込は、既定で禁止する(Default Deny)。

既定: 拒否(deny)。以下の許可条件を すべて 満たす場合に限り書込を許可する:
- Validation 通過(Validation Gate Approve)
- Human Gate 承認
- 明示操作(explicit action。暗黙・自動フローによる反映を認めない)

上記のいずれかを欠く書込・昇格・反映はすべて拒否される。

## 6. Exception Handling Boundary

encoding 差異などの環境依存要素は、GL7 Core では処理しない。
これらは Core より前段の正規化/検証境界で吸収する。

吸収場所:

    MAP-LAB Output
           |
           v
    Normalization / Validation Boundary
           |
           v
    GL7

原則: GL7 Core は「整合が保証された入力」のみを前提とする。
encoding 正規化の責務は Core の外(前段境界)に置く。

## 7. 将来実装条件(本記録では実施しない)

以下は次の Human Gate 承認後の別トラックとする:
- MAP-LAB 動的成果物を GL7 Core Integrity Scope から分離する具体機構
- Normalization / Validation Boundary の実装位置と方式
- GL7 走査スコープの再定義(未追跡 root ファイルの扱い)
- 保留中 F-A 3記録(検証済み)の書込再開

## 8. 未実施事項(本記録時点)

- v0.1 変更: なし(保持)
- GL7 設定変更: なし
- MAP-LAB 配置変更: なし
- .gitignore 変更: なし
- encoding 変換: なし
- F-A Event Write 再実行: なし
- Core 資産変更: なし
- commit / push: なし
- 本設計の実装: なし(記録のみ)
