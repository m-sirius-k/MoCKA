# COMMAND CENTER v6.1 Regression Recovery Plan v1.0

指示元: R01監査官(2026-07-11 最終裁定)
種別: 復旧設計のみ。コードは変更しない。実装はHuman Gate承認後
関連: COMMAND_CENTER_REGRESSION_INCIDENT_REPORT_v1.0.md、COMMAND_CENTER_DATAFLOW_CATALOG_v1.0.md

対象は「Regression」判定を受けた4パネル(civ/todo/bee/essence)。各パネルについて、復旧対象・依存API・必要Adapter・Render修正点・テスト方法・Human Gate・Rollbackを整理する。

## 1. Civilization Loop (civ)

- **復旧対象**: `fetchLive()`(index.html:1197-1224)のjobsループ内、`civ`パネルのfetch成功時に`renderCiv(data)`相当の呼び出しが行われていない箇所。
- **依存API**: `GET /loop/status`(既存、稼働確認済み)。実測レスポンス形状は`{"civilization_loop":{"observe":{...},"record":{...},"incident":{"count":248,"detail":"...","label":"Incident"},...}}`という8段階名をキーとするオブジェクトであり、`renderCiv`が期待する配列`[{n,name,color,pct,count}]`とは形状が異なる。
- **必要Adapter**: 新規`mapCivData(raw)`関数(hein用の`mapHeinData()`と同型の役割)。`raw.civilization_loop`の各キー(observe/record/incident/recurrence/prevention/decision/action/audit)を、既存STATIC.civの8段階定義(n/name/color)と対応付け、`count`はAPIの生値をそのまま採用できる。ただし`pct`(進捗バーの%)は現行STATICにしか存在しない意味付けであり、APIレスポンスに直接対応する値がないため、算出方法(何を分母とするか等)を実装着手前に博士へ確認する必要がある。
- **Render修正点**: `fetchLive()`のPromise.allSettledループの分岐に`if(j.panel==='civ') renderCiv(mapCivData(data));`相当を追加。
- **テスト方法**: (1)`/loop/status`の実レスポンスを流し込み`IC.expectArr`等の整合性チェックが通ることを確認、(2)Incident等の値がAPI実測(248件)またはevents.db実測(232件、集計方法の違いは別途要確認)と一致することを目視確認、(3)`/loop/status`を意図的に失敗させてSTATICへ正しくフォールバックすることを確認。
- **Human Gate**: 本Recovery Plan自体の承認。pct算出方法について追加確認が必要な場合はその時点で個別に博士確認。実装後はCHANGE_DONE記録。
- **Rollback**: index.htmlの当該diffのみをgit revertすれば旧STATIC-onlyの状態へ即座に戻せる。civパネル単体の変更のため影響範囲は他パネルに及ばない。

## 2. Active TODO (todo)

- **復旧対象**: render未接続に加え、**エンドポイント自体の妥当性再検討**が必要。`GET /risk/recommendation`は実測で`{"recommendation":{"id":"TODO_437","message":"...","priority":"...","reasons":[...]}}`という**単一の推奨事項オブジェクト**を返しており、`renderTodo`が期待する「TODO一覧(配列)」を返す設計になっていない。
- **依存API**: 現行`/risk/recommendation`のまま「単一の最優先推奨のみ表示するパネル」へ設計変更するか、別途「TODO一覧を返すエンドポイント」(新設、または`mocka_get_todo`相当のAPIをapp.py側に追加)を選定するか、方針決定が必要。この判断は他の3パネルより設計の自由度・影響範囲が大きい。
- **必要Adapter**: エンドポイント選定後に確定する。現行`/risk/recommendation`のまま活かす場合は、`renderTodo`自体を「配列前提の一覧表示」から「単一推奨事項の強調表示」へ作り替える必要があり、これは単純な配線修復ではなくパネルの再設計に近い。
- **Render修正点**: 上記の設計判断が確定してから決定する。
- **テスト方法**: 上記の設計判断が確定してから決定する。
- **Human Gate**: 他の3パネルとは異なり、実装着手前に「このパネルは何を表示すべきか」という設計方針そのものを博士に確認する必要がある。本Recovery Planでは方針決定を保留とする。
- **Rollback**: 方針確定後、civと同様にdiff限定でrevert可能な設計とする。

## 3. BEE Ecology (bee)

- **復旧対象**: `fetchLive()`のjobsループ内、`bee`パネルのfetch成功時に`renderBee(data)`相当の呼び出しが行われていない箇所。
- **依存API**: `GET /api/beta/status`(既存、稼働確認済み)。実測レスポンス形状は`{"betas":[{"beta_id":"institutional_evolution","beta_ja":"制度化フェーズ","evidence":74,"co_occurrence":[],"first_seen":"2026-06-01","last_seen":"2026-07-11",...}]}`であり、`renderBee`が期待する`data.items:[{lc,name,ev}]`とは配列内オブジェクトのフィールド名が異なる。
- **必要Adapter**: 新規`mapBeeData(raw)`関数。`raw.betas`配列の各要素を`{lc,name,ev}`形式へ変換する。`lc`(lifecycle: est確立/grow成長/obs観察)の判定ロジックをどのフィールド(`evidence`件数の閾値、`co_occurrence`の有無等)に対応させるかは、`interface/beta_engine.py`(TODO_216)側の既存分類ロジックと整合させる必要があり、実装前に該当コードを確認すること。
- **Render修正点**: `fetchLive()`の分岐に`if(j.panel==='bee') renderBee(mapBeeData(data));`相当を追加。
- **テスト方法**: (1)実データでの表示確認、(2)est/grow/obsの分類が`beta_engine.py`側の定義と一致するかの突合確認、(3)フォールバック確認。
- **Human Gate**: 本Recovery Plan承認、`lc`判定ロジックの妥当性について実装時に念のため確認、実装後CHANGE_DONE記録。
- **Rollback**: diff限定でrevert可能。

## 4. Essence/PHL (essence)

- **復旧対象**: `fetchLive()`のjobsループ内、`essence`(ess)パネルのfetch成功時に`renderEssence(data)`相当の呼び出しが行われていない箇所。
- **依存API**: `GET CALIBER:5679/phl/history`(既存、稼働確認済み)。ただし実測時点(2026-07-11)のレスポンスは`{"count":0,"history":[]}`であり、現在PHL(Philosophy/Lever)履歴データが空。
- **必要Adapter**: 新規`mapEssenceData(raw)`関数。`raw.history`が空配列の場合のフォールバック表示方針(現行STATIC.essence文言をそのまま維持する/「データ蓄積中」等の専用メッセージに切り替える、のいずれか)を実装前に決定する必要がある。データが蓄積された場合の`history`要素の実際の形状(axis/color/txt相当のフィールドがあるか)は、本Recovery Plan作成時点では実測不能(空のため)であり、実装着手時に改めてサンプルデータでの確認が必要。
- **Render修正点**: `fetchLive()`の分岐に`if(j.panel==='ess') renderEssence(mapEssenceData(data));`相当を追加。空データ時のハンドリングを含む。
- **テスト方法**: (1)PHL historyにデータが蓄積された状態(もしなければテスト用データを用意)でのレンダリング確認、(2)空配列時に不自然な空白・エラー表示にならないことの確認。
- **Human Gate**: 本Recovery Plan承認。特に「PHL historyが現状空である」という事実自体が別の制度的課題(essence_auto_updater運用、TODO_359関連)を示唆する可能性があり、この点は本Recovery Planのスコープ外として切り分け、博士へ別途報告する。
- **Rollback**: diff限定でrevert可能。

## 5. 実装方針(共通事項)

- 4パネルは**個別のCHANGE_START/CHANGE_DONEで1パネルずつ記録・commit**する。1回のcommitで4パネル同時に変更しない。これはCOMMAND_CENTER_REGRESSION_INCIDENT_REPORT_v1.0.mdで特定した「大規模一括書き換えがレビューを困難にし退行を見逃す遠因になった」という教訓(AUTO_SEAL_50EVTの946行/1133行一括書き換え)を踏まえた運用判断である。
- todoパネルは設計方針決定が先行事項であり、civ/bee/essenceの3パネルとは着手順序を分離してよい。
- 全パネル共通で、修正後は本Recovery Planおよび親文書のデータフロー台帳を更新し、次回リリース時の比較基準とする。

## 6. 非目的

本文書はコード変更を一切行っていない。上記はあくまで実装設計であり、着手可否はHuman Gate裁定に委ねる。
