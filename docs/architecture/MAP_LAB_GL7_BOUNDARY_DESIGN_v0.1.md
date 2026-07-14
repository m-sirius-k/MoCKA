# MAP-LAB / GL7 Boundary Design v0.1

Status: DESIGN RECORD / NON-CANONICAL / NOT IMPLEMENTED
Artifact Type: Boundary Design Record
Date: 2026-07-14
作成: くろこ(Claude-opus-4-8)

Authority: NONE
Decision: 確定済み Human Gate 方針の記録化のみ
Mutation: none (本記録は設計判断の固定であり、実装・配置・設定変更を含まない)

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

## 3. 依存方向

許可される方向:

    MAP-LAB
        |
        v
    Validation Gate
        |
        v
    GL7 Core

禁止される方向:

    MAP-LAB 成果物
        |
        v
    直接 GL7 / Core 侵入 (禁止)

原則: MAP-LAB 成果物は必ず Validation Gate を経由してから
GL7 Core に到達する。未検証の生成物が Core 整合空間へ直接流入しない。

## 4. Exception Handling Boundary

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

## 5. 将来実装条件(本記録では実施しない)

以下は次の Human Gate 承認後の別トラックとする:
- MAP-LAB 動的成果物を GL7 Core Integrity Scope から分離する具体機構
- Normalization / Validation Boundary の実装位置と方式
- GL7 走査スコープの再定義(未追跡 root ファイルの扱い)
- 保留中 F-A 3記録(検証済み)の書込再開

## 6. 未実施事項(本記録時点)

- GL7 設定変更: なし
- MAP-LAB 配置変更: なし
- .gitignore 変更: なし
- encoding 変換: なし
- F-A Event Write 再実行: なし
- Core 資産変更: なし
- 本設計の実装: なし(記録のみ)
