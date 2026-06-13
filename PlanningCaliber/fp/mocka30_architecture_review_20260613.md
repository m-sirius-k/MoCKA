# MoCKA 3.0 Architecture Review

- 発行: きむら博士 / 作成: くろこ(Claude Code)
- 作成日: 2026-06-13
- 目的: TODO_301(Event Taxonomy v1)〜TODO_311の次フェーズ設計基盤整備のための実態整理
- 方針: 事実ベースのみ。未確認/未存在のファイルは「未確認」と明記。追加設計・コード生成は行わない。

---

## 1. Architecture Overview

MoCKA 3.0は現在、**2つの並走するレイヤー体系**を持つ。

### (A) Caliber/運用レイヤー（きむら博士のタスク表が指す体系）

`interface/` 配下の各エンジン(Essence/Decision/Memory/Self-Audit/Feedback相当)と、
`caliber/chat_pipeline/mocka_caliber_server.py`(port:5679)、
`mocka_mcp_server.py`(port:5002)、`app.py`(COMMAND CENTER, port:5000)、
`structural/bee.py` / `beta_engine.py`(Structural Intelligence)、
`runtime/`(mocka_Movement / shadow_Movement)から構成される、
**MoCKA運用の実体(events.db中心)**。Phase4の商用展開・制度運用はこちら。

### (B) Governance Layer v1.1 パイプライン（直近フェーズで新規実装された体系）

`semantic/` → `decision/` → `memory/` → `self_audit/` → `feedback/` →
`learning_kernel/` という**新規6層パイプライン**(本セッション含む直近複数フェーズで実装)。
`structural/governance_pipeline.py` / `governance_regression.py` 等のGL1-7
Governance Layerと統合され、`structural/GOVERNANCE_REGRESSION_SUMMARY.md`に
"Overall PASS"が記録されている(最新: 2026-06-13 03:57:49 UTC, commit
`e35724b97b7abcdc68ce5df5574537581faf0dfb`, Event `E20260613_067`)。

> **重要な観察**: きむら博士のタスク表(Layer分析表)では「Self-Learning Kernel」を
> `morphology_engine.py` / `pattern_library.json` / `bee.py` / `beta_engine.py`
> に割り当てているが、これは(A)体系の「Structural Intelligence」モジュール群であり、
> (B)体系の `learning_kernel/`(本セッションでPhase 4-1として実装完了、
> commit `3827abc01`)とは**別物**である。両者は名称が同じ「Self-Learning」だが
> 実体は異なる。詳細は7章参照。

### 全体構成（現存確認済みコンポーネント）

| コンポーネント | パス | ポート | 状態 |
|---|---|---|---|
| COMMAND CENTER | `app.py` | 5000 | 存在確認・101ルート |
| Caliber Pipeline | `caliber/chat_pipeline/mocka_caliber_server.py` | 5679 | 存在確認(v5, APIゼロ) |
| MCP Caliber Server | `mocka_mcp_server.py` | 5002 | 存在確認(v1.5.0) |
| Runtime B (Go) | `runtime_b/mocka_runtime_b.exe` | 5003 | 存在確認 |
| Governance Layer v1.1 | `structural/governance_*.py` + 6層パイプライン | - | Overall PASS確認済み |

---

## 2. Layer-by-Layer Breakdown

きむら博士指定の7レイヤー表に基づき、(A)/(B)両体系の実体を対比する。

### Semantic（意味抽出）

| 項目 | 内容 |
|---|---|
| (A)実体 | `interface/Essence_Direct_Parser.py`(4原則抽出: 全文記録/ワード起因抽出/否定検知/インシデント経緯分析), `interface/essence_pipeline.py`(4軸選別: TODO_029), `interface/language_detector.py`(v2, 5軸+危険検知, ハインリッヒの法則1:29:300) |
| (B)実体 | `semantic/`(Phase 2-1で実装。本レポートでは詳細未調査) |
| 読取/状態変更 | (A)は`lever_essence.json`を**更新**(状態変更可能)。`language_detector.py`はスキャン/レポートで読み取り中心だが`analyze`で自己学習する |
| Governance発火点 | (A)は直接発火なし。danger検知時に`prevention_queue.json`へ投入(Human Gate入口) |
| Human Gate必須操作 | `incident_learner.py`によるdanger_patterns登録(候補提示→きむら博士承認、ただし`data/danger_patterns.json`は未確認、`interface/danger_patterns.json`は存在) |

### Decision（意思決定）

| 項目 | 内容 |
|---|---|
| (A)実体 | きむら博士表記の`auto_gate.py`は**未確認(存在しない)**。`/decision/log/detail`等は`app.py`内に直接実装。Human Gate判定は`app.py`の`prevention_queue()`、`policy_generator.py`、`risk_scorer.py`に分散 |
| (B)実体 | `decision/`(Phase 2-2) |
| 読取/状態変更 | `prevention_queue.json`(1709件、内`NEW`=1705件・`approved`=4件)への書き込みは状態変更操作 |
| Governance発火点 | `app.py`の`/decision/log/detail`、`mataka`の3回以上検知でprevention_queue自動昇格 |
| Human Gate必須操作 | `prevention_queue`内のNEW項目の承認/却下(承認済みはわずか4件、未承認1705件が滞留) |

### Memory（履歴・再利用・文脈保持）

| 項目 | 内容 |
|---|---|
| (A)実体 | `data/mocka_events.db`(SQLite単一化済み, テーブル: `events`=11,719件, `error_rows`=958件, `claude_sessions`=89,558件, `essence`, `guidelines_reviewed`, `guidelines_review_progress`, `user_voice`, `judgement_reason`, `gateway_nonces`), `data/lever_essence.json`(INCIDENT/OPERATION/PHILOSOPHY/IMMUTABLE軸), `data/ping_latest.json`(H/G/C/P/A + ESSENCE_SUMMARY), `data/recurrence_registry.csv`(67行=66件+header) |
| (B)実体 | `memory/`(Phase 2-3) |
| 読取/状態変更 | `mocka_events.db`はappend-only(events/error_rows/claude_sessions追記)。`ping_latest.json`/`lever_essence.json`は定期書き換え(essence_auto_updater) |
| Governance発火点 | append-onlyが原則。`anchor_update.py`がコミット後にanchor_record再封印 |
| Human Gate必須操作 | なし(読み取り・蓄積中心) |

### Self-Audit（評価・監査）

| 項目 | 内容 |
|---|---|
| (A)実体 | `interface/cross_audit.py`(複数AI相互検証, TRDP原則, APIゼロ・port5002活用), `scripts/ledger/ledger_verify.py`(`schema.schema.verify_ledger()`呼び出し), TIC Layer0/1: `interface/health_check.py`(7項目モーニングチェック), `interface/tech_watcher.py`(v3.0 意味差分検知) |
| (B)実体 | `self_audit/`(Phase 3-1) |
| 読取/状態変更 | `health_check.py`はFAIL時に`prevention_queue.json`へ投入(状態変更)。`ledger_verify.py`は読み取りのみ(LEDGER OK/ERROR出力) |
| Governance発火点 | `ledger_verify.py`→`schema.verify_ledger()` |
| Human Gate必須操作 | health_check FAIL項目(現在`relay_dom_selector`がFAIL継続中、6章A参照) |

### Feedback（改善提案生成）

| 項目 | 内容 |
|---|---|
| (A)実体 | `interface/incident_learner.py`(候補提示→承認→`danger_patterns.json`追加の自己進化ループ)、`app.py`の`/prevention/*`系・prevention_queue自動投入箇所(claim/mataka/health_check等) |
| (B)実体 | `feedback/`(Phase 3-2, commit `64de07c3b`) |
| 読取/状態変更 | `incident_learner.py`は候補提示まで(承認なしでは`danger_patterns.json`を変更しない=非破壊) |
| Governance発火点 | きむら博士承認(`approve`コマンド)がGate |
| Human Gate必須操作 | danger_patterns登録の全件 |

### Self-Learning Kernel（重み更新・状態変化）

| 項目 | 内容 |
|---|---|
| きむら博士表記(A)実体 | `interface/morphology_engine.py`(形態素解析+N-gram, AYX+TS。**ファイル内コメントがcp932文字化けで判読不能** — 7章Risk参照), `data/pattern_library.json`(INCIDENT=4件/SUCCESS=2件/RECURRENCE=22件), `structural/bee.py`(β Ecology Engine v2.0, confirmed_betas=4), `structural/beta_engine.py`(β抽出エンジン, TODO_211) |
| (B)実体(直近実装の本物のLearning Kernel) | `learning_kernel/`(Phase 4-1, commit `3827abc01`, 本日完了)。`learning_registry.py`/`learning_state.py`/`weight_state_store.py`/`learning_model.py`/`update_validator.py`/`learning_engine.py`/`learning_queue.py`/`learning_applier.py`/`learning_pipeline.py`の9ファイル+3テスト(計44/44 PASS) |
| 読取/状態変更 | (A)の`bee.py`/`beta_engine.py`は`structural/pattern_db.json`等への書き込みあり(状態変更)。(B)は`learning_kernel/data/learning_state.json`(shadow weight-state)のみを変更、Decision/Memory/Semantic実コードは無変更 |
| Governance発火点 | (B)は`structural/GOVERNANCE_REGRESSION_SUMMARY.md`の"Overall PASS"確認が`UpdateValidator`の`governance_compliance`チェックに直結 |
| Human Gate必須操作 | (B)は`LearningQueue.approve()`(pending→approved)が必須Gate。governance_status!="PASS"の場合は`LearningApplier`が適用を拒否 |

### Governance（最終制御・Fail Closed）

| 項目 | 内容 |
|---|---|
| (A)実体 | `runtime/main/ledger.json`(ハッシュチェーン台帳), `scripts/ledger/anchor_update.py`, `interface/health_check.py`(prevention_queue投入), `mocka_mcp_server.py`(GL1-7 Governance Pipeline import: `structural/`をsys.path追加) |
| (B)実体 | `structural/governance_pipeline.py`, `governance_regression.py`(Integration→Dogfood→Audit→Summary), `governance_audit_check.py`, `gl_integration_test.py`, `execution_governance.py`, `reasoning_governance.py`, `repository_policy.py` 等 |
| 最新封印 | OVERVIEW記載: `c2d8c54e`(2026-06-01, ALL CHECKS PASSED) / Governance Regression直近: `e35724b97b7abcdc68ce5df5574537581faf0dfb`(2026-06-13, Overall PASS) — **2つの封印系列が並走**(7章参照) |
| Fail Closed設計 | `learning_kernel`の`UpdateValidator`/`LearningApplier`はgovernance_status≠"PASS"時に明示的に拒否(ValueError/rejected) |

---

## 3. Data Flow Diagram (ASCII)

きむら博士提示のフローを実ファイルで裏付けたもの(確認できた経路のみ実線、未確認/部分実装は注記):

```
[入力] chrome拡張(PHI-OS) / MCP呼び出し(mocka_mcp_server.py:5002) / 右クリックボタン
  |
  v
[Semantic] Essence_Direct_Parser.py --4原則抽出--> 5W1H相当データ
  |
  v
[Memory] append_event() (app.py) --> data/mocka_events.db (events テーブル, 11,719件)
  |
  v
[Caliber Pipeline:5679] mocka_caliber_server.py v5
   auto_raw_loop: RAW -> REDUCED -> RE_REDUCED -> REDUCING
   (REDUCINGは essence_auto_updater.py v3 が1分間隔でRE_REDUCEDへ自動移動)
  |
  v
[Semantic 2] essence_auto_updater.py v3 (5分間隔) --> data/lever_essence.json 更新
                                                  --> data/ping_latest.json 更新
  |
  v
[Feedback] language_detector.py (5軸+危険検知)
   DANGER/CRITICAL検知 --> prevention_queue.json へ投入 (NEW)
  |
  v
[Decision] きむら博士確認(auto_gate.pyは未確認・実体はapp.py分散ロジック)
   NORMAL --> 自動承認相当 / HIGH以上 --> Human Gate(prevention_queue承認待ち)
   現状: NEW=1705件 / approved=4件 (承認率 約0.23%)
  |
  v
[Action] DECISION_APPROVED --> lever_essence.json更新 + ping_generator実行
  |
  v
[Governance] 
   (A)系: scripts/ledger/anchor_update.py (mocka-seal, 最新 c2d8c54e 2026-06-01)
   (B)系: structural/governance_regression.py (Integration->Dogfood->Audit->Summary,
          最新 Overall PASS 2026-06-13, commit e35724b97b)
```

### 学習ループ(きむら博士提示分の検証)

```
incident_learner.py
   --scan--> events.db中のCRITICAL/DANGERイベントを5軸分解
   --候補提示--> きむら博士承認
   --承認後--> data/danger_patterns.json へ追記(★data/danger_patterns.json自体は未確認。
                interface/danger_patterns.json は存在するため配置パスに齟齬の可能性)

morphology_engine.py
   --> data/morphology_patterns.db (★structural/morphology.db は未確認。
        実際の形態素DBは data/morphology_patterns.db に存在。
        structural/morphology.py というモジュールは別途存在)
   --> PHL-OS スコアへの影響経路は本レポートでは未追跡(caliber server内PHL-OS v2が対象)

bee.py
   --> β候補検出(confirmed_betas=4) --> structural/pattern_db.json等へ反映
   --> Structural Intelligence (/api/beta/status, /api/beta/evidence, /api/beta/meta)
```

---

## 4. Module Inventory (file-level)

### app.py (COMMAND CENTER, port:5000)

- 101個の`@app.route`を確認。主要グループ:
  - Decision系: `/decision/log/detail`, `/risk/todos`, `/risk/recommendation`
  - Prevention/Gate系: `/claim`, `/collect`, `/success`, `prevention_queue()`関数(PREVENTION_QUEUE_PATH管理)
  - Caliber連携: `/caliber/status`, `/caliber/process`, `/caliber/scan`, `/caliber/queue`
  - TIC系: `/tic/health`, `/tic/risk`, `/tic/queue`, `/tic/watcher-status`
  - ISE系: `/api/ise/knock`, `/api/ise/ack`, `/api/ise/state`, `/api/ise/state_machine`, `/api/ise/ledger`, `/api/ise/taxonomy`
  - β系: `/api/beta/status`, `/api/beta/evidence`, `/api/beta/meta`, `/api/beta-extract`(実装済み, TODO_215は完了扱い)
  - SCAMPER系: `/scamper/run`, `/scamper/recent`, `/scamper/status`
  - PHI-OS連携: `/api/phi-os-event`, `/api/phi-os-status`
  - クロス監査: `/cross_audit/task`, `/cross_audit/submit`, `/cross_audit/check/<task_id>`, `/cross_audit/report/<task_id>`, `/cross_audit/list`
  - 検証: `/api/verification/verify`

### interface/

| ファイル | 責務 | 状態 |
|---|---|---|
| `router.py` | events.csv形式定義、E{YYYYMMDD}_{NNN}採番。**ファイル先頭にcp932文字化けコメント混入**(2行目) | 存在・DEPENDENCY_BREAK修正済み(commit `6561fc5`記載) |
| `Essence_Direct_Parser.py` | 4原則抽出、lever_essence.json更新 | 存在(v1.0) |
| `essence_pipeline.py` | Essence_Direct_Parser→essence_classifier統合(TODO_029) | 存在(v1.0) |
| `essence_auto_updater.py` | 5分間隔自動更新、events.db直読み、REDUCING監視、Caliber死活監視 | 存在(v4) |
| `language_detector.py` | 5軸危険検知、analyze/scan/report | 存在(v2) |
| `incident_learner.py` | danger_patterns候補提示→承認学習ループ | 存在 |
| `morphology_engine.py` | 形態素解析+N-gram | 存在(v1.0)。**ファイル内docstringが文字化けで判読不能** |
| `auto_gate.py` | 条件付き自動承認(きむら博士表記) | **未確認(ファイル不存在)** |
| `health_check.py` | TIC Layer0、7項目モーニングチェック | 存在 |
| `tech_watcher.py` | TIC Layer1、意味差分検知(v3.0) | 存在・TODO_208は完了済み(7章参照) |
| `simulation_layer.py` | 疑似試験環境(sim_events.csv生成) | 存在 |
| `cross_audit.py` | クロス監査(TRDP原則) | 存在(v1.0) |
| `danger_patterns.json` | 危険語彙(きむら博士表記は`data/danger_patterns.json`) | `interface/danger_patterns.json`として存在、`data/`配下には**未確認** |

### caliber/chat_pipeline/mocka_caliber_server.py

- v5、APIゼロ化版(`anthropic` import削除)。`extract_local()`/`calc_rate_local()`でローカル処理。
- PHL-OS v2(`phl_build_state`/`phl_select_modules`/`phl_run_guard`/`phl_score`/`phl_build_trace`/`phl_record_event`)はファイル内に統合されている前提(本レポートでは関数単位の存在確認は未実施)。
- `auto_raw_loop`によるRAW→REDUCED→RE_REDUCED→REDUCING振り分け。port:5679。

### mocka_mcp_server.py

- v1.5.0。GL1-7 Governance Pipeline(`structural/`)をsys.path追加してimport。
- 提供ツール: `mocka_get_todo`/`mocka_get_overview`/`mocka_get_essence`/`mocka_get_guidelines`/`mocka_write_event`/`mocka_add_todo`/`mocka_update_todo`/`mocka_check_utf8`/`mocka_search`/`mocka_seal`/`mocka_get_incidents`/`mocka_list_events`/`mocka_read_event`/`mocka_get_command_center`(本セッションで使用したツール名と一致)。

### runtime/

| ファイル | 責務 |
|---|---|
| `main_loop.py` | mocka_Movement実装。`intent_logger`/`intent_to_goal`/`goal_to_plan`/`action_executor`/`result_to_state`/`state_to_graph`/`result_evaluator`/`eval_to_history`/`eval_selector`をimport(これらの個別ファイル存在は本レポートで未検証) |
| `civilization_bridge.py` | main_loopとcivilization_*エンジン群の接続ブリッジ |
| `main/ledger.json` | ハッシュチェーン台帳。存在確認のみ(内容未検証) |

### runtime_b/mocka_runtime_b.exe

- Go 1.22.3 Runtime、port:5003、SQLite read-only。実行ファイルとして存在確認のみ(ソース未確認)。

### structural/ (Governance Layer v1.1 + Structural Intelligence)

```
structural/
    __init__.py
    bee.py                       — β Ecology Engine v2.0(TODO_216)
    beta_engine.py                — β抽出エンジン(TODO_211)
    consensus.py
    dogfood_run.py                — governance_regression.pyのDogfoodステージ
    encoding_policy_validator.py
    event_file_resolver.py
    execution_governance.py
    gl_integration_test.py        — GL1-7統合テスト
    governance_audit_check.py     — governance_regression.pyのAuditステージ
    governance_pipeline.py
    governance_regression.py      — Overall PASS判定の本体
    grounding_engine.py
    knowledge_mass.py
    mocka_3_run.py
    morphology.py                 — きむら博士表記の"structural/morphology.db"とは別物(.py)
    phi_dna_migrate.py
    reasoning_governance.py
    repository_indexer.py
    repository_policy.py
    state_reconstructor.py
    thinking_mode.py
    working_memory.py
    GOVERNANCE_REGRESSION_SUMMARY.md  — 最新 Overall PASS(2026-06-13)
```

- `structural/morphology.db` は**未確認**。代わりに `data/morphology_patterns.db`(DBファイル)と
  `structural/morphology.py`(モジュール)が存在する。

### Governance Layer v1.1 6層パイプライン(本セッション含む直近実装)

```
semantic/        — Phase 2-1
decision/         — Phase 2-2
memory/            — Phase 2-3
self_audit/         — Phase 3-1 (commit 8e604b60c)
feedback/            — Phase 3-2 (commit 64de07c3b)
learning_kernel/      — Phase 4-1 (commit 3827abc01, 本日完了)
    learning_registry.py
    learning_state.py
    weight_state_store.py
    learning_model.py
    update_validator.py
    learning_engine.py
    learning_queue.py
    learning_applier.py
    learning_pipeline.py
    learning_integration_test.py / learning_safety_test.py / learning_queue_test.py
LEARNING_KERNEL.md / SELF_AUDIT_LAYER.md / FEEDBACK_LOOP.md
```

### data/

| ファイル/DB | 内容 |
|---|---|
| `mocka_events.db` | SQLite。テーブル: `events`(11,719), `error_rows`(958), `sqlite_sequence`, `claude_sessions`(89,558), `essence`, `guidelines_reviewed`, `guidelines_review_progress`, `user_voice`, `judgement_reason`, `gateway_nonces` |
| `lever_essence.json` | キー: IMMUTABLE/INCIDENT/OPERATION/PHILOSOPHY/updated_at/source |
| `ping_latest.json` | キー: H/G/C/P/A/ESSENCE_SUMMARY/essence_updated/ngrok_online/NGROK/current_phase |
| `prevention_queue.json` | `queue`配列、1,709件(NEW=1,705/approved=4) |
| `pattern_library.json` | INCIDENT=4件、SUCCESS=2件、RECURRENCE=22件 |
| `success_patterns.json` | キー: hint/great/success_great |
| `recurrence_registry.csv` | 66件(67行=header+66)。OVERVIEWの「87件」とは**件数不一致**(7章参照) |
| `trajectory.csv` | 325行(326行=header+325)。OVERVIEW記載「325件処理済み」と整合 |
| `MOCKA_OVERVIEW.json` | v3.0、472行 |
| `MOCKA_TODO.json` | 4,119行(JSON整形後) |
| `morphology_patterns.db` | 形態素パターンDB(きむら博士表記の`structural/morphology.db`の実体と推定) |
| `danger_patterns.json` | **`data/`配下には未確認**(`interface/danger_patterns.json`のみ存在) |
| `tic/` | TIC専用データ(個別ファイルは本レポート未列挙) |

### scripts/ledger/

- `ledger_verify.py` — `schema.schema.verify_ledger()`を呼び出し、`LEDGER OK`/`LEDGER ERROR`を出力
- `anchor_update.py` — `governance/anchor_record.json`, `mocka-governance-kernel/anchors/anchor_record.json`を再封印

### tools/mocka_orchestra_v10.py

- Playwright (`playwright.async_api`)ベース。引数: `PROMPT`, `MODE`(デフォルト"orchestra")。`chat_urls.json`読み込み。

### PlanningCaliber/workshop/

| パス | 内容 |
|---|---|
| `phi-os/` | PHI-OS v1.0。`phios/core/execution_gate.py`, `phios/ledger_gate.py`, `ise/`(Knock/Ack/State実装、`tests/test_execution_gate.py`存在)。core/adapters/restore/commit/optionsはディレクトリ存在確認のみ |
| `cyber_benchmark/` | きむら博士表記の`eval_cases_v2.jsonl`/`scorer.py`/`mocka_cyber_eval.py`(直下)は**パス不一致**。実際は`cases/eval_cases.jsonl`(v2無し), `cases/ground_truth.json`, `src/mocka_cyber_eval.py`, `src/benchmark_runner.py`, `src/phl_harness.py`, `results/result_A.json` |
| `needle_eye_project/experiments/lever_verification_claude.json` | **未確認(パス自体が不存在)**。`needle_eye_project`ディレクトリがPlanningCaliber/workshop配下に存在しない |

---

## 5. Completed vs Incomplete Mapping

| 項目 | 状態 | 根拠 |
|---|---|---|
| Governance Layer v1.1 (semantic→decision→memory→self_audit→feedback→learning_kernel) | **完了** | governance_regression.py Overall PASS(2026-06-13)、各層テスト全PASS、各層.md完成 |
| Self-Learning Kernel (Phase 4-1) | **完了** | 本セッションでcommit `3827abc01`、44/44 PASS |
| TIC Layer0 (health_check.py) | **稼働中・一部FAIL** | `relay_dom_selector`が継続FAIL(current_issues記載、6章A) |
| TIC Layer1 (tech_watcher.py v3.0) | **完了**(TODO_208/TODO_204とも"完了") | OVERVIEWのnext_actions記載は**古い情報**(7章参照) |
| TIC Layer2-4 (Sandbox/impact_analyzer/COMMAND CENTER TICパネル) | **未着手** | TODO_205〜207(OVERVIEW記載のまま、本レポートでは個別未検証) |
| Structural Intelligence (bee.py/beta_engine.py) | **稼働中** | bee v2.0 confirmed_betas=4、`/api/beta/*`実装済み |
| β Engine API公開(TODO_215) | **完了** | `/api/beta-extract`が`app.py`に実装確認済み(OVERVIEW "api_pending"記載は古い) |
| PHI OS v1.0実機テスト(TODO_195) | **完了**(2026-06-07) | MOCKA_TODO.json completed記載。OVERVIEW next_actionsは古い |
| Relay収益化(TODO_178) | **保留** | Stripe Webhook設定等が博士側タスクで未着手 |
| Cloudflare Tunnel恒久化(TODO_266) | **保留・優先度低下** | AI Connector Framework(TODO_268)優先に変更(2026-06-10) |
| Context Package API(TODO_279) | **未着手** | MOCKA_TODO.json active記載 |
| Knowledge Diff API(TODO_284) | **未着手** | 同上 |
| Event Taxonomy v1〜知識ライフサイクル自動化(TODO_301〜311) | **全て未着手** | MOCKA_TODO.json active記載、created_at 2026-06-12 |
| auto_gate.py | **不存在** | きむら博士のファイルマップに記載されているが`interface/`配下に存在しない。Decision/Gate機能は`app.py`へ直接実装されている可能性が高い |
| needle_eye_project | **不存在** | `PlanningCaliber/workshop/`配下に該当ディレクトリ無し |

---

## 6. TODO List (prioritized by category)

### A. Must Fix（構造崩壊リスク）

| TODO | 内容 | 現状 |
|---|---|---|
| (記載なしIssue) `relay_dom_selector` FAIL | health_check.py継続FAIL中(current_issues "ACTIVE") | TODO番号未割当。current_issues直書き |
| TODO_208 | tech_watcher形骸化防止(意味差分検知) | **既に"完了"**(2026-06-01)。OVERVIEW next_actionsの記載が古いだけ。再着手不要 |
| TODO_266 | Cloudflare Tunnel恒久化 | 保留中・優先度を意図的に下げた状態(TODO_268優先) |
| (新規発見) prevention_queue滞留 | NEW=1705件 / approved=4件 (承認率0.23%) | TODO番号未割当。Human Gateの実運用上のボトルネックとして7章に記載 |

### B. Should Improve（設計改善）

| TODO | 優先度 | 内容 |
|---|---|---|
| TODO_301 | 最高 | Event Taxonomy v1策定(未着手) — 本レポートが入力情報の一部となる |
| TODO_302 | 最高 | データライフサイクルv1策定(未着手) |
| TODO_303 | 高 | State Machine v1策定(未着手) |
| TODO_305 | 高 | Decision Ledger正式スキーマv1実装(未着手) |
| TODO_279 | 高 | Context Package API実装(未着手) |
| TODO_304 | 中 | Version Policy v1策定(未着手) |
| TODO_306 | 中 | モジュール成熟モデルv1実装(未着手) |
| TODO_284 | 中 | Knowledge Diff API(未着手) |
| TODO_296 | 中 | health_check.py .envのBOM検知追加(未着手) |
| TODO_297 | 中 | tech_watcher URL死活監視(未着手) |

### C. Future Expansion（次フェーズ）

| TODO | 優先度 | 内容 |
|---|---|---|
| TODO_307 | 中 | Prompt Compiler v1実装(未着手) |
| TODO_308 | 中 | SCAMPER Engine PHI-OS統合(未着手) |
| TODO_309 | 中 | Fluid Coordinate Theory ISE接続設計(未着手) |
| TODO_310 | 低 | Knowledge Evolution Engine設計・実装(MoCKA 4.0、未着手) |
| TODO_311 | 低 | 知識ライフサイクル自動化エンジン(MoCKA 4.0、未着手) |
| TODO_178 | 高(保留) | Relay収益化(Stripe+CWS+LP) |

---

## 7. Risk / Design Notes

1. **「Self-Learning Kernel」の名称重複**
   きむら博士のレイヤー表は`morphology_engine.py`/`pattern_library.json`/
   `bee.py`/`beta_engine.py`を「Self-Learning Kernel」としているが、これらは
   (A)体系のStructural Intelligence/形態素解析モジュールであり、実際に
   「FeedbackProposal→重み更新→Governance確認→Queue→Apply→Rollback」の
   三段階適用構造を持つのは本日完成した`learning_kernel/`(commit `3827abc01`)
   である。TODO_301(Event Taxonomy)策定時、両者を区別して命名する必要がある。

2. **2つの封印(Seal)系列の並走**
   OVERVIEWの`governance.latest_seal`は`c2d8c54e`(2026-06-01)だが、
   `structural/GOVERNANCE_REGRESSION_SUMMARY.md`は別系列のcommitハッシュ
   `e35724b97b7abcdc68ce5df5574537581faf0dfb`(2026-06-13)を"Overall PASS"
   として記録している。TODO_302(データライフサイクル)・TODO_305(Decision
   Ledger)策定時、この2系列の封印をどう統合するか(あるいは並走を許容するか)
   の設計判断が必要。

3. **OVERVIEW.json(v3.0, 2026-06-01更新)のnext_actions陳腐化**
   `next_actions.immediate`に記載のTODO_195/TODO_208は、MOCKA_TODO.jsonでは
   いずれも"完了"(それぞれ2026-06-07/2026-06-01)済み。`next_actions`は
   2026-06-01以降更新されていない可能性が高い。TODO_301(Event Taxonomy)/
   TODO_279(Context Package API)実装時、OVERVIEW.jsonの`next_actions`を
   自動再生成する仕組み(stale検知)を検討候補とすべき。

4. **prevention_queue.jsonの未承認滞留(1705件)**
   `data/prevention_queue.json`は1,709件中1,705件が`NEW`のまま
   (`approved`は4件のみ)。Human Gateが設計上の意図通り機能しているか
   (=博士が承認作業を行うフロー自体が運用されているか)について、
   TODO_303(State Machine v1)・TODO_306(モジュール成熟モデル)策定時に
   検証が必要。単純に「未処理が溜まっている」のか、「NEW=未評価で
   実害なし」の設計なのかは本レポートのファイル調査だけでは判別できない。

5. **`recurrence_registry.csv`の件数不一致**
   OVERVIEWは「recurrence_data.total: 87」「誤検知77件修正済み」と記載するが、
   現在の`data/recurrence_registry.csv`は66件(67行-header)。87→66への
   減少が「誤検知除去の結果」か「データ欠落」かは本レポートでは判別不可。
   TODO_301(Event Taxonomy)で再発(RECURRENCE)カテゴリの正本データソースを
   `recurrence_registry.csv`と`pattern_library.json`(RECURRENCE=22件)の
   どちらにするか、または統合するかの設計判断が必要。

6. **エンコーディング汚染ファイルの残存**
   `interface/router.py`の2行目、`interface/morphology_engine.py`の
   docstring全体がcp932由来の文字化け(mojibake)で判読不能な状態のまま
   残存している。MoCKAのCLAUDE.mdは新規ファイル生成時のUTF-8検証
   (`mocka_check_utf8`)を義務化しているが、既存ファイルの汚染除去は
   対象外になっている。TODO_296(BOM検知)のスコープを.envだけでなく
   `.py`ファイルのcp932混入検知にも広げる余地がある。

7. **きむら博士ファイルマップとの不一致一覧(再掲)**
   - `interface/auto_gate.py` — 不存在
   - `structural/morphology.db` — 不存在(実体は`data/morphology_patterns.db`)
   - `data/danger_patterns.json` — 不存在(`interface/danger_patterns.json`のみ)
   - `PlanningCaliber/workshop/cyber_benchmark/eval_cases_v2.jsonl`等(直下) — 不存在
     (実体は`cases/eval_cases.jsonl`サブディレクトリ配下、バージョンサフィックスなし)
   - `PlanningCaliber/workshop/needle_eye_project/` — ディレクトリ自体が不存在

8. **Governance Layer v1.1パイプラインのコード変更非破壊性**
   `learning_kernel/`を含む6層パイプラインは、Decision/Memory/Semantic
   Layerの実コード・Registryを一切変更せず、shadow weight-state
   (`learning_kernel/data/learning_state.json`)のみを操作する設計が
   全フェーズで一貫して維持されている(各層`*_SAFETY_TEST`相当でPASS)。
   この設計原則は(A)体系のStructural Intelligence(bee/beta_engine)にも
   適用可能か、TODO_310(Knowledge Evolution Engine)で検討余地がある。

---

## 8. Phase Evaluation（成熟度・ボトルネック・次フェーズ提案）

### 成熟度評価(モジュール単位、TODO_306の8段階を仮適用)

| モジュール | 推定段階 | 根拠 |
|---|---|---|
| Governance Layer v1.1(6層パイプライン) | Verified | 全層テストPASS、Governance Regression Overall PASS、ドキュメント完成 |
| COMMAND CENTER(app.py) | Official/Core | 101ルート、commit履歴あり、複数モジュールのハブとして稼働 |
| TIC Layer0-1 | Official(Layer0は部分FAIL) | health_check/tech_watcher v3.0とも実装完了、Layer0のみ`relay_dom_selector`未解決 |
| TIC Layer2-4 | Idea/未着手 | TODO_205〜207未着手 |
| Structural Intelligence(bee/beta_engine) | Caliber/Verified | v2.0稼働中、API公開済み、confirmed_betas=4 |
| incident_learner / danger_patterns学習ループ | Experimental | 承認制ループは実装済みだが`data/danger_patterns.json`配置の不一致(7章)が未解消 |
| PHI-OS v1.0 | Verified | 実機テスト完了(2026-06-07) |
| Relay(製品) | Prototype | 実装完了だが収益化(Stripe等)未着手 |
| Event Taxonomy / データライフサイクル / State Machine(制度設計) | Idea | TODO_301〜304すべて未着手 |

### ボトルネック

1. **制度設計(TODO_301〜306)が実装(learning_kernel等)に対して後追い**
   - 6層パイプラインやTIC/Structural Intelligenceは既に「Verified」相当まで
     実装が進んでいる一方、それらを統一的に記述するEvent Taxonomy/
     State Machine/Decision Ledgerスキーマがまだ存在しない。
   - 本レポート自体がTODO_301の入力として位置づけられている通り、
     **次フェーズの最大のボトルネックは「実装の追認・体系化」**である。

2. **Human Gateの処理能力(prevention_queue 1705件滞留)**
   - 制度上Human Gateは正しく機能している(NEWに積まれている=自動承認していない)
     が、実運用としてこの量を博士が処理できるかは別問題。
   - TODO_303(State Machine)で「NEW→approved以外の終端状態(例: auto-expire,
     batch-dismiss)」を定義しないと、キューが無限に肥大化する設計リスクがある。

3. **命名・配置の不一致によるドキュメント信頼性低下**
   - 7章で列挙した7件の不一致(auto_gate.py, morphology.db, danger_patterns.json
     のパス, cyber_benchmarkの構成, needle_eye_projectの不存在, Self-Learning
     Kernelの名称重複, OVERVIEW next_actionsの陳腐化)は、いずれも
     「ドキュメント(OVERVIEW/タスク表)が実装の変化に追従していない」ことが
     共通原因。TODO_284(Knowledge Diff API)はこの問題への直接的な対策候補。

### 次フェーズ提案(本レポートからの示唆)

1. TODO_301(Event Taxonomy v1)着手時、本レポート3章のデータフローと
   `mocka_events.db`の実テーブル構成(events/error_rows/claude_sessions/
   essence/guidelines_*/user_voice/judgement_reason/gateway_nonces)を
   taxonomy定義の出発点とする。
2. TODO_302(データライフサイクル v1)着手時、`prevention_queue.json`の
   NEW/approved以外の終端状態の定義を最優先項目とする(ボトルネック2)。
3. TODO_305(Decision Ledgerスキーマ)とGovernance Layer v1.1の
   `learning_kernel/learning_queue.py`の`pending/approved/rejected/applied/
   rolled_back`状態モデルは構造が類似しており、スキーマ設計時に参照可能。
4. 7章で列挙したファイルマップ不一致は、TODO_301〜306の各ドキュメント
   (taxonomy.json/lifecycle.md/state_machine.md等)が完成した時点で
   一括棚卸しし、OVERVIEW.json v3.1として再発行することを推奨。
5. 「Self-Learning Kernel」の名称重複(7章-1)は、TODO_301の
   taxonomy.json内で`learning_kernel/`(Governance Layer配下)と
   `structural_intelligence`(bee/beta_engine/morphology)を明確に
   別カテゴリとして定義することを推奨。

---

*Generated by Claude (執行官) on 2026-06-13*
*Reference: MOCKA_OVERVIEW.json v3.0 / MOCKA_TODO.json (2026-06-12時点の登録内容を含む) / TODO_301〜311*
