# Governance Classification v0.1 (Phase B-2)

位置づけ: R01実行指示書「MoCKA Governance Catalog v1.0 制定プロジェクト」Phase B-2(Classification)に基づく。入力資料は`GOVERNANCE_INVENTORY_v0.1.md`(Phase B-1)のみ。分類は指示書が提示した分類例(憲法層/標準層/ガバナンス層/監査層/運用層/記録層)に限定し、新しい階層は作らない。新制度追加・名称変更・統廃合・優先順位付け・将来構想・推測は一切行わない。

分類はInventoryの各グループ(節)単位で行う。311件すべてを個別に再判定するのではなく、Inventoryで既に同一性質としてグループ化された単位(例: docs/audits/全57件、docs/contracts/全37件等)に対して、そのグループを代表する自己記述(タイトルの自称・Statusマーカー・配置ディレクトリ)から層を割り当てる。一つのグループが複数層にまたがる場合はその旨を明記する。

---

## 1. 各層の適用基準(既存文書の自己記述から導出)

- **憲法層**: 文書自身がConstitution/Charter/憲章と自称する、または「確定」「制定済み」の状態で最上位規範として扱われている文書。
- **標準層**: 文書自身がStandard/Specification/基準/仕様と自称し、複数の下位文書・実装が従うべき基準として位置づけられている文書。
- **ガバナンス層**: 制度運営・意思決定プロセスそのもの(Policy/Decision/Governance)を扱う文書。
- **監査層**: Audit/Review/Verification/Analysis等、既存の状態を検証・評価する文書。
- **運用層**: Contract/Spec/Design等、実装・運用の設計を扱う文書(Draft・未実装含む)。
- **記録層**: Ledger/Event/Archive/Incident/Log/Snapshot等、事実の記録・保存を目的とする文書・データ。

---

## 2. 分類結果(Inventoryグループ単位)

### docs/governance/ 配下

| Inventory節 | グループ | 分類層 | 分類根拠 |
|---|---|---|---|
| 1-1 | Registry Series(KN-001〜007・TERM-001) | KN-001のみ憲法層、KN-002〜007・TERM-001は標準層 | KN-001は文書名自体が「Registry Series 憲章」と自称。KN-002〜007・TERM-001はSchema/Semantics/State Model/Validation/Terminologyという仕様・用語基準を定める文書 |
| 1-1 | GM2_REGISTRY_BASELINE_002.md | 記録層 | 「ベースラインスナップショット」と自称し、承認済み時点の状態記録 |
| 1-2 | Module Governance Series(MODULE_*_v1.md、13件) | 運用層(草案段階) | 全件Status: Draft。将来的な標準を志向するが現時点では実装・運用設計の草案 |
| 1-3 | Vocabulary/Cross Reference/CI Failure Audit系(Fact Collection/Analysis部分) | 監査層 | 事実収集・分析を行う文書 |
| 1-3 | 同上(Decision Brief/Final Decision部分) | ガバナンス層 | 裁定・意思決定プロセスそのものの記録 |
| 1-3 | MoCKA Audit Standard制定プロジェクト成果物(Process Extraction/Verification/Draft/Internal Audit) | 監査層(抽出・検証部分)/標準層(Draft自体は将来標準の草案) | 実績抽出・整合確認は監査的性質、Draftは標準文書の草案 |
| 1-4 | Guarantee & Assurance Audits(4件) | 監査層 | タイトルにAuditを含み、既存の保証状態を検証 |
| 1-5 | Human Gate & Institutional Audits(4件) | 監査層 | タイトルにAuditを含む |
| 1-6 | VOCABULARY_CONSTITUTION_v0.1.md | 憲法層 | 文書名自体がConstitutionと自称 |
| 1-6 | Vocabulary Pattern Audit Criteria/Target List | 監査層 | Audit判定基準・対象一覧 |
| 1-7 | Policy Documents(Activation/Decision/External Knowledge/Decision Rule Layer/Conflict Resolution) | ガバナンス層 | いずれもPolicyまたは意思決定ルールを扱う |
| 1-8 | STATUS_VOCABULARY_v1.0_CONSTITUTION.md | 憲法層 | 文書名自体がConstitutionと自称、確定(博士裁定) |
| 1-8 | STATUS_VOCABULARY_v1.0_DRAFT.md | 運用層(草案段階) | Status: DRAFT |
| 1-8 | REPOSITORY_STATUS_VOCABULARY_v0.1.md、ACTIVITY_FREQUENCY_METADATA_v0.1.md | 記録層 | ステータス・活動頻度のメタデータを扱う |
| 1-9 | SATELLITE_REPOSITORY_ARCHITECTURE_v1.0_CONSTITUTION.md | 憲法層 | 文書名自体がConstitutionと自称、確定(博士裁定) |
| 1-9 | SATELLITE_REPOSITORY_ARCHITECTURE_v1.0_DRAFT.md、POSITIONING_OPTIONS | 運用層(草案段階) | Draft/Options Study |
| 1-10 | Phase Execution Governance(5件) | ガバナンス層 | 「Execution Governance Layer」と自称、FINALIZED/APPROVED |
| 1-11 | Phase10統合・終端宣言(9件) | 記録層(Freeze/Declaration/Closure部分)/監査層(Boundary Audit・Stability Review部分) | Freeze Log・Final Freeze Declaration・Terminal Closureは状態確定の記録。Boundary Audit・Stability Reviewは検証行為 |
| 1-12 | Human Gate Architecture(5件) | 運用層 | 全件Status: DRAFT、設計文書 |
| 1-13 | Code Binding & Finalization(4件) | ガバナンス層 | Decision Draft/Finalization/Decision Summaryという裁定プロセスの文書 |
| 1-14 | MOCKA_CHARTER_v2.md | 憲法層 | 文書名自体がCharterと自称、8条憲章として制定済み |
| 1-14 | MOCKA_THOUGHT_EVOLUTION_v0.1.md | 記録層 | 「思想進化史」という経緯記録 |
| 1-14 | GOVERNANCE_ARCHITECTURE_OVERVIEW_v1.md | ガバナンス層(草案段階) | Governance Architectureの概観、Status: Draft |
| 1-15 | Operational Design & Runtime(7件) | 運用層 | Execution Gate/Minimal Safe Architecture等、実装設計(PROPOSED/DECISION_RECORDED含む) |
| 1-16 | System Integrity & Verification(3件) | 監査層(GL7_STATE_INTEGRITY_NOTE=Observation Record)/運用層(OVERRIDES_ENFORCEMENT設計、DESIGN_MEMO) | Observation Recordは検証記録、設計文書は運用層 |
| 1-17 | Evolution & Adoption Policies(2件) | ガバナンス層 | 制度運営上の設計方針 |
| 1-18 | Analysis & Investigation Reports(6件) | 監査層(分析行為)/記録層(調査結果の記録) | いずれもAnalysis/Investigation/Verification Logという事後的な確認記録 |
| 1-19 | TODO_ARTIFACT_GOVERNANCE_v1.0.md、mocka_knowledge_lineage_standard_v1.md | 標準層 | いずれも文書内で「Standard」と自称 |
| 1-19 | adapter_governance_v1.md | 運用層(草案段階) | Status: DRAFT、Authority Design |
| 1-20 | Contract & Design Separation(2件) | 運用層(設計案) | DESIGN_PROPOSAL |
| 1-21 | import_safety_rule_v1.md | 運用層(提案段階) | Status: PROPOSED |
| 1-21 | GPT_RESTRICTIONS.md | 記録層 | インシデント由来の禁止事項リスト(自動生成) |

### docs/audits/ 配下

| Inventory節 | グループ | 分類層 | 分類根拠 |
|---|---|---|---|
| 2-1〜2-4 | docs/audits/全57件 | 監査層 | 全件がAudit/Review/Analysis/Report等、既存状態の検証・評価を目的とするディレクトリに配置 |

### docs/contracts/ 配下

| Inventory節 | グループ | 分類層 | 分類根拠 |
|---|---|---|---|
| 3-1〜3-9 | docs/contracts/全37件 | 運用層 | 全件がContractと自称し、実装・運用の設計を扱う(大半がStatus: DRAFT、一部FROZEN) |

### その他docs/*配下

| Inventory節 | グループ | 分類層 | 分類根拠 |
|---|---|---|---|
| 4-0 | NAMING_CONVENTION.md | 標準層 | 「Official Specification」と自称、Status: FIXED |
| 4-1 | docs/architecture/(12件) | 運用層 | Architecture設計文書(一部Status: STABLE) |
| 4-2 | docs/caliber/(5件) | 運用層(設計原則書)/監査層(Gap Analysis) | DESIGN_PRINCIPLESは設計文書、Gap Analysisは監査的性質 |
| 4-3 | docs/archive/(18件) | 記録層 | ディレクトリ名自体がArchive、Freeze/Lock/Inventory等の過去状態記録 |
| 4-4 | docs/experimental/(1件) | 運用層(実験段階) | Status: EXPERIMENTAL/NON-CANONICAL |
| 4-5 | docs/handoff/(2件) | 記録層 | 引き継ぎ・再構成ログ |
| 4-6 | docs/incidents/(5件) | 記録層 | インシデント記録(ディレクトリ名自体がincidents) |
| 4-7 | docs/internal/(1件)・docs/lifecycle/(1件) | 記録層(事実抽出)/運用層(設計思想) | internal文書はPhase1事実抽出、lifecycle文書は設計思想文書 |
| 4-8 | docs/mocka3/(18件のMarkdown) | 運用層 | Contract/Protocol/Model等の設計文書群 |
| 4-8 | taxonomy.json(参考記載) | 標準層 | verify_taxonomy_integrity.pyにより「FROZEN v1.1」と検証される基準データ |
| 4-9 | papers/phase1/releases/verification(4件) | 記録層 | Verification LogはPASS記録、ReleaseはSeal記録、papers/phase1はスナップショット的記録 |
| 4-10 | docs/spec/(9件) | 運用層 | Spec(仕様設計)文書 |

### コード・データ層

| Inventory節 | グループ | 分類層 | 分類根拠 |
|---|---|---|---|
| 5 | governance/verify配下のverify_*.py(検証系9件) | 監査層 | verify_all.pyから呼ばれる検証ステップそのもの |
| 5 | governance/配下のsign_*.py・check_origin.py・mocka_git_safe_commit.py等(運用ユーティリティ) | 運用層 | 鍵署名・git操作等の運用ツール |
| 6 | data/MOCKA_TODO_ACTIVE.json内Architecture Contract系(18件) | ガバナンス層(status=完了等の意思決定記録)/運用層(未着手の技術仕様) | 多くが「決定記録」的性質(GM2/GM3/Registry Series関連の完了記録)。GL7-*-BUG等の技術的不具合記録は運用層寄り |
| 7 | governance/registry.json | 記録層 | 鍵台帳(root_keys/operational_keysの記録) |

---

## 3. 層別集計(概算、複数層に該当するグループは両方でカウント)

| 層 | 主な該当グループ | 件数概算 |
|---|---|---|
| 憲法層 | KN-001、VOCABULARY_CONSTITUTION、STATUS_VOCABULARY_v1.0_CONSTITUTION、SATELLITE_REPOSITORY_ARCHITECTURE_v1.0_CONSTITUTION、MOCKA_CHARTER_v2 | 5件 |
| 標準層 | KN-002〜007・TERM-001、Module Governance Series(草案)、TODO_ARTIFACT_GOVERNANCE、mocka_knowledge_lineage_standard、NAMING_CONVENTION、taxonomy.json | 約22件 |
| ガバナンス層 | Policy Documents、Phase Execution Governance、Code Binding & Finalization、GOVERNANCE_ARCHITECTURE_OVERVIEW、Evolution & Adoption Policies、Decision Brief/Final Decision群、TODO内Architecture Contract系の一部 | 約35件 |
| 監査層 | docs/audits/全57件、Guarantee & Assurance Audits、Human Gate & Institutional Audits、Vocabulary Pattern Audit Criteria/Target List、Analysis & Investigation Reports、verify_*.py(9件)、今回サイクルのFact Collection/Analysis部分 | 約90件 |
| 運用層 | docs/contracts/全37件、docs/architecture/、docs/spec/、docs/mocka3/(設計文書)、Human Gate Architecture、Operational Design & Runtime、Module Governance Series、Contract & Design Separation | 約110件 |
| 記録層 | docs/archive/全18件、docs/incidents/全5件、GM2_REGISTRY_BASELINE_002、Phase10統合・終端宣言(Freeze/Declaration部分)、MOCKA_THOUGHT_EVOLUTION、GPT_RESTRICTIONS、registry.json、Analysis & Investigation Reportsの一部 | 約35件 |

本集計は概算であり、一部グループは複数層に重複計上されている(例: Analysis & Investigation Reportsは監査層・記録層の双方に計上)。重複の解消・単一層への統合はPhase B-2の範囲を超えるため行っていない。

---

## 4. 分類不能・判別不能事項

- Module Governance Series(13件)は「将来的に標準となることを志向しているか、恒久的にDraftのまま運用設計文書として扱われるか」が文書自体からは判別できない。現状のStatus(Draft)のみに基づき運用層に分類したが、標準層への該当可能性を排除しない。
- Architecture Contract系(TODO内18件)は、通常TODO(進行度5値)ともArchitecture Contract系(9値)とも異なる第三の性質(意思決定記録と技術仕様が混在)を持ち、単一層への分類が困難なものが複数存在する(例: GM2_ROADMAPは「ビジョンのみ」と自己記載しており、運用層・ガバナンス層いずれとも言い切れない)。
- docs/mocka3/配下の文書群(EVENT_FOUNDATION、DECISION_LEDGER_SCHEMA等)は、名称に「Ledger」「Event」を含み記録層的性質も持つが、内容は「Contract」「Schema」という設計文書の形式を取るため、本分類では運用層とした。記録層との二重該当の可能性がある。

---

## 改訂履歴

- v0.1(2026-07-04): R01実行指示書Phase B-2に基づき新規作成。GOVERNANCE_INVENTORY_v0.1.mdの各グループを指示書提示の6層(憲法層/標準層/ガバナンス層/監査層/運用層/記録層)に分類。くろこ起草。
