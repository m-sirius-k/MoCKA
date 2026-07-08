# MOCKA_EDGE_AUDIT_REPORT_v1.0

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / 確認のみ・実装/修正・commit実行は一切行っていない

詳細な調査過程・根拠は[MOCKA_EDGE_AUDIT_v1.0.md](MOCKA_EDGE_AUDIT_v1.0.md)を参照。
本書はその要約と判定。

# Executive Summary

TODO_428で確立した"一次データ->状態生成->異常検出"という流れをMoCKA全体へ試験的に適用した。
対象はACTIVE.todos(69件)の全件、実行中プロセス、Artifact管理、.gitignore/.gitattributes、
Governance境界(human_gate_cli.py)、外部接続の表層。全件を同じ深さで監査できたわけではなく、
特にACTIVE.completed(48件)・ARCHIVE.completed(363件)は個別再監査していない
(Non Actionsを参照)。

**訂正(Phase 9調査、2026-07-08)**: 本書の初版は"app.pyが新旧2バージョン同時稼働"を
最大の発見(High Risk)としていたが、これは誤診断だった。PID 16436はMoCKA本体の
`app.py`ではなく`PlanningCaliber/workshop/seo-os/command_center/app.py`という
別ディレクトリ・別ファイルの独立プロセス(ポート8750)であり、MoCKA本体app.py
(PID 10904、ポート5000)とは無関係。コマンドライン文字列の表層一致のみで
同一ファイルと誤認したことが原因。MoCKA本体のRuntime Single Authorityは
実際には壊れていなかった。詳細は[MOCKA_EDGE_AUDIT_v1.0.md](MOCKA_EDGE_AUDIT_v1.0.md)
Phase 2訂正箇所を参照。

この誤診断の教訓として、今回最大の実質的成果は"Runtime確認は停止判断の前に必ず
親プロセス・作業ディレクトリ・ポートまで裏取りしないと誤診断し得る"という
検証手順そのものの学びであり、当初想定した具体的なapp.py二重化リスクではない。

# Current System State

- Repository: TODO_428の6ファイルcommit(571351a95)が最新。他に多数の未commit差分・
  未追跡ファイルが残存(TODO_428と無関係、既存作業)。
- Runtime: MoCKA本体のapp.py(PID 10904、ポート5000、commit後起動)・
  mocka_mcp_server.py(PID 1768)・gateway.py・sync_watch.py・interface/mocka_watcher.pyが
  稼働中。PlanningCaliber/workshop/seo-os/command_center/app.py(PID 16436、ポート8750)は
  別サービスであり無関係。watchdog_mocka.pyはプロセスリストで未確認(要追加調査)。
  MoCKA本体のRuntime Single Authorityは確認された(単一プロセス、commit後起動)。
- MCPセッション: 本セッションはMoCKA系ツール0件接続。既知のDrift事象と同型。

# Closed Items

ACTIVE.todos内でstatus="完了"の15件(TODO_401、GOVERNANCE_MILESTONE_GM1/ADDENDUM、
GM2_ROADMAP、CATEGORY_REGISTRY_V1、GM3_VISION、GM2_STEP1_COMPLETE、GM2_BASELINE_STEP1、
KN_SERIES_LEDGER、REGISTRY_CHARTER_APPROVAL、GM2_REGISTRY_BASELINE_001、
KN_IA_NAMING_CONFIRMED、REGISTRY_SERIES_V1_0_BASELINE、TODO_426、TODO_427)。
いずれも設計・実装・検証・Decision Record・責任境界の5条件を満たしていると
一次データ上確認できた(個別のDecision Record内容までは全件突合していない)。

**Closed: 15件**

# Open Edge Issues

TODO一次データ由来47件(未着手/保留/要判定、進行中6件・完了15件・廃止1件を除く)+
本監査で新規発見した1件(TODO_428自身のstatus未更新)。
(当初"app.py二重稼働"を新規発見2件目としていたが、Phase 9調査で誤診断と判明し撤回した)

**Open Edge: 48件**

主要なもの(詳細は監査本体参照):

1. **TODO_428自身のstatus未更新**(新規発見、High): 本セッションでGenerator実装・
   テスト・commitまで完了したが、`MOCKA_TODO_ACTIVE.json`のTODO_428エントリのstatusは
   "未着手"のまま。"Artifact存在->Review->Test->Decision Record->Commit->TODO Status更新"
   の最終工程が未実施(MCPセッション不通でmocka_update_todo相当の書込みができないため)。
2. **GL7-UNENFORCED-CONDITIONS-BUG**(High): 安全条件3点が実行経路に未接続という
   既存TODO。本監査では実行経路への接続有無を再検証していないため未着手のまま。
3. **TODO_411/412/413**(High): AUTO_SEAL書き込み経路トレース・承認ゲート構造検証・
   CHANGE_START/DONEプロトコル接続確認。いずれもTODO_427の後工程として重要。
4. **MCP-TOOL-REGISTRY-DRIFT / TODO_423**(High): 本セッション中に実際に再現(MCP0件接続)
   ・再確認(events.db文字化け15件)された、継続中の既知事象。
5. **TODO_429 / human_gate_cli.py統合ギャップ**(Medium): コードは存在するが
   他コードから未import、git未追跡。制度整理(TODO_429)が未実施。
6. **anchor_record.jsonの二重配置**(Medium): `governance/`と
   `mocka-governance-kernel/anchors/`に同一内容が存在する理由が不明。
7. **Orchestra バージョン欠番**(Low): `tools/mocka_orchestra_v01-03->v10`(v04-v09欠番)
   +バックアップファイル散在。整理対象。
8. その他(Medium/Low、E分類中心): TODO_365(表示バグ)、TODO_397(命名衝突)、
   TODO_377/390/WP_DUPLICATE等(整理対象)、TODO_417/424(外部要因保留)、
   TODO_325(セキュリティ設計、保留)。

# Risk Classification

| Risk | 件数 | 主な内容 |
|---|---|---|
| High | 4 | TODO_428 status未更新(新規)、GL7-UNENFORCED-CONDITIONS-BUG、TODO_411/412/413、MCP-TOOL-REGISTRY-DRIFT/TODO_423 |
| Medium | 約10 | TODO_429統合ギャップ、anchor_record二重配置、TODO_325、TODO_363/372、TODO_365、TODO_397、TODO_417、TODO_424、CRLF混入リスク |
| Low | 約32 | E分類の整理対象群(TODO_377/390/WP_DUPLICATE/369/410/REGISTRY_SERIES_V1_1_CANDIDATE/INL_DUPLICATE_OF等)、B分類の通常開発バックログ |

件数は本監査の分類判断であり、機械的に一意に決まる値ではない。
(当初High 7件としていたが、"app.py二重稼働"の誤診断撤回により4件へ修正)

# Recommended Order

1. **TODO_428のstatus更新+Decision Record登録**: MCPセッション復旧後、
   TODO_427と同様に遡及記録する。
2. TODO_411/412/413(AUTO_SEAL関連の構造検証3点)を次のガバナンス監査サイクルで着手。
3. TODO_429(human_gate_cli.py統合)を別セッションで着手(今回はNon Actionsのため未実施)。
4. anchor_record.json二重配置の理由確認(意図的か整理漏れか)。
5. Low分類群は優先度通りバックログに残す。

(当初1番目としていた"app.py二重稼働の解消"はPhase 9調査で誤診断と判明したため削除した。
MoCKA本体app.pyは単一プロセス(PID 10904)でRuntime Single Authorityは元々確保されている)

# Non Actions

今回意図的に行わなかったこと(指示通り):

- TODO_429の実装
- 新規architecture変更
- 既存artifact migration
- watchdog常駐化
- 大量整理(Orchestraバージョン統合、重複ファイル削除等)
- ACTIVE.completed(48件)・ARCHIVE.completed(363件)の全件再監査

(Phase 9で検証したPID 16436は無関係なSEO-OSサブシステムのプロセスと判明したため、
停止判断・停止実行のいずれも行っていない/行う必要がない)

# Final Judgment

MoCKAの根幹(記録・検証・継承・再構成)に照らすと、制度・設計文書のレベルでは
Closed 15件が示す通り健全に閉じている領域がある。当初"Runtime(実行中プロセス)と
Repository(commit履歴)の間に乖離(app.py二重稼働)がある"としていたが、Phase 9の
証跡確認(親プロセス・作業ディレクトリ・ポート)によりこれは誤診断であり、
MoCKA本体のRuntime Single Authorityは元々確保されていたことが判明した。

今回のAuditが示した本質的な教訓は、具体的なapp.py二重化リスクの発見ではなく、
"Runtimeに関する結論は、停止判断のような重い行動へ進む前に、コマンドライン文字列の
表層一致だけでなく親プロセス・作業ディレクトリ・ポートまで裏取りしなければ誤り得る"
という検証手順そのものである。実際、Phase 9の指示が"証跡取得(Task 1)を停止判断
(Task 4)より先に行う"という順序を明示していたからこそ、誤った停止実行に至る前に
この誤診断を発見できた。TODO_428自身も"実装は閉じたが制度としては未封印"という
状態にあり(status未更新・Decision Ledger未登録)、本Audit自体が"一次データからの
機械的検証"という設計原理を全体に適用した結果、自分自身(TODO_428)の未完了部分を
発見したことは、この手法が機能している証左と見なせる。
