# MoCKA Audit Standard v1.0 制定プロジェクト — Phase 1: Fact Collection v0.1

位置づけ: R01実行指示書「MoCKA Audit Standard v1.0 制定プロジェクト Phase 1: Fact Collection」に基づく。役割は制度書記官・実装調整官。標準の文言案・条文化は行わない。対象4件(Vocabulary Audit/Cross Reference Audit/CI Failure Analysis/Governance Catalog〈Phase B〉)で実際に運用された手順のみを、events.db記録・各成果物の自己記述から抽出する。新しい理論・未実施の手順は加えない。収集した事実を提示した時点で作業を停止し、R01と博士の判断を待つ。

## 確定状態(Freeze)

本文書は博士指示(2026-07-04)によりこの内容で確定(Freeze)された。以降、本v0.1には追記・修正を行わない(改訂が必要な場合はv0.2以降の新規文書とする)。

対象4件は以下の2区分に分かれる。

- **A. 完了済み(閉じた事例群)**: Vocabulary Audit・Cross Reference Audit・CI Failure Analysis。いずれもFact Collection→(Vocabulary Auditのみ)Evaluation→Analysis→Decision Preparation→Final Decisionまで完了し、R01によるFinal Decision(FD-001/002/003)が確定済み。
- **B. 未完了(開いた実験系)**: Governance Catalog(Phase B)。B-1〜B-6(Submission)までは完了しているが、R01による評価・Final Decisionは本Freeze時点で未確定。標準抽出(Phase 2)の材料としては、Aの完了済み3件とは別枠として扱う。

---

## ① フェーズ構造の抽出

出力形式: `[案件名] / [フェーズ] / [成果物ファイル名] / [開始条件] / [完了条件] / [担当] / [禁止事項] / [例外処理(あれば)]`

### Vocabulary Audit

```
[Vocabulary Audit] / [Fact Collection] / [VOCABULARY_INDEX_SCAN_EVIDENCE_v0.1.md(v0.1→v0.2)] / [きむら博士指示(2026-07-04「MoCKA用語索引 全体スキャン」最終版)] / [収集した事実と根拠を提示した時点で作業を停止し、監査官(R01)およびきむら博士の判断を待つ(文書冒頭・末尾に明記)] / [くろこ] / [評価・採否の判断は一切行わない] / [v0.1提示後、2系統の独立バックグラウンド収集を追加実行しv0.2として追記(第6節)。件数乖離(Human Gate 614件/1205件)の方法論的原因も記録]

[Vocabulary Audit] / [Evaluation(Optional Stage、Fact CollectionとAnalysisの間に介在)] / [VOCABULARY_AUDIT_EVALUATION_v0.1.md(v0.1→v0.2→v0.3)] / [きむら博士による評価フェーズへの移行指示(2026-07-04、8項目の確認質問+層別採点表の要求)] / [v0.3完了条件(第12節に明記): 評価理由の明文化・論点の分類・博士が裁定すべき事項の明確化・改善案/優先順位/採否判断の不記載を満たし、R01の役割を終了、最終裁定をきむら博士へ委ねる] / [くろこ(v0.1)→博士査読指摘反映(v0.2)→くろこ指示書に基づく論点整理(v0.3)] / [優先順位付け・スコアリング・重要度判定・緊急度判定・改善案/対応方法/ロードマップ/実装案の記載を一切行わない] / [v0.2で博士の査読指摘3点(評価基準明文化・呼び出し関係検証・命名ガバナンス軸追加)を反映する改訂が発生。他の2案件(Cross Reference/CI Failure)にはこの査読反映による改訂サイクルは発生していない]

[Vocabulary Audit] / [Analysis(Analysis-01)] / [VOCABULARY_AUDIT_ANALYSIS_v0.1.md] / [R01分析指示書v1.0(2026-07-04、Analysisフェーズ移行指示)] / [確認できた事実/事実から導かれる分析/未確認事項/博士判断が必要な事項の4節を整理した時点で完了] / [くろこ] / [入力資料をVOCABULARY_AUDIT_EVALUATION_v0.1.md(v0.3)のみに限定、新規調査禁止。他のAnalysis(Cross Reference/CI Failure)の結論を根拠に用いることを禁止。修正案・実装案・優先順位・ロードマップ・着手順・採否判断・原因断定を禁止] / [なし]

[Vocabulary Audit] / [Decision Preparation(Decision-01)] / [VOCABULARY_AUDIT_DECISION_BRIEF_v0.1.md] / [R01 Decision Preparation指示書v1.0] / [Analysis要約/博士裁定事項/判断後の影響範囲/未判断事項の4節を整理し、修正案・優先順位・採否を含めず、最終判断を博士へ委ねた時点で完了] / [くろこ] / [採択しない・却下しない・優先順位を決めない・修正案を書かない・実装案を書かない・博士の判断を代行しない] / [なし]

[Vocabulary Audit] / [Final Decision(FD-001)] / [R01_FINAL_DECISION_v0.1.md] / [くろこによる3件Decision Brief提出] / [裁定(承認)・状態(採択)・次工程(制度運用時の基準として利用可能)が示され、監査サイクル完了宣言がなされた時点で完了] / [裁定者=R01、記録者=くろこ] / [記録者(くろこ)は裁定の代行をしない] / [なし]
```

### Cross Reference Audit

```
[Cross Reference Audit] / [Fact Collection] / [CROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.md] / [くろこ作業指示(2026-07-04、Cross Reference Audit+Git状態調査、事実収集フェーズ最終版)] / [収集した事実を提示した時点で作業を停止し、監査官(R01)およびきむら博士の判断を待つ(文書末尾に明記)] / [くろこ(役割: 制度書記官・実装調整官)] / [評価・改善案・「すべきか」の判断は一切行わない。自動修正・自動リンク追加・自動プッシュは行わない] / [なし]

[Cross Reference Audit] / [Analysis(Analysis-02)] / [CROSS_REFERENCE_ANALYSIS_v0.1.md] / [R01分析指示書v1.0] / [4節(確認できた事実/分析/未確認事項/博士判断事項)を整理した時点で完了] / [くろこ] / [入力資料をCROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.mdのみに限定。VOCABULARY_CONSTITUTION_v0.1.mdの記述を「誤り」と断定せず不一致の事実のみ整理。他Analysisの結論を根拠に用いることを禁止] / [なし]

[Cross Reference Audit] / [Decision Preparation(Decision-02)] / [CROSS_REFERENCE_DECISION_BRIEF_v0.1.md] / [R01 Decision Preparation指示書v1.0] / [4節整理・修正案優先順位不記載・最終判断委譲の時点で完了] / [くろこ] / [Vocabulary Auditと同一原則] / [なし]

[Cross Reference Audit] / [Final Decision(FD-002)] / [R01_FINAL_DECISION_v0.1.md] / [くろこによる3件Decision Brief提出] / [裁定(承認)・状態(採択)・次工程(Reference Completenessを独立監査観点として活用)が示された時点で完了] / [裁定者=R01、記録者=くろこ] / [Vocabulary Auditと同一原則] / [なし]
```

### CI Failure Analysis

```
[CI Failure] / [Fact Collection] / [CI_FAILURE_FACT_COLLECTION_MOCKA_GLOBAL_RULE_GUARD_v0.1.md] / [くろこ作業指示(2026-07-04、GitHub CI Failure事実収集)] / [事実提示後に停止。監査官(R01)・きむら博士の判断待ち(文書末尾に明記)] / [くろこ(役割: 制度書記官・実装調整官)] / [原因推定・修正案の提示は一切行わない] / [前回報告(Cross Reference Audit Fact Collection)の誤り(「git exit code 128がjob失敗原因」)を、詳細ログ確認により本文書内で明示的に訂正。実際の失敗原因はステップ3のgrep一致によるexit 1であり、exit 128は別ステップ(Post Checkout、submodule警告)の無関係な事象であることを特定した]

[CI Failure] / [Analysis(Analysis-03)] / [CI_FAILURE_ANALYSIS_v0.1.md] / [R01分析指示書v1.0] / [4節整理の時点で完了] / [くろこ] / [入力資料をCI_FAILURE_FACT_COLLECTION_MOCKA_GLOBAL_RULE_GUARD_v0.1.mdのみに限定。修正方法・Workflow変更・実装修正・GitHub設定変更・原因断定は対象外。他Analysisの結論を根拠に用いることを禁止] / [なし]

[CI Failure] / [Decision Preparation(Decision-03)] / [CI_FAILURE_DECISION_BRIEF_v0.1.md] / [R01 Decision Preparation指示書v1.0] / [4節整理・修正案不記載の時点で完了] / [くろこ] / [Vocabulary Auditと同一原則] / [なし]

[CI Failure] / [Final Decision(FD-003)] / [R01_FINAL_DECISION_v0.1.md] / [くろこによる3件Decision Brief提出] / [裁定(承認)・状態(採択)・次工程(必要に応じ技術対応フェーズへ移行、本裁定に修正内容は含まない)が示された時点で完了] / [裁定者=R01、記録者=くろこ] / [Vocabulary Auditと同一原則] / [なし]
```

### Governance Catalog(Phase B、自案件固有の6工程名)【B. 未完了(開いた実験系) — R01評価・Final Decision未確定】

Governance Catalogは実際にはFact Collection/Analysis/Decision Preparation/Final Decisionという4名称ではなく、指示書自身が定めたB-1〜B-6という固有の工程名で運用された。名称を強制的に読み替えることはせず、実際に使われた名称のまま記録する。本区分(B)はR01によるFinal Decisionが確定するまで、標準抽出(Phase 2)の材料としてAと同列には扱わない。

```
[Governance Catalog] / [B-1: Governance Inventory] / [GOVERNANCE_INVENTORY_v0.1.md] / [R01実行指示書「MoCKA Governance Catalog v1.0 制定プロジェクト」Phase B-1] / [一覧化完了(指示書記載の完了条件)] / [くろこ] / [新制度追加・名称変更・統廃合・優先順位付け・将来構想・推測の禁止] / [なし]

[Governance Catalog] / [B-2: Classification] / [GOVERNANCE_CLASSIFICATION_v0.1.md] / [Phase B-2] / [すべて分類済み(指示書記載)。ただし判別不能事項(Module Governance Series等)は分類不能である旨を明記した状態で完了とした] / [くろこ] / [新しい階層を作らない。分類は既存制度から導ける範囲に限定] / [なし]

[Governance Catalog] / [B-3: Relationship Mapping] / [GOVERNANCE_RELATIONSHIP_MAP_v0.1.md] / [Phase B-3] / [関係整理完了(指示書記載)] / [くろこ] / [制度変更の禁止] / [なし]

[Governance Catalog] / [B-4: Governance Catalog Draft] / [MOCKA_GOVERNANCE_CATALOG_DRAFT_v0.1.md] / [Phase B-4] / [ドラフト完成(指示書記載)] / [くろこ] / [今回実証されていない制度を追加しないこと] / [なし]

[Governance Catalog] / [B-5: Internal Audit] / [MOCKA_GOVERNANCE_CATALOG_INTERNAL_AUDIT_v0.1.md] / [Phase B-5] / [混入ゼロを確認(指示書記載)] / [くろこ] / [実在しない制度・将来構想・推測・制度変更提案の混入、名称変更の有無を確認するのみ] / [なし]

[Governance Catalog] / [B-6: Submission] / [(提出行為そのもの。新規ファイルなし)] / [B-5完了] / [5件の成果物をR01へ提出した時点で完了] / [くろこ] / [内容の追記・修正をせずそのまま提出(後続の博士指示より)] / [提出時、「Phase B(実体層)の評価のみを対象とし、Phase A(方法論層)への言及・提言は本提出物の評価範囲外とする」という博士指示による申し送りを明記した]

[Governance Catalog] / [Final Decision] / [(本Fact Collection時点では未発生)] / [—] / [未完了。R01による分析・評価は本Fact Collection時点では確認できていない] / [裁定者=R01(予定)、記録者=くろこ(予定)] / [—] / [—]
```

---

## ② 停止条件・禁止事項の抽出

### フェーズごとの禁止事項一覧

| フェーズ | 明示された禁止事項 | 対象案件 |
|---|---|---|
| Fact Collection | 評価・採否の判断禁止、改善案禁止、「すべきか」の判断禁止、自動修正・自動リンク追加・自動プッシュ禁止、原因推定・修正案の提示禁止 | Vocabulary/Cross Reference/CI Failure全件共通(文言は案件ごとに若干異なるが趣旨は同一) |
| Evaluation(Optional Stage) | 優先順位付け・スコアリング・重要度判定・緊急度判定禁止、改善案・対応方法・ロードマップ・実装案の記載禁止 | Vocabulary Auditのみ(他2件にはこの工程自体が存在しない) |
| Analysis | 新規調査禁止、他Analysisの結論を根拠に用いることの禁止(独立性)、修正案・実装案・優先順位・ロードマップ・着手順・採否判断・原因断定の禁止 | Vocabulary/Cross Reference/CI Failure全件共通 |
| Decision Preparation | 採択しない・却下しない・優先順位を決めない・修正案を書かない・実装案を書かない・博士の判断を代行しない | Vocabulary/Cross Reference/CI Failure全件共通 |
| Final Decision | 記録者(くろこ)による裁定の代行禁止 | Vocabulary/Cross Reference/CI Failure全件共通 |
| B-1〜B-4(Governance Catalog) | 新制度追加・名称変更・統廃合・優先順位付け・将来構想・推測の禁止 | Governance Catalogのみ |
| B-5(Internal Audit) | 実在しない制度・将来構想・推測・制度変更提案の混入禁止 | Governance Catalogのみ |

### 停止条件の発生有無

**発生したケース**: 本Fact Collectionの対象4件そのものではなく、その前段にあたる旧「Phase A: MoCKA Audit Standard v1.0 制定プロジェクト(2026-07-04、第1回目の試行)」において、Phase A-2(Verification)からPhase A-3(Draft Preparation)への移行時に停止条件(「成果物間に矛盾が見つかった場合」「担当権限を超える判断が必要になった場合」)に該当した。原因は、Vocabulary Auditトラックのみ他の2トラック(Cross Reference/CI Failure)と異なる構造(Fact CollectionとAnalysisの間にEvaluationという工程が介在)を持っていたこと。停止時は「停止理由/確認できた事実/博士判断が必要な事項」の3点のみを報告し、R01の裁定(4点: 正式フェーズは4フェーズ維持/Evaluationは任意工程として付録記載/Analysis入力は直前フェーズの正式成果物/フェーズ移行は承認権限者による)を受けて再開し、Phase A-3/A-4を完了した。

**発生しなかったケース**: Vocabulary Audit/Cross Reference Audit/CI Failureそれぞれの個別のFact Collection→Analysis→Decision Preparation→Final Decisionの各遷移では、停止条件(正本特定不能・複数定義併存・制度間矛盾・名称正当性判断不能・新制度制定必要・担当権限超過)のいずれにも該当せず完了した。Governance Catalog(Phase B)のB-1〜B-6についても同様に停止条件には該当せず完了した(分類不能・判別不能事項は記録したが、これは各フェーズ自身の完了条件が想定する「明記すべき事項」であり、停止条件の発動ではない)。

---

## ③ 独立性維持の実例抽出

- **Vocabulary Audit / Cross Reference Audit / CI Failureの3件Analysis間の分離**: R01分析指示書v1.0の着手記録(event: E20260704_539313880dedf)に「3件は独立分析として扱い、一方の結論を他方の根拠に用いない」と明記。各Analysis文書の冒頭(位置づけ)にも同趣旨の記載がある(例: `VOCABULARY_AUDIT_ANALYSIS_v0.1.md`3行目「他のAnalysis(Cross Reference/CI Failure)とは独立に扱い、それらの結論をここでの分析根拠として用いていない」、`CROSS_REFERENCE_ANALYSIS_v0.1.md`3行目・`CI_FAILURE_ANALYSIS_v0.1.md`3行目も同様の文言)。
- **Phase A(方法論層)とPhase B(実体層)の分離**: 博士指示(前回セッション)により、Governance Catalog Phase B-6提出時の申し送りとして「Phase B(実体層)の評価のみを対象とし、Phase A(方法論層)への言及・提言は本提出物の評価範囲外とする」ことが明示的に運用された(本Fact Collection作成時点の直前のやり取りで確認)。

---

## ④ Phase 1の境界イベントログ(標準抽出Phase 2の材料ではない)

以下2件は、Phase 1(Fact Collection)の実行過程で発生した境界事象の記録である。標準抽出(Phase 2)がこれらを標準の構成要素として扱うかどうかは別途の判断を要するため、本節はあくまで「Phase 1実行時に起きた事象のログ」として位置づけ、Phase 2への接続・反映方法については何も述べない。

- **CI Failure Fact Collectionにおける前回報告の自己訂正**: `CI_FAILURE_FACT_COLLECTION_MOCKA_GLOBAL_RULE_GUARD_v0.1.md`冒頭に「くろこ作業指示(GitHub CI Failure事実収集)完了、前回報告の訂正を含む」と明記。前回(Cross Reference Audit Fact Collection内)で「git exit code 128がjob失敗原因である」と記載していたが、詳細ログ確認の結果これが誤りであったことを本文書内で明示的に訂正した(実際の失敗原因はステップ3のgrep一致によるexit 1、exit 128は別ステップの無関係な事象)。
- **META_OBSERVATION_LOG_v0.1.mdの同種性検証(一時開封)**: 博士指示により、通常のFact Collection→Analysis→Decision Preparation→Final Decisionという標準フローの外側で、「保存」でも「評価」でもない「検証のみの一時開封」という第三の状態が運用された。判定結果(同種/異種/判定不能)はmocka_write_eventのみに記録し、恒久的なgovernance文書としては保存しなかった(通常の成果物作成パターンからの意図的な逸脱)。

---

以上、確認できた事実の提示をもって本フェーズの作業を停止する。標準文言案・条文化・改善提案は行っていない。R01と博士の判断を待つ。

本文書は上記の通りFreeze済みである。Governance Catalog(Phase B-6)についてR01による評価・Final Decisionが確定するまで、Phase 2(Analysis/標準抽出)には着手しない。Final Decisionが確定した時点で、その旨をmocka_write_eventに記録し博士へ報告する。それまでは新たな作業を行わず待機する。

---

## 改訂履歴

- v0.1(2026-07-04): R01実行指示書「MoCKA Audit Standard v1.0 制定プロジェクト Phase 1: Fact Collection」に基づき新規作成。くろこ起草。
- v0.1 Freeze(2026-07-04): 博士指示に基づき本内容で確定(Freeze)。Governance Catalogを「B. 未完了(開いた実験系)」、Vocabulary Audit/Cross Reference Audit/CI Failureを「A. 完了済み」として区分を明記。例外処理2件を「Phase 1の境界イベントログ」として位置づけラベルを修正。以降本v0.1への追記・修正は行わない。くろこ起草。
