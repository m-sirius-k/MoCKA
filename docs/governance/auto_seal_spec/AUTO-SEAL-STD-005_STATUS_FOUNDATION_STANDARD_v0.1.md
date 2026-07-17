# AUTO_SEAL Status Foundation Standard v0.1 (Skeleton)

- Document ID: AUTO-SEAL-STD-005
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

文書および Seal 手続きが取りうる状態(Status)語彙と、その遷移、fail closed 既定を
定義する。状態を単一の語彙集合に閉じ込め、独自語彙の混入を防ぐ。

## 2. 責務(この Standard が正本となる範囲)

- 状態語彙の集合と各値の意味。
- 状態遷移の許容規則と既定(fail closed)。

責務外:

- 状態を持つ対象の識別(AUTO-SEAL-STD-004 Identifier)。
- 状態フィールドをメタデータのどこに置くか(AUTO-SEAL-STD-003 Metadata)。

## 3. 概要(Overview)

### 3.1 文書 Status(暫定語彙、詳細は S1)

| 値 | 意味 |
|---|---|
| Draft | 起草中(骨子含む) |
| Review Candidate | レビュー対象の候補。承認前。外部レビュー(ChatGPT / Gemini 等)へ入力される |
| Review Complete | 両レビューが出揃い、コメント統合・修正版作成が完了し、未解決の重大指摘がゼロ。Human Gate 待ち |
| Approved | Human Gate で採択済(骨格または内容が確定) |
| Effective | 承認され、制度として発効・適用中 |
| Superseded | 後継文書に置換 |
| Obsolete | 失効 |

### 3.1.1 ライフサイクル(遷移順)

```
Draft -> Review Candidate -> Review Complete -> Human Gate -> Approved -> Effective
```

- Human Gate は状態ではなく工程(きむら博士による採択 / 却下の判断点)。
- 却下時は Review Candidate へ差し戻す(修正後に再レビュー)。
- Review Complete の完了条件は AUTO-SEAL-RVW-001 (Review Guideline) 第 5 章に従う。
- Superseded / Obsolete はどの状態からも遷移しうる終端。

MoCKA 既存の TODO status(未着手 / 進行中 / 完了 / 保留 / 廃止)や Architecture Contract 系
9 値とは別軸である。本 Standard は「Series 文書の状態」を対象とし、既存軸に統合しない
(軸を混ぜない、MoCKA CLAUDE.md TODO_384 準拠の思想)。

### 3.2 fail closed 既定

- 状態が未確定 / 不明のとき、既定は「未承認(承認されていない)」側に倒す。
- Seal 手続きにおいて approved_by が human でない場合は Seal 不可(GOV-DESIGN-ASBD-001
  第 5 章、DC_20260713_003 確定事項)。これは fail closed の具体例である。

## 4. S1 以降で詳細化する項目(Placeholder)

- 状態遷移図(許容遷移と禁止遷移)の形式定義。
- 文書 Status と Seal 手続き状態(PENDING / SEALED 等)の分離と対応。
- Conformance 分類(AUTO-SEAL-IDX-001 第 4 章)との対応。

## 5. Open Questions

- Skeleton(骨子)を独立した Status 値とするか、Draft の一種とするか。
- Approved を「骨格確定」と「内容確定」で細分するか。

## 6. History

- 2026-07-13: 初版骨子(v0.1)。KUROKO-DOC-S0-001 Sprint S0 Phase S0-3。概要のみ。
- 2026-07-13: きむら博士裁定のライフサイクルを反映。Review Candidate に加え Review Complete /
  Effective を追加し、遷移順(Draft -> Review Candidate -> Review Complete -> Human Gate ->
  Approved -> Effective)を第 3.1.1 節に明記。完了条件は AUTO-SEAL-RVW-001 を参照。
