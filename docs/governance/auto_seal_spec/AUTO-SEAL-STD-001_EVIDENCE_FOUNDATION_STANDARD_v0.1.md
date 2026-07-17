# AUTO_SEAL Evidence Foundation Standard v0.1 (Skeleton)

- Document ID: AUTO-SEAL-STD-001
- Series: AUTO_SEAL Documentation Framework
- Class: Foundation
- Status: Review Candidate (skeleton; detailed spec deferred to Sprint S1; pending S0.5 review + Human Gate)
- Version: 0.1
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Commissioned / approval owner: きむら博士
- Directive: KUROKO-DOC-S0-001 (Sprint S0, Phase S0-3)
- Classification: Documentation only. No source code, no Core System File change.
- Depends on: AUTO-SEAL-ARCH-001, AUTO-SEAL-GLO-001

本書は骨子である。概要レベルまでを定め、詳細規格は Sprint S1 以降で確定する。

---

## 1. 目的

Evidence(証跡)とは何か、何をもって証跡が成立するかを、AUTO_SEAL 文書体系の共通土台
として定義する。他 Standard は「証跡が要る」と述べるとき、本書の定義を参照する。

## 2. 責務(この Standard が正本となる範囲)

- 証跡の定義と、証跡たりうる最小条件。
- 証跡の成立条件(書込の成功報告と、状態が変わったことの確認は別、という原則)。

責務外:

- 証跡をどのフィールドで保持するか(AUTO-SEAL-STD-003 Metadata)。
- 証跡を指す識別子の書式(AUTO-SEAL-STD-004 Identifier)。

## 3. 概要(Overview)

MoCKA の三要素のうち Record と Verification に対応する。AUTO_SEAL 文脈では、Seal が
「誰(who)によって、どの Decision(decision_id)に基づき、どの Artifact(artifact_hash)を
固定したか」を後から証明できることが証跡の目的である
(参照: GOV-DESIGN-ASBD-001 第 5 章 Auth Model)。

証跡の最小構成(概要、詳細は S1):

- who: 人間の承認者(approved_by は system 値を許容しない)。
- decision_id: 事前に人間が承認した Decision。
- artifact_hash: 固定対象の commit hash。
- seal_hash: sealed_summary_hash。
- approval_timestamp: 人間が承認した時刻。

成立条件(概要):

- 書込系ツールが ok を返したことのみを根拠に証跡成立とみなさない。対応する取得系で
  読み戻し、実データ反映を確認して初めて証跡が成立する(Execution Integrity 原則)。

## 4. S1 以降で詳細化する項目(Placeholder)

- 証跡種別の分類(承認証跡 / 実行証跡 / 監査証跡)。
- 各証跡の必須フィールドと検証手順の形式定義。
- 欠落時の扱い(fail closed は AUTO-SEAL-STD-005 と整合)。

## 5. Open Questions

- 直接実行(CLI)経路で git commit 証跡のみが残る場合の最小証跡水準(GOV-DESIGN-ASBD-001 RB-1)。
- emergency path における事後 decision_id の証跡上の扱い。

## 6. History

- 2026-07-13: 初版骨子(v0.1)。KUROKO-DOC-S0-001 Sprint S0 Phase S0-3。概要のみ。
