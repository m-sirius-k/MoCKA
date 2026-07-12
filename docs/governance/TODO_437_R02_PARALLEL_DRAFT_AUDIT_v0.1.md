# Parallel Draft Audit

作成: Claude-sonnet-5(くろこ) / 2026-07-10 / 監査記録のみ・正本統合は行っていない

目的: `TODO_437_R02_REMEDIATION_PLAN_v0.2.md`の出現を監査記録として残す。
本文書はv0.1・v0.2いずれの内容も変更・統合しない。両ファイルは現状のまま保持する。

## Detection

- 発見日時: 2026-07-10 16:51頃(git status確認時に発見。ファイルの実際の作成時刻は
  下記の通り)。
- ファイル名: `docs/governance/TODO_437_R02_REMEDIATION_PLAN_v0.2.md`
- 作成者表記: ファイル冒頭に「作成: Codex / 2026-07-10」と明記。Claude-sonnet-5
  (本セッション)が作成したものではない。
- ファイルシステム上のタイムスタンプ: Birth/Modify/Change いずれも
  2026-07-10 16:51:26(JST)。本セッションが`TODO_437_R02_REVIEW_SUMMARY_v0.1.md`を
  作成した時刻(CHANGE_DONE記録: 16:51:31)とほぼ同時刻であり、独立したプロセス
  (別AI・別セッション)による並行作業と推定される。
- サイズ: 11,577 bytes / 164行。
- Git状態: `git status --short`で`??`(untracked)。commit履歴には含まれていない。

## Classification

- 正本ではない。`TODO_437_R02_REMEDIATION_PLAN_v0.1.md`(本セッション作成、
  Human Gate提出準備中)が現時点の正本設計書である。
- 並行生成ドラフットである。v0.2冒頭に「前版: TODO_437_R02_REMEDIATION_PLAN_v0.1.md
  (保持)」と記載があり、v0.1を出発点として別途拡張を試みた形跡がある。ただし
  v0.1への統合作業を経ておらず、独立した並行ファイルのまま存在している。
- Human Gate未承認。v0.2の内容についてHuman Gateへの提出・承認手続きは
  行われていない。

## Content Review

### v0.1との差分概要

- 1〜10章の内容はv0.1(本セッション作成分の1〜10章)とほぼ同一の記述(現象整理・
  暫定対策整理・根本原因調査計画3.1〜3.5・恒久対策候補A〜E・計測項目・回帰試験計画・
  完了判定基準・ロールバック方針・Human Gateが必要となる判断点)。
- v0.1の11章(仮説マトリクス)・12章(恒久対策候補比較基準)に相当する内容は
  **v0.2には存在しない**(章番号が10の次に13へ飛んでいる)。
- v0.2独自の13章「Human Gate判断境界(更新)」は、v0.1の13章(6境界の一覧表)とは
  異なり、「Boundary 7: 計測結果に基づく恒久対策候補の絞り込み承認」という
  単一の追加境界のみを記載している。
- v0.2独自の14章「Root Cause Investigation Update」、および末尾の無番号セクション
  「Legacy Path Risk」は、**v0.1(本セッション作成分)には存在しない新規内容**である。

### 追加された技術事項(v0.2固有、要検証)

- 証拠一覧に、本セッションの実測(E2E latency・GATE latency・Context処理・未説明
  時間)に加え、以下の新規データ点が記載されている: DBサイズ(82,026,496 bytes)、
  events件数(15,312)、claude_sessions件数(94,408)、WAL有効、busy_timeout=5000ms。
  本セッションではこれらの数値を独自に取得・検証していない。
- H1(MCP同期処理経路内の未説明区間): `agent_call()`/`execute_tool()`/
  `mocka_write_event`分岐/HTTP前後処理/`auto_log()`/response生成を対象とする、
  より詳細な区間分解案。本セッションのH3(threaded化)/H4(I/O待ち)とは異なる
  切り口。
- H2(SQLite同期commit構造): GATEの`events` INSERT・`event_signatures` INSERT・
  `events` UPDATEに加え、**mocka_mcp_server.py側の`auto_log()`が同一SQLiteへ別途
  `claude_sessions` INSERTを行い、複数commitが発生している**という指摘。これは
  本セッションのH1(process_event()内サブステップ)・H2(events.dbロック競合)の
  いずれにも明示的に含まれていなかった新しい着眼点であり、未説明の3.7秒の
  有力な候補になり得る。
- H3(SQLite lock/busy待機): 本セッションのH2(ロック待ち)と概ね同義だが、
  「現時点ではlock/busy待機時間の直接実測はなく、根本原因としては未確認」と
  明記されている。
- H4(threaded未指定による直列化): 本セッションのH3と同義。
- Legacy Path Risk: `interface/router.py`に旧`data/events.db`(正規経路は
  `data/mocka_events.db`)への直接書込み実装が存在するとの指摘。本セッションの
  調査(3.1〜3.5、11〜15章)ではこの経路の存在に言及していない。候補B
  (events.db書き込み経路の見直し)を検討する際に無視できない新情報の可能性がある。

### 採用候補

- v0.2は候補A〜E(4章)を変更しておらず、本セッションのv0.1と同一の5候補を
  列挙している。新規候補の追加はない。
- v0.2独自のH1・H2(MCP側auto_log()の別commit、SQLite同期commit構造)は、
  既存候補A(GATE内部処理最適化)・候補B(events.db書き込み経路見直し)の
  スコープを拡張しうる着眼点だが、v0.2自体は新しい候補(F等)としては
  提案していない。

### 未検証事項

- v0.2記載の証拠一覧(DBサイズ・events件数・claude_sessions件数等)は、本監査
  時点で本セッションによる独立検証を行っていない。
- v0.2のH1(MCP同期処理経路内訳)・H2(auto_log()の別commit)は、いずれも
  実測による裏付けが記載されておらず、仮説段階のまま。
- Legacy Path Risk(interface/router.pyの旧経路)についても、本監査時点では
  該当箇所のコード確認を行っていない。

## Decision Boundary

- v0.2の内容(特にH1/H2の新規着眼点、Legacy Path Risk)をv0.1へ統合する場合は、
  Human Gate承認を要する。統合の要否・方法(v0.1への追記か、v0.2を正本に
  差し替えるか等)はHuman Gateの判断とする。
- Codex生成内容(v0.2)は、現時点では提案資料(参考情報)として扱う。正本としての
  地位は持たない。
- v0.2は削除せず、本監査の対象として保持する。

## 禁止事項の遵守

本監査作業において、以下はいずれも実施していない: v0.1への自動統合、
v0.2のリネーム、commit、Decision Ledgerへの追加。
