# MoCKA MCPツール17個の実体確認 — Fact Collection v0.1

位置づけ: 博士指示「MoCKA MCPツール17個の実体確認」への対応。役割は制度書記官・実装調整官、事実収集のみ。推測・階層モデル化・分類の提案は行わない。対象ファイルは`C:\Users\sirok\MoCKA\mocka_mcp_server.py`(777行、直接読了済み)。関連ファイルとして`deploy\mocka_mcp_server_vps.py`(381行)の存在も確認した。

## 前提事実(2ファイルの関係、および稼働中実体の確認)

- `mocka_mcp_server.py`(リポジトリルート直下)と`deploy\mocka_mcp_server_vps.py`は別ファイルである(Globで確認済み)。
- Windows上でポート5002をLISTENしているプロセス(PID 3372、`python3.13.exe`、開始時刻2026-07-04T07:12:12)のコマンドラインは`python -X utf8 mocka_mcp_server.py`であることを`Get-CimInstance Win32_Process`で確認した。現在稼働中の実体はリポジトリルート直下の`mocka_mcp_server.py`であり、`deploy\mocka_mcp_server_vps.py`ではない。
- `deploy\mocka_mcp_server_vps.py`のgit最終コミットは`640f35eba`(2026-06-01T06:32:21+09:00)で、以降の更新は確認されなかった。一方`mocka_mcp_server.py`(ルート)は`abeecb32b`(2026-07-01T14:09:14+09:00)まで更新が続いている。

以下、17ツールすべて`mocka_mcp_server.py`(ルート、稼働中の実体)についての事実。TOOLS配列(246-262行)の定義順に記載する。

---

```
[mocka_get_overview] / [TOOLS定義246行、実装294-298行] / [入力: なし(properties={}required=[])。出力: MOCKA_OVERVIEW.jsonの内容をjson.dumps(indent=2)でそのまま返す] / [読取専用: C:\Users\sirok\MOCKA_OVERVIEW.json(OVERVIEW_PATH、58行)] / [初出コミット 0da58c809, 2026-04-05T13:20:48+09:00「feat: MCP caliber v1.2.0 + TODO system + server status UI」]

[mocka_get_essence] / [TOOLS定義247行、実装300-304行] / [入力: なし。出力: http://127.0.0.1:5000/get_latest_dnaへのHTTP GET結果からdata["ping"]["ESSENCE_SUMMARY"]を抽出しjson.dumps(indent=2)で返す] / [静的ファイル直接読取なし。port5000(app.py)の/get_latest_dnaエンドポイント経由。description欄は「lever_essence.jsonの最新...を返す」と記載されているが、実装コードはlever_essence.jsonを直接読んでいない] / [初出コミット 52a221ae6, 2026-04-12T15:28:55+09:00「feat: mocka_get_essence MCPツール追加」]

[mocka_get_todo] / [TOOLS定義248行、実装306-310行] / [入力: なし。出力: load_todo()の内容をjson.dumps(indent=2)でそのまま返す] / [読み取り専用: C:\Users\sirok\MoCKA\data\MOCKA_TODO_ACTIVE.json(TODO_PATH、59行)] / [初出コミット 0da58c809, 2026-04-05T13:20:48+09:00。ファイル名がMOCKA_TODO.jsonからMOCKA_TODO_ACTIVE.jsonへ変わった時期は今回のpickaxe検索範囲では特定していない]

[mocka_add_todo] / [TOOLS定義249行、実装312-346行] / [入力: id(必須)/title(必須)/status(既定"未着手")/contract_status(任意)/priority(既定"中")/category/description/assigned_to/note/reference_event。出力: 成功時{"status":"ok","id":...,"action":"added"}、エラー時{"error":...}] / [読み書き: TODO_PATH(load_todo/save_todo、238-243行。save_todoは一時ファイル書き込み+os.replaceによるアトミック置換)] / [初出コミット 33a6eca67, 2026-04-18T12:33:18+09:00「No-Token Architecture完成・RAW113件処理・essence更新」。ファイル冒頭のdocstring(2-4行目、v1.5.0、「変更点: mocka_add_todo追加」)は本ツールを直近の変更点として記載しているが、git pickaxe検索による初出は2026-04-18であり、docstringの記載日時と一致しない。contract_statusフィールドの追加はcommit c9848c438(2026-06-28、TODO_385)であることを別途確認した]

[mocka_update_todo] / [TOOLS定義250行、実装348-380行] / [入力: id(必須)/status(任意、PATCH動作)/contract_status(任意)/note(任意)。出力: {"status":"ok","id":...,"new_status":...}] / [読み書き: TODO_PATH。statusが"完了"の場合、対象をtodosリストからcompletedリストへ移動] / [初出コミット 0da58c809, 2026-04-05T13:20:48+09:00]

[mocka_list_events] / [TOOLS定義251行、実装382-385行] / [入力: n(既定20)。出力: {"count":件数,"events":[...]}] / [読み取り専用: mocka_events.db(DB_PATH=data/mocka_events.db、64行)のeventsテーブル、_db_read_events経由] / [初出コミット 0da58c809, 2026-04-05T13:20:48+09:00]

[mocka_read_event] / [TOOLS定義252行、実装387-391行] / [入力: id(必須)。出力: 該当イベント1件のdict、またはnot found] / [読み取り専用: mocka_events.db(read_events(9999)で全件取得後event_idでフィルタ)] / [初出コミット 0da58c809, 2026-04-05T13:20:48+09:00]

[mocka_search] / [TOOLS定義253行、実装393-398行] / [入力: query(必須)。出力: {"query":...,"events_hits":[...],"knowledge_gate_hits":[...]}] / [読み取り専用: mocka_events.db(search_events)、および data/配下の全*.mdファイル(rglob、search_knowledge_gate関数、163-177行)] / [初出コミット 0da58c809, 2026-04-05T13:20:48+09:00]

[mocka_write_event] / [TOOLS定義254行、実装400-461行] / [入力: title(必須)/description(必須)/author(必須)/tags/why_purpose/how_trigger。出力: 成功時{"status":"ok","event_id":...,"when":...,"storage":"gate/sqlite"または"gate/sqlite(in-process)"}、失敗時{"status":"gate_rejected","errors":[...]}] / [書き込み: 通常経路はhttp://localhost:5000/api/gate/eventへPOST(GATE_URL、67行)。接続エラー時のフォールバックはphi_os/event_gate.pyのprocess_event()をインプロセス直接呼び出し(444-449行)] / [初出コミット 0da58c809, 2026-04-05T13:20:48+09:00。why_purpose/how_triggerフィールド追加はe72c77989(2026-04-11)。GATEプロキシ経由への変更はコード内コメント「[PHI-OS GATE v1 2026-06-16]」より2026-06-16頃。フォールバックのインプロセス化はe98251e21(2026-06-20、Phase5-2.1)]

[mocka_seal] / [TOOLS定義255行、実装463-472行] / [入力: なし。出力: {"sha256":...,"source":"sqlite","event_count":...,"timestamp":...}] / [読み取り専用: mocka_events.db全件(_db_read_events)をJSON化してsha256計算] / [初出コミット 0da58c809, 2026-04-05T13:20:48+09:00]

[mocka_get_incidents] / [TOOLS定義256行、実装474-505行] / [入力: category(既定""、任意)/limit(既定20)。出力: {"incidents":[...],"count":件数}] / [読み取り専用: mocka_events.dbへの直接SQLクエリ(what_type/title/free_note列へのLIKE検索)] / [初出コミット e328f070e, 2026-06-08T08:55:27+09:00(pickaxe検索による最古出現)]

[mocka_get_guidelines] / [TOOLS定義257行、実装507-515行] / [入力: なし。出力: {"guidelines":先頭20件(リストの場合),"total":件数}] / [読み取り専用: data/guidelines.json(BASE/"data"/"guidelines.json"、508行)] / [初出コミット e328f070e, 2026-06-08T08:55:27+09:00]

[mocka_get_command_center] / [TOOLS定義258行、実装517-532行(重複あり、下記参照)] / [入力: なし。出力(517-532行側): {"loop_status":...,"risk":...,"heinrich":...}各エンドポイント結果またはerror] / [読み取り専用: http://localhost:5000/loop/status・/risk/recommendation・/heinrich/status(517-532行側は3エンドポイント)] / [初出コミット 5a3a8f1c2, 2026-05-20T09:47:25+09:00(pickaxe検索による最古出現。どちらの実装がこの時点のものかは今回未特定)] — 【事実】execute_tool内に`elif name == "mocka_get_command_center":`という同一分岐が566-577行にも重複して存在する(loop/risk 2エンドポイントのみを参照する別実装)。Python if/elif構造では294行から始まる分岐チェーンが上から評価されるため、517行側が先に一致し、566行側は実行時に到達しない。

[mocka_check_utf8] / [TOOLS定義259行、実装534-564行] / [入力: filepath(必須)。出力: {"filepath","size_bytes","has_bom","ok","issues","encoding","line_count"}] / [引数で指定された任意のファイルパスを読む。固定データファイルなし] / [初出コミット e328f070e, 2026-06-08T08:55:27+09:00]

[mocka_registry_get] / [TOOLS定義260行、実装648-656行] / [入力: env(既定"test", "prod"|"test")。出力: registry_store.get_registry(env)の結果、またはエラー] / [registry_store モジュール(PlanningCaliber/workshop/registry_kn004、35行でsys.path追加後import)経由。同モジュールが実際に読み書きするファイル/DBの詳細は、mocka_mcp_server.py自体には記載がなく、registry_store.py側の確認は今回実施していない] / [初出コミット 8c00633e3, 2026-07-01T13:39:26+09:00(pickaxe検索による最古出現)]

[mocka_registry_add] / [TOOLS定義261行、実装658-674行] / [入力: layer(必須、identity/atlas/reference/classification/lifecycle/metadataのいずれか)/record(必須、object)/env(既定"test")。出力: {"status":"ok","layer":...,"env":...,"record":...}、またはREGISTRY_VALIDATION_FAILED等のエラー] / [registry_store.add_record()経由(詳細未確認、上記同様)] / [初出コミット 8c00633e3, 2026-07-01T13:39:26+09:00]

[mocka_registry_current_state] / [TOOLS定義262行、実装676-685行] / [入力: target_id(必須)/env(既定"test")。出力: registry_store.get_current_state()の結果、またはnot found] / [registry_store経由(詳細未確認、上記同様)] / [初出コミット 8c00633e3, 2026-07-01T13:39:26+09:00]
```

---

## 補足事実(17ツール以外に関連する事項)

- `execute_tool`関数(265-293行)には、GL1-7 Governance Pipeline(`structural/governance_pipeline.py`)による`before_tool()`チェックがすべてのツール呼び出しの前段に存在する。このゲート機構自体の導入は5c08a0338(2026-06-13、「feat: connect GL1-7 Governance Pipeline to Caliber MCP server」)。
- `TOOLS`配列(246-262行、17件)には現れないが、`execute_tool`内には`mocka_search_incidents`(579-606行)・`mocka_get_phl`(608-627行)・`mocka_get_spp`(629-646行)という3つの追加分岐が存在する。これらは`tools/list`のレスポンスには含まれないが、`/agent/<tool_name>`REST経由では呼び出し可能な状態になっている。
- SQLiteのevent読み出し処理(`_db_read_events`関数、99-121行)には、`when_ts`列から`when`キーへのフォールバックマッピング(113-115行)が存在する。これは稼働中のルート`mocka_mcp_server.py`自体に存在する記述であり、`deploy/mocka_mcp_server_vps.py`固有の実装ではない。

---

以上、確認できた事実の提示をもって本作業を終了する。推測・階層モデル化・分類の提案は行っていない。

---

## 改訂履歴

- v0.1(2026-07-04): 博士指示「MoCKA MCPツール17個の実体確認」に基づき新規作成。くろこ起草。
