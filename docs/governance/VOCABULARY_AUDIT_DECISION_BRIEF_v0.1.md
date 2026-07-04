# Vocabulary Audit Decision Brief v0.1 (Decision-01)

位置づけ: R01 Decision Preparation指示書v1.0 Decision-01に基づく。入力資料は`VOCABULARY_AUDIT_ANALYSIS_v0.1.md`(Analysis-01)のみとし、新規調査は行っていない。本文書は博士の裁定に必要な資料を整理するものであり、採択・却下・優先順位付け・修正案・実装案の提示、および裁定の代行は一切行わない。

---

## 1. Analysis要約

Analysis-01(入力: VOCABULARY_AUDIT_EVALUATION v0.3)で確認された内容は以下の通り。

- 7つの評価軸のうち、設計思想・実装整合性はB評価である一方、文書整合性・ガバナンス証跡・索引整合性・正本管理・命名ガバナンスの5軸はC以下と評価されている。
- 評価軸の分布に二極化構造が見られる。「個別の実体の質」を問う軸(B評価)と、「複数の実体を横断して束ねる仕組み」を問う軸(D評価)との間に明確な落差がある。
- Human Gate・Registry・Ledger・Archiveという4つの独立した語彙系統すべてで、「同一名称が複数の無関係な概念・実装に割り当てられる」という同一パターンが反復出現している。
- 各実装は個別には設計文書を伴う意図的な設計である一方、複数実装間の名称調整を担う上位の仕組みは確認されていない、という組み合わせが繰り返し現れている。
- 文書整合性の根拠とされた不備事例は、いずれも既存文書自身が「未確認」「将来課題」と明記した箇所であり、自己申告された不備がその後解消されないまま後続文書に引き継がれている。
- 正規監査文書群は一貫した記録文化(CHANGE_START/DONE・Human Approval Gate承認)を示す一方、semantic_dictionary(282MB規模)という大規模成果物にはその記録が確認されなかった。
- `docs/NAMING_CONVENTION.md`は実在するが、対象は最上位アーキテクチャ名(7件)のみで、本監査が扱うモジュール/概念レベルの語彙は範囲外。
- 索引整合性の不備として、GL7・TIC・Decision Policy・Guarantee系・Writer/Checker等、高頻度使用の制度語が19語辞典に含まれていないことが確認されている。
- 正本管理の不備として、REGISTRY_SCHEMA_v1.0.mdの物理的複製、KN_SERIES_LEDGER・Atlasの実体不在、KN-004とMODULE_CATALOG_v1のスコープ重複未解決が確認されている。

## 2. 博士裁定事項

- Vocabulary Audit Analysis(Analysis-01)を正式採択するか。
- 評価結果(7軸評価。うち5軸がC以下)を正式監査結果として採用するか。
- 「命名ガバナンス」「索引整合性」「正本管理」を正式評価軸として採択するか。
- 「モジュール単位の設計品質」と「モジュール横断の調整機構」の成熟度落差を、意図した設計上の分業と捉えるか、埋めるべき空白と捉えるか。
- 自己申告された不備(TERM-001のSource未確定等)を今後どのタイミング・体制で解消するか。
- semantic_dictionaryのような記録慣行の及んでいない成果物カテゴリを、今後どう位置づけるか(記録義務の遡及適用を含む)。

## 3. 裁定による影響範囲

- Vocabulary Governance関連文書群(TERM-001、VOCABULARY_CONSTITUTION_v0.1.md、`docs/NAMING_CONVENTION.md`)の適用範囲・改訂要否。
- 用語辞典(19語)の範囲・追加要否。
- REGISTRY_SCHEMA_v1.0.md、KN_SERIES_LEDGER、Atlas、KN-004/MODULE_CATALOG_v1の正本管理体制。
- 今後のVocabulary Audit系列文書(v0.2以降)の起点。
- 記録義務(mocka_write_event等)の適用範囲が遡及的に見直される場合、既存の大規模生成物(semantic_dictionary等)の扱い。

## 4. 未判断事項

- 「同名異義パターン」がHuman Gate・Registry・Ledger・Archiveの4系統以外にも存在するかは、Evaluation v0.3が扱った範囲でのみ確認されており、リポジトリ全体の悉皆調査は行われていない。
- 「個別には意図的、全体としては未調整」という組み合わせが、意図的な設計方針(局所的自律性優先)か、単に調整が未着手であるだけかは判別できていない。
- 自己申告型の不備が後続文書に引き継がれるパターンが、TERM-001/VOCABULARY_CONSTITUTION_v0.1以外の文書系列でも一般的に見られる慣行かどうかは未確認。

---

## 改訂履歴

- v0.1(2026-07-04): R01 Decision Preparation指示書v1.0 Decision-01に基づき新規作成。入力資料はVOCABULARY_AUDIT_ANALYSIS_v0.1.mdのみ。くろこ起草。
