# TODO_411/412/413 AUTO_SEAL Boundary Audit v1.0

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / 確認のみ・実装変更は一切行っていない

目的: AUTO_SEAL Pack1(TODO_427)完了後、TODO_428(Generator)完成後の現時点で、
AUTO_SEAL生成->Seal metadata->Integrity確認の境界に未接続箇所が残っていないかを
TODO_411/412/413の観点で再確認する。

## Step 1-2: 一次データ・関連設計文書確認

TODO_411/412/413はいずれも2026-07-01のAUTOSEAL調査由来で、2026-07-02時点で
"Step1追記"として詳細な事実確認が既に行われている(`docs/governance/GL7_STATE_INTEGRITY_NOTE_v1.0.md`
参照)。当時確認された骨子: AUTO_SEALには3経路(AUTO_SEAL_50EVT/AUTO_SEAL_{today}/MANUAL_SEAL)
があり、いずれも`anchor_update.py`経由で`mocka_git_safe_commit()`を呼ぶ。当時(2026-07-02)は
3経路とも無条件でanchor_update.pyを実行しており、承認ゲートも`mocka_write_event`との
接続もなかった。

## Step 3-4: 実装ファイル・runtime確認(現時点、2026-07-08)

2026-07-02の観測以降、TODO_370/371(50EVT分岐)・TODO_427(daily分岐)により、
2経路が是正されていることを確認した。**しかしMANUAL_SEAL経路(`/audit/seal`エンドポイント)は
是正対象に含まれておらず、2026-07-02時点の無条件実行のまま残っている。**

| 経路 | 実装箇所 | 現状 |
|---|---|---|
| AUTO_SEAL_50EVT | `app.py:auto_audit_loop()`(event_count差分50到達) | PENDING イベント記録のみ、anchor_update.py自動実行なし(TODO_370/371是正済み) |
| AUTO_SEAL_{today} | `app.py:auto_audit_loop()` + `watchdog_mocka.py:try_daily_seal()` | PENDING イベント記録のみ、anchor_update.py自動実行なし(TODO_427是正済み) |
| **MANUAL_SEAL** | `app.py:2150 @app.route("/audit/seal", methods=["POST"])` | **POST即座に`anchor_update.py`をsubprocess実行。PENDING化されておらず、承認ゲート・認証チェックともになし** |

`anchor_update.py`(`scripts/ledger/anchor_update.py`)自体を確認したところ、
`main()`内に`human_gate_override_event_id`等の自前ゲートは無い。2026-07-02以降の
最終commit(TODO_364統合、2026-06-30)時点でもゲート機構は追加されていない。
すなわち今回の是正(TODO_370/371/427)は**anchor_update.py本体や
mocka_git_safe_commit()側の構造変更ではなく、個々の呼び出し元(caller)側で
"呼ばない"判断を入れる形で行われている**。この方式は、新規/既存の呼び出し元を
1つでも見落とすとその経路だけ無防備に残るという構造的脆弱性を持ち、実際に
`/audit/seal`がその見落としに該当していることを本監査で確認した。

`/audit/seal`は`app.py`の`app.run(host="127.0.0.1", port=5000)`によりlocalhost限定で
リッスンしており(app.py:4130確認済み)、`gateway/gateway.py`にもこのエンドポイントへの
参照は無い(grep確認済み)。したがって外部(GPT/Copilot等Gateway経由のクライアント)からの
到達性は無いと考えられるが、同一マシン上の任意のローカルプロセス・スクリプトからは
認証なしでPOST可能であり、Human Gateを経由せず`mocka_git_safe_commit()`(git commit実行)を
即座にトリガーできる状態にある。`data/seal_log.json`(このエンドポイントが書き込むログ)は
現在存在せず、実際に呼び出された形跡は無い(未使用のまま放置されている経路と見られる)。

## Step 5: artifact確認

- `data/seal_log.json`: 不存在(MANUAL_SEAL未実行の傍証)
- `governance/anchor_record.json` / `mocka-governance-kernel/anchors/anchor_record.json`:
  Edge Audit(MOCKA_EDGE_AUDIT_v1.0.md)で既報の通り、sealed_at_utc=2026-07-07T11:03:41Zの
  ままで、本日(2026-07-08)のPENDING系イベント発生とは無関係に更新されていない
  (Generator実行のみでは更新されない設計のため、これ自体は想定通り)
- `data/mocka_events.db`: `AUTO_SEAL_PENDING_DAILY_20260708...`・`AUTO_SEAL_PENDING_...`の
  イベントが実際にevents.dbへ記録されていることを確認済み(`event_buffer.py`の
  `get_buffer().push()`経由。app.py全体で使われている汎用イベント記録機構であり、
  `structural/execution_governance.py`のCHANGE_START/CHANGE_DONE専用フックとは別系統)

## Step 6: 未整備点分類

| ID | 分類 | Operational Impact | 内容 |
|---|---|---|---|
| Gap-1 | **High(Boundary Risk)** | Not observed(`data/seal_log.json`不存在、実行証跡なし) | MANUAL_SEAL(`/audit/seal`)がHuman Gate PENDING化の対象から漏れている。TODO_370/371/427と対称的な修正が未実施。現時点では"発生中の障害"ではなく"未閉鎖境界"として扱う |
| Gap-2 | **Medium(構造)** | Not observed | Human Gate是正が"呼び出し元ごとの個別対応"方式であり、`anchor_update.py`/`mocka_git_safe_commit.py`自体には呼び出し元非依存の一元的なゲートが無い。将来の新規呼び出し元でも同じ見落としが起こり得る |
| Gap-3 | **Medium** | Not observed(制度設計判断の範疇であり、障害ではない) | TODO_413が求める"CHANGE_START/CHANGE_DONEプロトコルとの接続"は、PENDING化された2経路について`event_buffer`経由の汎用イベント記録は行われるようになったが、`structural/execution_governance.py`の正式なrecord_file_change/record_execution フックへの接続ではない。技術的記録はあるが、制度的変更記録としての接続は未確定。TODO_413の原義(CHANGE_START/CHANGE_DONE"プロトコル"接続)はまだ満たされていない可能性がある |
| Gap-4 | **Low** | Not observed | `/audit/seal`は認証なしでPOST可能(localhost限定のため外部到達性は無いと考えられるが、コードレベルでの認証チェックは存在しない) |

補足: 上記いずれも"発生中の障害"ではなく"未閉鎖境界(Boundary Risk)"である。
実行証跡(`data/seal_log.json`不存在、events.db上にMANUAL_SEAL起因のcommitやincidentが
見当たらないこと)から、現時点でのOperational Impactは"Not observed"と判定する。
Gap-1がHighである理由は実害が発生しているからではなく、Human Gateという制度の
一貫性(全Seal要求が同じ扱いを受けるべきという原則)に対する構造的な穴が
現に存在するためである。

## Step 7: 修正候補(報告のみ、実装は行っていない)

1. `/audit/seal`(MANUAL_SEAL)を、TODO_370/371/427と同型のPENDINGパターン
   (PENDINGイベント記録のみ、`human_gate_override_event_id`付き手動実行でのみ
   実際にanchor_update.pyを起動)へ揃える案
2. Gap-2への対応として、ゲート判断を各呼び出し元ではなく`anchor_update.py`の
   `main()`自体、または`mocka_git_safe_commit()`側に一元化する構造変更案
   (呼び出し元を今後追加・変更しても見落としが起きない設計)
3. Gap-3への対応として、PENDINGイベント記録を`structural/execution_governance.py`の
   正式フック経由に揃えるか、あるいは現行の`event_buffer`記録で
   TODO_413の要件を満たすと制度的に確定するかの判断
4. Gap-4は`/audit/seal`のリッスンアドレスがlocalhost限定である現状を維持する限り
   優先度は低いが、認証チェック追加も選択肢として記録

いずれも実装は行っていない。次工程着手の要否・優先順位はHuman Gateの判断に委ねる。

## 追記(2026-07-10): Gap-3の追跡先確定

TODO_413はDC_20260710_003(mocka_git_safe_commit()内部でgit commit操作をmocka_write_event
経由のHTTP POSTで自己記録する実装)により、「Git Commit経路におけるLedger記録漏れ」という
実害についてはClose済み(DC_20260710_004)。

ただし本Gap-3が指摘した`structural/execution_governance.py`のrecord_file_change()/
record_execution()経由の、CHANGE_START/CHANGE_DONEプロトコル本体との制度的接続は、
DC_20260710_003の対象外であり未解決のまま残っている。DC_20260710_003が追加した記録経路
(mocka_write_event経由のHTTP POST)は、record_file_change/record_executionとは別系統の
並行した記録経路であり、両者の統合可否はまだ制度的に確定していない。

この論点はTODO_438(execution_governance.pyとCHANGE_START/CHANGE_DONEプロトコル本体との
制度的接続)として独立管理へ切り出した。Gap-1・Gap-2・Gap-4は本追記時点で未着手のまま。
