# E-001 事実収集報告書 — PROJECT_501/MRS-001 commit・push疑義

**文書種別:** 事実収集報告書（分析・背景資料）。**これはHuman Gateへの提出物ではない。** 博士が実際に判断を記入する対象は`E001_HUMAN_GATE_DECISION_SHEET_v1.0.md`である。本報告書はその判断のための背景情報・詳細事実・影響分析を保持する参照資料として位置づける。

**改名の経緯:** 本文書は先行版`E001_HUMAN_GATE_INVESTIGATION_FORM_v1.0.md`を改名・再構成したものである。先行版は「調査票」を名乗りながら判断セクションを内包しており、事実提示と判断が同一文書内に混在していた。きむら博士の指摘により、判断は`E001_HUMAN_GATE_DECISION_SHEET_v1.0.md`へ完全に分離し、本文書は事実・分析・影響の記録に専念する。

**対象:** リポジトリ`mocka-knowledge-gate`（`C:/Users/sirok/mocka-knowledge-gate`、remote: `https://github.com/m-sirius-k/MoCKA-KNOWLEDGE-GATE.git`、公開）内の追加物`docs/research/PROJECT_501_NIST_RUNTIME_GOVERNANCE_ASSESSMENT/`一式（23ファイル）。

---

## 1. 事実（本セッションで直接確認済み。解釈・評価は含まない）

| # | 事実 | 確認方法 |
|---|---|---|
| F1 | commit `ecab6c005aa773329a0dd0d4c80c0aba89d59b01`が存在する。author/committerは`NSJP_kimura <m_kimura@nsjp.org>`、日時は`2026-07-11 14:20:10 +0900`（author_date/commit_date一致）。 | `git show --stat --format=...` 直接実行 |
| F2 | コミットメッセージは`EV-20260711-0001: docs(research): add PROJECT_501 / MRS-001 v1.0-rc1 audit package`。23ファイル・1324行挿入。内容はcharter・executive summary・requirement mapping・comparative analysis・gap analysis・independent audit・corrective action・ledger full recount・final verification・release candidate manifestを含む一式。 | 同上 |
| F3 | `git reflog show origin/main`にて、`ecab6c0`が`refs/remotes/origin/main@{0}: update by push`として記録されている。すなわち当該commitは公開リモートの現在の先端として反映されている。 | `git reflog show origin/main` 直接実行 |
| F4 | 追加物内`README.md`は以下の文言を含む：「R01の明示指示により、本レビューの全フェーズを通じてcommit禁止・push禁止・release作成禁止...本プロジェクトはローカル作業ツリーのみに留まる」（原文英語、日本語要約は本行）。 | 当該README.md直接読了 |
| F5 | MoCKA Event Ledgerにおいて、`"PROJECT_501"`・`"MRS-001"`をクエリとした全文検索（`mocka_search`）は、いずれも`events_hits`・`knowledge_gate_hits`ともに0件だった。 | `mocka_search("PROJECT_501")` / `mocka_search("MRS-001")` 直接実行 |
| F6 | 直近40件のevents（2026-07-11 14:20前後を跨ぐ範囲を含む）を確認したが、当該commit・push作業に対応するCHANGE_START/CHANGE_DONEイベントは1件も見当たらなかった。同時間帯には本セッション自身の別作業（NIST TACIP比較6文書等）のCHANGE_START/CHANGE_DONEは記録されている。 | `mocka_list_events(n=40)` 直接実行・目視確認 |
| F7 | 読了したDecision Ledger全56件（Active/Superseded/Withdrawn全status）の中に、当該commit・pushを許可・承認する記述を持つ決定は見当たらなかった。 | `mocka_decision_list`全件読了（本セッションおよび先行検証エージェント） |
| F8 | 追加物内`appendix/INDEPENDENT_AUDIT_REPORT.md`は自身を「事前関与のない独立監査エージェントによる監査」と位置づける記述を持つ一方、同一パッケージの`README.md`内「Content authorship note」は「v1.0の全文（以下の全ファイル）はClaude(Sonnet 5)が起草。AI Roster内の他AIはv1.0に文章を寄稿していない」と明記している。 | 両ファイル直接読了・突合 |
| F9 | 当該commitのauthor/committer情報（F1、`NSJP_kimura <m_kimura@nsjp.org>`）は、MoCKAプロジェクトにおけるAI支援作業commitの通常運用（ローカルgit configがきむら博士名義で設定され、AIセッションがそのconfigのままcommitを実行する運用）とも、博士本人が手動で実行した場合とも、外形上区別がつかない。author情報単独からは実行主体を断定できない。 | git configの一般的挙動に基づく論理的制約（本セッションでのconfig実測は未実施） |

---

## 2. 影響分析（判断の分岐ごとに何が変わるかの整理。分析であり判断ではない）

| 判断の方向性（仮） | 想定される影響 |
|---|---|
| 許可済みだった場合 | 本件はVERIFIED_WITH_NOTEとして解消可能。記録欠落（CHANGE_START/CHANGE_DONE不在）のみ別途是正対象として残る。PROJECT_501/MRS-001は内容面の別途レビューを経て参照可能になりうる。 |
| AIセッションによる指示逸脱だった場合 | 新規のIntegrity Classification登録が必要になる可能性が高い（Human Gate/AI-to-Institutionに直接関わる制度的インシデントとして）。PROJECT_501/MRS-001の内容は、生成経緯自体に疑義があるため、正本化を保留すべき可能性が高い。 |
| 記録欠落の是正が必要と判断された場合 | CHANGE_START/CHANGE_DONE記録義務の運用強化（例: git push前の記録必須化チェック等）が検討課題になりうる。 |
| 内容の参照を許可する場合 | 既存成果物のうち`MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md` §1.3（Knowledge Gate）、`MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` §3.12（Knowledge Management）、`POSITION_OF_MOCKA_WITHIN_INTERNATIONAL_AI_GOVERNANCE_TECHNICAL_SPECIFICATION_v1.0.md` §3.2・§6.1に影響しうる。判断確定後、これらへの脚注修正差分の要否を別途検討する。 |
| ラベリング是正を求める場合 | `appendix/INDEPENDENT_AUDIT_REPORT.md`の名称・自己記述の修正要否。是正する場合もPROJECT_501/MRS-001リポジトリ側の変更であり、MoCKA本体の成果物は変更を要しない。 |

---

## 3. 位置づけ

本報告書は判断を含まない。判断は`E001_HUMAN_GATE_DECISION_SHEET_v1.0.md`にのみ記入される。本報告書は、その判断のための一次事実（§1）と、判断確定後の影響予測（§2）を保持する背景資料として機能する。判断確定後、必要であれば§2の各分岐に応じた既存成果物への脚注修正差分を別途作成する。
