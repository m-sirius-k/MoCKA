# MoCKA Audit Instruction v1.0 — Observation Layer v0.1

位置づけ: 文書ID「MoCKA-AUDIT-INSTRUCTION-v1.0」への対応。博士確認(2026-07-04)により、くろこの役割は観測・事実収集のみに限定することが確定した。指示書4.1(構造評価A〜D)・4.2(Critical/Moderate/Low分類)・4.3(制度欠陥分類)・4.4(強化提案: 新規制度追加案・削除提案・責務再分割設計・ループ遮断構造の提案)を含む「4. 評価出力形式」全体は、評価・制度設計そのものでありくろこの担当範囲外とし、R01・博士によるPhase 2以降の領域として本文書には一切含めない。直前のGovernance Catalog Phase B-6 Final Decision待機(実行レイヤー)とは別の観測レイヤーとして、指示書3.1〜3.4の重点監査項目についてのみ、構造的事実をfile:line根拠付きで報告する。

判断・評価・改善提案は一切行っていない。

---

## 3.1 制度ループ構造の検出

### (1) 自己評価が自己承認に接続する構造

- 単独の自己評価=自己承認ループの直接証拠は確認されなかった。ただし、鍵生成と鍵台帳登録が同一スクリプト内で連続実行される構造を確認: `governance/keys/gen_role_keys.py:63-66`、`governance/keys/rotate_root_key_v2.py:48-51`はいずれも鍵生成後、外部検証を経ずに直接`governance/registry.json`へ`reg.append()`/`REG.write_text()`を実行する。
- `governance/sign_governance_event.py`(1-36行)がroot_key_v2の秘密鍵でイベントに署名する一方、`governance/verify_approval_flow.py`はapproval_flow.jsonの構造検証のみを行い署名検証は別経路(`verify_role_policy.py`/`verify_revoke_event.py`)である。

### (2) 監査プロセスが監査対象に依存する構造

- `governance/verify_role_policy.py:9`は`governance/keys/role_policy.json`を読むが、これを書き込む処理は今回の調査では確認されなかった。
- `governance/verify_approval_flow.py:9`は`governance/approval_flow.json`を読むが、これを書き込む処理も今回の調査では確認されなかった。
- registry.jsonの書き込み元は`gen_role_keys.py`/`rotate_root_key_v2.py`のみ確認された。監査対象(registry.json)を監査スクリプト自身が書き換える経路は確認されなかった。

### (3) 無限再帰的な評価ループの可能性

- `data/MOCKA_OVERVIEW.json`(41-42行)が定義する運用ループ「Observation→Record→Incident→Recurrence→Prevention→Decision→Action→Audit」について、`runtime/main_loop.py:30-62`・`runtime/civilization_bridge.py:34-64`にステージ出力が次ステージの入力となる循環構造を確認した: `push_to_civilization()`(main_loop.py:50-51)がアクション実行結果をcivilization側の目標として書き込み、`pull_from_civilization()`(civilization_bridge.py:50-54)が進捗を読み戻し、`update_causal_graph()`(main_loop.py:61)が次周回に反映する。同一データの再入を防ぐ明示的なガードは今回の調査範囲では確認されなかった。

### (4) Human Gateが形式化している箇所

- `phi_os/human_gate.py`(23行、163-172行)にタイムアウトによる自動承認ロジックは確認されなかった(expire()は明示呼び出しが必要)。
- `governance/mocka_git_safe_commit.py:79-84,106-122`の`human_gate_override_event_id`パラメータは、Core System Fileの除外を解除する仕組みだが、渡されたevent_idが実際に存在するか・承認権限者による正当な承認かを検証する処理は確認されなかった(文字列としてコミットメッセージに埋め込まれるのみ)。
- `docs/audits/MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1.md`(39-45行)は、human_gate_eventsテーブルの実イベント1776件中1768件がPENDING状態のまま滞留していることを記録している(同文書45行「PENDINGキューが事実上の死蔵状態」)。同74行は「呼び出し元が博士本人の操作であることを保証する仕組みが無い」と記録している。

---

## 3.2 スキーマ不一致検出

### (1) MCPとConnector間のデータ構造差異

- `mocka_mcp_server_vps.py`のEVENTS_FIELDS(21-27行)は`"when"`フィールドを使用する一方、DB層(77行)は`"when_ts"`カラムに書き込み、読み出し時にフォールバックマッピング(61-62行)で補完している。
- `gateway/connector_caliber.py:55-61`のMoCKAIndex生成には、MCP側23フィールドにあるタイムスタンプ相当のフィールドが含まれていない。
- `gateway/connector_router.py:78-88`のルーティング結果構造(ai/adapter_key/capability/query/context/routing)は、イベントスキーマとは別の構造。

### (2) ツールレジストリと実体呼び出しの不一致

- `core_kernel/core_store/capability_registry.py`(16-48行)・`interface/ai_capability_registry.py`(36-163行)・`PlanningCaliber/workshop/seo-os/caliber/capability_registry.py`(4-42行)の3つのcapability_registryは管理対象・スキーマがそれぞれ異なる。
- `gateway/connector_router.py:64`は`interface/ai_capability_registry`を参照するが、同レジストリにはMCPが公開する9ツール名(`mocka_get_overview`等、`mocka_mcp_server_vps.py:165`)に対応するエントリは無く、`core_kernel/capability_registry`がMCPツール用に参照される経路は今回の調査では確認されなかった。

### (3) Phaseごとのスキーマ変化による互換性崩壊

- `docs/governance/REGISTRY_SCHEMA_v1.0.md`(KN-004、22-114行)は`identity`/`reference`/`classification`/`lifecycle`/`metadata`を持つRecordスキーマを定義するが、実体である`governance/registry.json`(2-37行)はschema=`mocka.keys.ed25519.registry.v3`で、`root_keys`/`operational_keys`/`policy`/`meta`という鍵管理構造であり、KN-004が定義するフィールドは含まれていない。

### (4) 非互換状態のサイレント失敗

- `mocka_mcp_server_vps.py:123`(search_knowledge_gate)・`:137`(next_event_id)・`:153`(auto_log)にいずれも`except: pass`または`except: nums = []`という無条件except節が存在し、失敗を記録せず処理を継続する。
- `mocka_mcp_server_vps.py:284`(`args.get("author", "Claude")`)・`:288`(`.get("why_purpose", "")`)は、必須フィールド欠落時にデフォルト値へ静かに置き換える。

---

## 3.3 未定義責務領域

### (1) PHI-OS / Orchestra / Relay / Memoryの責務重複

- 各モジュールの自己記述: PHI-OS(`phi_os/__init__.py:1-2`「Single Entry Point for all MoCKA events」)、Relay(`relay/mcp_bridge.py:1-6`「MCP LayerとEvent Integrity Frameworkを繋ぐ唯一の橋」)、Memory(`core_kernel/memory_core/__init__.py:1-10`「最小永続化層、外部DB/Redis/Network/LLM/Workflow制御は行わない」)。Orchestraには同等の自己記述文書は確認されなかった。
- PHI-OS(`phi_os/api/time_api.py:29`)とRelay(`relay/mcp_bridge.py:10`)がそれぞれ独立に`RelayKernel()`をインスタンス化しており、同一機能領域の状態管理が2箇所に存在する。
- `core_kernel/phios_integration/adapters.py:3-9`はMemory/Relay/Orchestraへのno-opブリッジ層を宣言しており、3モジュールがPHI-OSを介して間接アクセスされる設計であることを示している。

### (2) 境界が曖昧なモジュール

- `data/mocka_events.db`: PHI-OSが「Single Truth」と宣言(`phi_os/event_gate.py:18-20`)する一方、Relay側からも参照されるが正式な契約文書は確認されなかった。
- `data/prevention_queue.json`: `phi_os/migrate_prevention_queue.py:23`が読む一方、書き込み元は`interface/health_check.py:31`・`app.py`であり、所有者の明記は確認されなかった。
- `data/tic/`配下(mcp_schema_hash.json・evaluation_queue.jsonl・relay_ping.json等): PHI-OS/Relay/Memory/Orchestraいずれの配下でもなく、`interface/`層が実質的に集約管理している。
- `core_kernel/phios_integration/adapters.py`自体が、PHI-OSでもMemory/Relay/Orchestraでもない`core_kernel`配下に存在する。

### (3) 所有責任が存在しない処理フロー

- `data/tic/evaluation_queue.jsonl`: `interface/tech_watcher.py`が書き込むが、読み出しは`app.py`のダッシュボード表示のみで、意思決定系への連携経路は今回の調査では確認されなかった。
- `data/prevention_queue.json`: `docs/governance/prevention_queue_backlog_analysis_v1.md:99-105`によれば、TODO_347修正(2026-06-25)後もphi_os_audit由来のprevention entryが生成され続けているが、投入元(health_check.py等)が新ロジックを参照しているかは同文書内で「未確認」とされている。
- `data/tic/relay_ping.json`: `app.py`のrelay_ping()が書き込み、`_load_relay_ping()`がダッシュボード表示に使うのみで、それ以上のアクション経路は確認されなかった。

### (4) 暗黙的依存関係

- `phi_os/api/time_api.py:23-24`が`relay.relay_kernel.RelayKernel`・`phi_os.semantic.query_resolver`をimportしているが、この依存関係を定めた契約文書(docs/contracts/配下)は確認されなかった(設計上の制約はコードコメント`time_api.py:18-19`にのみ記載)。
- `relay/mcp_bridge.py:9`が`phi_os.event_gate`のプライベート関数(`_get_conn`・`_ensure_idempotency_table`、アンダースコア始まり)を直接importしているが、これを定めた契約文書は確認されなかった。

---

## 3.4 障害再発条件

### (1) 過去障害の再発条件

- `docs/incidents/INC-20260401-001.md:12-14,23-24`: OAuthトークン露出の根本原因(storage_state()出力の未確認)は`.gitignore`拡張という手続き的対処に留まり、確認ステップ自体を構造的に強制する仕組みは今回の調査では確認されなかった。
- `docs/incidents/INC-20260401-002.md:28-29`: 外部API無料枠超過の対策(Playwright経由への切替)は設計提案の記載のみで、実装済みの確認は今回の調査範囲では得られなかった。
- `docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md:11-12`: 6箇所のスレッド起動をimport時から実行時へ移す設計は「Implementation完了」と記載されるが、同文書内に「本文書作成時点ではapp.pyへのコード変更は一切行っていない」とも明記されており、実装は人間承認待ちの状態。
- `docs/governance/INCIDENT_LEGACY_NOTE.md:9-12,20-21`: `runtime/error_capture_engine.py`が非稼働であることが確認されており、下流の`incident_classifier.py`等は入力なしで空振りしている可能性が記録されている。

### (2) タイミング依存バグ

- `docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md:66-70`: `_auto_audit_loop()`スレッドが`_load_pqueue()`定義(65行後)より先に起動する競合状態が実測ログ(`_trace_app_stdout.log:3`)で確認されている(`NameError: name '_load_pqueue' is not defined`)。
- `docs/governance/prevention_queue_backlog_analysis_v1.md:69-71`: ハッシュファイル書き込み中の不完全な状態を監視スクリプトが読み込むタイミング競合により、513件のJSON parse failureが発生したことが記録されている。
- `docs/governance/execution_gate_v1.md:31`: 「race conditionが再現不能であること」が判定基準として記載されているが、この基準が満たされているかの確認記録は今回の調査範囲では得られなかった。

### (3) キャッシュ・同期不整合

- `docs/governance/state_dependency_risk_map_v1.md:7-18,79-83`: working_memory.jsonへの非atomic書き込みと同時更新の可能性が「状態キャッシュ破損→全write系Fail Closed」という連鎖として記録されている。
- `interface/essence_auto_updater.py:1-26`: 300秒/60秒/120秒/600秒/3600秒という複数間隔のバックグラウンド処理が共有ディレクトリ(REDUCING/RE_REDUCED/ESSENCE_DONE)へ書き込むが、これらの間の排他制御・ロック機構は今回の調査範囲では確認されなかった。
- `docs/governance/prevention_queue_backlog_analysis_v1.md:95-105`: TODO_347修正(2026-06-25、gate_policy.py統一)後もphi_os_audit由来のprevention entryの比率が低いままであり、投入元コンポーネントが新ロジックを未参照である可能性が記録されている。

### (4) ループ停止・情報欠落の再現性

- `docs/governance/civilization_loop_investigation_v1.md:57-82`: 「断絶」と表現されていた事象は調査の結果、8種類の独立した健全性メトリクスが個別集計されているだけであり、パイプラインの接続破断ではないと記録されている。ただし、recurrence→prevention→decision→auditの実処理チェーン(`/prevention/generate`エンドポイント)自体の実行検証は本調査のスコープ外とされている(同文書93-95行)。
- `runtime/civilization_loop_engine.py:41-60`: 各エンジンのimport失敗は個別にtry/exceptで捕捉され`civilization_loop_log.json`に記録された上で処理が継続するが、部分的なループ失敗からの復旧・再同期の仕組みは確認されなかった。
- `docs/governance/CI_FAILURE_ANALYSIS_v0.1.md`(既存分析、本観測では再検証していない): 700件全件が同一パターンで失敗し続けている(2026-06-22〜2026-07-04)という既存の確認済み事実を参照。

---

## 除外事項の明記

指示書「4. 評価出力形式」(4.1構造評価A〜D、4.2不安定要素のCritical/Moderate/Low分類、4.3制度欠陥分類、4.4強化提案)は、評価・severity判定・制度設計そのものであり、くろこの担当範囲外として本文書には一切含めていない。上記3.1〜3.4で提示した構造的事実の重要度判定・分類・改善提案は、R01・博士によるPhase 2以降の判断に委ねる。

---

以上、確認できた構造的事実の提示をもって本観測作業を終了する。評価・severity分類・改善提案は行っていない。R01と博士の判断を待つ。

---

## 改訂履歴

- v0.1(2026-07-04): MoCKA-AUDIT-INSTRUCTION-v1.0への対応として新規作成。3.1〜3.4の重点監査項目についてのみ、観測レイヤー(file:line根拠に基づく構造的事実)を記録。4.評価出力形式は範囲外として除外。くろこ起草。
