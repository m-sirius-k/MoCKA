# 検証債務解消 Phase 1 終了報告

**役割の確認:** 本フェーズにおける役割は編集者ではなく監査記録者である。7成果物（NIST_REQUIREMENT_CATALOG/MOCKA_NIST_REQUIREMENT_MAPPING/MOCKA_NIST_GAP_ANALYSIS/MOCKA_BEYOND_NIST_ANALYSIS/MOCKA_EVIDENCE_MATRIX/MOCKA_INSTITUTIONAL_COMPLIANCE_AND_BEYOND_SPECIFICATION/MOCKA_INTERNATIONAL_AI_GOVERNANCE_POSITION_PAPER、全てv1.0）本文、Evidence Matrix、Decision Ledgerへの直接変更は本フェーズを通じて一切行っていない。Git commit/push/Release作成も一切行っていない。発見事項は消去せず、判断前の状態のまま記録する。

**実施体制:** 2件のバックグラウンド検証エージェント（Governanceドキュメント13件検証／Decision Ledger全56件+mocka-knowledge-gate検証）に加え、E分類4件（E-001〜E-004）について本セッションが直接、追加の事実確認調査を実施した。

---

## 1. E分類 追加調査結果（E-001〜E-004）

### E-001: PROJECT_501 / MRS-001 commit・push

| 項目 | 内容 |
|---|---|
| 対象 | `mocka-knowledge-gate`リポジトリの制度整合性 |
| 該当箇所 | `docs/research/PROJECT_501_NIST_RUNTIME_GOVERNANCE_ASSESSMENT/README.md`（「commit禁止・push禁止」の明示記述） |
| 参照元 | commit `ecab6c005aa773329a0dd0d4c80c0aba89d59b01`、`git reflog show origin/main`、`mocka_search("PROJECT_501")`/`mocka_search("MRS-001")`、`mocka_list_events(n=40)` |
| 確認結果 | (1) commit metadataより、author/committerとも`NSJP_kimura <m_kimura@nsjp.org>`（きむら博士のgit identity）であることを確認。ただしMoCKAのAI作業は通常このローカルgit configを用いてAIセッションからcommitされる運用のため、authorフィールド単独では「博士本人が手動実行したか」「AIセッションがこのconfigでcommitを実行したか」を区別できない。(2) `git reflog show origin/main`により、commit `ecab6c0`が`update by push`としてorigin/mainの先端に反映されていることを確認＝公開リモートへのpushは事実として成立している。(3) `mocka_search`で"PROJECT_501"・"MRS-001"を検索したが、いずれもevents_hits/knowledge_gate_hits共に0件。(4) 直近40件のevents(2026-07-11 14:20前後を含む範囲)を確認したが、PROJECT_501/MRS-001/knowledge-gate関連のCHANGE_START/CHANGE_DONEイベントは1件も見当たらなかった（同時間帯には本セッション自身のCHANGE_START/CHANGE_DONE、AUTO_SEAL_PENDING、Institution Handshake等は記録されている）。(5) 該当READMEに記載の「commit/push禁止」を許可・解除するDecision Ledger記録も、読了した全56件の中に見当たらなかった。 |
| 問題分類 | **E: 制度矛盾** |
| 最終状態 | **PENDING_DECISION** |
| 推奨対応 | きむら博士へ直接確認: (a) 本コミット/pushはご本人が事後に別途承認・実行されたものか、(b) AIセッションが「commit/push禁止」の明示指示を逸脱して実行した事例か。(b)であれば、当該content(PROJECT_501/MRS-001一式)を正本として扱う前に内容の精査が必要。いずれの場合も、対応するCHANGE_START/CHANGE_DONE記録の欠落は制度記録義務（「記録なき作業はMoCKAとして存在しない」）との不整合であり、別途是正の要否をご判断いただきたい |

### E-002: Decision Ledger件数差異（57 vs 56）

| 項目 | 内容 |
|---|---|
| 対象 | `MOCKA_OVERVIEW.json` / Decision Ledger本体の整合性 |
| 該当箇所 | `mocka_get_overview.current_view.recent_decisions.count` |
| 参照元 | `mocka_get_overview()`（本セッション再取得、`count: 57`）、`mocka_decision_list(status=Active)`（本セッション再取得、応答本文内`"count": 56`、`"broken_lines": 0`、decision_id一意数56を直接カウントし確認） |
| 確認結果 | `mocka_decision_list`ツール自身が応答内で明示的に`"count": 56`・`"broken_lines": 0`を返しており、Ledger本体側でのデータ破損・欠損は確認されなかった（破損行0）。一方`mocka_get_overview`側の`current_view.recent_decisions.count`は57のまま。両者は同一セッション内でほぼ同時に取得したため、時間差による新規decision追加が原因である可能性は低い。原因は「Ledger欠損」ではなく、「`current_view`生成ロジック側の集計方式（表示キャッシュまたは集計ロジック）が`mocka_decision_list`とは異なる母集団・カウント方式を用いている」可能性が高いと判定する。ただし集計ロジックの実装コード自体は本フェーズでは読んでおらず、断定はしていない。 |
| 問題分類 | **E → C相当へ縮小可**（制度矛盾というよりは表示/集計ロジックの不一致の可能性が高いと判明したため） |
| 最終状態 | **PENDING_EVIDENCE** |
| 推奨対応 | `current_view`生成スクリプト（`generator_version: 1.0`と記載されたコード側）を直接確認し、集計対象母集団（例: Superseded/Withdrawnを含む延べ件数か、archiveされた別レイヤーを含むか等）を特定すること。Ledger本体の毀損ではないため、緊急性は高くない |

### E-003: supersedeリネージの整合性

| 項目 | 内容 |
|---|---|
| 対象 | Decision Ledgerの`supersedes`/`superseded_by`双方向整合性 |
| 該当箇所 | DC_20260707_002/003ペア、DC_20260705_008/009ペア |
| 参照元 | `mocka_decision_get("DC_20260707_002")`、`mocka_decision_get("DC_20260707_003")`、`mocka_decision_get("DC_20260705_008")`、`mocka_decision_get("DC_20260705_009")`（本セッションで4件とも直接再取得・確認） |
| 確認結果 | DC_20260707_003は自身の`supersedes`フィールドに`"DC_20260707_002"`を明記し、`decision`本文でも「DC_20260707_002をSupersededとする」と明言している。しかし参照先のDC_20260707_002自身のレコードは`"status": "Active"`、`"superseded_by": null`のままであり、後続決定からの逆参照（backlink）が反映されていないことを直接確認した。DC_20260705_008/009ペアも同型（DC_20260705_009が`supersedes: "DC_20260705_008"`と明記するが、DC_20260705_008側は`status: Active`・`superseded_by: null`のまま）であることを確認した。これはLedgerの読み取り側の解釈ミスではなく、書込み側（`mocka_decision_write`相当）が新規decision作成時に旧decisionの`superseded_by`を自動更新しない実装上の欠落であると判定できる（2ペアとも同一パターンで再現しているため）。 |
| 問題分類 | **D: 意味的不一致（実装欠落として確認済み）** |
| 最終状態 | **VERIFIED_WITH_NOTE**（「supersede関係が存在する事実」自体は本文記述により検証済みだが、「`status`フィールド単独で現行性を判別できる」という前提は無効であることが確定した） |
| 推奨対応 | 7成果物中でDecision Ledgerの`status`フィールド（Active/Superseded/Withdrawn）の信頼性に言及する箇所（Mapping文書 Task 7.3行等）に、「supersede記述はdecision本文には反映されるが、参照先レコードの`status`/`superseded_by`には自動反映されない」という注記を追加する要否をR01審査で検討 |

### E-004: calc_drift_v3 / AEGIS異常検知

| 項目 | 内容 |
|---|---|
| 対象 | `interface/router.py`の実装状態 |
| 該当箇所 | Regression Governance（Beyond-NIST文書§1.6）、Mapping文書 Practice 2.3・3.4行の根拠 |
| 参照元 | `C:/Users/sirok/MoCKA/interface/router.py`直接読取・Python構文解析（`ast.parse`）・インポート試行・`git log`／`git show` |
| 確認結果 | (1) `ast.parse()`により**構文エラーを確認**: 5行目に非印字文字U+FEFF（BOM様文字、ファイル先頭ではなく5行目のimport文直前に混入）が存在し、現状のファイルはPythonとして**パース不能**（`SyntaxError: invalid non-printable character U+FEFF`）。(2) Python文字列レベルの直接検索（デコードエラーを無視した全文検索）でも、`calc_drift_v3`・`classify_anomaly`・`calc_error_rate`・`get_next_event_id`のいずれも**ファイル中に一切存在しない**ことを確認。(3) ファイル冒頭は`import sqlite3`で始まるが、実体は`EVENTS_CSV`・`FIELDNAMES`等CSV時代の別ロジックであり、`MOCKA_OVERVIEW.json`の`router.functions`が説明する内容（AEGIS多指標ドリフト検知等）とは一致しない、別バージョンのファイルである。(4) `git log`で当該ファイルの直近履歴を確認したところ、最新コミットは2026-06-16「AUTO_SEAL_50EVT」（Human Gate未経由の自動commitパターンとして別途Integrity Ledgerで問題視されている種別のコミット）であり、その前には2026-04-05「fix: restore router.py from ChatGPT overwrite」という、CLAUDE.mdのPhase18 Human Gate方針の起源となった事故そのものの復旧コミットが存在する。 |
| 問題分類 | **E: 制度矛盾（確認済み・推測ではなく実測で確定）** |
| 最終状態 | **INVALIDATED**（「`calc_drift_v3`/AEGIS分類器が現行`interface/router.py`に実装・稼働している」という個別の実装主張は、現時点のファイル内容によって直接反証された） |
| 推奨対応 | 7成果物中で本実装を根拠に挙げている箇所（Beyond-NIST文書§1.6 Regression Governance「Operational/Verified」、Mapping文書 Practice 2.3・3.4行「PARTIAL・Operational」）は、この実装レベルの証拠を撤回する必要がある。ただし`data/recurrence_registry.csv`（87件の記録、誤検知77件修正の履歴）自体は別ファイル（データ、コードではない）であり、本調査の対象外・未反証のまま残る。両者を区別した上での成熟度再評価をR01審査で検討されたい。なお本件はコード内容の実物確認により判明したものであり、修正は一切行っていない（構文エラーのままのファイルを変更せず保持） |

---

## 2. Governanceドキュメント13件検証（エージェント報告の確定分類）

| # | 対象 | 該当箇所 | 参照元 | 確認結果(要約) | 問題分類 | 最終状態 | 推奨対応 |
|---|---|---|---|---|---|---|---|
| G1 | Mapping Task 1.3 | TEVV相当機構の根拠 | AUDIT_STANDARD_PHASE1_FACT_COLLECTION_v0.1.md | 実施済み3監査サイクル(FD-001〜003)の裏付けあり、現行評価は保守的すぎる | B | VERIFIED_WITH_NOTE | Implemented/Operationalへの格上げ候補として記録（本フェーズでは変更しない） |
| G2 | Mapping Task 1.3 | 同上 | MOCKA_AUDIT_STANDARD_DRAFT_v0.1.md | 上記3サイクルのみから構成、憶測混入なし | B | VERIFIED_WITH_NOTE | Implementedへの格上げ候補 |
| G3 | Mapping Task 1.3 | 同上 | VERIFICATION_LOG_v0.1.md | 検証対象は`execution-runtime-system`（MoCKA本体とは無関係の別プロジェクト）であり、MoCKA自身のTEVVの直接証拠ではない | D | PENDING_DECISION | 引用範囲を「検証手法の成熟度の根拠」に限定するか、Task 1.3から除外するかをR01判断 |
| G4 | Mapping Task 1.3 | 同上 | GUARANTEE_VERIFICATION_MATRIX_v0.1.md | G1-G10の3分類整理は誠実。G6項目がcalc_drift_v3の実在に疑義を呈しており、これは本報告E-004で確認済みに格上げ | B（本体）／**E-004として別途確定** | VERIFIED_WITH_NOTE | Implemented/Operationalへの格上げ候補。G6由来の懸念はE-004として独立記録済み |
| G5 | Mapping Task 1.4 | 用語統一の実現状況 | VOCABULARY_CONSTITUTION_v0.1.md | 内容自体が用語不統一を誠実に自己申告、現行PARTIAL評価と整合 | A | VERIFIED | 変更不要 |
| G6 | Mapping Task 1.4 | 同上 | TERM-001_REGISTRY_TERMINOLOGY.md | 文書自体「Verification Status: Pending」と自己申告 | C | PENDING_EVIDENCE | 検証債務として登録。きむら博士承認待ちの状態を維持 |
| G7 | Mapping Task 1.4 | 同上 | CATEGORY_REGISTRY_v2.0.md | 「Pending」状態、TODO_ACTIVE.jsonとの正本関係も未確定と自己申告 | C | PENDING_EVIDENCE | 検証債務として登録 |
| G8 | Mapping Practice 6.2 | 「Concept/Implemented」の"Implemented"根拠 | REGISTRY_CHARTER/SCHEMA/SEMANTICS/STATE_MODEL/VALIDATION_v1.0.md（KN-001,004-007） | 全5文書が実装を明示的に除外（「実装は一切含まない」等）。「Implemented」の根拠は存在しない | D | **INVALIDATED**（"Implemented"成分のみ） | 6.2の成熟度から"Implemented"を除去し「Concept」のみに修正することをR01へ提案。`mocka_registry_*` MCPツールが別実装として機能している可能性は未確認のまま残る（別途C登録） |
| G9 | Evidence Matrix INT-06 | KN-Series引用チェーン | KN-003（REGISTRY_RECORD_SPEC_v1.0.md、未読） | SCHEMAが直接参照するが13件のname-onlyリストに含まれず未読のまま | C | PENDING_EVIDENCE | 追加の検証対象として登録 |
| G10 | Evidence Matrix INT-06 | 未使用引用 | MODULE_REGISTRY_MODEL_v1.md | 4分析文書の本文でどのTaskからも実際には引用されていない孤立引用と判明 | B | VERIFIED_WITH_NOTE | Evidence Matrixから除去、または"unused citation"と明記する改善候補として記録 |

---

## 3. Decision Ledger・mocka-knowledge-gate検証（エージェント報告の確定分類、E-001〜004以外）

| # | 対象 | 該当箇所 | 参照元 | 確認結果(要約) | 問題分類 | 最終状態 | 推奨対応 |
|---|---|---|---|---|---|---|---|
| L1 | Evidence Matrix §C | 既存引用7件（DC_20260711_002/001, DC_20260710_005/004, DC_20260708_007/006/001） | Decision Ledger全56件 | 7件全て、タイトル・日付・status完全一致 | A | **VERIFIED** | 変更不要 |
| L2 | 全7成果物横断 | Decision Ledger制度の起点そのものが未引用 | DC_20260705_002（Decision Ledger正式採用の決定） | Decision Ledgerを論じる文書のどこからも引用されていない、最も基礎的な決定の欠落 | C | PENDING_EVIDENCE | 取り込み候補として記録。約20件の未引用関連decision(Human Gate定義DC_20260705_008/009、AI-to-Institution実証DC_20260707_004/007/008等)も同様 |
| L3 | BEYOND_NIST §1.3 | Knowledge Gate評価の対象特定 | `mocka_mcp_server.py`の`search_knowledge_gate()`関数 vs `mocka-knowledge-gate`リポジトリ | 同名だが実体が異なる2つの「Knowledge Gate」（in-process grep検索機能／独立git repo）が現行文書で混同されている | D | PENDING_DECISION | どちらを評価対象とするか明示的に分離することをR01へ提案 |
| L4 | BEYOND_NIST §1.3 | Knowledge Gate成熟度「Concept/Implemented、内容未検証」 | `mocka-knowledge-gate`リポジトリ実地調査（409コミット、2026年4-6月の約4ヶ月休眠、CI無効化、`vercel.json.bak`に未解消コンフリクト残存） | 「内容未検証」は解消され、「文書資産は充実／アプリ層は未ビルド・CI無効・長期休眠」という具体的状態が判明 | B | VERIFIED_WITH_NOTE | 評価文言の精緻化候補として記録 |

---

## 4. 完了条件チェック

- [x] 全A〜E項目、分類済み（E-001〜004個別確認 + Governanceドキュメント10項目 + Decision Ledger/Knowledge Gate 4項目、合計18項目）
- [x] E案件の事実確認結果、記録済み（E-001: PENDING_DECISION／E-002: PENDING_EVIDENCEへ縮小／E-003: VERIFIED_WITH_NOTE／E-004: INVALIDATED、いずれも本セッションでの直接検証により確定）
- [x] 未解決事項、一覧化済み（本報告書 全項目の「最終状態」列に集約）
- [x] 修正対象と判断対象、分離済み（「推奨対応」列は全て将来の判断材料として記載、本フェーズでは一切実行せず）
- [x] 次工程不要な項目、確定済み（L1: VERIFIED＝完全に確定、これ以上の検証不要。G5: VERIFIED＝同様）

---

## 5. 最終状態サマリー

| 最終状態 | 件数 | 内訳 |
|---|---|---|
| **VERIFIED** | 2 | L1（既存Decision Ledger引用7件全て）、G5（VOCABULARY_CONSTITUTION整合） |
| **VERIFIED_WITH_NOTE** | 6 | G1, G2, G4, G10, L4, E-003 |
| **PENDING_EVIDENCE** | 4 | G6, G7, G9, E-002 |
| **PENDING_DECISION** | 3 | G3, L3, **E-001（最重要）** |
| **INVALIDATED** | 2 | G8（6.2の"Implemented"成分）、**E-004（calc_drift_v3実装主張）** |

---

## 検証債務解消 Phase 1 終了報告

本フェーズは監査記録者としての役割に徹し、既存7成果物・Evidence Matrix・Decision Ledgerへの直接変更、Git commit/push/Release作成のいずれも実施しなかった。

E分類4件（E-001〜E-004）について本セッションが直接の事実確認調査を行った結果、E-003（supersedeリネージの実装欠落）とE-004（`calc_drift_v3`/AEGIS実装の不在）は推測ではなく実測により確定した。特にE-004は、7成果物中で「Operational/Verified」と評価している具体的実装が現行コードに存在しないことを直接反証する結果であり、**INVALIDATED**として隔離した。E-001（PROJECT_501/MRS-001の無許可commit/push疑義）は事実関係（push自体の成立、対応するCHANGE_START/CHANGE_DONE記録の不在）までは確定したが、意図・経緯の解釈はきむら博士の判断に委ねる必要があるため**PENDING_DECISION**として隔離した。

全18項目の分類・最終状態は本報告書に確定記録した。次工程（7成果物への反映要否、E-001の事実確認、G8/E-004の評価修正等）は、いずれも本報告書を基礎資料としたR01審査後の判断に委ねる。

**検証債務解消 Phase 1 終了。**
