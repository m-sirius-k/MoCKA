# AUTO_SEAL Specification Series Index v1.0

- Document ID: AUTO-SEAL-IDX-001
- Series: AUTO_SEAL Documentation Framework
- Class: Foundation (Series catalog)
- Status: Review Candidate (S0 structural draft; pending S0.5 review + Human Gate; not yet Approved)
- Version: 1.0
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Commissioned / approval owner: きむら博士
- Directive: KUROKO-DOC-S0-001 (Sprint S0, Phase S0-2)
- Classification: Documentation only. No source code, no Core System File change.
- Governs by reference: AUTO-SEAL-ARCH-001 (Architecture)

本書は AUTO_SEAL Documentation Framework の目録である。Prefix Taxonomy、Master Catalog、
Dependency Matrix、Conformance 分類、Foundation / Process / Governance 区分を一元管理する。
文書の分類・依存の正本は本書とする(番号からは分類を導出しない、AUTO-SEAL-ARCH-001 第 5.2 節)。

---

## 1. Prefix Taxonomy

Series 接頭辞と TYPE コードの一覧。定義の正本は AUTO-SEAL-ARCH-001 第 5 章、本書はその
運用目録である。

| Prefix / TYPE | 意味 | 既定分類 | 採番状況 |
|---|---|---|---|
| AUTO-SEAL | Series 接頭辞(固定) | - | - |
| ARCH | Series Architecture | Foundation | 001 使用中 |
| IDX | Series Index | Foundation | 001 使用中 |
| STD | Standard(Foundation / Process) | Index で個別管理 | 001-006 使用中、009 予約(Review Standard) |
| GLO | Glossary | Foundation | 001 使用中 |
| RVW | Review Guideline | Process | 001 使用中 |
| PROC | Process 手順書 | Process | 未使用(将来) |
| GOV | Governance 規程 | Governance | 未使用(将来) |

---

## 2. Master Catalog

Series に属する全文書。分類はここが正本。

| Document ID | タイトル | 分類 | Version | Status | Sprint |
|---|---|---|---|---|---|
| AUTO-SEAL-ARCH-001 | Specification Series Architecture | Foundation | 1.0 | Review Candidate | S0 |
| AUTO-SEAL-IDX-001 | Specification Series Index | Foundation | 1.0 | Review Candidate | S0 |
| AUTO-SEAL-STD-001 | Evidence Foundation Standard | Foundation | 0.1 | Review Candidate (skeleton) | S0 |
| AUTO-SEAL-STD-002 | Traceability Foundation Standard | Foundation | 0.1 | Review Candidate (skeleton) | S0 |
| AUTO-SEAL-STD-003 | Metadata Foundation Standard | Foundation | 0.1 | Review Candidate (skeleton) | S0 |
| AUTO-SEAL-STD-004 | Identifier Foundation Standard | Foundation | 0.1 | Review Candidate (skeleton) | S0 |
| AUTO-SEAL-STD-005 | Status Foundation Standard | Foundation | 0.1 | Review Candidate (skeleton) | S0 |
| AUTO-SEAL-STD-006 | Proposal Standard | Process | 0.1 | Review Candidate (skeleton) | S0 |
| AUTO-SEAL-GLO-001 | Glossary | Foundation | 1.0 | Review Candidate | S0 |
| AUTO-SEAL-RVW-001 | Specification Review Guideline | Process | 0.1 | Review Candidate | S0.5 |
| AUTO-SEAL-STD-009 | Review Standard (reserved) | Process / Governance (未定) | - | Reserved | (将来) |

STD-009 は RVW-001 を将来規格化する用途に予約する(採番のみ、文書は未作成)。

Status 語彙は AUTO-SEAL-STD-005 (Status) を正本とする。S0 成果物は全て Review Candidate として
扱う(きむら博士裁定、2026-07-13)。Approved への移行と Decision Ledger 記録は、S0.5 レビュー
(ChatGPT / Gemini)と Human Gate による制度判断を経てから一括で行う。現時点で Approved は付与しない。

### 2.1 関連する既存文書(Series 外、Reference)

以下は本 Series 発足前から docs/governance/ に存在する AUTO_SEAL 関連文書。移設・改番せず、
本 Series から参照のみ行う(AUTO-SEAL-ARCH-001 第 5.4 節)。

| 既存 ID / ファイル | 役割 | 本 Series との関係 |
|---|---|---|
| GOV-DESIGN-ASBD-001 (AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md) | Seal Authorization Boundary 設計 | Evidence/Traceability/Status の実適用元。将来 Standard が参照 |
| AUTO_SEAL_M1_IMPLEMENTATION_PROPOSAL_v1.0.md | M1 実装提案 | Proposal Standard (STD-006) の既存実例 |
| AUTO_SEAL_M2_CONNECTION_PROPOSAL_v1.0.md | M2 接続提案 | Proposal Standard (STD-006) の既存実例 |
| AUTO_SEAL_M1_TERMINAL_PROCESS_PLAN_v1.0.md | M1 終端手続き計画 | Process 領域の既存実例 |
| TODO_411_412_413_AUTO_SEAL_BOUNDARY_AUDIT_v1.0.md | 境界監査 | Evidence/Audit の入力実例 |

---

## 3. Dependency Matrix

文書間の参照依存。AUTO-SEAL-ARCH-001 第 2 章の一方向性(Foundation <- Process <- Governance)を
満たすことを本表で保証する。行が「参照する側」、列が「参照される側」。

| 参照する \ される | ARCH-001 | IDX-001 | STD-001 Evd | STD-002 Trc | STD-003 Mtd | STD-004 Idn | STD-005 Sts | GLO-001 |
|---|---|---|---|---|---|---|---|---|
| ARCH-001 | - | - | - | - | - | - | - | 用語 |
| IDX-001 | 規約 | - | - | - | - | - | 状態語彙 | 用語 |
| STD-001 Evidence | 規約 | - | - | - | - | - | - | 用語 |
| STD-002 Traceability | 規約 | - | 証跡 | - | - | ID 書式 | - | 用語 |
| STD-003 Metadata | 規約 | - | - | - | - | ID 書式 | 状態語彙 | 用語 |
| STD-004 Identifier | 規約 | - | - | - | - | - | - | 用語 |
| STD-005 Status | 規約 | - | - | - | - | - | - | 用語 |
| STD-006 Proposal (Process) | 規約 | - | 証跡 | 追跡 | メタデータ | ID 書式 | 状態語彙 | 用語 |

依存の健全性:

- Foundation 群(STD-001..005)は Process(STD-006)を参照しない(一方向性 OK)。
- 循環依存なし。Identifier(STD-004)と Status(STD-005)は相互参照せず、責務境界
  (AUTO-SEAL-ARCH-001 第 3 章)で分離済み。
- 全文書が GLO-001(用語)を参照する。GLO-001 は他を参照しない葉ノード。

---

## 4. Conformance 分類

文書が Series 規格に適合しているかの分類枠。判定規程そのものは将来の Governance Standard で
確定する(AUTO-SEAL-ARCH-001 第 7 章)。本書は分類ラベルのみ定義する。

| Conformance ラベル | 意味 |
|---|---|
| Conformant | Metadata / Identifier / Status / Traceability の各 Foundation Standard を満たす |
| Skeleton | 骨格のみ。必須節は存在するが詳細規格が未記述(S0 成果物の既定) |
| Reference | Series 外の既存文書で、参照のみ行い規格適合は求めない |
| Non-Conformant | 必須メタデータまたは ID 規約を欠く。是正対象 |

S0 時点の分類:

- Conformant: (なし。判定規程未確定のため S0 では付与しない)
- Review Candidate: ARCH-001, IDX-001, GLO-001, STD-001..006(全 S0 成果物。承認前。S0.5 レビュー + Human Gate 待ち)
- Skeleton: STD-001..006(Review Candidate かつ骨格のみ)
- Reference: 第 2.1 節の既存文書群

---

## 5. Foundation / Process / Governance 区分

| 分類 | 所属文書(S0 時点) | 将来追加見込み |
|---|---|---|
| Foundation | ARCH-001, IDX-001, GLO-001, STD-001 Evidence, STD-002 Traceability, STD-003 Metadata, STD-004 Identifier, STD-005 Status | Foundation 詳細版(S1) |
| Process | STD-006 Proposal, RVW-001 Review Guideline | STD-009 Review Standard(予約), Verification, Audit, Release(PROC/STD) |
| Governance | (なし) | Conformance 規程, Human Gate Policy |

---

## 6. 更新手順

- 新規文書を追加したら、Master Catalog(第 2 章)・Dependency Matrix(第 3 章)・
  区分(第 5 章)を同時に更新する。3 表の不整合を残さない。
- 本書の更新は CHANGE_START / CHANGE_DONE 記録を伴う。

---

## 7. History

- 2026-07-13: 初版(v1.0)。KUROKO-DOC-S0-001 Sprint S0 Phase S0-2。Prefix Taxonomy、
  Master Catalog(9 文書 + 既存 Reference 5 件)、Dependency Matrix、Conformance 分類、
  F/P/G 区分を確定。依存の一方向性・循環なしを確認。
- 2026-07-13: きむら博士裁定により S0 成果物を Review Candidate へ統一(Master Catalog /
  Conformance 分類 / 本書 Status を更新)。Approved 移行は S0.5 レビュー + Human Gate 後。
- 2026-07-13: S0.5 として AUTO-SEAL-RVW-001 (Review Guideline) を Master Catalog / Prefix
  Taxonomy / F/P/G 区分へ追加。将来の規格化に備え STD-009 (Review Standard) を予約。
