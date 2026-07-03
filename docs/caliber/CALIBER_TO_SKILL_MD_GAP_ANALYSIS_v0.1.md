# Caliber to SKILL.md Gap Analysis v0.1

位置づけ: くろこ並行作業指示（2026-07-03）Task-Aに基づき新規作成。MoCKAに分散する「Caliber」実装群を実地調査し、Anthropic Claude CodeのSKILL.md形式（外部公開可能なパッケージ形式）へ変換できるかを検討する。

本ファイルはコードではなく調査・提案文書である。実装は一切含まない。既存ファイルの変更も行っていない。

参考: `C:\Users\sirok\MoCKA\docs\governance\EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.md`にて、本件（Caliber→SKILL.md対応調査）は暫定的に「実験対象（Experiment）」に分類されている。本文書はこの分類を追認・変更するものではない（それはTask-Dの管轄）。

---

## 第1部: 現状把握

### 1.1 調査方法

`C:\Users\sirok\MoCKA\`配下をGrep/Glob/Readで実地調査した。TODOデータ（MOCKA_TODO.json等）の"Caliber"関連記述もあわせて確認した。SKILL.mdの実例については、このマシン上の`C:\Users\sirok\.claude\plugins\marketplaces\claude-plugins-official\`配下に実在するファイルを一次情報として参照した。

推測で断定した箇所はなく、実際に読んだファイルパスと記述内容のみを根拠とする。判断がつかない箇所は「不明・要確認」と明記する。

### 1.2 MoCKA内「Caliber」実装の現行一覧

実地調査の結果、MoCKA内の「Caliber」は単一概念ではなく、相互にコード共有・呼び出し関係を持たない**少なくとも6系統**に分かれていることが判明した。各系統内でもファイルが独立している場合がある。

#### 系統A: テキスト濃縮Caliber（chat_pipeline）

| ファイル | 役割 | 稼働状態 |
|---|---|---|
| `docs/caliber/CALIBER_DESIGN_PRINCIPLES.md` | 設計原則書v1.0（2026-04-03制定）。言語統一・均等サンプリング・復元率閾値80%等の原則を定義 | 文書として存在。原則書内の`sample_text()`例（chunk_size=2000、閾値80%）と実装側の値には差異がある（後述1.4） |
| `caliber/chat_pipeline/mocka_caliber_server.py` | port 5679で稼働するFlaskサーバー。チャットログの重要文抽出・復元率算出パイプライン本体。v5でAPIゼロ化（Claude Haiku API呼び出しをローカル処理へ置換）。docstringに「Author: Claude（執行官） Date: 2026-04-27」 | MOCKA_OVERVIEW.jsonの`verified_working`に「Caliber pipeline -> localhost:5679 稼働（APIゼロ v5）」と明記。稼働中と判断できる一次記述あり |
| 同ファイル内「PHL-OS Caliber Integration v1」ブロック | AI応答モード選択エンジン（ghost/L99/OODA/SAGE/STRATEGIST等）。別イベント（E20260514_040）に紐づく別機能が同一ファイルに追記合体されている | チャット要約機能とは無関係の別機能が同居している状態 |
| `caliber/chat_pipeline/mocka_caliber_server_backup.py` 等バックアップ・`.bak`ファイル複数 | 旧バージョンの残存 | 非稼働（バックアップ） |

#### 系統B: PlanningCaliber評価スコアリング系

| ファイル | 役割 | 稼働状態 |
|---|---|---|
| `PlanningCaliber/PLANNING_CALIBER_LAW_v1.md` | 2026-06-17制定の基本法。「workshop→Caliber→PlanningCaliber」のフィードバックループ、「Caliber = PlanningCaliber内部監査部門・評価/採用判定/改善指示・統制機構（非生成）」と定義 | 制度文書として確定済み |
| `PlanningCaliber/caliber/SCORING_SPEC_v1.md` | スコアリング仕様書v1.0（2026-06-17制定、イベントID E20260617_017）。5軸（再現性R・構造明確性S・実装安定性St・拡張性E・外部価値X、各0.0〜1.0）、CaliberScore=(R+S+St+E+X)/5、閾値0.85でspecs昇格・0.65でcandidates・未満でworkshop再実験 | 実装ファイルと完全一致を確認済み |
| `PlanningCaliber/caliber/caliber_score.py` | 上記仕様のCLI実装（283行）。対話モード・JSON入力モード・履歴一覧モードを持つ。評価結果を`evaluation_history.jsonl`にJSONL保存 | 単体で完結する独立CLIツール。稼働記録（実行ログ等）は本調査では確認できず、実運用頻度は不明・要確認 |

#### 系統C: ドリフト監視・ルーティング・信頼度評価の寄せ集め群

| ファイル | 役割 | 稼働状態 |
|---|---|---|
| `caliber/caliber_engine.py` | `runtime/record/event_log.csv`を読み、独自のL/E/A/P/C/R/D（7項目）スコアからNORMAL/WARNING/DANGER/CRITICALを判定する簡易スクリプト | 参照先`event_log.csv`の実在は本調査で未確認。系統Bの5軸（R/S/St/E/X）とは名称が一部重複するが計算式・意味は別物 |
| `caliber/caliber_monitor.py` | `caliber_engine.py`をサブプロセス実行し結果を`data/events.csv`に追記する監視スクリプト（自称「Caliber-B Monitor」） | 書き込み先の`data/events.csv`はMOCKA_OVERVIEW.jsonに「廃止済み・SQLite単一化完了（2026-06-16移行）」と明記されている。**現状では実効性を持たない可能性が高い**（一次記述同士の突合による指摘であり断定はしない） |
| `interface/router_caliber.py` | 同じく`caliber_engine.py`をサブプロセス実行し、CRITICAL/DANGER/WARNING文字列でaudit_only等のルーティング判定を返す | `caliber_monitor.py`とロジックがほぼ重複 |
| `interface/trust_score_caliber.py` | AIメンバー（Gemini/GPT/Claude等）のタスク実行ログからTRUST_SCOREを算出。重み付け軸はaccuracy(0.30)/reproducibility(0.25)/nonvalue_match(0.20)/confidence_consistency(0.15)/history_alignment(0.10) | 保存先が`C:\Users\sirok\planningcaliber\data\scores`（MoCKA本体外の別リポジトリ、`repositories.caliber_workspace`として登録済みパス）。系統Bとは軸名も保存先も別 |
| `runtime/caliber_selector.py` | AIプロバイダ（Gemini/GPT/Claude/Perplexity）に固定スコア(3/4/5/2/1)を振り最大値を選ぶスタブ | コード内コメントに「仮スコア（後で実データ接続）」と明記。**未実装・プレースホルダ段階であることが一次記述で確認できる** |
| `runtime/analysis/caliber_drift_bridge.py` | `runtime/state/drift_state.json`を読み`runtime/state/caliber_state.json`の`mode`を書き換えるブリッジ（コメント「Phase5-B1: Drift予兆→Caliber-B連動」） | `caliber_state.json`を介して系統C内の一部ファイルとのみ疎結合。直接のimport関係はなし |
| `runtime/state/caliber_state.json` | 状態スナップショット（`{"drift_prediction": {...}, "mode": "NORMAL"}`） | 単純な共有ファイル |

#### 系統D: Connector Caliber（API Gateway）

| ファイル | 役割 | 稼働状態 |
|---|---|---|
| `gateway/connector_caliber.py` | ファイル冒頭コメントに「Connector Caliber v1.1 / Role: gateway/ を MoCKA Caliber層として位置づける / ref: E20260610_017 / TODO_273」と明記。他AI（gpt/gemini/copilot）からMoCKAコンテキストを取得するFlask Blueprint型APIゲートウェイ。`ConnectorCaliber`クラス、定数`CALIBER_ID = 'connector_caliber_v1.2'`（コメントのv1.1とコード内定数v1.2で表記に差異あり） | `mocka_index_writer.py`・`connector_router.py`（TODO_273）・`connector_log.py`（TODO_274）・`interface/ai_capability_registry.py`に依存。意味辞書（`docs/reference/semantic_dictionary/raw/all_terms.md`）にシンボル登録済みで、コードベース内で認識された実体であることを確認 |

系統Dは評価・スコアリングという概念を一切持たず、「Caliber」という語を「MoCKAへの入口となるゲートウェイ層」という別の意味で使用している。

**TODO_022との関係（要確認事項への回答）**: `data/MOCKA_TODO.json`等でTODO_022の全文を確認したところ、内容は「essence疎通確認」（ping_latest.jsonのessence_updated確認、2026-04-28完了）であり、Connector Caliberとは無関係であった。Connector Caliberの実装コメントが参照するTODO番号はTODO_273・TODO_274であり、TODO_022ではない。指示文中の「TODO_022周辺で言及されたConnector Caliber」という前提は、実地調査の結果、一次データでは裏付けが取れなかった。**不明・要確認**（きむら博士に確認を委ねる）。

#### 系統E: vasAI BaseCALIBER（企業アダプター抽象クラス）

| ファイル | 役割 | 稼働状態 |
|---|---|---|
| `PlanningCaliber/workshop/vasAI_Project/docs/CALIBER_GUIDE.md` | 「Caliberとは: 企業の社内システムとvasAIを繋ぐアダプター層。BaseCALIBERを継承して5つのメソッドを実装するだけで完成する」と明記 | ガイド文書として存在 |
| `PlanningCaliber/workshop/vasAI_Project/caliber/base_caliber.py` | 抽象基底クラス`BaseCALIBER(ABC)`。企業側が実装必須の抽象メソッド5つ（`get_caliber_id`/`classify_event`/`get_approval_rules`/`format_for_intranet`/`receive_from_intranet`）と、上書き禁止の共通実装3つ（`send_to_vasai`/`receive_from_vasai`/`process_intranet_request`）を持つ。docstringに「MoCKAを知らなくても、このインターフェースだけ理解すれば良い」と明記 | `PlanningCaliber/workshop/`配下（PLANNING_CALIBER_LAW_v1.md第2条により「唯一の実装空間」と位置づけられる領域）。本体統合済みか実験段階かは本調査だけでは確定できず、**不明・要確認** |

系統Eは評価スコアリングではなく、「継承するだけで外部システムと接続できる」という設計思想を持つ点で、後述する差分表において最もSKILL.mdの設計思想（パッケージ化・外部配布前提）に近い。

#### 系統F: Technology Intelligence Caliber（TIC）

| ファイル | 役割 | 稼働状態 |
|---|---|---|
| `interface/health_check.py`（Layer0） | 7点モーニングチェック | MOCKA_OVERVIEW.jsonに「稼働中」と記載 |
| `interface/tech_watcher.py` v3.0（Layer1） | 意味差分検知 | TODO_208完了・稼働中 |
| `data/tic/adr/ADR-001.md` | claude.ai DOM依存という制度的負債の意思決定記録（Risk Score 92 CRITICAL） | 確定済み文書 |
| `data/tic/reports/tic_report_20260601.md`、`tic_report_phase1_final.md` | 実装報告書（Phase1完了、Overall ALL PASS 7/7） | 完了報告として存在 |
| Layer2（tech_lab/ Sandbox） | TODO_205 | 未着手 |
| Layer3（impact_analyzer.py） | TODO_206 | 未着手 |
| Layer4（COMMAND CENTER TICパネル） | TODO_207 | 未着手 |

TICの「Caliber」は、外部技術（Anthropic API・Chrome MV3・Stripe等）の変化を監視しリスクスコアを算出する「防衛レイヤー」という第6の意味であり、他系統のいずれとも計算式・目的が異なる。MOCKA_TODO本文中には「Technology Intelligence Caliber」というフルスペル展開の記述は見つからなかった（mocka_get_overview()のJSON内でのみ定義されている）。

### 1.3 現状把握のまとめ（各系統の独立性についての判断）

6系統は、実際に読んだコード・コメント・ドキュメントの記述に基づく限り、コード共有・呼び出し関係・評価ロジックのいずれにおいても実質的な連続性がない。「Caliber」という語（品質・水準を測るという原義）が、複数の開発時期・目的で独立に再利用されたものと判断する。

唯一、系統C内部では`caliber_state.json`というファイルを介した疎結合（drift_bridgeが状態を書き、router/monitorが別経路で評価する）が存在するが、それも直接のコード依存ではなくファイルベースの緩い連携に留まる。

したがって、「MoCKAのCaliber」という単一の対象を前提にSKILL.md変換を論じることはできず、**どの系統を対象にするかをまず特定する必要がある**。本文書の第2部では、SKILL.mdの設計思想（外部配布可能な自己完結パッケージ）に照らして相対的に親和性が高いと判断できる系統A（テキスト濃縮）・系統B（PlanningCaliber評価）・系統E（vasAI BaseCALIBER）を中心に検討する。系統C（実効性不明な寄せ集め）・系統D（内部専用ゲートウェイ）・系統F（TIC、内部監視専用）は、外部公開パッケージ化の対象として現時点では性質が合わないと考えられる（理由は2.3で述べる）。

### 1.4 SKILL.mdの実例確認（一次情報）

このマシン上の`C:\Users\sirok\.claude\plugins\marketplaces\claude-plugins-official\`配下に、実在するSKILL.mdファイルが多数見つかった（例: `plugins/frontend-design/skills/frontend-design/SKILL.md`、`plugins/plugin-dev/skills/skill-development/SKILL.md`、`plugins/skill-creator/skills/skill-creator/SKILL.md`等）。以下はこれら実物ファイルを実際に読んだ結果に基づく一次情報であり、一般公開仕様からの推定ではない。

**実際のフロントマター構造（`frontend-design/SKILL.md`より引用）**:
```yaml
---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
license: Complete terms in LICENSE.txt
---
```

**実際のフロントマター構造（`skill-creator/SKILL.md`より引用）**:
```yaml
---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---
```

**実際のフロントマター構造（`skill-development/SKILL.md`より引用）**:
```yaml
---
name: skill-development
description: This skill should be used when the user wants to "create a skill", "add a skill to plugin", "write a new skill", "improve skill description", "organize skill content", or needs guidance on skill structure, progressive disclosure, or skill development best practices for Claude Code plugins.
version: 0.1.0
---
```

確認できたフィールドは`name`・`description`（必須の2フィールド）、`version`（一部ファイルのみ存在）、`license`（一部ファイルのみ存在）であった。指示文にあった`metadata.version`という入れ子構造は、少なくとも今回読んだ実例3件では確認できなかった（`version`はフロントマター直下のフラットなキーとして存在）。この点は指示文の前提と実物との差異であり、断定せず「実例では`metadata.version`という入れ子構造は未確認」と記録する。

**本文構造（`skill-development/SKILL.md`より）**: YAMLフロントマターの後にMarkdown本文が続き、`## About Skills`等の見出し構成、`scripts/`・`references/`・`assets/`という3種のバンドルリソースディレクトリを持つ「Progressive Disclosure（段階的開示）」設計が明記されている。本文は英語で「imperative/infinitive form（命令形）」「third-person description」で書くことが規約として明記されている。

これらは実例に基づく一次情報であり、Anthropic公式のSKILL.md仕様書そのものを直接参照したものではない点に留意する（本マシン上のプラグイン実装からの逆引きである）。

---

## 第2部: 提案

### 2.1 現行Caliber一覧とSKILL.md仕様との差分表

| 観点 | SKILL.mdが要求するもの（実例確認済み） | 系統A（テキスト濃縮） | 系統B（PlanningCaliber評価） | 系統E（vasAI BaseCALIBER） |
|---|---|---|---|---|
| 単一エントリファイル | `SKILL.md`1ファイル必須（name/description必須） | 存在しない。設計原則書（.md）と実装（.py）が別ファイル・別ディレクトリ（`docs/caliber/`と`caliber/chat_pipeline/`） | 存在しない。`SCORING_SPEC_v1.md`と`caliber_score.py`が同ディレクトリ（`PlanningCaliber/caliber/`）だが統合されたフロントマターはない | 存在しない。`CALIBER_GUIDE.md`と`base_caliber.py`が別ディレクトリ（`docs/`と`caliber/`） |
| トリガー記述（description） | 「いつ使うか」を第三者視点・具体的トリガー句で記述 | なし。設計原則書は運用ルールの記述であり、呼び出しトリガーの概念がない | なし。SCORING_SPECは評価軸の説明であり、いつ使うかの記述はない | GUIDEの冒頭一文「企業の社内システムとvasAIを繋ぐアダプター層」がdescriptionに近いが、トリガー句形式ではない |
| 外部配布時の自己完結性 | scripts/references/assetsを含め依存を內包 | `mocka_caliber_server.py`は`interface/event_buffer.py`・`interface/pattern_engine_v2.py`・SQLite（`mocka_events.db`）に依存し、MoCKA内部インフラなしには動作しない | `caliber_score.py`は外部依存なしで単体完結（`evaluation_history.jsonl`は自己完結的に生成） | `base_caliber.py`は`core.artifact_schema`/`core.audit_chain`/`core.event_store`/`core.governance`という vasAI core への依存があり、単体では動作しない |
| 実行形態 | スクリプト（scripts/）は「実行されるが読み込まれなくてもよい」ツール | Flaskサーバーとして常駐（port 5679）。スクリプト単体実行という形態ではない | argparse CLIとして単体実行可能。SKILL.mdのscripts/概念と形態が一致する | 抽象クラスであり単体実行不可（継承先の実装が必要） |
| バージョン管理 | 一部実例で`version`フィールドあり（フラット） | 設計原則書は改訂履歴表を持つが、SKILL.mdのversionフィールド形式ではない | SCORING_SPEC_v1.mdというファイル名でバージョンを表現（v1形式） | ガイド内にバージョン表記なし |

### 2.2 変換可能項目

以下は根拠付きで「そのまま、または軽微な変更でSKILL.md形式にマッピングできる」と判断した項目である。

1. **系統B（PlanningCaliber評価）の`caliber_score.py`は変換親和性が最も高い**。根拠: 外部依存がなく単体で完結するCLIスクリプトであること（1.2系統B該当行参照）、argparseによる`--project`/`--json`/`--list`という明確なインターフェースを持つこと。SKILL.mdの`scripts/`ディレクトリにこのファイルをそのまま配置し、`SCORING_SPEC_v1.md`の評価軸表・判定ルールをSKILL.md本文またはreferences/へ転記すれば、構造的な組み替えのみで対応できる可能性が高い。

2. **`SCORING_SPEC_v1.md`の評価軸定義はreferences/への転記に適する**。根拠: 既にMarkdown形式で完結した仕様書であり、SKILL.mdの「詳細情報はreferences/に逃がす」という設計原則（`skill-development/SKILL.md`内「Avoid duplication」の節）と構造的に一致する。

3. **系統E（vasAI BaseCALIBER）の設計思想はSKILL.mdの「name/descriptionのみ理解すればよい」という段階的開示の考え方と概念的に近い**。根拠: `CALIBER_GUIDE.md`の「MoCKAを知らなくても、このインターフェースだけ理解すれば良い」という記述が、SKILL.mdの「Claudeが最小限のメタデータだけで判断し、必要な時だけ詳細を読み込む」という設計思想と方向性が一致する。ただし実装（`base_caliber.py`）はvasAI coreへの依存を持つ抽象クラスであり、SKILL.mdが要求する「即実行可能なパッケージ」とは実行形態が異なる（2.3で後述）。

4. **系統A設計原則書（`CALIBER_DESIGN_PRINCIPLES.md`）のうち「言語統一」「均等サンプリング」の2原則は、独立した知見としてreferences/へ転記可能**。根拠: この2原則は特定のMoCKA内部インフラ（イベント台帳・essence等）に依存しない、テキスト処理一般に適用可能な記述である。ただし品質基準（復元率閾値）と実装のモデル運用方針（Claude API優先・gemma3補助）はMoCKA固有の運用選択であり、そのまま外部公開すると内部の技術選定判断が漏出する可能性がある（2.3参照）。

### 2.3 不足項目・論点

以下はSKILL.md形式が要求するがCaliber側に欠けている項目、またはMoCKAの内部制度依存をどう扱うかという論点である。

1. **単一エントリファイル（SKILL.md）の不在**: 6系統いずれも、名前(name)・トリガー記述(description)を統合した単一のフロントマター付きMarkdownファイルを持たない。設計原則書・仕様書・実装が別ディレクトリに分散しており（1.3の差分表参照）、変換の第一歩は「どの断片をSKILL.md本文にし、どれをreferences/に落とすか」の再編集作業になる。これは実装ではなく再編集の範囲だが、対象文書の一部書き換えを伴うため、本調査（Task-A）の範囲（実装禁止・既存ファイル変更禁止）を超える。実行する場合は別途承認とタスク化が必要。

2. **MoCKA内部制度依存（mocka_write_event呼び出し等）の扱い**: 系統A（`mocka_caliber_server.py`）は`interface/event_buffer.py`経由でMoCKAのイベント台帳（Gate Enforcement）に依存し、系統D（`connector_caliber.py`）は`MoCKAIndex`/`IndexWriter`で直接イベント記録を行う。系統E（`base_caliber.py`）も`event_store.append`・`audit_chain.sign`・`governance.process`というvasAI内部制度呼び出しを持つ。これらを外部公開Skill Packageにそのまま含めると、MoCKA固有の記録義務・監査体制の呼び出しコードが外部利用者の環境でエラーになるか、無効化されたまま形骸だけ残ることになる。**論点**: 外部公開版では該当呼び出しを（a）完全に除去する、（b）no-opスタブに置換する、（c）外部向けのオプトイン機能として明示的に説明する、のいずれかの方針が必要になるが、この判断はTask-Aの範囲外であり、方針決定には人間判断（きむら博士）が必要と考えられる。**不明・要確認**として記録する。

3. **機密情報・内部パスの分離**: 調査の過程で、複数のCaliber実装がMoCKA内部の絶対パス（例: `C:\Users\sirok\MoCKA\`、`C:\Users\sirok\planningcaliber\`）をハードコードしていることを確認した（`caliber_engine.py`のBASE_PATH、`trust_score_caliber.py`のSCORES_DIR等）。外部配布パッケージにこれらのパスをそのまま含めることはできず、少なくとも設定可能な変数への置き換えが必要になる。これは軽微な変更で済む可能性があるが、実装作業そのものは本調査の範囲外である。

4. **「Caliber」概念の対象確定が先決**: 1.3で述べた通り、6系統は独立しており、「MoCKAのCaliberをSKILL.md化する」という単一の作業は成立しない。どの系統（あるいは複数系統の組み合わせ）を外部公開の対象にするかは、本調査結果を踏まえて別途、人間判断による選定が必要である。本文書は系統B・系統Eが相対的に親和性が高いと判定したが、これは「対象として有望」という調査上の所見であり、「対象として決定した」という意味ではない。

5. **系統C・D・Fの位置づけ**: 系統C（ドリフト監視の寄せ集め）は一部が実効性を失っている可能性がある（2.1系統C該当行）ため、外部公開以前に内部でのCaliber実装自体の整理が必要と考えられる。系統D（Connector Gateway）と系統F（TIC）はいずれもMoCKA内部の運用監視・接続管理という性質上、外部公開SKILL.mdパッケージという配布形態とは目的が合わない（外部の第三者が単体で使う理由がない）。この3系統をSKILL.md化の対象とすることには、現時点では合理性が見出しにくい。**要確認**（この所見自体も人間判断による再検討の余地がある）。

6. **SKILL.md仕様の一次情報の限界**: 1.4で述べた通り、本調査で確認できたSKILL.md実例は本マシン上のClaude Codeプラグイン群（3件）に限られる。`metadata.version`という入れ子構造の要否等、指示文にあった具体的なフィールド仕様については実例で確認できなかった部分があり、Anthropic公式仕様書そのものへの参照はしていない。今後の判断ではこの限界を踏まえる必要がある。

---

## 改訂履歴

- v0.1（2026-07-03）: くろこ並行作業指示Task-Aに基づき新規作成。
