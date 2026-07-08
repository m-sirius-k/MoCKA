# MOCKA_EDGE_AUDIT_v1.0

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / 確認のみ・実装/修正は一切行っていない

対象: MoCKA全体(`C:\Users\sirok\MoCKA`)。TODO_429実装・新規architecture変更・
既存artifact migration・watchdog常駐化・大量整理は今回禁止事項として一切行っていない。

範囲の限界(正直な申告): `MOCKA_TODO_ARCHIVE.json`(完了363件)は個別再監査していない
(既にTODO_420/421/423のSSOT監査、MOCKA_OVERVIEW_STALENESS_REPORT.mdで一次監査済みのため)。
`ACTIVE.completed`(48件)も同様に全件精査はせず、TODO_428実装時に発見したTODO_414のみ
個別記録済み。外部リポジトリ(mocka-external-brain/mocka-civilization等)は表層確認のみ。

## Phase 1: ACTIVE.todos(69件)分類

凡例: A=実装済みだが未封印 / B=設計済み未実装 / C=制度判断待ち / D=技術的負債 / E=重複・整理対象 / 進行中=作業中(Edge Issueではない) / 完了=既に閉じている

| ID | Status | 分類 | 備考 |
|---|---|---|---|
| TODO_428 | 未着手(表示上) | **A** | 本セッションでGenerator実装・テスト・commit(571351a95)まで完了済みだが、ACTIVE.json自身のstatusフィールドが"未着手"のまま更新されておらず、Decision Ledger登録もMCPセッション不通で未発行。"Artifact存在->Review->Test->Decision Record->Commit->TODO Status更新"の最終2工程が未完了 |
| GL7-UNENFORCED-CONDITIONS-BUG | 未着手/高 | **D(High)** | title通り"GL7の安全条件3点が実行経路に未接続"。安全機構が名目上存在するが実行経路に繋がっていない、既知の重大ギャップ |
| MCP-TOOL-REGISTRY-DRIFT-DECISION-WRITE-PATH | 未着手/高 | **C/D(High)** | 本セッション自体がこの事象の再現(MoCKA系MCPツール0件接続)。DC_20260705_006のLedger反映が本セッションでも未完了のまま持ち越し |
| TODO_411 | 未着手/要判定 | C(High) | AUTO_SEAL書き込み経路の完全トレース。TODO_427(日次seal Human Gate化)の後工程として重要度高い |
| TODO_412 | 未着手/要判定 | C(High) | 承認ゲートの構造検証(mocka_git_safe_commit以外に承認処理がないか) |
| TODO_413 | 未着手/要判定 | C(High) | CHANGE_START/CHANGE_DONEプロトコルとAUTO_SEALの接続確認 |
| TODO_423 | 保留/中 | D(High) | Decision Ledger文字化け原因未特定。本セッションでもmocka_events.db when_ts列に文字化け15件を再確認(別事象だが同系統) |
| TODO_429 | 未着手/中 | **A/B** | Phase 6で確認: `governance/human_gate_cli.py`(133行)は実装済みだが他コードから一切importされておらず、統合作業(本TODOの本体)が未実施。git未追跡のまま |
| TODO_325 | 保留/高 | B/C | PHI-OS Trust Boundary(DBアクセスACL制限)。セキュリティ関連設計、実装未着手 |
| TODO_363 | 未着手/中 | C | sync_watch.py等のgit迂回パターンの制度確認 |
| TODO_372 | 未着手/中 | C | "修正方式の選択自体がHuman Gateを経ないパターン"— メタなガバナンス欠落の指摘 |
| TODO_365 | 未着手/中 | D | risk/recommendationが完了済みTODOを推奨し続ける表示バグ |
| TODO_397 | 未着手/低 | E | human_gate.py命名衝突(semantic/query_engine系 vs phi_os系) |
| TODO_417 | 保留/中 | C | Copilot Studio、Power Apps Premiumライセンス未契約で外部要因保留(既知) |
| TODO_424 | 未着手/低 | C | mocka-api Worker(Legacy)廃止可否の判断待ち(TODO_422関連) |
| TODO_MOCKA_SEAL_GIT_ADD_A_SEPARATION | 未着手/中 | B | anchor_update.pyのgit add -A分離設計、未実装 |
| GL7周辺以外のB群 | 各種 | B | TODO_207/205/166/150/122/334/335/368/383/392/SAKURA_SSH等、設計・計画段階で実装未着手(通常の開発バックログ、緊急性は低〜中) |
| TODO_377/390_CLEANUP_CHECK/WP_DUPLICATE_PAGES_CLEANUP/369/410/REGISTRY_SERIES_V1_1_CANDIDATE/TODO_INL_DUPLICATE_OF | 保留・未着手/低 | E | 整理・重複対応系、優先度低 |
| TODO_UNIFIED_PRODUCT_TODO_LOCATION | 未着手/中 | C | 製品横断TODO参照先の統一設計、制度判断待ち |
| TODO_221/220/242/HAB_5LAYER/PHI-OS-HUMAN-GATE-STATE-MODEL-V1/TODO_425 | 進行中 | (進行中) | 作業中、Edge Issueとしては扱わない |
| TODO_401/GM1系/GM2系/GM3_VISION/KN_SERIES_LEDGER/REGISTRY_CHARTER_APPROVAL/CATEGORY_REGISTRY_V1/KN_IA_NAMING_CONFIRMED/REGISTRY_SERIES_V1_0_BASELINE/TODO_426/TODO_427 | 完了 | (完了) | 設計・実装・検証・Decision Record・責任境界が揃った完了項目、15件 |
| TODO_PROS_PUBLISH_JOB_0002 | 廃止 | (テストデータ) | note記載通りTODO_241統合テスト用、実データではない |

## Phase 2: Repository <-> Runtime監査

現在実行中プロセス(2026-07-08 16:35時点、PowerShell `Get-CimInstance Win32_Process`で確認):

| Component | Commit(最終) | Runtime PID | 起動時刻 | Status | Risk |
|---|---|---|---|---|---|
| app.py(MoCKA本体) | 3bc8084(2026-07-08 15:46:56) | **10904** | 16:02:52 | commit後に起動(正) | 正常 |
| mocka_mcp_server.py | b5f36e4(2026-07-08 15:24:50) | 1768 | 15:26:35 | commit後に起動 | 正常 |
| gateway.py | (未確認) | 1912 | 14:27:38 | - | 未確認 |
| sync_watch.py | (未確認) | 6780 | 14:27:34 | - | 未確認 |
| watchdog_mocka.py | 3bc8084(同commit) | (プロセスリスト内に見当たらず) | - | **未起動の可能性** | 要確認 |

**訂正(2026-07-08、Phase 9調査により判明)**: 当初"app.pyが2プロセス同時稼働(PID 16436・10904)、
Runtime二重化"としてHigh Risk記載していたが、これは誤診断だった。PID 16436の親cmd.exeの
起動コマンドを確認したところ、作業ディレクトリは`C:\Users\sirok\MoCKA\PlanningCaliber\workshop\seo-os\command_center`
であり、MoCKA本体の`app.py`とは別ディレクトリの別ファイル(SEO-OSサブシステムの独立コンポーネント、
TODO_354によりMoCKA本体と別管理の私有リポジトリ領域)だった。ポートもPID 16436が8750、
PID 10904(MoCKA本体app.py)が5000で別。コマンドライン文字列(`python -X utf8 app.py`)の
表層一致のみで同一ファイルと誤認したことが原因。MoCKA本体のapp.pyはPID 10904の1プロセスのみで、
Runtime Single Authorityは実際には壊れていない。PID 16436は無関係な稼働中サービスであり
停止対象ではない。

`watchdog_mocka.py`のプロセスがリスト内に見当たらない点は、常駐が別方式(タスクスケジューラ等)
になっているか、単に現在停止しているだけかを本監査では切り分けていない(要追加確認)。

## Phase 3: Artifact管理監査

| Artifact | 分類 | 備考 |
|---|---|---|
| `C:\Users\sirok\MOCKA_OVERVIEW.json`(legacy) | Primary(Historical Snapshot) | TODO_428設計方針により意図的に凍結維持 |
| `data/MOCKA_OVERVIEW.json` | Derived | export_for_cloudflare.pyのミラー、`_snapshot_at`付き |
| `data/MOCKA_OVERVIEW_CURRENT.json` | Derived | 本日新設(TODO_428)。Generator+Input SSOTがPrimaryであり本体は非Git管理 |
| `data/MOCKA_TODO_ACTIVE.json`/`ARCHIVE.json` | Primary | 唯一の書込先、Git管理下(ホワイトリスト) |
| `data/MOCKA_TODO.json` | Derived(役割変更後) | TODO_420設計によりExport専用キャッシュへ再定義済み |
| `governance/anchor_record.json` / `mocka-governance-kernel/anchors/anchor_record.json` | Primary(seal) | 2箇所に同一内容が存在(重複そのものは意図的な二重化か要確認、Orphan寄りの疑い) |
| `_mocka_app_restart_*.log`/`_mocka_mcp_restart_*.log` | Runtime(保存不要) | 現在untracked、.gitignoreにも明示パターンなし(`*.log`ワイルドカードが存在しない) |
| `docs/governance/*_REPORT.md`類(TODO_206/HUMAN_GATE_CLI_ALIGNMENT等) | Primary(記録) | 複数が未commitのまま滞留(Phase 1参照) |

**発見**: `.gitignore`には`*.log`のような包括パターンがなく、`_mocka_*_restart_*.log`は
個別追加されない限りuntrackedのまま放置され続ける(Orphan化リスク)。また
`anchor_record.json`が`governance/`と`mocka-governance-kernel/anchors/`の2箇所に
同一内容で存在する理由は本監査では特定できず、意図的な複製か整理漏れかは要確認。

## Phase 4: Integrity監査(横展開)

- **status/bucket不整合パターン**: TODO_414(本セッションTODO_428実装時に発見、記録済み)。
  同型の不整合が他のTODO_IDにも存在するかは、ACTIVE.completed(48件)・ARCHIVE.completed
  (363件)の全件突合が必要だが本監査では未実施(範囲の限界を参照)。
- **timestamp破損パターン**: `mocka_events.db`のwhen_ts列に15件確認済み(本セッションで
  再確認、TODO_423関連)。`decision_ledger.jsonl`のapproved_atフィールドは目視サンプルでは
  ISO8601形式で一貫しており、同種の破損は確認されなかった(全43件の機械的検証はしていない)。
- **stale metadataパターン**: `MOCKA_OVERVIEW.json`(legacy)本文がv4.0(2026-06-18)で
  凍結(既知、TODO_428の発端そのもの)。`data/tic/mcp_schema_hash.json`は
  2026-07-08T14:27:58更新であり、mocka_mcp_server.pyの最終commit(15:24:50)より前
  ->ハッシュストアが最新commitを反映していない可能性がある(要再実行確認)。
- **hash不一致**: 上記mcp_schema_hash.jsonの鮮度以外に、本監査で新規のhash不一致は
  検出しなかった。

## Phase 5: Git安全監査

- `.gitattributes`は`* text=auto eol=lf`でLF正規化を宣言しているが、`git diff`実行時に
  `data/MOCKA_OVERVIEW.json`・`data/MOCKA_TODO.json`等複数ファイルで
  "CRLF will be replaced by LF"警告が発生した。これは正規化がcommit時点で働く仕様のため
  異常ではないが、Windows上のツール(Pythonスクリプト等)がCRLFで書き出している実態を示しており、
  次回commit時に無関係な改行コード差分が混入するリスクがある。
- `mocka_git_safe_commit()`(`governance/mocka_git_safe_commit.py`)は本セッションで
  実地使用し、Core System File除外・post-commit検証とも正常動作を確認済み(TODO_428 commit時)。
- `.gitignore`の`data/*`除外+ホワイトリスト方式は機能しているが、新規data/配下ファイルを
  追加する際にホワイトリスト追加を忘れると静かにスキップされる構造的リスクは
  TODO_428実装時に実際に発生しかけた(`MOCKA_OVERVIEW_CURRENT.json`、最終的に非Git管理と
  裁定して解消)。同種の見落としが将来の別ファイルでも起こり得る。
- UTF-8/CP932禁止文字混入は、本セッションで作成した文書内で複数回発生し都度修正した
  (""等の全角括弧)。既存の`TODO_428_DESIGN_NOTES.md`(前セッション作成)にも同様の
  違反が残存しているが、本監査では既存ファイルへの修正は行っていない(スコープ外)。

## Phase 6: Governance境界監査

- `governance/human_gate_cli.py`: 実装済み(133行、submit/approve/reject/get_state/
  list_pendingを既存`phi_os/human_gate.py`経由で呼ぶのみと明記)だが、他の.pyファイルから
  一切importされておらず、git未追跡のまま。TODO_429が"制度整理(既存Human Gateへの
  入口追加)"として存在するが未着手。実装と制度(TODO)の間にギャップがある状態
  ("名前だけ存在する制度"ではなく、"コードは存在するが制度的に未統合"に該当)。
- `interface/dashboard.py`: 既存ファイル、1行差分が未commitのまま滞留(内容未精査)。
- Decision Unit(B/C承認): `human_gate_cli.py`のコメントから存在が確認できるが、
  `phi_os/human_gate.py`本体の実装詳細までは本監査で深掘りしていない。

## Phase 7: 外部接続監査(表層確認)

- MCPセッション: 本セッションはMoCKA系MCPツール(mocka_get_todo等)が0件接続。
  これはMCP-TOOL-REGISTRY-DRIFT-DECISION-WRITE-PATH(TODO)が指す事象の再現であり、
  "MoCKA障害ではなくConnector/session問題"として扱う既存分類方針に従う。
- Orchestra: `tools/mocka_orchestra_v01〜v03.py`の後、`v04〜v09`が存在せず`v10`へ飛んでおり
  (`.bak_20260707_TODO419`・`_backup.py`も残存)、バージョン系列に欠番と複数バックアップの
  重複が見られる(整理対象、E分類)。`mocka_orchestra_parallel_v01〜v06`は連番で欠番なし。
- External Brain(`mocka-external-brain`): リポジトリとしては存在するが、README/CITATION等
  公開ドキュメント中心の構成であり、本監査ではMoCKA本体との実行時連携有無までは確認していない。
- Connector Framework: TODO_334/335(Perplexity/Genspark実機疎通テスト)が未着手のまま
  残っており、実装(設計)と実機検証の間にギャップがある。
