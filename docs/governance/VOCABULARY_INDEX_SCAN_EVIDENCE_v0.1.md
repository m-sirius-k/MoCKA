# Vocabulary Index Scan — Evidence v0.2

位置づけ: きむら博士指示（2026-07-04、「MoCKA用語索引 全体スキャン」最終版）に基づく事実収集フェーズの成果物。役割は制度書記官・実装調整官。評価・採否の判断は一切行っていない。収集した事実と根拠を提示した時点で作業を停止し、監査官(R01)およびきむら博士の判断を待つ。

対象範囲: MoCKAリポジトリ本体（C:/Users/sirok/MoCKA）単体。他のワーキングコピー（mocka-joints/mocka-ecosystem/MoCKA等）・エコシステム別リポジトリ（mocka-core-private/mocka-runtime/mocka-transparency/mocka-public等）は対象外（本作業着手前にきむら博士へ確認済み）。

## 0. 方法論（事実収集の方法そのものに関するメモ。優先順位判断ではない）

- vendor/依存ライブラリ除外: `.venv/` `.wsl_ots_venv/` `venv/` `.git/` `.pytest_cache/` `__pycache__/` をスキャン対象から除外した。除外理由: これらは第三者ライブラリのソースコードであり「MoCKA」が著作した内容ではないため。
- 対象語彙: 既存文書で既に扱われている19語（`TERM-001_REGISTRY_TERMINOLOGY.md`の12語 + `VOCABULARY_CONSTITUTION_v0.1.md`の8語、Registryが重複するため合計19語） = Ledger, Registry, Catalog, Memory, Archive, Caliber, Loop, Approval, Human Gate, Record, Entry, Artifact, Reference, Category, Series, Identifier, Status, Maturity, Source, Index。
- 生の文字列一致件数（vendor除外後、単語境界一致、大小文字無視）を先に計測した。Status=7430件/1830ファイル、Category=2870件/1317ファイル、Archive=16200件/51ファイル、Index=1750件/174ファイル、Source=1163件/246ファイル等、桁違いに多い語が存在した。この規模の全件file:line列挙は非現実的であり、大半が汎用コード変数・JSONキー・CSS属性等の非制度的用法であることを確認した（詳細は第3節）。
- そのため、頻度に応じて収集密度を変えた（これは事実収集の方法であり、語の重要度判断ではない）:
  - 低頻度語（Catalog/Identifier/Maturity/Approval/Human Gate/Series/Reference/Artifact/Entry）: 全件収集を試みた。
  - 高頻度語（Ledger/Registry/Memory/Caliber/Loop/Record/Category/Status/Source/Index/Archive）: 制度文脈（docs/governance, docs/audits, docs/spec, README系, .claude/, ui/, interface/配下）を優先収集し、それ以外（汎用コード変数・JSONキー等）は代表サンプルに留めた。
- 生の全件grep結果はスクラッチパス配下に保存済み（低頻度語8語分・Human Gate単独・高頻度語制度文脈分）。本文書には収集事実の要約と該当箇所を記載する。

## 1. 語彙候補ごとの事実（19語）

### [語彙候補] Catalog
[検出箇所一覧(ファイル:行)]
- docs\mocka3\MODULE_CATALOG_v1.md:1 — "# MoCKA Module Catalog v1"
- docs\mocka3\MODULE_CATALOG_v1.md:127 — "## 9. Initial Catalog"
- docs\governance\MODULE_REGISTRY_MODEL_v1.md:78 — "Module Catalog | RegistryはMODULE_CATALOGの登録情報（module_id・owner・public_interfaces等）を正本として参照する"
- docs\governance\GUARANTEE_MATRIX_AUDIT_v0.1.md:56 — "Catalog（MODULE_CATALOG_v1等） | G1（存在）、G8（索引の一貫性という意味での単一正本） | CONCEPT_AUDIT_v0.1.md 1.4節"
- docs\governance\GOVERNANCE_ARCHITECTURE_OVERVIEW_v1.md:53 — "MODULE_CATALOG_v1 | Module公式登録台帳 | Module Registration・Lifecycle Status・Initial Catalog"
- docs\governance\CONCEPT_AUDIT_v0.1.md:52 — "### 1.4 Archive / Catalog"
- docs\governance\CONCEPT_AUDIT_v0.1.md:118 — "### 3.3 「Registry」と「Catalog」の語彙境界の曖昧さ"
- docs\governance\CONCEPT_AUDIT_v0.1.md:120 — "CATEGORY_REGISTRY_v2.0.mdは名称に\"Registry\"を含むが、Catalog調査（分類目録機能）にも同時に該当した"
- docs\governance\VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md:20 — Catalog行サマリ
- docs\governance\VOCABULARY_CONSTITUTION_v0.1.md:49 — "### Catalog"
- docs\governance\REPOSITORY_STATUS_VOCABULARY_v0.1.md:86 — Task-F 7対象言及
- archive\_untracked_stash_20260226_170942\governance_phase16_upgrade\invariant_catalog_v1.md:1,11 — "Invariant Catalog v1（Phase16.1 baseline）"（アーカイブ内・凍結済み）
- archive\_untracked_stash_20260226_170942\governance_phase16_upgrade\err_catalog_v1.md:1,9 — "ERR Catalog v1（Phase16.1 baseline）"（アーカイブ内・凍結済み）
- docs\reference\semantic_dictionary\raw\unused_terms.md:15114,15120 — MODULE_CATALOG_v1由来の自動抽出ヒット（後述、第4節参照）
[分類タグ] Catalog
[正本候補(不明可)] docs\mocka3\MODULE_CATALOG_v1.md（実体文書として最も古い/具体的）。ただし`CONCEPT_AUDIT_v0.1.md`3.3節が「Registry」との境界曖昧さを既に指摘しており、単一の正本と言い切れるかは未確定。
[同義語・別名候補] Registry（`CATEGORY_REGISTRY_v2.0.md`がRegistry調査・Catalog調査の両方に該当すると既存文書が記録）。archive内`invariant_catalog_v1.md`/`err_catalog_v1.md`は別系統（Phase16.1由来）で、MODULE_CATALOG_v1と同一概念かは不明。
[影響範囲(件数+種別)] 合計35件（vendor除外後）: 制度文書(governance)8件・docs/mocka3 2件・archive(凍結)2件・semantic_dictionary自動抽出2件・その他ドキュメント1件・コード0件。

### [語彙候補] Identifier
[検出箇所一覧(ファイル:行)]
- docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md:143,195 — 正式定義「Identifier（識別子）」
- docs\governance\REGISTRY_SCHEMA_v1.0.md:28,30,32,123 — JSON Schema上のidentifierフィールド定義
- docs\governance\REGISTRY_RECORD_SPEC_v1.0.md:95,136 — "Index ModelではRecordは索引エントリである。索引の同一性はキー（Identifier）によって定まる"
- docs\governance\GM2_REGISTRY_BASELINE_002.md:44 — 12語彙リストの一部として言及
- PlanningCaliber\fp\REGISTRY_SCHEMA_v1.0.md:28,30,32,123 — 上記REGISTRY_SCHEMA_v1.0.mdの複製（PlanningCaliber\fp配下に同一内容が存在。正本重複の可能性、後述）
- core_kernel\governance\audit\audit_schema.py:23 — コード内コメント「rule identifier」（制度語Identifierとは別文脈、汎用識別子）
- semantic\query_engine\*.py 多数（structural_recovery.py, semantic_projection_layer.py, runtime_bridge.py, order_normalizer.py, observation_surface.py, execution_orchestrator.py）— 関数引数名`identifier`としての使用（プログラム変数名であり、Registry用語のIdentifierとは別文脈）
- archive\_untracked_stash_20260226_170942\infield\INFIELD_INDEX_NOTE.md:8 — "id: stable identifier"（アーカイブ内）
- docs\reference\semantic_dictionary\raw\unused_terms.md / synonym_candidates.md / category_candidates.md 内の複数ヒットは全て`archive\_untracked_stash_20260226_170942\.wsl_ots_venv\...\site-packages\...`配下（pip/Cryptodome等の第三者ライブラリのSPDXライセンスヘッダ由来）
[分類タグ] Registry（制度語としての用法）／その他（コード変数名としての汎用用法、大多数）
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md
[同義語・別名候補] なし（TERM-001は「KN-003で命名規則・形式を定義」と範囲外にしている）
[影響範囲(件数+種別)] 合計61件: 制度文書(governance)5件（PlanningCaliber\fp配下の複製2件含む）・コード（semantic/query_engine配下の変数名としての用法）約10件・archive(凍結)1件・semantic_dictionary自動抽出（第三者ライブラリ由来ノイズ）約6件・その他。

### [語彙候補] Maturity
[検出箇所一覧(ファイル:行)]
- docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md:155,159,205,208 — 正式定義「Maturity（成熟度）」。「Category/Seriesの属性であり、個別Recordの属性ではない」と明記。
- docs\governance\REGISTRY_RECORD_SPEC_v1.0.md:191 — TERM-001定義への参照確認
- docs\governance\MODULE_REGISTRY_MODEL_v1.md:42 — "Maturity Level | MODULE_MATURITY_MODELのLevel（M0〜M5）"
- docs\governance\MODULE_DISCOVERY_MODEL_v1.md:40 — "Maturity Level | MODULE_MATURITY_MODELのLevel | Category Index"
- docs\governance\GUARANTEE_MATURITY_INDEX_v0.1.md:1 — 別文書「Guarantee Maturity Index v0.1」（TERM-001のMaturityとは別文脈である可能性、要確認）
- docs\governance\GM2_REGISTRY_BASELINE_002.md:41,44 — TERM-001定義の再掲
- docs\mocka3\MODULE_MATURITY_MODEL_v1.md:1,19 — "MoCKA Module Maturity Model v1"「2. Maturity Levels（成熟度定義）」
- docs\mocka3\MODULE_CATALOG_v1.md:73,77 — "5. Maturity Integration" / "Maturity Level | Lifecycle Status"
- data\events_latest.json:2458,2494 — "博士指示: Task-L Guarantee Maturity Index 完了/着手"イベント記録
[分類タグ] Registry（Category/Series属性としてのMaturity）／その他（Guarantee Maturity Indexという別名称の存在、後述）
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md（Registry文脈）。ただし`GUARANTEE_MATURITY_INDEX_v0.1.md`という同じ「Maturity」を含む別文書が存在し、これがTERM-001のMaturity概念と同一かどうかは本調査では確認できていない（不明）。
[同義語・別名候補] MODULE_MATURITY_MODEL_v1のMaturity Level（M0〜M5）とTERM-001のMaturity（Category/Series属性）が同一概念かは既存文書で明示されていない。
[影響範囲(件数+種別)] 合計23件: 制度文書(governance)9件・docs/mocka3 3件・イベント記録2件・TODO記述1件。コード0件。

### [語彙候補] Approval / Human Gate
[検出箇所一覧(ファイル:行)] （614件中、代表箇所を抜粋。全件はスクラッチパス保存済み）
- docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md:43,239 — "記録の評価・承認・品質判定は Registry の外部（Human Approval Gate 等）が担う"
- docs\governance\VOCABULARY_CONSTITUTION_v0.1.md:104-113 — 「Approval（Human Gate）」の制度辞典エントリ（責務/保証/境界/禁止事項/依存関係）
- docs\governance\HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md:3,33,46,93 — Task-M監査。「Approval Gate本体（human_gate.py）」の接続断絶を調査
- docs\governance\REGISTRY_CHARTER_v1.0.md:110 — "Human Approval Gate による承認が得られていること（現時点では、きむら博士が Human Approval Gate を担う。）"
- docs\governance\DECISION_POLICY_v0.1.md:14,21,30,164 — "Approvalを持たない"はDecision Policyの明文化された制約
- docs\governance\CATEGORY_REGISTRY_v2.0.md:134,143 — Human Approval Gateによる承認要件
- governance\propagation\README.md:1 — "# Human Approval Gate"
- governance\propagation\sync_to_sheets.py:2-3,35,40 — 承認フラグ検証ロジック（実装コード）
- governance\mocka_git_safe_commit.py:26,110,119 — "Core System File Change Approval(Human Gate)対象"
- governance\approval_flow.json:2,15 — スキーマ`mocka.governance.approval.flow.v1`
- runtime\governance\human_boundary.py:13,16,30 — "approval"レベル判定の実装コード
- structural\execution_governance.py:15,238-242 — "Dry Run -> Approval(Human Gate) -> Execute -> Verify"フロー実装
- **docs\audits\MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1.md**
- **docs\audits\MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1.md:18,30,36,62,126** — "「Human Gate」という名称がMoCKA内で4つの異なる概念（Approval State Machine/Semantic Ruling/Governance Gate×2系統）を指している"
- **docs\audits\MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1.md:14,16,20** — HG-REG-01〜04として4実体を台帳化
- **docs\audits\MOCKA_HUMAN_GATE_FINALIZATION_AUDIT_v1.md / _CLOSURE_AUDIT_v1.md**
- **docs\audits\PHASE10_3_HUMAN_GATE_DECISION_BRIEF_v1.md / _DECISION_PACKAGE_v1.md / _DEPENDENCY_AUDIT_v1.md / _HEARING_PACKAGE_v1.md / _LOAD_ANALYSIS_v1.md**（`docs/audits/`配下に存在する追加のHuman Gate関連監査シリーズ、計10ファイル）
- docs\reference\semantic_dictionary\raw\duplicate_candidates.md:2158 — "Human Approval Gate / human_approval_gate → 同一概念の可能性"（自動抽出による表記ゆれ検出、大文字小文字/スペース有無の差）
[分類タグ] その他（Approval / Human Gate。Registry/Ledger/Catalog/Caliberいずれにも該当しない独立概念）
[正本候補(不明可)] 不明瞭・複数候補が並立。`VOCABULARY_CONSTITUTION_v0.1.md`（2026-07-03、Task-N）は「Approval（Human Gate）」を1エントリとして扱うが、これとは独立に`docs/audits/`配下に**MOCKA_HUMAN_GATE_*_AUDIT_v1.md（5件）+ PHASE10_3_HUMAN_GATE_*_v1.md（5件）合計10件**の既存監査シリーズが存在し、「Human Gate」という名称がMoCKA内で4つの異なる実体（Approval State Machine・Semantic Ruling・Governance Gate×2系統、HG-REG-01〜04）を指すと既に詳細に結論づけている。`VOCABULARY_CONSTITUTION_v0.1.md`側の参照文書リストにこの10件の既存監査シリーズへの言及は確認できなかった。
[同義語・別名候補] Human Approval Gate / human_approval_gate（表記ゆれ、semantic_dictionaryが自動検出済み）／Approval Gate／Approval State Machine（HG-REG-01の実体名）／Governance Gate（HG-REG-02/03系統）／Semantic Ruling（HG-REG系統の1つ）
[影響範囲(件数+種別)] 合計614件+「Approval」単独178件（Human Gateとの重複含む可能性あり、去重未実施）: 制度文書(governance) 約60件・docs/audits（Human Gate専用監査シリーズ）10ファイル・コード（governance/propagation, mocka_git_safe_commit.py, runtime/governance, structural/execution_governance.py等）約15件・TODO記述多数・semantic_dictionary自動抽出1件（表記ゆれ）。

### [語彙候補] Series
[検出箇所一覧(ファイル:行)]
- ARCHITECTURE.md:16 — "Time-Series Index"（統計用語としての用法、Registry Series概念とは無関係）
- BINDING_GAP_REPORT_v1.md:57 / BINDING_REGISTRY_v1.md:129 — "mini-mocka-series"（製品ディレクトリ名としてのSeries、Registry Series概念とは別文脈）
- data\MOCKA_TODO_ACTIVE.json:1166 — "Decision Policy Series（399→400→401→404→405→402）の数理閉包完成"
- docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md — 「Series（シリーズ）」正式定義（第3節既読）
- docs\governance\GM2_REGISTRY_BASELINE_002.md — Registry Series用語リストの一部
- PlanningCaliber\workshop\mini-mocka-series\ 配下多数（製品名としてのSeries、Registry Series概念とは別）
[分類タグ] Registry（制度語としてのSeries）／その他（統計用語Time-Series、製品名mini-mocka-series）
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md（Registry Series概念）。ただし「Decision Policy Series」「mini-mocka-series」等、TERM-001のSeries定義と直接紐付くか不明な用法が複数存在。
[同義語・別名候補] なし確認（ただし「~~ Series」という命名パターン自体がKnowledge Navigation Series/Registry Series/Decision Policy Seriesと複数のSeries系統に使われており、いずれも同一のTERM-001定義に従っているかは本調査では未確認）
[影響範囲(件数+種別)] 合計315件: 制度文書(governance)相当数・製品ディレクトリ名(mini-mocka-series)による水増しが多数を占める・コード（ARCHITECTURE.md等の技術文書内技術用語）少数。

### [語彙候補] Reference
[検出箇所一覧(ファイル:行)]
- docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md — 「Reference（リファレンス）」正式定義（第3節既読）："Artifactへの参照情報...ファイルパス・URL・識別子・場所情報などが該当"
- README_RESEARCH_ENTRY.md:111 — "This map acts as the reference registry of research experiments."
- docs\governance\GM2_REGISTRY_BASELINE_002.md — 12語彙リストの一部
[分類タグ] Registry
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md
[同義語・別名候補] なし
[影響範囲(件数+種別)] 合計205件。ただし本調査でdocs/governance・docs/audits・docs/spec・README・.claude配下に限定してヒットしたのは上記2件のみ。残り約200件超はコード内の一般的英単語"reference"としての用法（例: コメント中の「参照」を意味する汎用用法）であり、制度語Referenceとしての用法は極めて限定的である可能性が高い（断定はしない）。

### [語彙候補] Artifact
[検出箇所一覧(ファイル:行)]
- data\MOCKA_TODO_ACTIVE.json:1138 — "docs/governance/TODO_ARTIFACT_GOVERNANCE_v1.0.md"（Artifact Type: Design Note / Governance Document / Source Code / Investigation Report / Test Report / Config-Data / N/Aの4項目定義）
- docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md — 「Artifact（アーティファクト）」正式定義（第3節既読）
- README_RESEARCH_ENTRY.md:68,74,123 — "artifact generation" "Each artifact is hashed and logged" "artifact hashes"（Research Ledger文脈でのArtifact、TERM-001定義と整合する可能性）
- README_DEMO.md:190 — "Artifact Generation"
[分類タグ] Registry
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md。ただし`TODO_ARTIFACT_GOVERNANCE_v1.0.md`が独自に"Artifact Type"（Design Note/Governance Document/Source Code/Investigation Report/Test Report/Config-Data/N/A）という分類体系を定義しており、これがTERM-001のArtifact定義とどう接続するかは既存文書で明示されていない。
[同義語・別名候補] なし確認
[影響範囲(件数+種別)] 合計267件: 制度文書(governance)少数・README系3件・コード（大多数、汎用英単語としての"artifact"用法の可能性が高いが本調査では未分類）。

### [語彙候補] Entry
[検出箇所一覧(ファイル:行)]
- docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md — 「Entry（エントリ）」正式定義："Recordの別称として使用する同義語である...この暫定定義はKN-003で再確認・上書きしてよい"（暫定的同義語と明記）
- README_RESEARCH_ENTRY.md:1 — ファイル名自体が"Research Entry"（Registry Entry=Recordの意味かは不明）
- README.md:182,204,212,273,302,333,373,545,556,584 — "entry point"（プログラムの実行開始点を指す技術用語。Registry Entry=Recordの意味とは完全に別文脈）
[分類タグ] Registry（TERM-001定義のEntry=Record同義語）／その他（"entry point"という技術用語としての用法、圧倒的多数）
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md（Entry=Record暫定同義語の定義）
[同義語・別名候補] Record（TERM-001が明記する暫定同義語）
[影響範囲(件数+種別)] 合計526件。docs/governance・docs/audits・docs/spec・README限定では上記の通りごく少数のみヒットし、README.md内のヒットの大半は"entry point"という無関係な技術用語であることを確認した。Registry用語としてのEntryの実使用は極めて限定的である可能性が高い（断定はしない）。

## 2. 高頻度語（制度文脈優先収集）

以下11語は生の一致件数が数百〜16,200件に及ぶため、docs/governance・docs/audits・docs/spec・README系・.claude/・ui/・interface/配下に限定したヒットを全件記載し、それ以外は代表サンプルに留めた。

### [語彙候補] Ledger
[検出箇所一覧] README.md:158,161,200,604,609,618,631,643,649,786／README_RESEARCH_ENTRY.md:115,117,123,125,280（"Research Ledger"）／data\MOCKA_TODO.json:5489, data\MOCKA_TODO_ARCHIVE.json:4596（TODO_384関連note内"append-only ledger"言及）
[分類タグ] Ledger
[正本候補(不明可)] `VOCABULARY_CONSTITUTION_v0.1.md`のLedger項目が「実体は複数存在し統一されていない」と明記。内部下位区分: (a)runtime\main\ledger.json（ハッシュチェーン）(b)mocka_events.db+audit_trigger.py (c)PHI-OS decision_ledger.jsonl (d)KN_SERIES_LEDGER（実体未確認）。README.mdの"Research Ledger"（README_RESEARCH_ENTRY.md）はこの4系統のいずれとも明示的に紐付けられていない、5番目の名称である可能性がある。
[同義語・別名候補] 台帳（日本語表記、governance文書内で使用例あり）
[影響範囲(件数+種別)] 合計868件/218ファイル。制度文脈(README含む)16件、残り852件はコード変数・JSONキー等の非制度的用法のためサンプル対象外（全件はスクラッチパスに保存）。

### [語彙候補] Registry
[検出箇所一覧] README_RESEARCH_ENTRY.md:82,111（"Experiment registry"）／README_DEMO.md:188／README.md:318
[分類タグ] Registry
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md（Registry Series全体の正式定義群）
[同義語・別名候補] レジストリ（日本語表記）。Catalog（CONCEPT_AUDIT_v0.1.md 3.3節が境界曖昧と既に指摘）
[影響範囲(件数+種別)] 合計900件/170ファイル。制度文脈(README等)4件、残り896件はコード内クラス名・変数名・JSONキー等（例: `ai_capability_registry`, `recurrence_registry`, `beta_registry`等、VOCABULARY_CONSTITUTION_v0.1が既に列挙済みの内部下位区分）。

### [語彙候補] Memory
[検出箇所一覧] README_RESEARCH_ENTRY.md:39／README_DEMO.md:4,23,35,56,67,77,106,136,153,192／README.md:13,40,53,120,217,313,317,334,337-339,343,350,360,382,389,395,403,445,559,637,840,930,949-951,955,961,969,991,996,1010,1048（"Memory Layer"、GL2、working_memory.py関連の説明多数）
[分類タグ] その他（Memory。VOCABULARY_CONSTITUTION_v0.1は独立8語の1つとして扱う）
[正本候補(不明可)] 不明。`VOCABULARY_CONSTITUTION_v0.1.md`のMemory項目が「4粒度に分かれ、統合されていない」と既に明記（Memory拡張／mocka-infield／data/storage/infield／working_memory.py／Knowledge Assets・Reason Unit）。
[同義語・別名候補] 記憶（日本語表記）
[影響範囲(件数+種別)] 合計794件/219ファイル。制度文脈(README中心)約35件、残りはコード（memory/memory_*.py等）・JSONキー。

### [語彙候補] Caliber
[検出箇所一覧] README.md:130,132,133,158,161,211,758,760,786(日英併記)／data\MOCKA_TODO.json:4959, data\MOCKA_TODO_ARCHIVE.json:4066, docs\archive\todo_canonical\C_MOCKA_TODO.json:4867（BOM除去作業note内言及）
[分類タグ] Caliber
[正本候補(不明可)] `VOCABULARY_CONSTITUTION_v0.1.md`のCaliber項目が「6系統は相互にコード共有がなく、統一された単一実体は存在しない」と既に確定済みと明記（`CALIBER_TO_SKILL_MD_GAP_ANALYSIS_v0.1.md`参照）。
[同義語・別名候補] なし確認
[影響範囲(件数+種別)] 合計983件/134ファイル。制度文脈9件、残り974件はコード（caliber/chat_pipeline配下等）・データ。

### [語彙候補] Loop
[検出箇所一覧] README.md:63,69,76,98,108,120,133,156,386,429,597,606,607,646,647,663,994
[分類タグ] Loop
[正本候補(不明可)] `VOCABULARY_CONSTITUTION_v0.1.md`のLoop項目（LOOP_DESIGN_PRINCIPLES + DRIFT_STANDARD_v1.1 + Loop Health Index未実装案の3区分）
[同義語・別名候補] mocka_Movement（README内"civilization loop"の別名的表現の可能性、既存文書での同一性明記は未確認）
[影響範囲(件数+種別)] 合計794件/118ファイル。制度文脈17件、残りはコード（interface/router.py等）・データ。

### [語彙候補] Record
[検出箇所一覧] README_DEMO.md:56,66,120／README.md:71,177,196,268,608,611,620／data\MOCKA_TODO_ARCHIVE.json:2653, data\MOCKA_TODO.json:3546, todo_tmp.json:3339, docs\archive\todo_canonical\C_MOCKA_TODO.json:3454（change-record-store.js関連note言及）
[分類タグ] Registry（TERM-001定義）／その他（README冒頭のMovement図"Observation → Record → Incident..."という運用ループ内の1ステップとしての用法）
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md（Registry Record定義）。ただしREADME.mdのRecordはmocka_Movement（運用ループ）内のステップ名としての用法であり、TERM-001のRegistry Record定義と同一概念かは既存文書で明示されていない。
[同義語・別名候補] Entry（TERM-001が明記する暫定同義語）
[影響範囲(件数+種別)] 合計863件/272ファイル。制度文脈12件、残りはコード（change-record-store.js等）・JSONキー多数。

### [語彙候補] Category
[検出箇所一覧] data\MOCKA_TODO_ACTIVE.json:472, data\MOCKA_TODO.json:775（"category": "バグ/UI/risk_recommendation"、TODOメタデータのcategoryフィールド）
[分類タグ] Registry（TERM-001定義のCategory=DP/GV/IA/OA/KN/KAの6区分）／その他（TODOメタデータの自由記述categoryフィールド、無関係な文脈）
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md。ただしTODOメタデータの"category"フィールド（例:"バグ/UI/risk_recommendation"）はTERM-001のCategory（DP/GV/IA/OA/KN/KA）とは全く異なる自由記述文字列であり、同一語が2つの異なるスキーマで独立に使われている。
[同義語・別名候補] なし
[影響範囲(件数+種別)] 合計2870件/1317ファイル。制度文脈(README/docs/governance限定)2件のみ検出。残り2868件は大多数がJSONの"category"キー（TODOメタデータ等）・コード変数名で、TERM-001のCategory概念とは無関係と見られる（断定はしない、全数目視未実施）。

### [語彙候補] Status
[検出箇所一覧] data\MOCKA_TODO_ACTIVE.json:1138,1166（"Verification Status: Pending/Verified"等）／README.md:506,508,660／README_verify.txt:20,21
[分類タグ] Registry（TERM-001定義：Lifecycleで管理されるRecordの状態）／その他（Verification Status, HTTPステータス等汎用用法が大半）
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md（Record Status定義）。ただし「TODO管理schema」の観点では`.claude/CLAUDE.md`内に別途「TODO status正規値一覧（TODO_384準拠）」（通常5値：未着手/進行中/完了/保留/廃止、Architecture Contract系9値）という**独立したstatus語彙体系**が存在し、TERM-001のRegistry Status定義とは異なる制度的出自を持つ。
[同義語・別名候補] なし確認（ただしstatus/Status/STATUSの大小文字表記ゆれがコード内に多数存在する可能性が高い、第3節参照）
[影響範囲(件数+種別)] 合計7430件/1830ファイル（19語中最大）。制度文脈(README/docs/governance/data配下抜粋)7件のみ収集。残り7423件はJSONキー・HTTPステータス・変数名等の非制度的用法が支配的と見られる（断定はしない）。

### [語彙候補] Source
[検出箇所一覧] data\MOCKA_TODO_ACTIVE.json:1138／README_RESEARCH_ENTRY.md:11／README.md:266（"semantic_registry.py — single source of truth"）／PlanningCaliber\Experiment_v2.0\essence_out\pure_essence.json:456, master_essence.json:2849
[分類タグ] Registry（TERM-001定義：正本・参照元の概念）
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md。TERM-001自身が「Sourceの確定は将来の設計課題として残されている」と明記（第3節既読）。
[同義語・別名候補] 正本（日本語表記。governance文書内で頻用）
[影響範囲(件数+種別)] 合計1163件/246ファイル。制度文脈5件、残りはコード（"source code", import文等）・データ。

### [語彙候補] Index
[検出箇所一覧] docs\reference\semantic_dictionary\raw\unused_terms.md:16914,139963／governance\infield\docs\phase24_a_audit_note.md:7（"Index CSV templates"）／docs\reference\semantic_dictionary\raw\all_terms.json:890878
[分類タグ] Registry（TERM-001定義：Index Model採用の中核概念）／その他（"src/ui/index.html"というファイル名としての"index"、無関係）
[正本候補(不明可)] docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md（Index Model採用の確定文書）
[同義語・別名候補] なし確認
[影響範囲(件数+種別)] 合計1750件/174ファイル。制度文脈での直接ヒットは限定的（上記4件は"index.html"ファイル名言及や"Index CSV"等、TERM-001のIndex Model概念とは別文脈の可能性が高い）。TERM-001本文（第3節既読）以外でIndex Model概念に直接言及する制度文書は本調査では追加確認できなかった。

### [語彙候補] Archive
[検出箇所一覧] data\MOCKA_TODO_ARCHIVE.json:4596, data\MOCKA_TODO.json:5489（"[元status記録(TODO_384 B区分修正により移動)]"note内言及）／docs\reference\semantic_dictionary\raw\unused_terms.md:3362,73238（archive\_untracked_stash_20260226_170942配下の第三者ライブラリ由来ノイズ）
[分類タグ] その他（Archive。VOCABULARY_CONSTITUTION_v0.1は独立8語の1つとして扱う）
[正本候補(不明可)] 不明。`VOCABULARY_CONSTITUTION_v0.1.md`のArchive項目が「TIC Archive層／Phase ARCHIVE層／Module ARCHIVED状態の3つの無関係な意味で使われている可能性大」「同語異義」と既に明記。
[同義語・別名候補] なし（同語異義であり別名ではなく同名異義と既存文書が整理）
[影響範囲(件数+種別)] 合計16200件/51ファイル（一致件数は最大だがファイル数は51と少数に集中）。この集中の実体は主に`archive\_untracked_stash_20260226_170942\`という単一の凍結ディレクトリ配下（第三者ライブラリの`.wsl_ots_venv`含む）と、`data\MOCKA_TODO_ARCHIVE.json`という単一の大型JSONファイルである（詳細は第3節参照）。

## 3. 重複語・表記ゆれ

- 大小文字ゆれ: `docs/reference/semantic_dictionary/raw/duplicate_candidates.md`（2026-06-16生成、既存の自動抽出成果物）が以下を「同一概念の可能性」として既に検出済み: `ARCHIVE / archive`、`ARTIFACT / ARTIFACTS / Artifact / Artifacts`、`CALIBER / Caliber`、`CATEGORY / Category / category`、`INDEX / index`、`MEMORY / Memory`、`MEMORY_LAYER / Memory Layer`。19語中7語が既にこのリストに含まれることを確認した。
- 表記ゆれ（英語表現差）: 同ファイルが`Human Approval Gate / human_approval_gate`（スペース区切り+大文字始まり vs スネークケース）を検出済み。本調査の独自grep結果とも整合する（第1節Approval/Human Gate参照）。
- 日英表記ゆれ: Registry/レジストリ、Ledger/台帳、Memory/記憶、Archive/アーカイブ、Source/正本 等の日本語表現が governance 文書内に混在していることを確認した（件数は個別集計していない）。
- ファイル正本の物理的重複: `docs/governance/REGISTRY_SCHEMA_v1.0.md` と `PlanningCaliber/fp/REGISTRY_SCHEMA_v1.0.md` が同一内容（identifierフィールド定義部分を含め一致）で2箇所に存在することを確認した（第1節Identifier参照）。どちらが正本か、あるいは意図的な配布用複製かは本調査では判断していない。

## 4. 欠損語候補（欠損語の抽出）

- **Human Gate関連監査シリーズの非参照**: `docs/audits/`配下に`MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1.md`、`MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1.md`、`MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1.md`、`MOCKA_HUMAN_GATE_FINALIZATION_AUDIT_v1.md`、`MOCKA_HUMAN_GATE_FINALIZATION_CLOSURE_AUDIT_v1.md`、`PHASE10_3_HUMAN_GATE_DECISION_BRIEF_v1.md`、`PHASE10_3_HUMAN_GATE_DECISION_PACKAGE_v1.md`、`PHASE10_3_HUMAN_GATE_DEPENDENCY_AUDIT_v1.md`、`PHASE10_3_HUMAN_GATE_HEARING_PACKAGE_v1.md`、`PHASE10_3_HUMAN_GATE_LOAD_ANALYSIS_v1.md`の計10件が存在し、「Human Gate」という名称がMoCKA内で4つの異なる概念（Approval State Machine/Semantic Ruling/Governance Gate×2系統、HG-REG-01〜04）を指すと既に詳細に結論づけている。しかし2026-07-03付`VOCABULARY_CONSTITUTION_v0.1.md`の「Approval（Human Gate）」項目・参照文書リストにはこの10件への言及が確認できなかった。
- **既存文書の自己申告による未収録語**: `VOCABULARY_CONSTITUTION_v0.1.md`第3部が「本辞典は8用語に限定しており、今回の一連の監査で言及された他の用語（例: Decision Evidence、Knowledge Assets自体、GL7そのもの）は独立した見出しとして立てていない」と自ら明記している。
- **semantic_dictionary（既存の自動抽出成果物）の位置づけ**: `docs/reference/semantic_dictionary/raw/`配下に、2026-06-16生成の`all_terms.md`（51MB）・`all_terms.json`（282MB）・`category_candidates.md`（カテゴリ未分類で出現5回以上のterm 11,060件）・`duplicate_candidates.md`（6,215件）・`synonym_candidates.md`（2,297件）・`unused_terms.md`（24,002件）・`term_relationships.md`・`frequency.csv`が存在する。これは「MoCKAリポジトリ全体（vendor含む）」に対する機械的な単語頻度・類似度抽出であり、CSSプロパティ（font-size等）・PowerShellコマンドレット（Get-ChildItem等）・第三者ライブラリのライセンス文言（SOFTWARE/WARRANTIES/INCLUDING等、pip vendor配下）・合成テストデータの変数名（RUN_FAST_VAR863等）が大量に含まれており、MoCKAの制度語彙とは無関係な内容が支配的である。本ファイル群についてmocka_search（events.db全文検索）で"semantic_dictionary"を検索したが該当イベントは0件であり、mocka_write_eventによる記録が確認できない（`.claude/CLAUDE.md`が定める「記録なき作業はMoCKAとして存在しない」という原則に照らすと、この成果物自体の制度的位置づけが不明である）。

## 5. 未実施・限定事項（正直な報告）

- 低頻度語のうち、Series/Reference/Artifact/Entryについては「docs/governance・docs/audits・docs/spec・README」限定の絞り込み検索を行った。この4語の絞り込み前の生ヒット全件（Series=315件、Reference=205件、Artifact=267件、Entry=526件）は完全には個別分類していない。生の grep 結果はスクラッチパスに保存済みであり、必要であれば追加提示できる。
- 高頻度11語（Ledger/Registry/Memory/Caliber/Loop/Record/Category/Status/Source/Index/Archive）は制度文脈への絞り込みを行っており、コード内の汎用的用法（非制度的用法が大半と見られる）は個別に file:line 列挙していない。
- 本文書はMoCKA本体リポジトリ単体を対象としており、PlanningCaliber配下（ワークスペースとして同一リポジトリ内にネストされている）は含めているが、mocka-core-private等の別リポジトリは対象外。

## 6. v0.2追記: 2系統の独立バックグラウンド収集による追加事実

v0.1提示後、2系統の独立したバックグラウンド収集を実行した（いずれもv0.1の存在を知らない/一部認知した状態で独立に一次データを再取得）。両者はv0.1の内容とおおむね整合し、以下の新規事実を追加で確認した。断定・評価は行わず、事実の追記のみとする。

### 6-1. 実装レベルでの多重実装（新規確認）

- **Human Gate: 2つの独立した実装ファイルを確認**。`phi_os\human_gate.py`（"PHI-OSがHuman Gateの唯一の状態管理責務を持つ"と自己記述）と`semantic\query_engine\human_gate.py`（"Phase7-B-6 - Human Gate Ruling v0 (institutional design, not resolution)"）が別々に存在する。両者の関係は既存文書に明示なし。
- **Registry: 3つ以上の独立した`capability_registry`実装を確認**。`core_kernel\core_store\capability_registry.py`、`interface\ai_capability_registry.py`（2026-06-17作成。ファイル冒頭コメントで「core_kernel/core_store/の既存capability_registry.pyとは独立した別物」と明記）、`PlanningCaliber\workshop\seo-os\caliber\capability_registry.py`（今回新規発見）の3ファイル。既存VOCABULARY_CONSTITUTION_v0.1.mdは`ai_capability_registry`を「実装状況不明」としているが、実際には実装済みであることを確認した。
- **Artifact: PHI-OS独自クラス定義を確認**。`phi_os\runtime\runtime_types.py:113`に`class Artifact:`が定義されており、TERM-001のArtifact概念（Registry外部の参照対象）との対応関係は既存文書に明示がない。
- **KN_SERIES_LEDGER: 独立した実体ファイルとしては確認できなかった**。`data\MOCKA_TODO_ACTIVE.json`内のTODO項目ID文字列としてのみ存在し、CATEGORY_REGISTRY_v2.0.md・REGISTRY_CHARTER_v1.0.mdが「KN_SERIES_LEDGERに従い」と参照する先の独立実体（JSON/DB等）は本調査でも発見できなかった。
- **Atlas（Atlas Series）: 独立ファイルとしての実体は確認できなかった**。TERM-001・REGISTRY_SEMANTICS_v1.0.md等で「Category/Series間のTopologyはAtlas Seriesの管轄」と繰り返し予告されるが、Atlasという名の文書自体は本調査時点では存在しない（将来シリーズとしての言及のみ）。
- **REGISTRY_SCHEMA_v1.0.mdの物理的重複を再確認**: `docs/governance/REGISTRY_SCHEMA_v1.0.md`と`PlanningCaliber/fp/REGISTRY_SCHEMA_v1.0.md`が同一内容で2箇所に存在（両系統の独立収集で同一の指摘が出た）。

### 6-2. 件数の乖離とその原因（方法論上の事実）

"Human Gate"の一致件数について、本文書v0.1は614件/152ファイルと記載したが、単語境界を指定しない`rg -i -n "human gate"`では1205件/195ファイルとなることを別系統の収集で確認した。`rg -i -n '\bhuman gate\b'`（単語境界指定）では614件/152ファイルとなり、v0.1の値と一致することを確認した。v0.1の集計は単語境界指定ありの方法であったと推定される（断定はしない、両者とも同じgrep手法の異なるオプションによる差であり、リポジトリの変更によるものではないと考えられる）。

### 6-3. 追加の欠損語候補

第3節に加え、以下も欠損語候補として確認した: Decision Policy（governance配下66件）、GL7（137件）、TIC（168件）、Knowledge Assets（25件）、Reason Unit（16件）、Decision Evidence（20件、VOCABULARY_CONSTITUTION_v0.1.md第3部が名指しで「独立エントリを立てていない」と自己申告する3語の一つ）、Atlas（実体なきシリーズ予告）、BEE（`structural/bee.py`に実装ありだが用語集に定義なし）、Guarantee（`GUARANTEE_MATRIX_AUDIT_v0.1.md`等4専用文書が存在するほど頻出する概念だが独立エントリなし）、Writer/Checker（`WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md`という専用文書があるが独立エントリなし）。

### 6-4. 表記ゆれの追加確認（既存自動抽出ツールとの照合）

`docs/reference/semantic_dictionary/raw/duplicate_candidates.md`（2026-06-16生成）が、本調査の19語と関連して以下も「同一概念の可能性」として既に検出済みであることを確認した: `ARCHIVE/archive`、`ARCHIVE_PROOF/archive-proof`、`ARCHIVED`、`ArchiveInfo`、`CALIBER/Caliber`、`CALIBER_PROCESS/caliber_process`、`CATEGORY/Category/category`、`MEMORY/Memory`、`MEMORY_LAYER/Memory Layer`、`Human Approval Gate/human_approval_gate`、`HUMAN_GATE_OVERRIDES/human_gate_overrides`。加えて、`CapabilityRegistry`・`ContractRegistry`・`EventTypeRegistry`・`GateRegistry`・`FailureContainmentRegistry`という、Registryを語根に持つ複数の独立クラス名が既に自動検出されている（6-1のRegistry多重実装と符合する）。同様に`DecisionLedger`・`EvidenceLedger`（Ledger語根）、`ApprovalResult`・`ApprovalRule`（Approval語根）も検出済み。

以上、v0.2として追記した事実も含め、収集した事実と根拠の提示をもって本フェーズの作業を停止する。評価・採否・優先順位の判断は行っていない。監査官(R01)およびきむら博士の判断を待つ。

## 改訂履歴

- v0.1（2026-07-04）: きむら博士指示（用語索引全体スキャン最終版）に基づき新規作成。くろこ起草。
- v0.2（2026-07-04）: 2系統の独立バックグラウンド収集結果を追記。実装レベルでの多重実装（Human Gate 2実装・Registry 3実装以上・Artifact独自クラス）、KN_SERIES_LEDGER/Atlasの実体不在確認、件数乖離の方法論的説明、追加欠損語候補10件、既存自動抽出ツールとの追加照合を追記。くろこ起草。
