# TODO_428_DATA_FINDINGS

作成: Claude-sonnet-5(くろこ) / 2026-07-08

本文書はTODO_428 Generator実装の副産物として発見されたデータ不整合の記録のみを目的とする。
修正は行わない(TODO_428のスコープ外)。別TODOとして管理する。

## 発見1: TODO_414 status/bucket不整合

- 発見日時: 2026-07-08(`scripts/state/overview_current_generator.py`初回実行時)
- 検出元: `integrity_warnings`(TODO整合チェック、`_load_todo_summary()`)
- 対象: `data/MOCKA_TODO_ACTIVE.json`の`completed`配列内、`TODO_414`
  (title: watchdog_mocka.py x AUTO_SEAL_50EVT 同時実行時のgit書き込み競合リスク)
- 問題: `completed`配列(TODO_384運用上"完了"を意味するバケット)に分類されているにも
  かかわらず、レコード自身の`status`フィールドは`未着手`のまま
- 影響: 状態表示層(将来的に`MOCKA_OVERVIEW_CURRENT.json`を参照する運用になった場合)で
  TODO_414の進行度が実態と異なって見える可能性がある。MOCKA_OVERVIEW_STALENESS_REPORT.mdが
  発見したTODO_242/325/266/171/215/346とは別件の新規発見
- 対応: 本発見はTODO_428の実装が成果として検知したものであり、TODO_428自体の不具合ではない。
  修正(status更新またはcompleted配列からの削除)はTODO_428のスコープ外とし、別途TODO化して
  Human Gateの判断を仰ぐ

## 発見2: mocka_events.db when_ts列の破損レコード(既知事象、参考記録)

- 発見日時: 2026-07-08(Generator実装中、`ORDER BY when_ts DESC`が誤った最新値を返した際に発覚)
- 対象: `data/mocka_events.db`のeventsテーブル、when_ts列
- 問題: 15件のレコードでwhen_ts列に文字化けまたは`N/A`/`pipeline`等の非ISO8601値が
  格納されている(既知のTODO_423 Decision Ledger文字化けと同系統の事象と推定)
- 影響: `ORDER BY when_ts DESC`のような文字列比較ソートを行うと、これらの破損値が
  辞書順で実際の最新timestampより上位に来てしまい、誤った結果を返す
- 対応: `overview_current_generator.py`側は`ORDER BY rowid DESC`(挿入順、
  `export_for_cloudflare.py`の既存パターンと同一)へ変更することで回避済み。
  根本原因(when_ts列自体の文字化け)はTODO_423側の課題であり、本書では現状把握の
  記録に留め、修正はTODO_428のスコープ外とする
