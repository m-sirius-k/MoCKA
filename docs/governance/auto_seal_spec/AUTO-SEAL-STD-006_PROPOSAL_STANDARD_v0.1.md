# AUTO_SEAL Proposal Standard v0.1 (Skeleton)

- Document ID: AUTO-SEAL-STD-006
- Series: AUTO_SEAL Documentation Framework
- Class: Process
- Status: Review Candidate (skeleton; detailed spec deferred to Sprint S1; pending S0.5 review + Human Gate)
- Version: 0.1
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Commissioned / approval owner: きむら博士
- Directive: KUROKO-DOC-S0-001 (Sprint S0, Phase S0-4)
- Classification: Documentation only. No source code, no Core System File change.
- Depends on: AUTO-SEAL-ARCH-001, AUTO-SEAL-STD-001 (Evidence),
  AUTO-SEAL-STD-002 (Traceability), AUTO-SEAL-STD-003 (Metadata),
  AUTO-SEAL-STD-004 (Identifier), AUTO-SEAL-STD-005 (Status), AUTO-SEAL-GLO-001
- Aligns existing examples: AUTO_SEAL_M1_IMPLEMENTATION_PROPOSAL_v1.0.md (GOV-PROP-ASM1-001),
  AUTO_SEAL_M2_CONNECTION_PROPOSAL_v1.0.md

本書は骨子である。概要レベルまでを定め、詳細規格は Sprint S1 以降で確定する。本書は
Process Standard であり、提案文書(Proposal)が満たすべき構造と承認ゲート要件を規定する。

---

## 1. 目的

AUTO_SEAL に関する提案文書(実装提案・接続提案・移行提案等)が共通して満たすべき構造、
必須節、承認ゲート要件を定義する。既存の AUTO_SEAL M1/M2 提案文書を実例として、Series
Architecture(AUTO-SEAL-ARCH-001)に整合させる。

## 2. 責務(この Standard が正本となる範囲)

- 提案文書の必須節構成と、各節が答えるべき問い。
- 提案から実装着手に至る承認ゲート(Human Gate)の要件。
- 「提案は実装ではない」境界の明示要件。

責務外:

- 提案が参照する証跡の定義(AUTO-SEAL-STD-001 Evidence)。
- 提案文書の ID 書式(AUTO-SEAL-STD-004 Identifier)。

## 3. 既存提案文書との整合(Series Architecture への適合確認)

既存の AUTO_SEAL 提案文書は、本 Standard が定める骨格と既に整合している。以下を確認した。

| 観点 | 既存文書(GOV-PROP-ASM1-001 等)の実態 | 本 Standard での位置付け |
|---|---|---|
| 提案と実装の分離 | 冒頭で「コードは含まず、実装は本書承認後の別工程」と明示 | 必須節「実装非該当の明示」として規格化 |
| Purpose / Scope | 第 1 章に IN / OUT を明記 | 必須節 |
| Minimal Working Path | 最小実働経路を 1 経路に限定 | 推奨節(実装提案の場合は必須) |
| Parent decision / Proposal decision | メタデータに DC_ を明記 | Traceability(STD-002)により必須 |
| Design ref | 上流設計文書へ参照 | Traceability により必須 |

矛盾は検出されなかった。既存文書は GOV-PROP-* 体系を維持し、本 Series からは Reference
として関連付ける(AUTO-SEAL-ARCH-001 第 5.4 節、改番しない)。今後の新規 AUTO_SEAL 提案は
本 Standard に準拠する。

## 4. 提案文書の必須節(概要、詳細は S1)

1. メタデータ(AUTO-SEAL-STD-003 準拠。Parent decision / Design ref を含む)。
2. 実装非該当の明示(本書はコードを含まない旨)。
3. Purpose / Scope(IN / OUT の明記)。
4. 根拠(上流 Decision / 設計文書への Traceability)。
5. 承認ゲート要件(実装着手に必要な Human Gate 条件)。
6. Non Goals。
7. History。

## 5. 承認ゲート要件(概要)

- 提案の起草(drafting)と実装着手(implementation)を分離する。起草承認は実装承認を含まない。
- 実装着手は Core System File Human Gate の個別承認を要する(GOV-DESIGN-ASBD-001 Migration
  Plan の前提と整合)。
- 制度的裁定(採用 / 却下 / 保留)は Decision Ledger へ記録する(MoCKA 記録義務)。

## 6. S1 以降で詳細化する項目(Placeholder)

- 提案種別(実装 / 接続 / 移行 / 廃止提案)ごとの必須節の差分。
- Minimal Working Path の形式要件(sandbox 完了条件の書き方)。
- 却下・保留時の文書 Status 遷移(AUTO-SEAL-STD-005 と整合)。

## 7. Non Goals

- 既存 GOV-PROP-* 提案文書の改番・移設。
- 本 Standard に基づく提案の実際の起草(本書は規格のみ)。

## 8. History

- 2026-07-13: 初版骨子(v0.1)。KUROKO-DOC-S0-001 Sprint S0 Phase S0-4。既存 AUTO_SEAL
  M1/M2 提案文書との整合を確認(矛盾なし)。Series Architecture への適合を記述。
