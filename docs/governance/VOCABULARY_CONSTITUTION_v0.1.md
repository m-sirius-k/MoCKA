# Vocabulary Constitution v0.1

位置づけ: 博士指示（2026-07-03、Task-N）に基づき新規作成。`VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md`（Task-E）・`_TARGET_LIST_v0.1.md`（Task-F）の続編。用語辞典（意味の説明）ではなく制度辞典（責務・保証・境界・禁止事項・依存関係を定めた制度文書）として、MoCKAの主要語彙を統一フォーマットで記載する。

実装は一切含まない。新規のコード調査は行わず、本日作成済みの以下の文書を再構成した内容である: `CONCEPT_AUDIT_v0.1.md`、`GUARANTEE_MATRIX_AUDIT_v0.1.md`、`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`、`CALIBER_TO_SKILL_MD_GAP_ANALYSIS_v0.1.md`、`LOOP_HEALTH_INDEX_DESIGN_v0.1.md`、`VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md`。

**統一フォーマットの5項目:**

1. **責務** — この用語が何を行う（べき）ものか
2. **保証** — `GUARANTEE_MATRIX_AUDIT_v0.1.md`のG1〜G10のどれに対応するか
3. **境界** — この用語が対象としない範囲、他の用語との線引き（内部で断片化している場合はその区分を明記）
4. **禁止事項** — この用語に関して明示的に禁止されている行為
5. **依存関係** — 何に依存し、何がこれに依存するか

**重要な注記:** Ledger・Caliberのように内部で複数の無関係な実装に断片化している用語については、無理に単一の定義に押し込めず、「内部下位区分」として断片化の実態をそのまま記載する。これは今回の一連の監査（Concept Audit、Vocabulary Pattern Audit）で確認された事実に忠実であるための措置であり、断片化を隠蔽しない。

---

## 第1部: 現状把握

本辞典が扱う8用語は、本日一連の監査で扱った対象そのものである: Ledger、Registry、Catalog、Memory、Archive、Caliber、Loop、Approval（Human Gate）。これらのうちLedger・Caliber・Archiveは複数の無関係または未整理な実装に分かれていることが既に確認されている。Registry・Catalogは相互の境界が一部曖昧（CATEGORY_REGISTRY_v2.0が両方の調査に該当）であることが確認されている。Memory・Loop・Approvalは粒度・段階が異なる複数の要素から構成される。

---

## 第2部: 提案 — 制度辞典本体

### Ledger

| 項目 | 内容 |
|---|---|
| 責務 | 記録の追記・改ざん検知を担う（べき）概念。ただし実体は複数存在し統一されていない |
| 保証 | G2（不変性・改ざん検知保証）、G3（網羅性保証）の一部 |
| 境界 | 何が正本かは未確定（`VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md`のワークド・イグザンプルで4系統すべて「判定保留」）。KN_SERIES_LEDGERは実体そのものが未確認 |
| 禁止事項 | 追記専用が原則（Constitution「Event ledger is append only」）。上書き・削除は禁止 |
| 依存関係 | `anchor_update.py`（mocka-seal）、Decision Policy（Decision Evidence）、GL7との関係は不明 |
| 内部下位区分 | (a)`runtime\main\ledger.json`（ハッシュチェーン） (b)`mocka_events.db`+`audit_trigger.py`（SQLiteトリガー） (c)PHI-OS `decision_ledger.jsonl`（独自verify_chain()） (d)KN_SERIES_LEDGER（実体未確認） |

### Registry

| 項目 | 内容 |
|---|---|
| 責務 | システム内に何が存在するかの台帳化 |
| 保証 | G1（存在保証） |
| 境界 | 参照整合性（Referential Integrity）は保証しない（既存メモに基づく引用、要確認）。KN-004とMODULE_CATALOG_v1のスコープ境界は未確定（`CONCEPT_AUDIT_v0.1.md`第2.2節） |
| 禁止事項 | domain x categoryをまたぐ横断的競合の自動検出は行わない。人間判断（knowledge_relationshipsへの明示的記録）に委ねる（`DECISION_POLICY_v0.1.md`第5節） |
| 依存関係 | `mocka_registry_get`等のMCPツール、Decision Policy（裁定対象としてRegistryの内容を参照） |
| 内部下位区分 | KN-004（6層）、recurrence_registry、beta_registry、Impact Registry、各製品ローカルregistry（PHI-OS schema-registry、SEO-OS Capability/CommandRegistry、ed25519 keys registry）、ai_capability_registry（実装状況不明） |

### Catalog

| 項目 | 内容 |
|---|---|
| 責務 | 索引・分類による検索可能性の提供 |
| 保証 | G1（存在保証の一部）、G8（索引の一貫性という意味での単一正本保証） |
| 境界 | MODULE_CATALOG_v1とKN-004の役割分担は未確定（Registryと同一の論点）。Registryとの語彙境界も曖昧（CATEGORY_REGISTRY_v2.0が両方の調査に該当することが判明済み） |
| 禁止事項 | 明示的な禁止事項は今回の調査範囲では確認されていない（要確認） |
| 依存関係 | MODULE_REGISTRY_MODEL_v1はMODULE_CATALOG_v1の登録情報を正本として参照。MODULE_INDEX_SPEC_v1はMODULE_REGISTRY_MODELへの検索インターフェース |
| 内部下位区分 | MODULE_CATALOG_v1（マクロ層）、MODULE_REGISTRY_MODEL_v1（統合層）、MODULE_INDEX_SPEC_v1（検索層）、CATEGORY_REGISTRY_v2.0（分類層、Registryとも重複）、AUTOSEAL_SYSTEM_CATALOG_v1.0（行動記録の事実列挙） |

### Memory

| 項目 | 内容 |
|---|---|
| 責務 | 文脈・経験の保持（粒度は複数存在） |
| 保証 | G10（文脈・経験継承保証） |
| 境界 | セッション内（working_memory.py）／システム永続（data/storage/infield）／製品（Memory拡張、chrome.storage.local）／知識メタ層（Knowledge Assets・Reason Unit）の4粒度に分かれ、統合されていない |
| 禁止事項 | 記憶は参照するだけであり、強制適用は設計として禁止（`LOOP_DESIGN_PRINCIPLES.md`第4節「自動適用の禁止」） |
| 依存関係 | working_memory.pyはGL1（RepositoryGroundingEngine）からの初期化に依存。Knowledge AssetsはACTIVATION_POLICYのReview Gate（未実装）に依存 |
| 内部下位区分 | Memory拡張（Chrome拡張）、mocka-infield（独立リポジトリ、ORPHAN状態）、data/storage/infield（本体内部ストレージ）、working_memory.py、Knowledge Assets・Reason Unit |

### Archive

| 項目 | 内容 |
|---|---|
| 責務 | 非活性化された記録の保管（ただし対象ごとに意味が異なる） |
| 保証 | G2の派生（凍結後の不変性）。TIC Archiveのみ本来はG1寄り（採用履歴の保管、未実装） |
| 境界 | TIC Archive層（未実装）・Phase ARCHIVE層（凍結記録）・Module ARCHIVED状態（ライフサイクル終端）は意味論的に無関係な同語異義であり、相互に境界を持たない |
| 禁止事項 | Phase ARCHIVE層は「再構造化禁止・活性化禁止」と明記（`phase3_simulation_sealed_v1.md`、2026-06-25博士裁定） |
| 依存関係 | TIC ArchiveはTIC Layer0-1の後続段階（未接続）。Module ARCHIVEDはMODULE_LIFECYCLE_v1に依存 |
| 内部下位区分 | TIC Archive層、Phase ARCHIVE層、Module ARCHIVED状態 |

### Caliber

| 項目 | 内容 |
|---|---|
| 責務 | 品質評価・選別（対象は系統ごとに異なる） |
| 保証 | G7（品質・妥当性保証、局所的） |
| 境界 | 6系統は相互にコード共有がなく、統一された「Caliber」という単一実体は存在しない（`CALIBER_TO_SKILL_MD_GAP_ANALYSIS_v0.1.md`で確定済み） |
| 禁止事項 | テキスト濃縮系統において、復元率閾値（80%）の引き下げは禁止（`CALIBER_DESIGN_PRINCIPLES.md`第3節） |
| 依存関係 | 系統ごとに異なる（Claude API、gemma3:12b/4b等） |
| 内部下位区分 | (A)テキスト濃縮chat_pipeline (B)PlanningCaliberスコアリング (C)ドリフト監視・ルーティング (D)Connector Caliber (E)vasAI BaseCALIBER (F)Technology Intelligence Caliber |

### Loop

| 項目 | 内容 |
|---|---|
| 責務 | 反復処理の暴走防止・逸脱検知。「進捗なし（停滞）」の検知は別途新設中 |
| 保証 | G6（暴走・停滞検知保証） |
| 境界 | LOOP_DESIGN 3制約（暴走側）とDRIFT_STANDARD（逸脱側）は対象が異なる。「停滞」検知はLoop Health Index（未実装）が新規に埋める空白であり、既存2者では対象外だった |
| 禁止事項 | 自動展開禁止。同一問題への再試行は最大3回。過去実績から2段階以上の概念飛躍は棄却（`LOOP_DESIGN_PRINCIPLES.md`第3節） |
| 依存関係 | `interface\router.py`（calc_drift_v3等の実装が実ファイルに存在しない疑いあり、構文エラー・BOM混入も検出済み、要確認） |
| 内部下位区分 | LOOP_DESIGN_PRINCIPLES（暴走防止3制約）、DRIFT_STANDARD_v1.1（逸脱検知、実装疑義あり）、Loop Health Index（停滞検知、未実装の設計案） |

### Approval（Human Gate）

| 項目 | 内容 |
|---|---|
| 責務 | 最終的な意思決定の確定。AIの提案を人間の決定に変換する唯一の正規経路 |
| 保証 | G5（人間最終決定保証）、G9（権限分離保証） |
| 境界 | GL7・Knowledge Activation・Writer/Checkerとの接続に複数の断絶がある（`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`参照）。human_gate.py本体の実装は確認できるが、承認ログと実行ログの突合という検証段階は未達 |
| 禁止事項 | AIが自身の判断を自身で確定させる自動承認ループの構築禁止（自律裁定化リスク回避）。Decision Policyは「Approvalを持たない」ことが明文化されている |
| 依存関係 | Decision Policyのescalate_if_needed()から再利用される（新規実装ではなく既存submit()の再利用、TODO_401で確定）。GL7・ACTIVATION_POLICYのReview Gateからは接続待ちの状態にある |
| 内部下位区分 | 特になし（human_gate.py自体は単一実装だが、接続元は複数存在し断片的に接続されている） |

---

## 第3部: 未確定事項

- 「保証」列でのG番号対応は`GUARANTEE_MATRIX_AUDIT_v0.1.md`の作業分類に基づくものであり、その分類自体がまだ確定していない（同ファイル第3部参照）
- 「境界」「禁止事項」列の一部は「今回の調査範囲では確認されていない」ことを「存在しない」ことの証明として扱っていない。特にCatalogの禁止事項は未確認のままである
- 本辞典は8用語に限定しており、今回の一連の監査で言及された他の用語（例: Decision Evidence、Knowledge Assets自体、GL7そのもの）は独立した見出しとして立てていない。将来的に辞典を拡張する場合は、これらも同一フォーマットで追加することが考えられる
- 本辞典とTERM-001（`TERM-001_REGISTRY_TERMINOLOGY.md`）との統合・改訂は、Task-G（`VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md`第3部）で既に「次回TERM-001改訂時に合わせて解消するのが効率的」と記録済みであり、本辞典はその際の参照材料の一つと位置づけられる

---

## 改訂履歴

- v0.1（2026-07-03）: 博士指示Task-Nに基づき新規作成。
