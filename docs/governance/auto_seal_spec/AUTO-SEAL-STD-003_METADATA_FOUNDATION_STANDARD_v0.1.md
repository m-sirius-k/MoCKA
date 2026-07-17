# AUTO_SEAL Metadata Foundation Standard v0.1 (Skeleton)

- Document ID: AUTO-SEAL-STD-003
- Series: AUTO_SEAL Documentation Framework
- Class: Foundation
- Status: Review Candidate (skeleton; detailed spec deferred to Sprint S1; pending S0.5 review + Human Gate)
- Version: 0.1
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Commissioned / approval owner: きむら博士
- Directive: KUROKO-DOC-S0-001 (Sprint S0, Phase S0-3)
- Classification: Documentation only. No source code, no Core System File change.
- Depends on: AUTO-SEAL-ARCH-001, AUTO-SEAL-STD-004 (Identifier),
  AUTO-SEAL-STD-005 (Status), AUTO-SEAL-GLO-001

本書は骨子である。概要レベルまでを定め、詳細規格は Sprint S1 以降で確定する。

---

## 1. 目的

文書ヘッダ(メタデータ)の共通フィールドと、その必須 / 任意区分を定義する。本 Series の
全文書が同じメタデータ構造を持つことを保証する。

## 2. 責務(この Standard が正本となる範囲)

- 文書メタデータの共通フィールド集合と必須 / 任意区分。
- フィールドの意味と記載順。

責務外:

- Document ID の書式(AUTO-SEAL-STD-004 Identifier)。
- Status フィールドが取りうる値(AUTO-SEAL-STD-005 Status)。

## 3. 概要(Overview)

本 Series の各文書は、冒頭に次の共通メタデータを持つ(概要、詳細な必須判定は S1)。

| フィールド | 意味 | 区分(暫定) |
|---|---|---|
| Document ID | 文書の一意識別子(STD-004 準拠) | 必須 |
| Series | 所属 Series 名 | 必須 |
| Class | Foundation / Process / Governance | 必須 |
| Status | 文書状態(STD-005 準拠) | 必須 |
| Version | 版 | 必須 |
| Date | 発行 / 更新日 | 必須 |
| Author | 作成者(正確な AI 識別子または人間) | 必須 |
| approval owner | 承認責任者 | 必須 |
| Directive / Decision | 根拠指示または裁定 ID | 条件付き必須 |
| Depends on / Related | 依存・関連文書 | 任意 |
| Classification | 変更対象性(documentation only 等) | 必須 |

## 4. S1 以降で詳細化する項目(Placeholder)

- 各フィールドの値ドメインと形式(日付書式、Author 識別子規則)。
- 条件付き必須の条件の明文化(裁定を含む文書は Decision 必須、等)。
- 欠落時の Conformance 判定(AUTO-SEAL-IDX-001 Non-Conformant との対応)。

## 5. Open Questions

- メタデータを本文冒頭のリスト形式に固定するか、YAML front matter 化するか(既存 docs は
  リスト形式。CP932 汚染防止規約と UTF-8 検証の運用に合わせる)。

## 6. History

- 2026-07-13: 初版骨子(v0.1)。KUROKO-DOC-S0-001 Sprint S0 Phase S0-3。概要のみ。
