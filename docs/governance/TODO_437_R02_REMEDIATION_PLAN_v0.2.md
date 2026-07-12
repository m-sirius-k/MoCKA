# TODO_437 R02 Remediation Plan v0.2

作成: Codex / 2026-07-10 / 設計書のみ・実装は一切行っていない  
前版: `TODO_437_R02_REMEDIATION_PLAN_v0.1.md`（保持）

位置づけ: 本文書はTODO_437の中期(Root Cause Analysis)〜長期(Permanent Fix)に対応する設計文書である。v0.1の設計判断を保持し、追加調査の客観データとHuman Gate判断境界を追記した。本文書に基づく実装はHuman Gate承認後のR02実装フェーズでのみ行う。コード変更、timeout値変更、Core System File変更、DB構造変更はいずれも含まない。

## 1. 現象の整理

- `/agent/mocka_write_event`のE2Eレイテンシは実測で一貫して約5.8〜6.1秒(2026-07-10、5回連続計測。5.73/5.74/5.99/5.85/6.14秒等、常時であり間欠的ではない)。
- 内訳計測の結果: GATE(`/api/gate/event`)単体は5回連続で2.27〜2.33秒。
- `WorkingContext.live_update`/`emit_event_to_context_runtime`/`maybe_snapshot`の3関数は個別実行で合計約0.03秒。
- GATE単体(約2.3秒)+3関数(約0.03秒)の合計(約2.33秒)と、E2E全体(約6.0秒)の間に約3.7秒の未説明の差が残っている。
- 影響: timeout=3で呼ぶ既知の呼び出し元10箇所で、構造的に記録失敗(タイムアウト→fallback/例外)が発生していた可能性が高い。
- 未確定事項: (a)GATE側2.3秒の真因、(b)E2Eとの差3.7秒の真因。

## 2. 暫定対策の整理(実施済み、DC_20260710_005・commit 3755c107f/e7a779a4c)

- timeout=3→12統一(呼び出し元10箇所)。恒久対策ではない。記録失敗の発生可能性を下げる効果はあるが、レイテンシそのものは未解消。
- ロールバック: 各ファイルのtimeout値を3に戻すのみ(git revertまたは個別Edit)。低リスク・即時実施可能。

## 3. 根本原因調査計画(実装なし、調査・計測のみ)

以下の仮説を、互いに独立した形で個別に検証する。いずれも本番プロセスへの書き込み変更・再起動を伴わない手法を優先する。

### 3.1 GATE内部処理(`/api/gate/event`)の内訳計測

- 対象: `phi_os/event_gate.py`の`process_event()`(`validate`/`_next_event_id`/`_write`/`sign_event`/`commit`)。
- 手法: 各サブステップの前後に一時的な計測コード(`time.perf_counter()`)を挿入して実行するか、`py-spy dump --pid <pid>`等、対象プロセスを止めずに済むサンプリングプロファイラで計測する。
- 成功条件: 約2.3秒の内訳が、どのサブステップに帰属するかが定量的に判明すること。

### 3.2 events.dbロック競合

- 対象: `data/mocka_events.db`(WALモード、`busy_timeout=5000ms`)。
- 手法: WALファイルサイズの推移監視、`PRAGMA wal_checkpoint`頻度確認、同時書き込みプロセス数の実地棚卸し(essence_auto_updater/PostToolUseフック/他セッション等の書き込み頻度をログから集計)。可能であればSQLiteの`trace`/`profile`コールバックでロック待ち時間を直接計測する。
- 成功条件: 2.3秒のうちロック待ちが占める割合が定量化されること。書き込み集中時間帯とレイテンシの相関が確認または否定されること。

### 3.3 `mocka_mcp_server.py`のthreaded化の効果

- 対象: `mocka_mcp_server.py`の`app.run(host="0.0.0.0", port=5002, debug=False)` (`threaded`未指定)。
- 手法: 本番サーバーとは別プロセス・別ポートで一時起動する複製環境で`threaded=True`を設定し、同条件でE2Eレイテンシを再計測して比較する。本番サーバーは本調査では再起動しない。
- 成功条件: `threaded=True`環境下でE2Eレイテンシが有意に短縮するか、または変化しないかが実測で判明すること。

### 3.4 I/O待ち(ディスク/ネットワーク)

- 対象: `working_context_latest.json`/`event_runtime_log.json`/`scheduler_state.json`への読み書き、およびGATEへのHTTP round-trip。
- 手法: 3.1のプロファイリングと統合実施し、I/O待ち区間を分離抽出する。
- 成功条件: I/O待ちが支配的要因かどうかが判明すること。

### 3.5 クライアント共通化・非同期化による改善余地の評価(設計検討のみ)

- 対象: timeout=3→12にした10箇所+`mocka_git_safe_commit.py`の計11呼び出し元。
- 手法: 各呼び出し元の実装を比較し、共通クライアントヘルパー(timeout値・リトライ・fallbackログの一元化)への集約が技術的に可能かを設計レベルで検討する。非同期化(fire-and-forgetをスレッド/キューへ逃がす)については、既存の「呼び出し元をブロックしない」設計方針(fallbackログ方式)との整合性を確認する。
- 成功条件: 共通化・非同期化のいずれかまたは両方が実装可能な設計として具体化されること。このフェーズでは実装しない。

## 4. 恒久対策候補(仮説ベース。3の調査結果により絞り込む)

- 候補A: GATE内部処理の最適化(3.1で特定されたボトルネックへの個別最適化)
- 候補B: events.db書き込み経路の見直し(接続プーリング、専用ライタースレッド/キューへの一本化等、3.2の結果次第)
- 候補C: `mocka_mcp_server.py`の`threaded=True`化(3.3の結果が支持する場合のみ)
- 候補D: 呼び出し元の非同期化(fire-and-forgetをバックグラウンドキュー化)
- 候補E: 共通クライアントヘルパーへの集約(TODO_364のgit経路集約と同型の設計)

優先順位・組み合わせの決定は、3章および14章の調査結果が出た後にHuman Gateで判断する。本文書の時点ではいずれも未採用の候補として並列に列挙するに留める。

## 5. 計測項目

- E2Eレイテンシ(`/agent/mocka_write_event`、5回以上の連続計測、平均・最大・最小)
- GATE単体レイテンシ(`/api/gate/event`直接、同条件)
- `WorkingContext`/`ContextRuntime`3関数の個別実行時間
- events.db WALファイルサイズ・チェックポイント頻度
- 同時書き込みプロセス数(推定、ログベース)
- (threaded=True検証時)同一負荷条件下でのレイテンシ比較

## 6. 回帰試験計画

- 恒久対策実装後、TODO_437の暫定対策検証と同一手順(`tools/mocka_auto_record.py`の`_post()`を実importし、3回以上連続POST)で再計測する。
- 既存呼び出し元10箇所+`mocka_git_safe_commit.py`について、fallbackログに新規のOFFLINE記録が発生していないことを一定期間(最低24時間)観察する。
- 実装前後で`verify_all.py` = ALL CHECKS PASSEDを確認する。

## 7. 完了判定基準(TODO_437 Permanent Fix完了の定義)

以下すべてを満たした時点でPermanent Fixを完了とし、Human Gate承認を得てTODO_437をCloseする。

1. GATE単体レイテンシ・E2Eレイテンシの内訳(3.1〜3.4)が定量的に説明されている(未説明の差が残っていない)。
2. 恒久対策実装後、E2Eレイテンシが明確に改善している(具体的な数値目標はHuman Gateで確定する。本文書での暫定目標例: 1秒未満)。
3. 24時間以上の観察期間でfallbackログへの新規記録が発生していない。
4. 既存timeout=12設定を維持したままでも、実測latencyに対して十分な安全マージン(目安3倍以上)が確保されている。
5. `verify_all.py` = ALL CHECKS PASSED。

## 8. ロールバック方針

- 各恒久対策候補は、実装前に対象ファイルの現状(commit `e7a779a4c`時点)をrevert基点として記録する。
- threaded=True化は単一パラメータの変更のため、`app.run()`の該当行をrevertするのみで戻せる。ただし本番サーバープロセスの再起動を伴う。
- events.db書き込み経路の変更は、変更前に`mocka_events.db`のバックアップを取得してから着手する。
- 共通クライアントヘルパー集約は、呼び出し元は無改修とすることで、ヘルパー実装のみのrevertで済む設計とする。

## 9. Human Gateが必要となる判断点

1. 3.1〜3.4の調査手法(特に`mocka_mcp_server.py`複製環境での`threaded=True`比較検証)を実施してよいか。
2. 4章の恒久対策候補のうち、どれを採用するか(3章および14章の調査結果を踏まえた選定)。
3. `mocka_mcp_server.py`(本番プロセス)の再起動を伴う変更(threaded=True採用時)の実施タイミング。
4. events.db書き込み経路の構造変更(候補B)を採用する場合、その設計の承認。
5. 7章の完了判定基準(特に数値目標)の最終確定。
6. TODO_437の最終Close判断。

## 10. 実施していないことの明示

本文書はR02 Remediation Planの設計書であり、いかなるコード変更・timeout値の追加変更・Core System Fileの変更も行っていない。TODO_438(execution_governance.py統合)にも一切触れていない。

## 13. Human Gate判断境界（更新）

### Boundary 7: 計測結果に基づく恒久対策候補の絞り込み承認

- Root Cause確定前の実装は禁止する。
- 複数候補から採用案を選択する場合は、Human Gate承認を取得する。
- 承認資料には、14章の根拠、候補ごとの期待効果・副作用・ロールバック、既存経路への影響を含める。

## 14. Root Cause Investigation Update

### 確定した否定事項

- 「GATE高速・WorkingContext遅延」という仮説は実測により否定された。
- Context更新処理は約0.03秒であり、支配的な遅延ではない。

### 証拠一覧

| 項目 | 結果 |
| --- | --- |
| E2E latency | 5.73〜6.14秒 |
| GATE latency | 2.27〜2.33秒 |
| Context処理 | 約0.03秒 |
| 未説明時間 | 約3.7秒 |
| DBサイズ | 82,026,496 bytes |
| events件数 | 15,312 |
| claude_sessions件数 | 94,408 |
| WAL | 有効 |
| busy_timeout | 5000ms |

### 現在の有力仮説

#### H1: MCP同期処理経路内の未説明区間

対象は`agent_call()`、`execute_tool()`、`mocka_write_event`分岐、HTTP前後処理、`auto_log()`、response生成である。E2EとGATE単体の差約3.7秒を、相関IDを用いた開始・終了時刻で分解する。

#### H2: SQLite同期commit構造

対象はevents INSERT、event_signatures INSERT、events UPDATE、claude_sessions INSERT、および複数commitである。正常経路ではGATEのevents系トランザクション後にMCPの`auto_log()`が同一SQLiteへ別commitするため、各SQLとcommitを個別に計測する。

#### H3: SQLite lock/busy待機

`busy_timeout=5000ms`との時間相関を確認する。現時点ではlock/busy待機時間の直接実測はなく、根本原因としては未確認である。

#### H4: threaded未指定による直列化

MCPサーバーの`threaded`は未指定である。複製環境・別ポートでの比較計測後にのみ、直列化を原因候補として採否判断する。

## Legacy Path Risk

- 正規経路は`data/mocka_events.db`である。
- `interface/router.py`には旧`data/events.db`への直接書込み実装が存在する。
- R02でDB経路を変更する場合、正規経路と旧経路を混同しない。旧経路の扱いを含む変更は、影響分析およびHuman Gate承認の対象とする。

