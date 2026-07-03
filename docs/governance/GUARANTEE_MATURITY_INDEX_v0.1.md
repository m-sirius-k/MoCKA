# Guarantee Maturity Index v0.1

位置づけ: 博士指示（2026-07-03、Task-L）に基づき新規作成。`GUARANTEE_MATRIX_AUDIT_v0.1.md`のG1〜G10について、MoCKA・PHI-OS・Orchestra・Relay・Memoryの5対象での成熟度を評価する。

実装は一切含まない。新規のコード調査は行わず、本日までの調査結果（CONCEPT_AUDIT_v0.1、GUARANTEE_MATRIX_AUDIT_v0.1、HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1、GUARANTEE_VERIFICATION_MATRIX_v0.1）を用いた評価である。

---

## 第1部: 現状把握

### 1.1 成熟度レベルの定義（博士指示による）

| レベル | 名称 | 意味 |
|---|---|---|
| Level 0 | 構想 | アイデア・問題意識はあるが、制度としての文書化がまだない |
| Level 1 | 制度定義 | ポリシー文書・設計文書として明文化されているが、実装には至っていない |
| Level 2 | 部分実装 | 一部のコード・仕組みが実装されているが、既知の穴・未接続点がある |
| Level 3 | 実装済 | 主要な実装が完了し、宣言通りに機能していると考えられる |
| Level 4 | 継続検証済 | 実装が機能していることを継続的に検証する仕組み（カナリアテスト・監査ログ突合等）が稼働している |

### 1.2 評価対象データの偏り（重要な前提）

本日の一連の監査は、いずれもMoCKA本体とPHI-OSに関する情報が中心であり、Orchestra・Relay・Memory（製品）固有の保証実装については、`CONCEPT_AUDIT_v0.1.md`のArchive/Catalog調査で「独自のarchive/catalog概念は未検出」（MODULE_CATALOGの傘下に統一管理）という結果が出ている程度で、深く調査されていない。したがって、以下の表でOrchestra・Relay列の多くは「不明」または「対象外（共有基盤に依存）」となる。これは製品側に保証が存在しないことの証明ではなく、単に今回の調査範囲が及んでいないことを意味する。

---

## 第2部: 提案 — 成熟度マトリクス

| Guarantee | MoCKA | PHI-OS | Orchestra | Relay | Memory |
|---|---|---|---|---|---|
| G1 存在保証 | Level 2（KN-004は設計フェーズ、各種local registryは稼働中だが未統合。KN-004/MODULE_CATALOG重複疑いも未解消） | Level 2（schema-registry.js稼働、MODULE_CATALOG傘下） | Level 1（MODULE_CATALOGに登録される、という宣言レベルの存在保証のみ確認） | Level 1（同上） | Level 2（Memory拡張自体は稼働中の製品） |
| G2 不変性・改ざん検知保証 | Level 2（ledger.jsonはVerifyスクリプトまで存在、他候補は判定保留） | Level 2（decision_ledger.jsonlにverify_chain()はあるが定期実行は不明） | 不明（調査範囲外） | 不明（調査範囲外） | 不明（調査範囲外） |
| G3 網羅性保証 | Level 3（event_gate一元化・PostToolUse自動記録が稼働中との記録あり） | Level 2（audit_trigger.pyは稼働、突合検証は不明） | 不明 | 不明 | 不明 |
| G4 実行前安全性保証 | Level 2（GL7稼働中だがFORBIDDEN_EXECUTIONS未接続という既知の穴あり） | 不明（GL7がPHI-OS内のどこまで適用されるか未確認） | 対象外（共有基盤GL7に依存すると考えられるが未確認） | 対象外（同上） | 対象外（同上） |
| G5 人間最終決定保証 | Level 2（human_gate.py実装済みだが、GL7・Knowledge Activation・Writer/Checkerとの接続に複数の断絶。`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`参照） | Level 3（human_gate.py自体はPHI-OS配下に実装済みと考えられる。ただし検証段階は未達） | 不明 | 不明 | 不明 |
| G6 暴走・停滞検知保証 | Level 1（LOOP_DESIGN 3制約は制度定義済みだが、DRIFT_STANDARDの実装=calc_drift_v3等がrouter.pyに実在しない疑いがあり、Loop Health Indexは未実装） | 不明 | 不明 | 不明 | 不明 |
| G7 品質・妥当性保証 | Level 3（Caliber各系統・PLANNING_CALIBER_LAWの閾値判定は稼働中）／Writer/CheckerはLevel 0（本日の設計提案のみ） | 不明 | 不明 | 不明 | 不明 |
| G8 単一正本保証 | Level 1（Decision Policyは制度として明文化されているが、KN-004/MODULE_CATALOG重複疑いのように実際には複数正本が並立している可能性がある） | 不明 | 対象外 | 対象外 | 対象外 |
| G9 権限分離保証 | Level 2（Decision Policy責務境界は明文化、audit_trigger.pyによる一部監査機構あり） | Level 2（audit_trigger.pyはPHI-OS配下） | 不明 | 不明 | 不明 |
| G10 文脈・経験継承保証 | Level 2（working_memory.py・data/storage/infieldは実装済みだが、mocka-infieldがORPHANのため統合的な保証としては未完成） | 不明 | 不明 | 不明 | Level 3（Memory拡張のchrome.storage.local実装は稼働中の製品として確認できる） |

### 2.1 全体観察

- **MoCKA本体はLevel 1〜3の間に分布しており、Level 4（継続検証済）に到達している保証は一つもない。** これは`GUARANTEE_VERIFICATION_MATRIX_v0.1.md`で「検証」段階が全体的に手薄だったことと整合する
- **PHI-OSはMoCKA本体と重なる保証（G2/G3/G5/G9）についてはMoCKAと同等かやや進んだ実装状況にあるように見えるが、これはPHI-OSがMoCKAのガバナンス機構（audit_trigger.py、human_gate.py）の実装場所そのものであるためと考えられる。**PHI-OS固有の保証（Trust Boundary確立、TODO_325未着手）は本表には反映していない
- **Orchestra・Relayはほぼ全項目が不明であり、本表からは成熟度を語ることができない。** これは今回の調査不足そのものであり、Task-Pのカバレッジマップで改めて扱う
- **Memoryは唯一G10で他対象より高いLevel（3）を得ているが、これは「文脈継承」という単一の保証において製品として明確に機能しているためであり、Memory製品全体の保証成熟度が高いことを意味しない**

---

## 第3部: 未確定事項

- Orchestra・Relay列の「不明」「対象外」の多さは、製品側の保証が存在しないことを意味しない。今後の追加調査が必要
- 各セルのレベル判定は、本日の一連の監査で得られた記述（実装済み/未実装/設計のみ等の言明）を根拠にした評価であり、実際にコードを実行して確認したものではない。特にLevel 2と3の境界（「既知の穴がある」か「主要実装は完了している」か）は評価者の解釈に依存する部分がある
- PHI-OSのGL7適用範囲（G4）は本監査では確認できていない。GL7はMoCKA本体のstructural配下にあるが、PHI-OSの実行がGL7を経由するかどうかは要確認

---

## 改訂履歴

- v0.1（2026-07-03）: 博士指示Task-Lに基づき新規作成。
