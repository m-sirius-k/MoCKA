# TODO_437 R02 Remediation Plan v0.3 DRAFT

作成: R02 Claude / 2026-07-10 / **Human Gate提出用統合Draft (Draft Only)**

## 位置づけ (Draft Only)

本文書は、TODO_437 R02 Remediation Plan の以下4ソースを統合した **Human Gate提出用Draft** である。

- `TODO_437_R02_REMEDIATION_PLAN_v0.1.md` (正本、母体保持)
- `TODO_437_R02_REMEDIATION_PLAN_v0.2.md` (Parallel Investigation Draft, 作成者表記: Codex)
- `TODO_437_R02_OBSERVATION_CANDIDATES_v0.1.md` (未検証Evidence Candidate整理)
- `TODO_437_R02_PARALLEL_DRAFT_AUDIT_v0.1.md` (並行生成監査記録)

制度文脈参照: `DC_20260710_005` / R01監査 `E20260710_7368241085333` (条件付き承認)

本Draft の位置づけを明示する:

- **v0.3_DRAFT は新しい正本ではない。** 正本は引き続き v0.1 である。
- v0.1 / v0.2 いずれの原本も改変・削除・置換しない。
- Observation Candidates は「Not Yet Verified」状態を維持し、Fact に昇格させない。
- v0.1系仮説体系 (H1〜H5, Cause Location Model) と v0.2系仮説体系 (H1〜H4, Process Path Model) の番号統合は行わない。
- Human Gate判断領域の先行決定は行わない。統合の採否・正本差替えの要否は Human Gate に委任する。
- 本文書に基づくコード変更・timeout値変更・Core System File変更・DB構造変更・commit/push・Decision Ledger追加はいずれも行わない。

---

# Part I — v0.1 母体保持部 (§1〜§16)

**Source: `TODO_437_R02_REMEDIATION_PLAN_v0.1.md` (正本)**

本Part I は v0.1 の内容を保持したものである。§13 の Boundary 4 に v0.2 由来の Supporting Evidence Requirement を追記した以外、v0.1本文からの記述変更は行っていない。

## 1. 現象の整理

- `/agent/mocka_write_event`のE2Eレイテンシは実測で一貫して約5.8〜6.1秒(2026-07-10、
  5回連続計測。5.73/5.74/5.99/5.85/6.14秒等、常時であり間欠的ではない)。
- 内訳計測の結果: GATE(`/api/gate/event`)単体は5回連続で2.27〜2.33秒。
  `WorkingContext.live_update`/`emit_event_to_context_runtime`/`maybe_snapshot`の
  3関数は個別実行で合計約0.03秒。
- GATE単体(約2.3秒)+3関数(約0.03秒)の合計(約2.33秒)と、E2E全体(約6.0秒)の間に
  **約3.7秒の未説明の差**が残っている。
- 表現の精緻化(2026-07-10追記): この約3.7秒の**差分の存在自体は実測により確定
  している**(誤: 「未説明時間約3.7秒が存在する可能性」/正: 「実測により確認
  された未説明差分約3.7秒」)。未確定なのは差分の存在ではなく、その**原因**である。
  原因候補は11章のH1〜H4に対応する: (i)threaded=True未設定による直列化(H3)、
  (ii)MCP側の同期処理(process_event呼び出し前後・auto_log()等、H1関連)、
  (iii)SQLite書き込みのcommit構造(events/event_signatures等の複数commit、
  H1/H2関連)、(iv)SQLiteのlock/busy待機(H2)。単一原因とは限らず、複合の
  可能性を排除しない。
- 影響: timeout=3で呼ぶ既知の呼び出し元10箇所で、構造的に記録失敗(タイムアウト→
  fallback/例外)が発生していた可能性が高い(TODO_437 note参照)。
- 未確定事項: (a)GATE側2.3秒の真因、(b)E2Eとの差3.7秒の真因。
  DC_20260710_003が前提としていた「GATE高速・WorkingContext側が遅延源」という
  仮説は、DC_20260710_005にて実測により否定済み。

## 2. 暫定対策の整理(実施済み、DC_20260710_005・commit 3755c107f/e7a779a4c)

- timeout=3→12統一(呼び出し元10箇所)。**恒久対策ではない**。記録失敗の発生可能性を
  下げる効果はあるが、レイテンシそのものは未解消。
- ロールバック: 各ファイルのtimeout値を3に戻すのみ(git revertまたは個別Edit)。
  低リスク・即時実施可能。

## 3. 根本原因調査計画(実装なし、調査・計測のみ)

以下の仮説を、互いに独立した形で個別に検証する。いずれも本番プロセスへの
書き込み変更・再起動を伴わない手法を優先する。

### 3.1 GATE内部処理(`/api/gate/event`)の内訳計測

- 対象: `phi_os/event_gate.py`の`process_event()`(`validate`/`_next_event_id`/
  `_write`/`sign_event`/`commit`)。
- 手法: 各サブステップの前後に一時的な計測コード(`time.perf_counter()`)を挿入して
  実行するか、`py-spy dump --pid <pid>`等、対象プロセスを止めずに済むサンプリング
  プロファイラで計測する。
- 成功条件: 約2.3秒の内訳が、どのサブステップに帰属するかが定量的に判明すること。

### 3.2 events.dbロック競合

- 対象: `data/mocka_events.db`(WALモード、`busy_timeout=5000ms`)。
- 手法: WALファイルサイズの推移監視、`PRAGMA wal_checkpoint`頻度確認、同時書き込み
  プロセス数の実地棚卸し(essence_auto_updater/PostToolUseフック/他セッション等の
  書き込み頻度をログから集計)。可能であればSQLiteの`trace`/`profile`コールバックで
  ロック待ち時間を直接計測する。
- 成功条件: 2.3秒のうちロック待ちが占める割合が定量化されること。書き込み集中時間帯と
  レイテンシの相関が確認または否定されること。

### 3.3 `mocka_mcp_server.py`のthreaded化の効果

- 対象: `mocka_mcp_server.py`の`app.run(host="0.0.0.0", port=5002, debug=False)`
  (`threaded`未指定=単一リクエスト直列処理の可能性)。
- 手法: 本番サーバーとは別プロセス・別ポートで一時起動する複製環境で
  `threaded=True`を設定し、同条件でE2Eレイテンシを再計測して比較する。
  **本番サーバーは本調査では再起動しない**。
- 成功条件: `threaded=True`環境下でE2Eレイテンシが有意に短縮するか、または
  変化しないかが実測で判明すること。変化しない場合は直列処理待ちが原因ではないと
  確定できる。

### 3.4 I/O待ち(ディスク/ネットワーク)

- 対象: `working_context_latest.json`/`event_runtime_log.json`/
  `scheduler_state.json`への読み書き、およびGATEへのHTTP round-trip。
- 手法: 3.1のプロファイリングと統合実施し、I/O待ち区間を分離抽出する。
- 成功条件: I/O待ちが支配的要因かどうかが判明すること。

### 3.5 クライアント共通化・非同期化による改善余地の評価(設計検討のみ)

- 対象: timeout=3→12にした10箇所+`mocka_git_safe_commit.py`の計11呼び出し元。
- 手法: 各呼び出し元の実装を比較し、共通クライアントヘルパー(timeout値・リトライ・
  fallbackログの一元化)への集約が技術的に可能かを設計レベルで検討する。
  非同期化(fire-and-forgetをスレッド/キューへ逃がす)については、既存の
  「呼び出し元をブロックしない」設計方針(fallbackログ方式)との整合性を確認する。
- 成功条件: 共通化・非同期化のいずれかまたは両方が実装可能な設計として
  具体化されること(このフェーズでは実装しない)。

## 4. 恒久対策候補(仮説ベース。3の調査結果により絞り込む)

- 候補A: GATE内部処理の最適化(3.1で特定されたボトルネックへの個別最適化)
- 候補B: events.db書き込み経路の見直し(接続プーリング、専用ライタースレッド/
  キューへの一本化等、3.2の結果次第)
- 候補C: `mocka_mcp_server.py`の`threaded=True`化(3.3の結果が支持する場合のみ)
- 候補D: 呼び出し元の非同期化(fire-and-forgetをバックグラウンドキュー化)
- 候補E: 共通クライアントヘルパーへの集約(TODO_364のgit経路集約と同型の設計)

優先順位・組み合わせの決定は、3章の調査結果が出た後にHuman Gateで判断する。
本文書の時点ではいずれも未採用の候補として並列に列挙するに留める。

## 5. 計測項目

- E2Eレイテンシ(`/agent/mocka_write_event`、5回以上の連続計測、平均・最大・最小)
- GATE単体レイテンシ(`/api/gate/event`直接、同条件)
- `WorkingContext`/`ContextRuntime`3関数の個別実行時間
- events.db WALファイルサイズ・チェックポイント頻度
- 同時書き込みプロセス数(推定、ログベース)
- (threaded=True検証時)同一負荷条件下でのレイテンシ比較

## 6. 回帰試験計画

- 恒久対策実装後、TODO_437の暫定対策検証と同一手順(`tools/mocka_auto_record.py`の
  `_post()`を実importし、3回以上連続POST)で再計測する。
- 既存呼び出し元10箇所+`mocka_git_safe_commit.py`について、fallbackログ
  (`governance/mocka_git_safe_commit_ledger_fallback.log`等)に新規のOFFLINE記録が
  発生していないことを一定期間(最低24時間)観察する。
- 実装前後で`verify_all.py` = ALL CHECKS PASSEDを確認する。

## 7. 完了判定基準(TODO_437 Permanent Fix完了の定義)

以下すべてを満たした時点でPermanent Fixを完了とし、Human Gate承認を得て
TODO_437をCloseする。

(a) GATE単体レイテンシ・E2Eレイテンシの内訳(3.1〜3.4)が定量的に説明されている
    (未説明の差が残っていない)。
(b) 恒久対策実装後、E2Eレイテンシが明確に改善している(具体的な数値目標はHuman Gateで
    確定する。本文書での暫定目標例: 1秒未満)。
(c) 24時間以上の観察期間でfallbackログへの新規記録が発生していない。
(d) 既存timeout=12設定を維持したままでも、実測latencyに対して十分な安全マージン
    (目安3倍以上)が確保されている。
(e) `verify_all.py` = ALL CHECKS PASSED。

## 8. ロールバック方針

- 各恒久対策候補(4章)は、実装前に対象ファイルの現状(commit `e7a779a4c`時点)を
  revert基点として記録する。
- threaded=True化: 単一パラメータの変更のため、`app.run()`の該当行をrevertする
  のみで戻せる。ただし本番サーバープロセスの再起動を伴うため、revert時も
  再起動が必要。
- events.db書き込み経路の変更: 変更前に`mocka_events.db`のバックアップ(既存の
  `mocka_events.db.bak_*`と同じ命名規則)を取得してから着手する。
- 共通クライアントヘルパー集約: 呼び出し元は無改修(TODO_413と同型の設計)とすることで、
  ヘルパー実装のみのrevertで済む設計とする。
- いずれの対策も、異常検知時はtimeout=12の暫定対策状態(現状)へ即座に戻せることを
  実装方針の前提とする。

## 9. Human Gateが必要となる判断点

1. 3.1〜3.4の調査手法(特に`mocka_mcp_server.py`複製環境での`threaded=True`比較検証)を
   実施してよいか。
2. 4章の恒久対策候補のうち、どれを採用するか(3の調査結果を踏まえた選定)。
3. `mocka_mcp_server.py`(本番プロセス)の再起動を伴う変更(threaded=True採用時)の
   実施タイミング。
4. events.db書き込み経路の構造変更(候補B)を採用する場合、その設計の承認。
5. 7章の完了判定基準(特に数値目標)の最終確定。
6. TODO_437の最終Close判断。

## 10. 実施していないことの明示

本文書はR02 Remediation Planの設計書であり、いかなるコード変更・timeout値の
追加変更・Core System Fileの変更も行っていない。TODO_438
(execution_governance.py統合)にも一切触れていない。

## 11. 仮説マトリクス (Cause Location Model, H1〜H5)

3章の各仮説について、確認方法・成功条件(仮説が支持される条件)・
否定条件(仮説が否定される条件)を一覧化する。既存の3.1〜3.5の内容は変更せず、
本表はその要約として追記するものである。

本マトリクスは **原因の所在 (Cause Location) 観点** による仮説体系であり、
§17.1 の v0.2系仮説 (Process Path Model) とは異なる観点である。両者の対応関係は
§17.2 の Mapping Table を参照。

| 仮説ID | 仮説内容 | 対応節 | 確認方法 | 成功条件(支持) | 否定条件(反証) |
|---|---|---|---|---|---|
| H1 | GATE単体2.3秒の主要因はprocess_event()内の特定サブステップ(validate/_next_event_id/_write/sign_event/commit)にある | 3.1 | サブステップ別time.perf_counter計測、またはpy-spy等の非侵襲サンプリング | いずれか1つのサブステップが2.3秒の大半(目安80%以上)を占めることが定量的に確認される | 全サブステップの合計が2.3秒に遠く及ばない(目安0.5秒未満)、または特定サブステップに偏らず均等に分散している |
| H2 | GATE単体2.3秒の主要因はmocka_events.dbへの書き込みロック待ちである | 3.2 | WALファイルサイズ推移監視、同時書き込みプロセス数の実地棚卸し、SQLite trace/profileコールバックによるロック待ち時間計測 | ロック待ち時間が2.3秒のうち有意な割合(目安50%以上)を占め、書き込み集中時間帯とレイテンシに相関が見られる | ロック待ち時間が無視できる水準(目安10%未満)、または書き込み集中度とレイテンシに相関が見られない |
| H3 | E2Eとの差3.7秒の主要因はmocka_mcp_server.pyの単一スレッド直列処理によるキュー待ちである | 3.3 | 本番とは別プロセス・別ポートの複製環境でthreaded=Trueを設定し、同条件でE2Eレイテンシを比較計測 | threaded=True環境でE2Eレイテンシが有意に短縮する(目安30%以上の短縮) | threaded=True環境でもレイテンシがほぼ変化しない(目安10%未満の変化) |
| H4 | 2.3秒または3.7秒の一部はディスク/ネットワークI/O待ちによるものである | 3.4 | H1のプロファイリング結果からI/O待ち区間を分離抽出(独立計測は行わない) | I/O待ちが計測区間の中で明確に識別可能な時間を占める | I/O待ちがCPU処理時間に比べ無視できる水準 |
| H5 | 既存11呼び出し元の実装は、共通ヘルパーへの集約・非同期化が技術的に可能な構造である | 3.5 | 既存11呼び出し元の実装比較、非同期化と既存fallback方針(呼び出し元をブロックしない設計)との整合性の設計検討(計測ではない) | 共通化・非同期化のいずれかが具体的な設計として成立する | 呼び出し元ごとの要件差異が大きく、共通化のコストが利益を上回ると判断される |

注記: H1〜H4は互いに排他的ではない(複数が同時に真である可能性がある)。
H5は性能仮説ではなく設計可能性の検討であり、成功/否定条件は「採否」ではなく
「具体化できるか」で判定する。

## 12. 恒久対策候補A〜E比較基準

4章で列挙した候補A〜Eについて、採用判断に用いる比較基準を一覧化する。
既存の4章の内容は変更せず、本表はその判断材料として追記するものである。

| 候補 | 前提となる仮説 | 想定効果 | 実装コスト(目安) | リスク(目安) | 本番再起動要否 | 採用の判断根拠となる調査結果 |
|---|---|---|---|---|---|---|
| A: GATE内部処理の最適化 | H1 | ボトルネックサブステップへの個別最適化によるGATE単体レイテンシ短縮 | 低〜中 | 低(局所変更) | 要(app.py側プロセス) | H1が支持されること |
| B: events.db書き込み経路の見直し | H2 | ロック競合解消によるGATE単体レイテンシ短縮 | 中〜高(接続プーリング/専用ライター設計) | 中(データ整合性への影響が大きいため慎重な設計・検証が必要) | 要 | H2が支持されること |
| C: mocka_mcp_server.pyのthreaded=True化 | H3 | リクエスト直列化待ちの解消によるE2Eレイテンシ短縮 | 低(1パラメータ変更) | 中(並行処理化に伴うスレッドセーフ性の再検証が必要、特にSQLite接続・グローバル状態の扱い) | 要(mocka_mcp_server.py) | H3が支持されること |
| D: 呼び出し元の非同期化 | 汎用(H1〜H4いずれの結果でも有効な緩和策) | 呼び出し元のブロック時間を実質ゼロ化 | 中(11呼び出し元それぞれの対応) | 低〜中(既存fallback方針との整合性の確認が必要) | 呼び出し元プロセスの再起動要(GATE/mcp_server自体は不要) | H1〜H4のいずれの結果が出ても、他候補と並行して採用可能 |
| E: 共通クライアントヘルパーへの集約 | 汎用 | 将来のtimeout値変更等を1箇所に集約、保守性向上(レイテンシ自体の短縮効果はない) | 中 | 低(呼び出し元無改修、TODO_413と同型設計) | 呼び出し元プロセスの再起動要 | 性能改善候補(A/B/C)とは独立の観点(保守性)で採用可能 |

注記: A/B/Cは互いに排他ではなく、H1・H2・H3が複数支持された場合は組み合わせ採用も
あり得る。D/Eは性能改善候補ではなく緩和・保守性の観点であり、A/B/Cのいずれと
組み合わせても矛盾しない設計とする。

### 12.1 条件付き対応表

上表の「前提となる仮説」列は1対1の確定対応ではなく、以下の条件付き関係として
読むべきものであることを明示する(12章の表自体は変更しない)。

| 条件 | 結果 |
|---|---|
| H1(GATE単体2.3秒の主要因がprocess_event()内サブステップにある)が確認された場合 | 候補A(GATE内部処理の最適化)の有効性が高まる |
| H2(GATE単体2.3秒の主要因がevents.dbへの書き込みロック待ちである)が確認された場合 | 候補B(events.db書き込み経路の見直し)の有効性が高まる |
| H3(E2Eとの差3.7秒の主要因がmocka_mcp_server.pyの単一スレッド直列処理である)が確認された場合 | 候補C(threaded=True化)の有効性が高まる |
| H4(2.3秒または3.7秒の一部がI/O待ちである)が確認された場合 | 候補A・候補C双方の優先度評価に影響する(I/O待ちの内訳次第でどちらの候補がより有効かが変わる) |
| いずれの仮説が確認されても(排他ではない) | 候補D(非同期化)・候補E(共通クライアントヘルパー集約)は独立に有効性を保つ(汎用的な緩和・保守性改善のため) |

注記: 上記は「H_xが確認された場合、対応候補の有効性(採用の合理性)が高まる」という
条件付き関係であり、「H_xが確認されなければ対応候補が無効になる」という否定的な
意味ではない。複数の仮説が同時に真である場合、複数候補の組み合わせ採用も
排除しない。

## 13. Human Gate判断境界の明示

9章の判断点を、実施フェーズの境界として明示的に整理する。各境界を越える前に、
必ずHuman Gate承認を得ること。

| # | 判断境界 | 境界の内容 | 越えた先で行うこと |
|---|---|---|---|
| 1 | 調査実施承認 | 3章の根本原因調査計画(3.1〜3.5)を開始してよいかの承認 | 調査の着手(計測・比較・設計検討) |
| 2 | 計測コード追加承認 | 3.1(GATE内部処理の内訳計測)で、一時的な計測コード(time.perf_counter等)をprocess_event()等の対象コードへ挿入してよいかの承認。py-spy等の非侵襲サンプリングのみで完結する場合は本境界を経由しない | 対象コードへの一時的な計測コード挿入・実行・除去 |
| 3 | threaded=True検証承認 | 3.3で、本番とは別プロセス・別ポートの複製環境を用意し、threaded=Trueでの比較検証を行ってよいかの承認 | 複製環境の構築・比較計測の実施 |
| 4 | 恒久対策候補選択承認 | 3章の調査結果を踏まえ、4章/12章の候補A〜Eのうちどれを採用するか(組み合わせ含む)の選定承認 | 選定された候補の実装設計(詳細設計)への着手 |
| 5 | 本番変更承認 | 選定された候補の実装を、本番環境(mocka_mcp_server.py本体・app.py本体・events.db本体)へ適用してよいかの承認。mocka_mcp_server.py本体の再起動を伴う変更は必ずこの境界を経由する | 本番コードへの変更・commit・再起動を伴う適用 |
| 6 | TODO_437 Close判断 | 7章の完了判定基準(a)〜(e)を満たしたことを確認した上で、TODO_437をPermanent Fix完了としてCloseしてよいかの判断 | TODO_437のstatus変更(進行中→完了)・Decision Ledgerへの完了記録 |

いずれの境界も、Human Gate承認を得るまでは次のフェーズへ進まない。特に境界2
(計測コード追加)は、たとえ一時的・除去前提のコードであっても対象が本番稼働中の
プロセスに影響しうるため、py-spy等の非侵襲手法で完結できない場合は独立した
承認事項として扱う。

### 13.1 Boundary 4: Supporting Evidence Requirement

**Source: `TODO_437_R02_REMEDIATION_PLAN_v0.2.md` §13 (v0.2 Boundary 7 を Boundary 4 の下位要件として再配置。R01裁定に基づく)**

Boundary 4 (恒久対策候補選択承認) を成立させるための承認資料要件を、以下に明示する。本項は独立した新規判断境界ではなく、Boundary 4 の判断成立条件 (Evidence Requirement Extension) として扱う。

恒久対策候補を選択する場合、承認資料には以下を含める。

- Root Cause確定前の実装開始は禁止
- 複数候補から採用案を選択する場合、Human Gate承認を取得する
- 第14章計測結果を根拠として提示する
- 候補ごとの期待効果を提示する
- 副作用・既存経路への影響を提示する
- ロールバック方針を提示する

注記: 本要件は Boundary 4 を消滅させたり置換したりするものではない。Boundary 4 (判断境界そのもの) と 13.1 (判断成立条件) の分離整理である。

## 14. 計測項目の補足

5章の計測項目には、11章の仮説マトリクスで要求される粒度の項目が一部不足していたため、
以下を追加する(5章の既存項目は変更しない)。

- H1(GATE内部処理内訳)用: `process_event()`内サブステップ別実行時間
  (`validate`/`_next_event_id`/`_write`/`sign_event`/`commit`の内訳、それぞれの
  実行時間とGATE単体レイテンシに占める割合)。
- H2(events.dbロック競合)用: SQLite書き込みロック待ち時間そのもの
  (trace/profileコールバックによる直接計測値)。WALファイルサイズ・チェックポイント
  頻度は間接指標であり、ロック待ち時間の直接計測とは区別する。

## 15. 整合性確認結果

Human Gate提出前の最終整合確認を実施した結果を記録する。

- 1〜13章の章構成整合: 章番号の欠落・重複なし。OK。
- 仮説マトリクス(11章)と調査項目一覧(5章)の一致: 一部不一致を発見(H1のサブステップ
  別内訳、H2のロック待ち時間そのものが5章に未記載)。14章で計測項目を補足することで
  解消済み。
- 恒久対策候補A〜E(4章/12章)とHuman Gate判断境界(13章)の一致: 候補選択は境界4
  (恒久対策候補選択承認)で一致。本番適用(A/B/C/D/Eいずれも)は境界5(本番変更承認)で
  一致。OK。
- 完了判定基準(7章)とTODO_437 Close条件(13章境界6)の一致: 境界6は7章(a)〜(e)を
  明示的に参照しており一致。ただし9章項目5(完了判定基準の数値目標確定)は13章の
  6境界のいずれにも独立項目として明示されていなかった。これは境界6(TODO_437
  Close判断)に先立って行われるべき判断であり、数値目標が未確定のままでは境界6の
  判定基準(a)〜(e)自体が確定できないため、境界6に内包されるものとして扱う。独立の
  境界としては追加しないが、対応関係をここに明記する。
- ロールバック方針(8章)と変更境界(13章境界5)の一致: 8章のロールバック手順は
  いずれも境界5(本番変更承認)を経由した実装後を前提としており、矛盾なし。OK。

以上により、軽微な不一致1件(計測項目の粒度不足)を14章で解消した。他の確認項目は
いずれも一致を確認した。

## 16. 制度的文脈の保持確認

v0.2(Parallel Investigation Draft)の内容をv0.1へ統合する作業は現時点で
行っていない(現状維持)。ただし、将来Human Gate承認を経て統合作業を行う際に、
以下の制度的文脈が欠落しないことを事前に確認事項として記録する。

- R01監査による条件付き承認(「継続調査完了までは暫定対策完了・恒久対策未完了と
  扱うことを維持すべき」、event_id: `E20260710_7368241085333`)。
- Decision `DC_20260710_005`(DC_20260710_003の原因仮説を実測により否定、
  timeout=12統一を暫定対策として採用、根本原因は未確定、継続調査を行う)。
  `DC_20260710_003`自体は書き換えず、追記記録として扱う原則(append-only)を
  維持する。

現時点でこれらはv0.1本文(1章・2章)および`TODO_437_R02_REVIEW_SUMMARY_v0.1.md`の
Background/Confirmed Decisionsに明記済みであることを確認した。今後v0.2の内容を
統合する場合も、この制度的文脈を欠落させないことを統合作業の前提条件とする。

**注 (v0.3_DRAFT 追記):** 本 v0.3_DRAFT は、v0.2 の内容を「§17 Root Cause Investigation Update」および「§18 Observation Candidates」として **参照統合** したものである。v0.1 本文自体を書き換えたものではなく、v0.1 は正本として現状維持である。

---

# Part II — v0.2 / Observation Candidates / Parallel Draft Audit 統合部 (§17〜§19)

**Sources:**
- `TODO_437_R02_REMEDIATION_PLAN_v0.2.md` (§17)
- `TODO_437_R02_OBSERVATION_CANDIDATES_v0.1.md` (§18)
- `TODO_437_R02_PARALLEL_DRAFT_AUDIT_v0.1.md` (§17.3)

## 17. Root Cause Investigation Update (Process Path Model)

**Source: `TODO_437_R02_REMEDIATION_PLAN_v0.2.md` §14 + Parallel Draft Audit Content Review**

本章は、v0.2 (Parallel Investigation Draft) で提示された仮説体系を、v0.1 (Cause Location Model) と並列に保持するために設けた統合章である。両者は同一現象に対する異なる観測粒度・観点による仮説であり、統合Draftではこれを **番号統合せず二層並列** で扱う。

### 17.0 v0.2 における確定した否定事項および証拠一覧の位置づけ

v0.2 §14 では以下が確定した否定事項として記述されている:

- 「GATE高速・WorkingContext遅延」という仮説は実測により否定された。
- Context更新処理は約0.03秒であり、支配的な遅延ではない。

上記は v0.1 §1 (現象の整理) および DC_20260710_005 と整合する内容であり、v0.3_DRAFT 全体を通じた確定事項として扱う。

一方、v0.2 §14 では「証拠一覧」として以下の項目が列挙されているが、そのうち v0.1 側で独立検証されていない項目 (DBサイズ・events件数・claude_sessions件数・WAL・busy_timeout との時間相関) については、Observation Candidates §2.1 が「未検証」と明示分類している。したがって v0.3_DRAFT では、これらを **Fact ではなく Observation Candidate として §18 に格納** する (§18.1 参照)。

v0.1 が既に独立に実測している以下の項目のみ、本 v0.3_DRAFT において Fact として扱う:

- E2E latency: 5.73〜6.14秒
- GATE latency: 2.27〜2.33秒
- Context処理 (3関数合計): 約0.03秒
- 未説明時間: 約3.7秒 (差分の存在は確定、原因は未確定)

### 17.1 v0.2系 現在の有力仮説 (Process Path Model, H1〜H4)

**Source: `TODO_437_R02_REMEDIATION_PLAN_v0.2.md` §14 (原文の趣旨を保持)**

本節の H1〜H4 は **処理経路上のどこで時間が消費されるか** を分類する観点である。v0.1 §11 の H1〜H5 (Cause Location Model, 原因の所在) とは異なる観点であり、番号は独立体系として扱う。両者の対応関係は §17.2 の Mapping Table を参照。

#### v0.2 H1: MCP同期処理経路内の未説明区間

対象は `agent_call()`、`execute_tool()`、`mocka_write_event` 分岐、HTTP前後処理、`auto_log()`、response 生成である。E2E と GATE 単体の差約3.7秒を、相関IDを用いた開始・終了時刻で分解する。

注: v0.2 H1 は GATE **外部** (MCP経路) を対象とする。これは v0.1 H1 (GATE **内部** の process_event() サブステップ) とは対象領域が異なる。

#### v0.2 H2: SQLite同期commit構造

対象は events INSERT、event_signatures INSERT、events UPDATE、claude_sessions INSERT、および複数commit である。正常経路では GATE の events 系トランザクション後に MCP の `auto_log()` が同一SQLiteへ別commit するため、各SQL と commit を個別に計測する。

注: `auto_log()` による claude_sessions INSERT の別commit 構造は Observation Candidates §2.2 で未検証扱いとされている論点であり、本 §17.1 では v0.2 が提示した仮説内容の記録として掲載する。実測による検証は Boundary 1 (調査実施承認) 後の作業とする。

#### v0.2 H3: SQLite lock/busy 待機

`busy_timeout=5000ms` との時間相関を確認する。現時点では lock/busy 待機時間の直接実測はなく、根本原因としては未確認である。

#### v0.2 H4: threaded 未指定による直列化

MCPサーバーの `threaded` は未指定である。複製環境・別ポートでの比較計測後にのみ、直列化を原因候補として採否判断する。

### 17.2 Mapping Table (v0.1 H1〜H5 ↔ v0.2 H1〜H4)

**Note (R01裁定):**
本表は異なる調査観点間の概念的対応を示すものであり、仮説番号間の1対1対応を意味しない。

*The mapping below represents conceptual correspondence between different investigation perspectives. It does not represent direct one-to-one equivalence.*

| v0.1 番号 (Cause Location Model) | v0.2 番号 (Process Path Model) | 対応の性質 |
|---|---|---|
| v0.1 H1 (GATE内 process_event() サブステップ) | v0.2 H1 に対応なし (v0.2 H1 は GATE **外部** のMCP経路を対象) | **切り口が異なる。補完関係** — v0.1はGATE内部、v0.2はGATE外部を分解する観点 |
| v0.1 H2 (events.db ロック待ち) | v0.2 H2 (SQLite同期commit構造) および v0.2 H3 (lock/busy待機) の双方に部分的対応 | **粒度差** — v0.1 H2 は「ロック待ち時間」に集約、v0.2 は「commit構造」と「lock/busy待機」を分離 |
| v0.1 H3 (mocka_mcp_server.py 単一スレッド直列処理) | v0.2 H4 (threaded 未指定による直列化) | **概念的にほぼ同等** — 両者とも同一の技術要因を指すが、番号が異なる |
| v0.1 H4 (ディスク/ネットワーク I/O 待ち) | v0.2 に対応なし | **v0.1 固有の観点** — I/O 待ちを独立仮説として立てる観点は v0.2 では明示されていない |
| v0.1 H5 (共通ヘルパー集約可能性、設計仮説) | v0.2 に対応なし | **v0.1 固有の観点** — v0.2 は性能仮説のみを扱い、設計可能性の仮説は含まない |
| v0.1 に対応なし | v0.2 H1 (MCP経路内の未説明区間 agent_call/execute_tool/auto_log等) | **v0.2 固有の観点** — GATE呼び出し前後の MCP経路を分解する観点は v0.1 に明示的には含まれない |
| v0.1 に対応なし | v0.2 H2 の「auto_log() による claude_sessions への別commit」 | **v0.2 固有の観点、かつ未検証** (§18.2 参照) |

注記: 対応表自体を新しい分類体系として運用してはならない (R01裁定)。あくまで v0.1 と v0.2 の両者を独立に保持したうえで、参照上の対応を示すためのものである。

### 17.3 Parallel Draft Audit Summary

**Source: `TODO_437_R02_PARALLEL_DRAFT_AUDIT_v0.1.md` (要約、R01裁定に基づき3〜5行の技術文脈限定要約)**

本調査では、v0.1 母体Draft とは別経路で生成された v0.2 並行Draft の存在を確認した。並行Draft は正本ではなく、Human Gate 未承認の補完調査資料として扱う。統合Draft では、追加された技術的観測事項および未検証候補のみを対応する章へ分類配置する。並行Draft 生成経緯の詳細 (発見日時・作成者表記・Git状態・Classification 等) は `TODO_437_R02_PARALLEL_DRAFT_AUDIT_v0.1.md` 本文に保持されており、本要約はその要点のみを制度文脈として保持するものである。

## 18. Observation Candidates (Not Yet Verified)

**Source: `TODO_437_R02_OBSERVATION_CANDIDATES_v0.1.md`**

本章は、v0.2 (Parallel Investigation Draft) 固有の追加情報のうち、v0.1 側で独立検証を行っていない項目を **Observation Candidate (未検証)** として整理したものである。

**分類原則 (R01裁定):**
- 本章の全項目は `[Observed Data Candidate — Status: Not Yet Verified]` として扱う。
- Fact への昇格は Boundary 1 (調査実施承認) 後の検証作業を経てからのみ行う。
- 統合Draft は本項目群を Fact として扱ってはならない。

### 18.1 Observed Data Candidates

以下のデータ点は v0.2 §14 「証拠一覧」に記載されているが、v0.1 側で独立検証していない項目である。

| 項目 | v0.2 記載値 | Status |
|---|---|---|
| DBサイズ (mocka_events.db) | 82,026,496 bytes | **Not Yet Verified** |
| events 件数 | 15,312 | **Not Yet Verified** |
| claude_sessions 件数 | 94,408 | **Not Yet Verified** |
| WAL | 有効 (と記載) | **Not Yet Verified** (v0.1 側の WAL 確認は別時点・別手段によるものであり、この値そのものの再現確認は行っていない) |
| busy_timeout | 5000ms (と記載) | **Not Yet Verified** (v0.1 側も同値を別途確認済みだが、v0.2 記載値そのものとしては未検証扱い) |

### 18.2 auto_log() 別commit 構造仮説

**Status: Not Yet Verified**

- 内容: GATE (`/api/gate/event`) 側の `events` INSERT・`event_signatures` INSERT・`events` UPDATE に加え、mocka_mcp_server.py 側の `auto_log()` が同一SQLite (`mocka_events.db` と想定) へ **別途 `claude_sessions` テーブルへ INSERT し、別commit を発生させている** との指摘。
- 位置づけ: 未説明の約3.7秒 (GATE単体2.3秒 + Context 3関数0.03秒 と E2E全体6.0秒の差) の新しい候補要因となり得る。v0.1 の H1 (process_event() 内サブステップ)・H2 (events.db ロック競合) のいずれにも、`auto_log()` の別commit 構造という着眼点は明示的に含まれていなかった。
- 検証状態: 未検証。`auto_log()` の実装 (`mocka_mcp_server.py` 内) が実際に別途 commit を発生させているか、それがどのDBファイルに対してか (`mocka_events.db` か `claude_sessions` 用の別ファイルか) を含め、コード確認・実測のいずれも v0.1 側では行っていない。

### 18.3 Legacy Path Risk

**Status: Not Yet Verified**

- 内容: 正規経路は `data/mocka_events.db` であるところ、`interface/router.py` に旧 `data/events.db` への直接書込み実装が残存しているとの指摘。
- 位置づけ: 恒久対策候補B (events.db 書き込み経路の見直し) を検討する際、正規経路と旧経路を混同しないための前提情報になり得る。R02 で DB経路を変更する場合、正規経路と旧経路を混同しない。旧経路の扱いを含む変更は、影響分析および Human Gate 承認の対象とする。
- 検証状態: 未検証。`interface/router.py` の該当箇所の存在・現状の呼び出され方 (実際に稼働経路として使われているか、死んだコードか) のいずれも、v0.1 側ではコード確認を行っていない。

## 19. 版管理注記

### 19.1 v0.3_DRAFT の位置づけ

- 本文書は **Draft Only** である。**新しい正本ではない。**
- 正本は引き続き `TODO_437_R02_REMEDIATION_PLAN_v0.1.md` である。
- 本文書は、v0.1 母体を保持したうえで、v0.2 / Observation Candidates / Parallel Draft Audit の内容を参照統合した Human Gate 提出用Draft である。

### 19.2 統合方針の要点

- **v0.1 / v0.2 いずれの原本も改変・削除・置換していない。** 両ファイルは現状のまま保持する。
- **v0.1 H1〜H5 (Cause Location Model) と v0.2 H1〜H4 (Process Path Model) の番号統合は行わない。** 両者を §11 と §17.1 に独立に保持し、対応関係のみを §17.2 の Mapping Table で示す。
- **Observation Candidates の Fact 昇格は行わない。** §18 の全項目は `Not Yet Verified` を維持する。
- **v0.2 Boundary 7 は独立境界化しない。** §13.1 の Boundary 4 Supporting Evidence Requirement として Boundary 4 の下位要件に格納する。
- **並行生成経緯の記載は制度文脈保持に限定する。** §17.3 は 3〜5行程度の技術要約とし、責任追及・誤発注議論・個別生成主体評価は含めない。詳細は Parallel Draft Audit 原本に保持する。

### 19.3 Human Gate 判断委任事項

以下は本 v0.3_DRAFT の中で **決定しない**。全て Human Gate に委任する。

- v0.3_DRAFT を新しい正本として採用するか、v0.1 を正本として維持するか。
- v0.2 の内容を v0.1 に追記統合するか、v0.2 を Parallel Draft のまま保持するか。
- Observation Candidates (§18) の各項目を検証するか、そのタイミング。
- 恒久対策候補 A〜E のいずれを採用するか (Boundary 4)。
- 数値目標 (§7 (b)) の確定 (Boundary 6 に内包)。

### 19.4 制約遵守の確認 (本 Draft 作成時点)

- コード変更: 行っていない
- timeout 値変更: 行っていない
- Core System File 変更: 行っていない
- DB 構造変更: 行っていない
- git commit / push: 行っていない
- Decision Ledger 追加: 行っていない
- v0.1 / v0.2 原本改変: 行っていない
- Observation Candidate の Fact 昇格: 行っていない
- H 番号体系統合: 行っていない
- Human Gate 判断領域の先行決定: 行っていない

### 19.5 参照ソース一覧

| Source | 統合Draft内での参照範囲 |
|---|---|
| `TODO_437_R02_REMEDIATION_PLAN_v0.1.md` | §1〜§16 全体 (母体)、§13.1 に v0.2 由来の補足を追記 |
| `TODO_437_R02_REMEDIATION_PLAN_v0.2.md` | §13.1 (Boundary 4 Supporting Evidence Requirement)、§17.0〜§17.1、§18.1 |
| `TODO_437_R02_OBSERVATION_CANDIDATES_v0.1.md` | §18 全体 |
| `TODO_437_R02_PARALLEL_DRAFT_AUDIT_v0.1.md` | §17.3 (要約) |
| `DC_20260710_005` | §1、§2、§16 で参照 |
| R01監査 `E20260710_7368241085333` | §16 で参照 |

---

**End of TODO_437 R02 Remediation Plan v0.3 DRAFT**
