# Audit Process Extraction v0.1 (Phase A-1)

位置づけ: R01実行指示書「MoCKA Audit Standard v1.0 制定プロジェクト」Phase A-1(Process Extraction)に基づく。対象は今回の監査サイクル(Vocabulary Audit/Cross Reference Audit/CI Failure)で実際に使用された成果物・記録のみとし、新規調査は行っていない。改善案・制度設計・新概念追加・評価・解釈は一切含めない。実際に運用されたプロセスのみを一覧化する。

---

## 1. Fact Collection

### Cross Reference Audit track

- 目的(文書内記載): 役割は制度書記官・実装調整官。評価・改善案・「すべきか」の判断は一切行わない。
- 入力資料: くろこ作業指示(2026-07-04、「Cross Reference Audit(横方向参照監査) + Git状態調査 ― 事実収集フェーズ」最終版)
- 出力成果物: `docs/governance/CROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.md`(137行)
- 完了条件(文書内記載): 「収集した事実を提示した時点で作業を停止し、監査官(R01)およびきむら博士の判断を待つ」
- 担当者: くろこ
- フェーズ遷移条件: 事実提示後、R01分析指示書v1.0の着手指示によりAnalysisフェーズへ移行(event: E20260704_539313880dedf)

### CI Failure track

- 目的(文書内記載): 役割は制度書記官・実装調整官。原因推定・修正案の提示は一切行わない。
- 入力資料: くろこ作業指示(2026-07-04、「GitHub CI Failure(MoCKA Global Rule Guard) ― 事実収集フェーズ」)
- 出力成果物: `docs/governance/CI_FAILURE_FACT_COLLECTION_MOCKA_GLOBAL_RULE_GUARD_v0.1.md`(173行)
- 完了条件(文書内記載): 「収集した事実を提示した時点で作業を停止し、監査官(R01)およびきむら博士の判断を待つ」
- 担当者: くろこ
- フェーズ遷移条件: 事実提示後、R01分析指示書v1.0の着手指示によりAnalysisフェーズへ移行(event: E20260704_539313880dedf)

### Vocabulary Audit track

- 目的: `VOCABULARY_AUDIT_EVALUATION_v0.1.md`(v0.3)の位置づけ記述によれば、事実収集フェーズは「評価・採否の判断をしない」ことが厳守事項だったと記録されている。
- 入力資料に相当する成果物: `docs/governance/VOCABULARY_INDEX_SCAN_EVIDENCE_v0.1.md`(v0.2として言及。本抽出では同文書の本文までは読了していない。git status上の未追跡ファイルとして存在を確認)
- 完了条件: 本抽出調査の範囲では、当該文書自体に記載された完了条件文言は確認していない(`VOCABULARY_AUDIT_EVALUATION_v0.1.md`冒頭の言及からのみ把握)。
- 担当者: くろこ
- フェーズ遷移条件: きむら博士による直接の「評価フェーズへの移行指示」(2026-07-04、8項目の確認質問+層別採点表の要求)。

### 注記(3トラック間の構造差異、観測事実)

Cross Reference・CI Failureの2トラックでは、事実収集フェーズの成果物が直接Analysisフェーズへの入力となっている。一方Vocabulary Auditトラックのみ、事実収集フェーズ(`VOCABULARY_INDEX_SCAN_EVIDENCE_v0.1.md`)とAnalysisフェーズの間に、A~D評価・論点整理を行う「評価フェーズ」(`VOCABULARY_AUDIT_EVALUATION_v0.1.md`のv0.1→v0.2→v0.3)が介在しており、Analysis-01が実際に入力としたのは事実収集フェーズの成果物ではなく、この評価フェーズの最終成果物(v0.3)である。また、この評価フェーズへの移行指示は、他の2トラックにおけるFact Collection→Analysis間の移行指示(R01分析指示書v1.0という形式)とは異なり、きむら博士による直接指示(8項目質問+層別採点表要求)という形式で行われている。

## 2. Analysis

- 入力指示書: R01分析指示書v1.0(2026-07-04、Analysisフェーズ移行指示)
- 目的(着手記録より): 各分析は入力資料を単一の既存文書に限定し、新規調査は行わない。3件は独立分析として扱い、一方の結論を他方の根拠に用いない。修正案・実装案・優先順位・ロードマップ・着手順・採否判断・原因断定は一切行わない。
- 入力資料:
  - Analysis-01(Vocabulary Audit): `VOCABULARY_AUDIT_EVALUATION_v0.1.md`(v0.3)のみ
  - Analysis-02(Cross Reference Audit): `CROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.md`のみ
  - Analysis-03(CI Failure): `CI_FAILURE_FACT_COLLECTION_MOCKA_GLOBAL_RULE_GUARD_v0.1.md`のみ
- 出力成果物: `VOCABULARY_AUDIT_ANALYSIS_v0.1.md`(55行)/`CROSS_REFERENCE_ANALYSIS_v0.1.md`(59行)/`CI_FAILURE_ANALYSIS_v0.1.md`(55行)。各文書共通構成: (1)確認できた事実 (2)事実から導かれる分析 (3)未確認事項 (4)博士判断が必要な事項。
- 完了条件(着手記録より): 「各テーマについて確認できた事実/事実から導かれる分析/未確認事項/博士判断が必要な事項を整理した時点で完了とする」
- 担当者: くろこ
- フェーズ遷移条件: Analysisフェーズ完了記録(event: E20260704_686674221493b)を経て、R01 Decision Preparation指示書v1.0の着手指示によりDecision Preparationフェーズへ移行

## 3. Decision Preparation

- 入力指示書: R01 Decision Preparation指示書v1.0
- 目的(指示書記載): くろこの担当はDecision資料の整理であり、裁定そのものは行わない。共通原則: 採択しない・却下しない・優先順位を決めない・修正案を書かない・実装案を書かない・博士の判断を代行しない。
- 入力資料:
  - Decision-01(Vocabulary Audit): `VOCABULARY_AUDIT_ANALYSIS_v0.1.md`のみ
  - Decision-02(Cross Reference Audit): `CROSS_REFERENCE_ANALYSIS_v0.1.md`のみ
  - Decision-03(CI Failure): `CI_FAILURE_ANALYSIS_v0.1.md`のみ
- 出力成果物: `VOCABULARY_AUDIT_DECISION_BRIEF_v0.1.md`/`CROSS_REFERENCE_DECISION_BRIEF_v0.1.md`/`CI_FAILURE_DECISION_BRIEF_v0.1.md`。各文書共通構成: (1)Analysis要約 (2)博士裁定事項 (3)判断後の影響範囲 (4)未判断事項。
- 完了条件(指示書記載): 3件とも独立したDecision Briefを作成した/裁定事項を整理した/修正案を含めていない/優先順位を付けていない/採択・却下を行っていない/最終判断をすべて博士へ委ねている。
- 担当者: くろこ
- フェーズ遷移条件: くろこが3件のDecision Briefを提出した後、R01によるFinal Decision(FD-001/002/003)の発出によりFinal Decisionフェーズへ移行

## 4. Final Decision

- 入力: 3件のDecision Brief
- 目的(実施内容): 提出されたDecision Briefに対する裁定(承認等)、状態(採択等)、次工程の指定。
- 出力成果物: `R01_FINAL_DECISION_v0.1.md`(くろこが記録者として作成。裁定内容自体の発出者はR01)
- 完了条件: FD-001~FD-003それぞれについて裁定・状態・次工程が示され、監査サイクル完了宣言(Fact Collection→Analysis→Decision Preparation→Final Decisionの4フェーズが一貫して適用されたことの確認)がなされたこと。
- 担当者: 裁定者=R01。記録者=くろこ。
- フェーズ遷移条件: 監査サイクル完了宣言により本サイクル終了。後続として本Phase A(MoCKA Audit Standard v1.0制定プロジェクト)の着手指示に繋がった。

---

## 改訂履歴

- v0.1(2026-07-04): R01実行指示書Phase A-1に基づき新規作成。今回の監査サイクル(Vocabulary Audit/Cross Reference Audit/CI Failure)で実際に使用された成果物・記録のみを対象に抽出。くろこ起草。
