# MoCKA OPEN QUESTIONS (v0.1)

作成日: 2026-10-10
本書は、未確認事項・矛盾・重複・所在不明を記録する。推測で埋めず、確認に必要な手段を併記する。
各項目の状態は `UNKNOWN` (情報不足) または `NOT_VERIFIED` (確認未完了) とする。

| 記号 | 意味 |
|---|---|
| UNKNOWN | 情報が不足し判断できない |
| NOT_VERIFIED | 確認を試みていない、または完了していない |
| CONFLICT | 資料間で記載が食い違う |
| DUPLICATE | 同等の資産が複数ある |
| MISSING | 指示または記録で示された資産が見つからない |

---

## 1. 正本・重複

| ID | 種別 | 内容 | 確認方法 | 状態 |
|---|---|---|---|---|
| Q-01 | DUPLICATE / CONFLICT | MOCKA_OVERVIEW.json が二つある。リポジトリ内 data/MOCKA_OVERVIEW.json (A033) と外部 C:/Users/sirok/MOCKA_OVERVIEW.json (A034)。ハッシュが異なる。AI_BOOT_HUB と meta は外部版を primary とする。 | 両者の内容差分の比較 (読取のみ) | NOT_VERIFIED |
| Q-02 | DUPLICATE | TODO が二つある。data/MOCKA_TODO_ACTIVE.json (A035, 正本として宣言) と data/MOCKA_TODO.json (A036)。TODO_390_CLEANUP_CHECK は旧 MOCKA_TODO.json の削除判定を保留。 | 件数・内容の比較、削除判定の記録の確認 | NOT_VERIFIED |
| Q-03 | DUPLICATE | Essence が二つある。interface/lever_essence.json (Claude 用) と data/lever_essence.json (Gateway 用)。AI_BOOT_HUB は別ファイルと宣言。 | 内容差分の比較 | NOT_VERIFIED |
| Q-04 | DUPLICATE | Orchestra が三系統ある。(a) tools/mocka_orchestra_v10.py (Playwright)、(b) core_kernel/orchestra/ (実行エンジン)、(c) PlanningCaliber/workshop/Orchestra_Project/。MOCKA_OVERVIEW は (a) を repositories.heart.key_paths.orchestra と記す。 | 正本の宣言の確認 | NOT_VERIFIED |
| Q-05 | DUPLICATE | Relay が二つある。relay/ (Python 実装, root) と PlanningCaliber/workshop/Relay_Project/ (拡張機能の正本として宣言)。役割が異なる可能性。 | 両者の役割確認 | NOT_VERIFIED |
| Q-06 | DUPLICATE | Memory が三系統ある。memory/ (MoCKA 3.0)、core_kernel/memory_core/、feedback/。加えて PlanningCaliber/workshop/memory/ (拡張の正本として宣言)。 | 依存関係と統合状況の確認 | NOT_VERIFIED |
| Q-07 | CONFLICT | 台帳が二つある。data/mocka_events.db (AI_BOOT_HUB '唯一のイベント台帳') と runtime/main/ledger.json (MOCKA_OVERVIEW の repositories.heart.ledger)。OVERVIEW の constitution は'イベント履歴が唯一の正本'と記す。 | 両者の役割と参照元の比較 | NOT_VERIFIED |
| Q-08 | CONFLICT | 拡張機能の正本パス宣言 (extension_canonical_paths) と、root の実装 (relay/, memory/, phi_os/) の関係が未整理。 | 宣言と実体の比較。Chrome 側登録の確認 | NOT_VERIFIED |

## 2. 名称・内容の不一致

| ID | 種別 | 内容 | 状態 |
|---|---|---|---|
| Q-09 | CONFLICT | CONSTITUTION.md は実体がエンコーディング規約 (4条)。制度憲章の名称と一致しない。MOCKA_OVERVIEW の constitution 項目との関係は未確認。 | NOT_VERIFIED |
| Q-10 | CONFLICT | interface/router.py は data/events.csv を前提とする。MOCKA_OVERVIEW は events.csv を'廃止・SQLite化済み'と記す。現行の参照が残っていないかは未確認。 | NOT_VERIFIED |
| Q-11 | CONFLICT | TODO 件数集計に正規外の status が 1 件ある (保留（2026-06-15以降・設計範囲確定済み）)。CLAUDE.md は通常 TODO の status を未着手/進行中/完了/保留/廃止の5値と定める。 | NOT_VERIFIED |

## 3. 所在不明・未検出

| ID | 種別 | 内容 | 状態 |
|---|---|---|---|
| Q-12 | MISSING | 指示書の planning_caliberB (C:/Users/sirok/planning_caliberB) は存在しない。PlanningCaliber (C:/Users/sirok/MoCKA/PlanningCaliber) が該当する可能性がある。 | UNKNOWN |
| Q-13 | MISSING | JARVIS の実装体が特定できていない。docs/audits に JARVIS の文書群のみ確認。 | UNKNOWN |
| Q-14 | MISSING | GLK_RUNTIME_BRIDGE_v1.md は C:/Users/sirok/ 直下にあり、MoCKA 内には無い。 | UNKNOWN |
| Q-15 | MISSING | mocka-bridge の manifest (拡張機能の定義) 等はサブディレクトリ extension/ 内の確認のみ。 | NOT_VERIFIED |
| Q-16 | MISSING | decision_ledger.jsonl の存在と件数が未確認 (data/decisions/ に 5 ファイル)。 | NOT_VERIFIED |
| Q-17 | MISSING | MOCKA_OVERVIEW の backup (A:/MOCKA_OVERVIEW.json) は本環境からの確認対象外。 | UNKNOWN |
| Q-18 | MISSING | MOCKA_OVERVIEW の 'data/recurrence_registry.csv'、'data/trajectory.csv' の存在は未確認。 | NOT_VERIFIED |

## 4. 実行・接続の未確認

| ID | 内容 | 必要な確認 | 状態 |
|---|---|---|---|
| Q-19 | 各サーバーが稼働しているか | 2026-10-10 に読取の health で 5000/5002/5010/5679 が応答 (200)。稼働は確認済みだが、全機能の正常性は別問題 | RESOLVED_PARTIAL (稼働のみ) |
| Q-20 | 全イベントが Event Gate を通るか | 書込経路の実行証拠 | NOT_VERIFIED |
| Q-21 | Human Gate の承認が後続の実行を止めるか | 承認前後の実行証拠 | NOT_VERIFIED |
| Q-22 | memory/ が判断の根拠として実際に利用されているか | 利用ログ, 呼出の実行証拠 | NOT_VERIFIED |
| Q-23 | 整合性検証 (event_signatures) が実行されているか | 検証の実行結果 | NOT_VERIFIED |
| Q-24 | Claude Code の PostToolUse フックが有効で発火しているか | 設定ファイルの確認と発火の証拠 | NOT_VERIFIED |
| Q-25 | gateway の HMAC secret が設定され、未設定時に拒否されるか | 環境変数の存在確認 (値は記録しない) と動作確認 | NOT_VERIFIED |

## 5. 旧仕様・廃止資産

| ID | 内容 | 状態 |
|---|---|---|
| Q-26 | docs/governance/ の v0.1 シリーズは、AI_BOOT_HUB によれば裁定待ちで凍結中。現行との関係は未確認。 | NOT_VERIFIED |
| Q-27 | AI_BOOT_HUB が参照する docs/governance/GPT_RESTRICTIONS.md は 2026-04-01 作成のまま更新が止まっている可能性あり。 | NOT_VERIFIED |
| Q-28 | 0バイトの DB (mocka_events.db, data/events.db) が存在すると AI_BOOT_HUB が記す。本環境では未確認。 | NOT_VERIFIED |

## 6. 台帳・索引の品質

| ID | 内容 | 状態 |
|---|---|---|
| Q-29 | MOCKA_OVERVIEW の session_history / next_actions が 2026-06-18 以降更新されていない (meta.staleness_note)。 | CONFLICT |
| Q-30 | ARCHITECTURE.md (root) と docs/architecture/ARCHITECTURE.md の内容差分は未比較。 | NOT_VERIFIED |
| Q-31 | ADR は ADR-001.md のみ確認。ADR 運用の範囲は未確認。 | UNKNOWN |
| Q-32 | docs/STRUCTURE.md が挙げる docs サブディレクトリの全件の実在は未確認。 | NOT_VERIFIED |
| Q-33 | data/events.csv (廃止) への参照が残るファイルの全件は未調査。 | NOT_VERIFIED |

## 7. 本作業上の注意

- events.db の when_ts 列は、文字列の min/max が日時として解釈できない値になる (観測例: min = 0e7b1bcc8cc59a9d, max = pipeline)。期間の集計は行っていない。when_ts の形式は UNKNOWN。
- 本作業では events.db に対して読取専用の件数取得のみを行った。CHANGE_START / CHANGE_DONE の記録は、利用者の'DB の書換え禁止'の指示を優先し、書込していない。
- CLAUDE.md は作業ごとに CHANGE_START / CHANGE_DONE の記録を求める。本作業の記録は未実施。利用者の判断で補完すること。

## 8. 2026-10-10 実証作業で追加した項目

| ID | 種別 | 内容 | 状態 |
|---|---|---|---|
| Q-34 | CONFLICT (参照切れ) | イベント HG-GD-001 (E20260913_4757723792197) は Decision DC_20260913_001 を参照するが、data/decisions/decision_ledger.jsonl (110行) にも mocka_decision_list (110件) にも存在しない。mocka_decision_get は not_found を返す。 | BLOCKED (原因未確認: ID 採番の不一致か、未記録か) |
| Q-35 | CONFLICT (参照切れ) | memory/data/memory_store.json の全エントリ (180件) の metadata.decision (例: DEC_8ec12609) は Decision Ledger に 0件。メモリから判断記録への参照が解決できない。 | BLOCKED (同上) |
| Q-36 | DESIGN QUESTION | MCP の read 経路 (_db_read_events, mocka_mcp_server.py:125 / :981) と governance/write_path/runtime/generator.py は data_integrity が normal/alt_schema_intentional/NULL のみを読む。corrupted_migration の 22 件は読取から外れる。これが意図した隔離か、欠損の見落としかは HG 判断事項。 | HG_DECISION_REQUIRED |
| Q-37 | AUTHORIZATION | 2026-10-10 の mapping/ 作成に対する正式な変更記録 (補完) は、mocka_write_event が GL7_EXECUTION_BLOCKED (GL8_FAIL_1_NO_DECISION_ID) で拒否。decision_id の発行は HG 判断。 | BLOCKED_AUTHORIZATION |
| Q-38 | RELEVANCE | MemoryRetriever.retrieve は無関係語でも同じ上位3件 (スコア約0.15, 最新順) を返す。完全一致IDでは首位が変わるため、語句照合は働くが、一般的な質問への関連性は弱い。 | NOT_VERIFIED (改善方針は未決) |

## 9. 2026-10-10 第3回の更新 (verify_memory_chain.py で再現)

| ID | 更新前 | 更新後 | 根拠 |
|---|---|---|---|
| (更新) Q-34 | BLOCKED (原因未確認) | ORIGIN_IDENTIFIED: 未記録の宣言。DC_20260913_001 はイベント E20260913_4610548024b79 (2026-09-13 09:07:41) の本文に初めて現れる。Decision Ledger、event DB の決定系テーブル (authorization_state / execution_log / authorization_provenance)、human_gate_events (同日0行)、decision_id_counters (20260913 行なし) のいずれにも記録が無い。欠落であり、改名・移動の証拠は無い | verify_memory_chain.py Q-34 |
| (更新) Q-34 範囲 | (未確認) | event 本文の DC_ 参照 306 件 (distinct) のうち 274 件が Decision Ledger に無い (2026-07 198件, 08 39件, 09 37件)。274件すべてが event DB の決定系テーブルにも無い | 同上 |
| (更新) Q-35 | BLOCKED (参照解決不能) | NAMESPACE_DERIVED: メモリの decision は 'DEC_' + execution_trace_id の末尾8文字 (180件中180件)。closed_loop_runner.py:41 build_decision が生成する導出名で、採番ではない。台帳に0件。ETID も events.trace_id に0件 (156件中0件)。解決は ETID (memory の execution_trace_id) を経由するしかないが、その先のイベント記録も無い | verify_memory_chain.py Q-35 |
| (更新) Q-38 | NOT_VERIFIED (関連性弱い) | CAUSE_IDENTIFIED: 検索エンジンの故障ではなく索引対象の範囲と、閾値の無さ。index (memory_index._entry_text) は rationale/selected_action/summary_text/title/description/intent_key/phase/active_task とタグのみを対象とする。既存180件はタグと ETID しか持たず、概念語 (Governance, Knowledge Activation) は索引に0件。スコアは similarity (語句一致数/5、上限1.0, 重み0.20) + recency (位置/件数, 重み0.15) で、閾値が無いため一致0件でも最新3件が返る | verify_memory_chain.py Q-38 |

### 新規

| ID | 種別 | 内容 | 状態 |
|---|---|---|---|
| Q-39 | CONFLICT (二重の決定ストア) | event DB の authorization_state は decision_id 54件 (DC_ 形式 53件)、execution_log 27件のうち DC_ 形式、authorization_provenance 1件 (DC_20261006_001)。Decision Ledger 側でも一致するのは 1件のみ。決定の正本がどちらか未定 | BLOCKED (HG判断: 正本の宣言) |
| Q-40 | RISK (採番の二重) | DC_YYYYMMDD_NNN を採番する関数が2つある。phi_os/human_gate.py:163-188 は human_gate_events の approve 行 (UTC日付) を読み、mocka_mcp_server.py:459-475 は decision_ledger.jsonl を読む。同じ形式・別の読取元のため、同日に同じ番号を採番しうる | NOT_VERIFIED (再現には書込が要る。書込は行わない) |
| Q-41 | UNVERIFIED CLAIM | メモリ180件は authority = 'Human Gate' を持つが、対応する Decision Ledger 記録もイベント記録も確認できない。権限の主張は未検証のまま。権限をメモリから導出してはならない | UNRESOLVED |
| Q-42 | CALL PATH | Memory の判断向け呼出しは decision_outcome.build_decision_outcome -> extract_evidence_from_outcome のみ確認。これは closed_loop_runner.run_in_process からのみ呼ばれ、その呼出し元はテスト・検証モジュールだけ。本番の判断経路からの呼出しは未確認 | STATICALLY_TRACED |

### 判断が必要な事項 (HG)

1. Q-39: 決定の正本 (Decision Ledger か event DB の決定系テーブルか) の宣言。
2. Q-36 (既出): corrupted_migration の読取除外の扱い。
3. Q-37 (既出): 変更記録の補完に必要な decision_id の発行。
4. Q-40: 採番元の一本化 (どちらの読取元を正とするか)。
5. Q-38 の改善のうち、Memory 本体の変更 (索引対象の拡張、閾値の導入) の可否。

## 10. 2026-10-10 第4回: Q-40 隔離検証, Q-38 評価, 検証器の堅牢性

### Q-40 (採番) の訂正と実証

| 項目 | 結果 | 根拠 |
|---|---|---|
| MCP 側の採番 (_next_decision_id) | 定義のみで呼出し元なし (dead code)。前回の'二つの採番が衝突しうる'は、現行では誤り | grep: mocka_mcp_server.py:459 のみ。mocka_decision_write は decision_id を引数で受け取る (必須) |
| 現行の採番 | phi_os/human_gate.py:163-195 の approve() 内で1か所のみ。読取元は human_gate_events の approve 行 (LIMIT 1000, UTC 日付) | 静的読取 |
| 排他制御 | なし。採番と記録の間に予約が無く、同じ event_id 以外の一意制約も無い (decision_id に UNIQUE なし) | human_gate_events の定義 |
| 実データの衝突 | DC_ 形式の承認ID 72件に重複なし。重複 3件 (DECISION_STEP3_001 等) はすべて呼出し元指定の非 DC_ 形式 | 読取専用の集計 |
| decision_id_counters | どこからも読み書きされない残存テーブル | grep |
| 隔離再現 (mapping/verify_decision_allocation.py) | C1 逐次: 一意。C2 書込前の2回読取: 同一番号 (決定的)。C3 並行8スレッド: 試行 10 回中 10 回で重複 (余分 70 件)、エラー無し。C4 記録失敗後の再試行: 同じ番号が再利用され、重複なし。C5 呼出し元指定の重複: 受理される | 一時 SQLite のみ。本番 DB は mtime 不変を確認 |

判定: 同時実行での重複発生は隔離環境で再現した (CONFIRMED_IN_ISOLATION)。本番での発生は未確認 (実データに DC_ 形式の重複は無い)。発生の前提は、同じ日付の approve が並行に走ること。

前提となる HG 判断: Q-39 (正本の宣言) の後に、採番を正本の側へ置くべき。共通採番方式は今回は実装しない。

### Q-38 (検索) の原因の確定

- 原因1 (正規化): similarity = 一致語数 / 5 (上限 1.0)、重み 0.20。1語の完全一致は 0.04 にしかならず、最新3件の recency (0.15) に負ける。
- 原因2 (索引対象): 既存180件はタグと ETID だけを索引に持つ。概念語は索引に0件。
- 原因3 (閾値の無さ): 一致0件でも最新3件を返す。
- 評価 (mapping/evaluate_memory_retrieval.py, 5 ケース, 3 候補。Memory 本体は変更せず評価側で模擬):

| ケース | current | zero_hit (閾値のみ) | extended (索引拡張) | normalized (語数で正規化) |
|---|---|---|---|---|
| known_etid | MISS | MISS (閾値が既知IDも落とす) | HIT | HIT |
| known_decision_id | MISS | MISS | HIT | MISS |
| concept_absent | FALSE_POSITIVE | OK_EMPTY | OK_EMPTY | OK_EMPTY |
| unrelated | FALSE_POSITIVE | OK_EMPTY | OK_EMPTY | OK_EMPTY |
| no_record_word | FALSE_POSITIVE | OK_EMPTY | OK_EMPTY | OK_EMPTY |

- 観察: 閾値だけでは既知IDを落とす (索引にIDが無い場合)。正規化だけでは DEC_ 導出名を拾えない。索引拡張と正規化を組み合わせる必要がある。
- 限界: ケースは5件で、標本は小さい。評価指標は HIT/MISS と FALSE_POSITIVE に限る。関連性の順位評価 (nDCG 等) は、正解ラベルが揃った後に行う。

### 検証器 (verify_mapping.py) の堅牢性監査

| 試験 | 旧版 | 新版 |
|---|---|---|
| P1/P2 平文・コード内の状態語 | FAIL (正) | FAIL (正) |
| N1 否定文 (印なし) | PASS (緩い) | FAIL (厳格) |
| N2 否定文 + 印 [非主張] | PASS | PASS |
| E1 小文字 | PASS (見逃し) | FAIL |
| E2 ハイフン | PASS (見逃し) | FAIL |
| E3 '対象外ではない'で同行に紛れる | PASS (回避) | FAIL |
| E4 バックスラッシュ分割 | PASS (見逃し) | FAIL |
| E5 空白区切り | (未試験) | FAIL |
| E6 太字分割 | (未試験) | FAIL |
| 証拠 USED を static のみ | FAIL (正) | FAIL (正) |
| 証拠 VERIFIED を db のみ | FAIL (正) | FAIL (正) |
| runtime_read に日付なし | (検査なし) | FAIL (追加) |

- 旧版の否定語による例外は、回避可能だったため撤廃。現行は明示的な印 [非主張] のみ許可。
- 既存資料の3か所は、印 [非主張] を付けた (状態の使用箇所は、他に無い)。
- 残る弱点:
  1. runtime_read は、日付が書かれているかしか確認できない。実際に観測したことは検証できない (記録の真正性は証明できない)。
  2. 本文中の件数 (例: 57件) と ASSET_INDEX の実件数の一致は検査していない。
  3. status.verification の VERIFIED と、SCHEMA の段階 RUNTIME_VERIFIED は、名前が似ている。SCHEMA 9節で軸と段階を分けて定義した。

### 新規 HG 判断事項 (今回の追加分)

- Q-40 の正本: どちらの読取元 (human_gate_events か decision_ledger) を採番の正とするか。
- Q-40 の一意性: 採番と記録を一体の排他処理にするか、一意制約を設けるか。いずれも Memory・台帳・イベント DB の変更を伴う。
- Q-39 は未解決のまま。Q-39 の判断前に、参照記録の補完はしない。

## 11. HG 判断資料

判断事項の事実・選択肢・禁止操作は [HG_DECISION_PACKAGE.md](HG_DECISION_PACKAGE.md) に集約した。Q-39 が依存の起点である。

## 12. 最終監査 (2026-10-10) で追加した未解決事項

| ID | 種別 | 内容 | 状態 |
|---|---|---|---|
| Q-43 | CONFLICT (台帳の重複) | DC_20261006_001 が台帳に 2 行 (108 行, 109 行; approved_at 09:28:14 と 09:28:27)。内容は同一。書込み主体は未特定 | UNRESOLVED (Q-39 に依存) |
| Q-44 | CONFLICT (権限の第三の記録) | governance/authority_registry/authority_registry.json の 4 件 (HG-RCL-20261004-001〜004) は、台帳・event DB・human_gate_events に一致が無い。HG_RCL_20261004_003 は、独立記録の欠落を認める | UNRESOLVED (Q-41 に依存) |
| Q-45 | UNVERIFIED (実行時の効力) | Orchestra の RuntimeGate は authorization_records を検査するが、そのストア (core_kernel/orchestra/data/mocka_orchestra.db) は全テーブル 0 行。検査が実行経路で評価された証拠は無い | NOT_VERIFIED |
| Q-46 | UNKNOWN (書込み元) | authorization_state (69 行) の書込み元は .py で未検出。granted_by に AI_AUTHORITY 30 件 | UNKNOWN |
| Q-47 | UNKNOWN (書込み元) | 台帳の system:jarvis_observability 47 件の書込み元は .py で未検出。内容は GL7 の遮断観測 | UNKNOWN |
| Q-48 | RISK (経路の到達性) | app.py の /audit/seal (POST) は seal_governance_gate を経由し、台帳に書込む (approved_by system)。台帳内の該当記録は 0 件。ルートは未実行 (実行しない) | NOT_VERIFIED |

## 13. 残存証拠の出所追跡 (2026-10-10 第7回) で追加した未解決事項

ID は既存 Q-01 から Q-48 と衝突しない (Q-49 から)。

| ID | 種別 | 内容 | 状態 |
|---|---|---|---|
| Q-49 | CONFLICT (文書と実データ) | docs TERMINAL_GOAL_READINESS_ANALYSIS_20261003.md:145 は'268 HG events in authorization_state (no AI-generated decisions)'と記す。現在の authorization_state は 69 行で、granted_by AI_AUTHORITY は 30 行 (2026-10-10 読取)。作成時点の記録か否かは未確認 | UNRESOLVED (文書の作成時点と現在の差の由来) |
| Q-50 | CONFLICT (承認の主体) | human_gate_events の approve 行 (権限行の hg_event_source に対応する 30 件) の payload は actor に AI の主体 (gpt-4_ChatGPT 等 7 種)、authority_role は AI_AUTHORITY。approve() は actor と authority_role を検証せず、payload をそのまま記録する (phi_os/human_gate.py)。その承認が HG の判断であったかは、記録からは確定できない | UNRESOLVED (HG 判断事項: 承認主体の制度上の位置付け) |
| Q-51 | CONFLICT (規則の内部矛盾) | docs/mocka3/DECISION_LEDGER_SCHEMA_v1.md §7 は'既存レコードの上書き・削除禁止'と'旧レコードの superseded_by を更新する'を同じ節で記す。§4 の'重複禁止'は mocka_decision_write に検査が無く、実際の重複 (DC_20261006_001) が存在する | UNRESOLVED (規則の解釈は HG 判断事項) |
| Q-52 | UNVERIFIED (実行の由来) | AI_AUTHORITY に結合する実行 26 件の呼出し元と由来。human_identity は JARVIS_AUTOMATED (全件)、evidence 欄は None、request_executions は started のみで完了記録が無い | NOT_VERIFIED (追加の実行記録が必要) |
| Q-53 | UNVERIFIED (評価の結果) | RCL_AUTHORIZATION (4 件)、RCL_AUTHORITY_REGISTRATION (1 件)、GL8_AUTHORITY_VALIDATION (1 件) は存在するが、判定結果 (ADMIT、NON_ADMIT、PASS、FAIL 等) の構造化欄が無い。gate_decisions は 0 行 | NOT_VERIFIED |
| Q-54 | UNKNOWN (書込み主体) | authorization_state の書込み主体。テキストファイル内の INSERT/UPDATE は 0 件。CREATE 文は DB 内に存在。INSERT を禁止するトリガーは無い | UNKNOWN (DB の書込み履歴が要る) |

## 14. 2026-10-10 第8回: Q-49〜Q-54 の更新と Q-55 の追加 (HG_DECISION_PACKAGE.md 0.4 節)

| ID | 更新内容 | 状態 |
|---|---|---|
| (更新) Q-49 | 268 件を、候補の集計条件 (human_gate_events 全件 2,195、approve 164、events の Human Gate 文字列 1,050、hg_event_source 非 NULL 63 ほか) では再現できない。現行 DB と data/backup の 2026-09-28 スナップショットは、いずれも authorization_state 69 行 (AI 30)。268 の集計根拠は文書内に無い。268 を誤りとは断定しない | UNRESOLVED (原因未確定) |
| (更新) Q-50 | approve() は payload の actor と authority_role を検証せず記録する (phi_os/human_gate.py:191-196, 142-161, 102-123)。承認 164 件中、authority_role AI_AUTHORITY は 36 件 (うち 30 件が権限行に対応)。CLI 由来と思われる payload は actor を持たない。HTTP 版 http_approve は payload 全体を受け取るが、human_gate_bp は register_blueprint で登録されていない (リポジトリ内) | UNRESOLVED (HG 判断事項: 承認主体の制度上の位置付け) |
| (更新) Q-51 | DECISION_LEDGER_SCHEMA_v1.md の §4 (重複禁止) と §7 (上書き禁止と superseded_by 更新) の矛盾は、変わらず。mocka_decision_write に重複検査が無いことを確認 (1086-1131 行) | UNRESOLVED (HG 判断事項) |
| (更新) Q-52 | 26 件の result はすべて mocka_get_overview 相当の JSON (概要文書の読取と推定。推論)。判定結果の欄は無い。request_executions は started のみ。execution_log への INSERT 文は .py と文書の範囲で見つからない (書込み元は未特定) | NOT_VERIFIED (由来は未確定) |
| (更新) Q-53 | RCL_AUTHORIZATION (4)、RCL_AUTHORITY_REGISTRATION (1)、GL8_AUTHORITY_VALIDATION (1) の判定構造化欄は無い。gate_decisions は 0 行 | NOT_VERIFIED |
| (更新) Q-54 | authorization_state の INSERT/UPDATE/DELETE は、テキストファイルで 0 件。CREATE 文は DB 内に存在。更新と削除はトリガーで禁止、挿入は禁止されていない。2026-09-28 のスナップショットにも 69 行。書込み主体の履歴は、DB の外に無い限り確認不能 | UNKNOWN |
| Q-55 (新規) | 承認 payload の authority_role (AI_AUTHORITY 36 件、HUMAN_AUTHORITY 19 件ほか) と actor (AI 主体、test、test_human、approver ほか) を作ったコードが、リポジトリの .py に見つからない (authority_role の文字列は .py に 0 件)。payload の生成元が、削除された過去のスクリプト、別リポジトリ、DB 直接操作、外部ツールのいずれかは未確認 | UNKNOWN (追加の証拠が要る) |

## 15. Phase 4 で追加した未解決事項 (ID は Q-56 から)

| ID | 種別 | 内容 | 担当と次の確認 | 状態 |
|---|---|---|---|---|
| Q-56 | CONFLICT (書込み経路) | event_gate.process_event の docstring は events 保存の唯一の経路と記す。しかし seo-os の job_engine._mocka と mocka_bridge は events へ直接 SQL で書く。SEO-OS の行 44 件 (2026-06-07 から 06-12) に、DIRECT_UPDATE の監査記録が 132 件ある。トリガーの記録する actor は更新者ではなく行の who_actor のため、更新者は未特定 | 担当: 利用者と HG。次: 更新を行ったプロセスの特定 (実行ログ、時刻の照合) | NOT_VERIFIED |
| Q-57 | UNVERIFIED (認証境界) | MCP (0.0.0.0:5002) は before_request で鍵を検査せず、/mcp にも鍵の検査が無い。書込み系ツールを含む。cloudflared (mcp.nsjp.org) と ngrok が転送。到達性と実効性は未確認 | 担当: HG と利用者。次: 利用者の環境で、外部からの到達を確認 (本作業では外部試行をしない) | NOT_VERIFIED / BLOCKED_BY_HG |
| Q-58 | CONFLICT (監視の範囲) | Gate 監査の違反は 9 件。監査テーブルの DIRECT_UPDATE は 22476 件。Gate 監査は _source による分類で、更新を含まない | 担当: HG (設計判断)。次: 分類の定義の比較 | UNRESOLVED |
| Q-59 | UNKNOWN (実行時原因) | /guidelines/status は HTTP 500。ハンドラは Path を使い、app.py のモジュールレベルに Path の import が無い (静的の説明)。実行時の証拠は無い | 担当: 利用者。次: サーバーのログの読取 (再起動はしない) | UNKNOWN |
| Q-60 | UNVERIFIED (閉ループの帰結) | memory の actual_consequence は 178 件が UNKNOWN、2 件が CONFLICT。帰結が Memory に反映される経路は未確認 | 担当: 利用者 (実行系の承認が要る)。次: 承認後の隔離実行 | NOT_VERIFIED |
| Q-61 | UNKNOWN (Relay の参照) | relay/status は relay_ping.json を読み、health_check.py が参照すると記す。interface/health_check.py は存在する。ping の書込みは app.py の POST /relay/ping (2458 行付近) にある | 担当: 利用者。次: health_check の呼出し元の読取 | NOT_VERIFIED |

## 16. Phase 5 で追加した未解決事項と既存項目への追記 (ID は Q-62 から)

既存項目への追記 (Q-56、Q-57、Q-58、Q-36):
- Q-56 追記: 挿入トリガーは 2026-06-18 以降に記録を始めている。SEO-OS の挿入 (2026-06-07 から 06-12) は検出の記録が無い。更新の記録 132 件 (3 件ずつ) は、行の who_actor が SEO-OS のため、SEO-OS の更新の証拠ではない。
- Q-57 追記: /oauth/authorize は認証無しで認可コードを返す。/oauth/token のアクセストークンは保存も検証もされない。/register は誰でも登録できる。汎用プロキシ /api/<path> が :5000 へ全ヘッダと本文を転送する。
- Q-58 追記: 違反 9 件は、_source の値 orchestra_lineage の語彙不一致で説明できる (CHECK には有り、許可リストには無し)。DIRECT_UPDATE は違反の計数に含まれない。
- Q-36 追記: 22 件の corrupted_migration は、2026-06-19 00:52 の一括更新の束に含まれる (相関のみ。clean_events.py の付与と対応する)。除外の意図は未確定。

新規:

| ID | 種別 | 内容 | 担当と次の確認 | 状態 |
|---|---|---|---|---|
| Q-62 | CONFLICT (統制語彙) | events の CHECK 制約と gate_policy.py の許可リストの差分は orchestra_lineage の 1 値。gate_policy のコメントは 3 者の完全一致を規則としている。許可リストを拡張するか、CHECK と既存 9 行を扱うかは未決定 | 担当: HG。次: 選択肢の審査 (EVENT_GATE_CONTROL_PACKAGE 8 節) | HG_DECISION_REQUIRED |
| Q-63 | UNKNOWN (一括更新の実行者) | 2026-06-19 の 6 束の DIRECT_UPDATE は、reclassify_alt_schema.py と clean_events.py の UPDATE 文と相関する。実行者 (スクリプト、手動 SQL、別プロセス) は未確認 | 担当: 利用者。次: 実行ログ、スクリプトの実行記録の読取 | NOT_VERIFIED |
| Q-64 | UNKNOWN (外部の書込み元) | orchestra_lineage (9 行) と orchestra_multi_dispatcher の文字列は、リポジトリの全テキストに無い。書込み元は確認できない | 担当: 利用者。次: リポジトリ外 (拡張機能、別のリポジトリ) の検索 | UNKNOWN |
| Q-65 | UNVERIFIED (公開経路の到達) | 汎用プロキシ /api/<path> により、MCP の :5002 経由で :5000 の POST 系 (gate/event、publish 系) に到達しうる (静的)。到達性は未確認 | 担当: 利用者と HG。次: 利用者の環境での到達確認 (本作業では外部試行をしない) | NOT_VERIFIED / BLOCKED_BY_HG |
| Q-66 | UNVERIFIED (配信の実作用) | /api/action/publish_all と /api/distribution/publish は、外部配信の実装に向かう (静的)。接続器の設定と認証情報は未確認。実際の配信の有無は不明 | 担当: 利用者と HG。次: 接続器の設定の読取 (認証情報は読まない) | NOT_VERIFIED / BLOCKED_BY_HG |
| Q-67 | UNKNOWN (トリガーの作成日) | 挿入と更新のトリガーの作成日は、DB に記録が無い。挿入の検出の開始は 2026-06-18 (監査記録の最初) | 担当: 利用者。次: スキーマ変更の記録の確認 | UNKNOWN |
| Q-68 | UNVERIFIED (OAuth の実効性) | OAuth の各エンドポイントは実装されているが、利用者認証、同意、トークンの検証を行わない。実効性を示す証拠 (ログ、利用記録) は無い | 担当: HG。次: 利用の証拠の確認、要否の判断 | NOT_VERIFIED / BLOCKED_BY_HG |

## 17. Phase 6 の追記と新規項目 (証拠の統合、2026-10-10)

既存項目への追記 (当時の値は書き換えない):
- Q-56 追記: SEO-OS の 132 件の更新記録は、3 つの一括更新の束 (00:52:09、00:53:41、02:35:21) に 44 件ずつ現れる。44 行の現在の data_integrity はすべて alt_schema_intentional。reclassify_alt_schema.py の WHERE 句は ESEOS% を含む。したがって、更新は SEO-OS のコードではなく、データ整備の一括更新と相関する (実行の証拠ではない)。直接挿入 (2026-06-07 から 06-12) は残る。
- Q-59 追記: 既存のアプリ標準出力ログ (_final_app_stdout.log、mtime 2026-06-20) に name Path is not defined の記録 (guidelines_engine、ESSENCE_AUTO)。現在の app.py の /guidelines/status には Path の import が無い。現在の実行のトレースは未取得。
- Q-63 追記: 6 つの束の接頭辞 (EP_、EN8N、ESEO、UVA0、UVE6、E202) は、reclassify_alt_schema.py の WHERE と一致。実行者は未確認。canonical_trace の 2026-06-19 の 128 件に該当記載は無い。
- Q-67 追記: 検知トリガーは app.py の initialize_runtime (4150-4162 行) で毎回再インストールされる。注釈 (TODO_371) は、2026-06-20 から 06-30 の期間の検知の停止を記す。authorization_state のトリガーは、リポジトリ内に定義文が無い (DB と 2026-09-28 のバックアップにのみ存在)。
- Q-68 追記: OAuth の実験ログの送信元は 127.0.0.1 (27)、0.0.0.0 (1)。日時の記録は無い。外部からの利用の証拠は無い (網羅性は不明)。

新規:

| ID | 種別 | 内容 | 担当と次の確認 | 状態 |
|---|---|---|---|---|
| Q-69 | UNKNOWN (起動の失敗) | ESSENCE_AUTO の起動失敗 (name Path is not defined) の記録がある (既存ログ、2026-06-20 の版)。現在の interface/essence_auto_updater.py は Path を import している (12 行)。現在の起動状態は未確認 | 担当: 利用者。次: 現在の起動ログの読取 (再起動はしない) | NOT_VERIFIED |
| Q-70 | UNKNOWN (トリガーの変更) | data/reports/PRE_REINSTALL_SNAPSHOT_20260620.md:92 は trg_detect_direct_update の WHEN 条件の修正を記す。修正前の定義は保存されていない。現在の定義との差は確認できない | 担当: 利用者。次: 修正の記録と、修正前の定義の出所の確認 | UNKNOWN |

## 18. Phase 7 の参照

HG 判断資料の判断事項、選択肢、前提は IMPLEMENTATION_DECISION_PACKAGE.md の 2 節と 3 節にある。既存の Q 番号 (Q-34 から Q-70) は、その資料の各判断から参照する。新規の Q 番号は追加していない。判断状態は NOT_DECIDED のまま。

## 19. Phase 8: Q-57 と Q-65 の役割区分、Q-57 追記の範囲の訂正

Q-57 (正式な項目の定義、変更なし): MCP の /mcp の認証境界に関する静的な懸念。判断事項は IMPLEMENTATION_DECISION_PACKAGE.md の I-1 と I-3 (HG_DECISION_REQUIRED)。外部到達性は、Q-57 の対象ではなく、Q-65 の対象。

Q-65 (正式な項目の定義、変更なし): 公開経路 (汎用プロキシ /api/<path> を含む) の外部からの到達性。状態は NOT_VERIFIED。判断事項は I-1 と I-4。担当は利用者 (外部到達の確認) と HG。

役割の重なり: Q-57 の行の末尾にある 到達性と実効性は未確認 は、Q-65 の内容に属する。Q-57 の次の確認は、認証境界の判断に必要な証拠 (静的) に限る。外部からの到達の確認は Q-65 で扱う。

Q-57 追記の範囲の訂正 (17 節の 追記の訂正): 17 節の Q-57 追記には、OAuth の事実 (authorize、token、register) と、汎用プロキシ (/api/<path>) の事実が含まれる。OAuth の事実の判断事項は I-2 (Q-68)、汎用プロキシは I-4 (Q-65) に属する。Q-57 は、/mcp と書込み系ツールの認証境界に限る。17 節の記述は、当時の記録として残し、ここで範囲を示す。

I 番号と Q 番号の対応は IMPLEMENTATION_DECISION_PACKAGE.md の 9 節に一覧がある。

## 20. 閉ループ観測の未確認事項 (2026-10-11、新規の Q 番号は付与せず)

詳細は VERIFICATION_LOG.md の 21 節。以下は未確認または未実装の項目。

- 独立観測源: 既存の候補 5 件はいずれも SELF_REFERENTIAL (prism observation_engine、marker、GLK 自己申告、share_observer、drift_monitor)。INDEPENDENT_CANDIDATE は 0 件。全リポジトリの網羅探索は未実施。外部システムの状態をどこから読むかは、利用者の判断が必要。
- 実データの追跡: Memory リンク 180 件に対し、一致する Outcome は 0 件。observation_id を持つ実データの記録は無い。
- human_gate_event_id と Decision Ledger の照合: 未実装。台帳は読まれない。HG 判断の正本はどこに置くかを決める必要がある。
- Authority Registry: 既定の実行経路では適用されない (registry 引数が無い時は未適用)。
- 実 Event Store への書込みと readback: 未実施。実施の可否は HG と利用者が判断する。
- mocka_events.db-wal: 今日 14:14 に更新された。帰属は未確定 (稼働中のゲートか、別の記録処理か)。
- 既存の RCL テスト: 10 モジュールが修正前から失敗している (既定シナリオの U=MISSING による DENY、import 不足、旧い期待値)。hg_reference_limited_test と hg_rcl_004_verify の未束縛 fixture は、新ルールでは UNKNOWN になる。期待値の更新は未実施。

## 21. 2026-10-11 第18回の未確認事項 (インシデントと正本、新規の Q 番号は付与せず)

詳細は VERIFICATION_LOG.md の 22 節。

- 隔離 sandbox からの書込み漏れ (インシデント): 件数を確定できない。Event Store の読み戻しは禁止のため数えられない。受理された件数、記録の要否、障害記録 (mocka_write_event / Incident) の実施は、利用者の判断が必要。
- event_buffer.py の FALLBACK_PATH は絶対パスの固定であり、実リポジトリの data/ を指す。retry が取り込んで送信する設計になっている。これは実リポジトリの稼働 gate にも影響する設計上の欠陥。修正は本番コードの変更であり、利用者の承認が必要。
- 未対策の既存テスト: decision_ledger_persistence_test、experience_memory_integration_test など、Event Store への送信を伴うテストは、送信先を差し替えていない限り実 gate に到達しうる。実リポジトリでそのまま実行してはならない。
- 認可の正本: 既存文書の記述が衝突している (Ledger、Event Store、GATE の三者)。DP-1-B、DC_20260705_006、選択肢 C のいずれが現行かは、HG の判断事項として未決定のまま。
- WAL: 14:14:35 以降、サイズ 362592 と mtime は変わっていない。今回の作業以降は書込みが無いことの間接的な証拠。

## 22. フォールバック流入の未確認事項と設計判断 (2026-10-11、新規の Q 番号は付与せず)

詳細は VERIFICATION_LOG.md の 23 節。

- 取込みの有無と件数: events 行と gate_idempotency 行の件数は不明。読み戻しは禁止のため、利用者の承認が無い限り確認しない。
- 前回の「quarantine の 4 件」は二つの ETID の各 2 件。INSERT されていない (enforce の QUARANTINE)。ただし gate_idempotency への書込みは行われている可能性がある。
- 再発防止の設計 (R1 から R7、D1 から D3) は 23.6 節。実装は未着手。本番コードの変更 (event_buffer.py、event_gate.py の戻り値とステータス) は利用者の承認が必要。
- 送信系テストの実行: 23.5 節の一覧のテストは、隔離 (R1 から R7) が実装されるまで実行しない。
- インシデントの正式登録: 登録先 (events DB への書込みか、別の記録経路か) と認可主体は利用者が決める。重複確認は Mapping と Memory の文書で行う。

## 24. Stage 1 v3 の未解決事項 (2026-10-11 第26回。v3 設計は scratchpad/proposals/stage1_v3/ に保管)

v3 が定めた事項 (D1 の断片隔離、D3 の固定ポート、M1 の trust_env=False、4xx の保留、200 を永続化の証拠としないこと) は本節に含めない。残るのは次のとおり。
- 実装承認: 未取得。v3 は HG 審査前の設計段階。
- 起動スクリプトの変更 (MoCKA-START.bat の 67、69、70、75、76、77 行): 承認が必要。提案は launcher_proposal.md。
- 残余リスクの承認範囲: D2 (環境変数の誤設定)、D5 (二重送信)、D7 (タイムアウトの重複)、push から保存までの消失、保存先の肥大化。これらを許容するかの判断。
- 未確認 (隔離テストで確認): Windows のロック解放 (T6)、プロキシの実機での挙動 (T5)、断片の隔離と切詰めの順序 (T7、T14)。
- 4xx の保留の解除: 運用者の手順 (released の追記) を決める。自動解除はしない。
- 5xx の持続時の上限: 打ち切りの回数や時間は Stage 2 で決める。
- ライブラリ呼出しの起動経路 (14 件): どのプロセスで実行されるかの確認。

## 23. 実装前の未解決事項 (2026-10-11 第25回: Stage 1 v2 ゲート審査の結果。第26回で v3 に置換)

審査結果は scratchpad/proposals/stage1_v2/gate_review_result.md。判定は HOLD_NEEDS_DESIGN_CHANGE。解決済みの論点 (応答の意味、印の方式、環境識別の方式、許可リストの方針、リダイレクトの禁止、追記専用化) は本節に含めない。

Stage 1 v3 で直す欠陥 (設計変更):
- D1 部分書込み行の後の追記で、新しいイベントも読めなくなる。追記前の改行確認、または行ごとのチェックサムを決める。
- D3 テスト用の送信先が 127.0.0.1 の非本番ポート全般を許可する (5010 等の内部サービスに届く)。固定の一つのポートに限定するか決める。
- M1 requests の環境変数プロキシの扱い (trust_env=False にするか。実機での確認が必要)。

残余リスクとして明記し、承認に含めるか決める事項:
- D2 MOCKA_RUNTIME は環境変数のため、誤設定で本番送信しうる。識別値の設定元の制限を、どこまで求めるか。
- D5 二つの本番ゲートプロセスの間で、未送信分の二重送信が起こりうる (送信中の申告の要否)。
- D6 4xx の件は、永続的に拒否されても毎回再送される。拒否済みの印か隔離ファイルを Stage 2 で決める。
- D7 タイムアウトの件は、ゲートが処理済みでも再送される (重複)。Stage 2 の冪等性で扱う。

起動経路 (承認事項):
- MoCKA-START.bat:67 の app.py (ゲート) は MOCKA_RUNTIME を設定していない。設定を先に入れる必要がある。app.py は get_buffer().push の周辺に try が無い。
- MoCKA-START.bat:72 (SEO-OS の app.py) と vasAI-START.bat:5 (api/app.py) が、本リポジトリの event_buffer を使うかは未確認。
- ライブラリ 14 件 (watchdog_mocka 等) は、手動起動時に設定が必要。

Stage 2 へ分離: Gate の応答の意味 (永続化の結果)、events と gate_idempotency の同一トランザクション、event_id の付与、process_event の戻り値 (mocka_mcp_server.py の 356、834 行、db_helper.py 154 行、relay/mcp_bridge.py 40 行)、保持期間。

Mapping 以外の承認: 実装承認、起動スクリプトの変更、隔離テストの実行。いずれも未取得。

## 25. 閉ループ接続契約の HG 判断事項 (2026-10-11 第27回)

詳細は OPEN_CONNECTION_GAPS.md の 5 節。HG の判断は未記録。
- H1 本番の識別方式 (MOCKA_RUNTIME) の採否と、残余リスク D2 の許容 (Stage 1)
- H2 4xx 保留の解除 (released) の担当と条件 (Stage 1)
- H3 受理の応答の意味 (200 の定義、本文の結果) (Stage 2)
- H4 冪等性の記録の時点 (Stage 2)
- H5 event_id の割当 (Stage 2)
- H6 判断の正本 (Ledger、Event Store、GATE) (Stage 3)
- H7 Memory の戻り経路 (同一 ETID に限るか、異なる ETID への戻りを設計するか) (Stage 3)
- H8 本番の観測源 (observer の供給元) (Stage 3)
- H9 インシデントの正式登録先と認可主体
- H10 件数の確定のための読み戻しの承認


## 残存の不整合: 未コミットの作業状態への依存 (2026-10-17)

- 統合証拠 E016、E017、E018、E019、E020、E021 は、stash@{0} の未コミットのコードに依存する。HEAD と ce2244019 には対象の行やシンボルが無い。
- 扱い: 既知の不整合として記録。状態の降格 (CODE_CONFIRMED から PARTIAL) またはステータスの維持は、未決。
- 判断: 降格するか、stash の内容をコミットするか。コミットは Git への書込みのため、別途の承認が要る。

## 23. HG GO 後の残存課題 (2026-10-17、次フェーズのバックログ)

- B1 統合データの 13 件 FAILED (verify_unified.py): E016、E017、E018、E019、E020、E021 は stash@{0} の未コミット状態に依存。E016 から E019 と E021 は PARTIAL に降格済み、E020 は PENDING。解消は、stash の内容を HEAD に載せるか、HG の判断で別の扱いにする。
- B2 FILE_LOCATION_INDEX.csv への新規登録が未実施。採番規則と生成元が未確認。
- B3 Q-37 (変更記録の補完が GL8 で拒否された件) は未解決。
- B4 変更記録 (CHANGE_START/DONE) の未記録の例外。VERIFICATION_LOG の 2026-10-17 の節に記録済み。バックデートはしない。
- B5 A046 の原因 (reflog の確認、承認記録) は未確認。
- B6 MOCKA_WORKFLOW_PROTOCOL.md は git add 済み (ステージのみ)。commit は別途の承認が必要。
- B7 docs/governance の CRLF と .gitattributes の関係は未確認。

## 2026-10-17 MOCKA_WORKFLOW_PROTOCOL.md の commit (HG 承認 GO)

- commit: ae354c235 (feat/orbit-map-synapse)。メッセージ: docs(governance): add MOCKA_WORKFLOW_PROTOCOL.md under version control。対象は 1 ファイルのみ (62 行追加)。
- push: 行っていない (ローカルのみ)。
- B6 は解消。B7 (CRLF 警告) は、HG の判断により処理済みとして扱う。
- 作業ツリーの未追跡ファイル (他の 513 行) は変更していない。

## 24. B5 の結果 (2026-10-17、読取専用)

- B5-1 (確定): A046 の欠落は、削除や改名ではない。作業ツリーの未コミット変更 (phase5c 上) が stash@{0} に退避され、その後のブランチ切替で HEAD から見えなくなった。根拠は reflog (16:52:36 stash、16:52:38 reset、16:52:43 checkout)。
- B5-2 (未確認): stash の作成理由。reflog と events に記録がない。
- B5-3 (未確認): OPTION A の承認行為。events と decision_ledger に該当する記録がない。承認は文書の記述のみ。
- B5-4 (未確認): events に、2026-10-09 から 10-11 と 10-16 の記録がない。欠落の原因は未確認。
- 次の判断: B1 (統合データの 13 件) の扱いに、B5-1 の事実を使える。stash の内容は、HG の判断まで変更しない。

## 25. B5 残り 2 点の結果 (2026-10-17、事実のみ)

- B5-2 (解消せず、理由は特定不能): stash@{0} の作成理由は、reflog、ログ、ファイル mtime のいずれからも特定できない。作成時刻 (JST 16:52:36) に前後して、governance/mocka_git_safe_commit_ledger_fallback.log、tools/auto_record.log、data/decisions/decision_ledger.jsonl などの mtime が変わっている。
- B5-4 (欠落の範囲を特定、原因は未確認): events と event_signatures は 10-07 から 10-15 に 0 件。human_gate_events と event_bus には同じ区間に行がある。
- B8 (新規): data/decisions/decision_ledger.jsonl は、HEAD と main で 0 バイト。コミット f07679527 (10-01) 以降、このファイルは HEAD の系譜で空。phase5c の版は 110 行。Decision の記録は events テーブルに 343 件 ([DECISION_MADE]) ある。ledger の正本の所在は未確認。
- 次の判断: B8 は、HG の判断が要る。Decision の正本をどこに置くかは、B1 と同じく HG の判断。

## 26. B8 の結果 (2026-10-17、事実のみ)

- B8-1 (確定): decision_ledger.jsonl の 0 バイトは、コミット f07679527 (2026-10-01) で空のファイルとして作られたことによる。既存の内容を空にしたのではない。
- B8-2 (確定): 内容のある版は phase5c の系譜のみ。d1bcb834e (68688 バイト) と 44a84ff9f (101083 バイト)。HEAD と main には無い。
- B8-3 (未確認): 空のファイルを作った理由。コミットメッセージに記載がない。
- B8-4 (事実): Decision の記録は events テーブルに 343 件 ([DECISION_MADE])。ledger の内容と events の関係は未確認。
- 判断待ち: Decision の正本を、どの系譜の内容にするか。HG の判断。

## 状態の更新 (事実、2026-10-17)

- B1 (統合データ 13 件 FAILED): 既知の不整合。stash@{0} の未コミット版への依存 (PARTIAL 降格済み)。解決ではない。
- B2 (FILE_LOCATION_INDEX.csv への未登録): 未解決。採番規則と生成元が未確認。
- B3 (Q-37、変更記録の補完の拒否): 未解決。
- B4 (変更記録の未記録の例外): 二次台帳に記録済み。バックデートはしない。
- B5 (A046 の原因): 欠落の原因は確定 (未コミット変更の退避と、その後のブランチ切替)。退避の動機は未確認。承認行為の証拠は未確認。
- B6 (MOCKA_WORKFLOW_PROTOCOL.md の未追跡): 解決 (ae354c235 でコミット済み)。
- B8 (decision_ledger.jsonl の 0 バイト): 部分的に解決 (d14962dab で phase5c の版を復元し、UTF-8 に変換してコミット済み)。重複 DC_20261006_001、試験由来の記録、承認者名の文字化けは未解決 (HG 裁定により維持)。

## 2026-10-18: HG 条件付き GO の未解決事項（事実、推測なし）

HG の判断: 条件付き GO。完了の表記は「一次完了」とする（CLOSED_LOOP_VERIFIED の段階は主張しない [非主張]）。以下は未解決のまま残す。

- U-1 (MANUAL 33 件): verify_unified.py の証拠項目のうち、シンボルが記録されていないもの（E063, E064, E067, E071, E072, E077, E085, E087, E090, E092, E093, E112, E135 など）。推測で埋めていない。未確認のまま。
- U-2 (NOT_VERIFIED): ASSET_INDEX の A061〜A074 は、connection / usage / enforcement / verification が NOT_VERIFIED。静的参照も実行の確認もしていない。
- U-3 (台帳の食い違いの原因): 追補の注記（統合しない）と、台帳に A061〜A074 が入っていた経路が未確認。
- U-4 (BOM): structural/governance_pipeline.py に BOM があり、mocka_check_utf8 が ok false を返す。HEAD にも同じ BOM があるため既存の状態。除去は未実施。
- U-5 (stash@{0} と追跡 8 件): stash@{0}（7f9e9446）と作業ツリーの追跡 8 件の差分は、stash 作成後の書込みで説明できる内容。個別の正しさは未検証。stash@{0} は保持（削除しない）。
- U-6 (stash@{1}〜@{7}): 未確認。今回の範囲外。保持。
- U-7 (commit の扱い): 承認範囲の 2 ファイル（structural/governance_pipeline.py、mocka_mcp_server.py）は未 commit。台帳と文書（mapping/ 配下）は未追跡のため、commit に含めていない。commit は別途の承認が必要。
- U-8 (Git 状態): 作業ツリーの差分（追跡 13 件、未追跡 500 件）のうち、今回の作業以外のものは今回触っていない。出どころは未確認。
- U-9 (Memory 保存): 未実施。承認が必要。
