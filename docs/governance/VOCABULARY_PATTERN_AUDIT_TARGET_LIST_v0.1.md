# Vocabulary and Pattern Audit — 対象一覧 v0.1

位置づけ: くろこ作業指示（2026-07-03、Task-F）に基づき新規作成。Vocabulary and Pattern Audit本体（git回復後、人間承認を得てから正式着手）の対象範囲を確定する準備文書。新規のコード・ファイル調査は行わず、本日までに作成済みの以下4文書の内容を集約したのみである。

- `docs\governance\CONCEPT_AUDIT_v0.1.md`
- `docs\caliber\CALIBER_TO_SKILL_MD_GAP_ANALYSIS_v0.1.md`
- `docs\caliber\LOOP_HEALTH_INDEX_DESIGN_v0.1.md`
- `docs\governance\VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md`（Task-E、本ファイルと同時並行で作成）

本ファイルはコードではなく監査対象の整理文書である。v0.1とし、v1.0は名乗らない。実装・コード変更は一切含まない。

---

## 第1部: 現状把握 — 対象別サマリ

| 対象 | 今日時点でわかっていること | 出典 | Task-E基準での既知/未知 |
|---|---|---|---|
| **Ledger** | ledger.json（ハッシュチェーン、schema.pyのappend_event()で書込）/ mocka_events.db+audit_trigger.py（MCP経由・event_gate一元化）/ decision_ledger.jsonl(PHI-OS ISE、独自verify_chain())/ KN_SERIES_LEDGER(CATEGORY_REGISTRY_v2.0が一次ソースと言及、実体未確認)の3〜4重存在疑い | CONCEPT_AUDIT_v0.1.md 2.1節 | 4候補すべて「判定保留」（VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md 2.4節のワークド・イグザンプルで確認済み）。KN_SERIES_LEDGERは4観点すべて不明で最優先の実体確認対象 |
| **Registry** | KN-004（6層、存在確認台帳、正式帰属先ディレクトリ未確定）/ recurrence_registry（再発傾向）/ beta_registry（仮説成長管理）/ Impact Registry / PHI-OS schema-registry / SEO-OS Capability・CommandRegistry / ed25519 keys registry / ai_capability_registry（実装状況不明）。単体クラスタでは「階層が異なるため重複ではない」と判定済み | CONCEPT_AUDIT_v0.1.md 1.1節 | KN-004とMODULE_CATALOG_v1のスコープ重複疑い（両者が相手を参照していない）が未検証。この1点のみTask-Eの4観点で洗い直す必要がある |
| **Catalog** | MODULE_CATALOG_v1（マクロ層、モジュール一元台帳）/ MODULE_REGISTRY_MODEL_v1（統合層）/ MODULE_INDEX_SPEC_v1（検索層）/ CATEGORY_REGISTRY_v2.0（分類、Registry調査にも同時該当＝語彙境界の曖昧さあり）/ AUTOSEAL_SYSTEM_CATALOG_v1.0（行動記録の事実列挙）。Catalog内部は階層構造であり重複ではないと判定済み | CONCEPT_AUDIT_v0.1.md 1.4節、3.3節 | KN-004との重複疑い（Registry行と同一論点）。CATEGORY_REGISTRY_v2.0が「Registry」と「Catalog」のどちらの語彙が適切かという用語整理の論点も残る（統合提案ではなく用語整理の論点として記録するのみ） |
| **Archive** | TIC Archive層（外部知見採用後の保管、未実装）/ Phase ARCHIVE層（非構造・凍結された設計記録、活性化禁止）/ Module ARCHIVED状態（ライフサイクル終端、巻き戻し不可）の3つの無関係な意味で使われている可能性大。同語異義であり、重複実装ではなく用語の混同リスクとして分類済み | CONCEPT_AUDIT_v0.1.md 1.4節、3.1節 | 3者は「書き込み経路」「読み取り経路」が明確に異なる別実装（TIC=data/tic配下の未実装コード、Phase=凍結文書、Module=lifecycle状態遷移）と考えられるため、Task-E基準では恐らく「分離が必要」に分類される見込みだが、正式判定は本体監査で実施する |
| **Memory** | Memory製品（Chrome拡張、chrome.storage.local）/ mocka-infield（独立リポジトリ、BINDING_GAP_REPORT_v1 GAP-O01で「ORPHAN」と明記済みの既知の欠落）/ data/storage/infield（本体内部ストレージ）/ working_memory.py（GL2セッション内キャッシュ）/ Knowledge Assets・Reason Unit（ACTIVATION_POLICY_v0.1.md）。粒度が異なるため重複ではないと判定済み | CONCEPT_AUDIT_v0.1.md 1.3節 | mocka-infieldのORPHAN状態は「重複」ではなく「未接続」という別種の問題であり、本Vocabulary Auditのスコープ（同名/異名の役割重複判定）には本来含まれない可能性がある（要確認：対象に含めるか博士判断が必要） |
| **Loop** | LOOP_DESIGN_PRINCIPLES.md（暴走防止3制約：ループ上限3回・飛躍検知2段階・自動展開禁止）/ DRIFT_STANDARD_v1.1.md（Drift基準、NORMAL/WARNING/DANGER/CRITICAL、算出式ERROR含有率*0.6+router介入率*0.4）/ interface\router.pyのcalc_drift_v3・calc_error_rate・classify_anomaly（MOCKA_OVERVIEW.json記載の関数群だが、Loop Health Index設計時の実読調査で実ファイルに存在しないことが判明。加えて同ファイル128行目に構文エラー、冒頭にBOM混入がありast.parseが失敗することも検証済み）/ Loop Health Index設計（新設提案、既存指標との重複なしと判定済み） | LOOP_HEALTH_INDEX_DESIGN_v0.1.md | router.pyの構文エラー・BOM混入・記載関数の不在は「ドキュメントと実コードの乖離」という別種の問題であり、Vocabulary and Pattern Audit（用語・パターンの重複監査）の対象ではない。本Auditでは扱わないことをここで明記する（対応は別途、博士判断が必要） |
| **Caliber** | 確定済み。相互にコード共有のない6系統（A:テキスト濃縮chat_pipeline / B:PlanningCaliberスコアリング / C:ドリフト監視・ルーティング / D:Connector Caliber / E:vasAI BaseCALIBER / F:Technology Intelligence Caliber）。SKILL.md変換の親和性はB・Eが高い | CALIBER_TO_SKILL_MD_GAP_ANALYSIS_v0.1.md | 7対象中、唯一「単体クラスタ内ですでに明確な多重発明が確定している」対象。Task-Eの4観点（書込/読取/失敗時挙動/参照元）による正式な再点検は本体監査でまだ実施していない |

---

## 第2部: 提案（本体監査の進め方に関する案。統合・削除・命名変更の提案ではない）

### 2.1 調査順序案（暫定・非確定）

以下は、Task-Eの判定基準に基づいて「不明な観点の数が多い＝解像度が低い」対象を優先する、という単純な基準による調査順序の案である。確定した優先順位ではなく、博士確認を経てから採用の可否を判断すること。

1. **KN_SERIES_LEDGER の実体確認**（4観点すべて不明。Ledger疑惑全体の判定保留を解消する前提条件になっている）
2. **KN-004 Registry と MODULE_CATALOG_v1 の相互参照確認**（Registry行・Catalog行の共通論点であり、1回の調査で2対象の疑問を同時に解消できる）
3. **Ledgerクラスタの残り3候補**（ledger.json / mocka_events.db+audit_trigger.py / decision_ledger.jsonl）の(3)失敗時の挙動・(4)参照元一覧の確認
4. **Archive の3層**（同語異義の確認。恐らく「分離が必要」で決着する見込みだが、正式な4観点記録を残すため実施）
5. **Caliber の6系統**への4観点の正式適用（既に多重発明が確定しているため優先度は相対的に低いが、統合検討の材料として4観点記録を残す価値がある）

### 2.2 Loopに関する特記事項の切り分け提案

router.pyの構文エラー・BOM混入・記載関数の不在は、用語・パターンの重複監査とは性質が異なる問題（コードの実態とドキュメントの乖離、および構文エラーそのものの是正）である。本Vocabulary and Pattern Auditの対象からは除外し、別途「ドキュメント-実装整合性の確認」という異なる作業として扱うことを提案する（今回はこの提案をするのみで、対応そのものは行わない）。

### 2.3 Memoryのスコープ確認提案

mocka-infieldのORPHAN状態は「同名・異名の役割重複」ではなく「設計されたが未接続」という別種の欠落であるため、本Vocabulary and Pattern Auditの対象に含めるべきか、博士に確認することを提案する。

---

## 第3部: 参考情報（Task-G、今回対応不要）

`docs\governance\TERM-001_REGISTRY_TERMINOLOGY.md`は既に一部語彙の定義を持っている。次回TERM-001改訂時に、本Audit（および先行するCONCEPT_AUDIT_v0.1.md）で見つかった曖昧語彙（Archive、Registry/Catalogの境界等）を合わせて解消するのが効率的と考えられる。今回はTERM-001の改訂そのものは行わない。この情報は記録のみを目的とし、対応の要否は別途判断される。

---

## 第4部: 未確定事項

- 「一致」の判定閾値の妥当性（Task-E側の課題）は、本体監査を実際に走らせて初めて検証できる
- 上記2.1の調査順序案は、不明観点の数のみを基準にした単純な案であり、実際の重要度・リスクの高さは反映していない。優先順位の確定は博士判断を要する
- Memory行・Loop行のスコープ確認提案（2.2、2.3）は、本Audit自体の対象範囲を狭める可能性があるため、確定前に博士確認が必要

---

## 改訂履歴

- v0.1（2026-07-03）: くろこ作業指示Task-Fに基づき新規作成。
