# AUTO_SEAL Identifier Foundation Standard v0.1 (Skeleton)

- Document ID: AUTO-SEAL-STD-004
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

識別子(Identifier)の書式・採番・一意性・不変性を定義する。文書 ID、Decision ID、
seal_request_id、event_id 等、AUTO_SEAL 文脈で用いる ID の共通規則を与える。

## 2. 責務(この Standard が正本となる範囲)

- ID の書式(構文)と採番規則。
- 一意性(uniqueness)と不変性(immutability)の保証条件。

責務外:

- ID が指す対象の状態(AUTO-SEAL-STD-005 Status)。
- ID をメタデータのどこに置くか(AUTO-SEAL-STD-003 Metadata)。

## 3. 概要(Overview)

対象となる主な ID 系(概要、詳細は S1):

| ID 系 | 書式(例) | 正本 |
|---|---|---|
| 文書 ID | AUTO-SEAL-<TYPE>-<NNN> | AUTO-SEAL-ARCH-001 第 5 章 |
| Decision ID | DC_YYYYMMDD_NNN | MoCKA Decision Ledger |
| Event ID | E{YYYYMMDD}_{hex} | events.db 採番 |
| seal_request_id | (S1 で確定) | GOV-DESIGN-ASBD-001 Auth Model |

不変性の原則(概要):

- 一度採番した ID は再利用しない。廃止後も欠番として残す(AUTO-SEAL-ARCH-001 第 5.3 節)。
- 版更新で文書 ID を変えない。Version のみ上げる。

## 4. S1 以降で詳細化する項目(Placeholder)

- seal_request_id の書式と採番主体の確定(現状 GOV-DESIGN-ASBD-001 で未確定)。
- ID 衝突検出手順。
- 外部 ID(git commit hash 等)を内部 ID として引用する際の扱い。

## 5. Open Questions

- Decision ID の Gate 自己採番(DC_EXEC_...)と人間承認 Decision(DC_YYYYMMDD_...)の
  識別規則(GOV-DESIGN-ASBD-001 RB-4)。

## 6. History

- 2026-07-13: 初版骨子(v0.1)。KUROKO-DOC-S0-001 Sprint S0 Phase S0-3。概要のみ。
