# Writer/Checker分離とTODO_144の統合可否調査（簡易調査）

作成日: 2026-07-08
作成者: Claude（くろこ）
位置づけ: 指示書「R01査読対応・拡大調査（v2最適化版）」TASK-6 成果物（簡易調査、優先度低）
調査範囲: 調査のみ。**監査官R01指示により新規統合案は作らない。** 既存資産の存在確認と
重複整理に限定する。
一次データ: data/MOCKA_TODO_ARCHIVE.json（TODO_144）、
docs/governance/WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md（2026-07-03作成）、
docs/governance/EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.md。

---

## 0. 調査結論サマリー

**Writer/Checker分離は「新設すべき制度」ではなく「既に設計済みだが未実装のまま
保留になっている既存資産」である。** `docs/governance/WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md`
（2026-07-03、くろこ並行作業指示Task-Bにより作成）に、Writer/Checker/Retry/Ledger/
Human Gateの全フローが制度設計文書として既に存在する。ただし本文書1行目に
「本ファイルはコードではなく制度設計文書である。実装は一切含まない」と明記されており、
コードベース全体をgrepしても実装（class Writer/Checker等）は1件も存在しない。

**TODO_144は、この既存設計とは別物である。** TODO_144は「ファイル変更前後の
強制記録制度」（変更前後をClaude自身が記録する）であり、Checker（独立した客観評価者）
の概念を持たない。両者は重複せず、むしろTODO_144の記録メカニズム
（mocka_write_event）は、Writer/Checker設計のLedger記録ステージ（2.4節）が
そのまま流用できる既存インフラとして機能しうる関係にある。

**最も注目すべき点: WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.mdは、自己点検
（2.6節「自律裁定化リスクの自己点検」）において、本調査TASK-2〜TASK-5で実際に
発見したのと同型のリスク（『Human Gateが実装時に接続されないまま形骸化する』）を
2026-07-03時点で既に予見・明記していた。** これは設計自体の質が低いという意味ではなく、
「設計では回避策が明記されていたにもかかわらず、実装フェーズに進まないまま
5日後に同型の問題が実装コードの側で現実に発見された」という事実として記録する
価値がある。

---

## 1. TODO_144の実体

`data/MOCKA_TODO_ARCHIVE.json`より（status: 完了、2026-06-03実装完了）:

- 責務: Claudeがファイル変更を行う際、変更着手前（INCIDENT/PLAN、WHO/WHAT/WHERE/WHY/HOW+変更前状態）と完了後（FIX/CHANGE、変更後状態・差分・結果）をmocka_write_eventで記録する強制プロトコル。
- **記録者と検証者は同一主体。** 変更前後どちらの記録もClaude自身（変更を行う本人）が行う設計であり、独立した第三者（Checker）による評価ステップは含まれない。
- 2026-07-02の別調査（TODO_144とAUTO_SEALの関係確認）では、`anchor_update.py`・`mocka_git_safe_commit.py`・`app.py`の`auto_audit_loop()`のいずれもTODO_144のフック（`record_file_change`/`record_execution`、structural/execution_governance.py）を参照していないことが確認済みであり、AUTO_SEAL系はそもそもTODO_144の記録対象経路に接続されていない（本調査のTASK-1〜5とも整合する既知の事実）。

**結論: TODO_144は「記録者」役のみを制度化しており、「記録者と検証者が実質的に
同一主体になっているケース」という指示書原文の問いに対する答えは、
『そもそも検証者という役割自体がTODO_144には存在しない』である。**

---

## 2. 監査官R01指定5項目の確認結果（WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md準拠）

| 項目 | 設計上の定義 | 実装状況 |
|---|---|---|
| Writer責務（状態変更可能範囲） | 「作る」のみ。成果物候補+生成メタデータ（試行回数・入力ハッシュ）を出力。**自己採点・自己承認は行わない**と明記（2.1節） | 未実装 |
| Checker責務（検証条件） | Hard Gate基準（Test/Build/構造チェックの3種、Lint/Typeは既存インフラ不在のため対象外と明記、2.3節）に限定した機械的PASS/FAIL/判定保留 | 未実装 |
| Writerの自己承認境界 | **明示的に禁止。**「Writerが自らの成果物についてPASS証跡を生成することは禁止する（自己証明の禁止）」と2.4節に明記。Decision Policy v0.1の「判定するのみ・Approvalを持たない」責務境界と同形の設計 | 未実装（設計原則としては本調査で確認したどの既存コードよりも明確に自己承認禁止を意識している） |
| Ledger接続（検証結果が残るか） | PASS/FAIL/強制停止のいずれも記録対象。mocka_write_event経由での記録を明記（2.4節） | 未実装。ただし記録経路自体（mocka_write_event）はTODO_144が既に確立済みのインフラであり、新規に開発する必要はないと考えられる（推測を含む） |
| TODO_144との重複 | 重複なし（本調査1章の結論） | - |

**Writer提案／Checker認証／System確定の三分離について**: 設計文書2.1節・2.6節で、
Checkerは「次工程に進めてよいという機械的合否のみ」であり最終確定権（Approval）を
持たない、最終確定はHuman Gateが別ステージとして担うと明記されている。**概念設計上は
三分離が成立している。** ただし2.6節は同時に「Hard GateがすべてPASSした場合に
Human Gateが形式的な追認に終わるリスク」を明示的に「未確定・要確認」として
残しており、**三分離が実装レベルで維持されるかどうかは本文書だけでは保証されない**
と設計者自身が認めている。

---

## 3. GPT R01・Gemini・Perplexityとの役割分担との重複

指示書原文が求める「GPT R01・Gemini・Perplexityの既存役割分担とWriter/Checker分離案の
重複」について、docs/governance配下を調査した範囲では、AI別の役割分担を制度として
明文化した文書は発見できなかった（推測: 本調査（TASK-1〜6）自体が体現している
「くろこが実装調査を行い、R01（監査官、本セッションではきむら博士が代行）が
裁定する」という運用パターンが、事実上のWriter（くろこ）/Checker相当（R01の
裁定）に近い形にはなっているが、これはWriter/Checker設計文書が意図する
「機械的Hard Gate判定」とは性質が異なる人間主導の裁定である）。この点は
本調査の範囲では確定情報が得られなかったため、推測に留める。

---

## 4. 現在の制度上の位置づけ

`docs/governance/EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.md` 2.3節時点
（WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md作成前）では、Writer/Checker制度設計は
「保留（Hold）または実験対象」に分類され、「Task-Bの成果物が出た時点で再分類する
前提」と記載されている。Task-B成果物（WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md）は
2026-07-03に完成済みだが、**本調査ではこの再分類が実際に行われたかどうかを示す
Decision Ledger/TODOの記録を発見できなかった（未確認）。** 再分類が行われていない場合、
Writer/Checker設計は約5日間「保留」のまま放置されていることになる。

---

## 5. 推測・未確認の明示

- 3章のAI別役割分担の重複評価は推測を含む。
- 4章の「再分類が行われたか」は本調査では未確認（Decision Ledger全件検索までは
  実施していない簡易調査のため）。
- TODO_144のmocka_write_event経路がWriter/Checker設計のLedger記録にそのまま
  転用できるという評価は、既存インフラからの類推であり実装時に別の制約が
  見つかる可能性がある。

---

## 6. 次工程への申し送り

- **監査官R01指示（新規統合案は作らない）に従い、本調査は既存資産
  （WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md）の存在確認と重複整理に留めた。**
- TASK-7横断マッピングでは、本調査で発見したWRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.mdの
  2.6節（自律裁定化リスクの自己点検）が、TASK-2/4/5で実際に発見した現行コードの
  ギャップ（IC_20260708_004、mocka_update_todoの無検証完了等）を**設計段階で
  既に予見していた**という事実を明記すること。「設計時点で正しく懸念されていたが、
  実装に進まないまま同型の問題が別経路で現実化した」というパターンは、
  Autonomy Ladder・Execution Manifest双方の制度設計を進める際の教訓として扱う価値がある。
- 4章の再分類未確認事項は、Human Gate判断（きむら博士）で確認することを推奨する。
