# Genesis Phase Investigation v0.1

分類: Historical Reconstruction
統治方針: docs/governance/GENESIS_PHASE_INVESTIGATION_POLICY_v1.0.md（DC_20260728_006）
一次資料（Founder Narrative）: docs/MOCKA_ORIGIN.md
状態: 初期スケルトン（実データ収集は未実施。本ファイルは構造の器であり、実装履歴の確定記述ではない）

本文書は、MOCKA_ORIGIN.mdの記述から現在の構造を逆算して単一の歴史を作らないこと、
Statement単位でClassification（Confirmed / Source / Founder Narrative / Hypothesis / Unknown / Rejected）を付与すること、
Unknownを推測で埋めないことを前提に維持する。

---

## 1. Evidence

実データ収集（git log横断調査・過去commit分析・events.db横断照合等）は本v0.1時点では未実施。

候補となる一次資料（未分析・未Classification）:

- リポジトリのgit commit履歴（本リポジトリ・mocka-civilization等の関連リポジトリ）
- MOCKA_OVERVIEW.json の session_history欄（2026-03-28以降の日次記録。ただしOVERVIEW自体がstaleness_noteでv4.0時点データのまま未更新である旨を明示しているため、内容をそのままConfirmed扱いにはできない）
- docs/governance配下の各種audit/report文書群（作成日時が個々に異なり、横断的な時系列整理は未実施）
- Decision Ledger（data/decisions/decision_ledger.jsonl）— DC_20260622以降のみ運用開始（TODO_361）。それ以前の意思決定はLedger上に記録されていない

Classification: Unknown（一次資料候補のリストアップのみ。個々の資料内容の検証・分類は未実施）

---

## 2. Timeline

未確定。個々のEvidence精査後に、Statement単位でClassificationを付与しながら構築する。

現時点で確定しているのはFounder Narrative上の日付のみ:

- 2026-04-03: MOCKA_ORIGIN.md記録日（Classification: Founder Narrative / Source: docs/MOCKA_ORIGIN.md）

それ以前（preMoCKA着想期）および、それ以降の各Phaseへの移行時期・移行判断の詳細は Unknown。

---

## 3. Decisions

DC_20260622以降はDecision Ledger（mocka_decision_write）が正本。
それ以前の意思決定記録は本v0.1時点では未整理（Unknown）。

Genesis Phase調査自体に関する決定:

- DC_20260728_006: Genesis Phase調査 統合方針 v1.0（本文書の位置づけを規定）

---

## 4. Unknown

- pre-MoCKA期からMoCKA着想への正確な移行時期・契機の詳細
- AIとの出会いからMoCKA原型確立までの試行錯誤の具体的経緯（採用されなかった案を含む）
- MoCKA -> EBGA -> PHI-OS 等、現在の体系用語に至る各移行点が（当時実際にその順序・意図で発生したか）（現時点ではOriginの記述とこれら設計との概念的対応が未検証）
- Decision Ledger運用開始（DC_20260622前後）以前の意思決定の記録所在

上記はいずれも、今後のEvidence精査で確認が取れるまでUnknownのまま保持する。

---

## 5. Interpretation Boundary

- 本文書内のいかなる記述も、Origin文書の記述から現在の構造を逆算した一本道の歴史として提示してはならない。
- 概念的対応が見て取れる場合も（概念的対応が確認できる）という記述にとどめ、因果関係の確定（Confirmed）とはしない。
- Confirmedを付与できるのは、複数の独立したEvidence（commit・events.db記録・Decision Ledger等）で裏付けが取れた場合に限る。
- Founder Narrative（MOCKA_ORIGIN.md由来の記述）はきむら博士本人の意図・認識の記録として扱い、それ自体を実装史の確定事実（Confirmed）として扱わない。

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-07-28 | 0.1 | 初版。DC_20260728_006に基づく初期スケルトン作成（実データ収集は未着手）。 |
