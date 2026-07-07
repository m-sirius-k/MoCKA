# Essence正本化 設計提案 v0.1

## 位置づけ

本文書はIC_20260707_001(app.pyが第3のlever_essence.jsonを参照している問題)の続報調査であり、
Living Context整合性監査(監査官R01指示、2026-07-07)のPhase2-Bにおける「参照棚卸し+正本化案の提案」に対応する。

**本文書は提案のみであり、app.py・各essenceファイルへの変更は一切行っていない。**
app.pyはHuman Gate対象のコアシステムファイルであり、変更はHuman Gate承認後に別途実施する。

---

## Human Gate提出サマリー

### 問題発見経緯

1. Living Context整合性監査(監査官R01指示、2026-07-07)のPhase1でOrchestra拡張handshake復旧を確認中、
   COMMAND CENTERの`essence_updated`表示が実態と無関係な値を返し続けている疑義が浮上(IC_20260707_001)。
2. app.py内のessence参照19箇所を全数調査した結果、当初の想定を超える追加発見があり、
   IC_20260707_002(第3ファイルは生きた書込みパイプラインを持つ)→IC_20260707_003(旧4スクリプト
   チェーンの出力先だったことが判明、Legacy Essence Store命名確定)→IC_20260707_004(公開API境界不一致)
   と段階的に精密化した。

### 当初仮説(棄却済み)

「interface/lever_essence.jsonとdata/lever_essence.jsonの二重化(内容相違)」(IC_20260705_008)、
および「第3ファイルは更新停止した死蔵ファイル」(IC_20260707_001初期分類)。

### 調査結果(確定)

当初仮説はいずれも誤りであり、実態は**単純な重複ではなく、Canonical層・Projection層・Legacy層の
責任境界が未定義だった**ことが原因だった。具体的には:
- interface/data間は正常な一方向export(export_for_cloudflare.py、内容一致・実害なし)
- 第3ファイルは死蔵ではなく、旧essence処理チェーン(2026-04-11完成)の正規の出力先であり、
  かつapp.pyのMATAKA/DANGER自動フックが現在も書込みを続けている

### Canonical Essence定義

Source of Truth: `events.db`の`essence`テーブル。書込み主体は`essence_auto_updater.py`の
`update_essence_from_events()`のみ(events.dbのeventsテーブルから、きむら博士発言優先スコアリングで
蓄積型生成)。

### Projection定義

- **Projection A**(`interface/lever_essence.json`): Canonical Essenceの内部向け投影。
  書込み主体は`essence_auto_updater.py`の`sync_essence_db_to_file()`のみ(5分間隔、単一書込み主体を確認済み)。
  読者: `mocka_get_essence`(MCP)・Claude・Gateway・ping_generator.py
- **data/lever_essence.json**: Projection Aのさらなるexportスナップショット。書込み主体は
  `export_for_cloudflare.py`のみ(10分間隔、一方向性確認済み)。Gateway外部公開・Cloudflare同期専用

### Legacy Essence Store定義

> 過去のEssence生成・蓄積処理および現在限定利用される旧互換保存領域。
> Canonical Essenceではない。新規Writer追加は禁止。将来統合または廃止判断対象。

対象実体: `C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json`

### Writer分類(詳細は8.2)

| 分類 | 対象 | 扱い |
|---|---|---|
| Active Writer | app.pyの`auto_update_essence_from_mataka()`/`_auto_danger_to_essence()`/`run_essence()` | 継続監視 |
| Legacy Writer(凍結候補) | essence_extractor/condenser/trigger/pipeline.py、Essence_Direct_Parser.py、reflux.py(6スクリプト) | 凍結候補、Human Gate承認後に凍結実施 |
| Unknown Writer | 現時点で該当なし | 監査対象の器として維持 |

### Open課題一覧

| ID | 内容 | 状態 |
|---|---|---|
| IC_20260707_002 | Pipeline2(第3ファイル)の扱い方針 | Legacy Essence Storeとして制度化する方向で確定(本文書) |
| IC_20260707_003 | Canonical Model確定案そのもの | 本Human Gate提出により正式承認判断待ち |
| IC_20260707_004 | `/public/essence`・`/essence/detail`のpublic/private不一致 | Open課題として継続管理、Migration Spec検討対象 |
| (未採番) | Legacy Writer6スクリプトの完全な非稼働確認 | 「自動起動経路未発見」であり「絶対に実行されない」の証明ではない(Unknown Writer監査の継続対象) |

### 承認対象の明確化(A〜D)

**A. Canonical Essence**: `interface/lever_essence.json`をCanonical候補とする理由 — 
Claude/MCP/Gateway/ping_generatorが実際に参照している一次情報であり、`essence_auto_updater.py`という
単一の書込み主体からevents.db(唯一のSource of Truth)への一方向projectionとして構造が単純明快なため。

**B. Projection**: `data/lever_essence.json`の役割はGateway外部公開・Cloudflare同期用のexportスナップショット。
`export_for_cloudflare.py`による一方向export(dst→src読み込みなし)であることをコードレベルで確認済み。

**C. Legacy Essence Store**: Legacy Writer分類(6スクリプト)、新規Writer追加禁止、将来統合/廃止判断対象、
という定義そのものへの承認。

**D. API境界**: `/public/essence`・`/essence/detail`のpublic/private不一致をIC_20260707_004として
継続管理すること(緊急変更は不要、Migration Spec検討対象とする)への承認。

### 未承認事項(Human Gate承認まで変更禁止)

- app.py本体の変更
- essence参照経路(ESSENCE_PATH等)の変更
- Legacy Writer(6スクリプト)の削除
- API公開設定(`/public/essence`・`/essence/detail`の認証追加・廃止等)の変更
- いずれかのessenceファイルの移動・リネーム・削除

### Human Gate判断用チェックリスト

- [x] Canonical Essence(`interface/lever_essence.json`、events.db essenceテーブル起点)の責任範囲に同意するか
- [x] Legacy Essence Store(第3ファイル)を正式管理対象とするか
- [x] Legacy Writer(6スクリプト)凍結方針に同意するか
- [x] Projection export方式(`data/lever_essence.json`、export_for_cloudflare.py経由)を承認するか
- [x] app.py Migration Spec(ESSENCE Canonical Migration Spec v1.0)作成へ進むか

**承認済み(2026-07-07、DC_20260707_019、承認者: きむら博士/監査官R01)**。全5項目とも承認。
詳細は下記「Human Gate承認記録」を参照。

---

## Human Gate承認記録(DC_20260707_019)

監査官R01(きむら博士)により、以下の条件付きで全5項目が承認された(2026-07-07)。

1. **Canonical Essence**: `interface/lever_essence.json`をCanonical Essenceとして確定
   (責任: 最新Essence状態の保持)。条件: `essence_auto_updater.py`による単一Writer管理を維持すること。
2. **Legacy Essence Store**: 正式管理対象として承認。制約: 新規Writer追加禁止・既存ファイル削除禁止・
   統合/廃止判断は別途Human Gateで行う。理由: 現在削除すると旧処理チェーンの履歴・再現性を失う可能性がある。
3. **Legacy Writer凍結方針**: 承認。ただし状態表現を訂正する。
   **誤**: 「Legacy Writerは停止済み」/ **正**: 「Legacy Writerは新規利用禁止。既存稼働状態(6スクリプトの
   手動実行可能性)は別途監査対象」。理由: 手動実行可能性が残っている以上、制度上はWriter権限を保持した
   状態であり「停止済み」という表現は実態と乖離するため。
4. **Projection export方式**: `interface/lever_essence.json` → `export_for_cloudflare.py` →
   `data/lever_essence.json`の一方向export方式を承認。条件: data側への直接書込み禁止、export逆流
   (data→interface)禁止、同期失敗検知の追加は今後の検討課題とする。
5. **次工程**: ESSENCE Migration Spec v1.0の作成のみを許可。対象はapp.pyのessence参照整理
   (変更対象/現状参照/変更候補/Impact範囲/Human Gate確認項目の作成)。**app.py本体の変更・Legacy Writer
   削除・API公開設定変更・ファイル移動は本Decisionでは承認されていない**。Migration Spec作成後、
   Impact Analysis→Human Gate再承認を経て初めて実装に進む。

却下された代替案: (a)Legacy Essence Storeの退役(削除) (b)Legacy Writerを「停止済み」と記録すること
(c)Canonical Model承認と同時にapp.py変更へ進むこと。いずれも上記の理由により却下された。

Decision Ledger: `DC_20260707_019`

---

## 1. 参照棚卸し(app.py内 全essence参照箇所)

| 行 | 種別 | 対象ファイル | 用途 |
|---|---|---|---|
| 736-748 | 読み書き | 第3ファイル(planningcaliber) | `auto_update_essence_from_mataka()`: MATAKAパターンTop5をINCIDENT軸に追記。`check_and_trigger_essence_update()`(753行目)からMATAKAイベント件数が5の倍数の時にThread起動 |
| 1478,1490-1499 | 読み取り | 第3ファイル | COMMAND CENTER API: `essence_count`/`essence_axes`/`essence_updated`(={axis}_updatedの最大値)を算出 |
| 1680,1689-1695 | 読み取り | 第3ファイル | プロンプトヘッダー生成用途でessence全体を埋め込み |
| 1769,1822-1830 | 読み取り | 第3ファイル | 詳細ステータスAPIでaxis毎の`text`/`updated`/`count`/`filled`を返却 |
| 1833-1841 | 読み取り | 第3ファイル | `/essence/detail`ルート: ファイル内容をそのままJSON公開 |
| 1882-1891 | 読み取り | 第3ファイル | `/public/essence`ルート: ファイル内容をそのままJSON公開(認証なし) |
| 2005-2025 | 読み書き | 第3ファイル | `_auto_danger_to_essence()`: DANGER/CRITICALインシデント検知時にINCIDENT軸へ直接追記し、`INCIDENT_updated`を更新後、ping_generator.pyをサブプロセス起動 |

第3ファイル: `C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json`

## 2. 発見: 二重パイプライン構造

想定(IC_20260707_001時点)では「第3ファイルは更新が止まった死蔵ファイル」だったが、実際にはapp.py自身が
書込む生きた経路(MATAKA/DANGER自動パイプ)が存在する。すなわち、essenceには**独立した2系統のパイプライン**がある。

### Pipeline 1(interface/data系、SSOTとして機能中)

```
events.db(eventsテーブル)
    -> essence_auto_updater.py: update_essence_from_events()
       (きむら博士発言優先スコアリング、5分間隔)
    -> events.db(essenceテーブル)
    -> essence_auto_updater.py: sync_essence_db_to_file()
    -> interface/lever_essence.json
    -> (同期、機構未確認) -> data/lever_essence.json
```

読み取り側: `mocka_get_essence`(MCP)、`gateway/context_builder.py`、`gateway/gateway.py`(openapi.yaml公開)、
`ping_generator.py`の`_read_essence_from_db()`(events.db essenceテーブルを直接読む、最も新鮮)。

特徴: `updated_at`という単一の更新日フィールドのみを持ち、これ自体は2026-05-28から更新されていない
(sync処理が触れるのは`_synced_at`のみ)。ただし本文(INCIDENT/OPERATION/PHILOSOPHY)は2026-07-07時点の
最新イベントを反映しており実質的に鮮度は高い。

### Pipeline 2(第3ファイル系、app.py専用・部分的に生存中)

```
morphology_patterns.db(MATAKAパターン) / DANGER・CRITICALインシデント検知
    -> app.py: auto_update_essence_from_mataka() / _auto_danger_to_essence()
    -> C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json
```

読み取り側: COMMAND CENTER UI(`essence_updated`/`essence_axes`/`essence_count`)、
`/essence/detail`、`/public/essence`(認証なし公開API)。

特徴: `{AXIS}_updated`/`{AXIS}_source_count`フィールドを持つ(COMMAND CENTERの鮮度判定はここに依存)。
本文自体は2026-05-11時点の`gpt_handoff_20260509_v2`由来のテキストのまま、MATAKA/DANGERトリガー発火時に
INCIDENT軸へ短い追記がされるのみ(最終書込み痕跡: 2026-06-20)。トリガー条件(MATAKAイベント件数が5の倍数)が
成立しにくい、またはDANGER/CRITICAL検知が最近発生していないため、17日以上書込みが発生していない可能性が高い
(app.py側のtry/exceptがエラーを握りつぶす設計のため、書込み失敗であっても検知できない)。

### 影響

**COMMAND CENTER・`/public/essence`・`/essence/detail`が見せるessenceと、mocka_get_essence(MCP)・Gateway・
ping_latestが見せるessenceは、鮮度も本文も別物である。** これがLiving Context整合性監査の発端となった
「表示されている情報は本当に最新か」という疑義の技術的正体である。

## 3. 正本候補の評価

監査官R01からは「data正本+interface projection」(案A)と「interface正本+data projection」(案B)の
比較指示を受けたが、上記の発見によりinterface/data間の乖離は現状ほぼ無く(内容一致・同期済み)、
真に解消が必要なのはPipeline 2(第3ファイル)の扱いである。3案として整理する。

| 評価項目 | 案A: data正本(interfaceをprojection化) | 案B: interface正本(dataをprojection化) | 案C: Pipeline 2をPipeline 1へ統合(第3ファイル退役) |
|---|---|---|---|
| PHI-OS整合性 | dataはGateway(外部接続層)が読む前提の配置であり、内部知識層をGateway都合の場所に正本化することになりやや倒錯 | interfaceはClaude/MCP(内部)が読む配置と一致し、PHI-OSの「内部記憶」という位置づけに沿う | Pipeline 1(SQLite起点)は既にSSOTとして機能しており、これを唯一の正本とすることでPHI-OSの単一情報源原則に最も合致 |
| Runtime整合性 | 実行時の読み書き主体(essence_auto_updater.py)は現状interfaceを書いているため、dataを正本にすると同期方向を逆転する変更が必要 | 現行の実装方向と一致、変更不要 | COMMAND CENTER側の参照先変更(第3ファイル→interface or data)のみで済み、書込みパイプラインは1本化される |
| Interface境界 | Gateway/外部公開の観点では明確だが、Claude/MCP側が二次コピーを見ることになり境界がねじれる | Claude/MCP(一次情報)からGatewayへのprojectionという自然な方向 | Pipeline 2の公開API(`/public/essence`等)も同一の正本を見るようになり、境界が単純化される |
| 拡張性 | 今後Gateway側の要求が増える想定なら有利だが、現状その兆候はない | 現状の運用実態(essence_auto_updater.py中心)に沿い低コスト | 長期的に見て「なぜ2系統あるのか」を説明するコストが消える。TODO_419-422で進めてきたSSOT統合の流れとも整合 |
| 移行リスク | sync方向の逆転が必要(essence_auto_updater.pyの書込み先変更)、変更範囲が広い | 現状維持に近く低リスク | app.py側4箇所+COMMAND CENTER UI側の参照先変更が必要(Human Gate必須)。ただしMATAKA/DANGER自動パイプの「短い追記のみ」という機能自体をどう扱うかの追加判断が必要 |

## 4. 提案(暫定、Human Gate承認前提)

1. **interface/dataの関係**: 現状ほぼ同期済みで実害がないため緊急の変更は不要。将来的には案Bの方向
   (interface正本、dataはprojection)が実装済みの流れに最も自然に合う。
2. **第3ファイル(Pipeline 2)の扱い**: 以下いずれかの方針をHuman Gateで確定させる必要がある。
   - (i) 退役: COMMAND CENTER・`/public/essence`・`/essence/detail`の参照先をinterface(またはdata)版へ
     切り替え、MATAKA Top5/DANGER自動追記ロジックはPipeline 1側(`update_essence_from_events()`の
     スコアリングロジック)に統合する。第3ファイル自体はアーカイブし削除はしない。
   - (ii) 意図的別系統として維持: 第3ファイルが「MATAKA/DANGER専用の独立ログ」として意図的に設計された
     ものであれば、名称・ドキュメントを整備した上で「Pipeline 2はPipeline 1とは別の警報系essenceである」
     ことを明記し、COMMAND CENTER側の表示もその旨を区別する。
   - 現時点ではどちらが元々の設計意図だったか不明であり、この判断自体をHuman Gateで確定する必要がある。
3. **削除・移動は一切行わない**(監査官R01指示に従う)。上記いずれの方針も、決定後にSpec作成
   → 影響範囲分析 → Human Gate承認 → CHANGE_START → app.py変更 → CHANGE_DONE の手順を踏む。

## 5. 未解決事項(更新)

- ~~`data/lever_essence.json`の同期経路~~ → **解決済み(6.参照)**。
  `PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py`(10分間隔常駐、MoCKA-START.bat PHASE1起動)が
  `export_for_cloudflare.py`を起動し、同スクリプトのCOPIESリストが`interface/lever_essence.json`を
  `data/lever_essence.json`へコピーした後git pushする、正常な一方向exportパイプラインであることを確認した。
  `PlanningCaliber/fp/sync_watch_*.py`(3ファイル)は2026-06-27のgit競合調査時の一時退避コピーであり、
  現行の稼働経路ではないことも確認済み。
- `/public/essence`・`/essence/detail`の実際の外部呼び出し実績(誰が・どの頻度で叩いているか)は未調査。
  openapi.yamlには登録されていないため、Copilot Studio等の正式経路経由ではない。(未解決のまま)

## 6. Canonical Essence Model 確定案(監査官R01最終判断反映)

> 本セクション内の「Projection B」「第3ファイル」という表記は、8.1にて正式仮称
> **「Legacy Essence Store」**として命名確定した(2026-07-07)。以下は調査時点の記述をそのまま残す。

監査官R01の最終判断により、Pipeline 2(第3ファイル)は**退役ではなく、別系統Projectionとして正式制度化**する
方針が確定した。「正本が3つある」状態ではなく「正本1つ(Canonical Essence)+ 用途別Projection」として再定義する。

### 6.1 構造

```
Canonical Essence (Source of Truth)
  events.db の essence テーブル
  書込み主体: essence_auto_updater.py の update_essence_from_events() のみ
  (events.dbのeventsテーブルから、きむら博士発言優先スコアリングで蓄積型生成)
        |
        +-- Projection A: Knowledge Projection(知識・思想・運用ログ)
        |     interface/lever_essence.json
        |     書込み主体: essence_auto_updater.py の sync_essence_db_to_file() のみ(5分間隔)
        |     手動編集禁止(Canonical Essenceからの一方向コピーのため)
        |         |
        |         +-- data/lever_essence.json (further export snapshot)
        |               書込み主体: export_for_cloudflare.py のみ(10分間隔、sync_watch.py起動)
        |               手動編集禁止(Projection Aからの一方向コピーのため)
        |
        +-- Projection B: Alert/Signal Projection(警報・パターン検知)
              C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json
              書込み主体: app.py の auto_update_essence_from_mataka() / _auto_danger_to_essence() のみ
              Canonical Essenceとは独立した、イベント駆動型の警報生成ロジック専用ストア
              (MATAKAパターン検知・DANGER/CRITICALインシデント検知に特化。統合や書込み権限の混在は禁止)
```

### 6.2 責任範囲

| 対象 | 責任範囲 |
|---|---|
| Canonical Essence(events.db essenceテーブル) | 「きむら博士の発言・思想・インシデントの蓄積型要約」の唯一の真実源。全Projectionはここから派生する |
| Projection A(interface/lever_essence.json) | Canonical Essenceの内部向け投影。Claude/MCP/Gatewayが参照する「知識・運用」ビュー |
| data/lever_essence.json | Projection Aのさらなる派生(exportスナップショット)。Gateway外部公開・Cloudflare同期専用 |
| Projection B(第3ファイル) | MATAKA/DANGER自動パイプ専用の「警報・パターン検知」ビュー。Canonical Essenceとは意味的に異なる情報(短い自動追記のみ)であり、Knowledge Projectionと混同しないこと |

### 6.3 書込み権限境界

- Canonical Essence: `essence_auto_updater.py`の`update_essence_from_events()`のみが書込み権限を持つ
- Projection A: `essence_auto_updater.py`の`sync_essence_db_to_file()`のみ(Canonical Essenceからの一方向コピー)
- data/lever_essence.json: `export_for_cloudflare.py`のみ(Projection Aからの一方向コピー)
- Projection B: `app.py`の`auto_update_essence_from_mataka()`/`_auto_danger_to_essence()`のみ。他の書込み主体を追加しない

### 6.4 読取りAPI境界

- Knowledge Projection系(Canonical Essence / Projection A / data/lever_essence.json): `mocka_get_essence`(MCP)、
  `gateway/context_builder.py`、`gateway/gateway.py`(openapi.yaml公開)、`ping_generator.py`
- Alert/Signal Projection系(Projection B): COMMAND CENTER UI(app.py内部route)、`/public/essence`、`/essence/detail`
- 両系統は意味的に異なるビューであるため、将来のapp.py変更Specでは、COMMAND CENTER UIの表示ラベルを
  「Knowledge Essence」「Alert Essence」等に分離明示することを検討事項として含める(本文書では変更しない)

### 6.5 今後の手順(監査官R01指示順序)

```
本Canonical Model確定(本文書)
        ↓
Human Gate Phase確認
        ↓
Canonical Model正式承認
        ↓
app.py変更Spec作成(表示ラベル分離等、必要な場合のみ)
        ↓
影響範囲分析
        ↓
Human Gate承認
        ↓
実装(CHANGE_START -> 変更 -> CHANGE_DONE)
```

現時点ではapp.py・各essenceファイルへの変更は一切行っていない。本セクションはCanonical Model自体の
確定案であり、実装Specではない。

## 7. 追加調査(監査官R01指示、2026-07-07)

### 7.1 書込み主体の是正(重要な訂正)

6.2節で「Projection B(第3ファイル)= MATAKA/DANGER警報専用」と記述したが、これは不完全だった。
grep調査の結果、以下6スクリプトも第3ファイル(`C:/Users/sirok/planningcaliber/workshop/needle_eye_project/
experiments/lever_essence.json`)を書込み先としてハードコードしていることが判明した。

- `interface/essence_extractor.py`
- `interface/essence_condenser.py`
- `interface/essence_trigger.py`
- `interface/essence_pipeline.py`(内部でEssence_Direct_Parser→essence_classifierを順に呼ぶオーケストレータ)
- `interface/Essence_Direct_Parser.py`
- `interface/reflux.py`

これはMOCKA_OVERVIEW.jsonのsession_history(2026-04-11「LOOPパイプライン①〜⑤設計確定・完成」
「essence_classifier/extractor/condenser/trigger 4スクリプト完成」)と符合し、第3ファイルは
**essence_auto_updater.py(v4、SQLite起点)より歴史的に古い、旧essence処理チェーン(4原則抽出→4軸分類→
凝縮→トリガー)の正規の出力先だった**ことを示す。単なる「警報専用の副次ファイル」ではなく、
過去には本流だった処理チェーンの置き土産である可能性が高い。

**現在の自動起動状況(Task Scheduler照会+全コードgrepで確認)**:
- 自動稼働中と確認できたのはapp.py内の3経路のみ: `auto_update_essence_from_mataka()`
  (MATAKAイベント件数%5==0でThread起動)、`_auto_danger_to_essence()`(DANGER/CRITICAL検知)、
  `run_essence()`(success_great/hint処理後にessence_classifier.pyをsubprocess起動)
- 上記6スクリプトについては、Task Schedulerに該当タスクなし、他コードからのsubprocess/Thread呼出も
  発見できず。手動実行専用(セッション内でAIが直接pythonコマンドとして叩く運用)である可能性が高いが、
  「一切自動起動されていない」と断定はできない(悪魔の証明のため)。

**interface/lever_essence.json(Projection A)の書込み主体**: `essence_auto_updater.py`の
`sync_essence_db_to_file()`のみ。他に書込むコードは発見されなかった(単一書込み主体を維持できている)。

**data/lever_essence.jsonの書込み主体と一方向性**: `export_for_cloudflare.py`の`copy_files()`のみ。
`COPIES`リストはsrc→dstの固定タプルで`shutil.copy2(src, dst)`のみを実行し、dst→srcの逆方向読み込みは
コード上存在しない。一方向性を確認済み。

### 7.2 Pipeline 2(第3ファイル)の正式名称候補

7.1の是正を踏まえ、「警報専用」ではなく「旧essence処理チェーンの出力先+現行app.py自動フックの対象」
という実態を反映した名称候補を提示する(命名決定はHuman Gateに委ねる)。

| 候補 | 意図 |
|---|---|
| **Legacy Essence Store(レガシーessenceストア)** | 旧4スクリプトチェーンの出力先だった経緯を明示。app.pyの現行フックも含め「未整理のまま存続している旧系統」という実態に忠実 |
| **Console Essence(コンソールessence)** | 読者側(COMMAND CENTER UI・/public系API)を基準にした名称。書込み側の歴史的経緯を問わず、用途で識別 |
| **Signal Essence(シグナルessence)** | 現行で確実に自動稼働しているMATAKA/DANGER自動フックの役割に着目した名称。ただし7.1の6スクリプトの存在を捨象してしまう点に注意 |

暫定推奨は**Legacy Essence Store**。理由: 現行の自動稼働経路(MATAKA/DANGER/classifier)と、
手動実行専用と推定される6スクリプトの双方を包含でき、かつ「なぜこの2系統が存在するのか」という
経緯(旧チェーンからessence_auto_updater.py v4への移行が未完了のまま放置された)を名称自体が
示唆するため、将来の統合判断(退役するか、正式に別系統として整備するか)を先送りにしない効果がある。

### 7.3 公開API(`/public/essence`・`/essence/detail`)の公開範囲・権限境界

Cloudflare Tunnel設定(`C:/Users/sirok/.cloudflared/config.yml`、2026-07-05更新)のingressルールは
`gateway.nsjp.org`→`localhost:5010`、`mcp.nsjp.org`→`localhost:5002`の2件のみで、
その他は`http_status:404`(catch-all)。ポート5000(app.py)への直接ルールは存在しない。

`mocka_mcp_server.py`の`proxy_to_app()`(TODO_291)も`/api/<subpath>`のみを`localhost:5000/api/<subpath>`へ
転送する設計であり、`/public/*`・`/essence/*`は転送対象外。

**結論**: `/public/essence`・`/essence/detail`は現状、インターネットから到達不可能(localhost限定)。
ただし両ルート自体には認証機構がない(Flask側で無条件にJSONを返す実装)ため、将来Cloudflare Tunnelの
ingressルールにポート5000が追加された場合、無認証のまま即座に公開されるリスクを内包している。
権限境界としては「現状は事実上private、ただし実装上はpublicとして書かれている」という不一致がある。
この不一致の是正(認証追加、またはルート自体の廃止)もapp.py変更Specの検討事項に含めるべきである。

## 8. Human Gate最終調整(監査官R01最終レビュー、2026-07-07)

### 8.1 名称確定: Legacy Essence Store

7.2で提示した候補のうち、**「Legacy Essence Store」を正式仮称として採用確定**する(監査官R01承認)。

> **定義**: 過去のEssence生成・蓄積処理および現在限定利用される旧互換保存領域。
> Canonical Essenceではない。新規Writer追加は禁止。将来統合または廃止判断対象。

対象実体: `C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json`

### 8.2 Writer分類

| 分類 | 対象 | 扱い |
|---|---|---|
| **Active Writer**(継続監視) | app.pyの`auto_update_essence_from_mataka()`、`_auto_danger_to_essence()`、`run_essence()`(essence_classifier.py subprocess起動) | 現行稼働中、監視継続。新規Writer追加はLegacy Essence Store定義により禁止 |
| **Legacy Writer**(凍結候補) | `essence_extractor.py`・`essence_condenser.py`・`essence_trigger.py`・`essence_pipeline.py`・`Essence_Direct_Parser.py`・`reflux.py`の6スクリプト | 自動起動経路は未発見(手動実行の可能性)。制度上はWriter権限を保持したままのため凍結候補。凍結(実行不可化)の実施はHuman Gate承認後 |
| **Unknown Writer**(監査対象) | 現時点で該当なし | 今後の調査で新たな書込み経路が発見された場合、本分類へ追加する |

「手動実行可能」は制度上Writer権限を保持している状態であるため、Legacy Writerを凍結候補として明示し、
放置扱いにしないことを本分類の目的とする。

### 8.3 公開API境界不一致(Open課題化)

`/public/essence`・`/essence/detail`について、コード上はpublic(無認証・無条件応答)である一方、
現行ネットワーク構成(Cloudflare Tunnel未登録・proxy_to_app()対象外)では事実上private(localhost限定)
という**制度表現の不一致**を、緊急のセキュリティ課題としてではなく、Open課題として正式登録する。
将来Cloudflare Tunnel設定が変更された場合に無認証のまま公開されるリスクがあるため、
次のapp.py変更Spec(ESSENCE Canonical Migration Spec v1.0)の検討対象に含める。

### 8.4 次工程

Canonical Essence Model(本文書)のHuman Gate正式承認 → 承認後に「ESSENCE Canonical Migration Spec v1.0」
(対象: app.py、目的: Legacy Essence Store参照境界整理、変更: 参照先変更またはAdapter導入、禁止: 直接削除)
を別途作成 → 影響範囲分析 → Human Gate承認 → 実装。本文書時点ではMigration Specの作成・app.py変更は
行わない。
