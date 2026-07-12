# MoCKA vs NIST AI RMF / TACIP Gap Analysis v1.0

**対象資料:** `DiscussionDraft_NIST_AIRMF_TACIP_20260707.pdf`（NIST AI RMF Profile on Trustworthy AI in Critical Infrastructure, Community of Interest Discussion Draft, Jul 7 2026。ステータス: "NOT OFFICIAL GUIDANCE, FOR DISCUSSION ONLY"）

**目的:** NIST AIRMF/TACIP側が求めるAIガバナンス要件を正確に読み取り、MoCKA 1.0が現時点でどこまで達成しているか、また要求水準を超えて独自発展している領域はどこかを、証拠付きで明確化する。**「MoCKAが優れている」ことの主張ではなく、相手基準に基づく実証状態の監査可能な比較**である。

**継承する既存証拠:** 本文書は`NIST_REQUIREMENT_CATALOG_v1.0.md`（NIST全53Task抽出済み）、`MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md`、`MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md`、および直近の`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md`（E-001〜E-004の実測確認結果）を継承する。既存成果物本文は書き換えていない。特に、Phase1終了報告で**INVALIDATED**と確定した`calc_drift_v3`/AEGIS実装の不在、**PENDING_DECISION**のPROJECT_501/MRS-001無許可push疑義、Knowledge Gateの名称衝突（`search_knowledge_gate()`関数 vs `mocka-knowledge-gate`リポジトリ）は、本文書でも同じ評価を維持し、格上げ・隠蔽は行わない。

**評価基準（新規4段階、本文書専用）:**
- **NONE**: 対応なし、または証拠が確認できない
- **PARTIAL**: 一部対応、設計のみ、または実装はあるが未検証・運用実績不足
- **ACHIEVED**: 要求を実装・運用の両面で満たすことが証拠により確認できる
- **ADVANCED**: 要求を超えて独自発展しており、かつ「なぜ超えているか」を証拠付きで説明できる場合のみ使用（推測での付与は禁止）

不明な項目はPARTIALまたはNONEとし、推測でACHIEVED/ADVANCEDと判定しない。

---

## 1. Executive Summary

MoCKAはCritical Infrastructure運用者ではなく、AI支援作業を対象とした制度的ガバナンスシステムである。NIST TACIPが前提とする物理OT/ICS環境（バルブ・PLC・SCADA・医療機器等）はMoCKAに存在しないため、そもそも比較対象になりえない要求領域が一定数存在する（詳細は既存の`MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md`参照）。

本文書は12分類（Governance/Accountability/Risk Management/Human Oversight/Transparency/Explainability/Traceability/Verification-Validation/Documentation/Monitoring/Incident Management/Knowledge Management）で相手要求を再整理し、MoCKA資産と対応付けた結果、**ACHIEVED以上と判定できたのは12分類中5分類、PARTIALが6分類、NONEが1分類**という結果になった（詳細は§3）。ADVANCEDと判定したのは**Incident Management（Integrity Classification Ledgerの自己監査履歴）の1件のみ**であり、これも「NIST側の該当実装例が現時点でTBDプレースホルダのみである」という限定的な比較優位に基づくものであって、無条件の優位主張ではない。

同時に、直近の検証債務解消フェーズで確定した2件の重大な留保事項（Regression Governanceの中核実装`calc_drift_v3`が現行コードに不在であること、Knowledge Gateの名称衝突と一部content の無許可push疑義）を、本文書でも隠さずそのまま引き継ぐ。

---

## 2. NIST AIRMF/TACIP要求一覧（12分類での再整理）

NIST文書自体は12 Practice / 53 Taskの構造を持つが、指定の12分類は文書の分類軸とは異なる横断的な軸である。各分類がどのNIST Practice/Taskに主に対応するかを示す。

| 分類 | PDF内の対応する主な要求内容 |
|---|---|
| **Governance** | Practice 3（自動化・エージェント行動へのリスク・方針・監督の定義）、AI RMF Govern機能全般（全Practiceに横断的に付与されるGovern 1.x/2.x/3.x/4.xマッピング） |
| **Accountability** | Govern 2.1（役割・責任・コミュニケーション）、Govern 2.3（経営層の責任）、Practice 8.3（AIインシデント統治の役割指定） |
| **Risk Management** | Practice 3.1（リスクトレードオフの特定）、Practice 3.1.3（許容リスク閾値と対応の定義） |
| **Human Oversight** | Practice 4（緊急回避・オーバーライド・復旧・状況認識手順）、Practice 3.6（自動化慢心・スキル低下の緩和）、Practice 4.5（human-on/out-of-the-loop運用体制） |
| **Transparency** | Trustworthy Characteristic「Accountable & Transparent」、Practice 10（多層ロギング・監査能力） |
| **Explainability** | Trustworthy Characteristic「Explainable & Interpretable」、Practice 8.1.2（SHAP/LIME等事後説明ツールを法的証拠として扱わない旨の明記） |
| **Traceability** | Practice 10.1.2（Immutable Runtime Telemetry）、Practice 12.1.2（Provenance and Traceability） |
| **Verification/Validation** | Practice 1.3（TEVV導入）、Practice 2.3（体系的TEVV実施）、Practice 12.2（多層検証） |
| **Documentation** | Practice 1.3.4（監査対応可能なTEVVエビデンス生成）、Practice 7.1（内部AI展開レジストリ維持） |
| **Monitoring** | Practice 3.4（異常AI行動の監視）、Practice 10.3（体系的監査レビューとトレンド分析） |
| **Incident Management** | Practice 8（AI対応インシデント分析・対応手順全体） |
| **Knowledge Management** | Practice 7（内部AIサプライチェーン・データ来歴管理）— NIST文書には「Knowledge Management」に一対一で対応する専用Practiceは存在せず、最も近接する既存概念として扱う |

---

## 3. MoCKA対応マッピング表

各項目について、要求項目／PDF内の要求内容／MoCKA対応／対応する制度・実装／証拠／評価／差分／推奨対応を記載する。

### 3.1 Governance

**要求項目:** Practice 3冒頭「Establish well-defined, deterministic, actionable boundaries, policies, and oversight」／Govern 1.1・1.2・1.4・2.1・2.3・3.2・4.1（全Task共通で頻出）

**PDF内の要求内容:** 高リスクAI行動への明確で決定論的な境界・方針・監督体制を確立すること。経営層がAIリスクの意思決定に責任を持つこと。

**MoCKA対応:** MoCKA Constitution（5原則: "Event ledger is append only" / "All decisions preserve 5W1H" / "Infield is internal memory" / "Outfield is collaborative interface" / "Event history is the single source of truth"）、Human Gate write_policy（Phase18以降コアシステムファイルへの書込は人間ゲート承認必須）

**対応する制度・実装:** MOCKA_OVERVIEW.json `constitution` / `governance.write_policy`

**証拠:** `mocka_get_overview()`直接取得（本セッション複数回確認）。Constitutionは全セッションで一貫して同一内容。

**評価:** **PARTIAL**

**差分:** Constitution・write_policyという明文化された統治原則自体は確認できるが、`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md` E-001（IC_20260708_004由来）で確認した通り、少なくとも1つの実行経路（`/audit/seal`）でHuman Gateの明示承認を経ずにコアな封印操作が実行可能な状態が現存する。方針の「宣言」と「執行」の間にギャップがある。

**推奨対応:** IC_20260708_004の是正（Human Gate未接続実行経路の解消）を、Governance分類の評価をPARTIALからACHIEVEDへ引き上げるための最優先前提条件とする。

---

### 3.2 Accountability

**要求項目:** Govern 2.1・2.3／Practice 8.3「Designate roles for AI incident governance」

**PDF内の要求内容:** AIリスクに関する役割・責任・コミュニケーション経路を明確化し、経営層がAIリスク判断の責任を負うこと。

**MoCKA対応:** Decision Ledgerの`approved_by`フィールド（全決定が個人名または役割名に紐付く）、「監査官R01」という繰り返し登場する裁定役割パターン

**対応する制度・実装:** `mocka_decision_get`で取得した個別decisionレコード（例: DC_20260707_003 `"approved_by": "きむら博士(監査官R01名義での裁定)"`）

**証拠:** 本セッションで直接取得したDC_20260707_002/003、DC_20260705_008/009等、全てのdecisionレコードに`approved_by`が明記されていることを実測確認済み。

**評価:** **ACHIEVED**

**差分:** 個々の決定に対する責任者明記という点では要求を満たす。ただし「経営層」に相当する役割が実質的にきむら博士一名に集中しており、NISTが想定する複数ステークホルダーによる責任分散構造（Practice 8.3の"cross-functional AI Incident Response Team"）とは規模・構造が異なる。

**推奨対応:** 現状で不足はないが、将来的に組織規模が拡大した場合の役割分散設計は未検討のまま。

---

### 3.3 Risk Management

**要求項目:** Practice 3.1「Identify risk tradeoffs」／Practice 3.1.3「Define acceptable risk thresholds and associated control responses」

**PDF内の要求内容:** AIシステムのリスクトレードオフを特定し、影響severity・可能性・回復可能性に基づく許容リスク閾値と、それに紐づく組織的対応（隔離・権限制限等）を定義すること。

**MoCKA対応:** Integrity Classification Ledger（31件、`state`: Failure/Risk/Unknown の3分類）

**対応する制度・実装:** `mocka_integrity_list()`

**証拠:** 本セッションで全31件を直接読了。各レコードが`detection_method`・`impact_scope`・`status`（Open/Resolved）を保持することを確認済み。

**評価:** **PARTIAL**

**差分:** リスクの「特定・分類・記録」は強く実証されている。しかしNISTが求める「許容リスク閾値の事前定義」および「閾値超過時の組織的対応（自動隔離・権限縮小等）」に相当する明文化された仕組みは、本セッションの調査範囲内では確認できなかった。MoCKAのIntegrity Ledgerは事後分類が中心であり、事前の閾値設計は別レイヤー（未確認）に存在する可能性がある。

**推奨対応:** リスク閾値の事前定義文書が存在するか、追加調査で確認すること。存在しない場合はPARTIALのまま、NIST 3.1.3相当の設計を新規検討課題として登録。

---

### 3.4 Human Oversight（重点確認対象）

**要求項目:** Practice 4「Define procedures for emergency avoidance override, recovery, and situation awareness」／Practice 4.5「Define operational regimes for human-on-the-loop and human-out-of-the-loop operation」

**PDF内の要求内容:** AI行動を安全に停止・介入できる「break glass」手順の確立。人間がリアルタイム監視できない場面（human-out-of-the-loop）では、決定論的な自動保護機構に責任を移譲すること。

**MoCKA対応:** Human Gate（`phi_os/human_gate.py`、`app.py`の決定/承認エンドポイント、`mocka_git_safe_commit.py`の`human_gate_override_event_id`パラメータ）、COMMAND CENTER TICパネル

**対応する制度・実装/証拠:**
- DC_20260705_008（Human GateをDecision EngineではなくState Management Layerとして定義する決定）: 「自動検知系はPENDING投入のみを担当し、可否判断には一切関与しない」「approve()/reject()の呼び出しは、実際に人間がUI/APIを操作した場合にのみ許可する。自動ロジック・推論結果による呼び出し経路は一切設けない」と明記。本セッションで直接取得・確認済み。
- COMMAND CENTER TICパネル（Layer 4、Human Gate UI相当）は`mocka_get_overview().tic.layer4`に「未着手（TODO_207）」と明記されており、実装未達であることを確認済み。
- IC_20260708_004（`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md` E-001で本セッションが直接再確認）: `/audit/seal`実行経路がGL7の機械的ALLOWのみで完結し、DC_20260705_008が定義した「人間操作のみに限定する」という原則が、少なくともこの1経路では守られていない。

**確認（ユーザー指定の重点論点への回答）:** DC_20260705_008の文言を読む限り、Human Gateは単なる「確認工程」ではなく、**明示的に制度的判断点として設計**されている（「Decision EngineではなくState Management Layer」という定義そのものが、責務を意図的に分離する設計判断である）。しかし**設計と実装執行の間に確認済みのギャップが存在**しており、「制度的判断点として設計されているが、全経路で執行されているとは実証できていない」というのが証拠に基づく正確な評価である。

**評価:** **PARTIAL**

**差分:** 設計思想の明確さ・厳密さは高く評価できるが、(1) 実行経路レベルでの逸脱が最低1件確認済み（IC_20260708_004、Open）、(2) COMMAND CENTER TICパネル（Human Gate UI）が未実装、という2点で「要求達成済み」と判定するには証拠が不足する。

**推奨対応:** IC_20260708_004の是正を最優先。TODO_207（TIC Layer 4）の着手判断をR01審査で検討。

---

### 3.5 Transparency

**要求項目:** Trustworthy Characteristic「Accountable & Transparent」／Practice 10「Implement multi-tiered AI system logging and audit capabilities」

**PDF内の要求内容:** AI駆動処理の可視性を確保し、規制監督・事後調査を支援する多層ロギング体制を構築すること。

**MoCKA対応:** Event Ledger（append-only、15,000件超）、mocka-transparency リポジトリ（役割: 改ざん検知・署名検証デモ層）

**対応する制度・実装:** `events.db`、`mocka_list_events`/`mocka_read_event`

**証拠:** `mocka_get_overview().current_view.recent_events.count`（本セッション時点で15,412件）。mocka-transparencyリポジトリは存在確認のみ（`mocka_get_overview().repositories.transparency`）で、**内容は本文書の調査範囲内では未検証**。

**評価:** **PARTIAL**

**差分:** Event Ledger自体は強く実証されたTransparencyの基盤である。一方、mocka-transparencyという専用リポジトリの内容は名称と役割説明のみに依拠しており、Knowledge Gateで確認されたのと同様の「存在確認のみで内容未検証」という状態にある可能性がある（既存の`MOCKA_EVIDENCE_MATRIX_v1.0.md`と同じ限界）。

**推奨対応:** mocka-transparencyリポジトリの内容検証を、Knowledge Gate検証と同様の方式（別セッションでの直接確認）で実施することを推奨。

---

### 3.6 Explainability

**要求項目:** Trustworthy Characteristic「Explainable & Interpretable」／Practice 8.1.2「post-hoc explainability tools such as SHAP/LIME should not be treated as forensic proof」

**PDF内の要求内容:** AI決定の「なぜ」を統計的事後推測ではなく実際の意思決定過程から説明できること。

**MoCKA対応:** Decision Ledgerの`context`/`alternatives`/`rationale`/`impact`フィールド構造

**対応する制度・実装:** `mocka_decision_get`のレスポンス構造

**証拠:** DC_20260707_003を例に取ると、`alternatives`フィールドに却下案とその却下理由（例: 「Decision Ledgerから削除する→事実を消さない原則に反するため却下」）が明記され、`rationale`フィールドに「なぜこの判断に至ったか」の理由付けが記述されている。これは統計的事後推測（SHAP/LIME型）ではなく、**意思決定時点で記録された一次的な理由付け**である。

**評価:** **ACHIEVED**（Decision Ledgerが対象とする「制度的判断」の説明可能性について）／**NONE**（MoCKAは機械学習モデルを訓練・運用しておらず、モデル出力レベルの説明可能性は対象外）

**差分:** NISTのExplainability要求は主にAIモデル出力の説明可能性を指すが、MoCKAが有するのは「制度的意思決定」レベルの説明可能性である。対象レイヤーが異なるため、単純な優劣比較はできない。ただし、意思決定過程を却下案・理由付きで記録するという点は、NIST 8.1.2が警告する「事後の統計的再構成」問題への構造的な回避策になっている。

**推奨対応:** 本評価の二重性（Decision-level: ACHIEVED、Model-level: NONE/対象外）を明示した上で、他分析との混同を避ける。

---

### 3.7 Traceability（重点確認対象）

**要求項目:** Practice 10.1.2「Immutable Runtime Telemetry and Artifact Tracking」／Practice 12.1.2「Provenance and Traceability」

**PDF内の要求内容:** AI判断履歴を、後から改変不能な形で、モデルバージョン・プロンプト・推論コンテキストまで遡って追跡可能にすること。

**MoCKA対応:** Decision Ledger（`related_events`/`related_documents`フィールドによる相互参照）、Event Ledger（`E{YYYYMMDD}_{NNN}`一意ID）

**確認（ユーザー指定の重点論点への回答）:** 「単なるログ保存なのか、意思決定再構成まで達成しているか」について、本セッションが実際にDC_20260708_003を起点に相互参照を辿った結果（`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md`セクション3参照）、`related_documents`に`DC_20260708_007`・`IC_20260707_006`・`IC_20260708_002`・具体的なドキュメントパスが列挙されており、**単なるログ保存を超えて、特定commitから裁定決定までの意思決定再構成が実際に可能**であることを実地で確認した。これは「ログが存在する」という主張ではなく、「実際にログを辿って再構成した」という実証である。

**評価:** **ACHIEVED**

**差分:** 意思決定再構成という核心機能自体は実証済み。ただし`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md` E-003で確認した通り、`supersedes`関係が新決定側の本文には記録されるが、参照先の旧決定レコード側の`superseded_by`フィールドには自動反映されないという書込側の実装欠落が確認されている。これは「双方向からの機械的なlineage追跡」には支障があるが、「本文を読めば追跡できる」という意味でのTraceability自体は損なわれていない。

**推奨対応:** `superseded_by`自動更新の実装により、機械的な双方向追跡精度を向上させる余地がある（優先度: 中）。

---

### 3.8 Verification / Validation（重点確認対象）

**要求項目:** Practice 1.3「Implement evaluation and test plans, including TEVV, across the AI lifecycle」／Practice 2.3「Establish protocols for and regularly perform systematic TEVV」

**PDF内の要求内容:** AIライフサイクル全体にわたる体系的テスト・評価・検証・妥当性確認（TEVV）を実施し、監査対応可能なエビデンスを継続的に生成すること。

**MoCKA対応:** AUDIT_STANDARD（`AUDIT_STANDARD_PHASE1_FACT_COLLECTION_v0.1.md`等）、Caliber（`caliber/chat_pipeline/mocka_caliber_server.py`、`caliber/stress/`配下のストレステスト問題集）、GUARANTEE_VERIFICATION_MATRIX（G1-G10の稼働状況マトリクス）、Shadow Movement（`docs/architecture/SHADOW_MOVEMENT_PRINCIPLE.md`）

**確認（ユーザー指定の重点論点への回答）:** 「単発評価なのか継続検証制度なのか」について、証拠は**二層に分離**する必要がある。

(1) **継続検証制度として実証されている部分:** 検証エージェントが確認した通り、AUDIT_STANDARD系文書は「実施済み3監査サイクル（Vocabulary/Cross-Reference/CI-Failure Audit、各FD-001〜003で確定）」という反復実績を持ち、単発ではなく制度化された監査サイクルとして機能している。GUARANTEE_VERIFICATION_MATRIXも10件のguaranteeを継続的に稼働中/設計のみ/不明の3分類で追跡する仕組みである。

(2) **単発どころか現在機能していないことが確認された部分:** `VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md` E-004で本セッションが直接実測した通り、Regression Governanceの中核実装とされていた`interface/router.py`の`calc_drift_v3`/AEGIS異常検知は、**現行ファイルに構文エラー（U+FEFF非印字文字混入）があり、該当関数群が一切存在しない**ことを`ast.parse`および文字列検索で確認済み（INVALIDATED）。「継続的ドリフト検知」という自動化されたTEVV相当機構は、現時点では**主張と実態が一致していない**。

**評価:** **PARTIAL**

**差分:** 制度としての監査サイクル（AUDIT_STANDARD系）は継続検証制度として実証されているが、自動化されたドリフト検知（calc_drift_v3）は実装が失われている（または他の場所に移動している可能性があるが本セッションでは未発見）。NISTが求める「体系的かつ反復的なTEVV」のうち、人間主導の監査サイクル部分はACHIEVEDに近いが、自動化部分はNONEに近い。両者を平均してPARTIALとする。

**推奨対応:** `calc_drift_v3`の復旧または移設先の特定を優先課題とする。AUDIT_STANDARD系の監査サイクルは継続を推奨。

---

### 3.9 Documentation

**要求項目:** Practice 1.3.4「Generate and maintain audit-ready TEVV evidence」／Practice 7.1「Maintain an Internal Registry of AI Deployments」

**PDF内の要求内容:** 監査対応可能な形でTEVVエビデンスを生成・維持し、内部AI展開の一覧を管理すること。

**MoCKA対応:** `docs/governance/`配下180件超のドキュメント資産、`MOCKA_OVERVIEW.json`（内部資産一覧を兼ねる）

**証拠:** ディレクトリ一覧（本セッション確認）。ただし`MOCKA_OVERVIEW.json`自身の`meta.staleness_note`が「本文はv4.0(2026-06-18)時点のまま未更新であり、TODO_384以降...等の作業が反映されていない」と自己申告している。

**評価:** **PARTIAL**

**差分:** 文書量・体系性は極めて充実しているが、正本ファイル自体が自らの陳腐化を認めている状態であり、「監査対応可能」の要件のうち「最新性」の部分に明確な既知の欠落がある。

**推奨対応:** 既存の是正計画（「自動生成候補→Integrity Check→Human Gate→seal更新」方式）の実施状況をR01審査で確認。

---

### 3.10 Monitoring

**要求項目:** Practice 3.4「Monitor for anomalous AI behavior」／Practice 10.3「Implement systematic audit review and performance trend analysis」

**PDF内の要求内容:** AI行動の異常を継続的・リアルタイムで監視し、監査ログのトレンド分析を行うこと。

**MoCKA対応:** TIC（Technology Intelligence Caliber）Layer 0-1（`health_check.py`、`tech_watcher.py` v3.0）

**証拠:** `mocka_get_overview().tic`: layer0「稼働中」、layer1「稼働中（意味差分検知・TODO_208完了）」、layer2-4は「未着手」と明記。

**評価:** **PARTIAL**

**差分:** 基礎監視層（Layer 0-1）は稼働が確認できるが、影響分析（Layer 3）・Human Gate UI（Layer 4）を含む上位層は未着手であることが正本記録自身に明記されている。またリアルタイム異常検知の一部（calc_drift_v3、§3.8参照）が実装欠落状態にあることも監視能力に影響する。

**推奨対応:** TIC Layer 2-4着手の優先順位判断をR01審査で検討。

---

### 3.11 Incident Management

**要求項目:** Practice 8「Incorporate AI-aware incident analysis and response procedures」全体、特に8.1「Identify scenarios requiring deterministic root cause analysis」

**PDF内の要求内容:** AI関連インシデントの根本原因分析・対応手順を確立すること。事後の統計的説明（SHAP/LIME等）を法的証拠として扱わないこと。

**MoCKA対応:** Integrity Classification Ledger（31件）

**証拠:** 各レコードが`detection_method`に機械的な検証手順（例: IC_20260708_003「git log全AUTO_SEAL_50EVTコミット(5962件)とis_core_system_file()判定ロジックを機械的に突合する監査」）を明記し、`status`のOpen/Resolved遷移、解決時のcommit参照まで記録されている。

**評価:** **ADVANCED**

**ADVANCED判定の根拠（NIST要求／MoCKA制度／実装／運用／証拠の比較）:**
- **NIST要求**: Practice 8.1のImplementation 8.1.1〜8.1.5は、PDF原文において大部分が`(TBD — suggestions welcome)`のプレースホルダのままであり、根本原因分析の完成された実例をPDF自体は提示していない。
- **MoCKA制度**: Integrity Classification Ledgerという専用の制度が存在し、Failure/Risk/Unknownの3状態と、Open/Resolvedのライフサイクルを持つ。
- **実装**: `mocka_integrity_list`/`mocka_integrity_get`/`mocka_integrity_write`という専用MCPツールとして実装されている。
- **運用**: 本セッションで確認した31件は、2026-07-05から2026-07-08にかけて継続的に生成・解決されており、単発ではなく運用中の制度であることが確認できる。
- **証拠**: 個々のレコードに機械的検証手順・影響範囲・解決コミットハッシュが記載されている（例: IC_20260708_002はcommit `b66af6c63`を明記）。

**差分:** NIST側がまだ書き込んでいない領域を、MoCKA側は運用実績付きで先行している、という限定的な優位性である。NIST文書が今後Practice 8の内容を充実させた場合、比較は変化しうる。

**推奨対応:** 現状維持。継続的な運用実績の蓄積が最大の資産であるため、Integrity Ledgerの記録義務を今後も維持すること。

---

### 3.12 Knowledge Management（重点確認対象）

**要求項目:** Practice 7「Manage internal AI supply chain and data provenance」（NIST文書に「Knowledge Management」専用Practiceは存在しないため、最近接概念として扱う）

**PDF内の要求内容:** AIシステムに使用される内部データ・知識の来歴・バージョン管理・保持ポリシーを文書化すること。

**MoCKA対応:** Knowledge Gate、Institutional Memory（essenceパイプライン: RAW→REDUCED→RE_REDUCED→REDUCING→CORE→ESSENCE）、Decision Unit（Decision Ledgerの原子的単位としての設計）

**確認（ユーザー指定の重点論点への回答）:** 「保存を超えて継承制度になっているか」について、証拠は**肯定的な部分と否定的な部分の両方**がある。

**肯定的証拠:** `MOCKA_OVERVIEW.json`は「新しいchatにこれ1つ貼れば即作業開始できる完全マスターファイル」として明示的に設計されており、essenceパイプラインは単なる保存ではなく多段階の濃縮処理（RAW→ESSENCE）を経る。これは記憶を持たない新規AIセッションへの知識継承を目的とした制度であり、「保存」を超えている。

**否定的証拠（`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md`から継承、格上げ・隠蔽なし）:**
1. 「Knowledge Gate」という名称が、実際には2つの無関係な実体（`mocka_search`内の`search_knowledge_gate()`関数＝`C:/Users/sirok/MoCKA/data/`配下のgrep検索と、独立リポジトリ`mocka-knowledge-gate`）を指しており、既存文書で混同されている。
2. `mocka-knowledge-gate`リポジトリは2026年4-6月の約4ヶ月間コミット無し、CI無効化、未解消のマージコンフリクトマーカー残存という休眠状態が確認されている。
3. 同リポジトリ内のPROJECT_501/MRS-001は、文書自身が明記する「commit/push禁止」に反して公開リモートへpush済みであることが確認されており、対応する承認記録・CHANGE_START/CHANGE_DONE記録が見当たらない（PENDING_DECISION、未解決）。

**評価:** **PARTIAL**

**差分:** 「保存を超えた継承制度」という理念自体はessenceパイプライン・MOCKA_OVERVIEW.jsonのレベルで実証されているが、「Knowledge Gate」という名を冠する具体的実装は、名称の二重性・長期休眠・未承認のpush疑義という3つの未解決問題を抱えており、ACHIEVEDと判定する証拠には至らない。

**推奨対応:** (1) 「Knowledge Gate」の指す対象をどちらか一方に明確化するか両方を別名称で分離すること、(2) PROJECT_501/MRS-001の事実確認（E-001）を優先的に完了させること、(3) mocka-knowledge-gateリポジトリの再活性化方針をR01審査で検討すること。

---

## 4. 達成済み領域（ACHIEVED以上）

| 分類 | 評価 | 一言要約 |
|---|---|---|
| Accountability | ACHIEVED | 全Decision Ledgerレコードに承認者明記、実測確認済み |
| Explainability（Decision-level） | ACHIEVED | 却下案・理由付き記録により事後統計推測型の説明可能性問題を構造的に回避 |
| Traceability | ACHIEVED | 実際に相互参照を辿った意思決定再構成を実証（supersede双方向反映には既知の欠落あり） |
| Incident Management | **ADVANCED** | NIST側TBDプレースホルダに対し、運用実績付きの専用制度が先行（限定的優位） |

---

## 5. 未達・改善領域（PARTIAL/NONE）

| 分類 | 評価 | 最重要の不足点 |
|---|---|---|
| Governance | PARTIAL | Human Gate執行経路に確認済みギャップ（IC_20260708_004、Open） |
| Risk Management | PARTIAL | 許容リスク閾値の事前定義framework、本調査範囲内で未確認 |
| Human Oversight | PARTIAL | 設計は制度的判断点として明確だが、執行ギャップとUI(TIC Layer4)未実装 |
| Transparency | PARTIAL | mocka-transparencyリポジトリの内容が未検証 |
| Explainability（Model-level） | NONE | MoCKAは機械学習モデルを訓練・運用していないため対象外 |
| Verification/Validation | PARTIAL | 監査サイクル制度は実証済みだが、自動ドリフト検知(calc_drift_v3)はINVALIDATED |
| Documentation | PARTIAL | 文書量は充実するが正本自身が陳腐化を自己申告 |
| Monitoring | PARTIAL | 基礎層(Layer0-1)は稼働、上位層(Layer2-4)は未着手 |
| Knowledge Management | PARTIAL | 名称衝突・休眠状態・未承認push疑義の3点が未解決 |

---

## 6. MoCKAが要求を超えている領域

**Incident Management（ADVANCED）のみ**、§3.11に記載の通りの限定的根拠に基づく。他の全分類はACHIEVEDまたはそれ以下であり、要求水準を明確に超えていると証拠付きで断定できる領域は現時点で1件に留まる。これは意図的に保守的な判定であり、「MoCKAが優れている」という一般的主張を避けるための姿勢である。

---

## 7. 国際AI Governance上の位置づけ

本比較はNIST AIRMF/TACIP Discussion Draft（2026-07-07版、非公式・策定途上）という単一時点のスナップショットとの比較に限定される。ISO/IEC標準・EU AI Act等、他の国際的枠組みとの比較は本文書の範囲外であり、実施していない。

MoCKAは、NISTが前提とする「AIが物理インフラを操作する」文脈ではなく、「AIが組織自身の統治プロセスに参加する」という異なる文脈で発展した制度である。両者の要求が重なる領域（Accountability、Explainability(意思決定レベル)、Traceability、Incident Management）では、MoCKAは証拠に基づき要求を満たす、または限定的に超える結果を示した。一方、NISTがCritical Infrastructure運用者に求める領域の多くはMoCKAの対象外（NONE、ドメイン不一致）である。この位置づけは、既存の`MOCKA_INTERNATIONAL_AI_GOVERNANCE_POSITION_PAPER_v1.0.md`第6章の結論と整合する。

---

## 8. Remaining Gap Analysis

優先度順（`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md`の最終状態分類と統合）:

**最優先（Open・実装欠落が確定済み）:**
1. Human Gate執行ギャップ（IC_20260708_004）— Governance/Human Oversight双方に影響
2. `calc_drift_v3`/AEGIS実装の不在（E-004、INVALIDATED）— Verification/Validation、Monitoringに影響
3. PROJECT_501/MRS-001の無許可push疑義（E-001、PENDING_DECISION）— Knowledge Managementに影響

**中優先:**
4. Knowledge Gateの名称衝突の解消
5. mocka-transparencyリポジトリの内容検証（Transparency分類の証拠不足解消）
6. リスク閾値事前定義frameworkの有無確認（Risk Management）
7. `superseded_by`自動反映の実装欠落（Traceabilityの機械的双方向性向上）

**低優先:**
8. TIC Layer 2-4着手判断（Monitoring/Human Oversight UIの拡充）
9. MOCKA_OVERVIEW.json本文の最新化（Documentation）

---

## 9. Roadmap（提案、実施は本文書の範囲外）

1. IC_20260708_004・E-001の事実確認・是正をR01審査で優先的に扱う
2. `calc_drift_v3`の復旧または移設先確認により、Verification/Validation分類の再評価を実施
3. Knowledge Gate名称衝突の解消後、Knowledge Management分類を再評価
4. 上記3点の是正が完了した時点で、本文書のv1.1改訂を検討（既存v1.0は改変せず、新バージョンとして作成する）

---

## 制約の遵守について

本文書の作成にあたり、以下を遵守した。
- 既存7成果物（NIST_REQUIREMENT_CATALOG等）および`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md`の本文は一切書き換えていない
- Git commit/pushは一切行っていない
- 推測によるACHIEVED/ADVANCED判定は行っていない（不明点は全てPARTIAL/NONEとした）
- 全評価項目に証拠（参照ファイル・Ledger ID・実装パス）を付記した
- 既に確定している否定的証拠（INVALIDATED、PENDING_DECISION等）は格上げ・隠蔽せずそのまま継承した
