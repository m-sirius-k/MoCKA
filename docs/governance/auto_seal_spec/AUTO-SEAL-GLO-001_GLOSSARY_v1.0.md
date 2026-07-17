# AUTO_SEAL Glossary v1.0

- Document ID: AUTO-SEAL-GLO-001
- Series: AUTO_SEAL Documentation Framework
- Class: Foundation
- Status: Review Candidate (S0.5 Series は Review Complete(HG-11/DC_20260713_021)。文書個別 Status の Review Complete 昇格と IDX-001 Master Catalog 同期は全文書版確定後(HG-13/DC_20260713_023)へ繰延)
- Version: 1.1
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Commissioned / approval owner: きむら博士
- Directive: KUROKO-DOC-S0-001 (Sprint S0, Phase S0-5)
- Classification: Documentation only. No source code, no Core System File change.
- Depends on: AUTO-SEAL-ARCH-001

本書は AUTO_SEAL Documentation Framework の用語の唯一の正本である。本 Series 内の各文書は
用語を再定義せず、本書を参照する(AUTO-SEAL-ARCH-001 第 4.4 節)。用語定義が更新された場合、
参照側は再定義せず本書の更新に従う。

---

## 1. 用語定義

### Proposal(提案)

実装・接続・移行等を行うための提案文書。コードそのものを含まず、承認された後に別工程で
実装される。起草の承認は実装の承認を含まない。規格は AUTO-SEAL-STD-006(Proposal Standard)。

### Decision(決定 / 裁定)

制度上の意思決定(採用 / 却下 / 保留 / 凍結等)。MoCKA では Decision Ledger
(data/decisions/decision_ledger.jsonl)へ decision_id 付きで記録される。裁定を Markdown や
イベント記述のみに残すことは認められない(記録義務)。

### Evidence(証跡)

ある事実(承認・実行・監査)が起きたことを後から証明できる記録。書込ツールの成功報告のみ
では証跡は成立せず、取得系での読み戻し確認をもって成立する。規格は AUTO-SEAL-STD-001。

### Human Gate(ヒューマンゲート)

人間による明示承認を要する制度上の関門。人間不在の自動承認(GL7 pass 等)で代替しては
ならない。AUTO_SEAL では approved_by=human を成立条件とする(DC_20260713_003)。

補足(GEM-004 反映、DL-C1: DC_20260713_013): Human Gate は承認・採択・発効の唯一の権限主体である。
AI(ChatGPT / Gemini / くろこ)は提案・構造化・検証補助を担うが、状態を Approved / Effective へ
遷移させる権限を持たない。本補足は既存定義を変更せず、AI と人間の権限境界を明文化するものである。

### Traceability(追跡可能性)

ある成果物・決定・証跡から、その根拠と後続へ一意にたどれる性質。AUTO_SEAL では Trigger
(PENDING)と Completion(Seal)を pending_ref で接続することが要件。規格は AUTO-SEAL-STD-002。

### Verification(検証)

記録・成果物・状態が主張どおりであることを実地に確かめる行為。MoCKA の三要素の 1 つ。
UTF-8 妥当性・整合性・動作確認を含む。「ツールが動くこと」と「状態が変わったこと」は
別の検証事項である(Execution Integrity)。

### Audit(監査)

MoCKA ループ第 8 ステップ。検証・署名・封印(Seal)を通じて、記録と状態の整合を確認し
証明する行為。AUTO_SEAL は Audit 出力を anchor_record として固定する。

### Release(リリース)

検証・監査を経た成果物を確定・公開・封印する工程。本 Series では将来の Process Standard
で詳細を定義する(S0 時点では語彙の予約)。

### Conformance(適合)

文書または成果物が Series 規格(Metadata / Identifier / Status / Traceability 等)を
満たしている状態。分類ラベルは AUTO-SEAL-IDX-001 第 4 章、判定規程は将来の Governance
Standard が定義する。

### Fail Closed(フェイルクローズド)

状態が未確定 / 不明のとき、安全側(承認されていない / 実行しない)へ倒す既定動作。
approved_by が human でない場合に Seal を不可とするのはこの具体例。規格は AUTO-SEAL-STD-005。

### Frozen(凍結)

独立した Status 値ではなく、Review Candidate の運用保護属性である(GEM-001 反映、DL-C2:
DC_20260713_014)。レビュー入力のために一時的に編集を停止した状態を指す運用語であり、ライフ
サイクル(Draft -> Review Candidate -> Review Complete -> Human Gate -> Approved -> Effective)上の
状態遷移には含まれない。凍結中の文書の Status は Review Candidate のままである。正規 Status 語彙は
AUTO-SEAL-STD-005 を正本とし、本語は Status 語彙には追加しない(運用属性としての定義に留める)。

### Foundation(基盤)

Series の分類の 1 つ。全文書が従う共通の土台(語彙・構造・不変条件)を定義する。
Process / Governance に依存してはならない(一方向依存)。AUTO-SEAL-ARCH-001 第 2 章。

### Process(工程)

Series の分類の 1 つ。作業の進め方(手順・ゲート・成果物要件)を定義する。Foundation を
参照してよいが、他 Process と循環依存してはならない。AUTO-SEAL-ARCH-001 第 2 章。

### Governance(統治)

Series の分類の 1 つ。制度としての拘束・適合判定・逸脱時の扱いを定義する。Foundation /
Process を参照して適合基準を定める。AUTO-SEAL-ARCH-001 第 2 章。

---

## 2. 用語間の関係(補足)

- Proposal は承認されて Decision となり、Decision に基づく作業が Evidence を生む。
- Evidence は Traceability によってたどれ、Verification によって確かめられ、Audit によって
  封印される。
- Fail Closed は Status(AUTO-SEAL-STD-005)の既定として、Human Gate の実効性を担保する。
- Review Candidate は「Human Gate 承認前(Approved 前)」の意である(GEM-001 V-2 反映、HG-14:
  DC_20260713_024)。本 Series 内で用いる「承認前」「pending Human Gate」は Review Candidate と
  同義の言い換えであり、状態語彙そのものは AUTO-SEAL-STD-005 を正本とする(本注記は用語使用の
  一元化であり、Status 語彙の追加・変更ではない)。

---

## 3. History

- 2026-07-13: 初版(v1.0)。KUROKO-DOC-S0-001 Sprint S0 Phase S0-5。必須 13 用語
  (Proposal / Decision / Evidence / Human Gate / Traceability / Verification / Audit /
  Release / Conformance / Fail Closed / Foundation / Process / Governance)を定義。
- 2026-07-13: S0.5 二次レビュー反映。GEM-004(Major、DL-C1: DC_20260713_013 採用)により Human Gate
  定義へ権限境界の補足を追加。GEM-001(Minor、DL-C2: DC_20260713_014 採用)により Frozen(凍結)を
  運用保護属性として追加(独立 Status 値ではない。STD-005 の正規 Status 語彙 7 値は不変)。反映は
  きむら博士の限定凍結解除(RVW-001 / GLO-001 のみ)による。
- 2026-07-13: 版 re-cut v1.0 -> v1.1(HG-12 / DC_20260713_022)。GEM-001 V-2(Minor、HG-14 /
  DC_20260713_024)反映として第2節へ「Review Candidate = Human Gate 承認前」の用語使用一元化注記を
  追加(Status 語彙変更・Frozen 設計変更・アーキテクチャ変更なし)。S0.5 Series は Review Complete
  (HG-11 / DC_20260713_021)。文書個別 Status 昇格と IDX-001 Master Catalog 同期は全文書版確定後
  (HG-13 / DC_20260713_023)へ繰延。Document ID 不変。改版経路(HG-08)を維持。
