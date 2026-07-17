# AUTO_SEAL Traceability Foundation Standard v0.1 (Skeleton)

- Document ID: AUTO-SEAL-STD-002
- Series: AUTO_SEAL Documentation Framework
- Class: Foundation
- Status: Review Candidate (skeleton; detailed spec deferred to Sprint S1; pending S0.5 review + Human Gate)
- Version: 0.1
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Commissioned / approval owner: きむら博士
- Directive: KUROKO-DOC-S0-001 (Sprint S0, Phase S0-3)
- Classification: Documentation only. No source code, no Core System File change.
- Depends on: AUTO-SEAL-ARCH-001, AUTO-SEAL-STD-001 (Evidence),
  AUTO-SEAL-STD-004 (Identifier), AUTO-SEAL-GLO-001

本書は骨子である。概要レベルまでを定め、詳細規格は Sprint S1 以降で確定する。

---

## 1. 目的

Traceability(追跡可能性)を定義する。ある成果物・決定・証跡から、その根拠と後続へ
一意にたどれることを保証する共通土台を与える。

## 2. 責務(この Standard が正本となる範囲)

- 文書間・成果物間の参照関係の張り方と、たどれることの保証条件。
- 前方参照(根拠へ)と後方参照(後継へ)の対称性要件。

責務外:

- 参照に用いる ID の書式(AUTO-SEAL-STD-004 Identifier)。
- 参照先が持つべき証跡の中身(AUTO-SEAL-STD-001 Evidence)。

## 3. 概要(Overview)

AUTO_SEAL では、Trigger(AUTO_SEAL_PENDING イベント)と Completion(Seal 実行)が
pending_ref で接続されることが追跡の要である(参照: GOV-DESIGN-ASBD-001 RB-5、第 5 章
pending_ref フィールド)。この接続が無いと Human Gate が論理的に未閉鎖となる。

追跡の原則(概要、詳細は S1):

- どの Seal も、根拠 Decision(decision_id)へたどれること。
- どの AUTO 由来 Seal も、対応する PENDING イベント(pending_ref)へたどれること。
- 後継文書は旧文書へ、旧文書は後継文書へ相互参照する(SUPERSEDED 時)。

## 4. S1 以降で詳細化する項目(Placeholder)

- 参照リンクの必須方向と最小到達可能性(reachability)の形式定義。
- 切れたリンク(dangling reference)の検出と扱い。
- Dependency Matrix(AUTO-SEAL-IDX-001)との整合検証手順。

## 5. Open Questions

- 直接実行経路で pending_ref が存在しない Seal の追跡水準。
- 既存 Reference 文書(Series 外)への参照をどこまで追跡対象に含めるか。

## 6. History

- 2026-07-13: 初版骨子(v0.1)。KUROKO-DOC-S0-001 Sprint S0 Phase S0-3。概要のみ。
