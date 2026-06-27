# Civilization Loop断絶調査 + 関連系統棚卸し v1

Status: INVESTIGATION_REPORT（調査・整理のみ。断定・実装は行っていない）
Date: 2026-06-28
作成: Claude-sonnet-4-6
関連: TODO_374, TODO_375, TODO_369, TODO_368, TODO_361, TODO_359, TODO_136, TODO_137

## 1. TODO_375: 数値集計の出典特定（結果: 出典を特定できた）

### 1.1 結論

出典は**特定できた**。`app.py`の`/loop/status`エンドポイント（1470-1581行）が、
Observe/Record/Incident/Recurrence/Prevention/Decision/Action/Auditの8項目を
**毎リクエスト時にライブ計算して返すダッシュボードAPI**であり、これがTODO_374
記載の数値の出典である。静的なレポートファイルやログではなく、実行中サーバーの
APIレスポンスだったため、ファイル全文検索（前回調査）やDB列の集計検索だけでは
見つからなかった。

### 1.2 特定の経緯（実機確認）

稼働中サーバー（localhost:5000）に対し`curl http://localhost:5000/loop/status`を
実行し、現在(2026-06-28)の値を取得した:

```
observe:    count=11    (RAW未処理 — data/storage/infield/RAW/*.json件数)
record:     count=13692 (mocka_events.db総件数)
incident:   count=222   (risk_level=DANGER/CRITICAL または what_type/titleにINCIDENT含む行数)
recurrence: count=66    (data/recurrence_registry.csv の行数)
prevention: count=1799  (未承認Prevention案件数)
decision:   count=5     (承認済みDecision件数)
action:     count=3     (Auto Gate実行件数)
audit:      last_seal="2026-03-26T23:33:06..."
```

**`recurrence: count=66`が、TODO_374記載の「Recurrence=66」と完全一致した。**
これは決定的な証拠である。`recurrence_registry.csv`が2026-06-25前後から現在まで
更新されていないため、Recurrenceの値だけが時間が経っても変化せず、当時の報告値と
そのまま一致した。一方Observe/Record/Incidentは時間経過とともに変化する値
（events.dbは2026-06-25時点の1,842件から現在13,692件まで成長、RAWディレクトリの
未処理件数やINCIDENT判定件数も日々変動する）であるため、現在値が当時の報告値
（Observe=0/Record=1,842/Incident=23）と一致しないのは**矛盾ではなく**、ライブ
カウンタの自然な時間変化として説明がつく。

### 1.3 各カウンタのコード上の定義（app.py 1497-1576行）

| 項目 | 定義 | データソース |
|---|---|---|
| Observe | `len(RAW_DIR.glob("*.json"))` | `data/storage/infield/RAW/` |
| Record | `len(db_helper.read_events(limit=None))` | `mocka_events.db` events テーブル総件数 |
| Incident | `risk_level in [DANGER,CRITICAL]` または `what_type`/`title`に`INCIDENT`を含む行数 | events テーブルの動的フィルタ集計 |
| Recurrence | CSV行数 | `data/recurrence_registry.csv` |
| Prevention | `status not in [APPROVED,REJECTED]`の件数 | `data/prevention_queue.json` |
| Decision | `what_type`/`title`に`DECISION_APPROVED`を含む行数 | events テーブルの動的フィルタ集計 |
| Action | `what_type`/`title`に`AUTO_GATE`を含む行数 | events テーブルの動的フィルタ集計 |
| Audit | `ledger.json`の最終エントリのtimestamp/hash | `runtime/main/ledger.json` |

## 2. TODO_374: 断絶仮説の再評価（結果: 出典は見つかったが、当初仮説は前提が誤っていた）

### 2.1 当初仮説の再検証

TODO_374の当初仮説は次の2点だった。

- ①Observe→Record接続なき生成
- ②Incident→Recurrence出力過多

1.3の表で明らかなとおり、8項目はいずれも**互いに独立した別々のデータソースから
個別に集計される値**であり、「Observeの出力がRecordへ流れ込む」「Incidentの出力が
Recurrenceに変換される」といった**コード上のデータの受け渡し（パイプライン接続）は
そもそも実装されていない**。これは「接続が壊れている（断絶）」のではなく、
**この8項目はもともと連結されたパイプラインの中間生成物ではなく、8種類の独立した
健全性メトリクスを1つの管理画面に並べて表示しているだけ**という設計だったために、
「断絶」という表現自体が前提として成立しない可能性が高い。

ただし、これは「8段階Civilization Loopという概念全体が無意味」という意味ではない。
TODO_136/137（2026-05-11、後述2.2）が指す「8ステージ接続」は、`/loop/status`の
表示ロジックとは別の、実際の処理連鎖（`recurrence_registry`→`/prevention/generate`→
`prevention_queue`→Decision→Audit）を指しており、これは部分的に実装が存在する
（2.2参照）。つまり「概念としての8段階ループ」には**表示用の独立カウンタ群
（/loop/status）**と**実際に処理を連鎖させる機構（/prevention/generate等）**の
2つの異なる実装が混在しており、TODO_374はこの2つを区別せずに「断絶」と表現していた
可能性がある。

### 2.2 TODO_136/137の実装が現在も生きているかの確認

2026-05-11付TODO_136/137は、`/prevention/generate`エンドポイント実装
（recurrence_registry→prevention_queue自動生成）、Audit last_seal修正等を指す。

`app.py`を確認したところ、`/prevention/generate`（2169行以降）は現在も存在し、
`recurrence_registry.csv`を読み込み、`recurrence_count>=2`のパターンを
`prevention_queue`へ自動投入するロジックがコード上維持されていた（実行はしていない、
コードリードのみでの確認）。重大な構文崩れ等は確認時点では見当たらなかった。

ただし、これは**コードが存在し構文的に壊れていないことの確認**であり、実際に
正しく動作するか（実行テスト）・最新の運用要件と整合しているか（例: TODO_368で
書き込み口が増える計画等）までは本調査のスコープ外（実装変更を伴う検証のため）。

### 2.3 結論・提案

- TODO_374の「VIOLATION」「断絶」という表現は、出典が「独立メトリクス表示用
  ダッシュボード」であったと判明した時点で、前提が成立しないと考える（提案）。
- 「断絶」として扱うべき問題が本当にあるとすれば、それは`/loop/status`の表示値
  ではなく、TODO_136/137が指す**実処理連鎖**（recurrence_registry→
  prevention_generate→prevention_queue→...→Audit）が現在も正しく流れているか
  どうかという別の問いである。これは未検証（実行確認が必要）。

## 3. 関連周辺論点の棚卸し（現状確認のみ）

### 3.1 TODO_369（保留）— 記録文言の精度修正

TODO_322由来の「process_event()が唯一の書き込み経路」という記述が不正確
（実際は`phi_os/event_gate.py`の`_write()`が単一書き込み点）という訂正が、
まだ関連ドキュメントに反映されないまま保留中。TODO_374への影響は限定的と考える
（提案）。TODO_374の「Record」段階はevents.db全件数というシンプルな集計であり、
「process_event vs _write」という書き込み経路の呼称精度の問題は、Record段階の
カウント方法自体（COUNT(*)）には影響しない。ただし「正規の書き込み経路は何か」
という概念理解には影響するため、ドキュメント更新自体は別途進めるべき(優先度低のまま)。

### 3.2 TODO_368（未着手）— Orchestra→PHI-OS書き込み経路追加

Orchestra拡張機能からPHI-OSへの新規書き込みエンドポイント追加が計画されている。
実装されればevents.dbへの書き込み口が増え、「Record」カウント（events.db総件数）の
増加要因が1つ追加されることになる。TODO_374の数値（Record=1,842、現在13,692）は
**この変更が実施される前**の値である（TODO_368は本調査時点で未着手のまま）。
したがって「変更前か変更後か」を明確にする必要は現時点ではなく、TODO_368が実装され
次第、その時点のRecordカウントは「Orchestra経路追加後」として再解釈する必要がある
（提案: TODO_368完了時に一言メモを残すこと）。

### 3.3 TODO_361（未着手）— Decision Ledger Reconnection

8段階の「Decision」段階の判断根拠が、別制度（Decision Ledger Schema v1, TODO_305系）
と接続されていない状態がTODO_358から続いている。現在の「Decision」カウント
（`/loop/status`のdecision_count=5）は、events.db内で`title`/`what_type`に
`DECISION_APPROVED`を含む行を数えているだけであり、Decision Ledger（DCレコード）
とは無関係な別経路の集計である。つまり「Decision」段階は現状、**2つの未接続な
記録系統（events.db内のDECISION_APPROVEDタグ集計 と Decision Ledger Schema v1）**
が並存している状態であり、TODO_361が解決すれば両者が接続されるか、どちらが
正規かが明確になる（提案）。

### 3.4 TODO_359（進行中）— essence_auto_updaterの運用境界未決定

`app.py`内の`essence_auto_updater`（#2）を機能として残すか(判断A)Phase5で
廃止するか(判断B)が未決定のまま進行中。これはバックグラウンドループ機構全般
（civilization_loop_engine.py等の定期実行系を含む）の信頼性に間接的に関わる
（一言整理）: 起動経路が冗長なまま残っている間は、「このループは本当に1つの
正規経路でのみ動いているか」という疑いが他のループ系統にも及びやすくなる。
TODO_371（正本記録の信頼性実測、参考）とは「記録の中身が正しいか」という観点で
関連するが、TODO_359自体は「起動経路の冗長性」の問題であり、direct な依存関係は
ない。

## 4. 次のアクション提案（提案・断定なし）

1. **TODO_375**: 出典特定が完了したため、`完了`へのstatus変更を提案する。
   noteに本調査結果（app.py /loop/statusが出典であること）を追記する形を想定。
2. **TODO_374**: 当初仮説（①②）は「独立カウンタを連結パイプラインと誤解した」
   可能性が高いという結論に至ったため、現在の文言（断絶/VIOLATION疑い）のままでは
   実態と合わない。以下のいずれかを提案する。
   - 案A: TODO_374を`完了`とし、note に「断絶ではなく独立メトリクス表示と判明」を
     記録して終了する。
   - 案B: TODO_374の本体は完了としつつ、2.3で触れた「実処理連鎖
     （recurrence_registry→prevention_generate→...→Audit）が実際に動作しているか」
     という別の検証課題を、新規TODOとして切り出す（実行テストを伴うため別スコープ）。
   どちらを取るかはきむら博士の判断に委ねる。
3. TODO_369/368/361/359については、いずれも現状ステータス変更を提案するだけの
   新情報は得られなかった（3.1-3.4は現状確認のみ）。各TODOは現状のまま継続として
   問題ないと考える。
