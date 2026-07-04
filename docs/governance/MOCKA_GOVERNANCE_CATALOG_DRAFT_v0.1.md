# MoCKA Governance Catalog Draft v0.1 (Phase B-4)

位置づけ: R01実行指示書「MoCKA Governance Catalog v1.0 制定プロジェクト」Phase B-4(Governance Catalog Draft)に基づく。入力資料は`GOVERNANCE_INVENTORY_v0.1.md`(Phase B-1)・`GOVERNANCE_CLASSIFICATION_v0.1.md`(Phase B-2)・`GOVERNANCE_RELATIONSHIP_MAP_v0.1.md`(Phase B-3)である。本ドラフトはこれら3文書の統合・要約であり、新たな調査・新制度・名称変更・統廃合・優先順位付け・将来構想・推測は一切含まない。

---

## 1. 目的

本カタログは、MoCKA 1.0で現在運用されている制度・標準・シリーズ・監査体系を棚卸しし、Governance全体を体系的に整理するものである。新しい制度の設計は行わない。現在存在し、運用実績または正式承認を有する制度のみを対象とする。

## 2. 適用範囲

`docs/governance/`・`docs/audits/`・`docs/contracts/`・その他`docs/*`配下(architecture/caliber/archive/experimental/handoff/incidents/internal/lifecycle/mocka3/papers/phase1/releases/spec/verification/api)・`docs/NAMING_CONVENTION.md`・`governance/`および`verify/`配下のPythonコード・`data/MOCKA_TODO_ACTIVE.json`内のArchitecture Contract系エントリ・`governance/registry.json`。合計約311件(`GOVERNANCE_INVENTORY_v0.1.md`第8節参照)。`docs/reference/semantic_dictionary/`(生データ)、および通常TODO(category≠設計成果物)は対象外。

## 3. Governance全体構成

`GOVERNANCE_CLASSIFICATION_v0.1.md`で確認された6層構成(憲法層/標準層/ガバナンス層/監査層/運用層/記録層)により、MoCKAのGovernanceは概ね以下のように構成されている。

- **憲法層**(5件: MOCKA_CHARTER_v2、VOCABULARY_CONSTITUTION_v0.1、STATUS_VOCABULARY_v1.0_CONSTITUTION、SATELLITE_REPOSITORY_ARCHITECTURE_v1.0_CONSTITUTION、REGISTRY_CHARTER_v1.0〈KN-001〉)が最上位規範として存在する。
- **標準層**(約22件: KN-002〜007・TERM-001、TODO_ARTIFACT_GOVERNANCE、mocka_knowledge_lineage_standard、NAMING_CONVENTION等)が、憲法層の下で個別領域(Registry・命名・TODO管理・知識系譜)の基準を定める。
- **ガバナンス層**(約35件: Policy Documents、Phase Execution Governance、Code Binding & Finalization、Decision Brief/Final Decision群等)が、意思決定プロセスそのものを扱う。
- **監査層**(約90件: docs/audits/全57件、Guarantee/Human Gate関連監査、verify_*.pyの検証ステップ等)が、既存の状態を検証・評価する。
- **運用層**(約110件: docs/contracts/全37件、docs/architecture/・docs/spec/・docs/mocka3/の設計文書、Module Governance Series等)が、実装・運用の設計を扱う(大半がDraft)。
- **記録層**(約35件: docs/archive/全18件、docs/incidents/全5件、GM2_REGISTRY_BASELINE、registry.json等)が、事実の記録・保存を担う。

`GOVERNANCE_RELATIONSHIP_MAP_v0.1.md`で確認された通り、これらの層は以下の経路で接続されている。

- 憲法層(MOCKA_CHARTER・KN-001等)→標準層(KN-002〜007・TERM-001)という参照関係。
- 標準層・ガバナンス層の決定(GM2_ROADMAP等)→運用層の個別設計(Registry Series等)という上位下位関係。
- 監査層(verify_all.pyが呼ぶ9ステップ)→記録層(registry.json、taxonomy.json)という利用関係。
- 今回サイクル(Vocabulary/Cross Reference/CI Failure)に見られたFact Collection→Analysis→Decision Preparation→Final Decisionという直列プロセス構造。

## 4. 制度一覧

全件一覧は`GOVERNANCE_INVENTORY_v0.1.md`を参照(名称/文書名/保存場所/現在の状態/制定状況/関連制度の6項目、約311件)。主要な区分は以下の通り。

| 区分 | 件数概算 | 参照先 |
|---|---|---|
| docs/governance/配下 | 103〜104件 | GOVERNANCE_INVENTORY_v0.1.md 第1節 |
| docs/audits/配下 | 57件 | 同 第2節 |
| docs/contracts/配下 | 37件 | 同 第3節 |
| その他docs/*配下 | 69件+NAMING_CONVENTION.md | 同 第4節 |
| governance/・verify/配下コード | 約25件 | 同 第5節 |
| MOCKA_TODO_ACTIVE.json内Architecture Contract系 | 18件 | 同 第6節 |
| governance/registry.json | 1件 | 同 第7節 |

## 5. 分類

6層(憲法層/標準層/ガバナンス層/監査層/運用層/記録層)への分類結果は`GOVERNANCE_CLASSIFICATION_v0.1.md`に整理済み。層別集計(概算、複数層該当を含む)は以下の通り。

| 層 | 件数概算 |
|---|---|
| 憲法層 | 5件 |
| 標準層 | 約22件 |
| ガバナンス層 | 約35件 |
| 監査層 | 約90件 |
| 運用層 | 約110件 |
| 記録層 | 約35件 |

分類基準・グループ単位の詳細根拠は`GOVERNANCE_CLASSIFICATION_v0.1.md`第1・2節を参照。

## 6. 関係図(文章による整理)

詳細は`GOVERNANCE_RELATIONSHIP_MAP_v0.1.md`を参照。要点は以下の通り。

- **参照関係**: KN-002・KN-003・TERM-001はKN-001を含む「参照文書」節を持つが、KN-001自身・KN-004〜007・VOCABULARY_CONSTITUTION_v0.1には同節が存在しない。Human Gate監査シリーズ(10件)は、VOCABULARY_CONSTITUTION_v0.1・REGISTRY_STATE_MODEL_v1.0(KN-006)のいずれからも参照されていない。
- **上位下位関係**: MOCKA_CHARTER_v2を最上位とし、KN-001(Registry Series憲章)がKN-002〜007・TERM-001を、GM2_ROADMAPがRegistry Series(KN)全体を、それぞれ束ねる構造がTODO記録・参照節から確認できる。今回サイクルの監査4フェーズ(Fact Collection→Analysis→Decision Preparation→Final Decision)も直列の上位下位構造を持つ。
- **利用関係**: verify_all.pyが9件の検証コードを名指しで呼び出し、これらがgovernance/registry.json・docs/mocka3/taxonomy.jsonを参照する。git操作はgovernance/mocka_git_safe_commit.pyに一元化され、複数の自律スクリプトがこれを経由する。
- **適用対象**: docs/NAMING_CONVENTION.mdは最上位アーキテクチャ名7件のみに適用され、モジュール/概念レベルの語彙(Human Gate・Registry等)は対象外。MoCKA Global Rule Guardはリポジトリ全体の文字列一致検査(mocka_v0.1・ディレクトリ二重ネスト)に適用される。

## 7. 用語一覧

本調査で確認された、複数文書にまたがり使用される制度略称・シリーズ名(いずれも既存文書内での使用が確認されたもののみ)。

| 用語 | 意味(確認された用法) |
|---|---|
| KN(KN-001〜007) | Registry Seriesの文書番号(REGISTRY_CHARTER/CATEGORY_REGISTRY/REGISTRY_RECORD_SPEC/REGISTRY_SCHEMA/REGISTRY_SEMANTICS/REGISTRY_STATE_MODEL/REGISTRY_VALIDATION) |
| TERM-001 | Registry Terminology & Principlesを定める用語集文書 |
| GM1/GM2/GM3 | Governance Milestone 1(Decision Policy Series・Governance Audit Series確立)/GM2(Operational Assurance→Registry→Atlas→Knowledge Activationロードマップ)/GM3(Knowledge Governance長期ビジョン、現在の開発対象ではない) |
| Phase番号(Phase5・7・8・9・10等) | docs/contracts/・docs/audits/配下の文書群が示す開発フェーズ番号 |
| HAB | Human Authority Boundary(mocka_hab_v1_contract.md等) |
| GL7 | Execution Kernel仕様(gl7_execution_kernel_spec_v1.md等)を指す略称 |
| Human Gate | 承認ワークフロー(phi_os)と意味裁定装置(semantic/query_engine)という複数概念にまたがる名称(VOCABULARY_AUDIT_EVALUATION論点Aで既に指摘済み) |
| Optional Stage | 監査テーマ固有の任意工程(Evaluation等)を指す、MOCKA_AUDIT_STANDARD_DRAFT_v0.1.mdで定義された用語 |
| 承認権限者 | フェーズ移行の裁定を行う主体を指す、MOCKA_AUDIT_STANDARD_DRAFT_v0.1.mdで定義された用語(特定個人を指さない) |

## 8. 未分類事項

`GOVERNANCE_CLASSIFICATION_v0.1.md`第4節・`GOVERNANCE_RELATIONSHIP_MAP_v0.1.md`第5節に記載の事項をここに集約する。

- Module Governance Series(MODULE_*_v1.md、13件)は、将来標準を志向するか恒久的な運用設計文書として扱われるかが文書自体からは判別できない。
- data/MOCKA_TODO_ACTIVE.json内のArchitecture Contract系18件のうち、意思決定記録と技術仕様が混在するもの(例: GM2_ROADMAPは「ビジョンのみ」と自己記載)は単一層への分類が困難。
- docs/mocka3/配下のEVENT_FOUNDATION_v1.md・DECISION_LEDGER_SCHEMA_v1.md等は、名称上は記録層的性質(Event/Ledger)を持つが、内容はContract/Schema形式であるため運用層とした。記録層との二重該当の可能性がある。
- docs/contracts/配下のPhase番号付けが示す順序関係は、ファイル名からの推定であり、本文個別読了による依存関係の検証は行っていない。
- Module Governance Series相互の依存関係、およびdocs/mocka3/MODULE_CATALOG_v1.md・MODULE_DEPENDENCY_MODEL_v1.mdとの関係は未検証。KN-004とMODULE_CATALOG_v1のスコープ重複は既存監査(GUARANTEE_MATRIX_AUDIT_v0.1.md)で指摘済みだが未解決のまま。

---

## 改訂履歴

- v0.1(2026-07-04): R01実行指示書Phase B-4に基づき新規作成。GOVERNANCE_INVENTORY_v0.1.md・GOVERNANCE_CLASSIFICATION_v0.1.md・GOVERNANCE_RELATIONSHIP_MAP_v0.1.mdを統合。くろこ起草。
