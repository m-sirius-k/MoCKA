# Governance Relationship Map v0.1 (Phase B-3)

位置づけ: R01実行指示書「MoCKA Governance Catalog v1.0 制定プロジェクト」Phase B-3(Relationship Mapping)に基づく。入力資料は`GOVERNANCE_INVENTORY_v0.1.md`(Phase B-1)・`GOVERNANCE_CLASSIFICATION_v0.1.md`(Phase B-2)、および既に本セッション内・過去のAudit/Analysisで直接確認済みの一次資料に限定する。新規の広域調査は行わない。制度変更は一切行わない。整理対象は参照関係・上位下位関係・利用関係・適用対象の4点。

---

## 1. 参照関係(文書が他の文書を明示的に参照する関係)

以下は`CROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.md`(2026-07-04)で直接確認済みの事実。

| 参照元 | 参照先 | 参照形式 |
|---|---|---|
| CATEGORY_REGISTRY_v2.0.md(KN-002) | REGISTRY_CHARTER_v1.0.md(KN-001)、MOCKA_TODO_ACTIVE.json内3項目 | 「参照文書」節(154行目)で明示 |
| REGISTRY_RECORD_SPEC_v1.0.md(KN-003) | REGISTRY_CHARTER_v1.0.md(KN-001)、CATEGORY_REGISTRY_v2.0.md(KN-002)、TERM-001_REGISTRY_TERMINOLOGY.md、GM2_REGISTRY_BASELINE_002.md | 「参照文書」節(280行目)で明示 |
| TERM-001_REGISTRY_TERMINOLOGY.md | REGISTRY_CHARTER_v1.0.md(KN-001)、CATEGORY_REGISTRY_v2.0.md(KN-002)、MOCKA_TODO_ACTIVE.json内1項目 | 「参照文書」節(266行目)で明示 |
| VOCABULARY_CONSTITUTION_v0.1.md | TERM-001_REGISTRY_TERMINOLOGY.md | 第3部で本文中言及(独立した参照節ではない) | 
| REGISTRY_STATE_MODEL_v1.0.md(KN-006)§5.1 | `phi_os/human_gate.py` | 実装参照先として明記(ただし`semantic/query_engine/human_gate.py`・Human Gate監査シリーズへの言及はない) |

以下は参照が期待されるが確認されなかった関係(`CROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.md`で「参照すべきだが参照していない」として整理済み)。

| 文書 | 参照していない対象 |
|---|---|
| REGISTRY_CHARTER_v1.0.md(KN-001) | 「参照文書」節自体が存在しない(既存記録は「参照文書節を持つ」としていたが、直接確認では不存在) |
| REGISTRY_SCHEMA_v1.0.md(KN-004)〜REGISTRY_VALIDATION_v1.0.md(KN-007) | いずれも「参照文書」節が存在しない(KN-001〜003・TERM-001とは異なる) |
| VOCABULARY_CONSTITUTION_v0.1.md(Approval〈Human Gate〉項目) | `docs/audits/MOCKA_HUMAN_GATE_*_AUDIT_v1.md`系列(10件) |
| REGISTRY_STATE_MODEL_v1.0.md(KN-006)§5.1 | Human Gate監査シリーズ、および`semantic/query_engine/human_gate.py` |

今回サイクル(Vocabulary Audit/Cross Reference Audit/CI Failure)の各Decision Briefは、対応するAnalysis文書1件のみを参照する設計(R01分析指示書v1.0・R01 Decision Preparation指示書v1.0で明示)。3テーマは相互に参照しない独立分析として扱われた(`AUDIT_PROCESS_EXTRACTION_v0.1.md`参照)。

## 2. 上位下位関係(階層・依存順序)

以下は各文書のタイトル・シリーズ番号・自己記述から直接確認できる階層構造。

| 上位 | 下位 | 関係の根拠 |
|---|---|---|
| MOCKA_CHARTER_v2.md | 個別のPolicy/Governance文書群 | Charter(8条憲章)として全体基盤に位置づけ(GOVERNANCE_ARCHITECTURE_OVERVIEW_v1.md等がConstitution 5原則を参照する構造、MOCKA_OVERVIEW.json記載) |
| REGISTRY_CHARTER_v1.0.md(KN-001) | CATEGORY_REGISTRY_v2.0.md(KN-002)〜REGISTRY_VALIDATION_v1.0.md(KN-007)、TERM-001 | KN-001が「Registry Series 憲章」を自称し、KN-002以降がこれを参照文書として引用(1節参照関係) |
| GM2_ROADMAP(TODO) | GM2_BASELINE_STEP1、GM2_REGISTRY_BASELINE_001/002、KN-001〜007 | GM2_ROADMAPが「Operational Assurance→Registry→Atlas→Knowledge Activation」のロードマップを宣言し、Registry Series(KN)がそのStep2に対応するとMOCKA_TODO_ACTIVE.json記載のnoteで明記 |
| GM3_VISION(TODO) | (現時点で具体的な下位文書なし) | GM3_VISION自身が「長期ビジョン・現在の開発対象ではない」と明記し、GM2とは異なる将来理念として区別されている |
| Vocabulary Audit: Fact Collection(VOCABULARY_INDEX_SCAN_EVIDENCE)→Evaluation(VOCABULARY_AUDIT_EVALUATION)→Analysis(VOCABULARY_AUDIT_ANALYSIS)→Decision Brief→Final Decision | 各段階が前段階の正式成果物を入力とする直列構造 | `AUDIT_PROCESS_EXTRACTION_v0.1.md`(Phase A-1)で確認済み。ただしVocabulary AuditトラックのみFact CollectionとAnalysisの間にEvaluation(Optional Stage)が介在する点は他の2トラック(Cross Reference/CI Failure)と異なる(`MOCKA_AUDIT_STANDARD_DRAFT_v0.1.md`第8節) |
| Phase5→Phase7-A/B/C/D→Phase8→Phase9→Phase10 | docs/contracts/配下の各Contract文書 | ファイル名のPhase番号が示す順序(例: phase7_a4はPhase7-A-4、phase8_2はPhase8-2)。実際の依存関係の内容までは本調査では検証していない(ファイル名・番号付けから読み取れる順序のみ) |
| REGISTRY_SERIES_V1_0_BASELINE(TODO) | REGISTRY_SERIES_V1_1_CANDIDATE(TODO) | 前者がKN-001〜007確定時点のスナップショット、後者がその監査で発見されたMinor Finding 5件の改訂候補としてnoteに明記 |

## 3. 利用関係(コード・運用プロセスからの参照・呼び出し)

| 利用元 | 利用対象 | 関係の根拠 |
|---|---|---|
| verify_all.py | governance/verify_governance_event_required.py、verify_revoke_event.py、verify_role_policy.py、verify_approval_flow.py、deterministic_build_gate.py、chaos_gate.py、verify_anchor_interface.py、verify_external_audit_report.py、verify_taxonomy_integrity.py | 9ステップとして名指しで呼び出す(verify_all.py本文で確認済み) |
| verify_taxonomy_integrity.py | docs/mocka3/taxonomy.json | 「FROZEN v1.1、7カテゴリ」であることを検証 |
| verify_role_policy.py、verify_governance_event_required.py、verify_revoke_event.py | governance/registry.json | 鍵台帳(root_keys/operational_keys)を参照して署名・ロールを検証 |
| verify_anchor_interface.py | calc_summary_hash.py | anchor_record.jsonのsealed_summary_hash算出に利用(調査エージェントで確認済み) |
| scripts/ledger/anchor_update.py、PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py、runtime/incident_engine.py、runtime/incident_git_sync.py | governance/mocka_git_safe_commit.py | CLAUDE.md(TODO_364)記載により、これら4スクリプトは本ヘルパー経由へ移行済み(2026-06-30) |
| 今回セッションのGit意味別コミット(2026-07-04) | governance/mocka_git_safe_commit.py | 実際にPythonから`mocka_git_safe_commit(paths=..., message=..., push=False)`を呼び出しコミットを作成(本セッションで実施・確認済み) |

## 4. 適用対象(各制度がどの範囲に及ぶか)

| 制度 | 適用対象 | 根拠 |
|---|---|---|
| docs/NAMING_CONVENTION.md | `mocka_Receptor`・`mocka_insight_system`・`mocka_Movement`・`shadow_Movement`・`acceptor:infield/outfield`等、最上位アーキテクチャ名7件のみ | VOCABULARY_AUDIT_EVALUATION_v0.1.md第8節・全170行読了確認済み。Human Gate/Registry/Ledger等のモジュール/概念レベルの語彙は適用対象外と明記 |
| MoCKA Global Rule Guard(GitHub Actions workflow) | リポジトリ全体の`*.py`・`*.md`ファイル(grep対象)、および`mcp/mcp`・`relay/relay`・`event/event`という3種のディレクトリ二重ネストパターン | CI_FAILURE_FACT_COLLECTION_MOCKA_GLOBAL_RULE_GUARD_v0.1.mdで確認済みのworkflow定義内容 |
| governance/mocka_git_safe_commit.py(is_core_system_file) | `phi_os/`・`interface/`・`structural/`・`gateway/`配下の`.py`ファイル、`app.py`・`index.html`・`scripts/ledger/anchor_update.py`・`PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py`、および`PlanningCaliber/workshop/`配下全体 | mocka_git_safe_commit.py本文のCORE_SYSTEM_DIRS/CORE_SYSTEM_FILES_EXTRA/PRIVATE_REPO_DIRS定義で確認済み(本セッションでコード読了) |
| MoCKA Audit Standard Draft v0.1(第2節「適用範囲」) | 今回実証された3件の監査テーマ(Vocabulary Audit/Cross Reference Audit/CI Failure)の実績のみ | ドラフト文書自身が明記(「今回実証されていない監査類型への適用可否は本標準の範囲外」) |
| Registry Series(KN-001〜007) | Registry(capability_registry等の語彙・概念)に関する制度領域 | シリーズ名自体が示す適用範囲。ただし実装レベルでの適用状況(3実装の同名異義)はVOCABULARY_AUDIT_EVALUATION論点Aで別途整理済み |
| STATUS_VOCABULARY_v1.0_CONSTITUTION.md | リポジトリのステータス語彙体系(確定・博士裁定2026-07-03) | GOVERNANCE_INVENTORY_v0.1.md 1-8節記載の状態情報 |

---

## 5. 未確認・本調査の範囲外とした関係

- docs/contracts/配下のPhase番号付けが示す順序関係(Phase5→7→8→9→10)は、ファイル名からの推定であり、各Contract文書の本文を個別に読了して依存関係を検証したものではない。
- docs/mocka3/配下のEVENT_FOUNDATION_v1.md・DECISION_LEDGER_SCHEMA_v1.md等と、governance/registry.json・runtime/main/ledger.json等の実装側Ledgerとの対応関係は、本調査(Phase B-1〜B-3)の範囲では個別に検証していない。
- Module Governance Series(MODULE_*_v1.md、13件)相互の依存関係、およびdocs/mocka3/MODULE_CATALOG_v1.md・MODULE_DEPENDENCY_MODEL_v1.mdとの関係は、いずれもDraft段階であり本調査では確認していない(GUARANTEE_MATRIX_AUDIT_v0.1.mdが「KN-004とMODULE_CATALOG_v1のスコープ重複」を既に指摘済みであることのみ、GOVERNANCE_INVENTORY_v0.1.md 1-4節に記録済み)。

---

## 改訂履歴

- v0.1(2026-07-04): R01実行指示書Phase B-3に基づき新規作成。GOVERNANCE_INVENTORY_v0.1.md・GOVERNANCE_CLASSIFICATION_v0.1.md、および既に確認済みの一次資料(CROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.md・VOCABULARY_AUDIT_EVALUATION・verify_all.py・mocka_git_safe_commit.py・CLAUDE.md等)のみを根拠に、参照関係・上位下位関係・利用関係・適用対象を整理。くろこ起草。
